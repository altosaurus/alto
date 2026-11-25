#!/usr/bin/env python3
"""Confirm historical ASV slowdowns on one runner."""

import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from collections.abc import Iterator
from pathlib import Path


def _timings(table: str) -> Iterator[tuple[str, str, str]]:
    """
    Read comparable timing rows from an ASV Markdown table.

    Parameters
    ----------
    table : str
        Output from ASV compare.

    Yields
    ------
    tuple[str, str, str]
        Parameterized benchmark name, change marker, and original row.
    """
    for line in table.splitlines():
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 5:
            continue
        mark, _, _, ratio, benchmark = cells
        if mark in {"", "+", "-"} and ratio != "n/a":
            # Drop ASV’s optional [machine/environment] suffix.
            yield benchmark.partition(" [")[0], mark, line


def _confirm(previous: str, *, history: Path, report: Path) -> None:
    """
    Write a Markdown table of the slowdowns that reproduce.

    Parameters
    ----------
    previous : str
        Previous release tag.
    history : Path
        Archived comparison for the release and candidate.
    report : Path
        Destination for confirmed rows, empty when none reproduce.
    """
    flagged = {
        name for name, mark, _ in _timings(history.read_text()) if mark == "+"
    }
    if not flagged:
        report.write_text("")
        return

    root = Path.cwd()
    config = json.loads((root / "asv.conf.json").read_text())
    pattern = "^(?:" + "|".join(map(re.escape, sorted(flagged))) + ")$"
    machine = ["--machine", os.environ["MACHINE"]]
    asv = [sys.executable, "-m", "asv"]
    with tempfile.TemporaryDirectory() as directory:
        scratch = Path(directory)
        config.update(repo=str(root), results_dir=str(scratch / "results"))
        for ref in (previous, "HEAD"):
            sha = subprocess.check_output(
                ["git", "rev-parse", f"{ref}^{{commit}}"],
                text=True,
            ).strip()
            source = scratch / sha
            source.mkdir()
            archive = scratch / "alto.tar"
            subprocess.run(
                ["git", "archive", "-o", archive, sha, "alto"],
                check=True,
            )
            with tarfile.open(archive) as package:
                package.extractall(source, filter="data")
            shutil.copytree(
                root / config["benchmark_dir"],
                source / config["benchmark_dir"],
            )
            (source / "asv.conf.json").write_text(json.dumps(config))
            # Use this source in the workers and cold-start children.
            subprocess.run(
                [
                    *asv,
                    "run",
                    *machine,
                    "-E",
                    f"existing:{sys.executable}",
                    "--set-commit-hash",
                    sha,
                    "--bench",
                    pattern,
                    "--show-stderr",
                ],
                cwd=source,
                env={**os.environ, "ASV_PYTHONPATH": str(source)},
                check=True,
            )
        table = subprocess.check_output(
            [
                *asv,
                "compare",
                *machine,
                "--factor",
                "1.3",
                "--split",
                previous,
                "HEAD",
            ],
            cwd=source,
            text=True,
        )
    timings = {name: (mark, row) for name, mark, row in _timings(table)}
    missing = flagged.difference(timings)
    if missing:
        sys.exit("Missing paired timings for " + ", ".join(sorted(missing)))
    confirmed = [
        row
        for name, (mark, row) in timings.items()
        if name in flagged and mark == "+"
    ]
    header = [line for line in table.splitlines() if line.startswith("|")][:2]
    report.write_text(
        "\n".join([*header, *confirmed]) + "\n" if confirmed else "",
    )


if __name__ == "__main__":
    _confirm(sys.argv[1], history=Path(sys.argv[2]), report=Path(sys.argv[3]))
