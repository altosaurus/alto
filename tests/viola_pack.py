"""
The viola example plugin that the plugin tests install, read and edit.

The pack's manifest and its animation are kept here, as a test fixture.
Its recordings, photographs and icon are made when the
tests run (see `pack_fixtures`), because the plugin's author provides
the real ones. The tutorial that teaches how to build
it, and the ZIP that readers download, live in the
`viola-plugin-tutorial` repository, and the docs bring in only what the
tutorial page shows.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from pack_fixtures import ensure_icons, ensure_pictures, ensure_sounds

FOLDER = Path(__file__).resolve().parent / "packs" / "viola"
MANIFEST = FOLDER / "pack.json"
# The tutorial page, once `scripts/tutorial_docs.py viola` has brought
# it into the docs. Tests of the manifests printed in it
# run only then.
TUTORIAL = Path(__file__).resolve().parents[1] / "docs/plugins/viola.md"
needs_tutorial = pytest.mark.skipif(
    not TUTORIAL.is_file(),
    reason=(
        "Bring in the viola tutorial first: python "
        "scripts/tutorial_docs.py viola --from ../viola-plugin-tutorial"
    ),
)

ensure_sounds(
    FOLDER,
    seconds=1.0,
)  # the pack's recordings, as one second of tone each
ensure_icons(FOLDER)  # and its tile icon, as a plain one
ensure_pictures(
    FOLDER,
)  # and its photographs, as plain pictures with a dark band where the neck is


def archive() -> Path:
    """
    Zip the viola pack as a reader's download would be, with `pack.json`
    at the root, and keep the ZIP for the whole test run.

    Returns
    -------
    Path
        A `viola.zip` in the system's temporary folder. A pack whose
        files changed gets a new one.

    Examples
    --------
    >>> archive().name
    'viola.zip'
    """
    files = sorted(path for path in FOLDER.rglob("*") if path.is_file())
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.relative_to(FOLDER).as_posix().encode())
        digest.update(path.read_bytes())
    target = (
        Path(tempfile.gettempdir())
        / f"alto-test-viola-{digest.hexdigest()[:16]}"
        / "viola.zip"
    )
    if not target.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        partial = target.with_name(f"viola.{os.getpid()}.part")
        with ZipFile(partial, "w", ZIP_DEFLATED) as bundle:
            for path in files:
                bundle.write(path, path.relative_to(FOLDER))
        partial.replace(
            target,
        )  # one process at a time wins; the others find the finished file
    return target


ZIP = archive()
