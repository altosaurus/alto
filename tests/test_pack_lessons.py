"""
Lessons that an instrument plugin supplies are listed, shown, and
checked like Alto's own.
"""

from __future__ import annotations

import json
import random
import shutil
from collections.abc import Callable, Iterator
from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from alto.audio import INSTRUMENT_BY_KEY, sounds
from alto.exercises.base import REGISTRY, FingerboardPosition, PicturePosition
from alto.exercises.packs import load_packs, read_pack
from alto.instrument_packs import INSTALLED
from alto.lessons import LESSONS, Lesson, register_lesson
from alto.terms import PLUGIN_TERMS, PluginTerm
from alto.ui import icons
from alto.ui import lesson as lesson_page
from alto.ui.glossary import GlossaryPage
from alto.ui.home import TileCard, exercise_icon, lesson_card, lesson_icon
from alto.ui.lesson import LessonsPage, StepView
from alto.ui.lesson_nav import LessonNav
from alto.ui.reference import PluginReferencePanel, reference_panel_for
from viola_pack import MANIFEST

VIOLA = MANIFEST
PARTS = "pack.viola.parts-of-the-viola"
NOTES = "pack.viola.finding-notes"
NOTES_EXERCISE = "pack.viola.first-position"


@pytest.fixture(autouse=True)
def isolated_registries() -> Iterator[None]:
    """
    Keep what a pack registers local to each test.

    Yields
    ------
    None
        The test can install packs in the regular app registries.
    """
    exercises, instruments, recordings, lessons = (
        REGISTRY.copy(),
        INSTALLED.copy(),
        INSTRUMENT_BY_KEY.copy(),
        LESSONS.copy(),
    )
    terms = PLUGIN_TERMS.copy()
    yield
    REGISTRY[:] = exercises
    LESSONS[:] = lessons
    PLUGIN_TERMS.clear()
    PLUGIN_TERMS.update(terms)
    INSTALLED.clear()
    INSTALLED.update(instruments)
    INSTRUMENT_BY_KEY.clear()
    INSTRUMENT_BY_KEY.update(recordings)


@pytest.fixture
def installed(tmp_path: Path) -> list[Lesson]:
    """
    Install the example pack's folder as an editable plugin.

    Parameters
    ----------
    tmp_path : Path
        Isolated plugins folder.

    Returns
    -------
    list of Lesson
        The lessons registered by the plugin.
    """
    before = len(LESSONS)
    shutil.copytree(VIOLA.parent, tmp_path / "viola")
    assert load_packs(tmp_path) == []
    return LESSONS[before:]


def _edited(tmp_path: Path, *, edit: Callable[[dict], None]) -> Path:
    """
    Copy the example pack with its manifest changed by ``edit``.

    Parameters
    ----------
    tmp_path : Path
        Where the copy goes.
    edit : Callable[[dict], None]
        Changes the parsed manifest in place. Keyword-only.

    Returns
    -------
    Path
        The copy's pack.json.
    """
    folder = tmp_path / "edited"
    shutil.copytree(VIOLA.parent, folder)
    manifest = json.loads((folder / "pack.json").read_text())
    edit(manifest)
    (folder / "pack.json").write_text(json.dumps(manifest))
    return folder / "pack.json"


def test_plugin_lessons_join_the_list_after_alto_s_own(
    installed: list[Lesson],
) -> None:
    """
    List the plugin's lessons at the end, in manifest order, in their
    own category, each linked to a plugin exercise.

    Parameters
    ----------
    installed : list of Lesson
        The lessons the plugin registered.
    """
    assert [lesson.key for lesson in installed] == [PARTS, NOTES]
    assert LESSONS[-2:] == installed and not any(
        lesson.key.startswith("pack.") for lesson in LESSONS[:-2]
    )
    names = {cls.__name__: cls.name for cls in REGISTRY}
    for lesson in installed:
        assert (
            lesson.category == "Viola"
            and lesson.exercise in names
            and len(lesson.steps) >= 6
        )
        assert lesson.steps[-1].closing and not any(
            step.closing for step in lesson.steps[:-1]
        )
    assert (
        names[installed[0].exercise] == "Parts of the Viola"
        and names[installed[1].exercise] == "Viola Note Identification"
    )


def test_every_step_points_at_the_plugin_s_own_instrument(
    installed: list[Lesson],
) -> None:
    """
    Check that pictures, sounds and questions in the lessons are
    complete and refer to things the plugin declares.

    Parameters
    ----------
    installed : list of Lesson
        The lessons the plugin registered.
    """
    key = "pack.viola.bowed-viola"
    for lesson in installed:
        for step in lesson.steps[:-1]:
            assert (
                isinstance(step.picture, PicturePosition | FingerboardPosition)
                and step.picture.instrument == key
            )
            assert step.make_task is not None and step.text.startswith("<p>")
            task = step.make_task(None)  # type: ignore[arg-type]
            assert task.hint and task.explanation
            # a question answered by clicking the picture must not show
            # its answer
            if task.targets:
                assert (
                    isinstance(step.picture, PicturePosition)
                    and not step.picture.marker
                    and 1 <= len(task.targets) <= 4
                )
            else:
                assert (
                    task.correct in task.choices
                    and 2 <= len(task.choices) <= 6
                )
        for step in lesson.steps:
            assert step.hear_instrument in ("", key)
    whole = installed[0].steps[0].picture
    assert isinstance(whole, PicturePosition) and not whole.marker
    assert all(
        isinstance(step.picture, FingerboardPosition)
        for step in installed[1].steps[1:5]
    )
    turned = installed[0].steps[4].picture
    assert (
        isinstance(turned, PicturePosition)
        and turned.view == "back"
        and installed[0].steps[4].title.startswith("The back")
    )
    assert (
        installed[1].steps[0].hear == (("C3",), ("G3",), ("D4",), ("A4",))
        and installed[1].steps[0].hear_instrument == key
    )


def test_new_terms_are_defined_where_they_first_appear(
    installed: list[Lesson],
) -> None:
    """
    Mark each defined term in bold, and define a term in a step before
    any later step asks about it.

    Parameters
    ----------
    installed : list of Lesson
        The lessons the plugin registered.
    """
    parts, notes = installed
    text = " ".join(step.text for step in parts.steps)
    for term in (
        "viola",
        "head",
        "neck",
        "body",
        "scroll",
        "pegbox",
        "peg",
        "nut",
        "fingerboard",
        "bridge",
        "tailpiece",
        "fine tuner",
        "back plate",
        "ribs",
        "button",
    ):
        assert f"<b>{term}</b>" in text, term
    note_text = [step.text for step in notes.steps]
    for term, index in (
        ("open string", 0),
        ("fifth", 0),
        ("half step", 1),
        ("natural notes", 2),
        ("position", 3),
        ("first position", 3),
    ):
        assert f"<b>{term}</b>" in note_text[index], term


def test_lessons_show_in_the_list_and_on_a_tile(
    app: QApplication,
    installed: list[Lesson],
) -> None:
    """
    Offer the plugin's lessons in the lesson list and as tiles, with
    progress remembered under their own keys.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    installed : list of Lesson
        The lessons the plugin registered.
    """
    del app
    nav = LessonNav()
    nav.show_lesson(NOTES)
    assert len(nav.step_items) == 6
    titles = [nav.item(row).text() for row in range(nav.count())]
    assert (
        "VIOLA" in titles
        and "Parts of the Viola" in titles
        and "Finding Notes on the Viola" in titles
    )
    card = lesson_card(installed[0])
    assert card.accessibleName() == "Parts of the Viola, Viola"
    lesson_page.save_step(installed[1], step=3)
    assert (
        lesson_page.saved_step(installed[1]) == 3
        and lesson_page.saved_step(installed[0]) == 0
    )


def test_a_lesson_page_walks_through_every_step(
    app: QApplication,
    installed: list[Lesson],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Show each step with its picture, play its notes on the plugin's
    instrument, and mark a knowledge check right or wrong.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    installed : list of Lesson
        The lessons the plugin registered.
    monkeypatch : pytest.MonkeyPatch
        Observe playback instead of making sound.
    """
    del app
    play = Mock()
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(sounds, "play_notes", play)
    for lesson in installed:
        page = LessonsPage(lesson.key, step=0)
        practice = Mock()
        page.practice_requested.connect(practice)
        for number, step in enumerate(lesson.steps):
            page.view.go(to=number)
            view = page.view._views[number]
            assert (view.picture is not None) == (step.picture is not None)
            if step.picture is not None and view.picture is not None:
                assert (
                    view.picture.position == step.picture
                    and view.picture.model
                    is INSTALLED["pack.viola.bowed-viola"]
                )
            if step.hear:
                play.reset_mock()
                view.hear()
                assert (
                    play.call_args.kwargs["instrument"]
                    == "pack.viola.bowed-viola"
                )
            if step.make_task is not None:
                task = view.task
                assert task is not None
                if task.targets:
                    assert view.picture is not None and not view.choice_buttons
                    view.picture.picked.emit(1.0, 1.0)  # far from every target
                    assert (
                        view._wrong == 1
                        and "Not quite" in view.feedback.text()
                    )
                    view.picture.picked.emit(
                        task.targets[0][0],
                        task.targets[0][1],
                    )
                    assert "Right" in view.feedback.text() and view._done
                    continue
                wrong = next(
                    button
                    for button in view.choice_buttons
                    if button.text() != task.correct
                )
                wrong.click()
                assert view._wrong == 1
                next(
                    button
                    for button in view.choice_buttons
                    if button.text() == task.correct
                ).click()
        page.view._views[len(lesson.steps) - 1].practice_button.click()
        practice.assert_called_once_with(lesson.exercise)


def test_steps_without_a_plugin_picture_are_unchanged(
    app: QApplication,
) -> None:
    """
    Show no picture panel on a built-in step, so existing lessons look
    as they did.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    del app
    for lesson in LESSONS:
        assert all(
            step.picture is None and step.hear_instrument == ""
            for step in lesson.steps
        )
    assert StepView(LESSONS[0].steps[0]).picture is None


def test_register_lesson_refuses_a_repeated_key() -> None:
    """Keep each lesson key unique, since progress is saved under it."""
    first = LESSONS[0]
    with pytest.raises(ValueError, match="already listed"):
        register_lesson(first)


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        (lambda m: m["lessons"][0].update(exercise="missing"), "exercises"),
        (
            lambda m: m["lessons"][0].update(
                related_exercises=["first-position", "first-position"],
            ),
            "related_exercises",
        ),
        (
            lambda m: m["lessons"][0].update(
                related_exercises=["viola-parts"],
            ),
            "different exercise",
        ),
        (lambda m: m["lessons"][0].update(colour="red"), "only these fields"),
        (
            lambda m: m["lessons"][0].update(title="<b>Parts</b>"),
            "plain-text title",
        ),
        (lambda m: m["lessons"][0].update(steps=[]), "between 1 and"),
        (
            lambda m: m["lessons"][0].update(
                steps=m["lessons"][0]["steps"] * 3,
            ),
            "between 1 and",
        ),
        (lambda m: m["lessons"][0]["steps"][0].update(text=[]), "paragraphs"),
        (
            lambda m: m["lessons"][0]["steps"][0].update(
                text=["<script>x</script>"],
            ),
            "plain-text paragraph",
        ),
        (
            lambda m: m["lessons"][0]["steps"][0].update(colour="red"),
            "only these fields",
        ),
        (
            lambda m: m["lessons"][0]["steps"][0]["picture"].update(
                instrument="nothing",
            ),
            "Unknown instrument",
        ),
        (
            lambda m: m["lessons"][0]["steps"][2]["picture"].update(
                point=[-1, 0],
            ),
            "outside",
        ),
        (
            lambda m: m["lessons"][0]["steps"][2]["picture"].update(
                point=[1900, 700],
            ),
            "inside the focus region",
        ),
        (
            lambda m: m["lessons"][0]["steps"][2]["picture"].update(
                marker_size=1,
            ),
            "marker_size",
        ),
        (
            lambda m: m["lessons"][0]["steps"][2]["picture"].update(
                colour="red",
            ),
            "only these fields",
        ),
        (
            lambda m: m["lessons"][0]["steps"][2]["picture"].update(
                view="side",
            ),
            "views, or leave it out|name of one of",
        ),
        (
            lambda m: m["lessons"][1]["steps"][1]["picture"].update(
                string="E2",
            ),
            "one of",
        ),
        (
            lambda m: m["lessons"][1]["steps"][1]["picture"].update(note="C2"),
            "open string up to",
        ),
        (
            lambda m: m["lessons"][1]["steps"][1]["picture"].update(
                point=[1, 1],
            ),
            "instrument, string, and note only",
        ),
        (
            lambda m: m["lessons"][1]["steps"][0].update(hear=[["H9"]]),
            "Expected a note",
        ),
        (lambda m: m["lessons"][1]["steps"][0].update(hear=[]), "hear"),
        (
            lambda m: m["lessons"][1]["steps"][0].update(
                hear_instrument="nothing",
            ),
            "hear_instrument",
        ),
        (
            lambda m: m["lessons"][1]["steps"][0]["task"].update(
                answer="Z string",
            ),
            "match one of its choices",
        ),
        (
            lambda m: m["lessons"][1]["steps"][0]["task"].update(
                choices=["A string"],
            ),
            "two to six",
        ),
        (
            lambda m: m["lessons"][1]["steps"][0]["task"].pop("hint"),
            "these fields",
        ),
        (
            lambda m: m["lessons"].append(dict(m["lessons"][0])),
            "Duplicate lesson id",
        ),
    ],
)
def test_bad_lessons_are_refused_with_a_reason(
    tmp_path: Path,
    edit: Callable[[dict], None],
    message: str,
) -> None:
    """
    Refuse a lesson that is malformed, or that refers to something the
    plugin does not declare, and say why.

    Parameters
    ----------
    tmp_path : Path
        Isolated copy of the example pack.
    edit : Callable[[dict], None]
        Damages the parsed manifest in place.
    message : str
        Part of the expected diagnostic.
    """
    with pytest.raises(ValueError, match=message):
        read_pack(_edited(tmp_path, edit=edit))


def test_a_plugin_without_lessons_adds_none(tmp_path: Path) -> None:
    """
    Treat the lessons field as optional, so earlier packs keep working.

    Parameters
    ----------
    tmp_path : Path
        Isolated copy of the example pack.
    """

    def drop(manifest: dict) -> None:
        """
        Remove the lessons and everything in the manifest that links to
        them.

        Parameters
        ----------
        manifest : dict
            The parsed manifest, changed in place.
        """
        del manifest["lessons"], manifest["glossary"]
        for exercise in manifest["exercises"]:
            exercise.pop("lessons", None)

    bare = read_pack(_edited(tmp_path, edit=drop))
    assert bare[0].lessons == ()
    before = len(LESSONS)
    assert load_packs(tmp_path) == [] and len(LESSONS) == before


def test_exercises_and_lessons_link_both_ways(
    installed: list[Lesson],
    app: QApplication,
) -> None:
    """
    Offer a lesson from its exercise and an exercise from its lesson,
    whichever end the plugin wrote the link at.

    Parameters
    ----------
    installed : list of Lesson
        The lessons the plugin registered.
    app : QApplication
        Shared Qt application.
    """
    del app
    parts, notes = installed
    assert (
        parts.related_exercises == (NOTES_EXERCISE,)
        and notes.related_exercises == ()
    )  # the notes exercise names the parts lesson
    for cls in REGISTRY[-2:]:
        panel = reference_panel_for(cls())
        assert isinstance(panel, PluginReferencePanel)
        wanted = [
            lesson
            for lesson in installed
            if cls.__name__ in (lesson.exercise, *lesson.related_exercises)
        ]
        assert [button.toolTip() for button in panel.lesson_buttons] == [
            f"Open {lesson.title}" for lesson in wanted
        ]
        asked = []
        panel.lesson_requested.connect(asked.append)
        panel.lesson_button.click()
        assert asked == [wanted[0].key]
    assert (
        reference_panel_for(REGISTRY[0]()) is not None
    )  # the built-in reference panels are untouched


def test_an_exercise_cannot_name_a_missing_lesson(tmp_path: Path) -> None:
    """
    Refuse an exercise that lists a lesson the plugin does not have.

    Parameters
    ----------
    tmp_path : Path
        Isolated copy of the example pack.
    """
    with pytest.raises(
        ValueError,
        match="lists a lesson this plugin does not have",
    ):
        read_pack(
            _edited(
                tmp_path / "a",
                edit=lambda m: m["exercises"][0].update(lessons=["nothing"]),
            ),
        )
    with pytest.raises(ValueError, match="up to five distinct lessons"):
        read_pack(
            _edited(
                tmp_path / "b",
                edit=lambda m: m["exercises"][0].update(
                    lessons=["finding-notes"] * 2,
                ),
            ),
        )


def test_tiles_use_the_plugin_s_icon(
    installed: list[Lesson],
    app: QApplication,
) -> None:
    """
    Draw a plugin's exercise and lesson tiles with the icon the plugin
    supplied, not Alto's default.

    Parameters
    ----------
    installed : list of Lesson
        The lessons the plugin registered.
    app : QApplication
        Shared Qt application.
    """
    del app
    shapes = REGISTRY[-1].icon
    assert (
        shapes.startswith("<path")
        and "COLOR" in shapes
        and "fill-rule" in shapes
    )
    assert shapes != icons.EXERCISE_NOTE_NAMES
    for lesson in installed:
        assert (
            lesson.icon == ""
            and lesson_icon(lesson) == exercise_icon(lesson.exercise) == shapes
        )
    assert (
        exercise_icon("NoteNames") == icons.EXERCISE_NOTE_NAMES
    )  # Alto's own exercises keep theirs
    own = replace(
        installed[0],
        icon="<circle cx='12' cy='12' r='5' fill='COLOR'/>",
    )
    assert lesson_icon(own) == own.icon


@pytest.mark.parametrize(
    ("svg", "message"),
    [
        (
            (
                "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 "
                "24'><script>x</script></svg>"
            ),
            "simple shapes",
        ),
        (
            (
                "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 "
                "24'><image href='x.png'/></svg>"
            ),
            "simple shapes",
        ),
        (
            (
                "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 "
                "24'><path d='M0 0' onload='x'/></svg>"
            ),
            "simple shapes",
        ),
        (
            (
                "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 "
                "24'><path style='fill:red' d='M0 0'/></svg>"
            ),
            "simple shapes",
        ),
        (
            (
                "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 "
                "100'><path d='M0 0'/></svg>"
            ),
            "viewBox",
        ),
        (
            (
                "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 "
                "24'></svg>"
            ),
            "no shapes",
        ),
        (
            (
                "<!DOCTYPE svg [<!ENTITY a 'b'>]><svg "
                "xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 "
                "24'><path d='M0 0'/></svg>"
            ),
            "entities",
        ),
        ("not xml", "Cannot read"),
    ],
)
def test_bad_icons_are_refused(tmp_path: Path, svg: str, message: str) -> None:
    """
    Refuse an icon that is not a plain SVG of simple shapes.

    Parameters
    ----------
    tmp_path : Path
        Isolated copy of the example pack.
    svg : str
        The icon file's text.
    message : str
        Part of the expected diagnostic.
    """

    def swap(manifest: dict) -> None:
        """
        Point the first exercise at the bad icon.

        Parameters
        ----------
        manifest : dict
            The parsed manifest, changed in place.
        """
        manifest["exercises"][0]["icon"] = "icons/bad.svg"

    path = _edited(tmp_path, edit=swap)
    (path.parent / "icons/bad.svg").write_text(svg)
    with pytest.raises(ValueError, match=message):
        read_pack(path)


def test_icons_must_be_files_in_the_plugin(tmp_path: Path) -> None:
    """
    Refuse an icon that is missing, is not a path, or has the wrong type
    of file.

    Parameters
    ----------
    tmp_path : Path
        Isolated copy of the example pack.
    """
    for value, message in (
        ("icons/nothing.svg", "Missing file"),
        (3, "path of an SVG"),
        ("images/viola-front.webp", "Use .svg"),
    ):
        with pytest.raises(ValueError, match=message):
            read_pack(
                _edited(
                    tmp_path / str(value).replace("/", "-"),
                    edit=lambda m, v=value: m["lessons"][0].update(icon=v),
                ),
            )


def _step_with_click(manifest: dict) -> dict:
    """
    Find the example's click question, whose step shows the head.

    Parameters
    ----------
    manifest : dict
        The parsed manifest.

    Returns
    -------
    dict
        The step.
    """
    step = manifest["lessons"][0]["steps"][1]
    assert "targets" in step["task"]
    return step


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        (
            lambda s: s.update(
                picture={"instrument": "bowed-viola", "point": [190, 280]},
            ),
            "marker set to false",
        ),
        (
            lambda s: s["task"].update(choices=["A", "B"], answer="A"),
            "not both",
        ),
        (lambda s: s["task"].update(targets=[]), "between 1 and 4 targets"),
        (
            lambda s: s["task"].update(
                targets=[{"point": [1, 1], "radius": 5}] * 5,
            ),
            "between 1 and 4 targets",
        ),
        (
            lambda s: s["task"].update(targets=[{"point": [1, 1]}]),
            "a point and a radius",
        ),
        (
            lambda s: s["task"].update(
                targets=[{"point": [1, 1], "radius": 0}],
            ),
            "positive number",
        ),
        (
            lambda s: s["task"].update(
                targets=[{"point": [1, 1], "radius": True}],
            ),
            "positive number",
        ),
        (
            lambda s: s["task"].update(
                targets=[{"point": [5000, 1], "radius": 5}],
            ),
            "outside",
        ),
        (lambda s: s["task"].pop("hint"), "these fields"),
    ],
)
def test_bad_click_questions_are_refused(
    tmp_path: Path,
    edit: Callable[[dict], None],
    message: str,
) -> None:
    """
    Refuse a click question whose picture shows its answer or whose
    targets are malformed.

    Parameters
    ----------
    tmp_path : Path
        Isolated copy of the example pack.
    edit : Callable[[dict], None]
        Damages the click step in place.
    message : str
        Part of the expected diagnostic.
    """
    with pytest.raises(ValueError, match=message):
        read_pack(_edited(tmp_path, edit=lambda m: edit(_step_with_click(m))))


def test_clicking_the_picture_answers_a_question(
    installed: list[Lesson],
    app: QApplication,
) -> None:
    """
    Take a real mouse click on the instrument picture as the answer,
    hint at a miss, and show the place after two misses.

    Parameters
    ----------
    installed : list of Lesson
        The lessons the plugin registered.
    app : QApplication
        Shared Qt application.
    """
    del app
    step = installed[0].steps[1]
    view = StepView(step, rng=random.Random(1))
    assert (
        view.picture is not None
        and view.task is not None
        and view.task.targets
        and not view.choice_buttons
    )
    view.resize(1100, 600)
    view.show()
    view.picture.grab()  # paint once, so the picture knows how it is laid out
    to_picture = view.picture._to_picture
    assert to_picture is not None
    centre, scale, source = to_picture

    def spot(x: float, y: float) -> QPoint:
        """
        Find where a point of the picture is on the widget.

        Parameters
        ----------
        x : float
            The point's x in the picture's pixels.
        y : float
            The point's y in the picture's pixels.

        Returns
        -------
        QPoint
            The place on the widget.
        """
        return QPointF(
            (x - source.x()) * scale + centre.x(),
            (y - source.y()) * scale + centre.y(),
        ).toPoint()

    assert view.picture.cursor().shape() == Qt.CursorShape.PointingHandCursor
    QTest.mouseClick(
        view.picture,
        Qt.MouseButton.LeftButton,
        pos=spot(450, 300),
    )  # beside the head
    assert (
        view._wrong == 1
        and "Not quite" in view.feedback.text()
        and view.again.isHidden()
    )
    QTest.mouseClick(
        view.picture,
        Qt.MouseButton.LeftButton,
        pos=spot(100, 385),
    )  # the scroll, not a peg
    assert (
        view._wrong == 2
        and "Here it is" in view.feedback.text()
        and view._done
    )
    assert view.picture._reveal is not None and not view.again.isHidden()
    assert view.picture.cursor().shape() == Qt.CursorShape.ArrowCursor
    QTest.mouseClick(
        view.picture,
        Qt.MouseButton.LeftButton,
        pos=spot(192, 282),
    )
    assert view._wrong == 2  # the question is over
    view.again.click()
    assert (
        view.picture._reveal is None
        and view.picture.cursor().shape() == Qt.CursorShape.PointingHandCursor
    )
    QTest.mouseClick(
        view.picture,
        Qt.MouseButton.LeftButton,
        pos=spot(231, 488),
    )
    assert "Right" in view.feedback.text() and view.picture._reveal is not None


def test_plugin_glossary_entries(
    installed: list[Lesson],
    app: QApplication,
) -> None:
    """
    List a plugin's glossary entries among Alto's own, show each with
    its picture, and link it to its lessons and exercises.

    Parameters
    ----------
    installed : list of Lesson
        The lessons the plugin registered.
    app : QApplication
        Shared Qt application.
    """
    del app
    assert {"scroll", "position", "open string", "f-holes"} <= set(
        PLUGIN_TERMS,
    )
    scroll = PLUGIN_TERMS["scroll"]
    assert (
        scroll.pack == "Viola Instrument Pack"
        and scroll.lessons == (PARTS,)
        and scroll.exercises == (REGISTRY[-1].__name__,)
    )
    page = GlossaryPage()
    names = [page.terms.item(row).text() for row in range(page.terms.count())]
    assert names == sorted(names, key=str.casefold) and {
        "scroll",
        "pitch",
        "staff",
    } <= set(names)
    page.search.setText("scroll")
    assert page.terms.currentItem().text() == "scroll"
    assert (
        "carved end" in page.definition.toPlainText()
        and not page.example_board.isHidden()
        and page.next_example.isHidden()
    )
    assert (
        page.example_board.position is not None
        and page.example_label.text() == "The scroll"
    )

    def tiles() -> list[TileCard]:
        """
        List the tiles now offered, leaving out any that are waiting to
        be deleted.

        Returns
        -------
        list of TileCard
            The tiles in the glossary's activity grid.
        """
        found = (
            page.activity_tiles.itemAt(i).widget()
            for i in range(page.activity_tiles.count())
        )
        return [widget for widget in found if isinstance(widget, TileCard)]

    page._show_activities(1)
    assert [card.accessibleName().split(",")[0] for card in tiles()] == [
        installed[0].title,
    ]
    asked = []
    page.lesson_requested.connect(asked.append)
    tiles()[0].click()
    assert asked == [PARTS]
    page._show_activities(0)
    assert len(tiles()) == 1
    page.search.setText(
        "position",
    )  # an entry with no picture shows no example
    assert (
        page.demo.isHidden()
        and "first position" in page.definition.toPlainText()
    )
    page.search.setText("pitch")  # built-in entries still show their notation
    assert (
        not page.demo.isHidden()
        and not page.next_example.isHidden()
        and page.example_board.isHidden()
    )


def test_a_plugin_term_that_matches_alto_s_is_labeled(
    installed: list[Lesson],
    app: QApplication,
) -> None:
    """
    Keep a plugin's term apart from a built-in term with the same name
    by adding the plugin's name.

    Parameters
    ----------
    installed : list of Lesson
        The lessons the plugin registered.
    app : QApplication
        Shared Qt application.
    """
    del installed, app
    PLUGIN_TERMS["staff"] = PluginTerm(
        name="staff",
        pack="Viola Instrument Pack",
        definition="The viola's staff.",
    )
    page = GlossaryPage()
    names = [page.terms.item(row).text() for row in range(page.terms.count())]
    assert "staff" in names and "staff (Viola Instrument Pack)" in names
    page.search.setText("Viola Instrument")
    assert (
        page.definition.toPlainText().startswith("staff")
        and "viola's staff" in page.definition.toPlainText()
    )


def test_a_second_plugin_cannot_take_a_term(tmp_path: Path) -> None:
    """
    Skip a plugin that supplies a glossary term another plugin already
    supplies, and say why.

    Parameters
    ----------
    tmp_path : Path
        Isolated plugins folder.
    """
    shutil.copytree(VIOLA.parent, tmp_path / "viola")
    other = tmp_path / "other"
    shutil.copytree(VIOLA.parent, other)
    manifest = json.loads((other / "pack.json").read_text())
    manifest["id"] = "other-viola"
    (other / "pack.json").write_text(json.dumps(manifest))
    problems = load_packs(tmp_path)
    assert (
        len(problems) == 1
        and "glossary term" in problems[0]
        and "already supplied" in problems[0]
    )


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        (lambda m: m.update(glossary=[]), "between 1 and 40"),
        (
            lambda m: m.update(glossary=["scroll"]),
            "takes a term and a definition",
        ),
        (lambda m: m["glossary"][0].update(colour="red"), "only these fields"),
        (
            lambda m: m["glossary"][0].pop("definition"),
            "takes a term and a definition",
        ),
        (
            lambda m: m["glossary"][1].update(term=m["glossary"][0]["term"]),
            "appears twice",
        ),
        (
            lambda m: m["glossary"][0].update(term="<b>x</b>"),
            "plain-text term",
        ),
        (
            lambda m: m["glossary"][0].update(definition="x" * 501),
            "at most 500",
        ),
        (
            lambda m: m["glossary"][1].update(exercises=["nothing"]),
            "must be one of this plugin's exercises",
        ),
        (
            lambda m: m["glossary"][1].update(lessons=["nothing"]),
            "must be one of this plugin's lessons",
        ),
        (
            lambda m: m["glossary"][1].update(lessons=["finding-notes"] * 2),
            "up to five distinct lessons",
        ),
        (
            lambda m: m["glossary"][1].update(
                picture={
                    "instrument": "bowed-viola",
                    "string": "D4",
                    "note": "E4",
                },
            ),
            "not a note on a string",
        ),
        (
            lambda m: m["glossary"][1]["picture"].update(point=[-1, 0]),
            "outside",
        ),
    ],
)
def test_bad_glossary_entries_are_refused(
    tmp_path: Path,
    edit: Callable[[dict], None],
    message: str,
) -> None:
    """
    Refuse a glossary that is malformed or links to something the plugin
    does not declare.

    Parameters
    ----------
    tmp_path : Path
        Isolated copy of the example pack.
    edit : Callable[[dict], None]
        Damages the parsed manifest in place.
    message : str
        Part of the expected diagnostic.
    """
    with pytest.raises(ValueError, match=message):
        read_pack(_edited(tmp_path, edit=edit))
