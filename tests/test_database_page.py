"""The database browser: three read-only tables, a search box, and a popup for the question a row is about."""

from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import (
    QModelIndex,
    Qt,
)
from PySide6.QtGui import (
    QKeySequence,
    QShortcut,
)
from PySide6.QtTest import QSignalSpy, QTest
from PySide6.QtWidgets import QToolButton

from alto.exercises import REGISTRY
from alto.exercises.base import Question
from alto.exercises.library import NoteNames
from alto.learning import Database, Learner
from alto.learning.database import ItemRecord
from alto.ui import database_page
from alto.ui.charts import LineChart
from alto.ui.database_page import (
    ROW_ROLE,
    DatabasePage,
    RowsModel,
)
from alto.ui.main_window import MainWindow
from alto.ui.question_preview import QuestionPreview
from alto.ui.stats_dialog import StatsPage

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtWidgets import (
        QApplication,
        QWidget,
    )


def test_the_table_model_shows_text_sorts_by_value_and_right_aligns_numbers(app: QApplication) -> None:
    """
    Check that the table model shows text sorts by value and right aligns numbers.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    model = RowsModel(
        ["Name", "Count"],
        rows=[[("b", "b"), ("10", 10)], [("a", "a"), ("2", 2)]],
        numeric={1},
        extras=[{"x": 1}, {"x": 2}],
    )
    first = model.index(0, 1)
    assert model.rowCount() == 2 and model.columnCount() == 2
    assert model.rowCount(first) == 0 and model.columnCount(first) == 0  # a table has no children
    assert model.data(first) == "10" and model.data(first, database_page.SORT_ROLE) == 10
    assert model.data(first, ROW_ROLE) == {"x": 1}
    right = int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    assert model.data(first, Qt.ItemDataRole.TextAlignmentRole) == right
    assert model.data(model.index(0, 0), Qt.ItemDataRole.TextAlignmentRole) is None
    assert model.data(first, Qt.ItemDataRole.ToolTipRole) is None
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Count"
    assert model.headerData(1, Qt.Orientation.Vertical) is None
    assert model.headerData(1, Qt.Orientation.Horizontal, Qt.ItemDataRole.ToolTipRole) is None
    assert RowsModel(["A"], rows=[[("x", 1)]]).extras == [{}]  # rows with nothing hidden get an empty note each


def test_the_answers_table_lists_every_answer_newest_first(
    app: QApplication,
    practiced_learner: Callable[..., Learner],
) -> None:
    """
    Check that the answers table lists every answer newest first.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    practiced_learner : Callable[..., Learner]
        Builds a learner with a history of answers.
    """
    learner = practiced_learner(30)
    page = DatabasePage(learner)
    total = learner.db.count_attempts(learner.profile.id)
    assert page.proxy.rowCount() == total and f"{total:,} answers by Ada." in page.note.text()
    assert page.proxy.index(0, 0).data() >= page.proxy.index(total - 1, 0).data()  # sorted by time, newest at the top
    assert page.model.headers == [
        "When",
        "Exercise",
        "Question",
        "Answer given",
        "Result",
        "Attempt",
        "Time",
        "Due",
    ]
    assert page.grab().width() > 0


def test_a_long_history_says_how_much_of_it_is_shown(
    app: QApplication,
    practiced_learner: Callable[..., Learner],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that a long history says how much of it is shown.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    practiced_learner : Callable[..., Learner]
        Builds a learner with a history of answers.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    monkeypatch.setattr(database_page, "ROW_LIMIT", 5)
    page = DatabasePage(practiced_learner(60))
    assert page.proxy.rowCount() == 5 and "Showing the newest 5." in page.note.text()


def test_the_questions_and_profiles_tables(
    app: QApplication,
    practiced_learner: Callable[..., Learner],
) -> None:
    """
    Test the questions and profiles tables.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    practiced_learner : Callable[..., Learner]
        Builds a learner with a history of answers.
    """
    learner = practiced_learner(30)
    Learner(learner.db, profile=learner.db.add_profile("Ben"))
    page = DatabasePage(learner)
    page.tabs["questions"].click()
    assert page.proxy.rowCount() > 0 and "questions asked of Ada" in page.note.text()
    strains = [page.proxy.index(r, 2).data(database_page.SORT_ROLE) for r in range(page.proxy.rowCount())]
    assert strains == sorted(strains, reverse=True)  # the hardest first
    page.tabs["profiles"].click()
    assert page.proxy.rowCount() == 2 and page.note.text().startswith("2 profiles.")
    assert [page.proxy.index(r, 0).data() for r in range(2)] == ["Ada", "Ben"]  # alphabetical
    only = DatabasePage(practiced_learner(3, name="Solo"))
    only.tabs["profiles"].click()
    assert only.note.text() == "1 profile."


@pytest.mark.parametrize("tab", ["answers", "questions"])
def test_browser_shows_due_for_the_selected_scheduler(app: QApplication, tab: str) -> None:
    """
    Sort actual due timestamps and refresh the open table when the scheduler changes.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    tab : str
        Browser table displaying the current due date.
    """
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    exercise = NoteNames()
    questions = [Question("Name the note", choices=["A", "B", "C"], answer=note) for note in "ABC"]
    for question, (mode, when) in zip(questions, (("ASRS", 300), ("SM-2", 200), ("SM-2", 100)), strict=True):
        learner.set_mode(mode)
        learner.record(exercise, question=question, answer=question.answer, correct=True, attempt_no=1, seconds=1, now=when)
    learner.set_mode("FSRS")
    learner.record(exercise, question=questions[2], answer="?", correct=False, attempt_no=1, seconds=1, now=500)
    learner.set_mode("SM-2")

    window = MainWindow(learner)
    window.open_database()
    page = window._overlay
    assert isinstance(page, DatabasePage)
    page.tabs[tab].click()
    column = page.model.headers.index("Due")
    page.view.sortByColumn(column, Qt.SortOrder.AscendingOrder)
    window.open_settings()
    dialog = window._settings
    assert dialog is not None
    dialog.categories.setCurrentRow(7)  # Practice
    # Two attempts at the third question share its current schedule.
    repetitions = 2 if tab == "answers" else 1
    for mode, due in (
        ("SM-2", [86500] * repetitions + [86600]),
        ("FSRS", [1100] * repetitions + [86600]),
        ("ARTS", []),
        ("ASRS", []),
    ):
        item = dialog.scheduler_list.findItems(mode, Qt.MatchFlag.MatchExactly)[0]
        dialog.scheduler_list.setCurrentItem(item)
        assert page.proxy.sortColumn() == column and page.proxy.rowCount() == 2 + repetitions
        cells = [page.proxy.index(row, column) for row in range(page.proxy.rowCount())]
        assert [cell.data(database_page.SORT_ROLE) for cell in cells if cell.data() != "—"] == due
        assert [cell.data() for cell in cells if cell.data() != "—"] == [
            datetime.fromtimestamp(stamp).strftime("%Y-%m-%d %H:%M:%S") for stamp in due
        ]
    dialog.close()
    window.close()


def test_searching_narrows_every_table_and_says_so(
    app: QApplication,
    practiced_learner: Callable[..., Learner],
) -> None:
    """
    Check that searching narrows every table and says so.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    practiced_learner : Callable[..., Learner]
        Builds a learner with a history of answers.
    """
    learner = practiced_learner(60)
    page = DatabasePage(learner)
    everything = page.proxy.rowCount()
    page.search.setText("Right")
    matching = page.proxy.rowCount()
    assert 0 < matching < everything and f"{matching:,} match the search." in page.note.text()
    page.search.setText("zzzz-nothing-matches")
    assert page.proxy.rowCount() == 0 and "0 match the search." in page.note.text()
    page.search.clear()
    assert page.proxy.rowCount() == everything and "match the search" not in page.note.text()


def test_questions_whose_record_is_gone_or_unreadable_are_labeled(
    app: QApplication,
    practiced_learner: Callable[..., Learner],
) -> None:
    """
    Check that questions whose record is gone or unreadable are labeled.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    practiced_learner : Callable[..., Learner]
        Builds a learner with a history of answers.
    """
    learner = practiced_learner(3)
    pid = learner.profile.id
    db = learner.db
    db.add_attempt(
        pid,
        exercise="NoteNames",
        item_key="ghost",
        attempt_no=1,
        answer="C",
        correct=True,
        duration_ms=1000,
        answered_at=99.0,
    )  # an answer to a question that is no longer stored
    db.save_item(
        pid,
        exercise="NoteNames",
        item_key="broken",
        item=ItemRecord(
            1.0,
            seen=1,
            first_try_right=1,
            wrong_attempts=0,
            total_first_ms=0,
            last_seen=1.0,
            signature="",
            payload="{not json",
            item_key="broken",
        ),
    )
    db.add_attempt(
        pid,
        exercise="NoteNames",
        item_key="broken",
        attempt_no=1,
        answer="C",
        correct=True,
        duration_ms=1000,
        answered_at=98.0,
    )
    page = DatabasePage(learner)
    texts = [page.proxy.index(r, 2).data() for r in range(page.proxy.rowCount())]
    assert "(no longer stored)" in texts and "(unreadable)" in texts
    assert page._question_text("NoteNames", key="broken", payload="{not json") == "(unreadable)"  # remembered, not parsed again


def test_double_clicking_a_row_shows_the_question_it_is_about(
    app: QApplication,
    practiced_learner: Callable[..., Learner],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that double clicking a row shows the question it is about.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    practiced_learner : Callable[..., Learner]
        Builds a learner with a history of answers.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    opened = []

    class Preview:
        """
        A stand-in for the question preview popup that records how it was opened.
        """

        # noinspection PyShadowingNames
        def __init__(
            self,
            name: str,
            *,
            question: object,
            details: object,
            statistics: object,
            parent: QWidget | None,
        ) -> None:
            """
            Record what the popup was asked to show.

            Parameters
            ----------
            name : str
                The exercise name.
            question : object
                The question to show.
            details : object
                The details of the answer.
            statistics : object
                The action for showing the question statistics.
            parent : QWidget or None
                The owning widget.
            """
            del parent, statistics  # accepted to match what it stands in for, but not needed
            opened.append((name, question, details))

        # noinspection PyMethodMayBeStatic
        def exec(self) -> None:
            """
            Record that the popup was shown.
            """
            opened.append("exec")

    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(database_page, "QuestionPreview", Preview)
    learner = practiced_learner(30)
    page = DatabasePage(learner)
    page._preview(page.proxy.index(0, 0))
    assert opened[-1] == "exec"
    name, question, details = opened[0]
    assert name in {cls.name for cls in REGISTRY} and isinstance(question, Question)
    assert details and details[0].startswith("<b>You answered:</b>")
    opened.clear()
    page.tabs["questions"].click()
    page._preview(page.proxy.index(0, 0))
    assert opened and "History" in opened[0][2][0]
    opened.clear()
    page.tabs["profiles"].click()
    page._preview(page.proxy.index(0, 0))  # profiles have no question
    page._preview(QModelIndex())
    assert opened == []
    oddball = ItemRecord(
        1,
        seen=1,
        first_try_right=1,
        wrong_attempts=0,
        total_first_ms=0,
        last_seen=1.0,
        signature="",
        payload=json.dumps({"bad": 1}),
        item_key="oddball",
    )
    learner.db.save_item(
        learner.profile.id,
        exercise="NoteNames",
        item_key="oddball",
        item=oddball,
    )
    learner.db.add_attempt(
        learner.profile.id,
        exercise="NoteNames",
        item_key="oddball",
        attempt_no=1,
        answer="x",
        correct=False,
        duration_ms=500,
        answered_at=200.0,
    )
    page.tabs["answers"].click()
    row = next(r for r in range(page.proxy.rowCount()) if page.proxy.index(r, 3).data() == "x")
    page._preview(page.proxy.index(row, 0))  # the stored question cannot be read: nothing opens
    assert opened == []


def test_back_is_offered_by_a_button_and_by_escape(
    app: QApplication,
    practiced_learner: Callable[..., Learner],
) -> None:
    """
    Check that back is offered by a button and by escape.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    practiced_learner : Callable[..., Learner]
        Builds a learner with a history of answers.
    """
    page = DatabasePage(practiced_learner(3))
    spy = QSignalSpy(page.back)
    escape = [s for s in page.findChildren(QShortcut) if s.key() == QKeySequence(Qt.Key.Key_Escape)]
    escape[0].activated.emit()
    assert spy.count() == 1


@pytest.mark.parametrize("source", ["answers", "questions", "statistics", "needs_practice"])
def test_question_statistics_from_a_stored_card(app: QApplication, monkeypatch: pytest.MonkeyPatch, source: str) -> None:
    """
    Open a saved question and its lifetime statistics from each table that lists it.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Captures modal dialogs so the test can interact with them.
    source : str
        The table from which to open the question.
    """
    db = Database()
    profile = db.add_profile("Ada")
    other = db.add_profile("Sam")
    question = Question("Name the note.", choices=["C", "D"], answer="C")
    db.save_item(
        profile.id,
        exercise="NoteNames",
        item_key="target",
        item=ItemRecord(
            2.0,
            seen=2,
            first_try_right=1,
            wrong_attempts=1,
            total_first_ms=6000,
            last_seen=20.0,
            signature="s",
            payload=json.dumps(question.to_dict()),
        ),
    )
    for pid, exercise, key, attempt, correct, duration in (
        (profile.id, "NoteNames", "target", 1, False, 2000),
        (profile.id, "NoteNames", "target", 2, True, 7000),
        (profile.id, "NoteNames", "target", 1, True, 4000),
        (profile.id, "NoteNames", "other", 1, True, 9000),
        (profile.id, "KeyboardNotes", "target", 1, True, 9000),
        (other.id, "NoteNames", "target", 1, True, 9000),
    ):
        db.add_attempt(
            pid,
            exercise=exercise,
            item_key=key,
            attempt_no=attempt,
            answer="C",
            correct=correct,
            duration_ms=duration,
            answered_at=40.0 if duration == 4000 else 20.0,
        )
    dialogs = []
    monkeypatch.setattr(database_page.QDialog, "exec", lambda dialog: dialogs.append(dialog))

    def open_statistics(card: QuestionPreview) -> None:
        """
        Open the graphs from the question card.

        Parameters
        ----------
        card : QuestionPreview
            The preview opened by the selected row.
        """
        assert card.windowTitle() == "Note Identification"
        assert card.question == question
        card.show()
        layout = card.layout()
        assert layout is not None
        layout.setGeometry(card.rect())
        button = next(b for b in card.findChildren(QToolButton) if b.accessibleName() == "Question Statistics")
        assert not button.icon().isNull() and button.toolTip() == "Question Statistics"
        assert button.geometry().topRight() == card.rect().marginsRemoved(layout.contentsMargins()).topRight()
        button.click()

    monkeypatch.setattr(QuestionPreview, "exec", open_statistics)
    learner = Learner(db, profile=profile)
    if source == "needs_practice":
        page = StatsPage(learner)
        page.timeframe.setCurrentIndex(page.timeframe.findText("All time"))
        page.resize(1000, 800)
        page.show()
        page.scroller.ensureWidgetVisible(page.table)
        app.processEvents()
        assert page.table.rowCount() == 1
        table, model = page.table, page.table.model()
    elif source == "statistics":
        page = StatsPage(learner)
        page._open_detail("A day", exercise="NoteNames", since=0.0, until=30.0)
        table, model = page.answers, page.answers.proxy
    else:
        page = DatabasePage(learner)
        page.show_table(source)
        table, model = page.view, page.proxy
    indices = (model.index(row, 0) for row in range(model.rowCount()))
    index = next(i for i in indices if i.data(ROW_ROLE)["exercise"] == "NoteNames" and i.data(ROW_ROLE)["item_key"] == "target")
    if source == "needs_practice":
        position = table.visualRect(index.siblingAtColumn(2)).center()
        QTest.mouseClick(table.viewport(), Qt.MouseButton.LeftButton, pos=position)
        assert not dialogs
        QTest.mouseDClick(table.viewport(), Qt.MouseButton.LeftButton, pos=position)
    else:
        table.doubleClicked.emit(index)
    [dialog] = dialogs
    assert isinstance(dialog.parentWidget(), QuestionPreview)
    assert dialog.windowTitle() == "Question Statistics"
    speed, accuracy = dialog.findChildren(LineChart)
    assert speed.labels == accuracy.labels == ["#1", "#2"]
    assert speed.values == [2.0, 4.0]
    assert accuracy.values == [0.0, 50.0]
