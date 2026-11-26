#!/usr/bin/env python3
"""Extract the walkthrough's statements and line numbers for Jekyll."""

import argparse
import ast
import json
import subprocess
from pathlib import Path
from textwrap import dedent

SOURCE = "alto/ui/exercise_view.py"


def excerpts(
    source: str,
    *,
    selections: dict[str, list[str]],
) -> dict[str, dict[str, int | str]]:
    r"""
    Resolve each excerpt's anchors within its ExerciseView method.

    Parameters
    ----------
    source : str
        Python module from the working tree or release commit.
    selections : dict
        Method name followed by one or two text anchors per excerpt.

    Returns
    -------
    dict
        Inclusive source lines and dedented code for each excerpt.

    Raises
    ------
    ValueError
        If an anchor is missing, ambiguous, or out of order.

    Examples
    --------
    >>> source = (
    ...     "class ExerciseView:\n    def show(self):\n"
    ...     "        self.staff.show()"
    ... )
    >>> selections = {"staff": ["show", "self.staff.show()"]}
    >>> excerpts(source, selections=selections)
    {'staff': {'start': 3, 'end': 3, 'code': 'self.staff.show()'}}
    """
    lines = source.splitlines()
    view = next(
        node
        for node in ast.parse(source).body
        if isinstance(node, ast.ClassDef) and node.name == "ExerciseView"
    )
    methods = {
        node.name: node
        for node in view.body
        if isinstance(node, ast.FunctionDef)
    }
    result = {}
    for name, (method_name, *anchors) in selections.items():
        method = methods[method_name]
        statements = [
            (node.lineno, node.end_lineno)
            for node in ast.walk(method)
            if isinstance(node, ast.stmt) and node.end_lineno is not None
        ]
        assert method.end_lineno is not None
        bounds = []
        for anchor in anchors:
            matches = [
                line
                for line in range(method.lineno, method.end_lineno + 1)
                if anchor in lines[line - 1]
            ]
            if len(matches) != 1:
                raise ValueError(
                    f"{name}: expected one {anchor!r} in "
                    f"ExerciseView.{method_name}, found {len(matches)}",
                )
            line = matches[0]
            statement = min(
                (
                    (start, end)
                    for start, end in statements
                    if start <= line <= end
                ),
                key=lambda span: span[1] - span[0],
            )
            bounds.append(statement)
        start, end = bounds[0][0], bounds[-1][1]
        if start > end:
            raise ValueError(f"{name}: excerpt anchors are out of order")
        result[name] = dict(
            start=start,
            end=end,
            code=dedent("\n".join(lines[start - 1 : end])),
        )
    return result


def main() -> None:
    """
    Write excerpt data for one version of the guide.

    Examples
    --------
    Generate the line numbers and code from the current commit.

        python scripts/docs_excerpts.py --revision HEAD
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--docs",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "docs",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        help="Git checkout containing the requested revision",
    )
    parser.add_argument(
        "--revision",
        help="Read committed source instead of the working copy",
    )
    args = parser.parse_args()
    data = args.docs / "_data"
    selections = data / "exercise_view_excerpts.json"
    if not selections.exists():
        return  # Older versions of the guide have no source excerpts.
    repo = args.repo or args.docs.parent
    revision = subprocess.check_output(
        ["git", "-C", repo, "rev-parse", args.revision or "HEAD"],
        text=True,
    ).strip()
    committed = subprocess.check_output(
        ["git", "-C", repo, "show", f"{revision}:{SOURCE}"],
        text=True,
    )
    source = (
        committed
        if args.revision
        else (repo / SOURCE).read_text(
            encoding="utf-8",
        )
    )
    result = {
        "revision": revision if source == committed else None,
        "excerpts": excerpts(
            source,
            selections=json.loads(selections.read_text(encoding="utf-8")),
        ),
    }
    (data / "exercise_view_lines.json").write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
