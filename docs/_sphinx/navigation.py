"""Connect the shared guide metadata and API to the Alto sidebar."""

# ruff: noqa: INP001, PLR0917 -- Sphinx loads hooks by path and position.
from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from docutils import nodes
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment


def guide_children(
    app: Sphinx,
    env: BuildEnvironment,
    added: set[str],
    changed: set[str],
    removed: set[str],
) -> set[str]:
    """
    Order each guide's hidden toctree using the shared front matter.

    Returns
    -------
    set
        Guide sources to reread when their navigation changes.
    """
    pages = {}
    for doc in sorted(env.found_docs):
        path = env.doc2path(doc)
        if doc == "api/index":
            pages[doc] = {
                "title": "API reference",
                "nav_order": 11,
                "nav_group": "For developers",
                "permalink": "/api/",
            }
            continue
        if path.suffix in {".md", ".html"} and path.is_file():
            pages[doc] = yaml.safe_load(
                path.read_text(encoding="utf-8").split("---", 2)[1],
            )
    groups = {
        p["title"]: doc
        for doc, p in pages.items()
        if p.get("nav_group") == p["title"]
    }
    sections = {
        p["children"]: doc for doc, p in pages.items() if "children" in p
    }
    ordered = defaultdict(list)
    root = app.config.root_doc
    for doc, page in pages.items():
        if doc in {root, "plugins/detail"}:
            continue
        parent = sections.get(page.get("parent")) or groups.get(
            page.get("nav_group"),
        )
        if parent is None or parent == doc:
            parent = root
        order = page.get("order", page.get("nav_order", float("inf")))
        ordered[parent].append((order, doc))
    # Category and contents pages list the same navigation entries.
    index = [
        {
            "title": page["title"],
            "url": page["permalink"],
            "nav_group": page.get("nav_group"),
            "nav_order": page["nav_order"],
        }
        for page in sorted(
            pages.values(),
            key=lambda p: p.get("nav_order", float("inf")),
        )
        if "nav_order" in page
    ]
    children = {
        parent: [doc for _, doc in sorted(entries)]
        for parent, entries in ordered.items()
    }
    if (
        getattr(env, "alto_nav_index", None) == index
        and env.alto_guide_children == children
    ):
        return set()
    env.alto_nav_index = index
    env.alto_guide_children = children
    return pages.keys() - {"api/index"}


def update_sidebar(app: Sphinx, env: BuildEnvironment) -> set[str]:
    """
    Refresh every sidebar when the document tree or its titles change.

    Returns
    -------
    set
        Pages whose navigation needs rewriting.
    """
    tree = {
        doc: (title.astext(), tuple(env.toctree_includes.get(doc, ())))
        for doc, title in env.titles.items()
    }
    if getattr(env, "alto_sidebar", {}) == tree:
        return set()
    env.alto_sidebar = tree
    return env.found_docs


def page_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict,
    doctree: nodes.document | None,
) -> None:
    """Expose the resolved Sphinx tree to page and search templates."""
    context["no_toc"] = "alto_no_toc" in app.env.metadata.get(pagename, {})
    context["canonical_root"] = app.config.html_baseurl.rstrip("/")
    context["site_root"] = app.config.alto_site_root
    context["sidebar_tree"] = app.env.alto_sidebar
    if pagename == "plugins/detail" and "plugins" in app.builder.relations:
        # This page needs a plugin ID from the catalog to show content.
        title, children = context["sidebar_tree"]["plugins"]
        context["sidebar_tree"] = {
            **context["sidebar_tree"],
            "plugins": (title, (*children, pagename)),
        }
        doc = "plugins"
        parents = []
        while doc != app.config.root_doc:
            parents.append(
                {
                    "title": app.env.titles[doc].astext(),
                    "link": app.builder.get_relative_uri(pagename, doc),
                },
            )
            doc = app.builder.relations[doc][0]
        context["parents"] = list(reversed(parents))


def setup(app: Sphinx) -> dict:
    """
    Register navigation hooks for full and incremental builds.

    Returns
    -------
    dict
        Sphinx extension metadata.
    """
    app.connect("env-get-outdated", guide_children)
    app.connect("env-updated", update_sidebar)
    app.connect("html-page-context", page_context)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
