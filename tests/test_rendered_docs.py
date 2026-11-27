"""Check the API and screenshot links in the rendered site."""

from __future__ import annotations

import ast
import json
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(
    "ALTO_DOCS_HTML" in os.environ,
    "Requires a built documentation site.",
)
class RenderedDocsTest(unittest.TestCase):
    """Read the same HTML that the Docs check workflow publishes."""

    def article(self, route: str) -> str:
        """
        Read the page at a directory URL.

        Returns
        -------
        str
            Article markup without the site-wide sidebar.
        """
        page = (
            Path(os.environ["ALTO_DOCS_HTML"])
            / route.strip("/")
            / "index.html"
        )
        return (
            page.read_text(encoding="utf-8")
            .split("<article>")[1]
            .split("</article>")[0]
        )

    def test_public_components(self) -> None:
        """Check the module links and public method anchors."""
        index = self.article("api")
        for path in (ROOT / "alto").rglob("*.py"):
            if path.name in {"__init__.py", "__main__.py"}:
                continue
            module = ".".join(path.relative_to(ROOT).with_suffix("").parts)
            package = module.rsplit(".", 1)[0]
            assert f'href="{package}/"' in index
            assert f'href="../{module}/"' in self.article(f"api/{package}")
            route = f"api/{module}"
            overview = self.article(route)
            for node in ast.parse(path.read_text(encoding="utf-8")).body:
                if not isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    continue
                kind = (
                    "class" if isinstance(node, ast.ClassDef) else "function"
                )
                slug = f"{kind}-{node.name.lower()}/"
                assert (f'href="{slug}"' in overview) == (
                    not node.name.startswith("_")
                ), module
                if node.name.startswith("_"):
                    continue
                detail = self.article(f"{route}/{slug}")
                assert f'id="{module}.{node.name}"' in detail
                if isinstance(node, ast.ClassDef):
                    for method in node.body:
                        if isinstance(method, ast.FunctionDef):
                            anchor = f'id="{module}.{node.name}.{method.name}"'
                            assert (anchor in detail) == (
                                not method.name.startswith("_")
                            ), anchor

    def test_conflicting_bookmarks(self) -> None:
        """Resolve a class, method, and function that share a name."""
        page = self.article("api/alto.instrument_info")
        match = re.search(
            r'id="api-fragments">(.*?)</script>',
            page,
            re.DOTALL,
        )
        assert match
        targets = json.loads(match[1])
        assert targets["coverage"] == "class-coverage/"
        assert targets["coverage-1"] == "function-coverage/"
        assert (
            targets["coverageinstalled"] == "class-coverage/#coverageinstalled"
        )
        assert 'id="coverageinstalled"' in self.article(
            "api/alto.instrument_info/class-coverage",
        )

    def test_guide_bookmarks(self) -> None:
        """Keep historical package, step, and release bookmarks."""
        anchors = {
            "api": ("alto", "altotheory"),
            "contents": ("using-alto", "for-developers", "about"),
            "developer-guide/exercise-view": ("1-staff", "4-settings-pane"),
            "release-notes": ("003", "added-1", "changed-2"),
        }
        for route, fragments in anchors.items():
            article = self.article(route)
            for fragment in fragments:
                assert f'id="{fragment}"' in article

    def test_launch_screenshot_links(self) -> None:
        """Open the API page named by each launch diagram hotspot."""
        regions = ROOT / "docs" / "_data" / "launch_components.json"
        for screen in json.loads(regions.read_text(encoding="utf-8")).values():
            for region in screen:
                assert f"<h1>{region['type']}</h1>" in self.article(
                    region["href"],
                )

    def test_release_notes(self) -> None:
        """Check each version and its release link."""
        notes = self.article("release-notes")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        for version in re.findall(
            r"^## \[([\d.]+)\]",
            changelog,
            re.MULTILINE,
        ):
            assert f"<h2>{version}</h2>" in notes
            assert (
                f"https://github.com/altosaurus/alto/releases/tag/v{version}"
                in notes
            )
