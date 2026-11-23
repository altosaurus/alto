# Build the Windows installer: dist\alto-<version>-windows-x64-setup.exe, and test it.
#
#   powershell -File scripts\build-windows.ps1
#
# Needs Python 3.13 (set $env:PYTHON to use another) and Inno Setup 6 (iscc.exe). It makes a clean virtual environment, installs Alto,
# PyInstaller and Pillow in it, freezes Alto with packaging\alto.spec, checks that the frozen program starts, compiles
# packaging\windows\alto.iss, and then installs the result silently, runs it, uninstalls it keeping the data, installs it again and
# uninstalls it removing the data. The installer is not run with administrator rights and nothing is left installed afterwards, but
# the data check uses the real %APPDATA%\Alto, so run this only on a computer where that folder can be touched (a CI runner).
#
# Microsoft's Visual C++ runtime is left out of the program (see packaging\alto.spec); the installer makes sure Windows has it. The
# first test install runs that step even though the runner has the runtime (/RUNTIMETEST=1): it downloads Microsoft's
# redistributable, checks its signature and runs it quietly, so this needs the internet and an administrator account, as a runner has.
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
$RuntimeFile = Join-Path $Work "runtime.txt"
$env:ALTO_RUNTIME_FILE = $RuntimeFile
Push-Location $Work
try {
    Run (Join-Path $Work "venv\Scripts\pyinstaller.exe") @("--noconfirm", "--clean", "--log-level", "WARN", "--distpath", (Join-Path $Work "dist"), "--workpath", (Join-Path $Work "work"), (Join-Path $Root "packaging\alto.spec"))
}
finally {
    Pop-Location
    Remove-Item Env:ALTO_ICON, Env:ALTO_RUNTIME_FILE -ErrorAction SilentlyContinue
}
$Frozen = Join-Path $Work "dist\alto"

# What the installer must make sure of: the Visual C++ runtime files that were left out, and the version they must at least have.
$Runtime = @{}
foreach ($Line in Get-Content $RuntimeFile) {
    $Key, $Value = $Line -split "=", 2
    $Runtime[$Key] = $Value
}
if (-not $Runtime["version"] -or -not $Runtime["files"]) { throw "The build did not record the Visual C++ runtime it needs: $RuntimeFile" }
Write-Host "The installer will make sure of the Visual C++ runtime $($Runtime['version']): $($Runtime['files'])"
$Microsoft = Get-ChildItem -Path $Frozen -Recurse -File | Where-Object { $_.Name -match '^(vcruntime|msvcp|concrt|vccorlib|vcamp|vcomp)\d|^ucrtbase\.dll$|^api-ms-win-' }
if ($Microsoft) { throw "Microsoft's runtime must not be in the program: $($Microsoft.FullName -join ', ')" }
if (Get-ChildItem -Path $Frozen -Recurse -Directory -Filter "numpy") { throw "numpy must not be in the program" }

# The license the installer shows: Alto's, then the terms that protect the Microsoft code that every compiled program contains.
$License = Join-Path $Work "license.txt"
$LicenseText = (Get-Content -Raw (Join-Path $Root "LICENSE")).TrimEnd() + "`r`n`r`n`r`n" + (Get-Content -Raw (Join-Path $Root "packaging\windows\microsoft-components.txt"))
Set-Content -Path $License -Value $LicenseText -Encoding ascii -NoNewline
$InstallerDefines = @("/DRuntimeVersion=$($Runtime['version'])", "/DRuntimeFiles=$($Runtime['files'])", "/DLicenseFile=$License")
$DependencyLicenses = Join-Path $Root "packaging\dependency_licenses.py"
Run $Py @($DependencyLicenses, "copy", $Frozen)
Run $Py @((Join-Path $Root "packaging\qt_sources.py"), $Frozen, (Join-Path $Root "dist\qt-sources"))

# A program with no console prints nothing, so `--version` can only show that the imports worked, by ending with 0. The package's
# metadata, which is where the version comes from, must be in the folder.
Run (Join-Path $Frozen "alto.exe") @("--version")
# What an update needs (the certificate list and the signature check) must be inside the folder. It prints nothing without a console,
# and says what is wrong by its exit code.
Run (Join-Path $Frozen "alto.exe") @("--self-test")
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
Run $Iscc (@("/Qp", "/DAppVersion=$Version", "/DSourceDir=$Frozen", "/DOutputDir=$(Join-Path $Root 'dist')", "/DIconFile=$Icon") + $InstallerDefines + @((Join-Path $Root "packaging\windows\alto.iss")))
$Setup = Join-Path $Root "dist\alto-$Version-windows-x64-setup.exe"
if (-not (Test-Path $Setup)) { throw "The installer was not written: $Setup" }
Write-Host "Wrote $Setup ($([math]::Round((Get-Item $Setup).Length / 1MB)) MB)"

# Try the installer for real: install, run, uninstall keeping the data, install again, uninstall removing it.
$Target = Join-Path $Work "installed"
$Data = Join-Path $env:APPDATA "Alto"
$Quiet = @("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART")
$TermsKey = "HKCU:\Software\Alto Installer"

# A silent install for a Windows account that has not accepted the terms in microsoft-components.txt asks first, and installs
# nothing until they are answered. Setup.exe runs the installer as a child process, which shows the question, so both are stopped.
Remove-Item -Path $TermsKey -Recurse -ErrorAction SilentlyContinue
$Asking = Start-Process -FilePath $Setup -ArgumentList ($Quiet + @("/CURRENTUSER", "/DIR=$Target")) -PassThru
Start-Sleep -Seconds 15
if ($Asking.HasExited) { throw "A silent install without accepted terms ended (exit code $($Asking.ExitCode)) instead of asking" }
if (Test-Path (Join-Path $Target "alto.exe")) { throw "A silent install without accepted terms installed Alto before asking" }
Get-CimInstance Win32_Process -Filter "ParentProcessId = $($Asking.Id)" | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Stop-Process -Id $Asking.Id -Force -ErrorAction SilentlyContinue
$Asking.WaitForExit(30000) | Out-Null
if (Test-Path $Target) { throw "A silent install without accepted terms changed $Target" }
Write-Host "A silent install for an account that has not accepted the terms asks first, and changes nothing until then."

# The installs below accept the terms the way an automated install does. Alto's own update, further down, passes no such
# argument: the terms accepted by the install before it are remembered.
$Accept = @("/ACCEPTTERMS=1")
$InstallLog = Join-Path $Work "install.log"
try {
    RunAndWait $Setup ($Quiet + $Accept + @("/CURRENTUSER", "/DIR=$Target", "/RUNTIMETEST=1", "/LOG=$InstallLog"))
}
catch {
    # Exit code 7 means the runtime step stopped the installation: the log says why.
    if (Test-Path $InstallLog) { Get-Content $InstallLog | ForEach-Object { Write-Host $_ } }
    throw
}
if (-not (Test-Path (Join-Path $Target "alto.exe"))) { throw "The installer did not install alto.exe in $Target" }
if (-not (Select-String -Path $InstallLog -SimpleMatch "The Microsoft Visual C++ Runtime is ready." -Quiet)) {
    Get-Content $InstallLog | Select-String -Pattern "Visual C\+\+|Runtime" | ForEach-Object { Write-Host $_ }
    throw "The installer did not download, check and run Microsoft's Visual C++ Redistributable"
}
Write-Host "The installer downloads Microsoft's Visual C++ Redistributable, checks Microsoft's signature on it and runs it."
if ((Get-ItemProperty -Path $TermsKey -ErrorAction SilentlyContinue).AcceptedTerms -ne "1") { throw "The installer did not record the accepted terms" }
Run (Join-Path $Target "alto.exe") @("--version")
CheckStaysOpen (Join-Path $Target "alto.exe")
Run $Py @($DependencyLicenses, "verify", $Target)
foreach ($Notice in @("THIRD_PARTY_NOTICES.md", "licenses/Microsoft/microsoft-components.txt", "licenses/Qt/README.txt", "licenses/Qt/upstream-notices.zip", "licenses/Qt/LGPL-3.0-only.txt", "licenses/Qt/GPL-3.0-only.txt")) {
    if (-not (Test-Path (Join-Path $Target $Notice))) { throw "The installer is missing $Notice" }
}

New-Item -ItemType Directory -Force -Path $Data | Out-Null
Set-Content -Path (Join-Path $Data "alto.db") -Value "precious"
$Uninstaller = Join-Path $Target "unins000.exe"
RunAndWait $Uninstaller $Quiet
WaitUntilGone (Join-Path $Target "alto.exe") "The program"
if (-not (Test-Path (Join-Path $Data "alto.db"))) { throw "A silent uninstall removed the practice history, and should have kept it" }
Write-Host "A silent uninstall removes the program and keeps the data."

RunAndWait $Setup ($Quiet + $Accept + @("/CURRENTUSER", "/DIR=$Target"))
RunAndWait $Uninstaller ($Quiet + @("/PURGE=1"))
WaitUntilGone (Join-Path $Target "alto.exe") "The program"
WaitUntilGone $Data "The practice history"
if (Test-Path $TermsKey) { throw "An uninstall with /PURGE=1 kept the record of the accepted terms" }
Write-Host "An uninstall with /PURGE=1 removes the data too."

# An update, the way Alto does it: Alto starts the step that Alto itself builds (`selfupdate.windows_handoff_command`) and quits; the step
# waits for it to end, runs the newer installer, and opens Alto again. Here the open Alto is stopped, standing in for quitting.
$Newer = "99.0.0"
Run $Iscc (@("/Qp", "/DAppVersion=$Newer", "/DSourceDir=$Frozen", "/DOutputDir=$Work", "/DIconFile=$Icon") + $InstallerDefines + @((Join-Path $Root "packaging\windows\alto.iss")))
$NewerSetup = Join-Path $Work "alto-$Newer-windows-x64-setup.exe"
if (-not (Test-Path $NewerSetup)) { throw "The newer installer was not written: $NewerSetup" }
RunAndWait $Setup ($Quiet + $Accept + @("/CURRENTUSER", "/DIR=$Target"))
$env:QT_QPA_PLATFORM = "offscreen"
$env:ALTO_HOME = Join-Path $Work "home"
try {
    $Old = Start-Process -FilePath (Join-Path $Target "alto.exe") -PassThru
    Start-Sleep -Seconds 8
    if ($Old.HasExited) { throw "Alto did not stay open for the update test" }
    $Encoded = & $Py -c "import sys; from pathlib import Path; from alto import selfupdate; print(selfupdate.windows_handoff_command(Path(sys.argv[1]), pid=int(sys.argv[2]), alto=Path(sys.argv[3]))[-1])" $NewerSetup $Old.Id (Join-Path $Target "alto.exe")
    if ($LASTEXITCODE -ne 0 -or -not $Encoded) { throw "The update step could not be made" }
    $Step = Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-EncodedCommand", $Encoded) -PassThru
    Start-Sleep -Seconds 2
    if ($Step.HasExited) { throw "The update step ended before Alto had quit" }
    # Seed files that an older installation may have and this version does not, after startup, so the in-place upgrade exercises its
    # cleanup.
    $LegacyDlls = @(
        "PySide6/Qt6VirtualKeyboard.dll", "PySide6/plugins/platforminputcontexts/qtvirtualkeyboardplugin.dll",
        "PySide6/Qt6Pdf.dll", "PySide6/plugins/imageformats/qpdf.dll", "PySide6/plugins/multimedia/ffmpegmediaplugin.dll",
        "PySide6/avcodec-63.dll", "PySide6/avformat-63.dll", "PySide6/avutil-61.dll", "PySide6/swresample-7.dll", "PySide6/swscale-10.dll",
        "VCRUNTIME140.dll", "VCRUNTIME140_1.dll", "PySide6/MSVCP140.dll", "PySide6/VCRUNTIME140.dll", "shiboken6/MSVCP140.dll",
        "numpy/__init__.py", "numpy.libs/msvcp140-a4c2229bdc2a2a630acdc095b4d86008.dll"
    ) | ForEach-Object { Join-Path $Target "_internal/$_" }
    foreach ($File in $LegacyDlls) {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $File) | Out-Null
        New-Item -ItemType File -Path $File -ErrorAction Stop | Out-Null
    }
    $Old.Kill()
    $Old.WaitForExit(30000) | Out-Null
    if (-not $Step.WaitForExit(240000)) { throw "The update step did not finish" }
    foreach ($File in $LegacyDlls) {
        if (Test-Path $File) { throw "Update left an obsolete DLL: $File" }
    }
    $Open = $false
    for ($i = 0; $i -lt 60 -and -not $Open; $i++) {
        Start-Sleep -Milliseconds 500
        $Open = [bool](Get-Process -Name alto -ErrorAction SilentlyContinue)
    }
    if (-not $Open) { throw "The update did not open Alto again" }
    $Key = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{26F851E3-0F09-45A0-A9C4-13D12F91DA07}_is1"
    $Now = (Get-ItemProperty -Path $Key).DisplayVersion
    if ($Now -ne $Newer) { throw "After the update the installed version is $Now, not $Newer" }
    if (@(Get-Process -Name alto -ErrorAction SilentlyContinue).Count -ne 1) { throw "Alto was opened more than once by the update" }
}
finally {
    Get-Process -Name alto -ErrorAction SilentlyContinue | Stop-Process -Force
    Remove-Item Env:QT_QPA_PLATFORM, Env:ALTO_HOME -ErrorAction SilentlyContinue
}
Write-Host "An update step, built by Alto, waits for Alto to quit, installs the newer version and opens Alto again."
RunAndWait (Join-Path $Target "unins000.exe") ($Quiet + @("/PURGE=1"))
WaitUntilGone (Join-Path $Target "alto.exe") "The program"
Write-Host "Done: $Setup"
