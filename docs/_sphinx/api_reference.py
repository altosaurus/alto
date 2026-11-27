"""Publish the AutoAPI inventory at Alto’s existing reference URLs."""

# ruff: noqa: INP001 -- Sphinx loads this extension by path.
# ruff: noqa: PLR0917 -- Sphinx calls event handlers positionally.
from __future__ import annotations

import ast
import json
import re
import subprocess
from pathlib import Path
from textwrap import indent
from typing import TYPE_CHECKING

from api_docs import (
    TABLE_SECTIONS,
    class_fields,
    decorator_names,
    entries,
    split_sections,
)
from docutils import nodes
from sphinx import addnodes

if TYPE_CHECKING:
    from autoapi._objects import PythonObject
    from sphinx.application import Sphinx
    from sphinx.config import Config
    from sphinx.environment import BuildEnvironment


def inline_code(text: str) -> str:
    r"""
    Translate Markdown code spans in prose to reStructuredText.

    Returns
    -------
    str
        Inline literals with adjacent words and underscores escaped.
    """
    return re.sub(
        r"(?<!`)`([^`\n]+)`(?!`)(\w?)|(?<=\w)_(?=[\"'])",
        lambda m: (
            ("``" + m[1] + "``" + (r"\ " + m[2] if m[2] else ""))
            if m[1] is not None
            else r"\_"
        ),
        text,
    )


def field_tables(
    app: Sphinx,
    what: str,
    name: str,
    obj: object,
    options: object,
    lines: list[str],
) -> None:
    """Format NumPy fields and prose before Napoleon."""
    sections = split_sections("\n".join(lines))
    parts = []
    for title, content in sections.items():
        if title not in TABLE_SECTIONS:
            if title:
                parts.append(heading(title, "-"))
            parts.append(
                content if title == "Examples" else inline_code(content),
            )
            continue
        fields = entries(content)
        named = title != "Returns" or any(field[0] for field in fields)
        header = [TABLE_SECTIONS[title]] if named else []
        rows = [header + ["Type", "Description"]]
        for field, kind, description in fields:
            if title != "Returns" and not field:
                field, kind = kind, ""
            row = [f"``{field}``" if field else ""] if named else []
            kind_cell = f"``{kind}``" if kind else ""
            rows.append([*row, kind_cell, inline_code(description)])
        body = ["   * - " + "\n     - ".join(row) for row in rows]
        parts.append(
            "\n".join(
                [f".. list-table:: {title}", "   :header-rows: 1", "", *body],
            ),
        )
    lines[:] = "\n\n".join(parts).splitlines() + [""]


def configure_source_urls(app: Sphinx, config: Config) -> None:
    """Pin source links to the published revision or last local edit."""
    repo = app.srcdir.parent
    tracked = subprocess.run(
        ["git", "ls-files", "--", "alto"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if tracked.returncode:
        return
    modified = subprocess.check_output(
        ["git", "diff", "--name-only", "HEAD", "--", "alto"],
        cwd=repo,
        text=True,
    ).splitlines()
    published_revision = (
        config.alto_source_revision
        if config.html_context.get("preview_pr")
        or config.alto_site_root is not None
        else ""
    )
    urls = {}
    for path in set(tracked.stdout.splitlines()).difference(modified):
        if not path.endswith(".py"):
            continue
        revision = (
            published_revision
            or subprocess.check_output(
                ["git", "log", "-1", "--format=%H", "HEAD", "--", path],
                cwd=repo,
                text=True,
            ).strip()
        )
        if revision:
            urls[path] = (
                f"https://github.com/altosaurus/alto/blob/{revision}/{path}"
            )
    config.alto_source_urls = urls


def tree(paths: list[str]) -> str:
    """
    Attach child pages to the Sphinx navigation tree.

    Returns
    -------
    str
        A hidden toctree with the supplied paths.
    """
    if not paths:
        return ""
    return ".. toctree::\n   :hidden:\n\n" + "\n".join(
        "   " + p for p in paths
    )


def heading(title: str, level: str = "=") -> str:
    """
    Format a reStructuredText heading.

    Returns
    -------
    str
        The title and its underline.
    """
    return f"{title}\n{level * len(title)}"


def summary(obj: PythonObject) -> str:
    """
    Extract the opening paragraph.

    Returns
    -------
    str
        The summary on a single line.
    """
    return inline_code(
        " ".join(obj.obj["doc"].strip().partition("\n\n")[0].split()),
    )


def overview(title: str, children: list[PythonObject]) -> str:
    """
    List packages or modules with their descriptions.

    Returns
    -------
    str
        A section with links to each child page.
    """
    lines = [heading(title, "-")]
    for obj in children:
        about = summary(obj)
        lines.append(
            f"* :doc:`/api/{obj.id}`" + (f" — {about}" if about else ""),
        )
    return lines[0] + "\n\n" + "\n".join(lines[1:])


def module_pages(module: PythonObject) -> dict[str, str]:
    """
    Document the public components defined in a module.

    Returns
    -------
    dict
        Directive source for the module and its component pages.
    """
    # Astroid omits synthesized dataclass constructors from its model.
    source = Path(module.obj["file_path"])
    dataclasses = {
        node.name: class_fields(node)
        for node in ast.parse(source.read_bytes()).body
        if isinstance(node, ast.ClassDef)
        and any(
            d.startswith("dataclass") or d.endswith(".dataclass")
            for d in decorator_names(node)
        )
    }
    groups = {"class": [], "function": []}
    children = []
    pages = {}
    fragments = {}
    for obj in module.children:
        if (
            obj.imported
            or obj.name.startswith("_")
            or obj.type not in ("class", "exception", "function")
        ):
            continue
        kind = "function" if obj.type == "function" else "class"
        slug = f"{kind}-{obj.name.lower()}"
        page = f"{module.id}/{slug}"
        children.append(f"/api/{page}")
        key = obj.name.lower()
        fragments[key if key not in fragments else key + "-1"] = f"{slug}/"
        directive = f".. autoapi{kind}:: {obj.id}"
        if kind == "class":
            constructor = obj.constructor
            if obj.name in dataclasses and (
                not constructor or constructor.inherited
            ):
                directive += "(" + ", ".join(dataclasses[obj.name]) + ")"
            methods = [
                method.name
                for method in obj.children
                if method.type in ("method", "property")
                and not method.inherited
                and not method.name.startswith("_")
            ]
            directive += "\n   :show-inheritance:"
            if methods:
                directive += (
                    "\n   :members: "
                    + ", ".join(methods)
                    + "\n   :undoc-members:"
                )
            if (
                constructor
                and not constructor.inherited
                and constructor.docstring
            ):
                directive += "\n\n   **Constructor**\n\n" + indent(
                    constructor.docstring.rstrip(),
                    "   ",
                )
            for method in methods:
                anchor = (obj.name + method).lower()
                fragments[anchor] = f"{slug}/#{anchor}"
        pages[page] = heading(obj.name) + "\n\n" + directive
        about = summary(obj)
        groups[kind].append(
            f"* :doc:`{obj.name} </api/{page}>`"
            + (f" — {about}" if about else ""),
        )

    intro, _, notes = module.docstring.strip().partition("\n\n")
    sections = [heading(module.id), f".. py:module:: {module.id}", intro]
    for kind, title in (("class", "Classes"), ("function", "Functions")):
        if groups[kind]:
            sections.extend([heading(title, "-"), "\n".join(groups[kind])])
    if notes:
        # Reflow Markdown list items for reStructuredText.
        notes = re.sub(
            r"^\* (.+(?:\n(?!\n|\* ).+)*)",
            lambda match: "* " + " ".join(match[1].split()),
            notes,
            flags=re.MULTILINE,
        )
        sections.extend(
            [
                (
                    ".. raw:: html\n\n"
                    "   <details><summary>Module notes and examples</summary>"
                ),
                notes,
                ".. raw:: html\n\n   </details>",
            ],
        )
    if fragments:
        sections.append(
            ".. raw:: html\n\n"
            '   <script type="application/json" id="api-fragments">'
            + json.dumps(fragments)
            + "</script>\n\n.. raw:: html\n"
            "   :file: ../_includes/api-fragments.html",
        )
    sections.append(tree(children))
    pages[module.id] = "\n\n".join(sections)
    return pages


def generate_pages(app: Sphinx) -> None:
    """Write changed directive files before source discovery."""
    packages = sorted(
        obj
        for obj in app.env.autoapi_all_objects.values()
        if obj.type == "package"
    )
    root = app.srcdir / "api"
    pages = {}
    for package in packages:
        modules = [
            mod
            for mod in package.submodules
            if not mod.id.endswith(".__main__")
        ]
        sections = [
            heading(package.id),
            f".. py:module:: {package.id}",
            summary(package),
        ]
        if package.subpackages:
            sections.append(overview("Subpackages", package.subpackages))
        if modules:
            sections.append(overview("Modules", modules))
        sections.append(
            tree(
                [f"/api/{obj.id}" for obj in [*package.subpackages, *modules]],
            ),
        )
        pages[package.id] = "\n\n".join(sections)
        for module in modules:
            pages.update(module_pages(module))
    pages["index"] = "\n\n".join(
        [
            heading("API reference"),
            (
                "Choose a package to explore its modules. Each module lists "
                "its public classes and functions. Class pages include their "
                "public methods."
            ),
            overview("Packages", packages),
            tree(
                [
                    f"/api/{pkg.id}"
                    for pkg in packages
                    if pkg.is_top_level_object
                ],
            ),
        ],
    )
    stale = set(root.rglob("*.api.rst"))
    for page, body in pages.items():
        path = root / f"{page}.api.rst"
        stale.discard(path)
        content = body.rstrip() + "\n"
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    for path in stale:
        path.unlink()


def remove_obsolete_pages(
    app: Sphinx,
    env: BuildEnvironment,
    added: set[str],
    changed: set[str],
    removed: set[str],
) -> list[str]:
    """
    Drop obsolete API output during an incremental preview build.

    Returns
    -------
    list
        Additional pages to reread. Removing output requires none.
    """
    if app.builder.name == "dirhtml":
        for page in removed:
            if page.startswith("api/"):
                app.builder.get_output_path(page).unlink(missing_ok=True)
    return []


def api_links(app: Sphinx, document: nodes.document) -> None:
    """Preserve bookmarks and link each signature to its source."""
    if not app.env.docname.startswith("api/"):
        return
    for sig in document.findall(addnodes.desc_signature):
        module = sig.get("module")
        name = sig.get("fullname", "")
        obj = app.env.autoapi_all_objects.get(f"{module}.{name}")
        if obj is None:
            continue
        source = Path(app.env.autoapi_all_objects[module].obj["file_path"])
        app.env.note_dependency(source)
        anchor = name.replace(".", "").lower()
        if anchor not in sig["ids"]:
            sig["ids"].append(anchor)
        url = app.config.alto_source_urls.get(
            source.relative_to(app.srcdir.parent).as_posix(),
        )
        if url and "from_line_no" in obj.obj:
            href = f"{url}#L{obj.obj['from_line_no']}"
            sig += nodes.Text(" ")
            sig += nodes.reference("", "Source", refuri=href)


def setup(app: Sphinx) -> dict[str, bool]:
    """
    Register API discovery after AutoAPI parses the sources.

    Returns
    -------
    dict
        Sphinx extension metadata.
    """
    app.add_config_value("alto_source_urls", {}, "env")
    app.connect("config-inited", configure_source_urls)
    app.connect("builder-inited", generate_pages, priority=600)
    app.connect("autodoc-process-docstring", field_tables, priority=400)
    app.connect("env-get-outdated", remove_obsolete_pages)
    app.connect("doctree-read", api_links)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
