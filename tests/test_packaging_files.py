"""
Tests that keep the packaging files in step with each other and with the
choices the rest of Alto depends on.

The Windows installer and the release workflow can only really run on
GitHub, so these check what can be checked here: that the
files parse, agree on the names of what they build, and keep the few
settings that must not change.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from alto import selfupdate

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
INSTALLER = ROOT / "packaging" / "windows" / "alto.iss"
RELEASE = (WORKFLOWS / "release.yml").read_text(encoding="utf-8")
DOWNLOAD = (ROOT / "scripts/download-candidate.sh").read_text(encoding="utf-8")
PUBLISH = (ROOT / "scripts/publish-candidate.sh").read_text(encoding="utf-8")
BUILD = (WORKFLOWS / "build-packages.yml").read_text(encoding="utf-8")


def test_every_workflow_is_valid_yaml_with_jobs() -> None:
    """
    Check that each workflow file parses, so a typo is caught here and
    not after a tag is pushed.
    """
    yaml = pytest.importorskip("yaml")
    files = sorted(WORKFLOWS.glob("*.yml"))
    assert {file.name for file in files} >= {
        "build-packages.yml",
        "package.yml",
        "release.yml",
    }
    for file in files:
        data = yaml.safe_load(file.read_text(encoding="utf-8"))
        assert isinstance(data, dict) and data.get("jobs"), file.name


def test_release_never_pre_release_because_update_check_skips() -> None:
    """
    Check that a release is a normal one: the update check asks for the
    latest release, which skips pre-releases.
    """
    assert "gh release create" in PUBLISH and "--draft --verify-tag" in PUBLISH
    assert "--draft=false --prerelease=false" in PUBLISH


def test_release_made_only_for_tag_exists_and_only_publisher_can() -> None:
    """
    Check that publishing needs a version tag, verifies it, and is the
    only job allowed to write to the repository.
    """
    yaml = pytest.importorskip("yaml")
    data = yaml.safe_load(RELEASE)
    triggers = data.get(True, data.get("on"))
    assert (
        triggers["push"]["tags"] == ["v*"] and "workflow_dispatch" in triggers
    )
    assert data["permissions"] == {"contents": "read"}
    assert data["jobs"]["publish"]["permissions"] == {
        "actions": "read",
        "contents": "write",
    }
    assert data["jobs"]["publish"]["if"] == (
        "github.event_name == 'push' && github.ref_type == 'tag'"
    )
    assert (
        "needs" not in data["jobs"]["publish"]
        and "workflow_dispatch" in data["jobs"]["check"]["if"]
        and "refs/heads/main" in data["jobs"]["check"]["if"]
        and set(data["jobs"]["candidate"]["needs"])
        == {"sign-windows", "macos"}
        and data["jobs"]["macos"]["needs"] == "check"
        and data["jobs"]["macos"]["with"] == {"macos_notarize": True}
        and data["jobs"]["sign-windows"]["needs"] == "build"
        and data["jobs"]["build"]["needs"] == "check"
    )
    assert "--verify-tag" in PUBLISH
    assert all(
        "permissions" not in job
        for name, job in data["jobs"].items()
        if name not in {"publish", "sign-windows"}
    )


def test_release_publishes_the_verified_windows_installer() -> None:
    """
    Keep signing in the protected job and the unsigned installer out
    of the files used to produce the release checksums.
    """
    yaml = pytest.importorskip("yaml")
    jobs = yaml.safe_load(RELEASE)["jobs"]
    signing = jobs["sign-windows"]
    assert signing["environment"] == "windows-signing"
    assert signing["permissions"] == {"contents": "read", "id-token": "write"}
    steps = signing["steps"]
    assert steps[0]["with"]["name"] == "windows"
    assert "Get-AuthenticodeSignature" in steps[-2]["run"]
    assert "TimeStamperCertificate" in steps[-2]["run"]
    assert steps[-1]["with"]["name"] == "windows-signed"
    downloads = [
        step["with"]
        for step in jobs["candidate"]["steps"]
        if step.get("uses", "").startswith("actions/download-artifact@")
    ]
    assert downloads == [
        {
            "pattern": "{linux,*-sources-*,versions-*}",
            "path": "packages",
        },
        {"name": "windows-signed", "path": "dist"},
        {"name": "alto-macos-arm64-notarized", "path": "packages/macos"},
    ]


@pytest.mark.skipif(
    os.name == "nt"
    or any(shutil.which(tool) is None for tool in ("bash", "sha256sum", "jq")),
    reason="The publisher runs on a Linux runner.",
)
@pytest.mark.parametrize("changed", [False, True])
def test_draft_is_published_only_with_reviewed_hashes(
    tmp_path: Path,
    changed: bool,
) -> None:
    """
    Exercise promotion of a draft with a matching or changed asset.

    Parameters
    ----------
    tmp_path : Path
        Temporary candidate, draft, and GitHub CLI fixture.
    changed : bool
        Whether GitHub reports a different hash for the uploaded file.
    """
    contents = b"reviewed source archive"
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "source.tar").write_bytes(contents)
    digest = hashlib.sha256(b"changed" if changed else contents).hexdigest()
    gh = tmp_path / "gh"
    gh.write_text(
        """#!/bin/sh
case "$*" in
    *"--json isDraft"*) echo true ;;
    *"--json assets"*) echo source.tar ;;
    *"--json apiUrl"*) echo release-url ;;
    "api --paginate release-url/assets") echo "$ASSETS" ;;
    "release edit v1.0.0 --draft=false --prerelease=false") touch public ;;
    *) exit 2 ;;
esac
""",
        encoding="utf-8",
    )
    gh.chmod(0o755)
    result = subprocess.run(
        ["bash", ROOT / "scripts/publish-candidate.sh"],
        cwd=tmp_path,
        env={
            **os.environ,
            "PATH": str(tmp_path) + os.pathsep + os.environ["PATH"],
            "GITHUB_REF_NAME": "v1.0.0",
            "RUNNER_TEMP": str(tmp_path),
            "ASSETS": f'[{{"name":"source.tar","digest":"sha256:{digest}"}}]',
        },
        check=False,
    )
    assert result.returncode == int(changed)
    assert (tmp_path / "public").exists() == (not changed)


def test_release_checks_tag_against_version_and_changelog_before() -> None:
    """
    Check the tag against the version and require release notes.
    """
    assert 'tomllib.load(open("pyproject.toml"' in RELEASE
    assert '"$GITHUB_REF_NAME" != "v$version"' in DOWNLOAD
    assert "scripts/changelog_section.py" in RELEASE


def test_the_linux_build_has_the_x11_libraries_and_fails_without_them() -> (
    None
):
    """
    Check that the runner installs the libraries Qt's X11 plugin needs,
    and that the build script checks the plugin finds them.

    PyInstaller copies them into the download from the machine it runs
    on, and the offscreen check cannot tell they are missing.
    """
    for package in (
        "libxcb-cursor0",
        "libxcb-icccm4",
        "libxcb-image0",
        "libxcb-keysyms1",
        "libxkbcommon-x11-0",
    ):
        assert package in BUILD
    script = (ROOT / "scripts" / "build-linux.sh").read_text(encoding="utf-8")
    assert "libqxcb.so" in script and "ldd" in script and "not found" in script


def test_linux_package_built_on_old_ubuntu_with_python_shipped() -> None:
    """
    Check the Linux job's runner and Python: the program needs at least
    the C library of the system it is built on.
    """
    assert "runs-on: ubuntu-22.04" in BUILD
    assert (
        BUILD.count("python-version-file: packaging/python-version") == 2
    )  # for Linux and for Windows


def test_installer_and_workflows_agree_on_names_of_what_built() -> None:
    """
    Check that the names the build scripts give the Linux download and
    the Windows installer match what is uploaded.
    """
    iss = INSTALLER.read_text(encoding="utf-8")
    assert "OutputBaseFilename=alto-{#AppVersion}-windows-x64-setup" in iss
    assert "path: dist/alto-*-setup.exe" in BUILD
    assert 'NAME="alto-$VERSION-linux-$(uname -m)"' in (
        ROOT / "scripts" / "build-linux.sh"
    ).read_text(encoding="utf-8")
    assert "path: dist/alto-*.tar.gz" in BUILD
    assert BUILD.count("path: dist/qt-sources/*.tar.xz") == 2
    assert "path: dist/alto-*-library-sources.tar" in BUILD
    for suffix in (
        "linux-x86_64.tar.gz",
        "windows-x64-setup.exe",
        "macos-arm64.dmg",
        "linux-x86_64-library-sources.tar",
    ):
        assert f"alto-$version-{suffix}" in RELEASE
    assert "qt-everywhere-src-*.tar.xz" in RELEASE
    assert "pyside-setup-everywhere-src-*.tar.xz" in RELEASE
    assert "alto-$Version-windows-x64-setup.exe" in (
        ROOT / "scripts" / "build-windows.ps1"
    ).read_text(encoding="utf-8")


def test_linux_download_leaves_out_gtk_and_readline_and_covers() -> None:
    """
    Check that the Linux download leaves out Qt's GTK 3 theme and
    Python's readline, and notices its system libraries.

    The spec drops the theme plugin with the libraries only it needed,
    excludes readline, fails if either is still in the
    bundle, and lists the system libraries that remain. The build
    installs their notices and writes the sources archive,
    whose copyleft and permissive package lists do not overlap.
    """
    spec = (ROOT / "packaging" / "alto.spec").read_text(encoding="utf-8")
    assert '"readline"' in spec.split("excludes=")[1].split("]")[0]
    assert (
        '"libqgtk3.so"' in spec
        and "only_unused" in spec
        and "ALTO_SYSTEM_LIBRARIES" in spec
    )
    assert "readline and GTK must not be in the desktop package" in spec
    script = (ROOT / "scripts" / "build-linux.sh").read_text(encoding="utf-8")
    assert 'ALTO_SYSTEM_LIBRARIES="$WORK/system-libraries.json"' in script
    assert (
        '"$ROOT/packaging/linux_libraries.py" "$FROZEN" '
        '"$WORK/system-libraries.json"'
    ) in script
    assert (
        '"$ROOT/dist/$NAME-library-sources.tar"' in script
        and "licenses/Linux/README.txt" in script
    )
    helper = (ROOT / "packaging" / "linux_libraries.py").read_text(
        encoding="utf-8",
    )
    copyleft = set(
        re.findall(
            r'"([a-z0-9.+-]+)",',
            helper.split("SOURCE_PACKAGES = frozenset(")[1].split(")")[0],
        ),
    )
    permissive = set(
        re.findall(
            r'"([a-z0-9.+-]+)",',
            helper.split("NOTICE_PACKAGES = frozenset(")[1].split(")")[0],
        ),
    )
    assert {"glib2.0", "libsndfile", "pulseaudio", "gcc-12"} <= copyleft
    assert copyleft.isdisjoint(permissive)
    assert not {"gtk+3.0", "readline"} & (
        copyleft | permissive
    )  # left out of the download, so never expected


def test_packages_carry_notices_of_python_packages_and_native() -> None:
    """
    Check that the build installs the notices of the interpreter, the
    frozen packages, and the native code they contain.

    The license helper copies the license of each frozen package from
    its wheel, the interpreter's license and CPython's list
    of incorporated software, certifi's license with where its source
    is, and the licenses of LibYAML, libffi, ICU and
    OpenSSL, read for the versions in the build. Both build scripts run
    it and check the installed copy.
    """
    helper = (ROOT / "packaging" / "dependency_licenses.py").read_text(
        encoding="utf-8",
    )
    for package in (
        "typing_extensions",
        "chevron",
        "cached-property",
        "PyYAML",
        "cffi",
        "certifi",
        "fsrs",
    ):
        assert f'("{package}", "LICENSE", "{package}/LICENSE")' in helper
    for source in (
        "/python/cpython/v{python}/Doc/license.rst",
        "/python/cpython/v{python}/Modules/_hacl/{name}",
        "https://pypi.org/pypi/certifi/{certifi}/json",
        "https://www.mozilla.org/media/MPL/2.0/index.txt",
        "/yaml/libyaml/{libyaml}/License",
        "/libffi/libffi/v{libffi}/LICENSE",
        "/python-cffi/cffi/v{cffi}/src/c/libffi_x86_x64/LICENSE",
        "/unicode-org/icu/release-",
        "/openssl/openssl/openssl-{openssl}/LICENSE.txt",
    ):
        assert source in helper
    assert '"notices.json"' in helper and '"README.txt"' in helper
    assert (
        '"Python/HACL-star.txt"' in helper
    )  # HACL*'s MIT notice, which CPython's license.rst does not list
    for script in ("build-linux.sh", "build-windows.ps1"):
        text = (ROOT / "scripts" / script).read_text(encoding="utf-8")
        assert (
            "dependency_licenses.py" in text
            and "copy" in text
            and "verify" in text
        )


def test_qt_notices_follow_license_files_qt_names_and_mesa_left() -> None:
    """
    Check that the Qt notices include every license file a
    qt_attribution.json names, and that Windows has no Mesa renderer.

    PCRE2's LICENCE.md and Shiboken's Python license are found only
    through the attribution files. The build fails if a named
    file is missing from the source. Alto does not draw with OpenGL, so
    Qt's software OpenGL renderer is not shipped. The
    bindings' Python modules are shipped as files, so they can be
    replaced like the libraries.
    """
    helper = (ROOT / "packaging" / "qt_sources.py").read_text(encoding="utf-8")
    assert (
        '"LicenseFiles"' in helper
        and '"LicenseFile"' in helper
        and '"licence"' in helper
    )
    assert '{"FTL.TXT", "GPLv2.TXT"}' in helper and "are not in it" in helper
    spec = (ROOT / "packaging" / "alto.spec").read_text(encoding="utf-8")
    assert '"opengl32sw.dll"' in spec
    # The bindings' Python modules stay replaceable files, as the LGPL-3
    # notice says, and the build fails if one is compiled in.
    assert (
        'module_collection_mode={"PySide6": "py", "shiboken6": "py"}' in spec
    )
    assert "PySide6 and shiboken6 modules must be kept as .py files" in spec
    assert "as .py files that can be replaced with modified ones" in helper


def test_silent_install_asks_for_microsoft_terms_once_before() -> None:
    """
    Check that the terms in microsoft-components.txt are accepted once
    per Windows account, also on a silent update.

    Alto's update runs the installer silently, which skips the license
    page, so the installer asks with a message (which
    /SUPPRESSMSGBOXES does not hide) before anything is changed, and
    records the answer. The build test checks that an
    install without accepted terms waits and installs nothing, and
    accepts them for its own installs with /ACCEPTTERMS=1.
    """
    iss = INSTALLER.read_text(encoding="utf-8")
    code = iss.split("function InitializeSetup: Boolean;")[1].split(
        "procedure InitializeWizard;",
    )[0]
    assert (
        "if not WizardSilent or TermsAccepted then" in code
        and "{param:ACCEPTTERMS|0}" in code
    )
    assert (
        "MsgBox(Terms, mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES"
        in code
    )  # No is the default answer
    assert (
        "SuppressibleMsgBox" not in code
    )  # that one would be answered by /SUPPRESSMSGBOXES
    assert (
        "ExtractTemporaryFile('microsoft-components.txt')" in iss
        and '#define TermsVersion "' in iss
    )
    assert (
        "if CurPageID = wpLicense then" in iss
        and "RegDeleteKeyIncludingSubkeys(HKEY_CURRENT_USER, TermsKey);" in iss
    )
    script = (ROOT / "scripts" / "build-windows.ps1").read_text(
        encoding="utf-8",
    )
    assert (
        '$Accept = @("/ACCEPTTERMS=1")' in script
        and script.count("$Quiet + $Accept +") == 3
    )
    assert (
        "A silent install without accepted terms installed Alto before asking"
        in script
    )
    assert "ACCEPTTERMS" not in "".join(
        selfupdate.WINDOWS_INSTALLER_ARGUMENTS,
    )  # an update asks if the terms are not accepted


def test_the_documentation_carries_temml_and_katex_notices() -> None:
    """
    Check that the vendored Temml has its own MIT license and that of
    KaTeX, from which it is derived.
    """
    vendor = ROOT / "docs" / "assets" / "vendor" / "temml-0.14.0"
    assert "Ron Kok" in (vendor / "LICENSE").read_text(encoding="utf-8")
    assert "Khan Academy and other contributors" in (
        vendor / "LICENSE-KaTeX"
    ).read_text(encoding="utf-8")


def test_installer_keeps_id_installs_for_one_user_and_asks_about() -> None:
    """
    Check the settings of the installer that must not drift: its
    identity, no administrator prompt, and the data question.
    """
    iss = INSTALLER.read_text(encoding="utf-8")
    assert (
        "AppId={{26F851E3-0F09-45A0-A9C4-13D12F91DA07}" in iss
    )  # a newer installer finds the copy to update by this
    assert (
        "PrivilegesRequired=lowest" in iss
        and "DefaultDirName={autopf}\\Alto" in iss
    )
    assert (
        "LicenseFile={#LicenseFile}" in iss and "THIRD_PARTY_NOTICES.md" in iss
    )
    assert (
        "{userappdata}\\Alto" in iss and "Software\\alto" in iss
    )  # where Alto keeps its history and its settings
    assert (
        "UninstallSilent" in iss
        and "{param:PURGE|0}" in iss
        and "mbConfirmation" in iss
    )
    assert (
        "MB_DEFBUTTON2" in iss
        # the question defaults to No, so the data is kept unless the
        # person
        # says otherwise
    )


def test_windows_package_leaves_out_microsofts_runtime_and() -> None:
    """
    Check that the program uses the Visual C++ runtime installed on
    Windows, and that the installer makes sure it is there.

    The build leaves the runtime out and fails if any copy remains, and
    numpy is not a dependency. The installer downloads
    Microsoft's redistributable, checks Microsoft's signature, and runs
    it, also in a silent update. The license page has the
    terms for the Microsoft code in compiled programs.
    """
    spec = (ROOT / "packaging" / "alto.spec").read_text(encoding="utf-8")
    assert '"numpy"' in spec.split("excludes=")[1].split("]")[0]
    assert "MICROSOFT_RUNTIME" in spec and "ALTO_RUNTIME_FILE" in spec
    assert "Microsoft's runtime must not be in the desktop package" in spec
    dependencies = re.search(
        r"(?ms)^dependencies = \[(.*?)^]",
        (ROOT / "pyproject.toml").read_text(encoding="utf-8"),
    )
    assert dependencies and "numpy" not in dependencies.group(1)
    iss = INSTALLER.read_text(encoding="utf-8")
    assert (
        "RuntimeUrl = 'https://aka.ms/vc14/vc_redist.x64.exe';" in iss
        and "SignedByMicrosoft" in iss
    )
    assert (
        "aka.ms/vs/17" not in iss.split("RuntimeUrl = ")[1]
    )  # Visual Studio 2022's link stays at an older runtime
    assert (
        "O=Microsoft Corporation" in iss and "Get-AuthenticodeSignature" in iss
    )
    assert (
        "function PrepareToInstall" in iss
    )  # the silent update path, before anything is changed
    assert (
        "'/install /norestart'" in iss
    )  # Microsoft's own window, where the person accepts Microsoft's license
    assert (
        "MinVersion=10.0" in iss
        and "{#RuntimeVersion}" in iss
        and "{#RuntimeFiles}" in iss
    )
    assert (
        'Type: filesandordirs; Name: "{app}\\_internal"' in iss
    )  # an update removes files older versions installed
    # Inno Setup reads a line that begins with # as a preprocessor
    # directive, which a Pascal character code such as #13 is not,
    # and a line that begins with [ as a section, even in the code, so
    # an argument list such as [ResultCode] must not start one.
    assert not [line for line in iss.splitlines() if re.match(r"\s*#\d", line)]
    sections = {
        "[Setup]",
        "[Tasks]",
        "[InstallDelete]",
        "[Files]",
        "[Icons]",
        "[Run]",
        "[Code]",
    }
    assert {
        line.strip()
        for line in iss.splitlines()
        if line.lstrip().startswith("[")
    } <= sections
    script = (ROOT / "scripts" / "build-windows.ps1").read_text(
        encoding="utf-8",
    )
    assert (
        "/RUNTIMETEST=1" in script
        and "The Microsoft Visual C++ Runtime is ready." in script
    )
    assert (
        "older than the $($Runtime['version']) the program needs" in script
    )  # what the link serves is new enough
    assert (
        script.count("$InstallerDefines") == 3
    )  # defined once, given to both installers the script compiles
    terms = (
        ROOT / "packaging" / "windows" / "microsoft-components.txt"
    ).read_text(encoding="utf-8")
    for condition in (
        "alter any copyright, trademark or patent notice",
        "use Microsoft's trademarks",
        "other than Microsoft operating systems",
        "malicious, deceptive or unlawful programs",
    ):
        assert (
            condition in terms
        )  # the conditions of CPython's PC/crtlicense.txt
    assert terms.isascii()


def test_windows_build_reads_version_from_pyproject_and_tests() -> None:
    """
    Check that the Windows script takes the version from pyproject.toml
    and tries install, uninstall and purge for real.
    """
    script = (ROOT / "scripts" / "build-windows.ps1").read_text(
        encoding="utf-8",
    )
    assert "tomllib.load" in script and "pyproject.toml" in script
    assert (
        "/PURGE=1" in script
        and "/VERYSILENT" in script
        and "unins000.exe" in script
    )
    assert re.search(
        r"A silent uninstall removed the practice history",
        script,
    )


def test_the_release_is_signed_and_the_signature_is_published_with_it() -> (
    None
):
    """
    Check that the workflow signs the list of checksums with the secret
    key, checks that early, and uploads the signature.
    """
    yaml = pytest.importorskip("yaml")
    data = yaml.safe_load(RELEASE)
    assert (
        "scripts/sign_release.py dist/SHA256SUMS" in RELEASE
        and "SHA256SUMS.sig" in RELEASE
    )
    assert (
        RELEASE.count("secrets.ALTO_SIGNING_KEY") == 2
    )  # the early probe, and the signing itself
    assert (
        "scripts/sign_release.py" in RELEASE.split("build:")[0]
    )  # before anything is built, so a wrong secret costs no build time
    check_steps = [
        step.get("name", "") for step in data["jobs"]["check"]["steps"]
    ]
    assert "The release can be signed" in check_steps
    assert (
        "SHA256SUMS.sig" in RELEASE
        and (ROOT / "scripts" / "sign_release.py").is_file()
    )


def test_the_build_scripts_run_the_self_test_on_the_frozen_program() -> None:
    """
    Check that both build scripts run `--self-test`, which shows the
    certificate list and the signature check are in.
    """
    assert "--self-test" in (ROOT / "scripts" / "build-linux.sh").read_text(
        encoding="utf-8",
    )
    assert "--self-test" in (ROOT / "scripts" / "build-windows.ps1").read_text(
        encoding="utf-8",
    )


def test_windows_update_arguments_same_in_alto_test_script_and() -> None:
    """
    Check that the arguments Alto gives the installer suit the installer
    script, and that the build script runs Alto's own step.

    The installer's own restart must stay off, or Alto would be started
    twice.
    """
    script = (ROOT / "scripts" / "build-windows.ps1").read_text(
        encoding="utf-8",
    )
    assert (
        "selfupdate.windows_handoff_command" in script
    )  # the build script runs the step Alto builds, not a copy of it
    arguments = (
        "/SILENT",
        "/SUPPRESSMSGBOXES",
        "/NORESTART",
        "/CLOSEAPPLICATIONS",
        "/RELAUNCH=1",
    )
    assert selfupdate.WINDOWS_INSTALLER_ARGUMENTS == arguments
    iss = INSTALLER.read_text(encoding="utf-8")
    assert "Check: ShouldRelaunch" in iss and "{param:RELAUNCH|0}" in iss
    assert "RestartApplications=no" in iss and "CloseApplications=yes" in iss


def test_the_linux_installer_copies_beside_the_old_copy_and_swaps() -> None:
    """
    Check that `install.sh` no longer deletes the installed copy before
    the new one is in place.
    """
    script = (ROOT / "packaging" / "linux" / "install.sh").read_text(
        encoding="utf-8",
    )
    assert '"$OPT.new"' in script and '"$OPT.old"' in script
    assert script.index('cp -R "$HERE/alto" "$OPT.new"') < script.index(
        'mv "$OPT.new" "$OPT"',
    )
    assert 'rm -rf "$OPT"\n    cp -R' not in script
