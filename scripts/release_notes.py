#!/usr/bin/env python
"""
Write the Release notes page of the docs from CHANGELOG.md.

    python scripts/release_notes.py            # rewrite
    docs/release-notes.md
    python scripts/release_notes.py --check    # fail if it is out of
    date, changing nothing

`CHANGELOG.md` is the one place where release notes are written. The
docs page is made from it so that the two cannot differ:
a heading for each version, newest first, with its date and a link to
its GitHub release, and the Unreleased changes at the top
while there are any. The page is committed, because GitHub Pages cannot
run this script, and `tests/test_docs_site.py` fails when
it is out of date, so a change to the changelog comes with a new page in
the same pull request. A docs build of a release carries
the notes up to that release.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"
OUT = ROOT / "docs" / "release-notes.md"
RELEASES = "https://github.com/altosaurus/alto/releases/tag/v"
HEADING = re.compile(
    r"^## \[(?P<name>[^]]+)](?: - (?P<date>\d{4}-\d{2}-\d{2}))?[ \t]*$",
    re.MULTILINE,
)
LINK_DEFINITION = re.compile(r"^\[[^]]+]:\s+\S+[ \t]*$")
FRONT_MATTER = """---
title: Release notes
nav_order: 11.8
nav_group: About
permalink: /release-notes/
---
"""
INTRO = (
    "All notable changes to Alto, newest first. The format follows\n"
    "[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and Alto"
    " uses [semantic versioning](https://semver.org/).\n"
    "Each release's downloads are on its GitHub release.\n"
)


def sections(text: str) -> list[tuple[str, str | None, str]]:
    r"""
    Cut a changelog into its versions.

    A version starts at its `## [name]` heading and ends at the next
    one. The link definitions that close the file are not part of
    the last version.

    Parameters
    ----------
    text : str
        The changelog.

    Returns
    -------
    list of tuple of (str, str or None, str)
        For each version, in the order of the file: its name
        ("Unreleased" or such as "0.0.0"), its date (None if it has
        none) and
        its notes, without the blank lines around them.

    Examples
    --------
    >>> log = (
    ...     "# Changelog\n\n## [Unreleased]\n\n## [0.1.0] - 2026-12-01"
    ...     "\n\nNotes.\n\n- One.\n\n[0.1.0]: https://example.org\n"
    ... )
    >>> sections(log)
    [('Unreleased', None, ''), ('0.1.0', '2026-12-01', 'Notes.\n\n-
    One.')]
    """
    found = list(HEADING.finditer(text))
    result = []
    for number, heading in enumerate(found):
        end = (
            found[number + 1].start() if number + 1 < len(found) else len(text)
        )
        lines = text[heading.end() : end].splitlines()
        while lines and (
            not lines[-1].strip() or LINK_DEFINITION.match(lines[-1])
        ):
            lines.pop()
        result.append(
            (
                heading.group("name"),
                heading.group("date"),
                "\n".join(lines).strip(),
            ),
        )
    return result


def untitled(notes: str) -> str:
    r"""
    Keep the headings of a version's notes out of the page's "On this
    page" list, which is for the versions.

    Parameters
    ----------
    notes : str
        A version's notes.

    Returns
    -------
    str
        The notes, with a marker after each `###` heading.

    Examples
    --------
    >>> print(untitled("### Added\n\n- One."))
    ### Added
    {: .no-toc}
    <BLANKLINE>
    - One.
    """
    out = []
    for line in notes.splitlines():
        out.append(line)
        if line.startswith("### "):
            out.append("{: .no-toc}")
    return "\n".join(out)


def render(text: str) -> str:
    r"""
    Make the page: its front matter, an introduction, and a heading with
    the notes for each version.

    Unreleased changes are shown at the top while there are any, and
    left out when there are none. The notes are wrapped in
    Liquid's `raw` tags, so that nothing in the changelog is mistaken
    for Liquid.

    Parameters
    ----------
    text : str
        The changelog.

    Returns
    -------
    str
        The text of `docs/release-notes.md`.

    Examples
    --------
    >>> log = (
    ...     "# Changelog\n\n## [Unreleased]\n\n## [0.1.0] - 2026-12-01"
    ...     "\n\nNotes.\n"
    ... )
    >>> page = render(log)
    >>> (
    ...     "## Unreleased" in page,
    ...     "## 0.1.0" in page,
    ...     "Released 2026-12-01" in page,
    ... )
    (False, True, True)
    """
    body = []
    for name, date, notes in sections(text):
        if name == "Unreleased":
            if notes:
                body.append(
                    "## Unreleased\n\nChanges that are in the development "
                    "docs and not in a release yet.\n\n"
                    f"{untitled(notes)}"
                    "\n",
                )
            continue
        when = f"Released {date}. " if date else ""
        body.append(
            "## "
            f"{name}"
            "\n\n"
            f"{when}"
            "[GitHub release]("
            f"{RELEASES}"
            f"{name}"
            ")\n\n"
            f"{untitled(notes)}"
            "\n",
        )
    header = (
        "{% comment %}\n"
        "  The release notes of Alto. Written by "
        "scripts/release_notes.py from CHANGELOG.md: change the "
        "changelog and run\n"
        "  the script, not this file.\n"
        "{% endcomment %}\n"
    )
    return (
        FRONT_MATTER
        + header
        + "{% raw %}\n"
        + INTRO
        + "\n"
        + "\n".join(body)
        + "{% endraw %}\n"
    )


def main(argv: list[str] | None = None) -> int:
    """
    Write the page, or with `--check` say whether it is up to date.

    Parameters
    ----------
    argv : list of str or None, default None
        The arguments after the program's name; those the program was
        started with if None.

    Returns
    -------
    int
        0 if it was written or is up to date, 1 if `--check` found it
        out of date.

    Examples
    --------
    >>> main(["--check", "--out", "/no/such/file"])
    docs/release-notes.md is out of date: run scripts/release_notes.py
    1
    """
    parser = argparse.ArgumentParser(
        description=(
            "Write the release notes page of the docs from the changelog."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the page is out of date, and change nothing",
    )
    parser.add_argument(
        "--changelog",
        type=Path,
        default=CHANGELOG,
        help="the changelog to read (default: CHANGELOG.md)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=OUT,
        help="the page to write (default: docs/release-notes.md)",
    )
    arguments = parser.parse_args(argv)
    page = render(arguments.changelog.read_text(encoding="utf-8"))
    if arguments.check:
        current = (
            arguments.out.read_text(encoding="utf-8")
            if arguments.out.is_file()
            else None
        )
        if current != page:
            print(
                (
                    "docs/release-notes.md is out of date: run "
                    "scripts/release_notes.py"
                ),
            )
            return 1
        return 0
    arguments.out.write_text(page, encoding="utf-8")
    print(f"wrote {arguments.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
