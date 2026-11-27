"""Check API discovery and incremental Sphinx builds."""

from __future__ import annotations

import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

DOCS = Path(__file__).resolve().parents[1] / "docs"


def test_incremental_reference(tmp_path: Path) -> None:
    """
    Build, edit, and remove a component in a disposable source tree.

    Parameters
    ----------
    tmp_path : Path
        Temporary checkout containing a minimal Alto package.
    """
    sphinx = shutil.which("sphinx-build")
    if sphinx is None:
        pytest.skip("Install the docs dependency group to run Sphinx.")
    docs = tmp_path / "docs"
    includes = docs / "_includes"
    includes.mkdir(parents=True)
    shutil.copy(DOCS / "_includes/api-fragments.html", includes)
    (docs / "index.rst").write_text(
        "Reference\n=========\n\n.. toctree::\n\n   api/index\n",
        encoding="utf-8",
    )
    package = tmp_path / "alto"
    package.mkdir()
    (package / "__init__.py").touch()
    module = package / "example.py"
    intro = '"""Example module."""\n'
    module.write_text(intro, encoding="utf-8")
    out = tmp_path / "html"
    build = [
        sphinx,
        "-W",
        "-b",
        "dirhtml",
        "-c",
        str(DOCS / "_sphinx"),
        str(docs),
        str(out),
    ]
    subprocess.run(build, check=True)
    definition = '''
def result(value: int | None) -> int | None:
    """
    Read a sample value.

    Returns
    -------
    chosen : int | None
        The selected value.
    bool
        A status flag.
    """
'''
    module.write_text(intro + definition, encoding="utf-8")
    subprocess.run(build, check=True)
    overview = out / "api/alto.example/index.html"
    detail = overview.parent / "function-result/index.html"
    home = out / "index.html"
    assert 'href="api/alto.example/function-result/"' in home.read_text(
        "utf-8",
    )
    html = detail.read_text(encoding="utf-8")
    table = ET.fromstring(
        html[html.index("<table") : html.index("</table>") + len("</table>")],
    )
    rows = [
        ["".join(cell.itertext()).strip() for cell in row]
        for row in table.iter("tr")
    ]
    assert rows == [
        ["Name", "Type", "Description"],
        ["chosen", "int | None", "The selected value."],
        ["", "bool", "A status flag."],
    ]
    module.write_text(
        intro + definition.replace("selected value", "revised description"),
        encoding="utf-8",
    )
    subprocess.run(build, check=True)
    assert "The revised description." in detail.read_text(encoding="utf-8")
    module.write_text(intro, encoding="utf-8")
    subprocess.run(build, check=True)
    assert "function-result" not in overview.read_text(encoding="utf-8")
    assert "function-result" not in home.read_text("utf-8")
    assert not detail.exists()
