"""Build the ExerciseView walkthrough from the shared guide."""

# ruff: noqa: INP001 -- Sphinx loads this extension by path.
# ruff: noqa: PLR0917 -- Sphinx calls event handlers positionally.
from __future__ import annotations

import json
import re
import shlex
from typing import TYPE_CHECKING

from docs_excerpts import SOURCE, excerpts
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

if TYPE_CHECKING:
    from sphinx.application import Sphinx

GUIDE = "developer-guide/exercise-view"
PUBLISHED = "https://altosaurus.github.io/alto/dev"


def render_guide(app: Sphinx, docname: str, source: list[str]) -> None:
    """Render the shared chapter’s figures and source listings."""
    if docname != GUIDE:
        return
    module = app.srcdir.parent / SOURCE
    app.env.note_dependency(module)
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
    url = app.config.alto_source_urls.get(SOURCE, "")
    builder = app.builder

    def link(path: str) -> str:
        """
        Choose the destination for a guide link.

        Returns
        -------
        str
            Local class URL or published URL for an unported page.
        """
        page, anchor, fragment = path.partition("#")
        if page.startswith("/api/"):
            return (
                builder.get_relative_uri(GUIDE, page.strip("/"))
                + anchor
                + fragment
            )
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


def setup(app: Sphinx) -> dict[str, bool]:
    """
    Register the walkthrough build hook.

    Returns
    -------
    dict
        Sphinx extension metadata.
    """
    app.connect("source-read", render_guide)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
