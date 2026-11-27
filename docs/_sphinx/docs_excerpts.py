"""Locate ExerciseView listings by their source anchors."""

# ruff: noqa: INP001 -- Sphinx loads this module by path.
import ast
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
