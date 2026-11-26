"""Build the migrated Alto pages alongside the Jekyll site."""

# ruff: noqa: INP001 -- Sphinx loads this configuration by path.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

project = "Alto"
extensions = [
    "myst_parser",
    "sphinx.ext.napoleon",
    "autoapi.extension",
    "api_reference",
    "walkthrough",
]
autoapi_dirs = ["../alto"]
autoapi_generate_api_docs = False
autoapi_add_toctree_entry = False
autoapi_member_order = "bysource"
autoapi_options = ["members"]
# AutoAPI cannot resolve tuple-assigned constants imported by the UI.
# Component pages only document definitions owned by each module.
suppress_warnings = ["autoapi.python_import_resolution"]
autodoc_member_order = "bysource"
myst_title_to_header = True
source_suffix = {
    ".api.rst": "restructuredtext",
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# Expand this list as pages move to Sphinx. Both builders read the same
# Markdown, with the existing front matter supplying each page title.
include_patterns = [
    "index.rst",
    "credits.md",
    "developer-guide/exercise-view.md",
    "api/**.api.rst",
]
templates_path = ["templates", "../_includes"]
html_theme_path = ["themes"]
html_theme = "alto"
html_static_path = ["../assets/css", "../assets/js"]
html_favicon = "../assets/img/icon.png"
html_permalinks = False
html_show_sourcelink = False
html_use_index = False
html_copy_source = False
version = "dev"
html_static_path += [
    f"../assets/img/{screen}{suffix}.png"
    for screen in ("note-identification", "exercise-view-anatomy")
    for suffix in ("", "-dark")
]
