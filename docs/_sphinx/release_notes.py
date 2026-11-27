"""Render the release history from the selected revision’s changelog."""

# ruff: noqa: INP001 -- Sphinx loads this module by path.
import re

RELEASES = "https://github.com/altosaurus/alto/releases/tag/v"
HEADING = re.compile(
    r"^## \[(?P<name>[^]]+)](?: - (?P<date>\d{4}-\d{2}-\d{2}))?[ \t]*$",
    re.MULTILINE,
)
LINK_DEFINITION = re.compile(r"^\[[^]]+]:\s+\S+[ \t]*$")


def sections(text: str) -> list[tuple[str, str | None, str]]:
    r"""
    Cut a changelog into its versions.

    A version starts at its `## [name]` heading and ends at the next
    one. The link definitions that close the file are not part of
    the last version.

    Parameters
    ----------
    text : str
        The changelog.

    Returns
    -------
    list of tuple of (str, str or None, str)
        For each version, in the order of the file: its name
        ("Unreleased" or such as "0.0.0"), its date (None if it has
        none) and
        its notes, without the blank lines around them.

    Examples
    --------
    >>> log = (
    ...     "# Changelog\n\n## [Unreleased]\n\n## [0.1.0] - 2026-12-01"
    ...     "\n\nNotes.\n\n- One.\n\n[0.1.0]: https://example.org\n"
    ... )
    >>> sections(log)[1]
    ('0.1.0', '2026-12-01', 'Notes.\n\n- One.')
    """
    found = list(HEADING.finditer(text))
    result = []
    for number, heading in enumerate(found):
        end = (
            found[number + 1].start() if number + 1 < len(found) else len(text)
        )
        lines = text[heading.end() : end].splitlines()
        while lines and (
            not lines[-1].strip() or LINK_DEFINITION.match(lines[-1])
        ):
            lines.pop()
        result.append(
            (
                heading.group("name"),
                heading.group("date"),
                "\n".join(lines).strip(),
            ),
        )
    return result


def untitled(notes: str) -> str:
    r"""
    Keep the headings of a version's notes out of the page's "On this
    page" list, which is for the versions.

    Parameters
    ----------
    notes : str
        A version's notes.

    Returns
    -------
    str
        The notes, with a marker after each `###` heading.

    Examples
    --------
    >>> print(untitled("### Added\n\n- One."))
    ### Added
    {: .no-toc}
    <BLANKLINE>
    - One.
    """
    out = []
    for line in notes.splitlines():
        out.append(line)
        if line.startswith("### "):
            out.append("{: .no-toc}")
    return "\n".join(out)


def render(text: str) -> str:
    r"""
    Render a section for each version in the changelog.

    Unreleased changes are shown at the top while there are any, and
    left out when there are none.

    Parameters
    ----------
    text : str
        The changelog.

    Returns
    -------
    str
        The Markdown body of the release history.

    Examples
    --------
    >>> log = (
    ...     "# Changelog\n\n## [Unreleased]\n\n## [0.1.0] - 2026-12-01"
    ...     "\n\nNotes.\n"
    ... )
    >>> page = render(log)
    >>> (
    ...     "## Unreleased" in page,
    ...     "## 0.1.0" in page,
    ...     "Released 2026-12-01" in page,
    ... )
    (False, True, True)
    """
    body = []
    for name, date, notes in sections(text):
        if name == "Unreleased":
            if notes:
                body.append(
                    "## Unreleased\n\nChanges that are in the development "
                    "docs and not in a release yet.\n\n"
                    f"{untitled(notes)}"
                    "\n",
                )
            continue
        when = f"Released {date}. " if date else ""
        body.append(
            "## "
            f"{name}"
            "\n\n"
            f"{when}"
            "[GitHub release]("
            f"{RELEASES}"
            f"{name}"
            ")\n\n"
            f"{untitled(notes)}"
            "\n",
        )
    return "\n".join(body)
