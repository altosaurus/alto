"""
Tests that keep the packaging files in step with each other and with the choices the rest of Alto depends on.

The Windows installer and the release workflow can only really run on GitHub, so these check what can be checked here: that the
files parse, agree on the names of what they build, and keep the few settings that must not change.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from alto import selfupdate

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
INSTALLER = ROOT / "packaging" / "windows" / "alto.iss"
RELEASE = (WORKFLOWS / "release.yml").read_text(encoding="utf-8")
BUILD = (WORKFLOWS / "build-packages.yml").read_text(encoding="utf-8")


def test_every_workflow_is_valid_yaml_with_jobs() -> None:
    """Check that each workflow file parses, so a typo is caught here and not after a tag is pushed."""
    yaml = pytest.importorskip("yaml")
    files = sorted(WORKFLOWS.glob("*.yml"))
    assert {file.name for file in files} >= {"build-packages.yml", "package.yml", "release.yml"}
    for file in files:
        data = yaml.safe_load(file.read_text(encoding="utf-8"))
        assert isinstance(data, dict) and data.get("jobs"), file.name


def test_a_release_is_never_a_pre_release_because_the_update_check_skips_those() -> None:
    """Check that a release is a normal one: the update check asks for the latest release, which skips pre-releases."""
    assert "gh release create" in RELEASE
    assert "--prerelease" not in RELEASE and "--draft" not in RELEASE


def test_the_release_is_made_only_for_a_tag_that_exists_and_only_the_publisher_can_write() -> None:
    """Check that publishing needs a version tag, verifies it, and is the only job allowed to write to the repository."""
    yaml = pytest.importorskip("yaml")
    data = yaml.safe_load(RELEASE)
    triggers = data.get(True, data.get("on"))
    assert triggers["push"]["tags"] == ["v*"] and "workflow_dispatch" in triggers
    assert data["permissions"] == {"contents": "read"}
    assert data["jobs"]["publish"]["permissions"] == {"contents": "write"}
    assert data["jobs"]["publish"]["if"] == "github.ref_type == 'tag'"
    assert data["jobs"]["publish"]["needs"] == "build" and data["jobs"]["build"]["needs"] == "check"
    assert "--verify-tag" in RELEASE
    assert all("permissions" not in job for name, job in data["jobs"].items() if name != "publish")


def test_the_release_checks_the_tag_against_the_version_and_the_changelog_before_building() -> None:
    """Check that the first job compares the tag with pyproject.toml's version and asks the changelog script for its notes."""
    assert 'tomllib.load(open("pyproject.toml"' in RELEASE
    assert '"${GITHUB_REF_NAME}" != "v${version}"' in RELEASE
    assert "scripts/changelog_section.py" in RELEASE


def test_the_linux_build_has_the_x11_libraries_and_fails_without_them() -> None:
    """
    Check that the runner installs the libraries Qt's X11 plugin needs, and that the build script checks the plugin finds them.

    PyInstaller copies them into the download from the machine it runs on, and the offscreen check cannot tell they are missing.
    """
    for package in ("libxcb-cursor0", "libxcb-icccm4", "libxcb-image0", "libxcb-keysyms1", "libxkbcommon-x11-0"):
        assert package in BUILD
    script = (ROOT / "scripts" / "build-linux.sh").read_text(encoding="utf-8")
    assert "libqxcb.so" in script and "ldd" in script and "not found" in script


def test_the_linux_package_is_built_on_an_old_ubuntu_with_the_python_that_is_shipped() -> None:
    """Check the Linux job's runner and Python: the program needs at least the C library of the system it is built on."""
    assert "runs-on: ubuntu-22.04" in BUILD
    assert BUILD.count('python-version: "3.13"') == 2  # for Linux and for Windows


def test_the_installer_and_the_workflows_agree_on_the_names_of_what_is_built() -> None:
    """Check that the names the build scripts give the Linux download and the Windows installer match what is uploaded."""
    iss = INSTALLER.read_text(encoding="utf-8")
    assert "OutputBaseFilename=alto-{#AppVersion}-windows-x64-setup" in iss
    assert "path: dist/alto-*-setup.exe" in BUILD
    assert 'NAME="alto-$VERSION-linux-$(uname -m)"' in (ROOT / "scripts" / "build-linux.sh").read_text(encoding="utf-8")
    assert "path: dist/alto-*.tar.gz" in BUILD
    assert "dist/alto-*.tar.gz dist/alto-*-setup.exe dist/SHA256SUMS" in RELEASE
    assert "alto-$Version-windows-x64-setup.exe" in (ROOT / "scripts" / "build-windows.ps1").read_text(encoding="utf-8")


def test_the_installer_keeps_its_id_installs_for_one_user_and_asks_about_the_data() -> None:
    """Check the settings of the installer that must not drift: its identity, no administrator prompt, and the data question."""
    iss = INSTALLER.read_text(encoding="utf-8")
    assert "AppId={{26F851E3-0F09-45A0-A9C4-13D12F91DA07}" in iss  # a newer installer finds the copy to update by this
    assert "PrivilegesRequired=lowest" in iss and "DefaultDirName={autopf}\\Alto" in iss
    assert "LicenseFile=..\\..\\LICENSE" in iss and "THIRD_PARTY_NOTICES.md" in iss
    assert "{userappdata}\\Alto" in iss and "Software\\alto" in iss  # where Alto keeps its history and its settings
    assert "UninstallSilent" in iss and "{param:PURGE|0}" in iss and "mbConfirmation" in iss
    assert "MB_DEFBUTTON2" in iss  # the question defaults to No, so the data is kept unless the person says otherwise


def test_the_windows_build_reads_the_version_from_pyproject_and_tests_the_installer() -> None:
    """Check that the Windows script takes the version from pyproject.toml and tries install, uninstall and purge for real."""
    script = (ROOT / "scripts" / "build-windows.ps1").read_text(encoding="utf-8")
    assert "tomllib.load" in script and "pyproject.toml" in script
    assert "/PURGE=1" in script and "/VERYSILENT" in script and "unins000.exe" in script
    assert re.search(r"A silent uninstall removed the practice history", script)


def test_the_release_is_signed_and_the_signature_is_published_with_it() -> None:
    """Check that the workflow signs the list of checksums with the secret key, checks that early, and uploads the signature."""
    yaml = pytest.importorskip("yaml")
    data = yaml.safe_load(RELEASE)
    assert "scripts/sign_release.py dist/SHA256SUMS" in RELEASE and "dist/SHA256SUMS.sig" in RELEASE
    assert RELEASE.count("secrets.ALTO_SIGNING_KEY") == 2  # the early probe, and the signing itself
    assert (
        "scripts/sign_release.py" in RELEASE.split("build:")[0]
    )  # before anything is built, so a wrong secret costs no build time
    check_steps = [step.get("name", "") for step in data["jobs"]["check"]["steps"]]
    assert "The release can be signed" in check_steps
    assert "SHA256SUMS.sig" in RELEASE and (ROOT / "scripts" / "sign_release.py").is_file()


def test_the_build_scripts_run_the_self_test_on_the_frozen_program() -> None:
    """Check that both build scripts run `--self-test`, which shows the certificate list and the signature check are in."""
    assert "--self-test" in (ROOT / "scripts" / "build-linux.sh").read_text(encoding="utf-8")
    assert "--self-test" in (ROOT / "scripts" / "build-windows.ps1").read_text(encoding="utf-8")


def test_the_windows_update_arguments_are_the_same_in_alto_the_test_script_and_the_installer() -> None:
    """
    Check that the arguments Alto gives the installer suit the installer script, and that the build script runs Alto's own step.

    The installer's own restart must stay off, or Alto would be started twice.
    """
    script = (ROOT / "scripts" / "build-windows.ps1").read_text(encoding="utf-8")
    assert "selfupdate.windows_handoff_command" in script  # the build script runs the step Alto builds, not a copy of it
    arguments = ("/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS", "/RELAUNCH=1")
    assert selfupdate.WINDOWS_INSTALLER_ARGUMENTS == arguments
    iss = INSTALLER.read_text(encoding="utf-8")
    assert "Check: ShouldRelaunch" in iss and "{param:RELAUNCH|0}" in iss
    assert "RestartApplications=no" in iss and "CloseApplications=yes" in iss


def test_the_linux_installer_copies_beside_the_old_copy_and_swaps() -> None:
    """Check that `install.sh` no longer deletes the installed copy before the new one is in place."""
    script = (ROOT / "packaging" / "linux" / "install.sh").read_text(encoding="utf-8")
    assert '"$OPT.new"' in script and '"$OPT.old"' in script
    assert script.index('cp -R "$HERE/alto" "$OPT.new"') < script.index('mv "$OPT.new" "$OPT"')
    assert 'rm -rf "$OPT"\n    cp -R' not in script
