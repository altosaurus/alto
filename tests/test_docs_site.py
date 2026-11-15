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
import re
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from alto import updates

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
    assert 'createElement("select")' not in script and 'class="avs-ico"' in script and "avs-menu" in script
    assert "unreleased)" not in script and "label: name" in script  # the entry for the development docs says "dev" and no more
    assert 'concat(data.versions.indexOf("dev") >= 0 ? ["dev"] : [])' in script  # releases first, then dev
    assert "Match your computer" not in script
    css = (DOCS / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    assert ".dd-menu {" in css and ".dd-item" in css and ".version select" not in css  # the theme menu in the layout uses these


def test_the_version_dropdown_brings_its_own_styles_because_a_versions_stylesheet_is_frozen() -> None:
    """
    Check that the dropdown does not depend on the stylesheet of the page it is in.

    Each version of the docs keeps the stylesheet it was built with, so a page built before the dropdown was restyled has none of
    its rules. Without styles of their own the icons had no size, and the menu showed as a giant arrow over unreadable text.
    """
    script = (SITE_ROOT / "version-switcher.js").read_text(encoding="utf-8")
    start = script.index("var STYLE = [")
    style = script[start : script.index('].join("\\n");', start)]
    classes = set(re.findall(r"avs(?:-[a-z]+)?", script[:start] + script[script.index('].join("\\n");', start) :]))
    classes.discard("avs-style")  # the id of the style element, not a class
    assert "avs" in classes and 'id = "avs-style"' in script and "addStyle();" in script
    for name in classes:
        assert f".{name}" in style, f"the class {name} is used but not styled"
    assert "width=" in script and "height=" in script  # an icon has its size written on it, in case no rule reaches it
    assert "dd-" not in script  # none of the classes of the page's own stylesheet


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


def test_the_home_page_has_a_download_button_and_a_download_section_in_place_of_get_started() -> None:
    """Check the button under the first paragraph, the section it goes to, and the words in it."""
    home = (DOCS / "index.md").read_text(encoding="utf-8")
    assert "## Get started" not in home  # the section for developers is gone; the Getting started page keeps those steps
    hero = home[home.index('<div class="hero">') : home.index("</div>", home.index('<div class="hero">'))]
    assert hero.index('class="lead"') < hero.index('class="dl-go" href="#download"')  # under the first paragraph
    assert '<section class="dl" id="download"' in home and "<b>Version {{ v }}</b>. Free on all platforms." in home
    assert "Windows may warn" not in home and "publisher is unknown" not in home
    assert "run Alto from its source code" in home and "/getting-started/#install-and-run" in home
    assert "## Install and run" in (DOCS / "getting-started.md").read_text(encoding="utf-8")  # the section that link goes to


def test_the_file_names_in_the_download_section_are_the_ones_the_release_workflow_makes() -> None:
    """Check the file names and the address of a release's files against the name the updater itself looks for."""
    home = (DOCS / "index.md").read_text(encoding="utf-8")
    linux = updates.platform_asset_name("1.2.3", system="Linux", machine="x86_64")
    windows = updates.platform_asset_name("1.2.3", system="Windows", machine="AMD64")
    assert linux and windows
    assert linux.replace("1.2.3", "{{ v }}") in home and windows.replace("1.2.3", "{{ v }}") in home
    assert "https://github.com/altosaurus/alto/releases/download/v" in home


def test_each_build_says_which_release_to_offer_and_a_build_without_a_release_shows_no_download() -> None:
    """Check that every build is given its release (the newest for dev) and that the page copes with there being none."""
    workflow = (ROOT / ".github" / "workflows" / "docs.yml").read_text(encoding="utf-8")
    assert 'app_version: "%s"' in workflow and 'APP_VERSION="${VERSION#v}"' in workflow
    assert "docs_site.py latest $(git -C source tag --list" in workflow  # for dev: the newest release
    home = (DOCS / "index.md").read_text(encoding="utf-8")
    assert '{% if site.app_version != "" %}' in home and '{% if v != "" %}' in home
    assert "app_version:" in (DOCS / "_config.yml").read_text(encoding="utf-8")


def test_the_download_script_detects_the_system_and_keeps_and_sends_nothing() -> None:
    """
    Check the script that chooses the main button: it names the systems, copes with phones and ARM Linux, and stores nothing.

    Reading the visitor's system to choose a button is harmless only while it stays in the page, so no way to store or send it may
    ever be added to this file.
    """
    script = (DOCS / "assets" / "js" / "downloads.js").read_text(encoding="utf-8")
    for word in ("windows", "linux", "macos", "phone", "other", "aarch64", "userAgentData", "Your system"):
        assert word in script
    for forbidden in (
        "localStorage",
        "sessionStorage",
        "document.cookie",
        "fetch(",
        "XMLHttpRequest",
        "sendBeacon",
        "WebSocket",
        "Image(",
    ):
        assert forbidden not in script, f"downloads.js must not use {forbidden}"


def test_the_logos_are_in_the_page_and_credited() -> None:
    """Check that the three system marks exist as symbols and that the page of credits names where two of them come from."""
    icons = (DOCS / "_includes" / "os-icons.html").read_text(encoding="utf-8")
    for name in ("os-windows", "os-apple", "os-linux", "os-computer"):
        assert f'id="{name}"' in icons
    page = (DOCS / "credits.md").read_text(encoding="utf-8")
    assert "Simple Icons" in page and "CC0" in page


def test_every_icon_has_its_size_written_on_it_and_the_files_it_needs_are_stamped_with_the_build() -> None:
    """
    Check what keeps a page readable when the browser still has an old stylesheet.

    An icon with no size is drawn at the browser's default of 300 by 150 pixels, which filled the screen when a new page met an
    old, cached stylesheet. Each icon now says how big it is, and the stylesheet and the script are asked for by an address that
    changes with every build, so a new page does not meet an old file.
    """
    pages = {
        "layout": (DOCS / "_layouts" / "default.html").read_text(encoding="utf-8"),
        "home": (DOCS / "index.md").read_text(encoding="utf-8"),
        "script": (DOCS / "assets" / "js" / "downloads.js").read_text(encoding="utf-8"),
        "switcher": (SITE_ROOT / "version-switcher.js").read_text(encoding="utf-8"),
    }
    for name, text in pages.items():
        for tag in re.findall(r"<svg[^>]*>", text):
            assert "width=" in tag and "height=" in tag, f"an icon in the {name} has no size: {tag}"
    assert "site.css' | relative_url }}?v={{ site.time" in pages["layout"]
    assert "downloads.js' | relative_url }}?v={{ site.time" in pages["home"]


def _brightness(colour: str) -> float:
    """
    Give the relative luminance of a colour written as "#rrggbb", as the web accessibility guidelines define it.

    Parameters
    ----------
    colour : str
        The colour.

    Returns
    -------
    float
        0 for black up to 1 for white.
    """
    parts = [int(colour[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4 for value in parts]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first: str, second: str) -> float:
    """
    Give the contrast ratio of two colours, from 1 (the same) to 21 (black on white).

    Parameters
    ----------
    first : str
        One colour, "#rrggbb".
    second : str
        The other.

    Returns
    -------
    float
        The ratio.
    """
    high, low = sorted((_brightness(first), _brightness(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


@pytest.mark.parametrize("block", [":root {", ':root:not([data-theme="light"]) {', ':root[data-theme="dark"] {'])
def test_the_download_buttons_are_readable_and_stand_out_in_light_and_dark(block: str) -> None:
    """
    Check each theme's button colour: its words are readable on it (4.5 to 1) and the button stands out from the page (3 to 1).

    Parameters
    ----------
    block : str
        The start of the block of colours: light, dark by the system's setting, and dark by choice.
    """
    css = (DOCS / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    start = css.index(block)
    colours = css[start : css.index("}", start)]
    button = re.search(r"--button:\s*(#[0-9a-fA-F]{6})", colours)
    words = re.search(r"--button-text:\s*(#[0-9a-fA-F]{6})", colours)
    page = re.search(r"--bg:\s*(#[0-9a-fA-F]{6})", colours)
    assert button and words and page
    assert _contrast(button.group(1), words.group(1)) >= 4.5
    assert _contrast(button.group(1), page.group(1)) >= 3.0
    if "dark" in block or "light" in block:
        assert button.group(1).lower() == "#2f6bd0"  # royal blue in both ways of getting dark


def _nav_pages() -> list[dict[str, str]]:
    """
    Read the front matter of every page that is listed in the sidebar, in the order the sidebar lists them.

    Returns
    -------
    list of dict of str to str
        For each page its title, its `nav_order` and its `nav_group` (empty if it has none), by `nav_order`.
    """
    pages = []
    for path in sorted(DOCS.glob("*.md")) + sorted((DOCS / "guide").glob("index.md")) + sorted((DOCS / "api").glob("index.md")):
        text = path.read_text(encoding="utf-8")
        found = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
        if not found:
            continue
        fields = dict(re.findall(r"^([a-z_]+):\s*(.*)$", found.group(1), re.MULTILINE))
        if "nav_order" in fields:
            pages.append({"title": fields["title"], "order": fields["nav_order"], "group": fields.get("nav_group", "")})
    return sorted(pages, key=lambda page: float(page["order"]))


def test_every_page_in_the_sidebar_but_home_has_a_group_and_each_group_is_one_block() -> None:
    """Check that the pages sort into three headings, each a single run in the order of the sidebar, with Home on its own."""
    pages = _nav_pages()
    assert pages[0]["title"] == "Home" and pages[0]["group"] == ""
    assert all(page["group"] for page in pages[1:])
    runs = [page["group"] for index, page in enumerate(pages[1:]) if index == 0 or pages[index]["group"] != page["group"]]
    assert runs == ["Using Alto", "For developers", "About"]  # no heading comes twice


def test_no_page_is_listed_twice_and_a_heading_that_is_a_page_is_that_pages_link() -> None:
    """
    Check that the sidebar can list each page once: the titles differ, and a heading named like a page stands for that page.

    "For developers" is both a heading and a page. The layout makes the heading the page's link and leaves the page out of the
    list under it, so it appears once. The developer guide and the API reference are single rows that link to their page and
    open their chapters, so they appear once as well.
    """
    pages = _nav_pages()
    titles = [page["title"] for page in pages]
    assert len(titles) == len(set(titles))
    same = [page for page in pages if page["title"] == page["group"]]
    assert [page["title"] for page in same] == ["For developers"]
    layout = (DOCS / "_layouts" / "default.html").read_text(encoding="utf-8")
    assert 'where: "title", group' in layout and 'unless group != "" and p.title == group' in layout
    assert (
        layout.count("<summary") >= 4
        and 'class="count"' not in layout
        and "count" not in layout.split("<nav")[1].split("</nav>")[0].replace("account", "")
    )


def test_the_sidebar_opens_whatever_holds_the_current_page_and_the_groups_are_remembered() -> None:
    """Check that the current page's group, section and package are open, and that the script keeps only what you closed."""
    layout = (DOCS / "_layouts" / "default.html").read_text(encoding="utf-8")
    assert "page.parent == p.children" in layout and "page.package == a.package" in layout and "data-nav-group" in layout
    script = (DOCS / "assets" / "js" / "nav.js").read_text(encoding="utf-8")
    assert (
        "localStorage" in script and "try" in script and '[aria-current="page"]' in script
    )  # never closes the current page's group
    assert "fetch(" not in script and "XMLHttpRequest" not in script


def test_the_on_this_page_list_is_made_from_the_headings_and_only_for_pages_with_more_than_one() -> None:
    """Check the contents list script: it reads h2 and h3, skips pages with under two, follows the scroll, and has a fallback."""
    script = (DOCS / "assets" / "js" / "toc.js").read_text(encoding="utf-8")
    assert '"h2, h3"' in script and "heads.length < 2" in script and "On this page" in script
    assert "scroll" in script and "toc-inline" in script and "has-toc" in script
    layout = (DOCS / "_layouts" / "default.html").read_text(encoding="utf-8")
    assert 'id="toc"' in layout and 'id="page-grid"' in layout and "toc.js" in layout and "nav.js" in layout
    css = (DOCS / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    assert ".page-grid.has-toc" in css and "min-width: 1240px" in css and ".toc-inline" in css


def test_the_home_page_keeps_to_the_download_and_leaves_checking_and_updating_to_the_installation_guide() -> None:
    """Check the home page's links, and that the instructions that moved off it are in Getting started."""
    home = (DOCS / "index.md").read_text(encoding="utf-8")
    links = home[home.index('<p class="dl-more">') : home.index("</section>")]
    assert (
        "Release notes" in links and "Older releases" in links and "/getting-started/" in links and ">Getting started<" in links
    )
    assert "Installation guide" not in home and "SHA256SUMS" not in home and "update themselves" not in home
    guide = (DOCS / "getting-started.md").read_text(encoding="utf-8")
    assert (
        "### Check your download" in guide
        and "sha256sum --check --ignore-missing SHA256SUMS" in guide
        and "Get-FileHash" in guide
    )
    assert "## Updating Alto" in guide and "**Check for updates…**" in guide
    assert "offers to open its download page" not in guide  # a packaged copy replaces itself now
    assert guide.index("## Updating Alto") < guide.index(
        "## Install and run",
    )  # for everyone, not under the Linux-only script section
