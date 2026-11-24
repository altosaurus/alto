"""
The ASV benchmarks: every operation's time, and the first-use times,
recorded for each release so they can be compared.

Run `asv run` for the current commit, `asv run v0.0.0..HEAD` for the
commits since a tag, and `asv compare v0.0.0 HEAD` to see
what changed between two of them. `asv publish` writes the pages with a
graph for each operation.
"""

from __future__ import annotations

from benchmarks.operations import (
    COLD,
    Operation,
    Workbench,
    isolate,
    measure_cold_in_new_process,
    operation_names,
)

_BENCH: list[Workbench] = []


def workbench() -> Workbench:
    """
    Give the app and its long history, building them the first time in
    this process.

    Returns
    -------
    Workbench
        The shared workbench.
    """
    if not _BENCH:
        isolate()  # only now, so that importing this file changes nothing
        _BENCH.append(Workbench())
    return _BENCH[0]


class TimeOperation:
    """
    Time one operation of the app, with the app already warm: pages,
    questions, painting and data.
    """

    params = [operation_names()]
    param_names = ["operation"]
    # one run for each sample, with `setup` before each, so the state is
    # the same every time
    number = 1
    repeat = (5, 11, 20.0)
    warmup_time = 0.0
    timeout = 120.0
    operation: Operation

    def setup(self, name: str) -> None:
        """
        Put the app in the state the operation starts from.

        Parameters
        ----------
        name : str
            The operation's name.
        """
        self.operation = workbench().operations[name]
        self.operation.setup()

    def time_operation(self, name: str) -> None:
        """
        Do the operation.

        Parameters
        ----------
        name : str
            The operation's name.
        """
        assert self.operation.name == name  # the one that `setup` prepared
        self.operation.run()


class TrackFirstUse:
    """
    Time the first use of something in a new process: starting the app,
    and the first look at a page.
    """

    params = [list(COLD)]
    param_names = ["operation"]
    unit = "s"
    timeout = 300.0

    # noinspection PyMethodMayBeStatic
    def track_first_use(self, name: str) -> float:
        """
        Give the time of the first use, in seconds.

        Parameters
        ----------
        name : str
            "startup", or the name of an operation.

        Returns
        -------
        float
            The median of three new processes.
        """
        return measure_cold_in_new_process(name)
