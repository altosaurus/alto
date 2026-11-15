"""
Tests for the versioned docs: the script that puts the site together, and the files that make the dropdown and the search rules.

The Jekyll builds and the push to `gh-pages` happen on GitHub, so these tests cover what can be checked without them: the logic
of which release is the latest and what is written around the versions, and that the layout, the workflow and the shared files
say what the design needs.
"""

from __future__ import annotations

import doctest
import importlib.util
import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE_ROOT = DOCS / "site-root"
SITE_URL = "https://example.org/alto"


def load() -> ModuleType:
    """
    Load `scripts/docs_site.py` as a module, without running it.

    Returns
    -------
    ModuleType
        The loaded module.
    """
    spec = importlib.util.spec_from_file_location("docs_site", ROOT / "scripts" / "docs_site.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


docs_site = load()


def make_site(
    tmp_path: Path,
    *,
    folders: tuple[str, ...],
) -> tuple[Path, Path]:
    """
    Make a site with some version folders, and a folder of shared files to go with it.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    folders : tuple of str
        The names of the folders in the site, such as "dev" or "v0.1.0".

    Returns
    -------
    tuple of Path and Path
        The site's folder, and the folder of shared files.
    """
    site, shared = tmp_path / "site", tmp_path / "shared"
    for name in folders:
        (site / name).mkdir(parents=True)
    shared.mkdir(parents=True)
    (shared / "robots.txt").write_text("Sitemap: @SITE@/sitemap.xml\nPath: @SITE_PATH@\n", encoding="utf-8")
    return site, shared


@pytest.mark.parametrize(
    ("tags", "newest"),
    [
        (["v0.0.0"], "v0.0.0"),
        (["v0.9.0", "v0.10.0", "v0.2.0"], "v0.10.0"),  # numbers, not text: 10 is more than 9
        (["v1.0.0", "v1.0.0-rc1", "v1.1.0-beta1"], "v1.0.0"),  # a pre-release is never the latest
        (["v1.0.0-rc1"], None),
        (["main", "dev", "latest", "v1"], None),
        ([], None),
    ],
)
def test_the_latest_release_is_the_highest_version_that_is_not_a_pre_release(tags: list[str], newest: str | None) -> None:
    """
    Check which tag counts as the latest release.

    Parameters
    ----------
    tags : list of str
        The tags.
    newest : str or None
        The one that is the latest, or None if there is none.
    """
    assert docs_site.latest_release(tags) == newest


def test_versions_are_listed_newest_first_with_a_pre_release_before_its_release() -> None:
    """Check the order of the dropdown: the newest release first, and a release candidate under the release it leads to."""
    tags = ["v0.0.0", "v1.0.0-rc2", "v1.0.0", "v0.1.0", "v1.0.0-rc10", "notes"]
    assert docs_site.sort_versions(tags) == ["v1.0.0", "v1.0.0-rc2", "v1.0.0-rc10", "v0.1.0", "v0.0.0"]


def test_finishing_a_site_lists_dev_and_the_releases_and_names_the_latest(tmp_path: Path) -> None:
    """
    Check `versions.json`, which the dropdown in every page reads.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    """
    site, shared = make_site(tmp_path, folders=("dev", "latest", "v0.0.0", "v0.1.0"))
    docs_site.finish(site, root_files=shared, site_url=SITE_URL)
    assert json.loads((site / "versions.json").read_text(encoding="utf-8")) == {
        "latest": "v0.1.0",
        "versions": ["dev", "v0.1.0", "v0.0.0"],  # "latest" is an alias, not a version of its own
    }


def test_the_home_page_goes_to_latest_and_to_dev_until_there_is_a_release(tmp_path: Path) -> None:
    """
    Check where the root of the site sends a visitor in each state.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    """
    site, shared = make_site(tmp_path / "with-release", folders=("dev", "latest", "v0.0.0"))
    docs_site.finish(site, root_files=shared, site_url=SITE_URL)
    page = (site / "index.html").read_text(encoding="utf-8")
    assert 'url=latest/"' in page and f'href="{SITE_URL}/latest/"' in page

    site, shared = make_site(tmp_path / "only-dev", folders=("dev",))
    docs_site.finish(site, root_files=shared, site_url=SITE_URL)
    assert 'url=dev/"' in (site / "index.html").read_text(encoding="utf-8")

    site, shared = make_site(tmp_path / "empty", folders=())
    site.mkdir()
    (site / "index.html").write_text("old", encoding="utf-8")
    docs_site.finish(site, root_files=shared, site_url=SITE_URL)
    assert not (site / "index.html").exists()  # nothing to send anyone to


def test_the_sitemap_of_the_site_is_the_one_of_latest_and_goes_when_there_is_no_latest(tmp_path: Path) -> None:
    """
    Check that only the latest release's pages are offered to search engines.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    """
    site, shared = make_site(tmp_path, folders=("dev", "latest", "v0.0.0"))
    (site / "latest" / "sitemap.xml").write_text("<urlset>latest</urlset>", encoding="utf-8")
    (site / "dev" / "sitemap.xml").write_text("<urlset>dev</urlset>", encoding="utf-8")
    docs_site.finish(site, root_files=shared, site_url=SITE_URL)
    assert (site / "sitemap.xml").read_text(encoding="utf-8") == "<urlset>latest</urlset>"
    (site / "latest" / "sitemap.xml").unlink()
    docs_site.finish(site, root_files=shared, site_url=SITE_URL)
    assert not (site / "sitemap.xml").exists()


def test_the_shared_files_get_the_address_of_the_site_and_nothing_stops_pages_from_serving_them(tmp_path: Path) -> None:
    """
    Check the placeholders in the shared files, and that GitHub Pages is told not to run Jekyll on the finished site.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    """
    site, shared = make_site(tmp_path, folders=("dev",))
    docs_site.finish(site, root_files=shared, site_url=f"{SITE_URL}/")  # a slash at the end makes no difference
    assert (site / "robots.txt").read_text(encoding="utf-8") == f"Sitemap: {SITE_URL}/sitemap.xml\nPath: /alto\n"
    assert (site / ".nojekyll").is_file()


def test_the_command_line_prints_the_latest_and_refuses_a_site_that_is_not_there(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    Check the two commands the workflow runs.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    capsys : pytest.CaptureFixture
        Collects what is printed.
    """
    assert docs_site.main(["latest", "v0.0.0", "v0.0.1", "v0.1.0-rc1"]) == 0
    assert capsys.readouterr().out.strip() == "v0.0.1"
    assert docs_site.main(["latest"]) == 0 and capsys.readouterr().out.strip() == ""
    assert docs_site.main(["finish", str(tmp_path / "nothing"), "--root-files", str(tmp_path), "--site-url", SITE_URL]) == 1
    site, shared = make_site(tmp_path, folders=("v0.0.0",))
    assert docs_site.main(["finish", str(site), "--root-files", str(shared), "--site-url", SITE_URL]) == 0
    assert (site / "versions.json").is_file()


def test_the_layout_has_the_dropdown_slot_and_sends_search_engines_to_latest() -> None:
    """Check the layout: a slot the dropdown fills, the canonical address under /latest/, noindex for dev, and the script."""
    layout = (DOCS / "_layouts" / "default.html").read_text(encoding="utf-8")
    assert (
        'id="version-slot"' in layout
        and 'data-version="{{ site.docs_version }}"' in layout
        and 'data-root="{{ site.site_root }}"' in layout
    )
    assert "prepend: '/latest'" in layout and '<link rel="canonical" href="{{ canonical }}">' in layout
    assert "site.docs_version == 'dev'" in layout and 'content="noindex"' in layout
    assert "version-switcher.js" in layout
    assert "site.docs_version == 'latest'" in layout  # the structured data is for the latest release only


def test_the_top_bar_has_the_version_then_the_theme_then_github_and_the_theme_is_only_a_picture_until_clicked() -> None:
    """Check the order of the top bar, that the theme button has no words of its own, and that the words are in its menu."""
    layout = (DOCS / "_layouts" / "default.html").read_text(encoding="utf-8")
    bar = layout[layout.index('<div class="top-actions">') : layout.index("</header>")]
    assert bar.index('id="version-slot"') < bar.index('id="theme-button"') < bar.index('class="icon-link"')
    button = bar[bar.index('id="theme-button"') : bar.index("</button>", bar.index('id="theme-button"'))]
    assert 'aria-label="Colour theme"' in button and 'aria-haspopup="menu"' in button
    assert ">Light<" not in button and ">Dark<" not in button  # no words on the button itself
    menu = bar[bar.index('id="theme-menu"') : bar.index('class="icon-link"')]
    assert "hidden>" in menu and ">Light<" in menu and ">Dark<" in menu and ">System<" in menu
    assert "theme-toggle" not in layout  # the old button with words is gone
    assert "Match your computer" not in layout  # System has no note under it
    assert layout.count('class="dd-ico"') == 3  # an icon tile beside each of Light, Dark and System
    assert 'removeAttribute("data-theme")' in layout and "Escape" in layout  # System forgets the choice; Escape closes the menu


def test_the_version_dropdown_is_made_like_the_theme_menu_with_dev_last_and_named_plainly() -> None:
    """Check the version dropdown: a menu with icon tiles and not a native select, dev after the releases, and called "dev"."""
    script = (SITE_ROOT / "version-switcher.js").read_text(encoding="utf-8")
    assert 'createElement("select")' not in script and 'class="dd-ico"' in script and "dd-menu" in script
    assert "unreleased)" not in script and "label: name" in script  # the entry for the development docs says "dev" and no more
    assert 'concat(data.versions.indexOf("dev") >= 0 ? ["dev"] : [])' in script  # releases first, then dev
    assert "Match your computer" not in script
    css = (DOCS / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    assert ".dd-menu {" in css and ".dd-item" in css and ".version select" not in css


def test_the_config_builds_dev_by_default_and_keeps_the_shared_files_out_of_every_version() -> None:
    """Check that a plain build is the dev docs, at the address GitHub Pages used before, and that root files are not built in."""
    config = (DOCS / "_config.yml").read_text(encoding="utf-8")
    assert "docs_version: dev" in config and "site_root: /alto" in config
    assert "- site-root" in config and "- Gemfile" in config
    assert (DOCS / "Gemfile").read_text(encoding="utf-8").count("github-pages") >= 1


def test_the_shared_files_are_in_site_root_and_the_google_file_is_exactly_as_google_gave_it() -> None:
    """Check the files that belong to the whole site, and that the Search Console verification file has not been touched."""
    for name in ("version-switcher.js", "404.html", "robots.txt", "llms.txt"):
        assert (SITE_ROOT / name).is_file()
    assert (
        not (DOCS / "robots.txt").exists() and not (DOCS / "llms.txt").exists()
    )  # they moved: Jekyll would build them into each version
    google = next(SITE_ROOT.glob("google*.html"))
    assert google.read_bytes() == f"google-site-verification: {google.name}".encode()  # no newline: the file must match exactly
    assert not list(DOCS.glob("google*.html"))
    robots = (SITE_ROOT / "robots.txt").read_text(encoding="utf-8")
    assert "Sitemap: @SITE@/sitemap.xml" in robots
    assert "@SITE@/latest/" in (SITE_ROOT / "llms.txt").read_text(encoding="utf-8")


def test_an_old_address_is_sent_to_the_same_page_in_latest_by_the_404_page() -> None:
    """Check that the 404 page moves a visitor of /alto/getting-started/ to /alto/latest/getting-started/, and does not loop."""
    page = (SITE_ROOT / "404.html").read_text(encoding="utf-8")
    assert 'var root = "@SITE_PATH@"' in page and 'location.replace(root + "/latest/" + rest' in page
    assert 'first === "latest"' in page and 'first === "dev"' in page  # a missing page inside a version is not sent round again


def test_the_dropdown_reads_the_list_of_versions_from_the_site_and_warns_on_dev_and_on_old_versions() -> None:
    """Check the dropdown's script: it fetches the list, falls back to a version's home for a missing page, and shows banners."""
    script = (SITE_ROOT / "version-switcher.js").read_text(encoding="utf-8")
    assert '"/versions.json"' in script and 'method: "HEAD"' in script
    assert "version-banner" in script and "development version" in script and "not the latest release" in script
    assert "latest (" in script  # the alias is shown with the version it stands for


def test_the_docs_workflow_builds_each_version_into_its_own_folder_and_only_writes_to_gh_pages() -> None:
    """Check the workflow's triggers, its one writer permission, the concurrency group and the builds."""
    yaml = pytest.importorskip("yaml")
    text = (ROOT / ".github" / "workflows" / "docs.yml").read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    triggers = data.get(True, data.get("on"))
    assert triggers["push"]["tags"] == ["v*"] and triggers["push"]["branches"] == ["main"] and "workflow_dispatch" in triggers
    assert data["permissions"] == {"contents": "write"}
    assert data["concurrency"]["group"] == "docs" and data["concurrency"]["cancel-in-progress"] is False
    assert "--baseurl" not in text and "baseurl: %s/%s" in text  # the address of each version is given in a config file
    assert "build latest latest" in text and "docs_site.py latest" in text
    assert "docs_site.py finish site" in text and "git push --quiet origin HEAD:gh-pages" in text
    assert "cp -R tooling/docs/_layouts/." in text  # a release without the dropdown gets the current layout


def test_the_examples_in_the_script_run() -> None:
    """Check the examples in the docstrings of `scripts/docs_site.py`, which pytest does not collect from `scripts/`."""
    result = doctest.testmod(docs_site, optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
    assert result.attempted > 10 and result.failed == 0
