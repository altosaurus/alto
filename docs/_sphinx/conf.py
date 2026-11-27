"""Build the Alto guides and API reference."""

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
    "guides",
    "navigation",
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
myst_all_links_external = True
myst_enable_extensions = ["colon_fence", "attrs_block", "dollarmath"]
source_suffix = {
    ".api.rst": "restructuredtext",
    ".rst": "restructuredtext",
    ".md": "markdown",
    ".html": "markdown",
}

# Build the shared guides and the Sphinx-generated API sources.
include_patterns = [
    "index.rst",
    "*.md",
    "developer-guide/*.md",
    "guide/*.md",
    "plugins/*.md",
    "plugins/detail.html",
    "api/**.api.rst",
]
templates_path = ["templates", "../_includes"]
html_theme_path = ["themes"]
html_theme = "alto"
html_static_path = ["../assets/css", "../assets/js"]
html_extra_path = ["../../LICENSE"]
html_favicon = "../assets/img/icon.png"
html_permalinks = False
html_show_sourcelink = False
html_use_index = False
html_copy_source = False
version = "dev"
html_static_path += [
    "../assets/vendor/temml-0.14.0/temml.min.js",
    "../site-root/plugins.js",
    "../site-root/plugins.json",
]
mathjax_path = "temml.min.js"
mathjax_options = {
    "defer": "defer",
    "onload": (
        "temml.renderMathInElement(document.querySelector('article'), "
        "{fences: '(', annotate: true})"
    ),
}
html_domain_indices = False
