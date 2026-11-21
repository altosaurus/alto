#!/usr/bin/env python3
"""Check plugin registration names, pack IDs, and codes against the registry and its history."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from collections.abc import Iterable, Iterator
from pathlib import Path

REGISTRY = "docs/site-root/plugins.json"


def identities(entries: object) -> Iterator[tuple[str, str, str]]:
    """
    Read the identifying fields of each registration.

    Parameters
    ----------
    entries : object
        JSON value from the registry.

    Yields
    ------
    tuple of str, str, str
        Normalized display name, manifest ID, and registration code.

    Raises
    ------
    ValueError
        If a required field is absent or invalid.

    Examples
    --------
    >>> list(identities([{"name": " Viola  Studio ", "id": "viola", "code": "014"}]))
    [('viola studio', 'viola', '014')]
    """
    if not isinstance(entries, list):
        raise ValueError("The registry must be a JSON array.")
    for index, row in enumerate(entries, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"Registry entry {index} must be an object.")
        name, pack_id, code = row.get("name"), row.get("id"), row.get("code")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Registry entry {index} needs a plugin name.")
        if not isinstance(pack_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", pack_id):
            raise ValueError(f"Invalid Pack ID {pack_id!r} for {name!r}. Use lowercase letters, digits, and single hyphens.")
        if not isinstance(code, str) or not re.fullmatch(r"[0-9]+", code):
            raise ValueError(f"Plugin {name!r} needs a numeric registration code stored as a string.")
        yield " ".join(unicodedata.normalize("NFKC", name).casefold().split()), pack_id, code


def check_registry(entries: object, *, history: Iterable[object] = ()) -> None:
    """
    Reject duplicate identities and reassignment of previously registered names, IDs, or codes.

    Parameters
    ----------
    entries : object
        Proposed registry.
    history : Iterable of object
        Earlier registry snapshots, oldest first. The original owner retains each identity.

    Raises
    ------
    ValueError
        If two entries clash or an existing registration changes its pack ID or code.

    Examples
    --------
    >>> check_registry([])
    """
    owners: dict[tuple[str, str], str] = {}

    def record(snapshot: object) -> None:
        """
        Reserve a complete valid snapshot, committing all claims together.

        Parameters
        ----------
        snapshot : object
            Registry entries to validate against earlier registrations.

        Raises
        ------
        ValueError
            If a field is claimed by two registrations.

        Examples
        --------
        An empty snapshot leaves earlier claims in place.
        """
        claims: dict[tuple[str, str], str] = {}
        for name, pack_id, code in identities(snapshot):
            for field, value, owner in (
                ("Plugin name", name, code),
                ("Pack ID", pack_id, code),
                ("Registration code", code, pack_id),
            ):
                key = (field, value)
                previous = claims.get(key, owners.get(key))
                if key in claims or (previous is not None and previous != owner):
                    detail = f"pack {previous!r}" if field == "Registration code" else f"registration code {previous}"
                    raise ValueError(f"{field} {value!r} is already registered to {detail}.")
                claims[key] = owner
        owners.update(claims)

    for snapshot in history:
        try:
            record(snapshot)
        except ValueError:
            continue  # A rejected registry must not reserve names or prevent a later correction.
    record(entries)


def registry_history(base: str) -> Iterator[object]:
    """
    Read snapshots where the registry was added or changed on the target branch.

    Parameters
    ----------
    base : str
        Target branch tip or commit.

    Yields
    ------
    object
        Each historical JSON registry, including the last version before removal.

    Examples
    --------
    From the repository root, use `registry_history("main")` to check earlier registrations.
    """
    commits = subprocess.check_output(
        ["git", "log", "--first-parent", "--reverse", "--diff-filter=AM", "--format=%H", base, "--", REGISTRY],
        text=True,
    )
    for commit in commits.splitlines():
        raw = subprocess.check_output(["git", "show", f"{commit}:{REGISTRY}"])
        try:
            yield json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue  # A malformed historical file could not have been published.


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="HEAD", help="target branch or commit containing accepted registrations")
    args = parser.parse_args()
    try:
        check_registry(json.loads(Path(REGISTRY).read_bytes()), history=registry_history(args.base))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(f"Plugin registry check failed: {error}")
