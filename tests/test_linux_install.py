"""
Tests for the install script of the Linux download.

The script installs for one user, updates in place, removes cleanly, keeps or deletes the user's data as asked, and never
touches a copy of Alto that was installed another way. It runs for real, in a scratch home, against a stand-in for the unpacked
download.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import NamedTuple

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "packaging" / "linux" / "install.sh"


class Site(NamedTuple):
    """
    A scratch home, and an unpacked download to install from.

    Attributes
    ----------
    download : Path
        The folder the download was unpacked to, holding `install.sh`, the program and the icons.
    prefix : Path
        Where the script is told to install (`ALTO_PREFIX`).
    data : Path
        The user's data folder (`XDG_DATA_HOME`).
    config : Path
        The user's settings folder (`XDG_CONFIG_HOME`).
    env : dict of str to str
        The environment to run the script in.
    """

    download: Path
    prefix: Path
    data: Path
    config: Path
    env: dict[str, str]

    @property
    def opt(self) -> Path:
        """
        Give the folder the program is installed in.

        Returns
        -------
        Path
            `opt/alto` under the prefix.
        """
        return self.prefix / "opt" / "alto"

    @property
    def link(self) -> Path:
        """
        Give the command that starts the program.

        Returns
        -------
        Path
            `bin/alto` under the prefix.
        """
        return self.prefix / "bin" / "alto"

    @property
    def entry(self) -> Path:
        """
        Give the application menu entry.

        Returns
        -------
        Path
            `alto.desktop` in the user's applications folder.
        """
        return self.data / "applications" / "alto.desktop"

    @property
    def icons(self) -> list[Path]:
        """
        Give the icons the script installs.

        Returns
        -------
        list of Path
            The 256 and 512 pixel icons.
        """
        return [self.data / "icons" / "hicolor" / size / "apps" / "alto.png" for size in ("256x256", "512x512")]


def run(
    site: Site,
    *args: str,
) -> subprocess.CompletedProcess[str]:
    """
    Run the install script from the unpacked download.

    Parameters
    ----------
    site : Site
        The scratch home and the download.
    *args : str
        The arguments to give it.

    Returns
    -------
    subprocess.CompletedProcess
        What it did, with its output as text.
    """
    return subprocess.run(
        ["sh", str(site.download / "install.sh"), *args],
        env=site.env,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture
def site(tmp_path: Path) -> Site:
    """
    Make a scratch home and an unpacked download whose program just says its version.

    Parameters
    ----------
    tmp_path : Path
        A new folder.

    Returns
    -------
    Site
        The home and the download.
    """
    download = tmp_path / "alto-9.9.9-linux-test"
    program = download / "alto" / "alto"
    program.parent.mkdir(parents=True)
    program.write_text('#!/bin/sh\necho "Alto 9.9.9"\n')
    program.chmod(0o755)
    (program.parent / "_internal").mkdir()
    (program.parent / "_internal" / "library.so").write_text("a file the program needs")
    (download / "icons").mkdir()
    for name in ("icon-256.png", "icon.png"):
        shutil.copy(ROOT / "alto" / "assets" / name, download / "icons" / name)
    shutil.copy(SCRIPT, download / "install.sh")
    home = tmp_path / "home"
    data, config = home / "data", home / "config"
    env = {
        "PATH": os.environ["PATH"],
        "HOME": str(home),
        "ALTO_PREFIX": str(tmp_path / "prefix"),
        "XDG_DATA_HOME": str(data),
        "XDG_CONFIG_HOME": str(config),
    }
    home.mkdir()
    return Site(download, tmp_path / "prefix", data, config, env)


def keep_some_data(site: Site) -> tuple[Path, Path]:
    """
    Put a practice history and a settings file where Alto keeps them.

    Parameters
    ----------
    site : Site
        The scratch home.

    Returns
    -------
    tuple of Path and Path
        The database file and the settings file.
    """
    database, settings = site.data / "Alto" / "alto.db", site.config / "alto" / "alto.conf"
    for path in (database, settings):
        path.parent.mkdir(parents=True)
        path.write_text("precious")
    return database, settings


def test_installing_copies_the_program_links_it_and_adds_the_menu_entry_and_icons(site: Site) -> None:
    """
    Check that install puts the program, the command, the menu entry and the icons where they belong, with no root.

    Parameters
    ----------
    site : Site
        The scratch home and the download.
    """
    done = run(site, "install")
    assert done.returncode == 0, done.stderr
    assert "Installed Alto 9.9.9" in done.stdout
    assert (site.opt / "alto").is_file() and os.access(site.opt / "alto", os.X_OK)
    assert (site.opt / "_internal" / "library.so").read_text() == "a file the program needs"
    assert site.link.is_symlink() and site.link.readlink() == site.opt / "alto"
    lines = site.entry.read_text().splitlines()
    assert 'Exec="' + str(site.opt / "alto") + '"' in lines and "Icon=alto" in lines and "Name=Alto" in lines
    assert not any(line.startswith(("StartupNotify", "StartupWMClass")) for line in lines)
    assert all(icon.is_file() and icon.stat().st_size > 0 for icon in site.icons)


def test_installing_again_replaces_the_old_files_and_keeps_the_data(site: Site) -> None:
    """
    Check that installing a newer download replaces the program, leaves nothing of the old one, and keeps the data.

    Parameters
    ----------
    site : Site
        The scratch home and the download.
    """
    assert run(site, "install").returncode == 0
    (site.opt / "left-over-from-the-old-version").write_text("old")
    database, settings = keep_some_data(site)
    again = run(site, "install")
    assert again.returncode == 0, again.stderr
    assert not (site.opt / "left-over-from-the-old-version").exists() and (site.opt / "alto").is_file()
    assert database.read_text() == settings.read_text() == "precious"


def test_uninstalling_removes_what_was_installed_and_keeps_the_data(site: Site) -> None:
    """
    Check that uninstall removes the program, the command, the menu entry and the icons, and says the data was kept.

    Parameters
    ----------
    site : Site
        The scratch home and the download.
    """
    run(site, "install")
    database, settings = keep_some_data(site)
    done = run(site, "uninstall")
    assert done.returncode == 0, done.stderr
    assert not site.opt.exists() and not site.link.exists() and not site.link.is_symlink() and not site.entry.exists()
    assert not any(icon.exists() for icon in site.icons)
    assert database.read_text() == settings.read_text() == "precious"
    assert "were kept" in done.stdout and "--purge" in done.stdout


def test_uninstalling_with_purge_also_deletes_the_history_and_the_settings(site: Site) -> None:
    """
    Check that `uninstall --purge` removes the practice history and the settings as well, and says what it deleted.

    Parameters
    ----------
    site : Site
        The scratch home and the download.
    """
    run(site, "install")
    database, settings = keep_some_data(site)
    done = run(site, "uninstall", "--purge")
    assert done.returncode == 0, done.stderr
    assert not site.opt.exists() and not site.entry.exists()
    assert not database.parent.exists() and not settings.parent.exists()
    assert str(database.parent) in done.stdout and str(settings.parent) in done.stdout


def test_uninstalling_when_nothing_is_installed_says_so_and_can_still_purge(site: Site) -> None:
    """
    Check that uninstalling with nothing installed succeeds and says so, and that purge still deletes the data.

    Parameters
    ----------
    site : Site
        The scratch home and the download.
    """
    assert "is not installed" in run(site, "uninstall").stdout
    database, _ = keep_some_data(site)
    done = run(site, "uninstall", "--purge")
    assert done.returncode == 0 and not database.parent.exists()


class Foreign(NamedTuple):
    """
    What a copy of Alto installed another way (with alto-install.sh) leaves behind, which has the same names.

    Attributes
    ----------
    program : Path
        The program the command points at.
    """

    program: Path


def install_another_way(site: Site) -> Foreign:
    """
    Leave what alto-install.sh would: a command that is a link to a program elsewhere, a menu entry for it, and an icon.

    Parameters
    ----------
    site : Site
        The scratch home.

    Returns
    -------
    Foreign
        The program the command points at.
    """
    program = site.prefix / "elsewhere" / "alto"
    program.parent.mkdir(parents=True)
    program.write_text("#!/bin/sh\n")
    site.link.parent.mkdir(parents=True)
    site.link.symlink_to(program)
    site.entry.parent.mkdir(parents=True)
    site.entry.write_text(f"[Desktop Entry]\nExec={site.link}\nIcon=alto\n")
    for icon in site.icons:
        icon.parent.mkdir(parents=True)
        icon.write_text("their icon")
    return Foreign(program)


def test_installing_refuses_to_overwrite_a_copy_installed_another_way(site: Site) -> None:
    """
    Check that install stops, changes nothing, and says how to remove the other copy, if the command already exists.

    Parameters
    ----------
    site : Site
        The scratch home and the download.
    """
    other = install_another_way(site)
    before = site.entry.read_text()
    done = run(site, "install")
    assert done.returncode == 1 and "alto-install.sh uninstall" in done.stderr
    assert site.link.readlink() == other.program and site.entry.read_text() == before
    assert not site.opt.exists()
    assert all(icon.read_text() == "their icon" for icon in site.icons)


def test_uninstalling_leaves_a_copy_installed_another_way_alone(site: Site) -> None:
    """
    Check that uninstall does not remove a command, menu entry or icons that are not this download's, even by the same name.

    Parameters
    ----------
    site : Site
        The scratch home and the download.
    """
    other = install_another_way(site)
    before = site.entry.read_text()
    done = run(site, "uninstall")
    assert done.returncode == 0 and "is not installed" in done.stdout
    assert site.link.readlink() == other.program and site.entry.read_text() == before
    assert all(icon.read_text() == "their icon" for icon in site.icons)


def test_a_link_that_was_removed_by_hand_still_lets_uninstall_clean_up(site: Site) -> None:
    """
    Check that uninstall still removes the program folder, the menu entry and the icons if the command link is already gone.

    Parameters
    ----------
    site : Site
        The scratch home and the download.
    """
    run(site, "install")
    site.link.unlink()
    assert run(site, "uninstall").returncode == 0
    assert not site.opt.exists() and not site.entry.exists() and not any(icon.exists() for icon in site.icons)


def test_running_it_from_a_folder_with_no_program_fails_with_a_message(site: Site) -> None:
    """
    Check that install says what is wrong, and changes nothing, if the folder does not hold the program.

    Parameters
    ----------
    site : Site
        The scratch home and the download.
    """
    shutil.rmtree(site.download / "alto")
    done = run(site, "install")
    assert done.returncode == 1 and "no alto/alto program" in done.stderr
    assert not site.opt.exists() and not site.link.exists()


def test_with_no_argument_the_script_prints_how_to_use_it_and_changes_nothing(site: Site) -> None:
    """
    Check that running it with no arguments explains the commands and exits with 2.

    Parameters
    ----------
    site : Site
        The scratch home and the download.
    """
    done = run(site)
    assert done.returncode == 2 and "install.sh install" in done.stdout and "uninstall --purge" in done.stdout
    assert not site.opt.exists() and not site.entry.exists()


def test_the_download_scripts_are_valid_shell() -> None:
    """Check that the install script and the build script at least parse, so a typo is caught before a release."""
    for script in (SCRIPT, ROOT / "scripts" / "build-linux.sh"):
        done = subprocess.run(["sh", "-n", str(script)], capture_output=True, text=True, check=False)
        assert done.returncode == 0, done.stderr


def test_a_failed_copy_leaves_the_installed_copy_exactly_as_it_was(site: Site) -> None:
    """
    Check that when the new files cannot be copied, install stops, says nothing was changed, and keeps the old copy.

    Parameters
    ----------
    site : Site
        The scratch home and the download.
    """
    assert run(site, "install").returncode == 0
    (site.opt / "marker").write_text("the old copy")
    unreadable = site.download / "alto" / "unreadable"
    unreadable.write_text("x")
    unreadable.chmod(0)
    try:
        done = run(site, "install")
    finally:
        unreadable.chmod(0o644)
    assert done.returncode == 1 and "nothing was changed" in done.stderr
    assert (site.opt / "marker").read_text() == "the old copy" and (site.opt / "alto").is_file()
    assert site.link.is_symlink() and site.link.readlink() == site.opt / "alto"
    assert not (site.opt.parent / "alto.new").exists() and not (site.opt.parent / "alto.old").exists()


def test_a_successful_update_leaves_no_copy_of_the_old_files_beside_the_new(site: Site) -> None:
    """
    Check that after installing over an old copy only the new one remains, with nothing set aside.

    Parameters
    ----------
    site : Site
        The scratch home and the download.
    """
    assert run(site, "install").returncode == 0
    (site.opt / "old-only").write_text("x")
    assert run(site, "install").returncode == 0
    assert not (site.opt / "old-only").exists()
    assert sorted(path.name for path in site.opt.parent.iterdir()) == ["alto"]
