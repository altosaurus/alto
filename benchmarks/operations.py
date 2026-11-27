"""
The operations whose speed Alto watches: opening pages, asking and
answering questions, painting, and reading and writing data.

Each operation is a `setup` that puts the app in a known state, which is
not timed, and a `run` that is. The same list is used by
the budget tests in `tests/test_performance.py` (which fail when an
operation is far slower than it should be), by the ASV
benchmarks in `benchmarks/suite.py` (which keep the history from release
to release), and by `python -m benchmarks.survey`.

The app runs offscreen, with a profile with a long history, so the data
operations are measured on the
amount of practice a person has after a year or two rather than on an
empty database.
"""

from __future__ import annotations

import atexit
import cProfile
import os
import pstats
import random
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from alto.audio import sounds  # noqa: E402
from alto.exercises import REGISTRY  # noqa: E402
from alto.exercises.base import Exercise  # noqa: E402
from alto.learning import (  # noqa: E402
    Database,
    Learner,
)
from alto.learning.database import ItemRecord  # noqa: E402
from alto.ui.exercise_page import ExercisePage  # noqa: E402
from alto.ui.lesson import LessonsPage  # noqa: E402
from alto.ui.main_window import MainWindow  # noqa: E402
from alto.ui.reference import ExplorableCircle  # noqa: E402

DAY = 86_400.0
ATTEMPTS = 20_000  # about a year of daily practice


def isolate() -> str:
    """
    Give the app settings and data folders of its own, so that measuring
    never touches a person's real ones.

    The tests do not call this: their own set-up has already done the
    same.

    Returns
    -------
    str
        The folder that holds them, which is removed when the program
        ends.
    """
    home = tempfile.mkdtemp(prefix="alto-perf-")
    os.environ["XDG_CONFIG_HOME"] = f"{home}/config"
    os.environ["XDG_DATA_HOME"] = f"{home}/data"
    os.environ["ALTO_HOME"] = f"{home}/alto"
    atexit.register(lambda: shutil.rmtree(home, ignore_errors=True))
    return home


@dataclass(frozen=True)
class Operation:
    """
    One thing to time.

    Attributes
    ----------
    name : str
        What it is, such as "page:KeySignatures".
    setup : Callable
        Puts the app in the state the operation starts from. It is not
        timed.
    run : Callable
        The operation. It is timed, and it includes the events Qt
        handles afterwards (layout and painting).
    """

    name: str
    setup: Callable[[], object]
    run: Callable[[], object]


class Workbench:
    """
    The app, built once, with a profile that has a long history, and
    every operation that is timed on it.

    Attributes
    ----------
    app : QApplication
        The Qt application.
    directory : Path
        Where the database is, removed by `close`.
    db : Database
        The database, on disk, with `ATTEMPTS` answers in it.
    learner : Learner
        The learner for the profile that has them.
    window : MainWindow
        The main window, shown.
    exercises : list of type of Exercise
        Every exercise.
    operations : dict of str to Operation
        The operations, by name.
    """

    def __init__(
        self,
        *,
        show: bool = True,
    ) -> None:
        """
        Build the database, and the window and the list of operations.

        Parameters
        ----------
        show : bool, default True
            Whether to open the window now. A measurement of the
            start-up opens it itself. Keyword-only.
        """
        sounds.enabled = False
        self.app = QApplication.instance() or QApplication([])
        self.directory = Path(tempfile.mkdtemp(prefix="alto-perf-db-"))
        self.db = Database(self.directory / "perf.db")
        self.exercises: list[type[Exercise]] = list(REGISTRY)
        profile = self.db.add_profile("Perf")
        self.profile_id = profile.id
        self._fill(profile.id)
        self.learner = Learner(self.db, profile=profile)
        self.window: MainWindow
        self._circle: ExplorableCircle | None = None
        self._turn = 0
        if show:
            self.start()
            self.operations = {
                operation.name: operation for operation in self._build()
            }

    def start(self) -> None:
        """
        Open the main window, the way starting the app does, and let Qt
        finish drawing it.
        """
        self.window = MainWindow(self.learner)
        self.window.resize(1100, 820)
        self.window.show()
        self.settle()

    def settle(self) -> None:
        """
        Let Qt finish layout, painting and deferred widget deletion, as
        its event loop normally would.
        """
        self.app.processEvents()
        self.app.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    def _fill(
        self,
        profile_id: int,
    ) -> None:
        """
        Give a profile `ATTEMPTS` answers spread over a year, with what
        is known about the questions they were for.

        Parameters
        ----------
        profile_id : int
            The profile. Keyword-only.
        """
        rng = random.Random(7)
        names = [cls.name for cls in self.exercises]
        now = time.time()
        with self.db.conn:
            for number in range(ATTEMPTS):
                exercise = names[number % len(names)]
                key = f"item-{number % 400}"
                self.db.add_attempt(
                    profile_id,
                    exercise=exercise,
                    item_key=key,
                    attempt_no=1,
                    answer="x",
                    correct=rng.random() < 0.8,
                    duration_ms=rng.randint(600, 6000),
                    answered_at=now
                    - (ATTEMPTS - number) * DAY * 365 / ATTEMPTS,
                )
        for exercise in names:
            for number in range(400):
                self.db.save_item(
                    profile_id,
                    exercise=exercise,
                    item_key=f"item-{number}",
                    item=ItemRecord(
                        float(number % 7),
                        seen=3,
                        first_try_right=1,
                        wrong_attempts=2,
                        total_first_ms=9000,
                        last_seen=time.time(),
                        signature="perf",
                        payload="{}",
                    ),
                )

    def _view(self) -> ExercisePage:
        """
        Give the exercise screen that is open.

        Returns
        -------
        ExercisePage
            The current page, which must be an exercise.
        """
        view = self.window.stack.currentWidget()
        assert isinstance(view, ExercisePage)
        return view

    def _open(
        self,
        action: Callable[[], object],
    ) -> Callable[[], object]:
        """
        Wrap an action so that the events it causes are handled inside
        the timing.

        Parameters
        ----------
        action : Callable
            What to do.

        Returns
        -------
        Callable
            The action followed by the handling of events.
        """

        def run() -> None:
            """Do the action and let Qt catch up."""
            action()
            self.settle()

        return run

    def _home(self) -> None:
        """Go to the home page, with the settings closed."""
        # noinspection PyProtectedMember
        settings = self.window._settings
        if settings is not None:
            settings.close()
        self.window.show_home()
        self.settle()

    def _build(self) -> list[Operation]:
        """
        Make the list of operations.

        Returns
        -------
        list of Operation
            Pages, questions, painting and data.
        """
        window, db, profile = self.window, self.db, self.profile_id
        operations: list[Operation] = []

        def add(
            name: str,
            *,
            setup: Callable[[], object],
            run: Callable[[], object],
        ) -> None:
            """
            Add an operation.

            Parameters
            ----------
            name : str
                Its name.
            setup : Callable
                The untimed start. Keyword-only.
            run : Callable
                The timed operation. Keyword-only.
            """
            operations.append(Operation(name, setup=setup, run=run))

        add(
            "page:home",
            setup=lambda: window.open_exercise(self.exercises[0]),
            run=self._open(window.show_home),
        )
        for cls in self.exercises:
            add(
                f"page:{cls.__name__}",
                setup=self._home,
                run=self._open(partial(window.open_exercise, cls)),
            )
            add(
                f"paint:{cls.__name__}",
                setup=partial(window.open_exercise, cls),
                run=window.grab,
            )
            add(
                f"question:{cls.__name__}",
                setup=partial(window.open_exercise, cls),
                run=self._open(self._next_question),
            )
        add(
            "page:lesson",
            setup=self._home,
            run=self._open(lambda: window.open_lessons("circle-of-fifths")),
        )
        add(
            "page:lesson-step",
            setup=lambda: window.open_lessons("circle-of-fifths"),
            run=self._open(self._next_step),
        )
        add(
            "page:lesson-to-exercise",
            setup=lambda: window.open_lessons("circle-of-fifths"),
            run=self._open(lambda: window.open_exercise(self.exercises[0])),
        )
        add(
            "page:exercise-to-lesson",
            setup=lambda: window.open_exercise(self.exercises[0]),
            run=self._open(lambda: window.open_lessons("circle-of-fifths")),
        )
        add("resize:circle", setup=lambda: None, run=self._resize_circle)
        add(
            "page:statistics",
            setup=self._home,
            run=self._open(window.open_stats),
        )
        add(
            "page:settings",
            setup=self._home,
            run=self._open(window.open_settings),
        )
        add(
            "answer:right",
            setup=self._first_buttons_exercise,
            run=self._open(self._answer_right),
        )
        add(
            "answer:wrong",
            setup=self._first_buttons_exercise,
            run=self._open(self._answer_wrong),
        )
        add(
            "data:count",
            setup=lambda: None,
            run=lambda: db.count_attempts(profile),
        )
        add(
            "data:attempt-rows",
            setup=lambda: None,
            run=lambda: db.attempt_rows(profile),
        )
        add(
            "data:item-rows",
            setup=lambda: None,
            run=lambda: db.item_rows(profile),
        )
        add(
            "data:attempts-in",
            setup=lambda: None,
            run=lambda: db.attempts_in(
                [profile],
                since=time.time() - 30 * DAY,
            ),
        )
        add(
            "data:strained",
            setup=lambda: None,
            run=lambda: db.strained_items([profile], limit=10),
        )
        add("data:snapshot", setup=lambda: None, run=db.snapshot)
        add("learner:pick", setup=lambda: None, run=self._pick)
        add("learner:record", setup=lambda: None, run=self._record)
        return operations

    def _resize_circle(self) -> None:
        """
        Draw the circle of fifths, with every name on it, at ten sizes
        it has not been drawn at, as when its window is stretched.

        Text of a size that has not been used before has to be set up by
        Qt, which is slow if it is done for the wrong things, so
        what matters is how long it takes the first time. Each run uses
        new sizes, until they begin to repeat.
        """
        circle = self._circle
        if circle is None:
            circle = self._circle = ExplorableCircle()
            circle.show()
            self.settle()
        for step in range(10):
            side = 140 + ((self._turn * 10 + step) * 9) % 400
            circle.resize(side, side)
            circle.grab()
        self._turn += 1

    def _next_step(self) -> None:
        """Go to the next step of the lesson that is open."""
        page = self.window.stack.currentWidget()
        assert isinstance(page, LessonsPage)
        page.view.next_button.click()

    def _next_question(self) -> None:
        """Ask the next question of the exercise that is open."""
        self._view().next_question()

    def _first_buttons_exercise(self) -> None:
        """
        Open an exercise that is answered with buttons, ready to be
        answered.
        """
        for cls in self.exercises:
            self.window.open_exercise(cls)
            view = self._view()
            if view.control_area.answers.buttons:
                return

    def _answer_right(self) -> None:
        """Answer the open question correctly."""
        view = self._view()
        question = view.question
        assert question is not None
        button = next(
            b
            for b in view.control_area.answers.buttons
            if b.text() == question.answer
        )
        view.submit(question.answer, button=button)
        # noinspection PyProtectedMember
        view.controller._advance.stop()

    def _answer_wrong(self) -> None:
        """Answer the open question wrongly."""
        view = self._view()
        question = view.question
        assert question is not None
        button = next(
            b
            for b in view.control_area.answers.buttons
            if b.text() != question.answer
        )
        view.submit(button.text(), button=button)
        # noinspection PyProtectedMember
        view.controller._advance.stop()

    def _pick(self) -> None:
        """Ask the learner for a question."""
        self.learner.pick(self.exercises[0](), rng=random.Random(3))

    def _record(self) -> None:
        """Log one answer."""
        exercise = self.exercises[0]()
        question = self.learner.pick(exercise, rng=random.Random(3))
        self.learner.record(
            exercise,
            question=question,
            answer=question.answer,
            correct=True,
            attempt_no=1,
            seconds=1.5,
        )

    def close(self) -> None:
        """Close the window and the database, and remove the files."""
        if self._circle is not None:
            self._circle.close()
            self._circle.deleteLater()
        self.window.close()
        self.window.deleteLater()
        self.settle()
        self.db.close()
        shutil.rmtree(self.directory, ignore_errors=True)


def measure(
    operation: Operation,
    *,
    repeats: int = 5,
) -> float:
    """
    Time an operation, and give the middle of several runs, in seconds.

    Parameters
    ----------
    operation : Operation
        What to time.
    repeats : int, default 5
        How many times to run it. Keyword-only.

    Returns
    -------
    float
        The median time of one run.
    """
    times = []
    for _ in range(repeats):
        operation.setup()
        start = time.perf_counter()
        operation.run()
        times.append(time.perf_counter() - start)
    return statistics.median(times)


FIXED = (
    "resize:circle",
    "page:home",
    "page:lesson",
    "page:lesson-step",
    "page:lesson-to-exercise",
    "page:exercise-to-lesson",
    "page:statistics",
    "page:settings",
    "answer:right",
    "answer:wrong",
    "data:count",
    "data:attempt-rows",
    "data:item-rows",
    "data:attempts-in",
    "data:strained",
    "data:snapshot",
    "learner:pick",
    "learner:record",
)


def operation_names() -> list[str]:
    """
    Give the names of the operations without building the app, so a
    benchmark can list them before it runs.

    Returns
    -------
    list of str
        The same names as `Workbench.operations`.
    """
    per_exercise = [
        f"{kind}:{cls.__name__}"
        for cls in REGISTRY
        for kind in ("page", "paint", "question")
    ]
    return [*FIXED, *per_exercise]


COLD = (
    "startup",
    "resize:circle",
    "page:KeySignatures",
    "page:CircleOfFifths",
    "page:lesson",
    "page:statistics",
    "page:settings",
)


def measure_cold(name: str) -> float:
    """
    Time an operation the first time it is done in a new process, which
    is what a person meets after starting the app.

    Fonts, glyphs and layouts that are made on first use are not yet
    cached, so this is slower than `measure`, and is where a
    slow first look at a page shows up.

    Parameters
    ----------
    name : str
        "startup", or the name of one of the operations.

    Returns
    -------
    float
        The time in seconds.
    """
    bench = Workbench(show=name != "startup")
    if name == "startup":
        start = time.perf_counter()
        bench.start()
        seconds = time.perf_counter() - start
    else:
        operation = bench.operations[name]
        operation.setup()
        start = time.perf_counter()
        operation.run()
        seconds = time.perf_counter() - start
    bench.close()
    return seconds


def measure_cold_in_new_process(
    name: str,
    *,
    repeats: int = 3,
) -> float:
    """
    Run `measure_cold` in a new Python process each time, and give the
    middle of several runs, in seconds.

    Parameters
    ----------
    name : str
        "startup", or the name of one of the operations.
    repeats : int, default 3
        How many new processes to run. Keyword-only.

    Returns
    -------
    float
        The median time.
    """
    times = []
    for _ in range(repeats):
        done = subprocess.run(
            [sys.executable, "-m", "benchmarks.operations", name],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).resolve().parent.parent,
        )
        times.append(float(done.stdout.strip().splitlines()[-1]))
    return statistics.median(times)


def profile_cold(
    name: str,
    *,
    lines: int = 25,
) -> None:
    """
    Print where the time goes the first time an operation is done in a
    new process, leaving out the building of the app.

    Parameters
    ----------
    name : str
        The operation's name; not "startup", which is the building of
        the window itself.
    lines : int, default 25
        How many functions to show, the ones that took longest
        themselves. Keyword-only.
    """
    bench = Workbench()
    operation = bench.operations[name]
    operation.setup()
    profile = cProfile.Profile()
    profile.enable()
    operation.run()
    profile.disable()
    pstats.Stats(profile).sort_stats("tottime").print_stats(lines)
    bench.close()


if __name__ == "__main__":
    isolate()
    if "--profile" in sys.argv:
        profile_cold(sys.argv[1])
    else:
        print(measure_cold(sys.argv[1]))
