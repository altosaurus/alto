"""
Public-domain piano excerpts available for offline notation practice.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path


@dataclass(frozen=True)
class Excerpt:
    """
    A versioned score and its visible notation components in SVG marker
    order.
    """

    folder: Path
    credit: str
    targets: tuple[str, ...]


@cache
def excerpts() -> dict[str, Excerpt]:
    """
    Read the bundled excerpt manifests.

    Returns
    -------
    dict
        Passages keyed by their permanent, versioned directory names.
    """
    catalog = {}
    for manifest in sorted(
        Path(__file__)
        .with_name("assets")
        .joinpath("excerpts")
        .glob("*/excerpt.json"),
    ):
        data = json.loads(manifest.read_text(encoding="utf-8"))
        start, end = data["measures"]
        measures = f"m. {start}" if start == end else f"mm. {start}–{end}"
        credit = f"{data['composer']} · {data['work']} · {measures}"
        catalog[manifest.parent.name] = Excerpt(
            manifest.parent,
            credit,
            tuple(data["targets"]),
        )
    return catalog


@cache
def passages_by_term() -> dict[str, dict[str, list[int]]]:
    """
    Group score locations by term and passage so dense passages do not
    dominate the selection.

    Returns
    -------
    dict
        Matching marker indices for each term in each passage.
    """
    locations: dict[str, dict[str, list[int]]] = {}
    for key, excerpt in excerpts().items():
        for index, term in enumerate(excerpt.targets):
            locations.setdefault(term, {}).setdefault(key, []).append(index)
    return locations
