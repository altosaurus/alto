"""Read NumPy docstring fields and dataclasses for AutoAPI."""

# ruff: noqa: INP001 -- Sphinx loads this module by path.
import ast
import re

SECTION = re.compile(r"^(?P<title>[A-Z][A-Za-z ]+)\n-{3,}$", re.MULTILINE)
TABLE_SECTIONS = {
    "Parameters": "Parameter",
    "Attributes": "Attribute",
    "Properties": "Property",
    "Returns": "Name",
}


def split_sections(doc: str) -> dict[str, str]:
    r"""
    Split a cleaned NumPy-style docstring into its sections.

    Parameters
    ----------
    doc : str
        The docstring, already dedented.

    Returns
    -------
    dict of str to str
        Section title to its text. The text before the first section is
        under the key "".

    Examples
    --------
    >>> split_sections(
    ...     "Summary.\n\nReturns\n-------\nint\n    A number."
    ... )
    {'': 'Summary.', 'Returns': 'int\n    A number.'}
    """
    found = list(SECTION.finditer(doc))
    out = {"": doc[: found[0].start()].strip() if found else doc.strip()}
    for i, m in enumerate(found):
        end = found[i + 1].start() if i + 1 < len(found) else len(doc)
        out[m["title"]] = doc[m.end() : end].strip("\n").rstrip()
    return out


def entries(text: str) -> list[tuple[str, str, str]]:
    r"""
    Read named fields and return or exception types from a section.

    Parameters
    ----------
    text : str
        The section's text.

    Returns
    -------
    list of tuple of str
        One `(name, type, description)` per entry. The name is empty for
        a Returns or Raises entry, which has only a type.

    Examples
    --------
    >>> entries(
    ...     "n : int\n    How many.\nflag : bool, default False\n    "
    ...     "Whether."
    ... )
    [('n', 'int', 'How many.'), ('flag', 'bool, default False',
    'Whether.')]
    >>> entries("int\n    A number.")
    [('', 'int', 'A number.')]
    """
    out: list[tuple[str, str, str]] = []
    for line in text.split("\n"):
        if line and not line.startswith(" "):
            name, sep, kind = line.partition(" : ")
            out.append((name, kind, "") if sep else ("", line, ""))
        elif line.strip() and out:
            name, kind, desc = out[-1]
            out[-1] = (name, kind, f"{desc} {line.strip()}".strip())
    return out


def decorator_names(node: ast.FunctionDef | ast.ClassDef) -> list[str]:
    r"""
    List the decorators of a function or class, written as in the
    source.

    Parameters
    ----------
    node : ast.FunctionDef or ast.ClassDef
        The definition.

    Returns
    -------
    list of str
        The decorators, without the `@`.

    Examples
    --------
    >>> decorator_names(
    ...     ast.parse(
    ...         "@property\ndef f(self): ..."
    ...     ).body[0]
    ... )
    ['property']
    """
    return [ast.unparse(d) for d in node.decorator_list]


def class_fields(node: ast.ClassDef) -> list[str]:
    r"""
    List the fields of a dataclass as constructor parameters.

    Parameters
    ----------
    node : ast.ClassDef
        The class.

    Returns
    -------
    list of str
        One string per field, with `*` where the keyword-only fields
        start (a `KW_ONLY` marker).

    Examples
    --------
    >>> tree = ast.parse(
    ...     "class C:\n    a: int\n    _: KW_ONLY\n    b: str = 'x'"
    ... )
    >>> class_fields(tree.body[0])
    ['a: int', '*', "b: str = 'x'"]
    """
    out = []
    for stmt in node.body:
        if not isinstance(stmt, ast.AnnAssign) or not isinstance(
            stmt.target,
            ast.Name,
        ):
            continue
        annotation = ast.unparse(stmt.annotation)
        if annotation == "KW_ONLY":
            out.append("*")
        elif not annotation.startswith("ClassVar"):
            out.append(
                f"{stmt.target.id}: {annotation}"
                + (
                    f" = {ast.unparse(stmt.value)}"
                    if stmt.value is not None
                    else ""
                ),
            )
    return out
