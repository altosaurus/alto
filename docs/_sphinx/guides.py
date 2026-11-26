"""Render Alto’s shared guide sources as MyST pages."""

# ruff: noqa: PLR0917 -- Sphinx hooks and Liquid filters take positional arguments.
# ruff: noqa: INP001 -- Sphinx loads this extension by path.
from __future__ import annotations

import hashlib
import json
import posixpath
import re
import subprocess
import tomllib
from typing import TYPE_CHECKING

import yaml
from docutils import nodes
from liquid import DictLoader, Environment, FileSystemLoader
from sphinx.errors import ExtensionError
from sphinx.util.docutils import SphinxDirective
from sphinx.util.fileutil import copy_asset
from tutorial_docs import TUTORIALS
from walkthrough import listings

if TYPE_CHECKING:
    from sphinx.application import Sphinx

INCLUDE = re.compile(r"{% include ([\w./-]+)(.*?) %}")
ARGUMENT = re.compile(r""" (\w+)=("[^"]*"|'[^']*'|[^\s]+)""")


def relative_url(route: str, path: str) -> str:
    """
    Resolve a site URL relative to the current page's public route.

    Returns
    -------
    str
        A link that works under any documentation version prefix.
    """
    target, separator, fragment = path.partition("#")
    url = posixpath.relpath(target, route)
    if target.endswith("/"):
        url += "/"
    return url + separator + fragment


def render_liquid(app: Sphinx, page: dict, body: str) -> str:
    """
    Expand shared page and figure templates before MyST parses the text.

    Returns
    -------
    str
        Markdown with the page’s data, includes, and URLs resolved.
    """
    templates = {}
    context = {}
    includes = FileSystemLoader(app.srcdir / "_includes")
    for name in set(match[1] for match in INCLUDE.finditer(body)):
        if name == "exercise-view-source.html":
            context["listings"] = listings(app)
            templates[name] = "{{ listings[name] }}"
        else:
            path = includes.resolve_path(name)
            app.env.note_dependency(path)
            templates[name] = path.read_text(encoding="utf-8").replace(
                "include.",
                "",
            )
    engine = Environment(loader=DictLoader(templates))
    route = page["permalink"]
    engine.add_filter("relative_url", lambda path: relative_url(route, path))
    engine.add_filter("jsonify", json.dumps)
    engine.add_filter("group_by", group_by)
    site = {
        "app_version": app.config.alto_app_version,
        "source_revision": app.config.alto_source_revision,
        "site_root": relative_url(route, "/_static"),
    }
    if "site.time" in body:
        script = app.srcdir / "assets/js/downloads.js"
        app.env.note_dependency(script)
        digest = hashlib.sha256(script.read_bytes()).hexdigest()[:12]
        body = body.replace("site.time | date: '%s'", "'" + digest + "'")
    if "category-pages.html" in templates:
        site["pages"] = []
        pages = [
            app.env.doc2path(doc)
            for doc in app.env.found_docs
            if not doc.startswith("api/")
            and app.env.doc2path(doc).suffix in {".md", ".html"}
        ]
        # During the parallel builds the API index still supplies its
        # shared navigation title and order in Jekyll front matter.
        pages.append(app.srcdir / "api/index.md")
        for path in sorted(pages):
            app.env.note_dependency(path)
            meta = yaml.safe_load(
                path.read_text(encoding="utf-8").split("---", 2)[1],
            )
            if "nav_order" in meta:
                site["pages"].append({**meta, "url": meta["permalink"]})
        body = body.replace(' | where_exp: "p", "p.nav_order"', "")
    if "component-shot.html" in templates:
        data = app.srcdir / "_data/launch_components.json"
        app.env.note_dependency(data)
        site["data"] = {
            "launch_components": json.loads(data.read_text(encoding="utf-8")),
        }

    def include(match: re.Match[str]) -> str:
        """
        Translate Jekyll's include arguments to standard Liquid syntax.

        Returns
        -------
        str
            A Liquid include tag with named arguments.
        """
        args = ARGUMENT.sub(r", \1: \2", match[2])
        return "{% include '" + match[1] + "'" + args + " %}"

    return engine.from_string(INCLUDE.sub(include, body)).render(
        site=site,
        page=page,
        **context,
    )


def group_by(pages: list[dict], key: str) -> list[dict]:
    """
    Group the contents page in navigation order.

    Returns
    -------
    list
        Groups with a name and their member pages.
    """
    groups = {}
    for page in pages:
        groups.setdefault(page.get(key), []).append(page)
    return [{"name": name, "items": items} for name, items in groups.items()]


class Platform(SphinxDirective):
    """Group the installation instructions for an operating system."""

    has_content = True
    required_arguments = 1
    final_argument_whitespace = True

    def run(self) -> list[nodes.Node]:
        """
        Parse Markdown inside the operating system selector.

        Returns
        -------
        list
            The platform wrapper and the parsed instructions.
        """
        content = self.parse_content_to_nodes()
        for child in content:
            for rubric in child.findall(nodes.rubric, include_self=True):
                rubric["heading-level"] = rubric["level"]
        systems = self.arguments[0]
        return [
            nodes.raw("", f'<div data-platforms="{systems}">', format="html"),
            *content,
            nodes.raw("", "</div>", format="html"),
        ]


def platform_blocks(body: str) -> str:
    """
    Convert nested platform sections into nested MyST directives.

    Returns
    -------
    str
        Markdown with a longer fence around each outer platform.
    """
    lines = body.splitlines()
    depth = 0
    for i, line in enumerate(lines):
        match = re.fullmatch(
            r'<div data-platforms="([a-z ]+)" markdown="1">',
            line,
        )
        if match:
            lines[i] = ":" * (5 - depth) + "{platform} " + match[1] + "\n"
            depth += 1
        elif depth and line == "</div>":
            depth -= 1
            lines[i] = "\n" + ":" * (5 - depth)
    return "\n".join(lines)


def prepare_guide(app: Sphinx, docname: str, source: list[str]) -> None:
    """
    Render a shared page and preserve its interactive figures.

    Raises
    ------
    ExtensionError
        When the catalog links to a tutorial that needs importing.
    """
    if app.env.doc2path(docname).suffix not in {".md", ".html"}:
        return
    _, header, body = source[0].split("---", 2)
    page = yaml.safe_load(header)
    body = render_liquid(app, page, body)
    if docname == "plugins":
        for page_path, _ in TUTORIALS.values():
            path = app.srcdir / page_path
            if not path.is_file():
                raise ExtensionError(
                    f"Missing {path.name}. Import the tutorials with "
                    "'python scripts/tutorial_docs.py all' before building.",
                )
            app.env.note_dependency(path)
    if docname == "getting-started":
        body = platform_blocks(body)
        # MyST preserves classes on a quote, but drops ARIA attributes.
        body = re.sub(
            r"(?m)^(>[^\n]*(?:\n>[^\n]*)*)\n"
            r'{: (role="note" aria-label="[^"]+")}',
            r"<div \2>\n\n\1\n\n</div>",
            body,
        )
    # Kramdown puts block attributes after the element. MyST puts them
    # before the corresponding Markdown block.
    body = re.sub(
        r"(?m)^([^\n]+(?:\n[^\n]+)*?)\n{:\s*([^}]+?)[ ]*}",
        r"{\2}\n\1",
        body,
    )
    if page.get("math"):
        body = re.sub(r"\$\$([^$\n]+)\$\$", r"$\1$", body)
    # Keep embedded SVG, HTML controls, and highlighted source intact
    # through blank lines and indentation inside those elements.
    body = re.sub(
        r"(?ms)^<(svg|figure|div|section|table|fieldset|picture|template)"
        r'\b(?! role="note")[^\n]*\n.*?^</\1>',
        lambda m: "\n```{raw} html\n" + m[0] + "\n```\n",
        body,
    )
    if docname == "index":
        children = sorted(
            p
            for p in app.env.found_docs
            if p != "index" and not p.startswith("api/")
        )
        body += (
            "\n\n```{toctree}\n:hidden:\n:glob:\n\n"
            + "\n".join([*children, "api/index"])
            + "\n```\n"
        )
    # Keep the section ID independent of IDs used by interactive HTML,
    # including the plugin-details element populated by the catalog.
    label = "{#plugin-detail-page}\n" if docname == "plugins/detail" else ""
    source[0] = label + "# " + page["title"] + "\n\n" + body


def home_title(app: Sphinx, tree: nodes.document, docname: str) -> None:
    """Use the title in the home page’s hero as the visible heading."""
    if docname == "index" and app.env.doc2path(docname).suffix == ".md":
        title = next(tree.findall(nodes.title))
        title.parent.remove(title)


def copy_assets(app: Sphinx, exception: Exception | None) -> None:
    """Publish images and downloads at their existing URLs."""
    if exception is None and app.builder.format == "html":
        copy_asset(app.srcdir / "assets", app.outdir / "assets", force=True)


def setup(app: Sphinx) -> dict:
    """
    Register the content conversion and release inputs.

    Returns
    -------
    dict
        Sphinx extension metadata.
    """
    repo = app.confdir.parents[1]
    project = tomllib.loads(
        (repo / "pyproject.toml").read_text(encoding="utf-8"),
    )
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    app.add_config_value(
        "alto_app_version",
        project["project"]["version"],
        "env",
    )
    app.add_config_value(
        "alto_source_revision",
        revision.stdout.strip() or "main",
        "env",
    )
    app.add_directive("platform", Platform)
    app.connect("source-read", prepare_guide)
    app.connect("doctree-resolved", home_title)
    app.connect("build-finished", copy_assets)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
