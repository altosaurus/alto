#!/usr/bin/env python
"""
Print one version's section of CHANGELOG.md, to be used as the notes of
a GitHub release.

    python scripts/changelog_section.py 0.0.0         # the notes of
    version 0.0.0 (a leading "v", as in a tag, is fine)
    python scripts/changelog_section.py Unreleased    # what is waiting
    for the next release

It prints the notes without their heading and exits with 0. If there is
no such section, or it is empty, it prints nothing to
standard output, says why on standard error and exits with 1, so a
release cannot go out with no notes.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"
LINK_DEFINITION = re.compile(r"^\[[^]]+]:\s+\S+")


def section(
    text: str,
    *,
    version: str,
) -> str | None:
    r"""
    Cut one version's notes out of a changelog.

    A section starts at its `## [version]` heading and ends at the next
    `## [` heading or at the link definitions that close the
    file. The heading itself is not part of it.

    Parameters
    ----------
    text : str
        The whole changelog.
    version : str
        The version, such as "0.0.0", or "Unreleased". Keyword-only.

    Returns
    -------
    str or None
        The notes, without the blank lines around them; empty if the
        section has nothing in it; None if there is no such section.

    Examples
    --------
    >>> log = (
    ...     "# Changelog\n\n## [Unreleased]\n\n## [0.1.0] - 2026-12-01"
    ...     "\n\nNotes.\n\n- One.\n\n[0.1.0]: https://example.org\n"
    ... )
    >>> section(log, version="0.1.0")
    'Notes.\n\n- One.'
    >>> section(log, version="Unreleased")
    ''
    >>> section(log, version="9.9.9") is None
    True
    """
    heading = re.compile(rf"^## \[{re.escape(version)}](?: - .*)?\s*$")
    lines = text.splitlines()
    for number, line in enumerate(lines):
        if heading.match(line):
            body: list[str] = []
            for after in lines[number + 1 :]:
                if after.startswith("## [") or LINK_DEFINITION.match(after):
                    break
                body.append(after)
            return "\n".join(body).strip()
    return None


def main(argv: list[str] | None = None) -> int:
    """
    Print the notes of the version named on the command line.

    Parameters
    ----------
    argv : list of str or None, default None
        The arguments after the program's name; those the program was
        started with if None.

    Returns
    -------
    int
        0 if the notes were printed, 1 if there is no such section or it
        is empty.

    Examples
    --------
    >>> main(["--file", "/no/such/file", "0.0.0"])
    1
    """
    parser = argparse.ArgumentParser(
        description="Print one version's section of the changelog.",
    )
    parser.add_argument(
        "version",
        help='a version such as 0.0.0 or v0.0.0, or "Unreleased"',
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=CHANGELOG,
        help="the changelog to read (default: CHANGELOG.md)",
    )
    arguments = parser.parse_args(argv)
    try:
        text = arguments.file.read_text(encoding="utf-8")
    except OSError as error:
        print(
            f"Could not read {arguments.file}: {error.strerror or error}",
            file=sys.stderr,
        )
        return 1
    version = arguments.version.removeprefix("v")
    notes = section(text, version=version)
    if notes is None:
        print(
            f"{arguments.file} has no section for {version}.",
            file=sys.stderr,
        )
        return 1
    if not notes:
        print(
            f"The section for {version} in {arguments.file} is empty.",
            file=sys.stderr,
        )
        return 1
    print(notes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
