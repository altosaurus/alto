#!/usr/bin/env python
"""
Write the icons of the exercises for the docs, from the icons the app
draws on its home screen.

    python scripts/exercise_icons.py            # rewrite
    docs/_includes/exercise-icons.html
    python scripts/exercise_icons.py --check    # fail if it is out of
    date, changing nothing

The app draws each exercise's icon from a few lines of SVG in
`alto/ui/icons.py`, tinted with the theme's text color. The home
page of the docs shows the same icons beside the names of the exercises,
so this writes them as an SVG sprite that the page
includes, with `currentColor` where the app has its tint, so that they
follow the docs' light and dark themes by themselves.
`tests/test_docs.py` fails when the file is out of date.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault(
    "QT_QPA_PLATFORM",
    "offscreen",
)  # importing the app's screens needs no display, but Qt wants to be told

from alto.exercises import REGISTRY  # noqa: E402
from alto.ui.home import EXERCISE_ICONS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "_includes" / "exercise-icons.html"
HEADER = (
    "{% comment %}\n"
    "  The icons of the exercises, as the app draws them. Written by "
    "scripts/exercise_icons.py: change the icons in\n"
    "  alto/ui/icons.py and run the script, not this file.\n"
    "{% endcomment %}\n"
)


def render() -> str:
    """
    Make the sprite: a symbol for each exercise, in the order of the
    home screen, with the id `ex-` and its class name.

    Returns
    -------
    str
        The text of the include.

    Examples
    --------
    >>> text = render()
    >>> (
    ...     '<symbol id="ex-NoteNames" viewBox="0 0 24 24">' in text
    ...     and "COLOR" not in text
    ... )
    True
    """
    symbols = []
    for cls in REGISTRY:
        inner = EXERCISE_ICONS[cls.__name__].replace("COLOR", "currentColor")
        if cls.__name__ == "KeyboardNotes":
            # Let the card show through the long keys and tint the short
            # keys and outlines.
            inner = inner.replace("#ffffff", "none").replace(
                "#202020",
                "currentColor",
            )
        symbols.append(
            '  <symbol id="ex-'
            f"{cls.__name__}"
            '" viewBox="0 0 24 24">'
            f"{inner}"
            "</symbol>\n",
        )
    wrapper = (
        '<svg width="0" height="0" style="position:absolute" '
        'aria-hidden="true" focusable="false">\n'
    )
    return HEADER + wrapper + "".join(symbols) + "</svg>\n"


def main(argv: list[str] | None = None) -> int:
    """
    Write the include, or with `--check` say whether it is up to date.

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
    >>> main(["--check", "--file", "/no/such/file"])
    docs/_includes/exercise-icons.html is out of date: run
    scripts/exercise_icons.py
    1
    """
    parser = argparse.ArgumentParser(
        description="Write the exercise icons for the docs.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the file is out of date, and change nothing",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=OUT,
        help="the file to write (default: docs/_includes/exercise-icons.html)",
    )
    arguments = parser.parse_args(argv)
    text = render()
    if arguments.check:
        current = (
            arguments.file.read_text(encoding="utf-8")
            if arguments.file.is_file()
            else None
        )
        if current != text:
            print(
                (
                    "docs/_includes/exercise-icons.html is out of date: "
                    "run scripts/exercise_icons.py"
                ),
            )
            return 1
        return 0
    arguments.file.parent.mkdir(parents=True, exist_ok=True)
    arguments.file.write_text(text, encoding="utf-8")
    print(f"wrote {len(REGISTRY)} icons to {arguments.file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
