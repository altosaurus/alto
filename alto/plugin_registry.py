"""Install registered instrument packs from the latest release in their public GitHub repositories."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from tempfile import TemporaryDirectory

from alto import selfupdate, updates
from alto.exercises.packs import InstalledPlugin, install_pack, installed_pack_info
from alto.instrument_packs import identifier

REGISTRY_URL = "https://altosaurus.github.io/alto/plugins.json"


def _json(url: str, *, description: str) -> object:
    """
    Read the registry or the latest release and identify failed requests in the dialog.

    Returns
    -------
    object
        The decoded JSON response.

    Raises
    ------
    ValueError
        If the server cannot supply the requested JSON.
    """
    status, text = updates.fetch_text(url, seconds=20)
    if status != 200:
        raise ValueError(f"Could not read {description}: {text or status}.")
    try:
        return json.loads(text)
    except ValueError as error:
        raise ValueError(f"Invalid JSON in {description}.") from error


def _registration(code: str, *, selected: InstalledPlugin | None) -> tuple[str, str, str]:
    """
    Resolve an install code or the selected ZIP's pack ID in the shared registry.

    Returns
    -------
    tuple of str, str, str
        Registration code, pack ID, and GitHub owner/repository.

    Raises
    ------
    ValueError
        If the registration is missing, ambiguous, or incomplete.
    """
    field, value = "code", code.strip()
    installed_id = None
    if selected is not None:
        if selected.path != selected.manifest or selected.path.is_symlink():
            raise ValueError("Select an installed plugin ZIP to update.")
        installed_id = identifier(installed_pack_info(selected.manifest).get("id"))
        receipt = re.fullmatch(r"registered-([0-9]+)\.zip", selected.path.name)
        if receipt:
            value = receipt[1]
        else:
            field, value = "id", installed_id
    elif not re.fullmatch(r"[0-9]+", value):
        raise ValueError("Enter the numeric code shown in the plugin registry.")
    entries = _json(REGISTRY_URL, description="the Alto plugin registry")
    if not isinstance(entries, list):
        raise ValueError("The plugin registry is unreadable.")
    matches = [row for row in entries if isinstance(row, dict) and row.get(field) == value]
    if not matches:
        raise ValueError(f"No registered plugin has {field} {value}.")
    if len(matches) != 1:
        raise ValueError("The plugin registry contains conflicting registrations.")
    row = matches[0]
    pack_id = identifier(row.get("id"))
    if installed_id is not None and installed_id != pack_id:
        raise ValueError("The registration code no longer matches the installed pack ID.")
    registered_code = row.get("code")
    repository = row.get("repository")
    address = (
        re.fullmatch(r"https://github\.com/([\w-]+/[\w.-]+)/?", repository, re.ASCII) if isinstance(repository, str) else None
    )
    if (
        not isinstance(registered_code, str)
        or not re.fullmatch(r"[0-9]+", registered_code)
        or not address
        or address[1].split("/")[1] in (".", "..")
    ):
        raise ValueError("This registration needs a numeric code and a public GitHub repository.")
    return registered_code, pack_id, address[1]


def install_registered(code: str, *, folder: Path, selected: InstalledPlugin | None = None) -> str | None:
    """
    Install by registration code, or update a selected ZIP from its registered repository.

    Parameters
    ----------
    code : str
        The published code, including any leading zeros. Updates recover the code from the installation or its registered pack ID.
    folder : Path
        The plugins directory.
    selected : InstalledPlugin or None
        The installed ZIP to update. Editable directories stay under the author's control.

    Returns
    -------
    str or None
        The installed pack name and release tag, or None if the installed ZIP already matches the latest asset.

    Raises
    ------
    ValueError
        If registration, release selection, integrity checks, or pack validation fails.
    """
    registered_code, pack_id, repo = _registration(code, selected=selected)
    release = _json(f"https://api.github.com/repos/{repo}/releases/latest", description=f"the latest release of {repo}")
    if not isinstance(release, dict) or release.get("draft") or release.get("prerelease") or not release.get("tag_name"):
        raise ValueError(f"{repo} has no published full release.")
    assets = release.get("assets")
    if not isinstance(assets, list):
        raise ValueError("The release has no attached plugin ZIP.")
    zips = [a for a in assets if isinstance(a, dict) and str(a.get("name")).lower().endswith(".zip")]
    candidates = [a for a in zips if a["name"] == f"{pack_id}.zip"] or zips
    if len(candidates) != 1:
        raise ValueError(f"Attach one plugin ZIP to the release, or name its asset {pack_id}.zip.")
    asset = candidates[0]
    allowed = f"https://github.com/{repo}/releases/download/"
    url = asset.get("browser_download_url")
    if not isinstance(url, str) or not url.startswith(allowed):
        raise ValueError("The plugin ZIP must be a release asset in its registered repository.")
    expected = asset.get("digest")
    if expected is not None and (not isinstance(expected, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", expected)):
        raise ValueError("The release asset has an invalid SHA-256 digest.")
    installed_hash = None
    if selected is not None:
        with selected.path.open("rb") as existing:
            installed_hash = hashlib.file_digest(existing, "sha256").hexdigest()
        if expected == f"sha256:{installed_hash}":
            return None
    with TemporaryDirectory(prefix="alto-plugin-") as work:
        source = Path(work) / f"registered-{registered_code}.zip"
        actual = selfupdate.download(
            url,
            destination=source,
            allowed=allowed,
            max_bytes=256 * 1024**2,
            progress=lambda *_: None,
            canceled=lambda: False,
        )
        if expected is not None and expected != f"sha256:{actual}":
            raise ValueError("The downloaded ZIP does not match its release digest.")
        if actual == installed_hash:
            return None
        name = install_pack(source, folder=folder, expected_id=pack_id, replacing=selected)
    return f"{name} ({release['tag_name']})"
