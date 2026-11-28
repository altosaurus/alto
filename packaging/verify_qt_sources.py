#!/usr/bin/env python3
"""Match the published Qt source companions to an installed package."""

import hashlib
import re
import sys
from pathlib import Path


def verify(readme_path: Path, *, sources: Path) -> None:
    """
    Check both archives against the installed Qt notice.

    Parameters
    ----------
    readme_path : Path
        Installed licenses/Qt/README.txt.
    sources : Path
        Directory containing the source companions.

    Raises
    ------
    ValueError
        If a required archive is missing or its checksum differs.
    """
    archives = sorted(sources.glob("*-everywhere-src-*.tar.xz"))
    if len(archives) != 2:
        raise ValueError("Expected separate Qt and Qt for Python sources")
    readme = readme_path.read_text(encoding="utf-8")
    for source in archives:
        with source.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if not re.search(
            re.escape(source.name) + r"\n[^\n]+\nSHA-256 " + digest,
            readme,
        ):
            raise ValueError(f"Source mismatch: {source.name}")


if __name__ == "__main__":
    verify(Path(sys.argv[1]), sources=Path(sys.argv[2]))
