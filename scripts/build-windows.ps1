# Build the Windows installer: dist\alto-<version>-windows-x64-setup.exe, and test it.
#
#   powershell -File scripts\build-windows.ps1
#
# Needs Python 3.13 (set $env:PYTHON to use another) and Inno Setup 6 (iscc.exe). It makes a clean virtual environment, installs Alto,
# PyInstaller and Pillow in it, freezes Alto with packaging\alto.spec, checks that the frozen program starts, compiles
# packaging\windows\alto.iss, and then installs the result silently, runs it, uninstalls it keeping the data, installs it again and
# uninstalls it removing the data. The installer is not run with administrator rights and nothing is left installed afterwards, but
# the data check uses the real %APPDATA%\Alto, so run this only on a computer where that folder can be touched (a CI runner).
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
$Work = if ($env:ALTO_BUILD_DIR) { $env:ALTO_BUILD_DIR } else { Join-Path $Root ".package-build" }

function Run {
    param([string]$Program, [string[]]$Arguments)
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Program failed with exit code $LASTEXITCODE" }
}

# An installer is a program with a window, which PowerShell does not wait for, so wait for it and look at how it ended.
function RunAndWait {
    param([string]$Program, [string[]]$Arguments)
    $process = Start-Process -FilePath $Program -ArgumentList $Arguments -Wait -PassThru
    if ($process.ExitCode -ne 0) { throw "$Program failed with exit code $($process.ExitCode)" }
}

# The uninstaller copies itself to a temporary folder and finishes from there, so the program it started can end before the work does.
function WaitUntilGone {
    param([string]$Path, [string]$What)
    for ($i = 0; $i -lt 120; $i++) {
        if (-not (Test-Path $Path)) { return }
        Start-Sleep -Milliseconds 500
    }
    throw "$What was not removed: $Path is still there after a minute."
}

$Version = (& $Python -c "import sys, tomllib; print(tomllib.load(open(sys.argv[1], 'rb'))['project']['version'])" (Join-Path $Root "pyproject.toml")).Trim()
if ($LASTEXITCODE -ne 0 -or -not $Version) { throw "Could not read the version from pyproject.toml" }
Write-Host "Building Alto $Version with $(& $Python --version)"

if (Test-Path $Work) { Remove-Item -Recurse -Force $Work }
New-Item -ItemType Directory -Force -Path $Work, (Join-Path $Root "dist") | Out-Null

# Alto is installed from a copy of the source, because installing from the folder itself would leave build files in it.
robocopy $Root (Join-Path $Work "source") /E /XD .git .venv .package-build dist build __pycache__ alto.egg-info /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Copying the source failed (robocopy exit code $LASTEXITCODE)" }
$global:LASTEXITCODE = 0

Run $Python @("-m", "venv", (Join-Path $Work "venv"))
$Py = Join-Path $Work "venv\Scripts\python.exe"
Run $Py @("-m", "pip", "install", "--quiet", ((Join-Path $Work "source") + "[package]"), "pillow")

# The program's icon, an .ico with several sizes, made from the PNG the app already ships.
$Icon = Join-Path $Work "alto.ico"
$MakeIcon = Join-Path $Work "make_icon.py"
@"
import sys
from PIL import Image
Image.open(sys.argv[1]).save(sys.argv[2], sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
"@ | Set-Content -Path $MakeIcon -Encoding ascii
Run $Py @($MakeIcon, (Join-Path $Root "alto\assets\icon.png"), $Icon)

$env:ALTO_ICON = $Icon
Push-Location $Work
try {
    Run (Join-Path $Work "venv\Scripts\pyinstaller.exe") @("--noconfirm", "--clean", "--log-level", "WARN", "--distpath", (Join-Path $Work "dist"), "--workpath", (Join-Path $Work "work"), (Join-Path $Root "packaging\alto.spec"))
}
finally {
    Pop-Location
    Remove-Item Env:ALTO_ICON -ErrorAction SilentlyContinue
}
$Frozen = Join-Path $Work "dist\alto"

# A program with no console prints nothing, so `--version` can only show that the imports worked, by ending with 0. The package's
# metadata, which is where the version comes from, must be in the folder.
Run (Join-Path $Frozen "alto.exe") @("--version")
if (-not (Get-ChildItem -Path $Frozen -Recurse -Directory -Filter "alto-$Version.dist-info")) { throw "The frozen program has no metadata for alto $Version" }

# It must open its window and stay open. Nothing is drawn on a screen, and it uses its own folder for its data.
function CheckStaysOpen {
    param([string]$Program)
    $env:QT_QPA_PLATFORM = "offscreen"
    $env:ALTO_HOME = Join-Path $Work "home"
    try {
        $process = Start-Process -FilePath $Program -PassThru
        Start-Sleep -Seconds 10
        if ($process.HasExited) { throw "$Program did not stay open (exit code $($process.ExitCode))" }
        Stop-Process -Id $process.Id -Force
    }
    finally {
        Remove-Item Env:QT_QPA_PLATFORM, Env:ALTO_HOME -ErrorAction SilentlyContinue
    }
}
CheckStaysOpen (Join-Path $Frozen "alto.exe")
Write-Host "The frozen program starts."

$Iscc = (Get-Command iscc.exe -ErrorAction SilentlyContinue).Source
if (-not $Iscc) { $Iscc = Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe" }
if (-not (Test-Path $Iscc)) { throw "Inno Setup 6 (ISCC.exe) was not found. Install it from https://jrsoftware.org/isinfo.php" }
Run $Iscc @("/Qp", "/DAppVersion=$Version", "/DSourceDir=$Frozen", "/DOutputDir=$(Join-Path $Root 'dist')", "/DIconFile=$Icon", (Join-Path $Root "packaging\windows\alto.iss"))
$Setup = Join-Path $Root "dist\alto-$Version-windows-x64-setup.exe"
if (-not (Test-Path $Setup)) { throw "The installer was not written: $Setup" }
Write-Host "Wrote $Setup ($([math]::Round((Get-Item $Setup).Length / 1MB)) MB)"

# Try the installer for real: install, run, uninstall keeping the data, install again, uninstall removing it.
$Target = Join-Path $Work "installed"
$Data = Join-Path $env:APPDATA "Alto"
$Quiet = @("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART")
RunAndWait $Setup ($Quiet + @("/CURRENTUSER", "/DIR=$Target", "/LOG=$(Join-Path $Work 'install.log')"))
if (-not (Test-Path (Join-Path $Target "alto.exe"))) { throw "The installer did not install alto.exe in $Target" }
Run (Join-Path $Target "alto.exe") @("--version")
CheckStaysOpen (Join-Path $Target "alto.exe")
if (-not (Test-Path (Join-Path $Target "THIRD_PARTY_NOTICES.md"))) { throw "The notices were not installed" }

New-Item -ItemType Directory -Force -Path $Data | Out-Null
Set-Content -Path (Join-Path $Data "alto.db") -Value "precious"
$Uninstaller = Join-Path $Target "unins000.exe"
RunAndWait $Uninstaller $Quiet
WaitUntilGone (Join-Path $Target "alto.exe") "The program"
if (-not (Test-Path (Join-Path $Data "alto.db"))) { throw "A silent uninstall removed the practice history, and should have kept it" }
Write-Host "A silent uninstall removes the program and keeps the data."

RunAndWait $Setup ($Quiet + @("/CURRENTUSER", "/DIR=$Target"))
RunAndWait $Uninstaller ($Quiet + @("/PURGE=1"))
WaitUntilGone (Join-Path $Target "alto.exe") "The program"
WaitUntilGone $Data "The practice history"
Write-Host "An uninstall with /PURGE=1 removes the data too."
Write-Host "Done: $Setup"
