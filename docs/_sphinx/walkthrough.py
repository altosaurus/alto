"""Build the ExerciseView walkthrough and API preview."""

# ruff: noqa: INP001 -- Sphinx loads this extension by path.
# ruff: noqa: PLR0917 -- Sphinx calls event handlers positionally.
from __future__ import annotations

import json
import re
import shlex
import subprocess
from typing import TYPE_CHECKING

from api_docs import TABLE_SECTIONS, entries
from docs_excerpts import SOURCE, excerpts
from docutils import nodes
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
from sphinx import addnodes

if TYPE_CHECKING:
    from sphinx.application import Sphinx

GUIDE = "developer-guide/exercise-view"
API = "api/alto.ui.exercise_view/class-exerciseview"
PUBLISHED = "https://altosaurus.github.io/alto/dev"


def source_url(app: Sphinx) -> str:
    """
    Find the committed source behind the listings.

    Returns
    -------
    str
        URL of the last file revision, or empty for local edits.
    """
    repo = app.srcdir.parent
    if subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", SOURCE],
        cwd=repo,
        check=False,
    ).returncode:
        return ""
    sha = subprocess.check_output(
        ["git", "log", "-1", "--format=%H", "HEAD", "--", SOURCE],
        cwd=repo,
        text=True,
    ).strip()
    if not sha:
        return ""
    return f"https://github.com/altosaurus/alto/blob/{sha}/{SOURCE}"


def render_guide(app: Sphinx, docname: str, source: list[str]) -> None:
    """Render the shared chapter’s figures and source listings."""
    if docname not in (GUIDE, API):
        return
    module = app.srcdir.parent / SOURCE
    app.env.note_dependency(module)
    if docname == API:
        return
    selections = app.srcdir / "_data/exercise_view_excerpts.json"
    components = app.srcdir / "_data/launch_components.json"
    diagram = app.srcdir / "_includes/first-question-c4.html"
    for path in (selections, components, diagram):
        app.env.note_dependency(path)
    for name in ("source-listing.html", "component-shot.html.jinja"):
        app.env.note_dependency(app.confdir / "templates" / name)
    snippets = excerpts(
        module.read_text(encoding="utf-8"),
        selections=json.loads(selections.read_text(encoding="utf-8")),
    )
    regions = json.loads(components.read_text(encoding="utf-8"))
    url = app.config.alto_source_url
    builder = app.builder
    local_api = builder.get_relative_uri(GUIDE, API)

    def link(path: str) -> str:
        """
        Choose the destination for a guide link.

        Returns
        -------
        str
            Local class URL or published URL for an unported page.
        """
        page, anchor, fragment = path.partition("#")
        if page.strip("/") == API:
            return local_api + anchor + fragment
        return PUBLISHED + path

    def include(match: re.Match[str]) -> str:
        """
        Render a chapter illustration.

        Returns
        -------
        str
            MyST raw HTML block containing the figure or code listing.

        Raises
        ------
        ValueError
            For an unrecognized include.
        """
        name, *options = shlex.split(match[1])
        args = dict(option.split("=", 1) for option in options)
        if name == "first-question-c4.html":
            html = diagram.read_text(encoding="utf-8")
        elif name == "component-shot.html":
            html = builder.templates.render(
                "component-shot.html.jinja",
                {
                    **args,
                    "regions": regions[args["screen"]],
                    "link": link,
                    "images": "../../_static",
                },
            )
        elif name == "exercise-view-source.html":
            snippet = snippets[args["name"]]
            html = builder.templates.render(
                "source-listing.html",
                {
                    **snippet,
                    "path": SOURCE,
                    "url": url,
                    "highlighted": highlight(
                        str(snippet["code"]),
                        PythonLexer(),
                        HtmlFormatter(nowrap=True),
                    ),
                },
            )
        else:
            raise ValueError(f"Unknown walkthrough include: {name}")
        return f"```{{raw}} html\n{html}\n```"

    source[0] = re.sub(r"{% include (.*?) %}", include, source[0])
    source[0] = re.sub(
        r"{{ '([^']+)' \| relative_url }}",
        lambda m: link(m[1]),
        source[0],
    )


def field_tables(
    app: Sphinx,
    what: str,
    name: str,
    obj: object,
    options: object,
    lines: list[str],
) -> None:
    """Format NumPy fields as tables before Napoleon parses examples."""

    def table(match: re.Match[str]) -> str:
        """
        Render one block of fields.

        Returns
        -------
        str
            A reStructuredText table with one row per entry.
        """
        title = match[1]
        fields = entries(match[2])
        named = title != "Returns" or any(field[0] for field in fields)
        header = [TABLE_SECTIONS[title]] if named else []
        rows = [header + ["Type", "Description"]]
        for field, kind, description in fields:
            cells = [f"``{field}``" if field else ""] if named else []
            rows.append(cells + [f"``{kind}``", description])
        body = ["   * - " + "\n     - ".join(row) for row in rows]
        return "\n".join(
            [
                f".. list-table:: {title}",
                "   :header-rows: 1",
                "",
                *body,
                "",
            ],
        )

    text = re.sub(
        r"^(Parameters|Attributes|Returns)\n-{3,}\n([^\n]+(?:\n[^\n]+)*)",
        table,
        "\n".join(lines),
        flags=re.MULTILINE,
    )
    lines[:] = text.splitlines()


def skip_empty_attribute(
    app: Sphinx,
    what: str,
    name: str,
    obj: object,
    skip: bool,
    options: object,
) -> bool | None:
    """
    Keep inferred instance fields out of the public methods list.

    Returns
    -------
    bool or None
        True for an undocumented field, otherwise Sphinx decides.
    """
    if getattr(obj, "type", None) == "attribute" and not getattr(
        obj,
        "docstring",
        "",
    ):
        return True
    return None


def api_links(app: Sphinx, document: nodes.document) -> None:
    """Preserve method bookmarks and link signatures to their source."""
    if app.env.docname != API:
        return
    for sig in document.findall(addnodes.desc_signature):
        name = sig.get("fullname", "")
        obj = app.env.autoapi_all_objects.get(f"{sig.get('module')}.{name}")
        if obj is None:
            continue
        sig["ids"].append(name.replace(".", "").lower())
        if app.config.alto_source_url and "from_line_no" in obj.obj:
            href = f"{app.config.alto_source_url}#L{obj.obj['from_line_no']}"
            sig += nodes.Text(" ")
            sig += nodes.reference("", "Source", refuri=href)


def setup(app: Sphinx) -> dict[str, bool]:
    """
    Register the walkthrough and API build hooks.

    Returns
    -------
    dict
        Sphinx extension metadata.
    """
    app.add_config_value("alto_source_url", source_url(app), "env")
    app.connect("source-read", render_guide)
    app.connect("doctree-read", api_links)
    app.connect("autodoc-skip-member", skip_empty_attribute)
    app.connect("autodoc-process-docstring", field_tables, priority=400)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
