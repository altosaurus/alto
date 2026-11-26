"""Build the migrated Alto pages alongside the Jekyll site."""

# ruff: noqa: INP001 -- Sphinx loads this configuration by path.

project = "Alto"
extensions = ["myst_parser"]
myst_title_to_header = True

# Expand this list as pages move to Sphinx. Both builders read the same
# Markdown, with the existing front matter supplying each page title.
include_patterns = ["index.rst", "credits.md"]
templates_path = ["../_includes"]
html_theme_path = ["themes"]
html_theme = "alto"
html_static_path = ["../assets/css", "../assets/js"]
html_favicon = "../assets/img/icon.png"
html_permalinks = False
html_show_sourcelink = False
html_use_index = False
html_copy_source = False
version = "dev"
