#!/usr/bin/env python3
"""Audit the unpacked Mac application and its source downloads."""

import hashlib
import re
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile


def check(app: Path, *, sources: Path) -> None:
    """
    Verify installed assets, Mach-O dependencies, and source archives.

    Parameters
    ----------
    app : Path
        Unpacked or mounted Alto.app.
    sources : Path
        Corresponding source archives from this build.

    Raises
    ------
    ValueError
        If a file, source checksum, or library reference fails a check.
    """
    resources = app / "Contents/Resources"
    root = Path(__file__).resolve().parents[2]
    assets = Path("alto/assets")
    for directory in (root / assets, resources / assets):
        expected = {
            p.relative_to(directory)
            for p in directory.rglob("*")
            if p.is_file()
        }
        for name in expected:
            if (root / assets / name).read_bytes() != (
                resources / assets / name
            ).read_bytes():
                raise ValueError(f"Asset mismatch: {name}")
    forbidden = re.compile(
        r"QtPdf(?:\.framework)?$|libqpdf\.dylib$|ffmpeg|"
        r"lib(?:avcodec|avformat|avutil|swresample|swscale)[.\d]*\.dylib$",
        re.IGNORECASE,
    )
    native = []
    for path in (app / "Contents").rglob("*"):
        if forbidden.search(path.name) or (
            path.is_symlink() and not path.exists()
        ):
            raise ValueError(f"Unexpected file or broken link: {path}")
        if path.is_file() and not path.is_symlink():
            with path.open("rb") as stream:
                if stream.read(4) == bytes.fromhex("cffaedfe"):
                    native.append(path)
    if not native:
        raise ValueError("No arm64 Mach-O binaries found")
    links = subprocess.check_output(["otool", "-L", *native], text=True)
    for line in links.splitlines():
        if line.startswith("\t"):
            library = line.strip().split(" (", 1)[0]
            if any(forbidden.search(part) for part in Path(library).parts):
                raise ValueError(f"Excluded library still linked: {library}")

    qt = resources / "licenses/Qt"
    for filename, text in (
        ("LGPL-3.0-only.txt", "LESSER GENERAL PUBLIC LICENSE"),
        ("GPL-3.0-only.txt", "GENERAL PUBLIC LICENSE"),
    ):
        if text not in (qt / filename).read_text():
            raise ValueError(f"Incorrect license: {filename}")
    with ZipFile(qt / "upstream-notices.zip") as archive:
        if archive.testzip() or not any(
            n.endswith("qt_attribution.json") for n in archive.namelist()
        ):
            raise ValueError("Invalid Qt notice archive")
    archives = sorted(sources.glob("*-everywhere-src-*.tar.xz"))
    if len(archives) != 2:
        raise ValueError("Expected separate Qt and Qt for Python sources")
    readme = (qt / "README.txt").read_text()
    for source in archives:
        with source.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if not re.search(
            re.escape(source.name) + r"\n[^\n]+\nSHA-256 " + digest,
            readme,
        ):
            raise ValueError(f"Source mismatch: {source.name}")
    print(
        f"Verified {len(native)} Mach-O files, assets, and Qt distribution.",
    )


if __name__ == "__main__":
    check(Path(sys.argv[1]), sources=Path(sys.argv[2]))
