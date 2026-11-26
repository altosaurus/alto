"""
The API reference in docs/api stays in step with the docstrings it is
written from.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import re
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def api_docs() -> ModuleType:
    """
    Load scripts/api_docs.py as a module, without running it.

    Returns
    -------
    ModuleType
        The loaded module.
    """
    spec = importlib.util.spec_from_file_location(
        "api_docs",
        ROOT / "scripts" / "api_docs.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(
        module,
    )  # only defines things; the work happens under __main__
    return module


def test_the_committed_pages_match_the_docstrings(
    api_docs: ModuleType,
) -> None:
    """
    Check that the committed pages match the docstrings; if not, run
    `python scripts/api_docs.py`.

    Parameters
    ----------
    api_docs : ModuleType
        The script that writes the pages.
    """
    assert api_docs.problems() == [], (
        "docs/api is out of date: run `python scripts/api_docs.py`"
    )


def test_every_module_has_a_page_with_its_public_names(
    api_docs: ModuleType,
) -> None:
    """
    Check that every module has a page, listed on the index, that names
    its public classes and leaves out private ones.

    Parameters
    ----------
    api_docs : ModuleType
        The script that writes the pages.
    """
    pages = api_docs.build()
    for path in api_docs.module_files():
        module = api_docs.dotted(path)
        overview = pages[f"{module}.md"]
        assert f"[{module}]" in pages["index.md"]
        package = api_docs.package_of(path)
        assert f"[{package}]({package}/)" in pages["index.md"]
        assert f"[{module}](../{module}/)" in pages[f"{package}.md"]
        assert 'class="api-signature"' not in overview
        for node in ast.parse(path.read_text()).body:
            if not isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                continue
            if node.name.startswith("_"):
                continue
            kind = "class" if isinstance(node, ast.ClassDef) else "function"
            slug = f"{kind}-{node.name.lower()}"
            assert f"[`{node.name}`]({slug}/)" in overview
            component = pages[f"{module}/{slug}.md"]
            assert f"parent: {module}\n" in component
            assert f"permalink: /api/{module}/{slug}/\n" in component
            if isinstance(node, ast.ClassDef):
                for method in node.body:
                    if isinstance(method, ast.FunctionDef):
                        heading = f"## {node.name}.{method.name}\n"
                        assert (heading in component) == (
                            not method.name.startswith("_")
                        )
    assert "alto.ui.charts/class-_chart.md" not in pages


def test_return_tables_preserve_names_and_literal_pipes(
    api_docs: ModuleType,
) -> None:
    """
    Keep optional return names and union types in their own cells.

    Parameters
    ----------
    api_docs : ModuleType
        The API generator.
    """
    table = api_docs.field_table(
        "Returns",
        text="value : int | None\n    Use `x | y` or a | b.\nbool\n    Valid.",
    )
    assert table.splitlines() == [
        "| Name | Type | Description |",
        "| --- | --- | --- |",
        r"| `value` | `int | None` | Use `x | y` or a \| b. |",
        "|  | `bool` | Valid. |",
    ]
    unnamed = api_docs.field_table("Returns", text="int\n    The count.")
    assert unnamed.startswith("| Type | Description |")


def test_module_bookmarks_resolve_to_the_original_components(
    api_docs: ModuleType,
) -> None:
    """
    Distinguish a class, its method, and a similarly named function.

    Parameters
    ----------
    api_docs : ModuleType
        The API generator.
    """
    name = "alto.instrument_info"
    pages = api_docs.render_module(api_docs.SOURCE / "instrument_info.py")
    mapping = re.search(
        r'id="api-fragments">(.*?)</script>',
        pages[f"{name}.md"],
    )
    assert mapping is not None
    targets = json.loads(mapping[1])
    assert targets["coverage"] == "class-coverage/"
    assert targets["coverage-1"] == "function-coverage/"
    assert targets["coverageinstalled"] == "class-coverage/#coverageinstalled"
    assert "## Coverage.installed" in pages[f"{name}/class-coverage.md"]


def test_a_page_has_the_front_matter_the_site_needs(
    api_docs: ModuleType,
) -> None:
    """
    Check that a page carries the front matter the docs layout reads,
    and wraps its text in Liquid's raw tags.

    Parameters
    ----------
    api_docs : ModuleType
        The script that writes the pages.
    """
    page = api_docs.build()["alto.theory.pitch/class-note.md"]
    head, _, body = page.removeprefix("---\n").partition("---\n")
    assert (
        "title: Note" in head
        and "parent: alto.theory.pitch" in head
        and "permalink: /api/alto.theory.pitch/class-note/" in head
    )
    assert body.startswith("{% raw %}") and body.rstrip().endswith(
        "{% endraw %}",
    )
    source_tag = r'{% include api-source\.html name="[\w.]+" line=\d+ %}'
    raw_body, count = re.subn(
        "{% endraw %}" + source_tag + "{% raw %}",
        "",
        body,
    )
    assert count > 0
    assert "{%" not in raw_body.removeprefix("{% raw %}").removesuffix(
        "{% endraw %}\n",
    )
    lines = (ROOT / "alto/theory/pitch.py").read_text().splitlines()
    for name, line in re.findall(r'name="([\w.]+)" line=(\d+)', body):
        assert re.match(
            rf"(class|def) {re.escape(name.split('.')[-1])}\b",
            lines[int(line) - 1].lstrip(),
        )


def test_adding_a_module_leaves_existing_pages_identical(
    api_docs: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Insert a module earlier in the API index and compare the existing
    page byte for byte.

    Parameters
    ----------
    api_docs : ModuleType
        The API page generator.
    monkeypatch : pytest.MonkeyPatch
        Supplies a small module list to the generator.
    """
    files = [api_docs.SOURCE / "theory" / "pitch.py"]
    monkeypatch.setattr(api_docs, "module_files", lambda: files)
    before = api_docs.build()
    files.insert(0, api_docs.SOURCE / "theory" / "fifths.py")
    after = api_docs.build()
    assert after["index.md"] != before["index.md"]
    assert after["alto.theory.pitch.md"] == before["alto.theory.pitch.md"]


def test_the_check_reports_what_is_missing_or_stale(
    api_docs: ModuleType,
    tmp_path: Path,
) -> None:
    """
    Check that a folder with a missing, a stale and an unwanted page is
    reported, and a freshly written one is clean.

    Parameters
    ----------
    api_docs : ModuleType
        The script that writes the pages.
    tmp_path : Path
        A scratch folder unique to this test.
    """
    assert api_docs.write(out=tmp_path) == len(api_docs.build())
    assert api_docs.problems(out=tmp_path) == []
    (tmp_path / "alto.audio.md").write_text("old")
    (tmp_path / "alto.settings.md").unlink()
    (tmp_path / "alto.audio" / "gone.md").write_text("x")
    assert sorted(api_docs.problems(out=tmp_path)) == [
        "missing: alto.settings.md",
        "no longer wanted: alto.audio/gone.md",
        "out of date: alto.audio.md",
    ]
