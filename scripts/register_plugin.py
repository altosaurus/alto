#!/usr/bin/env python3
"""Prepare a registry change from the GitHub issue as it appeared when a maintainer approved it."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

import yaml
from scripts.check_plugin_registry import REGISTRY, check_registry, registry_history

FORM = Path(".github/ISSUE_TEMPLATE/plugin-registration.yml")


def issue_entry(issue: dict, *, form: dict) -> dict[str, str]:
    """
    Convert a completed issue form into the entry that Alto uses for installation and its docs.

    Parameters
    ----------
    issue : dict
        The issue number and Markdown body from the label event.
    form : dict
        GitHub form definition, which supplies field labels and the required license statement.

    Returns
    -------
    dict of str to str
        A registry entry with the issue number as its install code.

    Raises
    ------
    ValueError
        If the issue is incomplete, the URLs are invalid, or the author has not confirmed the rights statement.

    Examples
    --------
    Issue 247 yields the install code "247".
    """
    number, body = issue.get("number"), issue.get("body")
    if type(number) is not int or number < 1 or not isinstance(body, str):
        raise ValueError("Expected a numbered issue with a completed plugin registration form.")
    fields = {item["attributes"]["label"]: item for item in form["body"] if "id" in item}
    headings = "|".join(re.escape(label) for label in fields)
    parts = re.split(rf"^### ({headings})[ \t]*$", body.replace("\r\n", "\n"), flags=re.MULTILINE)
    answers: dict[str, str] = {}
    for label, content in zip(parts[1::2], parts[2::2], strict=True):
        key = fields[label]["id"]
        if key in answers:
            raise ValueError(f"Duplicate issue heading: {label}.")
        answers[key] = content.strip()
    for label, field in fields.items():
        answer = answers.get(field["id"], "")
        if field.get("validations", {}).get("required") and answer in ("", "_No response_"):
            raise ValueError(f"Complete the {label} field before approval.")
    rights = fields["Rights and licenses"]["attributes"]["options"][0]["label"]
    checked = " ".join(answers.get("rights-and-licenses", "").split())
    if checked not in (f"- [x] {rights}", f"- [X] {rights}"):
        raise ValueError("The author must check the Rights and licenses statement in the registration form.")

    repository = answers["repository"].rstrip("/").removesuffix(".git")
    if not re.fullmatch(r"https://github\.com/[\w-]+/[\w.-]+", repository, re.ASCII) or repository.rsplit("/", 1)[1] in (
        ".",
        "..",
    ):
        raise ValueError("Use the HTTPS address of the plugin’s public GitHub repository.")
    entry = {
        "id": answers["pack-id"],
        "code": str(number),
        "name": answers["name"],
        "description": answers["description"],
        "repository": repository,
    }
    metadata = answers.get("metadata", "")
    if metadata and metadata != "_No response_":
        url = urlsplit(metadata)
        if url.scheme != "https" or not url.hostname or url.username or url.password or any(c.isspace() for c in metadata):
            raise ValueError("Use a public HTTPS URL for the metadata file.")
        entry["metadata"] = metadata
    return entry


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("event", type=Path, help="GitHub issues event JSON")
    args = parser.parse_args()
    try:
        issue = json.loads(args.event.read_bytes())["issue"]
        entry = issue_entry(issue, form=yaml.safe_load(FORM.read_text(encoding="utf-8")))
        registry = Path(REGISTRY)
        entries = json.loads(registry.read_bytes())
        if not isinstance(entries, list):
            raise ValueError("The registry must be a JSON array.")
        proposed = entries if entry in entries else [*entries, entry]
        check_registry(proposed, history=registry_history("HEAD"))
        if proposed != entries:
            registry.write_text(json.dumps(proposed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (KeyError, ValueError, OSError) as error:
        sys.exit(f"Plugin registration failed: {error}")
