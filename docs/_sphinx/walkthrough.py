"""Build the ExerciseView walkthrough from the shared guide."""

# ruff: noqa: INP001 -- Sphinx loads this extension by path.
from __future__ import annotations

import json
from typing import TYPE_CHECKING

from docs_excerpts import SOURCE, excerpts
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

if TYPE_CHECKING:
    from sphinx.application import Sphinx


def listings(app: Sphinx) -> dict[str, str]:
    """
    Render the source listings used in the ExerciseView walkthrough.

    Returns
    -------
    dict
        Highlighted listings keyed by the chapter’s excerpt names.
    """
    module = app.srcdir.parent / SOURCE
    selections = app.srcdir / "_data/exercise_view_excerpts.json"
    for path in (
        module,
        selections,
        app.confdir / "templates/source-listing.html",
    ):
        app.env.note_dependency(path)
    snippets = excerpts(
        module.read_text(encoding="utf-8"),
        selections=json.loads(selections.read_text(encoding="utf-8")),
    )
    url = app.config.alto_source_urls.get(SOURCE, "")
    return {
        name: app.builder.templates.render(
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
        for name, snippet in snippets.items()
    }
