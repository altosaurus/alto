#!/usr/bin/env python
"""
Write the API reference pages in docs/api from the docstrings in alto/.

    python scripts/api_docs.py            # rewrite docs/api
    python scripts/api_docs.py --check    # fail if docs/api is out of
    date, changing nothing

Each module indexes its public classes and functions. Each component
page contains its signature and docstring, including class methods.
The script reads source text without importing Alto or starting Qt.
GitHub Pages cannot run this script, so the pages are
committed, and `tests/test_api_docs.py` fails when they are
out of date.
"""

from __future__ import annotations

import argparse
import ast
import inspect
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "alto"
OUT = ROOT / "docs" / "api"
SECTION = re.compile(r"^(?P<title>[A-Z][A-Za-z ]+)\n-{3,}$", re.MULTILINE)
TABLE_SECTIONS = {
    "Parameters": "Parameter",
    "Attributes": "Attribute",
    "Returns": "Name",
}


def module_files() -> list[Path]:
    """
    List the modules that get a page: every file of the package except
    the `__init__` and `__main__` files.

    Returns
    -------
    list of Path
        The source files, ordered by package and then by name.

    Examples
    --------
    >>> top_level = [
    ...     dotted(p)
    ...     for p in module_files()
    ...     if package_of(p) == "alto"
    ... ]
    >>> top_level == sorted(top_level)
    True
    """
    files = [
        p
        for p in SOURCE.rglob("*.py")
        if p.name not in ("__init__.py", "__main__.py")
    ]
    return sorted(
        files,
        key=lambda p: (package_of(p) != "alto", package_of(p), p.name),
    )


def dotted(path: Path) -> str:
    """
    Return the dotted module name of a source file.

    Parameters
    ----------
    path : Path
        A file under `alto/`.

    Returns
    -------
    str
        The name, such as `alto.theory.pitch`.

    Examples
    --------
    >>> dotted(SOURCE / "theory" / "pitch.py")
    'alto.theory.pitch'
    >>> dotted(SOURCE / "theory" / "__init__.py")
    'alto.theory'
    """
    parts = list(path.relative_to(ROOT).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def package_of(path: Path) -> str:
    """
    Return the package a module belongs to.

    Parameters
    ----------
    path : Path
        A file under `alto/`.

    Returns
    -------
    str
        The dotted name of the folder it is in, such as `alto.theory`,
        or `alto` for a module at the top.

    Examples
    --------
    >>> package_of(SOURCE / "theory" / "pitch.py")
    'alto.theory'
    >>> package_of(SOURCE / "audio.py")
    'alto'
    """
    return dotted(path).rsplit(".", 1)[0]


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
    Read the entries of a Parameters, Attributes, Returns or Raises
    section.

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


def field_table(title: str, *, text: str) -> str:
    r"""
    Format the fields in a NumPy-style API section as a Markdown table.

    Parameters
    ----------
    title : str
        Parameters, Attributes, or Returns.
    text : str
        The section body.

    Returns
    -------
    str
        A header and one row per documented entry.

    Examples
    --------
    >>> print(field_table("Returns", text="int\n    Beat count."))
    | Type | Description |
    | --- | --- |
    | `int` | Beat count. |
    """
    fields = entries(text)
    named = title != "Returns" or any(name for name, _, _ in fields)
    headers = ["Type", "Description"]
    if named:
        headers.insert(0, TABLE_SECTIONS[title])
    rows = [headers, ["---"] * len(headers)]
    for name, kind, description in fields:
        if title != "Returns" and not name:
            name, kind = kind, ""
        # Kramdown keeps pipes inside code spans in the same cell.
        description = re.sub(
            r"(`+).*?\1|\|",
            lambda match: r"\|" if match[0] == "|" else match[0],
            description,
        )
        cells = [f"`{kind}`" if kind else "", description]
        if named:
            cells.insert(0, f"`{name}`" if name else "")
        rows.append(cells)
    return "\n".join("| " + " | ".join(row) + " |" for row in rows)


def render_doc(doc: str | None) -> str:
    r"""
    Turn a docstring into Markdown.

    Parameters
    ----------
    doc : str or None
        The raw docstring, or None if there is none.

    Returns
    -------
    str
        The Markdown: the text, then each section. The examples go in a
        fenced block.

    Examples
    --------
    >>> print(
    ...     render_doc(
    ...         "Do it.\n\nParameters\n----------\nn : int\n    How "
    ...         "many."
    ...     )
    ... )
    Do it.
    <BLANKLINE>
    **Parameters**
    <BLANKLINE>
    | Parameter | Type | Description |
    | --- | --- | --- |
    | `n` | `int` | How many. |
    """
    if not doc:
        return ""
    parts = split_sections(inspect.cleandoc(doc))
    out = [parts[""]] if parts[""] else []
    for title, text in parts.items():
        if not title:
            continue
        if title == "Examples":
            # Rouge uses its console lexer for Python sessions,
            # including continuation prompts.
            lexer = (
                "console?lang=python&prompt=%3E%3E%3E,..."
                if ">>> " in text
                else "text"
            )
            out.append(f"**Examples**\n\n```{lexer}\n{text}\n```")
        elif title in TABLE_SECTIONS:
            out.append(f"**{title}**\n\n{field_table(title, text=text)}")
        elif title in ("Yields", "Raises"):
            lines = []
            for name, kind, desc in entries(text):
                label = (
                    f"`{name}` (*{kind}*)"
                    if name and kind
                    else f"`{name}`"
                    if name
                    else f"*{kind}*"
                )
                lines.append(f"- {label}: {desc}" if desc else f"- {label}")
            out.append(f"**{title}**\n\n" + "\n".join(lines))
        else:
            out.append(f"**{title}**\n\n{text}")
    return "\n\n".join(out)


def parameters(args: ast.arguments) -> list[str]:
    """
    List the parameters of a function as they are written in its
    signature, without `self` or `cls`.

    Parameters
    ----------
    args : ast.arguments
        The function's arguments.

    Returns
    -------
    list of str
        One string per parameter, such as `n: int = 3`, with `*` and
        `**` entries where they belong.

    Examples
    --------
    >>> parameters(
    ...     ast.parse(
    ...         "def f(self, a: int, *, b: str = 'x', **rest: int): ..."
    ...     )
    ...     .body[0]
    ...     .args
    ... )
    ['a: int', '*', "b: str = 'x'", '**rest: int']
    """
    positional = [*args.posonlyargs, *args.args]
    if positional and positional[0].arg in ("self", "cls"):
        positional = positional[1:]
    defaults: list[ast.expr | None] = [None] * (
        len(args.posonlyargs) + len(args.args) - len(args.defaults)
    ) + list(args.defaults)
    defaults = defaults[len(defaults) - len(positional) :]

    def one(arg: ast.arg, *, default: ast.expr | None) -> str:
        """
        Write one parameter.

        Parameters
        ----------
        arg : ast.arg
            The parameter.
        default : ast.expr or None
            Its default value, if it has one. Keyword-only.

        Returns
        -------
        str
            The parameter as written in a signature.

        Examples
        --------
        >>> one(
        ...     ast.arg(
        ...         arg="n",
        ...         annotation=ast.Name(id="int"),
        ...     ),
        ...     default=ast.Constant(value=3),
        ... )
        'n: int = 3'
        """
        text = arg.arg + (
            f": {ast.unparse(arg.annotation)}" if arg.annotation else ""
        )
        return text + (
            f" = {ast.unparse(default)}" if default is not None else ""
        )

    out = [
        one(a, default=d) for a, d in zip(positional, defaults, strict=True)
    ]
    if args.vararg:
        out.append("*" + one(args.vararg, default=None))
    elif args.kwonlyargs:
        out.append("*")
    out += [
        one(a, default=d)
        for a, d in zip(args.kwonlyargs, args.kw_defaults, strict=True)
    ]
    if args.kwarg:
        out.append("**" + one(args.kwarg, default=None))
    return out


def fence(
    head: str,
    *,
    params: list[str] | None,
    returns: str = "",
) -> str:
    """
    Write a signature as a Python code block, one parameter to a line
    when there are two or more.

    Parameters
    ----------
    head : str
        What comes before the parentheses, such as `def area` or `Note`.
    params : list of str or None
        The parameters, or None for a name with no parentheses at all.
        Keyword-only.
    returns : str, default ""
        The return annotation, written after `->`. Keyword-only.

    Returns
    -------
    str
        The fenced code block.

    Examples
    --------
    >>> print(
    ...     fence(
    ...         "def f",
    ...         params=["a: int"],
    ...         returns="int",
    ...     )
    ... )
    ```python
    def f(a: int) -> int
    ```
    >>> print(fence("def f", params=["a", "b"]))
    ```python
    def f(
        a,
        b,
    )
    ```
    """
    tail = f" -> {returns}" if returns else ""
    if params is None:
        body = head + tail
    elif len(params) < 2:
        body = f"{head}({', '.join(params)}){tail}"
    else:
        body = (
            f"{head}(\n" + "".join(f"    {p},\n" for p in params) + f"){tail}"
        )
    return f"```python\n{body}\n```"


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


def signature_box(code: str, *, name: str, line: int) -> str:
    """
    Group a signature with its source link.

    Parameters
    ----------
    code : str
        The fenced Python signature.
    name : str
        The displayed class, function, or qualified method name.
    line : int
        The line where the definition starts in the module.

    Returns
    -------
    str
        The Markdown box with a version-specific source link.

    Examples
    --------
    >>> 'line=12' in signature_box('example()', name='example', line=12)
    True
    """
    return (
        '<div class="api-signature" markdown="1">\n\n'
        f"{code}\n\n"
        "{% endraw %}{% include api-source.html "
        f'name="{name}" line={line}'
        " %}{% raw %}\n\n</div>"
    )


def render_function(
    node: ast.FunctionDef,
    *,
    owner: str = "",
) -> str:
    r"""
    Write the section for one function or method.

    Parameters
    ----------
    node : ast.FunctionDef
        The function.
    owner : str, default ""
        The class name when rendering a method. Keyword-only.

    Returns
    -------
    str
        The Markdown: a heading, the signature and the docstring.

    Examples
    --------
    >>> tree = ast.parse(
    ...     "def f(n: int) -> int:\n    '''Double it.'''\n    return n"
    ...     " * 2"
    ... )
    >>> section = render_function(tree.body[0])
    >>> "def f(n: int) -> int" in section
    True
    """
    head = "\n".join(f"@{d}" for d in decorator_names(node))
    sig = fence(
        f"def {node.name}",
        params=parameters(node.args),
        returns=ast.unparse(node.returns) if node.returns else "",
    )
    if head:
        sig = sig.replace("```python\n", f"```python\n{head}\n", 1)
    name = f"{owner}.{node.name}" if owner else node.name
    parts = [
        f"## {name}" if owner else "",
        signature_box(sig, name=name, line=node.lineno),
        render_doc(ast.get_docstring(node, clean=False)),
    ]
    return "\n\n".join(p for p in parts if p)


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


def render_class(node: ast.ClassDef) -> str:
    r"""
    Write the section for one class: its constructor, its docstring and
    its public methods.

    Parameters
    ----------
    node : ast.ClassDef
        The class.

    Returns
    -------
    str
        The Markdown.

    Examples
    --------
    >>> tree = ast.parse(
    ...     "class C(Base):\n    '''A thing.'''\n    def go(self) -> "
    ...     "None:\n        '''Go.'''"
    ... )
    >>> "## C.go" in render_class(tree.body[0])
    True
    """
    init: ast.FunctionDef | None = None
    methods: list[ast.FunctionDef] = []
    for stmt in node.body:
        if isinstance(stmt, ast.FunctionDef) and stmt.name == "__init__":
            init = stmt
        elif isinstance(stmt, ast.FunctionDef) and not stmt.name.startswith(
            "_",
        ):
            methods.append(stmt)
    if init is not None:
        params: list[str] | None = parameters(init.args)
    elif any(
        d.startswith("dataclass") or d.endswith(".dataclass")
        for d in decorator_names(node)
    ):
        params = class_fields(node)
    else:
        params = None
    bases = ", ".join(ast.unparse(b) for b in node.bases)
    signature = (
        fence(node.name, params=params)
        if params is not None
        else fence(
            f"class {node.name}" + (f"({bases})" if bases else ""),
            params=None,
        )
    )
    parts = [signature_box(signature, name=node.name, line=node.lineno)]
    if params is not None and bases:
        parts.append(f"Bases: `{bases}`")
    parts.append(render_doc(ast.get_docstring(node, clean=False)))
    if init is not None and ast.get_docstring(init):
        built = render_doc(ast.get_docstring(init, clean=False)).replace(
            "**Examples**",
            "**Constructor examples**",
        )
        parts.append(f"**Constructor**\n\n{built}")
    parts.extend(
        render_function(method, owner=node.name) for method in methods
    )
    return "\n\n".join(p for p in parts if p)


def summary(doc: str | None) -> str:
    r"""
    Return the first paragraph of a docstring on one line.

    Parameters
    ----------
    doc : str or None
        The docstring.

    Returns
    -------
    str
        The first paragraph, joined into a single line. Empty if there
        is no docstring.

    Examples
    --------
    >>> summary(
    ...     "First line\ncontinues here.\n\nSecond paragraph."
    ... )
    'First line continues here.'
    """
    return (
        " ".join(inspect.cleandoc(doc).split("\n\n")[0].split()) if doc else ""
    )


def render_module(path: Path) -> dict[str, str]:
    """
    Build the module overview and the pages linked from its index.

    Parameters
    ----------
    path : Path
        The Python module to document.

    Returns
    -------
    dict of str to str
        Markdown pages keyed by path relative to the API reference.

    Examples
    --------
    >>> pages = render_module(SOURCE / "theory" / "pitch.py")
    >>> "alto.theory.pitch/class-note.md" in pages
    True
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    name = dotted(path)
    package = package_of(path)
    pages = {}
    groups: dict[str, list[str]] = {"Classes": [], "Functions": []}
    components = []
    fragments: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, (ast.ClassDef, ast.FunctionDef)):
            continue
        if node.name.startswith("_"):
            continue
        if isinstance(node, ast.ClassDef):
            kind, group = "class", "Classes"
            detail = render_class(node)
        else:
            kind, group = "function", "Functions"
            detail = render_function(node)
        slug = f"{kind}-{node.name.lower()}"
        url = f"/api/{name}/{slug}/"
        components.append({"title": node.name, "url": url})
        pages[f"{name}/{slug}.md"] = (
            f"---\ntitle: {node.name}\nparent: {name}\napi_module: {name}\n"
            f"package: {package}\npermalink: {url}\n---\n"
            f"{{% raw %}}\n{detail}\n{{% endraw %}}\n"
        )
        about = summary(ast.get_docstring(node))
        entry = f"- [`{node.name}`]({slug}/)"
        groups[group].append(f"{entry} — {about}" if about else entry)
        # Kramdown numbered duplicate headings, such as the class
        # Coverage and the function coverage in alto.instrument_info.
        anchor = node.name.lower()
        if anchor in fragments:
            anchor += "-1"
        fragments[anchor] = f"{slug}/"
        if isinstance(node, ast.ClassDef):
            for method in node.body:
                if not isinstance(method, ast.FunctionDef):
                    continue
                if not method.name.startswith("_"):
                    anchor = (node.name + method.name).lower()
                    fragments[anchor] = f"{slug}/#{anchor}"

    doc = render_doc(ast.get_docstring(tree, clean=False))
    intro, _, notes = doc.partition("\n\n")
    parts = [intro]
    for group, entries in groups.items():
        if entries:
            parts.extend([f"## {group}", "\n".join(entries)])
    if notes:
        parts.append(
            '<details markdown="1">\n'
            "<summary>Module notes and examples</summary>"
            f"\n\n{notes}\n\n</details>",
        )
    body = "\n\n".join(parts)
    components.sort(key=lambda component: component["title"])
    pages[f"{name}.md"] = (
        f"---\ntitle: {name}\nparent: api\npackage: {package}\n"
        f"api_components: {json.dumps(components)}\n"
        f"permalink: /api/{name}/\n---\n{{% raw %}}\n{body}\n{{% endraw %}}\n"
    )
    if fragments:
        pages[f"{name}.md"] += (
            f'\n<script type="application/json" id="api-fragments">'
            f"{json.dumps(fragments)}</script>\n"
            "{% include api-fragments.html %}\n"
        )
    return pages


def render_indexes(files: list[Path]) -> dict[str, str]:
    """
    Write the API index and an overview for each package.

    Parameters
    ----------
    files : list of Path
        Public modules in sidebar order.

    Returns
    -------
    dict of str to str
        The index and package pages, keyed by Markdown file name.

    Examples
    --------
    >>> sorted(render_indexes([SOURCE / "theory" / "pitch.py"]))
    ['alto.theory.md', 'index.md']
    """
    out = [
        (
            "---\ntitle: API reference\nnav_order: 11\nnav_group: For "
            "developers\nchildren: api\npermalink: /api/\n---\n"
        ),
        (
            "Choose a module to see its public classes and functions. "
            "Each has a page with its signature, documentation, and "
            "examples. Class pages also list their public methods. "
            "Names that begin with an "
            "underscore are internal and are left out. The pages are "
            "written from the docstrings by `scripts/api_docs.py`, so "
            "they match the code.\n"
        ),
    ]
    packages: dict[str, list[Path]] = {}
    for path in files:
        packages.setdefault(package_of(path), []).append(path)
    pages = {}
    for name, modules in packages.items():
        init = modules[0].parent / "__init__.py"
        about = (
            summary(ast.get_docstring(ast.parse(init.read_text("utf-8"))))
            if init.exists()
            else ""
        )
        out.extend([f"\n## [{name}]({name}/)\n", about])
        body = [
            (
                f"---\ntitle: {name}\nparent: api\npackage: {name}\n"
                f"api_package: true\npermalink: /api/{name}/\n---\n"
            ),
            about,
        ]
        subpackages = [
            pkg for pkg in packages if pkg.rpartition(".")[0] == name
        ]
        if subpackages:
            body.extend(["", "## Subpackages", ""])
            body.extend(f"- [{pkg}](../{pkg}/)" for pkg in subpackages)
        body.extend(["", "## Modules"])
        for page in (out, body):
            page.extend(["", "| Module | What it is |", "|---|---|"])
        for path in modules:
            module = dotted(path)
            tree = ast.parse(path.read_text("utf-8"))
            doc = summary(ast.get_docstring(tree)).replace("|", r"\|")
            out.append(f"| [{module}]({module}/) | {doc} |")
            body.append(f"| [{module}](../{module}/) | {doc} |")
        pages[f"{name}.md"] = "\n".join(body) + "\n"
    return {"index.md": "\n".join(out) + "\n", **pages}


def build() -> dict[str, str]:
    """
    Write every page, in memory.

    Returns
    -------
    dict of str to str
        File name (relative to `docs/api`) to its content.

    Examples
    --------
    >>> built = build()
    >>> "index.md" in built and "alto.audio.md" in built
    True
    """
    files = module_files()
    pages = render_indexes(files)
    for path in files:
        pages.update(render_module(path))
    return pages


def problems(*, out: Path = OUT) -> list[str]:
    """
    Compare the pages on disk with the ones the docstrings give.

    Parameters
    ----------
    out : Path, default docs/api
        The folder the pages are in. Keyword-only.

    Returns
    -------
    list of str
        One line for each page that is missing, out of date or no longer
        wanted. Empty when everything is current.

    Examples
    --------
    >>> problems(out=Path("/nonexistent"))[0]
    'missing: index.md'
    """
    wanted = build()
    found = {p.relative_to(out).as_posix() for p in out.rglob("*.md")}
    out_of_date = [
        f"out of date: {n}"
        for n, text in wanted.items()
        if n in found and (out / n).read_text(encoding="utf-8") != text
    ]
    return (
        [f"missing: {n}" for n in wanted if n not in found]
        + out_of_date
        + [f"no longer wanted: {n}" for n in sorted(found - set(wanted))]
    )


def write(*, out: Path = OUT) -> int:
    """
    Write the pages to disk and remove the ones that are no longer
    wanted.

    Parameters
    ----------
    out : Path, default docs/api
        The folder to write to. Keyword-only.

    Returns
    -------
    int
        How many pages were written.

    Examples
    --------
    >>> write(
    ...     out=Path("/tmp/api-docs-example")
    ... ) > 10  # doctest: +SKIP
    True
    """
    pages = build()
    out.mkdir(parents=True, exist_ok=True)
    for stale in out.rglob("*.md"):
        if stale.relative_to(out).as_posix() not in pages:
            stale.unlink()
    for name, text in pages.items():
        dest = out / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
    return len(pages)


def main() -> int:
    """
    Run the script: rewrite docs/api, or with `--check` only report what
    is out of date.

    Returns
    -------
    int
        0 on success, 1 if `--check` found pages that are out of date.

    Examples
    --------
    >>> main()  # doctest: +SKIP
    wrote 43 pages to docs/api
    0
    """
    parser = argparse.ArgumentParser(
        description=(__doc__ or "").split("\n")[1].strip(),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report out-of-date pages instead of writing them",
    )
    args = parser.parse_args()
    if args.check:
        found = problems()
        for line in found:
            print(line)
        if found:
            print("docs/api is out of date: run `python scripts/api_docs.py`")
        return 1 if found else 0
    count = write()
    print(f"wrote {count} pages to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
