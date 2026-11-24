#!/usr/bin/env python3
"""
Bring the plugin tutorials into the docs site from their own
repositories.

A tutorial page and the pictures and downloads it shows live in a
repository of their own: `altosaurus/viola-plugin-tutorial`
and `altosaurus/harpsichord-plugin-tutorial`. Each mirrors the paths of
Alto's `docs/` folder, and Alto keeps no copy. The Docs
workflows run this script before Jekyll builds, and it copies in each
page and only the files the page refers to, so the site
publishes nothing else from the tutorial repositories: no loose sound
files, no screenshots meant for a README.

To preview the docs on your own machine, bring them all in once, which
clones them from GitHub:

    python scripts/tutorial_docs.py all

or take one from a checkout of your own, to try a change before you push
it:

    python scripts/tutorial_docs.py harpsichord --from
    ../harpsichord-plugin-tutorial

The files it writes are listed in `.gitignore`, so they are never
committed to Alto.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# Each tutorial: the page it adds to the site, and the repository it
# comes from.
TUTORIALS = {
    "viola": (
        "plugins/viola.md",
        "https://github.com/altosaurus/viola-plugin-tutorial.git",
    ),
    "harpsichord": (
        "plugins/harpsichord.md",
        "https://github.com/altosaurus/harpsichord-plugin-tutorial.git",
    ),
}


# A file the page offers or shows with relative_url, or a screenshot it
# includes with shot.html.
USES = re.compile(
    (
        "\\{\\{\\s*['\"]/(assets/[^'\"]+)['\"]\\s*\\|\\s*relative_url\\s*}}|shot\\.ht"
        'ml src="([^"]+\\.png)\\x22'
    ),
)


def references(page: str) -> list[str]:
    """
    List the files a tutorial page shows or offers, as paths under the
    docs folder.

    Parameters
    ----------
    page : str
        The text of the page.

    Returns
    -------
    list of str
        Each path once, in the order the page first uses it. A picture
        included with `shot.html` is listed in both its light
        and its dark form.

    Examples
    --------
    >>> text = (
    ...     '[zip]({{ "/assets/plugins/a.zip" | relative_url }}) {% '
    ...     'include shot.html src="b.png" alt="x" %}'
    ... )
    >>> references(text)
    ['assets/plugins/a.zip', 'assets/img/b.png',
    'assets/img/b-dark.png']
    """
    found: dict[str, None] = {}
    for match in USES.finditer(page):
        if match.group(1):
            found[match.group(1)] = None
        else:
            found[f"assets/img/{match.group(2)}"] = None
            found[
                f"assets/img/{match.group(2).removesuffix('.png')}-dark.png"
            ] = None
    return list(found)


def bring_in(name: str, *, source: Path, docs: Path = DOCS) -> list[str]:
    """
    Copy a tutorial's page and the files it refers to into the docs
    folder.

    Parameters
    ----------
    name : str
        The tutorial, a key of `TUTORIALS`.
    source : Path
        A checkout of the tutorial's repository.
    docs : Path, default the docs folder of this checkout
        The docs folder to copy into. Keyword-only.

    Returns
    -------
    list of str
        The paths copied, relative to the docs folder, the page first.

    Raises
    ------
    FileNotFoundError
        If the page, or a file it refers to, is missing from the
        tutorial.

    Examples
    --------
    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     base = Path(tmp)
    ...     (base / "t/docs/plugins").mkdir(
    ...         parents=True
    ...     )
    ...     _ = (
    ...         base / "t/docs/plugins/viola.md"
    ...     ).write_text("No pictures here.")
    ...     bring_in(
    ...         "viola",
    ...         source=base / "t",
    ...         docs=base / "d",
    ...     )
    ['plugins/viola.md']
    """
    page, _ = TUTORIALS[name]
    text = (source / "docs" / page).read_text(encoding="utf-8")
    copied = [page]
    for path in references(text):
        if not (source / "docs" / path).is_file():
            raise FileNotFoundError(
                "The "
                f"{name}"
                " tutorial's page refers to docs/"
                f"{path}"
                ", which the repository does not have.",
            )
        copied.append(path)
    for path in copied:
        target = docs / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / "docs" / path, target)
    return copied


def main(argv: list[str] | None = None) -> int:
    """
    Run the command named on the command line.

    Parameters
    ----------
    argv : list of str or None, default None
        The arguments after the program's name; those the program was
        started with if None.

    Returns
    -------
    int
        0 on success; 1 if the tutorial cannot be fetched or is
        incomplete.

    Examples
    --------
    >>> main(["viola", "--from", "/no/such/folder"])
    The viola tutorial is not at /no/such/folder.
    1
    """
    parser = argparse.ArgumentParser(
        description="Bring the plugin tutorials into the docs.",
    )
    parser.add_argument(
        "tutorial",
        choices=[*TUTORIALS, "all"],
        help="the tutorial to bring in",
    )
    parser.add_argument(
        "--from",
        dest="source",
        type=Path,
        help="a checkout of the tutorial (default: clone it from GitHub)",
    )
    parser.add_argument(
        "--docs",
        type=Path,
        default=DOCS,
        help="the docs folder to copy into (default: this checkout's)",
    )
    arguments = parser.parse_args(argv)
    names = (
        list(TUTORIALS)
        if arguments.tutorial == "all"
        else [arguments.tutorial]
    )
    for name in names:
        with tempfile.TemporaryDirectory() as tmp:
            source = arguments.source
            if source is None:
                source = Path(tmp) / name
                clone = [
                    "git",
                    "clone",
                    "--quiet",
                    "--depth",
                    "1",
                    TUTORIALS[name][1],
                    str(source),
                ]
                if subprocess.run(clone, check=False).returncode:
                    print(
                        "Could not clone the "
                        f"{name}"
                        " tutorial from "
                        f"{TUTORIALS[name][1]}"
                        ".",
                        file=sys.stderr,
                    )
                    return 1
            if not (source / "docs" / TUTORIALS[name][0]).is_file():
                print(f"The {name} tutorial is not at {source}.")
                return 1
            try:
                copied = bring_in(name, source=source, docs=arguments.docs)
            except FileNotFoundError as problem:
                print(problem, file=sys.stderr)
                return 1
        print(
            "The "
            f"{name}"
            " tutorial: "
            f"{len(copied)}"
            " files copied into "
            f"{arguments.docs}"
            ".",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
