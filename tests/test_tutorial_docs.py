"""
Tests for bringing the plugin tutorials into the docs.

The tutorial pages live in repositories of their own. The docs workflows
copy in the page and only the files it refers to, so
these tests check that the script copies exactly that, that it refuses a
tutorial with a file missing, and that Alto keeps no
copy of what it brings in.
"""

from __future__ import annotations

import doctest
import importlib.util
import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent
PAGE = """Download [the pack]({{ '/assets/plugins/demo.zip' | relative_url }}).

{% include shot.html src="demo-screen.png" alt="The screen." %}

<img src="{{ '/assets/plugins/demo-wide.png' | relative_url }}" alt="">
Again [the pack]({{ '/assets/plugins/demo.zip' | relative_url }}).
"""


def load() -> ModuleType:
    """
    Load `scripts/tutorial_docs.py` as a module, without running it.

    Returns
    -------
    ModuleType
        The loaded module.
    """
    spec = importlib.util.spec_from_file_location(
        "tutorial_docs",
        ROOT / "scripts" / "tutorial_docs.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tutorial_docs = load()


def make_tutorial(base: Path, *, leave_out: str = "") -> Path:
    """
    Make a tutorial repository with a page, the files the page refers
    to, and some files it does not.

    Parameters
    ----------
    base : Path
        An empty folder to make it in.
    leave_out : str, default ""
        A path under docs/ not to write. Keyword-only.

    Returns
    -------
    Path
        The repository's folder.
    """
    repo = base / "tutorial"
    files = {
        "plugins/viola.md": PAGE,
        "assets/plugins/demo.zip": "zip",
        "assets/plugins/demo-wide.png": "wide",
        "assets/img/demo-screen.png": "light",
        "assets/img/demo-screen-dark.png": "dark",
        "assets/plugins/demo/sounds/C4.wav": "unused audio",
        "assets/plugins/demo-answer.gif": "a picture for the README only",
        "assets/img/other.png": "a screenshot nothing shows",
    }
    for path, text in files.items():
        if path != leave_out:
            target = repo / "docs" / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
    return repo


def test_the_doctests_of_the_script_pass() -> None:
    """Run the examples in the script's docstrings."""
    result = doctest.testmod(
        tutorial_docs,
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
    )
    assert result.attempted and not result.failed


def test_a_page_lists_each_file_it_refers_to_once() -> None:
    """
    Find the downloads, the pictures and both themes of each screenshot,
    without repeats.
    """
    assert tutorial_docs.references(PAGE) == [
        "assets/plugins/demo.zip",
        "assets/img/demo-screen.png",
        "assets/img/demo-screen-dark.png",
        "assets/plugins/demo-wide.png",
    ]


def test_only_the_page_and_the_files_it_refers_to_are_copied(
    tmp_path: Path,
) -> None:
    """
    Copy the page and what it shows, and nothing else from the tutorial
    repository.

    Parameters
    ----------
    tmp_path : Path
        The folder for the tutorial and for the docs.
    """
    repo = make_tutorial(tmp_path)
    docs = tmp_path / "docs"
    copied = tutorial_docs.bring_in("viola", source=repo, docs=docs)
    assert copied[0] == "plugins/viola.md"
    on_disk = sorted(
        path.relative_to(docs).as_posix()
        for path in docs.rglob("*")
        if path.is_file()
    )
    assert on_disk == sorted(copied)
    assert "assets/plugins/demo/sounds/C4.wav" not in on_disk
    assert "assets/plugins/demo-answer.gif" not in on_disk
    assert "assets/img/other.png" not in on_disk
    assert (docs / "assets/img/demo-screen-dark.png").read_text() == "dark"


@pytest.mark.parametrize(
    "missing",
    [
        "assets/plugins/demo.zip",
        "assets/img/demo-screen-dark.png",
        "plugins/viola.md",
    ],
)
def test_a_tutorial_with_a_file_missing_is_refused_before_anything_is_copied(
    tmp_path: Path,
    missing: str,
) -> None:
    """
    Refuse a tutorial whose page refers to a file the repository does
    not have, and leave the docs as they were.

    Parameters
    ----------
    tmp_path : Path
        The folder for the tutorial and for the docs.
    missing : str
        The file left out of the tutorial.
    """
    repo = make_tutorial(tmp_path, leave_out=missing)
    docs = tmp_path / "docs"
    with pytest.raises(FileNotFoundError):
        tutorial_docs.bring_in("viola", source=repo, docs=docs)
    assert not docs.exists()


def test_api_guide_can_reference_tutorial_assets(tmp_path: Path) -> None:
    """
    Import a tutorial asset used only by the shared Plugin API guide.

    Parameters
    ----------
    tmp_path : Path
        Temporary tutorial checkout and destination site.
    """
    repo = make_tutorial(tmp_path)
    docs = tmp_path / "docs"
    (docs / "plugins").mkdir(parents=True)
    path = "assets/plugins/viola/animations/string.gif"
    animation = repo / "docs" / path
    animation.parent.mkdir(parents=True)
    animation.write_bytes(b"example")
    (docs / "plugins/api.md").write_text(
        f"[Animation]({{{{ '/{path}' | relative_url }}}})\n"
        "[Other pack]({{ '/assets/plugins/harpsichord/keys.png' "
        "| relative_url }})",
        encoding="utf-8",
    )
    copied = tutorial_docs.bring_in("viola", source=repo, docs=docs)
    assert path in copied
    assert (docs / path).read_bytes() == animation.read_bytes()


def test_the_command_reports_a_missing_tutorial(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    Fail with a message when the tutorial is not where it was said to
    be.

    Parameters
    ----------
    tmp_path : Path
        An empty folder to look in.
    capsys : pytest.CaptureFixture
        The command's output.
    """
    assert (
        tutorial_docs.main(
            [
                "viola",
                "--from",
                str(tmp_path),
                "--docs",
                str(tmp_path / "docs"),
            ],
        )
        == 1
    )
    assert "not at" in capsys.readouterr().out


def test_the_command_copies_from_a_checkout(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    Bring a tutorial in from a checkout and say how many files came.

    Parameters
    ----------
    tmp_path : Path
        The folder for the tutorial and for the docs.
    capsys : pytest.CaptureFixture
        The command's output.
    """
    repo = make_tutorial(tmp_path)
    assert (
        tutorial_docs.main(
            ["viola", "--from", str(repo), "--docs", str(tmp_path / "docs")],
        )
        == 0
    )
    assert "5 files" in capsys.readouterr().out


def test_alto_keeps_no_copy_of_a_tutorial_it_brings_in() -> None:
    """
    Ignore every path the script writes, so that none of it is
    committed, and keep none of it in the repository.
    """
    ignored = (ROOT / ".gitignore").read_text()
    for path in (
        "docs/plugins/viola.md",
        "docs/assets/plugins/viola/",
        "docs/assets/img/plugin-viola-*.png",
        "docs/plugins/harpsichord.md",
        "docs/assets/img/plugin-harpsichord-*.png",
    ):
        assert path in ignored
    tracked = subprocess.run(
        ["git", "ls-files", "docs"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    assert not re.search(r"viola|harpsichord", tracked), (
        "the plugin tutorials are brought in, not stored here"
    )


def test_the_workflows_bring_the_tutorials_in_before_they_build() -> None:
    """
    Check that the docs build and the pull request check both run the
    script before Jekyll.
    """
    for name in ("docs.yml", "docs-check.yml"):
        workflow = (ROOT / ".github/workflows" / name).read_text()
        assert workflow.index("tutorial_docs.py all") < workflow.index(
            "jekyll build",
        ), name
