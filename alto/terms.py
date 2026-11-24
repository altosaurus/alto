"""
Glossary entries that an installed plugin supplies, kept apart from the
built-in ones.

A plugin describes each entry in its manifest as plain text, and may
show one of its own instrument pictures with it. The glossary
page merges these with the built-in terms and lists them under their own
names.

Examples
--------
>>> entry = PluginTerm(
...     name="scroll",
...     pack="Demo",
...     definition="The carved end.",
...     lessons=("pack.demo.parts",),
... )
>>> register_term(entry)
>>> PLUGIN_TERMS["scroll"] is entry
True
>>> _ = PLUGIN_TERMS.pop("scroll")
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from alto.exercises.base import (
    FingerboardPosition,
    PicturePosition,
)
from alto.instrument_packs import (
    PackInstrument,
    read_text,
)
from alto.lessons.packs import (
    inline,
    read_picture,
)

TERM_LIMIT = 40  # glossary entries in one plugin
TERM_KEYS = {
    "term",
    "definition",
    "guide",
    "picture",
    "caption",
    "exercises",
    "lessons",
}


@dataclass(frozen=True, kw_only=True)
class PluginTerm:
    """
    One glossary entry from a plugin.

    Attributes
    ----------
    name : str
        The term, as listed.
    pack : str
        The plugin's display name.
    definition : str
        What the term means, as simple HTML.
    guide : str
        How to recognize or use it, as simple HTML. May be empty.
    picture : PicturePosition or None
        An instrument picture to show beside the text, with the term
        marked on it. None for none.
    caption : str
        The words under the picture. May be empty.
    exercises : tuple of str
        The registered keys of the exercises to offer as practice.
    lessons : tuple of str
        The keys of the lessons to offer.

    Examples
    --------
    >>> PluginTerm(
    ...     name="nut",
    ...     pack="Demo",
    ...     definition="It holds the strings.",
    ... ).exercises
    ()
    """

    name: str
    pack: str
    definition: str
    guide: str = ""
    picture: PicturePosition | None = None
    caption: str = ""
    exercises: tuple[str, ...] = ()
    lessons: tuple[str, ...] = ()


PLUGIN_TERMS: dict[str, PluginTerm] = {}
(
    "Every plugin entry by its term. Installed plugins add theirs with "
    "`register_term`."
)


def register_term(entry: PluginTerm) -> None:
    """
    Add a plugin's glossary entry.

    Parameters
    ----------
    entry : PluginTerm
        The entry.

    Raises
    ------
    ValueError
        If another plugin already supplies the same term.

    Examples
    --------
    >>> register_term(
    ...     PluginTerm(
    ...         name="bridge",
    ...         pack="Demo",
    ...         definition="It lifts the strings.",
    ...     )
    ... )
    >>> register_term(
    ...     PluginTerm(
    ...         name="bridge",
    ...         pack="Other",
    ...         definition="Again.",
    ...     )
    ... )
    Traceback (most recent call last):
    ...
    ValueError: The term bridge is already supplied by Demo.
    >>> _ = PLUGIN_TERMS.pop("bridge")
    """
    if entry.name in PLUGIN_TERMS:
        raise ValueError(
            "The term "
            f"{entry.name}"
            " is already supplied by "
            f"{PLUGIN_TERMS[entry.name].pack}"
            ".",
        )
    PLUGIN_TERMS[entry.name] = entry


def read_terms(
    value: object,
    *,
    pack_id: str,
    pack_name: str,
    instruments: Mapping[str, PackInstrument],
    exercises: Mapping[str, str],
    lessons: Mapping[str, str],
) -> tuple[PluginTerm, ...]:
    """
    Validate the optional ``glossary`` list of a plugin manifest.

    Parameters
    ----------
    value : object
        The manifest's ``glossary`` entry: a list of objects with a
        ``term`` and a ``definition``, and optionally a ``guide``, a
        ``picture`` with a ``caption``, and the ids of related
        ``exercises`` and ``lessons``. None when there is none.
    pack_id : str
        The plugin's id. Keyword-only.
    pack_name : str
        The plugin's display name. Keyword-only.
    instruments : mapping of str to PackInstrument
        The plugin's instruments by qualified key. Keyword-only.
    exercises : mapping of str to str
        The plugin's exercises, from the id the manifest uses to the key
        Alto registers it under. Keyword-only.
    lessons : mapping of str to str
        The plugin's lessons, from the id the manifest uses to the key
        Alto registers it under. Keyword-only.

    Returns
    -------
    tuple of PluginTerm
        The entries, in the order the manifest lists them.

    Raises
    ------
    ValueError
        If an entry is malformed, repeats a term, or links to an
        exercise or lesson the plugin does not declare.

    Examples
    --------
    >>> read_terms(
    ...     None,
    ...     pack_id="demo",
    ...     pack_name="Demo",
    ...     instruments={},
    ...     exercises={},
    ...     lessons={},
    ... )
    ()
    >>> read_terms(
    ...     [
    ...         {
    ...             "term": "nut",
    ...             "definition": "It holds the strings.",
    ...         }
    ...     ],
    ...     pack_id="demo",
    ...     pack_name="Demo",
    ...     instruments={},
    ...     exercises={},
    ...     lessons={},
    ... )[0].name
    'nut'
    """
    if value is None:
        return ()
    if not isinstance(value, list) or not value or len(value) > TERM_LIMIT:
        raise ValueError(f"List between 1 and {TERM_LIMIT} glossary entries.")
    entries: list[PluginTerm] = []
    for row in value:
        if (
            not isinstance(row, dict)
            or set(row) - TERM_KEYS
            or not {"term", "definition"} <= set(row)
        ):
            raise ValueError(
                "Each glossary entry takes a term and a definition, and "
                "only these fields: "
                f"{', '.join(sorted(TERM_KEYS))}"
                ".",
            )
        name = read_text(
            row["term"],
            limit=40,
            what="term",
            where="a glossary entry",
        )
        where = f"glossary entry {name!r}"
        if any(earlier.name == name for earlier in entries):
            raise ValueError(
                f"The term {name!r} appears twice in the glossary.",
            )
        picture = None
        if "picture" in row:
            shown = read_picture(
                row["picture"],
                where=where,
                pack_id=pack_id,
                instruments=instruments,
            )
            if isinstance(shown, FingerboardPosition):
                raise ValueError(
                    "Show "
                    f"{where}"
                    " a marked place on the picture, not a note on a "
                    "string.",
                )
            picture = shown
        links = []
        for field, known in (("exercises", exercises), ("lessons", lessons)):
            ids = row.get(field, [])
            if (
                not isinstance(ids, list)
                or len(ids) > 5
                or len(set(map(str, ids))) != len(ids)
            ):
                raise ValueError(
                    f"List up to five distinct {field} for {where}.",
                )
            if any(
                not isinstance(item, str) or item not in known for item in ids
            ):
                raise ValueError(
                    "Each of the "
                    f"{field}"
                    " of "
                    f"{where}"
                    " must be one of this plugin's "
                    f"{field}"
                    ".",
                )
            links.append(tuple(known[item] for item in ids))
        entries.append(
            PluginTerm(
                name=name,
                pack=pack_name,
                definition=inline(
                    read_text(
                        row["definition"],
                        limit=500,
                        what="definition",
                        where=where,
                    ),
                ),
                guide=inline(
                    read_text(
                        row["guide"],
                        limit=500,
                        what="guide",
                        where=where,
                    ),
                )
                if "guide" in row
                else "",
                picture=picture,
                caption=read_text(
                    row["caption"],
                    limit=120,
                    what="caption",
                    where=where,
                )
                if "caption" in row
                else "",
                exercises=links[0],
                lessons=links[1],
            ),
        )
    return tuple(entries)
