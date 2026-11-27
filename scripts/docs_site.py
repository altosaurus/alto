#!/usr/bin/env python
"""
Put together the published docs: one folder for each release, one for
the development version, and the files that belong to none.

The Docs workflow builds each version with Sphinx into its own folder of
a checkout of the `gh-pages` branch, and then runs this
to write what sits around them:

    python scripts/docs_site.py finish SITE --root-files docs/site-root
    --site-url https://altosaurus.github.io/alto
    python scripts/docs_site.py latest v0.0.0 v0.1.0 v0.1.1-rc1     #
    prints v0.1.0, the newest release that is not a pre-release

`finish` installs a staged stable build at the site root and writes the
version list and shared files. Old `latest/` page URLs redirect to the
root copy.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from html import escape
from pathlib import Path
from urllib.parse import quote, urlparse

VERSION = re.compile(r"^v(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?$")
DEV = "dev"
LATEST = "latest"
STABLE_MANIFEST = ".stable-docs.json"
REDIRECT = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Alto</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="canonical" href="{canonical}">
  <script>
    var target = document.querySelector('link[rel="canonical"]').href;
    location.replace(target + location.search + location.hash);
  </script>
  <meta http-equiv="refresh" content="0; url={target}">
</head>
<body>
  <p>Going to the <a href="{target}">{what}</a>.</p>
</body>
</html>
"""


def parse_version(tag: str) -> tuple[tuple[int, int, int], str | None] | None:
    """
    Split a release tag into its numbers and its pre-release label.

    Parameters
    ----------
    tag : str
        A tag such as "v0.1.0" or "v1.0.0-rc1".

    Returns
    -------
    tuple of (tuple of int, str or None) or None
        The major, minor and patch numbers, and the label after the
        hyphen (None for a release); None if it is not a version tag.

    Examples
    --------
    >>> parse_version("v0.1.2")
    ((0, 1, 2), None)
    >>> parse_version("v1.0.0-rc1")
    ((1, 0, 0), 'rc1')
    >>> parse_version("main") is None
    True
    """
    found = VERSION.match(tag)
    if found is None:
        return None
    major, minor, patch, label = found.groups()
    return (int(major), int(minor), int(patch)), label


def sort_versions(tags: list[str]) -> list[str]:
    """
    Put version tags in order, newest first, and leave out anything that
    is not a version tag.

    A pre-release comes before the release it leads to, so "v1.0.0-rc1"
    is older than "v1.0.0".

    Parameters
    ----------
    tags : list of str
        Tags, in any order.

    Returns
    -------
    list of str
        The version tags, newest first.

    Examples
    --------
    >>> sort_versions(
    ...     [
    ...         "v0.9.0",
    ...         "v0.10.0",
    ...         "v1.0.0-rc1",
    ...         "v1.0.0",
    ...         "notes",
    ...         "v0.2.1",
    ...     ]
    ... )
    ['v1.0.0', 'v1.0.0-rc1', 'v0.10.0', 'v0.9.0', 'v0.2.1']
    """
    keyed = []
    for tag in tags:
        parsed = parse_version(tag)
        if parsed is not None:
            numbers, label = parsed
            keyed.append(((numbers, label is None, label or ""), tag))
    return [tag for _, tag in sorted(keyed, reverse=True)]


def latest_release(tags: list[str]) -> str | None:
    """
    Give the newest tag that is a release and not a pre-release.

    Parameters
    ----------
    tags : list of str
        Tags, in any order.

    Returns
    -------
    str or None
        The tag, or None if there is no release yet.

    Examples
    --------
    >>> latest_release(
    ...     ["v0.0.0", "v0.1.0", "v0.2.0-beta1"]
    ... )
    'v0.1.0'
    >>> latest_release(["v0.2.0-beta1"]) is None
    True
    """
    for tag in sort_versions(tags):
        parsed = parse_version(tag)
        if parsed is not None and parsed[1] is None:
            return tag
    return None


def versions_in(site: Path) -> list[str]:
    """
    List the versions that have a folder in the site, newest first.

    Parameters
    ----------
    site : Path
        The site's folder.

    Returns
    -------
    list of str
        The folder names that are version tags.

    Examples
    --------
    >>> import tempfile
    >>> with (
    ...     tempfile.TemporaryDirectory() as folder
    ... ):
    ...     for name in (
    ...         "v0.1.0",
    ...         "v0.0.0",
    ...         "dev",
    ...         "latest",
    ...     ):
    ...         (Path(folder) / name).mkdir()
    ...     versions_in(Path(folder))
    ['v0.1.0', 'v0.0.0']
    """
    return (
        sort_versions(
            [entry.name for entry in site.iterdir() if entry.is_dir()],
        )
        if site.is_dir()
        else []
    )


def redirect_page(
    *,
    target: str,
    canonical: str,
    what: str,
) -> str:
    """
    Write a page that sends the visitor on.

    Parameters
    ----------
    target : str
        Where to go.
    canonical : str
        The address that search engines should treat as this page's.
    what : str
        What the visitor is being sent to, for the link in the page.

    Returns
    -------
    str
        The HTML.

    Examples
    --------
    >>> "url=latest/" in redirect_page(
    ...     target="latest/",
    ...     canonical="https://example.org/alto/latest/",
    ...     what="latest docs",
    ... )
    True
    """
    return REDIRECT.format(
        target=escape(target),
        canonical=escape(canonical),
        what=escape(what),
    )


def _install_stable(site: Path, *, stable: Path, site_url: str) -> None:
    """
    Replace only the root entries owned by the stable docs build.

    Parameters
    ----------
    site : Path
        The published site directory.
    stable : Path
        The staging directory containing the new stable docs.
    site_url : str
        The canonical site URL without a trailing slash.

    Raises
    ------
    ValueError
        The staged build has no home page or uses a reserved root name.

    Examples
    --------
    >>> import tempfile
    >>> with tempfile.TemporaryDirectory() as folder:
    ...     site = Path(folder, "site")
    ...     stable = Path(folder, "stable")
    ...     stable.mkdir()
    ...     _ = (stable / "index.html").write_text("Stable docs")
    ...     _install_stable(
    ...         site, stable=stable, site_url="https://example.org/alto"
    ...     )
    ...     (site / "index.html").read_text()
    'Stable docs'
    """
    manifest = site / STABLE_MANIFEST
    entries = sorted(entry.name for entry in stable.iterdir())
    if not (stable / "index.html").is_file() or any(
        name.startswith(".")
        or name in (DEV, LATEST, "versions.json")
        or parse_version(name) is not None
        for name in entries
    ):
        raise ValueError("Unexpected stable docs output")
    if manifest.is_file():
        for name in json.loads(manifest.read_text(encoding="utf-8")):
            path = site / name
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink(missing_ok=True)

    legacy = site / LATEST
    if legacy.is_dir():
        shutil.rmtree(legacy)
    shutil.copytree(stable, site, dirs_exist_ok=True)
    for page in sorted(stable.rglob("*.html")):
        relative = page.relative_to(stable)
        suffix = relative.as_posix()
        if relative.name == "index.html":
            suffix = suffix.removesuffix("index.html")
        target = f"{site_url}/{quote(suffix)}"
        alias = legacy / relative
        alias.parent.mkdir(parents=True, exist_ok=True)
        alias.write_text(
            redirect_page(target=target, canonical=target, what="latest docs"),
            encoding="utf-8",
        )
    manifest.write_text(json.dumps(entries) + "\n", encoding="utf-8")


def finish(
    site: Path,
    *,
    root_files: Path,
    site_url: str,
    stable: Path | None = None,
) -> dict[str, object]:
    """
    Write everything around the versions in a site: their list, the home
    page, the sitemap and the shared files.

    Parameters
    ----------
    site : Path
        The site's folder, with a folder for each version and perhaps
        `dev` and `latest`.
    root_files : Path
        A folder of files that belong to the whole site. They are copied
        to its root with `@SITE@` replaced by `site_url` and
        `@SITE_PATH@` by its path. Keyword-only.
    site_url : str
        The address of the site's root, such as
        "https://altosaurus.github.io/alto", without a slash at the end.
        Keyword-only.
    stable : Path or None
        A staged stable build, if this run is publishing one.

    Returns
    -------
    dict of str to object
        What was written to `versions.json`.

    Examples
    --------
    >>> import tempfile
    >>> with (
    ...     tempfile.TemporaryDirectory() as folder
    ... ):
    ...     built, shared = (
    ...         Path(folder, "site"),
    ...         Path(folder, "shared"),
    ...     )
    ...     for name in (
    ...         "v0.0.0",
    ...         "v0.1.0",
    ...         "dev",
    ...         "latest",
    ...     ):
    ...         built.joinpath(name).mkdir(
    ...             parents=True
    ...         )
    ...     shared.mkdir()
    ...     _ = shared.joinpath(
    ...         "robots.txt"
    ...     ).write_text(
    ...         "Sitemap: @SITE@/sitemap.xml"
    ...     )
    ...     finish(
    ...         built,
    ...         root_files=shared,
    ...         site_url="https://example.org/alto",
    ...     )
    ...     built.joinpath("robots.txt").read_text()
    {'latest': 'v0.1.0', 'versions': ['dev', 'v0.1.0', 'v0.0.0']}
    'Sitemap: https://example.org/alto/sitemap.xml'
    """
    site_url = site_url.rstrip("/")
    if stable is not None:
        _install_stable(site, stable=stable, site_url=site_url)
    stable_at_root = (site / STABLE_MANIFEST).is_file()
    site_path = urlparse(site_url).path
    versions = versions_in(site)
    latest = latest_release(versions)
    names = [*([DEV] if (site / DEV).is_dir() else []), *versions]
    listing: dict[str, object] = {"latest": latest, "versions": names}
    commit_file = site / DEV / "commit.txt"
    if commit_file.is_file():
        listing["dev_commit"] = commit_file.read_text(encoding="utf-8").strip()
    (site / "versions.json").write_text(
        json.dumps(listing, indent=2) + "\n",
        encoding="utf-8",
    )

    for source in sorted(root_files.iterdir()):
        if source.is_file() and not source.name.startswith("."):
            text = (
                source.read_text(encoding="utf-8")
                .replace("@SITE_PATH@", site_path)
                .replace("@SITE@", site_url)
            )
            (site / source.name).write_text(text, encoding="utf-8")

    if not stable_at_root:
        if (site / LATEST).is_dir():
            target, what = f"{LATEST}/", "latest docs"
        elif (site / DEV).is_dir():
            target, what = f"{DEV}/", "development docs"
        else:
            target, what = "", ""
        home = site / "index.html"
        if target:
            home.write_text(
                redirect_page(
                    target=target,
                    canonical=f"{site_url}/{target}",
                    what=what,
                ),
                encoding="utf-8",
            )
        else:
            home.unlink(missing_ok=True)

        sitemap = site / LATEST / "sitemap.xml"
        if sitemap.is_file():
            shutil.copyfile(sitemap, site / "sitemap.xml")
        else:
            (site / "sitemap.xml").unlink(missing_ok=True)
    (site / ".nojekyll").write_text(
        "",
        encoding="utf-8",
    )  # the site is built already; Pages must not run Jekyll on it again
    return listing


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
        0 on success; 1 if the site's folder does not exist.

    Examples
    --------
    >>> main(["latest", "v0.0.0", "v0.0.1"])
    v0.0.1
    0
    >>> main(
    ...     [
    ...         "finish",
    ...         "/no/such/folder",
    ...         "--root-files",
    ...         "/no/such",
    ...         "--site-url",
    ...         "https://example.org",
    ...     ]
    ... )
    1
    """
    parser = argparse.ArgumentParser(
        description="Put together the published docs.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    newest = commands.add_parser(
        "latest",
        help="print the newest tag that is not a pre-release",
    )
    newest.add_argument("tags", nargs="*", help="version tags")
    end = commands.add_parser(
        "finish",
        help=(
            "write versions.json, the home page, the sitemap and the "
            "shared files"
        ),
    )
    end.add_argument("site", type=Path, help="the folder of the site")
    end.add_argument(
        "--root-files",
        type=Path,
        required=True,
        help="the folder of files that belong to the whole site",
    )
    end.add_argument(
        "--site-url",
        required=True,
        help="the address of the site's root",
    )
    end.add_argument(
        "--stable",
        type=Path,
        help="the staged stable docs build",
    )
    arguments = parser.parse_args(argv)
    if arguments.command == "latest":
        print(latest_release(arguments.tags) or "")
        return 0
    if not arguments.site.is_dir():
        print(f"{arguments.site} is not a folder.", file=sys.stderr)
        return 1
    finish(
        arguments.site,
        root_files=arguments.root_files,
        site_url=arguments.site_url,
        stable=arguments.stable,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
