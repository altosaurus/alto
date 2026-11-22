"""
Tests for the lessons: the switch on the home page, the lesson page, the circle of fifths lesson and its soft tasks.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QRadioButton,
)

from alto.audio import INSTRUMENT_BY_KEY, sounds
from alto.exercises import REGISTRY, Question
from alto.exercises.library import (
    CircleOfFifths,
    IntervalNames,
    KeyboardIntervals,
    KeyboardNotes,
    KeySignatureConstruction,
    KeySignatures,
    NotationIdentification,
    NoteConstruction,
    NoteNames,
)
from alto.lessons import LESSONS, Step
from alto.lessons.circle_of_fifths import (
    CIRCLE_OF_FIFTHS,
    summary,
)
from alto.lessons.intervals import INTERVALS
from alto.lessons.key_signatures import KEY_SIGNATURES
from alto.lessons.pitches_and_notes import PITCHES_AND_NOTES
from alto.theory.fifths import (
    MAJORS,
    SIGNATURES,
)
from alto.theory.pitch import Note
from alto.ui.app_settings import AppSettingsDialog
from alto.ui.exercise_view import ExerciseView
from alto.ui.home import HomePage
from alto.ui.keyboard import KeyboardWidget
from alto.ui.lesson import (
    GIVE_UP_AFTER,
    LessonsPage,
    LessonView,
    StepView,
    saved_step,
)
from alto.ui.main_window import MainWindow
from alto.ui.store import store
from alto.ui.transition_preview import (
    PAUSE_MS,
    TransitionPreview,
)
from alto.ui.transitions import (
    TRANSITIONS,
    save_transition,
    saved_transition,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from PySide6.QtWidgets import QApplication

    from alto.exercises.base import Exercise
    from alto.lessons.base import Lesson


@pytest.fixture
def clean_lessons() -> Iterator[None]:
    """
    Start a test with no saved lesson progress and the exercises showing, and leave it so.

    Yields
    ------
    None
        Once the saved state is cleared.
    """
    for key in ("lessons", "ui/homeMode"):
        store().remove(key)
    yield
    for key in ("lessons", "ui/homeMode"):
        store().remove(key)


def test_the_home_page_switches_between_exercises_and_lessons(app: QApplication, clean_lessons: None) -> None:
    """
    Check that the switch at the top of the home page shows the exercise cards or the lesson cards, and remembers which.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    page = HomePage(REGISTRY)
    page.show()
    assert page.mode == "exercises" and page.cards[0].isVisible() and not page.lesson_cards[0].isVisible()
    page.mode_control.buttons[1].click()
    assert page.mode == "lessons" and page.lesson_cards[0].isVisible() and not page.cards[0].isVisible()
    assert HomePage(REGISTRY).mode == "lessons"  # remembered
    page.mode_control.buttons[0].click()
    assert page.mode == "exercises" and page.cards[0].isVisible()


def wait_until_still(page: HomePage) -> None:
    """
    Wait for a transition on the home page to finish, for at most three seconds.

    Parameters
    ----------
    page : HomePage
        The page.
    """
    for _ in range(150):
        if not page.canvas.running:
            return
        QTest.qWait(20)


def jump_to_the_end(page: HomePage) -> None:
    """
    Take a transition on the home page to its last frame at once, so a test need not wait for it in real time.

    Parameters
    ----------
    page : HomePage
        The page.
    """
    QTest.qWait(1)  # the transition begins from a zero-delay timer, so let that go first
    # noinspection PyProtectedMember
    animation = page.canvas._animation
    animation.setCurrentTime(animation.duration())
    wait_until_still(page)


def test_every_transition_plays_to_the_end_and_leaves_the_new_cards_showing(app: QApplication, clean_lessons: None) -> None:
    """
    Check that each transition covers the cards while it plays, finishes, and leaves the new cards in place.

    The first one is waited for in real time; the others are taken to their last frame, which ends them the same way.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    try:
        for number, transition in enumerate(TRANSITIONS):
            finish = wait_until_still if number == 0 else jump_to_the_end
            save_transition(transition.key)
            page = HomePage(REGISTRY)
            page.resize(1000, 600)
            page.show()
            QTest.qWait(30)
            page.mode_control.buttons[1].click()
            assert page.lesson_cards[0].isVisible() and not page.cards[0].isVisible()  # in place at once
            assert page.canvas.running == (transition.frame is not None), transition.key
            QTest.qWait(40)
            if transition.frame is not None:
                assert page.canvas.running and page.canvas.new and page.canvas.old, transition.key
            finish(page)
            assert not page.canvas.running and not page._hidden.isEnabled(), transition.key
            page.mode_control.buttons[0].click()  # and back again
            finish(page)
            assert page.cards[0].isVisible() and not page.lesson_cards[0].isVisible() and not page.canvas.running
            page.close()
    finally:
        store().remove("ui/homeTransition")


def test_a_second_flip_during_a_transition_ends_the_first(app: QApplication, clean_lessons: None) -> None:
    """
    Check that flipping the switch again while a transition plays settles on the side that was last asked for.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    save_transition("cascade")
    try:
        page = HomePage(REGISTRY)
        page.resize(1000, 600)
        page.show()
        QTest.qWait(30)
        page.mode_control.buttons[1].click()
        QTest.qWait(60)
        page.mode_control.buttons[0].click()
        wait_until_still(page)
        assert page.mode == "exercises" and page.cards[0].isVisible() and not page.lesson_cards[0].isVisible()
        assert not page.canvas.running
    finally:
        store().remove("ui/homeTransition")


def test_the_transition_is_cascade_until_another_is_chosen_in_the_settings(app: QApplication) -> None:
    """
    Check the default, that the settings offer all of them with "no transition", and that choosing one is remembered.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    store().remove("ui/homeTransition")
    assert saved_transition() == "cascade"
    assert len({item.key for item in TRANSITIONS}) == len(TRANSITIONS) > 11  # every one has its own key
    assert [item.key for item in TRANSITIONS][:2] == ["none", "cascade"]  # the default comes straight after "no transition"
    dialog = AppSettingsDialog()
    dialog.categories.setCurrentRow(4)
    assert set(dialog.transition_items) == {item.key for item in TRANSITIONS}
    assert dialog.transition_list.currentItem() is dialog.transition_items["cascade"]
    dialog.transition_list.setCurrentItem(dialog.transition_items["flip"])
    assert saved_transition() == "flip"
    dialog.transition_list.setCurrentItem(dialog.transition_items["none"])
    assert saved_transition() == "none"
    store().remove("ui/homeTransition")


def test_the_switch_has_an_icon_on_each_side(app: QApplication) -> None:
    """
    Check that both sides of the switch have an icon.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    page = HomePage(REGISTRY)
    assert [not button.icon().isNull() for button in page.mode_control.buttons] == [True, True]


def test_the_switch_is_compact_in_the_workspace_and_changes_only_the_list(app: QApplication, clean_lessons: None) -> None:
    """
    Keep the selected list independent of the activity and use compact controls in the workspace.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    window = MainWindow()
    window.show()
    control = window.home.mode_control
    window.open_exercise(CircleOfFifths)
    exercise = window.stack.currentWidget()
    assert control.isVisible() and [button.text() for button in control.buttons] == ["", ""]
    control.buttons[1].click()
    assert window.stack.currentWidget() is exercise and window.nav_stack.currentWidget() is window.lesson_nav
    window.open_lessons("circle-of-fifths")
    lesson = window.stack.currentWidget()
    control.buttons[0].click()
    assert window.stack.currentWidget() is lesson and window.nav_stack.currentWidget() is window.nav
    assert [button.text() for button in control.buttons] == ["", ""]
    window.show_home()
    assert [button.text() for button in control.buttons] == ["", ""]


def test_a_lesson_card_opens_its_lesson_and_leaving_returns_to_the_lessons(app: QApplication, clean_lessons: None) -> None:
    """
    Check that clicking a lesson card opens the lesson, with the lesson's title, and that leaving shows the lessons again.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    window = MainWindow()
    window.show()
    window.show_lessons()
    assert window.home.mode == "lessons"
    window.home.lesson_cards[0].click()
    assert window.title_label.text() == LESSONS[0].title and isinstance(window.stack.currentWidget(), LessonsPage)
    page = window.stack.currentWidget()
    assert isinstance(page, LessonsPage)
    page.back_button.click()
    assert window.stack.currentWidget() is window.home and window.home.mode == "lessons"


def test_the_lessons_menu_entry_goes_to_the_lessons(app: QApplication, clean_lessons: None) -> None:
    """
    Check that the lessons button at the top is always there, and takes you to the lessons on the home page.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    window = MainWindow()
    window.show()
    window.open_exercise(CircleOfFifths)
    window.show_lessons()
    assert window.stack.currentWidget() is window.home and window.home.mode == "lessons"


def test_the_reference_pane_has_a_button_that_opens_the_lesson(app: QApplication, clean_lessons: None) -> None:
    """
    Check that the circle of fifths reference pane offers the lesson at its top, and that the button opens it.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    window = MainWindow()
    window.show()
    window.open_exercise(CircleOfFifths)
    view = window.stack.currentWidget()
    assert isinstance(view, ExerciseView) and view.book_btn is not None
    view.book_btn.setChecked(True)
    assert view._reference is not None and not view._reference.lesson_button.isHidden()
    view._reference.lesson_button.click()
    page = window.stack.currentWidget()
    assert isinstance(page, LessonsPage) and page.view.lesson.key == "circle-of-fifths"
    page.back_button.click()
    assert window.stack.currentWidget() is view


def test_the_note_references_connect_the_related_exercises(app: QApplication, clean_lessons: None) -> None:
    """
    Follow each exercise's hints into the lesson and leave it for a different exercise.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears saved progress.
    """
    window = MainWindow()
    window.show()
    for source, clue, destination in (
        (KeyboardNotes, "pair of black keys", NoteNames),
        (NoteNames, "second line is G4", NoteConstruction),
        (NoteConstruction, "degree 2 in C major is D", NotationIdentification),
        (NotationIdentification, "vertical stroke", KeyboardNotes),
    ):
        window.open_exercise(source)
        exercise = window.stack.currentWidget()
        assert isinstance(exercise, ExerciseView) and exercise.book_btn is not None
        exercise.book_btn.click()
        reference = exercise._reference
        assert reference is not None and reference.isVisible()
        assert any(clue in label.text() for label in reference.findChildren(QLabel))
        reference.lesson_button.click()
        page = window.stack.currentWidget()
        assert isinstance(page, LessonsPage) and page.view.lesson is PITCHES_AND_NOTES
        page.view.go(to=len(PITCHES_AND_NOTES.steps) - 1)
        closing = page.view.pages.currentWidget()
        assert isinstance(closing, StepView)
        button = next(button for button in closing.findChildren(QPushButton) if button.text() == destination.name)
        button.click()
        practice = window.stack.currentWidget()
        assert isinstance(practice, ExerciseView) and isinstance(practice.exercise, destination)
    window.close()


@pytest.mark.parametrize("instrument", INSTRUMENT_BY_KEY)
def test_key_signature_lesson_matches_note_identification_volume(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    instrument: str,
) -> None:
    """
    Compare the final output for the F sharp and F natural in both views.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Records each effect and its volume at the moment playback starts.
    instrument : str
        The selected instrument.
    """
    lesson = StepView(next(step for step in KEY_SIGNATURES.steps if step.title == "A natural beside the note"))
    assert lesson.hear_button is not None
    notes = [Note.parse("F#4"), Note.parse("F4")]
    questions = iter([Question("Name the note.", choices=[note.name], answer=note.name, staff=[[note]]) for note in notes])
    exercise = NoteNames()
    monkeypatch.setattr(exercise, "generate", lambda rng: next(questions))
    view = ExerciseView(exercise, rng=random.Random(1))
    monkeypatch.setattr(sounds, "instrument", instrument)
    monkeypatch.setattr(sounds, "enabled", True)
    played = []

    def make_effect() -> Mock:
        """
        Capture the recording and gain passed to the output device for each note.

        Returns
        -------
        Mock
            An effect that records playback without opening a device.
        """
        effect = Mock()
        effect.play.side_effect = lambda: played.append((effect.setSource.call_args.args[0], effect.setVolume.call_args.args[0]))
        effect.isPlaying.return_value = False
        return effect

    monkeypatch.setattr("alto.audio.QSoundEffect", Mock(side_effect=make_effect))
    monkeypatch.setattr(sounds, "_effects", {})
    monkeypatch.setattr(sounds, "_release", lambda effect: effect.stop())
    with monkeypatch.context() as clock:
        pending = []
        clock.setattr("alto.audio.QTimer.singleShot", lambda delay, callback: pending.append(callback))
        lesson.hear_button.click()
        while pending:
            pending.pop(0)()
    lesson_output = played.copy()
    played.clear()
    for index, note in enumerate(notes):
        if index:
            view.next_question()
        next(button for button in view.buttons if button.text() == note.name).click()
        view._advance.stop()
    assert len(played) == 2 and played == lesson_output
    assert played[0][0] != played[1][0]
    assert [volume for _, volume in played] == pytest.approx([INSTRUMENT_BY_KEY[instrument].gain] * 2)
    sounds.stop_all()


def test_staff_sample_highlights_follow_playback(app: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Follow shared pitches, successive notes, and chords through playback, replay, and navigation.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Captures the audio clock so each onset can be inspected.
    """
    pending = []
    monkeypatch.setattr(sounds, "enabled", False)
    monkeypatch.setattr("alto.audio.QTimer.singleShot", lambda delay, callback: pending.append(callback))
    first, second = (StepView(step) for step in KEY_SIGNATURES.steps[:2])
    first.show()
    second.show()
    assert first.hear_button and second.hear_button
    first.hear_button.click()
    assert [staff.playback_column for staff in first.staves] == [0, 0]
    second.hear_button.click()
    first.hide()
    pending.pop(0)()  # the first sample's canceled end callback
    assert [staff.playback_column for staff in first.staves] == [None, None]
    assert [staff.playback_column for staff in second.staves] == [0, None]
    pending.pop(0)()
    assert [staff.playback_column for staff in second.staves] == [None, 0]
    second.hear_button.click()
    assert [staff.playback_column for staff in second.staves] == [0, None]
    second.close()
    while pending:
        pending.pop(0)()
    assert [staff.playback_column for staff in second.staves] == [None, None]

    for step in (step for step in INTERVALS.steps if step.hear_display == "staff"):
        view = StepView(step)
        assert view.hear_button is not None
        view.hear_button.click()
        staff = view.staves[0]
        for index, chord in enumerate(step.hear):
            assert staff.playback_column == index
            assert staff.columns[index] == [Note.parse(name) for name in chord]
            pending.pop(0)()
        assert staff.playback_column is None


@pytest.mark.parametrize("audible", [True, False])
@pytest.mark.parametrize(
    "step",
    [
        PITCHES_AND_NOTES.steps[0],
        PITCHES_AND_NOTES.steps[4],
        INTERVALS.steps[1],
        Step(title="Chord and melody", text="", hear=(("C4", "E4", "G4"), ("F#4",)), hear_display="keyboard"),
    ],
)
def test_lesson_keyboard_follows_sample_onsets(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    step: Step,
    audible: bool,
) -> None:
    """
    Follow each audio onset and restore the lesson's keys on completion, replay, or leaving the step.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Captures the playback clock and audio output.
    step : Step
        A keyboard example with a target pitch, an interval, or a chord.
    audible : bool
        Whether notes are sent to the audio output.
    """
    pending = []
    output = Mock()
    monkeypatch.setattr(sounds, "enabled", audible)
    monkeypatch.setattr(sounds, "_effect", Mock())
    monkeypatch.setattr(sounds, "_play_column", output)
    view = StepView(step)
    view.show()
    keys = view.keyboard
    assert keys is not None and view.hear_button is not None
    idle = (keys.highlight, keys.additional_highlights.copy(), keys.highlight_color, keys.accessibleName())
    monkeypatch.setattr("alto.audio.QTimer.singleShot", lambda delay, callback: pending.append(callback))

    view.hear_button.click()
    for column in step.hear:
        midis = [Note.parse(name).midi for name in column]
        assert (keys.highlight, keys.additional_highlights) == (midis[0], set(midis[1:]))
        assert keys.highlight_color != idle[2]
        assert keys.accessibleName() == f"Keyboard with {' and '.join(column)} highlighted"
        if audible:
            assert output.call_args.args[0] == midis
        pending.pop(0)()
    assert output.call_count == (len(step.hear) if audible else 0)
    assert (keys.highlight, keys.additional_highlights, keys.highlight_color, keys.accessibleName()) == idle

    view.hear_button.click()
    view.hear_button.click()
    pending.pop(0)()  # stale callback from the first play
    assert keys.highlight == Note.parse(step.hear[0][0]).midi
    view.hide()
    pending.pop(0)()
    assert (keys.highlight, keys.additional_highlights, keys.highlight_color, keys.accessibleName()) == idle


def test_interval_examples_match_their_playback_and_feedback(app: QApplication) -> None:
    """
    Check the written notes, highlighted keys, and answers across the lesson.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    # With seed zero, the last question asks for F up to C.
    answers = ("Third", None, "m3", None, "10", "d5", "P5", None)
    for step, answer in zip(INTERVALS.steps, answers, strict=True):
        view = StepView(step, rng=random.Random(0))
        columns = [[Note.parse(name) for name in chord] for chord in step.hear]
        if step.hear_display == "staff":
            assert view.staves[0].columns == columns
        if step.hear_display == "keyboard":
            keyboard = view.findChild(KeyboardWidget)
            assert keyboard is not None
            assert {keyboard.highlight, *keyboard.additional_highlights} == {n.midi for chord in columns for n in chord}
        if answer is not None:
            assert view.task is not None and view.task.correct == answer
            next(button for button in view.choice_buttons if button.text() == answer).click()
            assert "Right." in view.feedback.text()


@pytest.mark.parametrize(
    ("lesson", "first", "second"),
    [(INTERVALS, IntervalNames, KeyboardIntervals), (KEY_SIGNATURES, KeySignatures, KeySignatureConstruction)],
)
def test_lesson_and_both_practice_links(
    app: QApplication,
    clean_lessons: None,
    lesson: Lesson,
    first: type[Exercise],
    second: type[Exercise],
) -> None:
    """
    Open the lesson from each exercise, practice the other format, and return to the closing step.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears saved progress.
    lesson : Lesson
        The lesson linked from both exercises.
    first, second : type of Exercise
        The two practice destinations.
    """
    window = MainWindow()
    window.show()
    for source, destination in ((first, second), (second, first)):
        window.open_exercise(source)
        exercise = window.stack.currentWidget()
        assert isinstance(exercise, ExerciseView) and exercise.book_btn is not None
        exercise.book_btn.click()
        assert exercise._reference is not None
        exercise._reference.lesson_button.click()
        page = window.stack.currentWidget()
        assert isinstance(page, LessonsPage) and page.view.lesson is lesson
        last = len(lesson.steps) - 1
        page.view.go(to=last)
        closing = page.view.pages.currentWidget()
        assert isinstance(closing, StepView)
        next(button for button in closing.findChildren(QPushButton) if button.text() == destination.name).click()
        practice = window.stack.currentWidget()
        assert isinstance(practice, ExerciseView) and isinstance(practice.exercise, destination)
        practice.lesson_back_button.click()
        returned = window.stack.currentWidget()
        assert isinstance(returned, LessonsPage) and returned.view.lesson is lesson and returned.view.current == last
    window.close()


def test_the_first_lesson_illustrates_its_keyboard_examples(app: QApplication) -> None:
    """
    Check the keyboard landmarks and the pitches paired with listening examples.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    assert LESSONS[0] is PITCHES_AND_NOTES
    examples = [step for step in PITCHES_AND_NOTES.steps if step.keyboard_note]
    expected = (
        (60, (("C4",), ("G4",)), True),
        (62, (), True),
        (72, (("C4",), ("C5",)), False),
        (61, (("C4",), ("C#4",)), False),
    )
    for step, (midi, pitches, labeled) in zip(examples, expected, strict=True):
        view = StepView(step)
        keyboard = view.findChild(KeyboardWidget)
        assert keyboard is not None and (keyboard.lo, keyboard.hi, keyboard.highlight) == (60, 72, midi)
        assert step.hear == pitches
        assert bool(keyboard.accessibleDescription()) == labeled


def test_pitch_lesson_questions_match_their_examples(app: QApplication) -> None:
    """
    Answer the listening, keyboard, and staff questions using the pitches each step presents.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    listening, keyboard, _, staff, _, _ = PITCHES_AND_NOTES.steps
    assert listening.hear == (("C4",), ("G4",))
    for step, answer in ((listening, "Second"), (keyboard, "D"), (staff, "A")):
        view = StepView(step)
        if step is staff:
            assert [(s.clef, s.columns[0][0].midi) for s in view.staves] == [("treble", 67), ("treble", 69)]
        next(button for button in view.choice_buttons if button.text() == answer).click()
        assert "Right." in view.feedback.text()


def test_every_step_of_the_lesson_builds_and_has_something_to_read(app: QApplication) -> None:
    """
    Check that each step can be built, with its circle where it says it has one.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    for step in CIRCLE_OF_FIFTHS.steps:
        view = StepView(step, rng=random.Random(1))
        assert step.title and step.text
        assert (view.circle is not None) == (step.circle != "none")
        assert (view.task is not None) == (step.make_task is not None)


def test_try_again_repeats_a_single_knowledge_check_question(app: QApplication) -> None:
    """
    Follow the hint, reveal the answer, and retry the same keyboard question.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = StepView(PITCHES_AND_NOTES.steps[1])
    task = view.task
    assert task is not None
    wrong = [button for button in view.choice_buttons if button.text() != task.correct]
    wrong[0].click()
    assert "Try again." in view.feedback.text() and task.hint in view.feedback.text()
    wrong[1].click()
    assert task.explanation in view.feedback.text()
    assert view.again.text() == "Try again" and not view.again.isHidden()
    view.again.click()
    assert view.task == task and view.prompt.text() == task.prompt
    assert view.feedback.text() == "" and all(button.isEnabled() for button in view.choice_buttons)


def test_a_task_can_be_answered_wrong_twice_and_is_then_given(app: QApplication) -> None:
    """
    Check that a wrong answer gets a hint, and a second one gets the answer, and that nothing can be failed.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = StepView(CIRCLE_OF_FIFTHS.steps[3], rng=random.Random(1))  # find the key with N sharps
    task = view.task
    assert task is not None and view.circle is not None
    right = next(iter(task.cells))
    wrong = ("outer", (right[1] + 5) % 12)
    view.circle.select(wrong[0], place=wrong[1])
    assert "Not quite" in view.feedback.text() and view.again.isHidden()
    for _ in range(GIVE_UP_AFTER - 1):
        view.circle.select(wrong[0], place=wrong[1])
    assert "Here it is" in view.feedback.text() and not view.again.isHidden()
    assert view.again.text() == "Try another"
    assert view.circle.cell == right


def test_a_right_answer_is_praised_and_another_can_be_asked(app: QApplication) -> None:
    """
    Check that the right cell is praised, and that Try another asks a fresh task.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = StepView(CIRCLE_OF_FIFTHS.steps[3], rng=random.Random(1))
    assert view.task is not None and view.circle is not None
    ring, place = next(iter(view.task.cells))
    view.circle.select(ring, place=place)
    assert "Right" in view.feedback.text() and not view.again.isHidden()
    view.again.click()
    assert view.feedback.text() == "" and view.again.isHidden()


def test_the_button_task_checks_the_letter(app: QApplication) -> None:
    """
    Check that the fifth task takes a button, praises the right letter and hints at a wrong one.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = StepView(CIRCLE_OF_FIFTHS.steps[1], rng=random.Random(3))
    assert view.task is not None
    wrong = next(button for button in view.choice_buttons if button.text() != view.task.correct)
    wrong.click()
    assert "Not quite" in view.feedback.text() and not wrong.isEnabled()
    right = next(button for button in view.choice_buttons if button.text() == view.task.correct)
    right.click()
    assert "Right" in view.feedback.text() and not any(button.isEnabled() for button in view.choice_buttons)


def test_walking_the_circle_steps_a_fifth_at_a_time(app: QApplication) -> None:
    """
    Check that the walk buttons go clockwise and counterclockwise around the outer ring, and tell the key signature.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = StepView(CIRCLE_OF_FIFTHS.steps[2], rng=random.Random(1))
    assert view.circle is not None
    for expected in (1, 2, 3):
        view.up.click()
        assert view.circle.cell == ("outer", expected)
        assert summary("outer", place=expected) in view.info.text()
    view.down.click()
    view.down.click()
    view.down.click()
    view.down.click()
    assert view.circle.cell == ("outer", 11) and "flat" in view.info.text()


def test_every_task_that_can_be_made_has_the_right_answer(app: QApplication) -> None:
    """
    Check each task maker many times: its answer is on the circle, and a task about sharps or flats counts them rightly.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    rng = random.Random(7)
    for step in CIRCLE_OF_FIFTHS.steps:
        if step.make_task is None:
            continue
        for _ in range(40):
            task = step.make_task(rng)
            assert task.prompt and task.hint and task.explanation
            if task.choices:
                assert task.correct in task.choices and len(set(task.choices)) == len(task.choices)
            else:
                assert task.cells and all(ring in {"outer", "inner"} and place in range(12) for ring, place in task.cells)
    sharps, flats = CIRCLE_OF_FIFTHS.steps[3], CIRCLE_OF_FIFTHS.steps[4]
    assert sharps.make_task is not None and flats.make_task is not None
    for _ in range(20):
        _, place = next(iter(sharps.make_task(rng).cells))
        assert SIGNATURES[place] > 0
        _, place = next(iter(flats.make_task(rng).cells))
        assert SIGNATURES[place] < 0 and MAJORS[place]


def test_a_lesson_remembers_its_step_and_leaves_from_either_end(app: QApplication, clean_lessons: None) -> None:
    """
    Check that moving through a lesson saves the step, that Back on the first step leaves, and that Finish leaves and resets.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    lesson = LESSONS[0]
    view = LessonView(lesson)
    left: list[bool] = []
    view.leave.connect(lambda: left.append(True))
    view.next_button.click()
    view.next_button.click()
    assert view.current == 2 and saved_step(lesson) == 2
    assert view.counter.text() == f"Step 3 of {len(lesson.steps)}"
    view.go(to=len(lesson.steps) - 1)
    assert view.next_button.text() == "Finish"
    view.next_button.click()
    assert left == [True] and saved_step(lesson) == 0
    first = LessonView(lesson, start=0)
    first.leave.connect(lambda: left.append(True))
    first.back_button.click()
    assert left == [True, True]


def test_a_started_lesson_says_where_to_continue_and_can_start_over(app: QApplication, clean_lessons: None) -> None:
    """
    Check that the lesson's card on the home page says where it was left, and that Start over goes back to the first step.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    home = HomePage(REGISTRY)
    assert not any(label.text().startswith("Step") for label in home.lesson_cards[0].findChildren(QLabel))
    assert home.lesson_cards[0].progress_bar is None
    page = LessonsPage(LESSONS[0].key, step=3)
    home.show()  # showing the page brings its cards up to date
    card = home.lesson_cards[0]
    assert f"Step 4/{len(LESSONS[0].steps)}" in [label.text() for label in card.findChildren(QLabel)]
    assert card.progress_bar is not None and card.progress_bar.fraction == 3 / len(LESSONS[0].steps)
    assert "Continue at step 4 of" in card.accessibleDescription()
    page.restart_button.click()
    assert page.view.current == 0 and saved_step(LESSONS[0]) == 0


def test_the_last_step_offers_to_practice_the_exercise(app: QApplication, clean_lessons: None) -> None:
    """
    Open practice from the final step and use Back to lesson to return to that step.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    window = MainWindow()
    window.show()
    window.show_lessons()
    window.home.lesson_cards[0].click()
    page = window.stack.currentWidget()
    assert isinstance(page, LessonsPage) and page.view.lesson is PITCHES_AND_NOTES
    for _ in PITCHES_AND_NOTES.steps[1:]:
        page.view.next_button.click()
    step_view = page.view.pages.currentWidget()
    assert isinstance(step_view, StepView)
    next(button for button in step_view.findChildren(QPushButton) if button.text() == NoteNames.name).click()
    assert window.title_label.text() == NoteNames.name
    practice = window.stack.currentWidget()
    assert isinstance(practice, ExerciseView) and practice.lesson_back_button.isVisible()
    app.processEvents()
    button = practice.lesson_back_button
    assert practice.rect().contains(button.mapTo(practice, button.rect().center()))
    QTest.mouseClick(button, Qt.MouseButton.LeftButton)
    assert window.stack.currentWidget() is page
    assert page.view.pages.currentWidget() is step_view
    assert practice.lesson_back_button.isHidden()
    window.open_exercise(NoteNames)
    assert practice.lesson_back_button.isHidden()


def test_lesson_mode_has_a_list_on_the_left_that_follows_the_steps(app: QApplication, clean_lessons: None) -> None:
    """
    Check that opening a lesson shows the lesson list in place of the exercise list, listing its steps, and keeps it in step.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    window = MainWindow()
    window.show()
    assert window.nav_stack.currentWidget() is window.nav
    window.open_lessons("circle-of-fifths")
    assert window.nav_stack.currentWidget() is window.lesson_nav
    nav = window.lesson_nav
    titles = [item.text().strip().split(".", 1)[1].strip() for item in nav.step_items]
    assert titles == [step.title for step in CIRCLE_OF_FIFTHS.steps]
    page = window.stack.currentWidget()
    assert isinstance(page, LessonsPage)
    page.view.next_button.click()
    assert nav.currentItem() is nav.step_items[1]
    nav.itemClicked.emit(nav.step_items[4])  # a click on a step goes to it
    assert page.view.current == 4 and nav.currentItem() is nav.step_items[4]


def test_the_lesson_list_can_be_hidden_and_shown_with_its_button(app: QApplication, clean_lessons: None) -> None:
    """
    Check that the lesson page has the toggle for the list, and that it works as the exercise one does.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    window = MainWindow()
    window.show()
    window.open_lessons("circle-of-fifths")
    page = window.stack.currentWidget()
    assert isinstance(page, LessonsPage)
    QTest.qWait(600)
    assert window.sidebar_width() > 0
    window.pane_button.click()
    QTest.qWait(600)
    assert window.sidebar_width() == 0
    window.toggle_sidebar()  # leave it as it was found
    QTest.qWait(600)


def test_leaving_a_lesson_brings_back_the_right_list(app: QApplication, clean_lessons: None) -> None:
    """
    Check that leaving a lesson that was opened from an exercise brings back the exercise list, and from the home page, no list.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    window = MainWindow()
    window.show()
    window.open_exercise(CircleOfFifths)
    QTest.qWait(600)
    window.open_lessons("circle-of-fifths")
    page = window.stack.currentWidget()
    assert isinstance(page, LessonsPage)
    page.back_button.click()
    assert window.stack.currentWidget() is not window.home and window.nav_stack.currentWidget() is window.nav
    window.show_lessons()
    window.home.lesson_cards[0].click()
    QTest.qWait(600)
    page = window.stack.currentWidget()
    assert isinstance(page, LessonsPage)
    page.back_button.click()
    QTest.qWait(600)
    assert window.stack.currentWidget() is window.home and window.sidebar_width() == 0
    window.home.set_mode("exercises")


def test_the_circle_of_a_lesson_is_never_cut_off(app: QApplication, clean_lessons: None) -> None:
    """
    Check that in a window of the default size, and a smaller one, the whole circle shows on every step that has one.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    for size in ((1100, 820), (1000, 640)):
        window = MainWindow()
        window.resize(*size)
        window.show()
        window.open_lessons("circle-of-fifths")
        page = window.stack.currentWidget()
        assert isinstance(page, LessonsPage)
        for number in range(len(CIRCLE_OF_FIFTHS.steps)):
            page.view.go(to=number)
            QTest.qWait(40)
            step = page.view.pages.currentWidget()
            assert isinstance(step, StepView)
            if step.circle is not None:
                bottom = step.circle.mapTo(page.view, step.circle.rect().bottomLeft()).y()
                assert bottom <= page.view.height() and min(step.circle.width(), step.circle.height()) >= 300, (size, number)
        window.close_overlay()
        window.close()


def test_the_transition_settings_have_a_list_on_the_left_and_a_preview_that_plays_once(app: QApplication) -> None:
    """
    Check the layout of the Transitions section, and that a transition is played once in the preview, and not again.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    store().remove("ui/homeTransition")
    try:
        dialog = AppSettingsDialog()
        dialog.resize(1000, 640)
        dialog.show()
        dialog.categories.setCurrentRow(4)
        QTest.qWait(50)
        listing, preview = dialog.transition_list, dialog.transition_preview
        assert listing.mapTo(dialog, listing.rect().topLeft()).x() < preview.mapTo(dialog, preview.rect().topLeft()).x()
        assert not dialog.appearance_pages.currentWidget().findChildren(QRadioButton)  # a list, not radio buttons
        dialog.transition_list.setCurrentItem(dialog.transition_items["flip"])
        assert preview.transition.key == "flip" and saved_transition() == "flip" and preview.side == 0
        QTest.qWait(PAUSE_MS + 200)  # after a short rest it plays
        assert preview.stage.canvas.running and preview.side == 1
        for _ in range(150):
            if not preview.stage.canvas.running:
                break
            QTest.qWait(20)
        assert not preview.stage.canvas.running
        QTest.qWait(PAUSE_MS * 3)  # and it does not start again by itself
        assert not preview.stage.canvas.running and preview.side == 1
        preview.replay()  # unless asked to
        assert preview.side == 0
        QTest.qWait(PAUSE_MS + 200)
        assert preview.side == 1
        dialog.transition_list.setCurrentItem(dialog.transition_items["none"])
        QTest.qWait(PAUSE_MS + 200)
        assert not preview.stage.canvas.running and preview.side == 1  # it switches at once, with nothing to play
        dialog.close()
    finally:
        store().remove("ui/homeTransition")


def test_the_switch_in_the_preview_works(app: QApplication) -> None:
    """
    Check that pressing a side of the switch in the preview plays the transition to it, and back, as often as wanted.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    store().remove("ui/homeTransition")
    try:
        preview = TransitionPreview()
        preview.resize(700, 500)
        preview.show()
        preview.show_transition("crossfade")
        assert all(button.isEnabled() for button in preview.switch.buttons)
        preview.switch.buttons[1].click()
        assert preview.side == 1 and preview.stage.canvas.running and preview.switch.current() == 1
        QTest.qWait(PAUSE_MS + 300)  # the rest that it would have taken to play by itself passes, and nothing else starts
        assert preview.side == 1
        preview.switch.buttons[0].click()  # back again: if the last one is still playing, it ends first
        assert preview.side == 0 and preview.switch.current() == 0
        preview.switch.buttons[0].click()  # the side that is already showing: nothing happens
        assert preview.side == 0
        for _ in range(150):
            if not preview.stage.canvas.running:
                break
            QTest.qWait(20)
        assert not preview.stage.canvas.running
        preview.close()
    finally:
        store().remove("ui/homeTransition")


def test_key_signature_lesson_examples(app: QApplication) -> None:
    """
    Check the displayed signature, note spelling, and feedback for the guided examples.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    for step, counts in zip(KEY_SIGNATURES.steps[:6], [(0, 1), (1, 1), (1, 2), (-1, -3), (0,), (-3, -4, 4)], strict=True):
        view = StepView(step, rng=random.Random(0))
        assert tuple(staff.key for staff in view.staves) == counts
        if step.hear:
            notes = [staff.columns[0][0] for staff in view.staves]
            assert list(dict.fromkeys(notes)) == [Note.parse(chord[0]) for chord in step.hear]
        if view.task:
            next(button for button in view.choice_buttons if button.text() == view.task.correct).click()
            assert "Right." in view.feedback.text()


def test_key_signature_lesson_reads_new_signatures(app: QApplication) -> None:
    """
    Verify fresh staff questions across all signatures against independently spelled answers.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    majors = "C♭ G♭ D♭ A♭ E♭ B♭ F C G D A E B F♯ C♯".split()
    minors = "A♭ E♭ B♭ F C G D A E B F♯ C♯ G♯ D♯ A♯".split()
    step = next(step for step in KEY_SIGNATURES.steps if step.task_staff)
    view = StepView(step, rng=random.Random(29))
    seen = set()
    for _ in range(250):
        assert view.task is not None
        staff = view.staves[0]
        minor = "minor" in view.task.prompt
        answer = (minors if minor else majors)[staff.key + 7]
        assert view.task.check(answer)
        assert len(set(view.task.choices)) == 3 and answer in view.task.choices
        assert staff.clef == view.task.clef and not staff.clef_hidden
        seen.add((staff.key, minor))
        view.ask()
    assert len(seen) == 30
