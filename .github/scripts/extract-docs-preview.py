#!/usr/bin/env python3
"""Copy regular site files from a PR artifact into a fresh directory for publication."""

import shutil
import stat
import sys
from pathlib import Path
from zipfile import ZipFile

archive, destination = map(Path, sys.argv[1:])
destination.mkdir()
with ZipFile(archive) as site:
    if sum(member.file_size for member in site.infolist()) > 512 * 1024**2:
        sys.exit("Preview exceeds the 512 MiB unpacked size limit.")
    for member in site.infolist():
        parts = member.filename.rstrip("/").split("/")
        if any(not part or part.startswith(".") or "\\" in part for part in parts):
            sys.exit("Unexpected path in the preview artifact.")
        if member.is_dir():
            continue
        kind = stat.S_IFMT(member.external_attr >> 16)
        if kind not in (0, stat.S_IFREG):
            sys.exit("Only regular site files can be published.")
        target = destination.joinpath(*parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        with site.open(member) as source, target.open("xb") as output:
            shutil.copyfileobj(source, output)
