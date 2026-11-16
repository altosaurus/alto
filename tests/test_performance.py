"""
Budgets for the speed of the app: pages, questions, painting and data must each stay within a generous time.

The operations are in `benchmarks/operations.py`, the same ones the ASV history records, and the time each may take is in
`benchmarks/budgets.py`. A budget is several times what the operation takes, so that a slow build machine does not fail a test,
but a change that makes something many times slower does.
"""

from __future__ import annotations

import pytest
from benchmarks.budgets import budget_seconds
from benchmarks.operations import (
    Workbench,
    measure,
    measure_cold_in_new_process,
    operation_names,
    profile_cold,
)
from PySide6.QtWidgets import QApplication

pytestmark = pytest.mark.perf


def test_benchmark_settling_and_closing_release_widgets(app: QApplication) -> None:
    """
    Check that page switches and benchmark teardown destroy widgets instead of accumulating discarded pages.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    bench = Workbench()
    discarded = []
    closed = []
    bench.window.destroyed.connect(lambda: closed.append(True))
    try:
        bench.window.open_exercise(bench.exercises[0])
        previous = bench.window.stack.currentWidget()
        assert previous is not None
        previous.destroyed.connect(lambda: discarded.append(True))
        bench.window.open_exercise(bench.exercises[1])
        bench.settle()
        assert discarded == [True]
    finally:
        bench.close()
    assert closed == [True]


def test_every_operation_is_listed_by_name_and_has_a_budget(app: QApplication) -> None:
    """
    Check that the names the ASV benchmarks list before running are the operations that exist, and that each has a budget.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    bench = Workbench()
    try:
        assert sorted(operation_names()) == sorted(bench.operations)
        for name in bench.operations:
            assert budget_seconds(name) > 0
    finally:
        bench.close()


def test_every_operation_is_within_its_budget(app: QApplication) -> None:
    """
    Check that opening each page, asking and answering questions, painting, and reading and writing data are within their budgets.

    The app is built once, with a year of practice behind it. An operation over its budget is measured again before the test
    fails, so that one slow moment of the machine does not.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    bench = Workbench()
    try:
        slow = {}
        for name, operation in bench.operations.items():
            budget = budget_seconds(name)
            seconds = measure(operation)
            if seconds > budget:
                seconds = min(seconds, measure(operation, repeats=9))
            if seconds > budget:
                slow[name] = f"{seconds * 1000:.0f} ms, over its budget of {budget * 1000:.0f} ms"
    finally:
        bench.close()
    assert not slow, "\n".join(f"{name}: {how}" for name, how in slow.items())


@pytest.mark.parametrize("name", ["startup", "resize:circle", "page:CircleOfFifths", "page:lesson"])
def test_the_first_use_in_a_new_process_is_within_its_budget(name: str) -> None:
    """
    Check starting the app, the first look at a page, and drawing the circle at new sizes, all of which are slower the first time.

    Parameters
    ----------
    name : str
        The operation: "startup" or a page.
    """
    # Only a new process shows the cost of text sizes that have not been used: in this one other tests have used most of them.
    seconds = measure_cold_in_new_process(name, repeats=1)
    budget = budget_seconds(name, cold=True)
    assert seconds <= budget, f"{name}: {seconds * 1000:.0f} ms, over its budget of {budget * 1000:.0f} ms"


def test_the_profile_of_an_operation_shows_where_its_time_goes(
    app: QApplication,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    Check that profiling an operation prints the functions that took longest, and only for the operation itself.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    capsys : pytest.CaptureFixture
        Collects what is printed.
    """
    profile_cold("data:count", lines=5)
    shown = capsys.readouterr().out
    assert "function calls" in shown and "count_attempts" in shown
    assert "fill" not in shown  # the building of the test data is not part of what is profiled
