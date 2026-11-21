"""Install and update a real format-2 pack using simulated registry and GitHub releases."""

import hashlib
import json
import shutil
import time
from pathlib import Path
from unittest.mock import Mock
from zipfile import ZipFile

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox
from scripts.check_plugin_registry import check_registry

from alto import plugin_registry
from alto.exercises.packs import InstalledPlugin, installed_plugins, read_pack
from alto.ui.plugins_dialog import PluginsDialog
from viola_pack import ZIP

DOCS = Path(__file__).resolve().parents[1] / "docs"

VIOLA = ZIP
REPO = "example/strings"
ASSET = f"https://github.com/{REPO}/releases/download/published/viola.zip"
ENTRY = {"code": "0042", "id": "viola", "repository": f"https://github.com/{REPO}"}


@pytest.fixture
def release(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[dict, Mock, Mock]:
    """
    Mock only the network boundaries, leaving validation and installation intact.

    Parameters
    ----------
    tmp_path : Path
        The simulated release's storage.
    monkeypatch : pytest.MonkeyPatch
        Replace the metadata and asset transports.

    Returns
    -------
    tuple of dict, Mock, Mock
        The adjustable release, metadata transport, and download transport.
    """
    archive = tmp_path / "published.zip"
    shutil.copyfile(VIOLA, archive)
    asset = {"name": "viola.zip", "browser_download_url": ASSET}
    latest = {"tag_name": "summer", "assets": [asset]}
    responses = {
        plugin_registry.REGISTRY_URL: [ENTRY],
        f"https://api.github.com/repos/{REPO}/releases/latest": latest,
    }

    def fetch(url: str, *, seconds: int) -> tuple[int, str]:
        """
        Serve current JSON for the requested URL.

        Parameters
        ----------
        url : str
            The simulated endpoint.
        seconds : int
            Request timeout.

        Returns
        -------
        tuple of int and str
            Successful JSON response.
        """
        return 200, json.dumps(responses[url])

    def download(url: str, *, destination: Path, **kwargs: object) -> str:
        """
        Supply the release archive and its transport digest.

        Parameters
        ----------
        url : str
            The URL selected from the release.
        destination : Path
            The temporary download destination.
        kwargs : object
            Download limits and callbacks.

        Returns
        -------
        str
            SHA-256 of the downloaded bytes.
        """
        assert url == ASSET and kwargs["allowed"] == f"https://github.com/{REPO}/releases/download/"
        shutil.copyfile(archive, destination)
        return hashlib.sha256(destination.read_bytes()).hexdigest()

    metadata, transfer = Mock(side_effect=fetch), Mock(side_effect=download)
    monkeypatch.setattr(plugin_registry.updates, "fetch_text", metadata)
    monkeypatch.setattr(plugin_registry.selfupdate, "download", transfer)
    return latest, metadata, transfer


def test_registered_release_lifecycle(tmp_path: Path, release: tuple[dict, Mock, Mock]) -> None:
    """
    Preserve the original through failures, detect current content, and replace a changed release.

    Parameters
    ----------
    tmp_path : Path
        The fake release and installation.
    release : tuple
        The network fixtures.
    """
    latest, _, transfer = release
    folder = tmp_path / "plugins"
    assert plugin_registry.install_registered(" 0042 ", folder=folder) == "Viola Instrument Pack (summer)"
    selected = installed_plugins(folder)[0][0]
    original = selected.path.read_bytes()
    with pytest.raises(ValueError, match="already installed"):
        plugin_registry.install_registered("0042", folder=folder)
    assert plugin_registry.install_registered("", folder=folder, selected=selected) is None
    digest = hashlib.sha256(original).hexdigest()
    latest["assets"][0]["digest"] = f"sha256:{digest}"
    transfer.reset_mock()
    assert plugin_registry.install_registered("", folder=folder, selected=selected) is None
    transfer.assert_not_called()
    archive = tmp_path / "published.zip"
    with ZipFile(archive, "a") as z:
        z.comment = b"new release"
    with pytest.raises(ValueError, match="release digest"):
        plugin_registry.install_registered("0042", folder=folder)
    del latest["assets"][0]["digest"]
    archive.write_bytes(b"invalid archive")
    with pytest.raises(ValueError, match="pack ZIP"):
        plugin_registry.install_registered("", folder=folder, selected=selected)
    assert selected.path.read_bytes() == original
    # Older installs keep their chosen file name and recover the registration from the manifest.
    selected.path.rename(folder / "my-viola.zip")
    selected = installed_plugins(folder)[0][0]
    archive.write_bytes(original)
    with ZipFile(archive, "a") as z:
        z.comment = b"autumn"
    latest["tag_name"] = "autumn"
    assert plugin_registry.install_registered("", folder=folder, selected=selected) == "Viola Instrument Pack (autumn)"
    assert selected.path.read_bytes() == archive.read_bytes()
    assert read_pack(selected.path)[0].pack_id == "viola"
    with ZipFile(archive, "a") as z:
        z.comment = b"later"
    with pytest.raises(ValueError, match="changed"):
        plugin_registry.install_registered("", folder=folder, selected=selected)
    with ZipFile(selected.path) as installed:
        assert installed.comment == b"autumn"


def test_registry_codes_and_release_selection(tmp_path: Path, release: tuple[dict, Mock, Mock]) -> None:
    """
    Reject unknown codes, mismatched pack IDs, and missing or ambiguous release assets.

    Parameters
    ----------
    tmp_path : Path
        The fake installation.
    release : tuple
        Release and network fixtures.
    """
    latest, metadata, transfer = release
    folder = tmp_path / "plugins"
    with pytest.raises(ValueError, match="No registered plugin"):
        plugin_registry.install_registered("99", folder=folder)
    with pytest.raises(ValueError, match="numeric"):
        plugin_registry.install_registered("../bad", folder=folder)
    asset = latest["assets"][0]
    latest["assets"] = []
    with pytest.raises(ValueError, match="ZIP"):
        plugin_registry.install_registered("0042", folder=folder)
    latest["assets"] = [asset | {"name": "a.zip"}, asset | {"name": "b.zip"}]
    with pytest.raises(ValueError, match="ZIP"):
        plugin_registry.install_registered("0042", folder=folder)
    transfer.assert_not_called()
    latest["assets"] = [asset]
    metadata.side_effect = [(200, json.dumps([ENTRY | {"id": "wrong-pack"}])), (200, json.dumps(latest))]
    with pytest.raises(ValueError, match="registered ID"):
        plugin_registry.install_registered("0042", folder=folder)
    assert installed_plugins(folder)[0] == []


def test_code_dialog(
    tmp_path: Path,
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    release: tuple[dict, Mock, Mock],
) -> None:
    """
    Install and update through the dialog, with no external network or actual restart.

    Parameters
    ----------
    tmp_path : Path
        Isolated plugin folder.
    app : QApplication
        Drives delivery of the worker result.
    monkeypatch : pytest.MonkeyPatch
        Supply the install code and restart response.
    release : tuple
        Local transport fixtures.
    """
    dialog = PluginsDialog(tmp_path / "plugins")
    monkeypatch.setattr("alto.ui.plugins_dialog.QInputDialog.getText", lambda *_: ("0042", True))
    monkeypatch.setattr(QMessageBox, "question", lambda *_: QMessageBox.StandardButton.Yes)
    restart = Mock()
    dialog.restart_requested.connect(restart)
    assert not dialog.update_button.isEnabled()
    for button in (dialog.code_button, dialog.update_button):
        button.click()
        deadline = time.monotonic() + 10
        while not dialog.close_button.isEnabled() and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(0.005)
        assert dialog.close_button.isEnabled() and dialog.update_button.isEnabled(), dialog.status.text()
        assert dialog.list.count() == 1
    restart.assert_called_once()
    assert "up to date" in dialog.status.text()


def test_published_registrations_are_unique() -> None:
    """Check all published registration names, pack IDs, and install codes."""
    check_registry(json.loads((DOCS / "site-root/plugins.json").read_text(encoding="utf-8")))


@pytest.mark.parametrize(
    ("changed", "conflict"),
    [
        ({"name": " Ｖiola   STUDIO "}, "Plugin name"),
        ({"id": "viola"}, "Pack ID"),
        ({"code": "0042"}, "Registration code"),
    ],
)
def test_registration_conflicts(changed: dict[str, str], conflict: str) -> None:
    """
    Reject a single field collision within a proposal and against a removed registration.

    Parameters
    ----------
    changed : dict
        Field to reuse from the first registration.
    conflict : str
        Field identified in the validation error.
    """
    existing = ENTRY | {"name": "Viola Studio"}
    candidate = {"name": "Other", "id": "other", "code": "0043"} | changed
    with pytest.raises(ValueError, match=conflict):
        check_registry([existing, candidate])
    with pytest.raises(ValueError, match=conflict):
        check_registry([candidate], history=[[existing], []])


def test_registration_edits_keep_ownership() -> None:
    """Allow updates to the same plugin while reserving both its old and new display names."""
    original = ENTRY | {"name": "Viola Studio"}
    renamed = original | {"name": "String Studio"}
    other = {"name": "Viola Practice", "id": "viola-practice", "code": "24"}
    check_registry([renamed, other], history=[[original]])
    # An invalid earlier snapshot did not register its first entry, even if the conflict came later.
    rejected = [other | {"code": "80"}, other | {"name": original["name"]}]
    check_registry([other], history=[[original], rejected])
    check_registry([renamed | {"description": "New exercises"}], history=[[original], [renamed]])
    with pytest.raises(ValueError, match="Plugin name"):
        check_registry([other | {"name": original["name"]}], history=[[original], [renamed]])
    with pytest.raises(ValueError, match="Invalid Pack ID"):
        check_registry([other | {"id": "Viola Practice"}])


def serve(monkeypatch: pytest.MonkeyPatch, answers: dict[str, tuple[int, str]]) -> None:
    """
    Answer each metadata request with a status and a body.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replace the metadata transport.
    answers : dict of str to tuple of int and str
        The status and text for each address.
    """

    def fetch(url: str, *, seconds: int) -> tuple[int, str]:
        """
        Serve the planned answer.

        Parameters
        ----------
        url : str
            The requested address.
        seconds : int
            Request timeout.

        Returns
        -------
        tuple of int and str
            The status and the text.
        """
        return answers[url]

    monkeypatch.setattr(plugin_registry.updates, "fetch_text", fetch)


LATEST = f"https://api.github.com/repos/{REPO}/releases/latest"


def asset(**changes: object) -> dict[str, object]:
    """
    Describe a release asset that passes every check, with some fields changed.

    Parameters
    ----------
    **changes : object
        Fields to set or replace.

    Returns
    -------
    dict of str to object
        The asset.
    """
    return {"name": "viola.zip", "browser_download_url": ASSET} | changes


@pytest.mark.parametrize(
    ("registry", "message"),
    [
        ((503, "down"), "Could not read the Alto plugin registry: down"),
        ((200, "{"), "Invalid JSON"),
        ((200, '{"a": 1}'), "unreadable"),
        ((200, json.dumps([ENTRY, ENTRY])), "conflicting"),
        ((200, json.dumps([ENTRY | {"repository": "not a repository"}])), "public GitHub repository"),
    ],
)
def test_a_bad_registry_is_refused(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    registry: tuple[int, str],
    message: str,
) -> None:
    """
    Refuse an install code when the registry cannot be read or does not give a clear registration.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder.
    monkeypatch : pytest.MonkeyPatch
        Supply the registry.
    registry : tuple of int and str
        The status and text the registry answers with.
    message : str
        Part of the expected diagnostic.
    """
    serve(monkeypatch, {plugin_registry.REGISTRY_URL: registry})
    with pytest.raises(ValueError, match=message):
        plugin_registry.install_registered("0042", folder=tmp_path / "plugins")


def test_an_update_needs_an_installed_zip(tmp_path: Path) -> None:
    """
    Refuse to update an editable folder, which stays under its author's control.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder.
    """
    folder = tmp_path / "viola"
    folder.mkdir()
    (folder / "pack.json").write_text("{}")
    selected = InstalledPlugin(title="viola", path=folder, manifest=folder / "pack.json", snapshot=folder.lstat())
    with pytest.raises(ValueError, match="installed plugin ZIP"):
        plugin_registry.install_registered("", folder=tmp_path, selected=selected)


def test_an_update_follows_the_registration_it_was_installed_from(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Refuse an update when the registration for the installed code now names another pack.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder.
    monkeypatch : pytest.MonkeyPatch
        Supply the registry.
    """
    folder = tmp_path / "plugins"
    folder.mkdir()
    shutil.copyfile(VIOLA, folder / "registered-0042.zip")
    selected = installed_plugins(folder)[0][0]
    serve(monkeypatch, {plugin_registry.REGISTRY_URL: (200, json.dumps([ENTRY | {"id": "another"}]))})
    with pytest.raises(ValueError, match="no longer matches"):
        plugin_registry.install_registered("", folder=folder, selected=selected)


@pytest.mark.parametrize(
    ("latest", "message"),
    [
        ({"tag_name": ""}, "no published full release"),
        ({"tag_name": "summer"}, "no attached plugin ZIP"),
        ({"tag_name": "summer", "assets": [asset(browser_download_url="https://example.org/viola.zip")]}, "release asset in"),
        ({"tag_name": "summer", "assets": [asset(digest="md5:abc")]}, "invalid SHA-256 digest"),
    ],
)
def test_a_bad_release_is_refused(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    latest: dict,
    message: str,
) -> None:
    """
    Refuse a release that is not published, has no plugin ZIP, offers one from elsewhere, or has an invalid digest.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder.
    monkeypatch : pytest.MonkeyPatch
        Supply the registry and the release.
    latest : dict
        What the latest-release request returns.
    message : str
        Part of the expected diagnostic.
    """
    serve(monkeypatch, {plugin_registry.REGISTRY_URL: (200, json.dumps([ENTRY])), LATEST: (200, json.dumps(latest))})
    with pytest.raises(ValueError, match=message):
        plugin_registry.install_registered("0042", folder=tmp_path / "plugins")
