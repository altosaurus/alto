; Inno Setup script for the Windows installer of Alto. scripts\build-windows.ps1 runs it, after PyInstaller has made dist\alto:
;   iscc /DAppVersion=0.0.0 /DRuntimeVersion=14.44.35211.0 /DRuntimeFiles=msvcp140.dll;vcruntime140.dll /DLicenseFile=license.txt
;     packaging\windows\alto.iss
;
; Alto uses the Microsoft Visual C++ runtime installed on Windows. The installer checks that Windows has the runtime files Python
; and Qt need (RuntimeFiles), at least as new as the copies they were built with (RuntimeVersion, which
; packaging\alto.spec reads from them). If not, it downloads Microsoft's Visual C++ Redistributable from Microsoft, checks Microsoft's
; signature on it, and runs it with its own window, where the user accepts Microsoft's license. That needs administrator rights, so
; Windows asks for them. /RUNTIMETEST=1 runs this step even when the runtime is there, and quietly: only the build test uses it.
; LicenseFile is Alto's license followed by microsoft-components.txt, the terms that protect the bits of Microsoft code in every
; program Microsoft's compiler builds.
;
; The installer is for one user: no administrator prompt, Alto in %LOCALAPPDATA%\Programs\Alto, an entry in the Start menu and in
; Settings > Apps. Running a newer installer over an older one updates it, because AppId stays the same. The uninstaller asks
; whether to also remove the practice history and the settings, and a silent uninstall keeps them unless /PURGE=1 is given.

#ifndef AppVersion
  #error Pass the version: iscc /DAppVersion=0.0.0 packaging\windows\alto.iss
#endif
#ifndef RuntimeVersion
  #error Pass the Visual C++ runtime the program needs: /DRuntimeVersion=14.44.35211.0 /DRuntimeFiles=msvcp140.dll;vcruntime140.dll
#endif
#ifndef RuntimeFiles
  #error Pass the Visual C++ runtime files the program needs: /DRuntimeFiles=msvcp140.dll;vcruntime140.dll
#endif
#ifndef LicenseFile
  #error Pass the license to show: /DLicenseFile=license.txt (Alto's LICENSE followed by microsoft-components.txt)
#endif
; SourceDir: the folder PyInstaller made. OutputDir: where the installer is written. IconFile: an .ico, if there is one.
#ifndef SourceDir
  #define SourceDir "..\..\dist\alto"
#endif
#ifndef OutputDir
  #define OutputDir "..\..\dist"
#endif

[Setup]
; Never change this: it is how a newer installer finds the copy it should update.
AppId={{26F851E3-0F09-45A0-A9C4-13D12F91DA07}
AppName=Alto
AppVersion={#AppVersion}
AppPublisher=Alto
AppPublisherURL=https://github.com/altosaurus/alto
AppSupportURL=https://github.com/altosaurus/alto/issues
AppUpdatesURL=https://github.com/altosaurus/alto/releases
DefaultDirName={autopf}\Alto
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; Windows 10 and later include the Universal C runtime, the part of Microsoft's runtime that comes with Windows itself.
MinVersion=10.0
LicenseFile={#LicenseFile}
OutputDir={#OutputDir}
OutputBaseFilename=alto-{#AppVersion}-windows-x64-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; An update started from inside Alto closes it with /CLOSEAPPLICATIONS and starts it again with /RELAUNCH=1 (see [Run] below), so the
; installer's own restart of the programs it closed is off: Alto would be started twice.
CloseApplications=yes
RestartApplications=no
UninstallDisplayIcon={app}\alto.exe
#ifdef IconFile
SetupIconFile={#IconFile}
#endif

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; Flags: unchecked

[InstallDelete]
; An update installs over the older version, which would leave behind files the newer one no longer has. Everything under
; _internal is replaced, so it is cleared first.
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "microsoft-components.txt"; DestDir: "{app}\licenses\Microsoft"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Alto"; Filename: "{app}\alto.exe"
Name: "{autodesktop}\Alto"; Filename: "{app}\alto.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\alto.exe"; Description: "Start Alto"; Flags: nowait postinstall skipifsilent
; After an update that Alto started itself, which is silent and given /RELAUNCH=1: open Alto again.
Filename: "{app}\alto.exe"; Flags: nowait; Check: ShouldRelaunch

[Code]
const
  RuntimeUrl = 'https://aka.ms/vs/17/release/vc_redist.x64.exe';  { Microsoft's permanent link to its latest x64 redistributable }
  RuntimeSetup = 'vc_redist.x64.exe';

var
  RuntimeDownload: TDownloadWizardPage;
  RuntimeHandled: Boolean;  { the runtime step has run once and succeeded }
  RuntimeRestart: Boolean;  { Microsoft's installer asked for Windows to be restarted }

function ShouldRelaunch: Boolean;
begin
  Result := ExpandConstant('{param:RELAUNCH|0}') = '1';
end;

function RuntimeTest: Boolean;
begin
  Result := ExpandConstant('{param:RUNTIMETEST|0}') = '1';
end;

{ Whether one runtime file is in the 64-bit System32 folder, at least as new as the copy the program was built with. }
function RuntimeFileReady(const Name: String): Boolean;
var
  Installed, Needed: Int64;
begin
  Result := GetPackedVersion(ExpandConstant('{sys}\') + Name, Installed) and StrToVersion('{#RuntimeVersion}', Needed)
    and (ComparePackedVersion(Installed, Needed) >= 0);
end;

function RuntimeReady: Boolean;
var
  Names: TArrayOfString;
  I: Integer;
begin
  Names := StringSplit('{#RuntimeFiles}', [';'], stExcludeEmpty);
  Result := True;
  for I := 0 to GetArrayLength(Names) - 1 do
    if not RuntimeFileReady(Names[I]) then
    begin
      Log('The Microsoft Visual C++ Runtime needs updating: ' + Names[I] + ' is missing or older than {#RuntimeVersion}.');
      Result := False;
      Exit;
    end;
end;

function RuntimeNeeded: Boolean;
begin
  Result := not RuntimeHandled and (RuntimeTest or not RuntimeReady);
end;

{ Whether Windows confirms that Microsoft signed the downloaded file and that it was not changed since. }
function SignedByMicrosoft(const Path: String): Boolean;
var
  ResultCode: Integer;
  Report: String;
  Found: AnsiString;
begin
  Result := False;
  Report := ExpandConstant('{tmp}\signature.txt');
  { PowerShell writes the signature's status and its signer's name, or the error that stopped it; the decision is made here,
    where it can be logged. The module path is reset to the machine's, because Windows PowerShell started from PowerShell 7
    inherits PowerShell 7's modules and then cannot load the one that checks signatures. }
  if not Exec(ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe'),
    '-NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "' +
    '$env:PSModulePath = [Environment]::GetEnvironmentVariable(''PSModulePath'', ''Machine''); ' +
    'try { $s = Get-AuthenticodeSignature -LiteralPath ''' + Path + '''; $v = [string]$s.Status + ''|'' + $s.SignerCertificate.Subject } ' +
    'catch { $v = ''Error|'' + $_ }; Set-Content -LiteralPath ''' + Report + ''' -Encoding ASCII -Value $v"',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    Log(Format('PowerShell could not be started to check the signature: %s', [SysErrorMessage(ResultCode)]));
    Exit;
  end;
  if not LoadStringFromFile(Report, Found) then
  begin
    Log(Format('PowerShell ended with code %d and did not report the signature.', [ResultCode]));
    Exit;
  end;
  Log('Signature of ' + Path + ': ' + String(Found));
  Result := (Pos('Valid|', String(Found)) = 1) and (Pos('O=Microsoft Corporation', String(Found)) > 0);
end;

{ Download Microsoft's Visual C++ Redistributable and run it. Page shows the download, or is nil for a silent install.
  Returns an empty string when the runtime is ready, or else what went wrong. }
function InstallRuntime(Page: TDownloadWizardPage): String;
var
  Setup, Parameters: String;
  ResultCode: Integer;
begin
  Result := '';
  try
    if Page <> nil then
    begin
      Page.Clear;
      Page.Add(RuntimeUrl, RuntimeSetup, '');
      Page.Show;
      try
        Page.Download;
      finally
        Page.Hide;
      end;
    end
    else
      DownloadTemporaryFile(RuntimeUrl, RuntimeSetup, '', nil);
  except
    { A line must not begin with a character code such as #13: the preprocessor would read it as one of its directives. }
    Result := 'Alto needs the Microsoft Visual C++ Runtime, but it could not be downloaded from Microsoft: ' +
      GetExceptionMessage + #13#10#13#10 + 'Connect to the internet and try again, or install it yourself from ' +
      'https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist and then run this installer again.';
    Exit;
  end;
  Setup := ExpandConstant('{tmp}\') + RuntimeSetup;
  if not SignedByMicrosoft(Setup) then
  begin
    Result := 'The Microsoft Visual C++ Runtime that was downloaded is not signed by Microsoft, so it was not run.';
    Exit;
  end;
  if RuntimeTest then
    Parameters := '/install /quiet /norestart'
  else
    Parameters := '/install /norestart';
  Log('Running Microsoft''s Visual C++ Redistributable: ' + Setup + ' ' + Parameters);
  if not ShellExec('runas', Setup, Parameters, '', SW_SHOW, ewWaitUntilTerminated, ResultCode) then
  begin
    Result := 'Alto needs the Microsoft Visual C++ Runtime, but its installer could not be started: ' + SysErrorMessage(ResultCode);
    Exit;
  end;
  Log(Format('Microsoft''s Visual C++ Redistributable ended with code %d.', [ResultCode]));
  if (ResultCode = 1641) or (ResultCode = 3010) then  { installed, and Windows must be restarted to finish }
    RuntimeRestart := True
  else if ResultCode = 1602 then
  begin
    Result := 'Alto needs the Microsoft Visual C++ Runtime, whose installation was canceled, so Alto was not installed.';
    Exit;
  end
  else if (ResultCode <> 0) and (ResultCode <> 1638) then  { 0: installed; 1638: a newer version was already there }
  begin
    Result := Format('Alto needs the Microsoft Visual C++ Runtime, whose installer ended with code %d, ' +
      'so Alto was not installed.', [ResultCode]);
    Exit;
  end;
  if not RuntimeRestart and not RuntimeReady then
  begin
    Result := 'The Microsoft Visual C++ Runtime was installed, but the files Alto needs are still missing or out of date.';
    Exit;
  end;
  Log('The Microsoft Visual C++ Runtime is ready.');
  RuntimeHandled := True;
end;

procedure InitializeWizard;
begin
  RuntimeDownload := CreateDownloadPage('Microsoft Visual C++ Runtime',
    'Alto needs Microsoft''s Visual C++ Runtime, which this computer does not have yet. Downloading it from Microsoft...', nil);
end;

{ An ordinary install handles the runtime on leaving the Ready page, where the download can be shown and an error lets the user
  try again. }
function NextButtonClick(CurPageID: Integer): Boolean;
var
  Problem: String;
begin
  Result := True;
  if (CurPageID = wpReady) and not WizardSilent and RuntimeNeeded then
  begin
    Problem := InstallRuntime(RuntimeDownload);
    if Problem <> '' then
    begin
      MsgBox(Problem, mbError, MB_OK);
      Result := False;
    end;
  end;
end;

{ A silent install, such as an update started from inside Alto, skips the pages, so it handles the runtime here, before anything is
  changed: if that fails, the version already installed is left as it was. }
function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  if RuntimeNeeded then
    Result := InstallRuntime(nil);
end;

function NeedRestart: Boolean;
begin
  Result := RuntimeRestart;
end;

{ Alto keeps its practice history in %APPDATA%\Alto and its settings in the registry under HKEY_CURRENT_USER\Software\alto. }
procedure RemoveUserData;
begin
  DelTree(ExpandConstant('{userappdata}\Alto'), True, True, True);
  RegDeleteKeyIncludingSubkeys(HKEY_CURRENT_USER, 'Software\alto');
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep <> usPostUninstall then
    Exit;
  if UninstallSilent then
  begin
    { A silent uninstall never asks, and keeps the data unless it was told to remove it: Unins000.exe /VERYSILENT /PURGE=1 }
    if ExpandConstant('{param:PURGE|0}') = '1' then
      RemoveUserData;
  end
  else if MsgBox('Alto has been removed.' + #13#10 + #13#10 +
                 'Also remove your practice history and your settings? Choose No to keep them, for example to install Alto again later.',
                 mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
    RemoveUserData;
end;
