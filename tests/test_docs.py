"""
The docs and their screenshots stay in step.

Every picture a page shows exists in both themes, and each one can be
regenerated with scripts/screenshots.py.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType

import ast
import base64
import importlib.util
import json
import re
from html import unescape
from pathlib import Path
from urllib.parse import unquote

from docs._sphinx.docs_excerpts import excerpts
from PySide6.QtGui import QColor, QImage

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "docs" / "assets" / "img"


def script() -> ModuleType:
    """
    Load scripts/screenshots.py as a module, without running it.

    Returns
    -------
    ModuleType
        The loaded module.
    """
    spec = importlib.util.spec_from_file_location(
        "screenshots",
        ROOT / "scripts" / "screenshots.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(
        module,
    )  # only defines things; the work happens under __main__
    return module


def developer_guide_screens() -> set[str]:
    """
    Collect the Developer guide screenshots covered by the pre-release
    refresh.

    Returns
    -------
    set of str
        The screen names passed to the component-shot include.
    """
    docs = ROOT / "docs"
    chapters = (
        page
        for page in (docs / "developer-guide").glob("*.md")
        if page.name != "ui-style-guide.md"
    )
    pages = [docs / "developer-guide.md", *chapters]
    return {
        name
        for page in pages
        for name in re.findall(
            r'component-shot\.html screen="([\w-]+)"',
            page.read_text(),
        )
    }


def shown() -> set[str]:
    """
    Return the picture names the docs pages include with shot.html,
    without the .png.

    Returns
    -------
    set of str
        The pictures the docs pages include.
    """
    found = set()
    docs = ROOT / "docs"
    spec = importlib.util.spec_from_file_location(
        "tutorial_docs",
        ROOT / "scripts" / "tutorial_docs.py",
    )
    assert spec is not None and spec.loader is not None
    tutorials = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tutorials)
    # A tutorial brought in from its own repository takes its own
    # pictures, in that repository.
    brought_in = {docs / page for page, _ in tutorials.TUTORIALS.values()}
    for page in (
        *docs.glob("*.md"),
        *(docs / "guide").glob("*.md"),
        *(docs / "plugins").glob("*.md"),
    ):
        if page not in brought_in:
            found |= set(
                re.findall(r'shot\.html src="([^"]+)\.png"', page.read_text()),
            )
    home = (ROOT / "docs" / "index.md").read_text()
    front_matter = home.split("---", 2)[1]
    found.update(
        re.findall(r"^    image: ([\w-]+)\.png$", front_matter, re.MULTILINE),
    )
    found.update(developer_guide_screens())
    return found


def test_launch_screens_link_visible_regions_to_api_classes() -> None:
    """
    Check the paired images, region bounds, and destination of each link
    in the launch guide.
    """
    screens = json.loads(
        (ROOT / "docs" / "_data" / "launch_components.json").read_text(),
    )
    assert set(screens) == developer_guide_screens()
    for screen, regions in screens.items():
        assert (
            QImage(str(IMG / f"{screen}.png")).size()
            == QImage(str(IMG / f"{screen}-dark.png")).size()
        )
        assert regions
        for region in regions:
            x, y, width, height = region["rect"]
            assert 0 <= x < x + width <= 100 and 0 <= y < y + height <= 100, (
                screen,
                region,
            )
            module, slug = region["href"].strip("/").split("/")[1:]
            name = region["type"]
            assert slug == f"class-{name.lower()}"
            source = ROOT.joinpath(*module.split(".")).with_suffix(".py")
            assert any(
                isinstance(node, ast.ClassDef) and node.name == name
                for node in ast.parse(source.read_text(encoding="utf-8")).body
            )


def test_every_picture_a_page_shows_exists_in_both_themes() -> None:
    """
    Check the app window color in every light and dark screenshot.
    """
    assert shown()
    for name in shown():
        for suffix in ("", "-dark"):
            path = IMG / f"{name}{suffix}.png"
            image = QImage(str(path))
            assert not image.isNull(), path.name
            # Sample the window background, clear of the white notation
            # paper and piano keys.
            assert (image.pixelColor(10, 10).lightness() < 128) == (
                suffix == "-dark"
            ), path.name


def test_screenshot_comparison_uses_decoded_pixels_and_dimensions() -> None:
    """
    Count visible pixel changes across image formats.
    """
    compare = script().changed_fraction
    before = QImage(10, 10, QImage.Format.Format_RGB32)
    before.fill(QColor(100, 100, 100))
    after = before.convertToFormat(QImage.Format.Format_RGBA8888)
    assert compare(before, after=after) == 0
    after.setPixelColor(0, 0, QColor(116, 100, 100))
    assert compare(before, after=after) == 0
    after.setPixelColor(0, 0, QColor(117, 100, 100))
    assert compare(before, after=after) == 0.01
    assert compare(QImage(), after=after) == 1
    assert compare(before, after=after.copy(0, 0, 5, 5)) == 1


def test_every_picture_can_be_regenerated_by_the_script() -> None:
    """
    Check that every picture can be regenerated by the script.
    """
    made = set(script().SHOTS)
    assert shown() == made, "docs pictures and scripts/screenshots.py disagree"


def test_exercise_view_screenshot_labels_the_visible_widgets() -> None:
    """Keep the view's widget walkthrough paired with its callouts."""
    docs = ROOT / "docs"
    guide = (docs / "developer-guide" / "exercise-view.md").read_text()
    screen = "exercise-view-anatomy"
    assert f'component-shot.html screen="{screen}" labels=true' in guide
    regions = json.loads(
        (docs / "_data" / "launch_components.json").read_text(),
    )
    assert [region["type"] for region in regions[screen]] == [
        "StaffWidget",
        "ExerciseView",
        "DegreeButton",
        "NoteNameSettingsPanel",
    ]


def test_exercise_view_excerpts_follow_their_source_lines() -> None:
    """A multiline excerpt moves with its source."""
    source = """class ExerciseView:
    def next_question(self):
        self.staff.show_notes(
            q.staff,
        )
"""
    selections = {"staff": ["next_question", "self.staff.show_notes("]}
    for extra in (0, 5):
        snippet = excerpts("\n" * extra + source, selections=selections)
        assert snippet["staff"] == {
            "start": 3 + extra,
            "end": 5 + extra,
            "code": "self.staff.show_notes(\n    q.staff,\n)",
        }


def readme_badges() -> dict[str, tuple[str, str]]:
    """
    Read the linked badges in the README table.

    Returns
    -------
    dict of str to tuple of str
        Each image's accessible label mapped to its image URL and link
        destination.
    """
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    links = re.findall(
        r'<a href="([^"]+)"><img src="([^"]+)" alt="([^"]+)"></a>',
        readme,
    )
    return {
        label: (unescape(src), unescape(href)) for href, src, label in links
    }


def test_python_versions_in_readme_badge_ones_tests_run_on() -> None:
    """
    Check that the python versions in the readme badge are the ones the
    tests run on.
    """
    workflow = (ROOT / ".github" / "workflows" / "tests.yml").read_text()
    matrix = re.search(
        r"ALL:\s*'\[([^]]*)]'",
        workflow,
    )  # the versions a push to main runs, in the scope job
    assert matrix is not None
    tested = re.findall(r'"([\d.]+)"', matrix.group(1))
    badge = re.match(
        r"https://img\.shields\.io/badge/python-([^-]+)-",
        readme_badges()["Python"][0],
    )
    assert badge is not None, "the README has no Python versions badge"
    assert unquote(badge.group(1)).split(" | ") == tested
    # and the oldest of them is what pyproject.toml asks for
    minimum = re.search(
        r'requires-python\s*=\s*">=([\d.]+)"',
        (ROOT / "pyproject.toml").read_text(),
    )
    assert minimum is not None and minimum.group(1) == tested[0]


def test_readme_badges_name_tool_carry_logo_as_small_embedded() -> None:
    """
    Check the six badges with a logo: each names a real workflow (or the
    Python versions) and carries its picture in its address.

    Shields has a one-color pytest and Python logo of its own, but the
    color ones, and the pictures for Pyright,
    ASV and Jekyll, are not in its set. So each picture is carried in
    the badge's address. They must stay small,
    so that the address does, and be PNG files.
    """
    badges = readme_badges()
    for label, workflow in (
        ("Tests", "tests.yml"),
        ("Ruff", "ruff.yml"),
        ("Pyright", "pyright.yml"),
        ("ASV", "performance.yml"),
        ("Docs", "docs.yml"),
    ):
        badge, link = badges[label]
        assert badge.startswith("https://img.shields.io/")
        assert (
            f"/{workflow}?" in badge
            and (ROOT / ".github" / "workflows" / workflow).is_file()
        )
        assert f"/actions/workflows/{workflow}" in link or label == "Docs"
    for label in ("Tests", "Ruff", "Pyright", "ASV", "Docs", "Python"):
        logo = re.search(r"[?&]logo=([^&\s]+)", badges[label][0])
        assert logo is not None, f"the {label} badge has no logo"
        image = unquote(logo.group(1))
        assert image.startswith("data:image/png;base64,")
        data = base64.b64decode(image.split(",", 1)[1])
        assert data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) < 2000
        assert (
            len(logo.group(1)) < 2000
        )  # the whole address stays short enough for GitHub to fetch it


def test_ruff_workflow_runs_version_of_pre_commit_hook_on_every() -> None:
    """
    Check that the Ruff workflow pins the hook's version, checks the
    formatting and the rules, and runs on pull requests.
    """
    workflow = (ROOT / ".github" / "workflows" / "ruff.yml").read_text(
        encoding="utf-8",
    )
    hook = re.search(
        r"astral-sh/ruff-pre-commit\s+rev: v([0-9.]+)",
        (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8"),
    )
    assert hook is not None
    assert (
        f'pip install "ruff=={hook.group(1)}"' in workflow
    )  # the hook and the workflow hold the code to the same rules
    assert "ruff format --check ." in workflow and "ruff check ." in workflow
    assert "pull_request:" in workflow and "branches: [main]" in workflow
