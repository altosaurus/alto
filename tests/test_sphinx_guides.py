"""Build the installation guide and plugin detail page with Sphinx."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

DOCS = Path(__file__).resolve().parents[1] / "docs"


def test_interactive_pages(tmp_path: Path) -> None:
    """
    Preserve the OS groups, versioned downloads, and plugin mount point.

    Parameters
    ----------
    tmp_path : Path
        Destination for the sample project and rendered documentation.
    """
    sphinx = shutil.which("sphinx-build")
    if sphinx is None:
        pytest.skip("Install the docs dependency group to run Sphinx.")
    docs = tmp_path / "docs"
    for name in (
        "getting-started.md",
        "plugins/detail.html",
        "assets/js/downloads.js",
        "_includes/macos-download.html",
        "_includes/os-icons.html",
        "_includes/shot.html",
        "_includes/source-install-unix.md",
    ):
        target = docs / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(DOCS / name, target)
    (docs / "index.rst").write_text(
        "Alto\n====\n\n.. toctree::\n\n"
        "   getting-started\n   plugins/detail\n   api/index\n",
        encoding="utf-8",
    )
    package = tmp_path / "alto"
    package.mkdir()
    (package / "__init__.py").touch()
    out = tmp_path / "html"
    for version in ("0.0.2", "0.0.3"):
        subprocess.run(
            [
                sphinx,
                "-W",
                "-b",
                "dirhtml",
                "-c",
                str(DOCS / "_sphinx"),
                "-D",
                f"alto_app_version={version}",
                str(docs),
                str(out),
            ],
            check=True,
        )
        guide = (out / "getting-started/index.html").read_text("utf-8")
        assert re.search(
            r'<div data-platforms="windows">\s*'
            r'<h3 [^>]*id="windows-installer"',
            guide,
        )
        assert 'role="note" aria-label="Windows installer notice"' in guide
        assert f"alto-{version}-windows-x64-setup.exe" in guide
        assert (f"alto-{version}-macos-arm64.dmg" in guide) == (
            version == "0.0.3"
        )
    detail = (out / "plugins/detail/index.html").read_text("utf-8")
    assert detail.count('id="plugin-details"') == 1
    assert 'data-registry="../../_static/plugins.json"' in detail
