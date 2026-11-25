"""
Exercise filters, media, scheduling, and repeat imports in Alto's
portable Anki decks.
"""

from __future__ import annotations

import json
import multiprocessing
import random
import re
import sqlite3
import time
from concurrent.futures import CancelledError
from contextlib import closing
from itertools import islice, pairwise
from pathlib import Path
from unittest.mock import Mock
from zipfile import ZipFile

import pytest
from PySide6.QtCore import QCoreApplication, Qt, QTimer, QUrl
from PySide6.QtGui import QImage, QTextDocument
from PySide6.QtTest import QSignalSpy, QTest
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QWidget,
)

from alto import settings
from alto.anki_export import (
    DeckSelection,
    ExportControl,
    Review,
    _schedule,
    export_deck,
    plan_deck,
    profile_reviews,
    write_decks,
)
from alto.exercises import REGISTRY
from alto.exercises.library import (
    ChordQualities,
    CircleOfFifths,
    ClefBasics,
    IntervalConstruction,
    IntervalNames,
    KeyboardIntervals,
    KeyboardNotes,
    NotationIdentification,
    NoteConstruction,
    NoteNames,
)
from alto.learning import Database, Learner
from alto.ui import anki_exporter as exporter
from alto.ui.anki_exporter import AnkiExporter, card_fields
from alto.ui.main_window import MainWindow
from alto.ui.settings_panel import NotationSettingsPanel
from alto.ui.store import export_settings, store
from alto.ui.theme import PARTS, STUDIO, apply_theme, saved_theme


def wait_for_export(window: exporter._ExportDialog) -> None:
    """
    Process Qt's queued card rendering and progress signals until the
    export finishes.

    Parameters
    ----------
    window : _ExportDialog
        Dialog that owns the export job.
    """
    deadline = time.monotonic() + 10
    while (
        window._job is not None or window._counter is not None
    ) and time.monotonic() < deadline:
        QApplication.processEvents()
        time.sleep(0.001)
    assert window._job is None and window._counter is None, (
        "The exporter did not finish."
    )


def test_export_worker_progress_and_errors(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify worker results and progress signals directly, including
    failures before and during a write.

    Parameters
    ----------
    app : QApplication
        GUI thread for rendering the sample card.
    tmp_path : Path
        Destination for the finished package.
    monkeypatch : pytest.MonkeyPatch
        Simulate a failed render and a failed card count.
    """
    parent = QWidget()
    exercise = ClefBasics()
    sample = exercise.generate(random.Random(1))
    monkeypatch.setattr(
        exercise,
        "daily_candidates",
        lambda rng: iter([sample]),
    )
    planner = exporter._PlanJob([DeckSelection(exercise, [])], parent=parent)
    planner.run()
    assert not planner.error and len(planner.plans[0].cards) == 1

    path = tmp_path / "clefs.apkg"
    job = exporter._ExportJob(path, plans=planner.plans, parent=parent)
    # run() is called on the GUI thread here, so deliver its render
    # request before it waits for the result.
    job.render_requested.disconnect(job._paint_card)
    job.render_requested.connect(
        job._paint_card,
        Qt.ConnectionType.DirectConnection,
    )
    decks = QSignalSpy(job.deck_progress)
    progress = QSignalSpy(job.progress)
    job.run()
    assert job.count == 1 and not job.error
    assert [decks.at(i) for i in range(decks.count())] == [
        [0, False],
        [0, True],
    ]
    stages = [progress.at(i) for i in range(progress.count())]
    total = stages[-1][2]
    assert any(
        message.startswith("Packing images") for message, _, _ in stages
    )
    assert stages[-1] == [f"Saved {path.name}.", total, total]
    assert all(
        completed <= following <= total
        for (_, completed, _), (_, following, _) in pairwise(stages)
    )

    saved = path.read_bytes()
    monkeypatch.setattr(
        exporter,
        "card_fields",
        Mock(side_effect=OSError("render failed")),
    )
    job.run()
    assert (
        job.error == "Export failed. render failed"
        and path.read_bytes() == saved
    )
    monkeypatch.setattr(
        exercise,
        "daily_candidates",
        Mock(side_effect=ValueError("invalid settings")),
    )
    planner.run()
    assert planner.error == "Could not count cards. invalid settings"


def test_all_exercise_types_package_their_music(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check each exercise's front and back fields and resolve every
    referenced image in its package.

    Parameters
    ----------
    app : QApplication
        Qt application used by the music renderers.
    tmp_path : Path
        Destination directory for deck files.
    monkeypatch : pytest.MonkeyPatch
        Supply two representative questions for each media-rendering
        check.
    """
    settings.note_names.require_octave = True
    instructions = {
        NoteNames: "Identify the note. Include the octave.",
        KeyboardNotes: "Identify the note by letter.",
        IntervalNames: "Identify the interval and quality.",
        KeyboardIntervals: "Identify the interval.",
        ChordQualities: "Identify the Chord Quality.",
    }
    for cls in REGISTRY:
        exercise = cls()
        sample = list(
            islice(exercise.daily_candidates(random.Random(cls.__name__)), 2),
        )
        monkeypatch.setattr(
            exercise,
            "daily_candidates",
            Mock(return_value=iter(sample)),
        )
        path = tmp_path / f"{cls.__name__}.apkg"
        count = export_deck(
            path,
            exercise=exercise,
            reviews=[],
            render=lambda q, folder, ex=exercise: card_fields(
                q,
                folder=folder,
                exercise=ex,
            ),
        )
        assert count == 2, exercise.name
        with (
            ZipFile(path) as archive,
            closing(sqlite3.connect(":memory:")) as db,
        ):
            db.deserialize(archive.read("collection.anki2"))
            assert db.execute(
                "SELECT COUNT(*) FROM cards WHERE type=0 AND queue=0",
            ).fetchone() == (count,)
            decks = json.loads(
                db.execute("SELECT decks FROM col").fetchone()[0],
            )
            (deck_id,) = db.execute(
                "SELECT DISTINCT did FROM cards",
            ).fetchone()
            assert decks[str(deck_id)]["name"] == f"Alto::{exercise.name}"
            manifest = json.loads(archive.read("media"))
            referenced = set()
            for (fields,) in db.execute("SELECT flds FROM notes"):
                prompt, front, answer, _ = fields.split("\x1f")
                assert prompt and "<img" in front and answer
                assert prompt != exercise.name
                if cls in instructions:
                    assert prompt == instructions[cls]
                if cls is NoteConstruction:
                    assert prompt.startswith("Place ") and prompt.endswith(
                        " on the staff.",
                    )
                referenced.update(re.findall(r'<img src="([^"]+)"', fields))
            assert referenced == set(manifest.values())
            assert all(
                archive.read(entry).startswith(b"\x89PNG")
                for entry in manifest
            )


def test_card_instructions_follow_the_expected_answer_format() -> None:
    """
    Cover alternate naming systems, interval questions, and compact
    construction targets.
    """
    rng = random.Random(4)
    intervals = IntervalNames()
    for mode, target in (
        ("interval", "numeric interval"),
        ("quality", "quality"),
        ("combined", "interval and quality"),
    ):
        settings.intervals.quality_mode = mode
        assert (
            intervals.card_prompt(intervals.generate(rng))
            == f"Identify the {target}."
        )
        settings.intervals.inversions = True
        inversion = intervals.generate(rng)
        settings.intervals.inversions = False
        assert intervals.card_prompt(inversion) == inversion.prompt

    keyboard = KeyboardNotes()
    settings.keyboard.require_octave = True
    assert (
        keyboard.card_prompt(keyboard.generate(rng))
        == "Identify the note by letter and octave."
    )
    settings.keyboard.key_signature = True
    settings.keyboard.keys = {1}
    assert keyboard.card_prompt(keyboard.generate(rng)) == (
        "Identify the note by letter and octave. Use the spelling for "
        "the displayed key signature."
    )
    for naming, instruction in (
        ("degrees", "Give its scale degree in G major."),
        ("functions", "Give its scale-degree function in G major."),
    ):
        settings.keyboard.naming = naming
        assert (
            keyboard.card_prompt(keyboard.generate(rng))
            == f"Identify the note. {instruction} Include the octave."
        )
    settings.note_names.naming = "solfege"
    assert (
        NoteNames()
        .card_prompt(NoteNames().generate(rng))
        .startswith("Identify the note. Use solfège.")
    )

    circle = CircleOfFifths()
    for kind in ("major", "minor"):
        settings.circle.questions = {kind}
        question = next(q for q in circle.daily_candidates(rng) if q.required)
        prompt = circle.card_prompt(question)
        assert (
            prompt
            == question.prompt.split("?")[0]
            + "? Name both enharmonic spellings."
        )
    single = next(q for q in circle.daily_candidates(rng) if not q.required)
    assert circle.card_prompt(single) == single.prompt

    settings.notation.question_type = "staff"
    notation = NotationIdentification()
    assert notation.card_prompt(notation.generate(rng)).startswith("Locate ")

    construction = NoteConstruction()
    settings.note_names.naming = "degrees"
    for kind in ("notes", "scale"):
        settings.construction.question_type = kind
        question = construction.generate(rng)
        assert (
            construction.card_prompt(question)
            == f"Place {question.prompt} on the staff."
        )


@pytest.mark.parametrize("mode", ["SM-2", "FSRS"])
def test_review_export_uses_the_active_profile_and_preserves_identity(
    app: QApplication,
    tmp_path: Path,
    mode: str,
) -> None:
    """
    Compare a new deck with one that transfers a reviewed note from the
    active profile.

    Parameters
    ----------
    app : QApplication
        Qt application for staff rendering.
    tmp_path : Path
        Location of the generated deck.
    mode : str
        Calendar scheduler to exercise.
    """
    with closing(Database()) as db:
        learner = Learner(db, profile=db.add_profile("Ada"))
        assert not profile_reviews(learner)
        learner.set_mode(mode)
        ex = NoteNames()
        now = time.time()
        question = learner.calendar.take(
            ex,
            profile=learner.profile.id,
            mode=mode,
            now=now,
        )
        assert question is not None
        learner.calendar.grade(
            "NoteNames",
            profile=learner.profile.id,
            key=question.item_key(),
            mode=mode,
            correct=True,
            now=now,
        )
        reviews = profile_reviews(learner)["NoteNames"]
        other = Learner(db, profile=db.add_profile("Other"))
        other.set_mode(mode)
        assert profile_reviews(other) == {}
        path = tmp_path / "notes.apkg"
        identities = []
        for records in ([], reviews):
            count = export_deck(
                path,
                exercise=ex,
                reviews=records,
                render=lambda q, folder: card_fields(
                    q,
                    folder=folder,
                    exercise=ex,
                ),
            )
            with (
                ZipFile(path) as archive,
                closing(sqlite3.connect(":memory:")) as cards,
            ):
                cards.deserialize(archive.read("collection.anki2"))
                identities.append(set(cards.execute("SELECT guid FROM notes")))
                assert count == ex.card_count()
                scheduled = cards.execute(
                    (
                        "SELECT type,queue,due,ivl,factor,data FROM cards "
                        "WHERE type!=0"
                    ),
                ).fetchall()
                if not records:
                    assert not scheduled
                elif mode == "SM-2":
                    assert (
                        len(scheduled) == 1
                        and scheduled[0][:2] == (2, 2)
                        and scheduled[0][3:5] == (1, 2500)
                    )
                else:
                    assert len(scheduled) == 1 and scheduled[0][:3] == (
                        1,
                        1,
                        int(reviews[0].due),
                    )
                    assert json.loads(scheduled[0][-1])["s"] > 0
        assert identities[0] == identities[1]
        assert (
            db.conn.execute(
                "SELECT COUNT(*) FROM review_schedules",
            ).fetchone()[0]
            == 1
        )


def test_checked_decks_share_a_package_and_preview_the_exported_fields(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check deck placement across two categories and compare the preview
    with the exported cards.

    Parameters
    ----------
    app : QApplication
        Qt event loop for the modeless dialog.
    tmp_path : Path
        Destination for the Anki package.
    monkeypatch : pytest.MonkeyPatch
        Choose a package path through the file picker.
    """
    settings.intervals.clefs = {"treble"}
    settings.intervals.ranges = {"treble": (28, 29)}
    settings.intervals.intervals = {"M2"}
    settings.intervals.accidentals = {0}
    settings.keyboard_intervals.low = 21
    settings.keyboard_intervals.high = 81
    settings.keyboard_intervals.intervals = {1}
    keyboard_count = len(
        list(
            KeyboardIntervals().daily_candidates(
                random.Random("KeyboardIntervals"),
            ),
        ),
    )
    assert keyboard_count > 50
    window = AnkiExporter(None, reviews={}, selected="IntervalNames")
    window.show()
    window.nav_toggle.click()
    assert window.tree.isHidden()
    window.nav_toggle.click()
    group = window.items[IntervalNames].parent()
    root = window.tree.topLevelItem(0)
    assert (
        group is not None
        and group.checkState(0) == Qt.CheckState.PartiallyChecked
    )
    window.tree.setCurrentItem(group)
    group.setExpanded(False)
    assert window.exercise.name == IntervalNames.name
    group.setExpanded(True)
    root.setCheckState(0, Qt.CheckState.Checked)
    assert all(
        item.checkState(0) == Qt.CheckState.Checked
        for item in window.items.values()
    )
    root.setCheckState(0, Qt.CheckState.Unchecked)
    assert not window.save.isEnabled()
    group.setCheckState(0, Qt.CheckState.Checked)
    window.items[IntervalConstruction].setCheckState(
        0,
        Qt.CheckState.Unchecked,
    )
    settings.notation.terms.clear()
    window.items[NotationIdentification].setCheckState(
        0,
        Qt.CheckState.Checked,
    )
    window.items[ClefBasics].setCheckState(0, Qt.CheckState.Checked)
    assert window.status.text() == "4 decks selected"
    window.gear.click()
    window.tree.setCurrentItem(window.items[KeyboardIntervals])
    front = window.preview.toPlainText()
    window.side.buttons[1].click()
    assert window.preview.toPlainText() != front
    assert front.strip() in window.preview.toPlainText()
    fields = window.fields.copy()
    image = re.search(r'<img src="([^"]+)"', fields[1])
    assert image
    resource = window.preview.document().resource(
        QTextDocument.ResourceType.ImageResource,
        QUrl(image[1]),
    )
    assert isinstance(resource, QImage) and not resource.isNull()
    window.resize(820, 540)
    app.processEvents()
    assert window.preview.horizontalScrollBar().maximum() == 0
    path = tmp_path / "both.apkg"
    window.save.click()
    dialog = window.export_dialog
    assert dialog is not None and dialog.isVisible() and dialog.isModal()
    wait_for_export(dialog)
    assert dialog.total.text() == f"Total: {keyboard_count + 3} cards"
    assert dialog.summary.topLevelItemCount() == 2
    notation, intervals = (dialog.summary.topLevelItem(i) for i in range(2))
    assert notation.text(0) == "Notation" and notation.isExpanded()
    assert [
        notation.child(i).text(0) for i in range(notation.childCount())
    ] == [ClefBasics.name, NotationIdentification.name]
    assert intervals.text(0) == "Intervals" and intervals.isExpanded()
    assert [
        intervals.child(i).text(0) for i in range(intervals.childCount())
    ] == [IntervalNames.name, KeyboardIntervals.name]
    assert [row.text(1) for row in dialog.rows] == [
        "2",
        "0",
        "1",
        str(keyboard_count),
    ]
    assert [row.text(2) for row in dialog.rows] == [
        "Pending",
        "No cards",
        "Pending",
        "Pending",
    ]
    assert dialog.findChildren(QProgressBar) == [dialog.progress]
    assert not path.exists() and dialog.progress.isHidden()
    assert dialog.filename.text() == str(Path.home() / "alto.apkg")
    monkeypatch.setattr(
        QFileDialog,
        "exec",
        lambda self: QFileDialog.DialogCode.Accepted,
    )
    monkeypatch.setattr(
        QFileDialog,
        "selectedFiles",
        lambda self: [str(path.with_suffix(""))],
    )
    dialog.browse.click()
    assert dialog.filename.text() == str(path.with_suffix(""))
    messages = []
    values = []
    maxima = []
    states = []
    dialog.progress.valueChanged.connect(values.append)
    dialog.progress.valueChanged.connect(
        lambda _: messages.append(dialog.status.text()),
    )
    dialog.progress.valueChanged.connect(
        lambda _: maxima.append(dialog.progress.maximum()),
    )
    dialog.progress.valueChanged.connect(
        lambda _: states.append(tuple(row.text(2) for row in dialog.rows)),
    )
    dialog.save.click()
    assert dialog.progress.isVisible() and not dialog.destination.isEnabled()
    wait_for_export(dialog)
    assert (
        values == sorted(values)
        and values[0] == 0
        and values[-1] == dialog.progress.maximum() > 0
    )
    assert set(maxima) == {dialog.progress.maximum()}
    assert ("In progress", "No cards", "Pending", "Pending") in states
    assert ("Complete", "No cards", "In progress", "Pending") in states
    assert ("Complete", "No cards", "Complete", "In progress") in states
    assert states[-1] == ("Complete", "No cards", "Complete", "Complete")
    assert [row.icon(2).isNull() for row in dialog.rows] == [
        False,
        True,
        False,
        False,
    ]
    assert all(
        any(stage in message for message in messages)
        for stage in (
            "Deck 1 of 3",
            "Deck 2 of 3",
            "Deck 3 of 3",
            "Packing images",
        )
    )
    assert dialog.status.text() == (
        f"Export successful. Saved {keyboard_count + 3} cards to {path.name}."
    )
    assert [
        button.text()
        for button in dialog.findChildren(QPushButton)
        if button.isVisible()
    ] == ["Close"]
    assert window.status.text() == "4 decks selected"
    QTest.keyClick(dialog, Qt.Key.Key_Return)
    assert window.export_dialog is None and window.isVisible()
    with ZipFile(path) as archive, closing(sqlite3.connect(":memory:")) as db:
        db.deserialize(archive.read("collection.anki2"))
        decks = json.loads(db.execute("SELECT decks FROM col").fetchone()[0])
        counts = {
            decks[str(did)]["name"]: n
            for did, n in db.execute(
                "SELECT did, COUNT(*) FROM cards GROUP BY did",
            )
        }
        assert counts == {
            "Alto::Notation::Clef Basics": 2,
            "Alto::Intervals::Interval Identification": 1,
            ("Alto::Intervals::Keyboard Interval Identification"): (
                keyboard_count
            ),
        }
        assert db.execute(
            "SELECT COUNT(*) FROM notes WHERE flds=?",
            ("\x1f".join(fields),),
        ).fetchone() == (1,)
        assert image[1] in json.loads(archive.read("media")).values()
    window.close()


def test_deck_status_animations(app: QApplication) -> None:
    """
    Verify that each check draws in independently while the next deck
    can start.

    Parameters
    ----------
    app : QApplication
        Drives the status animation timer.
    """
    window = AnkiExporter(None, reviews={}, selected="KeyboardNotes")
    window.items[ClefBasics].setCheckState(0, Qt.CheckState.Checked)
    window.save.click()
    dialog = window.export_dialog
    assert dialog is not None
    wait_for_export(dialog)
    first, second = dialog.rows
    dialog._deck_progress(0, False)
    frame = first.icon(2).pixmap(16).toImage()
    assert not frame.isNull() and second.icon(2).isNull()
    assert QSignalSpy(dialog._spinner.timeout).wait(1000)
    assert (
        first.icon(2).pixmap(16).toImage() != frame and second.icon(2).isNull()
    )
    dialog._deck_progress(0, True)
    assert not dialog._spinner.isActive() and first.text(2) == "Complete"
    first_animation, second_animation = dialog._check_animations
    start = first.icon(2).pixmap(16).toImage()
    dialog._deck_progress(1, False)
    assert dialog._spinner.isActive() and second.text(2) == "In progress"
    assert first_animation.state() == first_animation.State.Running
    first_animation.setCurrentTime(first_animation.duration() // 2)
    middle = first.icon(2).pixmap(16).toImage()
    assert middle != start
    first_finished = QSignalSpy(first_animation.finished)
    dialog._deck_progress(1, True)
    assert QSignalSpy(second_animation.finished).wait(1000)
    assert first_finished.count() or first_finished.wait(1000)
    final = first.icon(2).pixmap(16).toImage()
    assert final != middle and second.icon(2).pixmap(16).toImage() == final
    assert first.icon(2).cacheKey() == dialog._check_frames[-1].cacheKey()
    window.close()


def test_exporter_uses_the_selected_panel_and_handles_empty_filters(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Select one notation term through its actual exercise panel and
    export it from the dialog.

    Parameters
    ----------
    app : QApplication
        Qt application for the modeless window.
    tmp_path : Path
        Destination for the exported package.
    monkeypatch : pytest.MonkeyPatch
        Control overwrite confirmation and simulate a failed card
        render.
    """
    window = AnkiExporter(None, reviews={}, selected="NotationIdentification")
    window.show()
    assert not window.isModal() and not window.scheduling.isEnabled()
    window.gear.click()
    assert window.pane.isVisible()
    panel = window.panel
    assert isinstance(panel, NotationSettingsPanel)
    panel.select_none.switched.emit(True)
    assert not window.save.isEnabled()
    panel.terms.boxes["Vertical turn"].click()
    assert window.save.isEnabled() and settings.notation.terms == {
        "Vertical turn",
    }
    path = tmp_path / "terms.apkg"
    window.save.click()
    dialog = window.export_dialog
    assert dialog is not None
    wait_for_export(dialog)
    assert (
        dialog.total.text() == "Total: 1 card"
        and dialog.summary.topLevelItem(0).child(0).text(1) == "1"
    )
    assert dialog.filename.text() == str(
        Path.home() / "alto - Notation Identification.apkg",
    )
    dialog.filename.setText(str(tmp_path / "missing" / path.name))
    dialog.save.click()
    assert "existing directory" in dialog.status.text()
    dialog.filename.clear()
    dialog.save.click()
    assert "Enter a file name" in dialog.status.text()
    (tmp_path / "folder.apkg").mkdir()
    dialog.filename.setText(str(tmp_path / "folder.apkg"))
    dialog.save.click()
    assert "directory already" in dialog.status.text()
    dialog.filename.setText(str(path))
    dialog.save.click()
    wait_for_export(dialog)
    assert (
        dialog.status.text()
        == f"Export successful. Saved 1 card to {path.name}."
    )
    dialog.dismiss.click()
    with (
        ZipFile(path) as archive,
        closing(sqlite3.connect(":memory:")) as cards,
    ):
        cards.deserialize(archive.read("collection.anki2"))
        assert (
            "Vertical turn"
            in cards.execute("SELECT flds FROM notes").fetchone()[0]
        )
    previous = path.read_bytes()
    window.save.click()
    dialog = window.export_dialog
    assert dialog is not None
    wait_for_export(dialog)
    dialog.filename.setText(str(path))
    warnings = []

    def decline_replacement() -> None:
        """
        Measure the visible warning before declining the overwrite.
        """
        warning = app.activeModalWidget()
        assert isinstance(warning, QMessageBox)
        warnings.append(
            (warning.windowTitle(), warning.width(), warning.text()),
        )
        warning.button(QMessageBox.StandardButton.No).click()

    QTimer.singleShot(0, decline_replacement)
    dialog.save.click()
    title, width, prompt = warnings.pop()
    assert title == "Replace file?" and width >= 360 and path.name in prompt
    assert dialog._job is None and path.read_bytes() == previous

    def approve_replacement() -> None:
        """Approve the overwrite in the displayed warning."""
        warning = app.activeModalWidget()
        assert isinstance(warning, QMessageBox)
        warning.button(QMessageBox.StandardButton.Yes).click()

    with monkeypatch.context() as failure:
        failure.setattr(
            exporter,
            "card_fields",
            Mock(side_effect=OSError("disk full")),
        )
        QTimer.singleShot(0, approve_replacement)
        dialog.save.click()
        wait_for_export(dialog)
    assert (
        dialog.progress.isHidden()
        and dialog.destination.isEnabled()
        and dialog.save.isEnabled()
    )
    assert (
        dialog.rows[0].text(2) == "Failed" and dialog.rows[0].icon(2).isNull()
    )
    assert not dialog._spinner.isActive()
    assert (
        "disk full" in dialog.status.text() and path.read_bytes() == previous
    )
    QTimer.singleShot(0, approve_replacement)
    dialog.save.click()
    assert dialog.rows[0].text(2) == "Pending"
    window.close()
    assert window.isVisible()
    wait_for_export(dialog)
    assert not window.isVisible()


@pytest.mark.parametrize("cancel", [True, False])
def test_cancel_during_export(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    cancel: bool,
) -> None:
    """
    Answer the cancellation warning after the first card and verify the
    destination.

    Parameters
    ----------
    app : QApplication
        Runs the real export and confirmation dialogs.
    tmp_path : Path
        Directory containing a previously saved package.
    monkeypatch : pytest.MonkeyPatch
        Accept replacement of the previous file when starting the
        export.
    cancel : bool
        Whether to discard the new package or finish writing it.
    """
    window = AnkiExporter(None, reviews={}, selected="KeyboardNotes")
    window.show()
    window.save.click()
    dialog = window.export_dialog
    assert dialog is not None
    wait_for_export(dialog)
    path = tmp_path / "notes.apkg"
    path.write_bytes(b"previous package")
    dialog.filename.setText(str(path))
    monkeypatch.setattr(dialog, "_confirm_replace", lambda path: True)
    prompted = []

    def answer_warning() -> None:
        """
        Inspect and answer the cancellation warning in its modal event
        loop.
        """
        warning = app.activeModalWidget()
        assert isinstance(warning, QMessageBox)
        assert (
            warning.windowTitle() == "Cancel export?"
            and warning.icon() == QMessageBox.Icon.Warning
        )
        assert warning.defaultButton() == warning.button(
            QMessageBox.StandardButton.No,
        )
        prompted.append(True)
        warning.button(
            QMessageBox.StandardButton.Yes
            if cancel
            else QMessageBox.StandardButton.No,
        ).click()

    def on_progress(value: int) -> None:
        """
        Click Cancel while the first card's progress is visible.

        Parameters
        ----------
        value : int
            Number of cards or images written in the current stage.
        """
        if value == 1 and "Cards prepared" in dialog.status.text():
            dialog.progress.valueChanged.disconnect(on_progress)
            assert (
                dialog.dismiss.isEnabled()
                and dialog.dismiss.text() == "Cancel"
            )
            QTimer.singleShot(0, answer_warning)
            dialog.dismiss.click()

    dialog.progress.valueChanged.connect(on_progress)
    dialog.save.click()
    wait_for_export(dialog)
    assert prompted == [True]
    if cancel:
        assert window.export_dialog is None and window.isVisible()
        assert path.read_bytes() == b"previous package"
    else:
        assert dialog.status.text().startswith("Export successful.")
        with ZipFile(path) as archive:
            assert "collection.anki2" in archive.namelist()
    assert list(tmp_path.iterdir()) == [path]
    window.close()


def test_cancel_before_package_replacement(tmp_path: Path) -> None:
    """
    Accept a cancellation at the final saving stage and verify that no
    partial file remains.

    Parameters
    ----------
    tmp_path : Path
        Destination and temporary working directory for the package
        writer.
    """
    path = tmp_path / "new.apkg"
    control = ExportControl()
    plans = [plan_deck(DeckSelection(KeyboardNotes(), []))]

    def progress(message: str, completed: int, total: int) -> None:  # noqa: PLR0917 (progress callback)
        """
        Confirm cancellation as soon as the package is ready to save.

        Parameters
        ----------
        message : str
            Current writer stage.
        completed : int
            Units completed.
        total : int
            Total units in the stage.
        """
        if message.startswith("Saving"):
            assert control.confirm_cancel(lambda: True)

    with pytest.raises(CancelledError):
        write_decks(
            path,
            plans=plans,
            render=lambda *args: ["Question", "", "Answer", ""],
            progress=progress,
            control=control,
        )
    assert list(tmp_path.iterdir()) == []


def test_export_summary_handles_empty_counts_and_cancel(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Keep the exporter available after an empty sample, a count failure,
    or cancellation.

    Parameters
    ----------
    app : QApplication
        Runs the exporter and its destination dialog.
    monkeypatch : pytest.MonkeyPatch
        Simulate empty card selections, file picker cancellation, and a
        counting error.
    """
    window = AnkiExporter(None, reviews={}, selected="KeyboardNotes")
    window.show()
    monkeypatch.setattr(
        window.exercise,
        "daily_candidates",
        lambda rng: iter(()),
    )
    window.save.click()
    dialog = window.export_dialog
    assert dialog is not None
    wait_for_export(dialog)
    assert (
        dialog.total.text() == "Total: 0 cards" and not dialog.save.isEnabled()
    )
    assert "No cards match" in dialog.status.text()
    filename = dialog.filename.text()
    monkeypatch.setattr(
        QFileDialog,
        "exec",
        lambda self: QFileDialog.DialogCode.Rejected,
    )
    dialog.browse.click()
    assert dialog.filename.text() == filename
    dialog.dismiss.click()
    monkeypatch.setattr(
        exporter,
        "plan_deck",
        Mock(side_effect=ValueError("invalid settings")),
    )
    window.save.click()
    dialog = window.export_dialog
    assert dialog is not None
    wait_for_export(dialog)
    assert (
        "invalid settings" in dialog.total.text()
        and not dialog.save.isEnabled()
    )
    dialog.dismiss.click()
    window.save.click()
    dialog = window.export_dialog
    assert dialog is not None
    dialog.reject()
    wait_for_export(dialog)
    assert window.export_dialog is None and window.isVisible()
    window.close()


def test_empty_and_failed_exports_leave_existing_deck_intact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Protect a previous export when nothing matches or the illustration
    cannot be saved.

    Parameters
    ----------
    tmp_path : Path
        Folder containing a previous export.
    monkeypatch : pytest.MonkeyPatch
        Supplies an empty sample and simulates a failed render.
    """
    path = tmp_path / "previous.apkg"
    path.write_bytes(b"previous deck")
    exercise = KeyboardNotes()
    widget = Mock()
    widget.grab.return_value.save.return_value = False
    with pytest.raises(OSError, match="render"):
        exporter._picture(widget, folder=tmp_path, label="Staff")
    with pytest.raises(OSError):
        export_deck(
            path,
            exercise=exercise,
            reviews=[],
            render=Mock(side_effect=OSError("disk full")),
        )
    monkeypatch.setattr(exercise, "daily_candidates", lambda rng: iter(()))
    assert export_deck(path, exercise=exercise, reviews=[], render=Mock()) == 0
    assert path.read_bytes() == b"previous deck"


def test_modeless_session_reuses_the_window_and_recovers_a_closed_pipe(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Launch from Tools, reopen the same child, and start a new one if the
    old window has just closed.

    Parameters
    ----------
    app : QApplication
        Qt application for the parent window.
    monkeypatch : pytest.MonkeyPatch
        Substitute a process transport and capture launch errors.
    """
    ctx = Mock()
    monkeypatch.setattr(QApplication, "desktopFileName", lambda: "alto-dev")
    reader, writer = Mock(), Mock()
    ctx.Pipe.return_value = (reader, writer)
    monkeypatch.setattr(
        exporter.multiprocessing,
        "get_context",
        lambda method: ctx,
    )
    with closing(Database()) as db:
        learner = Learner(db, profile=db.add_profile("Ada"))
        window = MainWindow(learner)
        window.open_exercise(KeyboardNotes)
        tools = next(
            a.menu()
            for a in window.menu_button.menu().actions()
            if a.text() == "Tools"
        )
        assert isinstance(tools, QMenu)
        action = next(
            a for a in tools.actions() if a.text() == "Anki Exporter"
        )
        action.trigger()
        assert (
            ctx.Process.call_args.kwargs["kwargs"]["selected"]
            == "KeyboardNotes"
        )
        assert (
            ctx.Process.call_args.kwargs["kwargs"]["desktop_id"] == "alto-dev"
        )
        action.trigger()
        writer.send.assert_called_once_with("raise")
        window.open_settings()
        assert window._settings is not None
        window._settings.choose_theme("studio_dark")
        writer.send.assert_called_with(("theme", "studio_dark", "[]"))
        window._settings.choose_theme("system")
        window._settings.close()
        assert ctx.Process.call_count == 1
        writer.send.side_effect = BrokenPipeError
        action.trigger()
        assert ctx.Process.call_count == 2
        warning = Mock()
        monkeypatch.setattr(QMessageBox, "warning", warning)
        ctx.Process.return_value.start.side_effect = OSError("launch failed")
        action.trigger()
        assert "launch failed" in warning.call_args.args[-1]
        window._exporter.commands = writer
        window._exporter.sync_theme("studio")
        assert window._exporter.commands is None
        window.close()


@pytest.mark.parametrize("desktop_id", ["alto", "alto-dev"])
def test_isolated_export_window_reads_practice_settings_and_uses_private_edits(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    desktop_id: str,
) -> None:
    """
    Drive the exporter entry point with a private preferences folder and
    a real Qt event loop.

    Parameters
    ----------
    app : QApplication
        Existing application used in place of the child process's
        QApplication.
    tmp_path : Path
        Parent settings folder.
    monkeypatch : pytest.MonkeyPatch
        Supplies the application in this test interpreter.
    desktop_id : str
        Desktop entry of the installed or development copy that opened
        the exporter.
    """
    monkeypatch.setenv("ALTO_HOME", str(tmp_path))
    store().setValue("notationIdentification/terms", "Vertical turn")
    store().setValue("ui/theme", "studio")
    snapshot = export_settings()
    reader, writer = multiprocessing.Pipe(duplex=False)
    writer.send("raise")
    light, dark = (
        {part: getattr(theme, part) for part in PARTS} for theme in STUDIO
    )
    dark["window"] = "#172431"
    user_themes = json.dumps(
        [{"id": "my_export", "name": "Custom", "light": light, "dark": dark}],
    )
    writer.send(("theme", "my_export_dark", user_themes))
    writer.close()
    observed = []
    # Capture assertions outside Qt signal handlers, where exceptions
    # would not fail pytest.
    original_show = AnkiExporter.show
    original_close = AnkiExporter.close

    def inspect(window: AnkiExporter) -> None:
        """
        Capture the filter and scheduling controls, then edit the
        private settings.

        Parameters
        ----------
        window : _ExportDialog
            Dialog created by the exporter process entry point.
        """
        original_show(window)
        child_app.setDesktopFileName.assert_called_once_with(desktop_id)
        assert (
            window.windowType() == Qt.WindowType.Window
            and not window.isModal()
        )
        assert window.palette().window().color().name() == "#eceef1"
        assert window.save.property("primary")
        window.save.click()
        dialog = window.export_dialog
        assert (
            dialog is not None
            and dialog.filename.property("field")
            and dialog.save.property("primary")
        )
        wait_for_export(dialog)
        assert (
            dialog.palette().window().color()
            == window.palette().window().color()
        )
        assert QCoreApplication.testAttribute(
            Qt.ApplicationAttribute.AA_DontUseNativeDialogs,
        )
        picker_checks = []

        def inspect_picker() -> None:
            """
            Record the file picker palette and check the shape of an
            open dropdown.
            """
            picker = app.activeModalWidget()
            assert isinstance(picker, QFileDialog)
            combos = picker.findChildren(QComboBox)
            combo = combos[-1]
            combo.showPopup()
            app.processEvents()
            popup = combo.view().window()
            picker_checks.append(
                (
                    picker.palette().window().color(),
                    all(field.property("field") for field in combos),
                    popup.isVisible() and not popup.mask().isEmpty(),
                ),
            )
            combo.hidePopup()
            picker.reject()

        QTimer.singleShot(0, inspect_picker)
        dialog.browse.click()
        assert picker_checks == [
            (window.palette().window().color(), True, True),
        ]
        panel = window.panel
        assert isinstance(panel, NotationSettingsPanel)
        assert not panel.next_question_row.isEnabled()
        observed.append(
            (
                window.exercise.name,
                window.scheduling.isEnabled(),
                set(settings.notation.terms),
            ),
        )
        panel.select_none.switched.emit(True)
        assert not settings.notation.terms

    def inspect_close(window: AnkiExporter) -> bool:
        """
        Verify the live palette on both windows before processing the
        close.

        Parameters
        ----------
        window : AnkiExporter
            The window whose child dialog stayed open during the theme
            change.

        Returns
        -------
        bool
            Whether Qt closed the window.
        """
        dialog = window.export_dialog
        if dialog is not None:
            observed.append(
                (
                    window.palette().window().color().name(),
                    dialog.palette().window().color().name(),
                    saved_theme(),
                ),
            )
        return original_close(window)

    child_app = Mock()
    child_app.exec.side_effect = app.exec
    monkeypatch.setattr(exporter, "QApplication", lambda argv: child_app)
    native_flag = Qt.ApplicationAttribute.AA_DontUseNativeDialogs
    old_native = QCoreApplication.testAttribute(native_flag)
    monkeypatch.setattr(AnkiExporter, "close", inspect_close)
    monkeypatch.setattr(AnkiExporter, "show", inspect)
    # Returning to the suite must keep the main application's event loop
    # available.
    old_quit = app.quitOnLastWindowClosed()
    app.setQuitOnLastWindowClosed(True)
    try:
        exporter._run_exporter(
            reader,
            desktop_id=desktop_id,
            plugins=tmp_path / "plugins",
            preferences=snapshot,
            mode="FSRS",
            self_grading=True,
            limits=[("", 5, 100)],
            reviews={},
            selected="NotationIdentification",
        )
    finally:
        app.setQuitOnLastWindowClosed(old_quit)
        QCoreApplication.setAttribute(native_flag, old_native)
        apply_theme("system")
    assert observed == [
        ("Notation Identification", True, {"Vertical turn"}),
        ("#172431", "#172431", "my_export_dark"),
    ]
    monkeypatch.setenv("ALTO_HOME", str(tmp_path))
    assert export_settings() == snapshot


def test_sm2_relearning_uses_a_timestamp_and_preserves_ease() -> None:
    """
    Keep an intraday relearning deadline when importing a self-graded
    SM-2 card.
    """
    due = 1_800_000_123
    review = Review(
        item_key="abc",
        signature="",
        payload="",
        scheduler="SM-2",
        due=due,
        state=json.dumps({"interval": 4, "ease": 2.1, "phase": "relearning"}),
        seen=5,
    )
    assert _schedule(review) == (3, 1, due, 4, 2100, 5, 1001, "")
