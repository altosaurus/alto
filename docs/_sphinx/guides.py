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
import xml.etree.ElementTree as ET
from importlib.metadata import distribution
from typing import TYPE_CHECKING
from urllib.parse import urljoin

import yaml
from docutils import nodes
from liquid import DictLoader, Environment, FileSystemLoader
from release_notes import render as render_release_notes
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
        "site_root": (
            app.config.alto_site_root
            if app.config.alto_site_root is not None
            else relative_url(route, "/_static")
        ),
    }
    if "site.time" in body:
        script = app.srcdir / "assets/js/downloads.js"
        app.env.note_dependency(script)
        digest = hashlib.sha256(script.read_bytes()).hexdigest()[:12]
        body = body.replace("site.time | date: '%s'", "'" + digest + "'")
    if "category-pages.html" in templates:
        site["pages"] = app.env.alto_nav_index
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
    if docname == "release-notes":
        changelog = app.srcdir.parent / "CHANGELOG.md"
        app.env.note_dependency(changelog)
        body += "\n" + render_release_notes(
            changelog.read_text(encoding="utf-8"),
        )
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
    children = app.env.alto_guide_children.get(docname, [])
    if children:
        body += (
            "\n\n```{toctree}\n:hidden:\n\n"
            + "\n".join("/" + child for child in children)
            + "\n```\n"
        )
    # Keep the section ID independent of IDs used by interactive HTML,
    # including the plugin-details element populated by the catalog.
    metadata = []
    if page.get("toc") is False:
        metadata.append("alto_no_toc: true")
    label = ""
    if docname == "plugins/detail":
        metadata.append("orphan: true")
        label = "{#plugin-detail-page}\n"
    header = "---\n" + "\n".join(metadata) + "\n---\n" if metadata else ""
    source[0] = header + label + "# " + page["title"] + "\n\n" + body


def guide_bookmarks(app: Sphinx, tree: nodes.document, docname: str) -> None:
    """Keep historical guide bookmarks alongside MyST section IDs."""
    if app.env.doc2path(docname).suffix != ".md":
        return
    counts = {}
    for section in tree.findall(nodes.section):
        title = section[0]
        if not isinstance(title, nodes.title):
            continue
        slug = re.sub(r"[^\w -]", "", title.astext().lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        anchor = f"{slug}-{count}" if count else slug
        if slug and anchor not in tree.ids and anchor not in section["ids"]:
            section["ids"].append(anchor)
            tree.ids[anchor] = section


def home_title(app: Sphinx, tree: nodes.document, docname: str) -> None:
    """Use the title in the home page’s hero as the visible heading."""
    if docname == "index" and app.env.doc2path(docname).suffix == ".md":
        title = next(tree.findall(nodes.title))
        title.parent.remove(title)


def copy_assets(app: Sphinx, exception: Exception | None) -> None:
    """
    Publish guide assets and notices for bundled browser code.

    Raises
    ------
    ExtensionError
        A dependency's distribution is missing its license text.
    """
    if exception is not None or app.builder.format != "html":
        return
    copy_asset(app.srcdir / "assets", app.outdir / "assets", force=True)
    for package, filename in (
        ("Sphinx", "LICENSE.rst"),
        ("Pygments", "LICENSE"),
    ):
        notice = distribution(package).read_text(f"licenses/{filename}")
        if not notice:
            raise ExtensionError(
                f"Missing license in the installed {package} distribution",
            )
        (app.outdir / "_static" / f"{package}-LICENSE.txt").write_text(
            notice,
            encoding="utf-8",
        )


def stable_sitemap(app: Sphinx, exception: Exception | None) -> None:
    """List the stable pages at their canonical URLs."""
    if (
        exception
        or app.builder.name != "dirhtml"
        or app.config.version != "latest"
    ):
        return
    urls = ET.Element(
        "urlset",
        xmlns="http://www.sitemaps.org/schemas/sitemap/0.9",
    )
    for doc in sorted(app.env.found_docs):
        if "orphan" in app.env.metadata[doc]:
            continue
        entry = ET.SubElement(urls, "url")
        ET.SubElement(entry, "loc").text = urljoin(
            app.config.html_baseurl,
            app.builder.get_target_uri(doc),
        )
    ET.ElementTree(urls).write(
        app.outdir / "sitemap.xml",
        encoding="utf-8",
        xml_declaration=True,
    )


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
    app.add_config_value(
        "alto_site_root",
        None,
        "env",
        types={str, type(None)},
    )
    app.add_directive("platform", Platform)
    app.connect("source-read", prepare_guide)
    app.connect("doctree-resolved", guide_bookmarks)
    app.connect("doctree-resolved", home_title)
    app.connect("build-finished", copy_assets)
    app.connect("build-finished", stable_sitemap)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
