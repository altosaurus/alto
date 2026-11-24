"""
Turn the lessons that an instrument plugin declares into `Lesson`s that
Alto lists and shows.

A plugin describes each lesson in its manifest as plain text and small
objects: paragraphs, an optional picture of its own
instrument, notes to hear, and a question with buttons. This module
checks all of that and builds the same `Lesson` and `Step`
objects the built-in lessons use, so the lesson pages need to know
nothing about any particular plugin or instrument.

Examples
--------
>>> inline("A **scroll** is the carved end.")
'A <b>scroll</b> is the carved end.'
"""

from __future__ import annotations

import html
import random
import re
from collections.abc import Mapping
from dataclasses import replace
from functools import partial

from alto.exercises.base import (
    FingerboardPosition,
    PicturePosition,
)
from alto.instrument_packs import (
    PackInstrument,
    identifier,
    image_point,
    pitch,
    read_focus,
    read_marker_size,
    read_text,
)
from alto.lessons.base import (
    Lesson,
    Step,
    Task,
)

LESSON_LIMIT = 6  # lessons in one plugin
STEP_LIMIT = 14  # steps in one lesson
PARAGRAPH_LIMIT = 8  # paragraphs in one step
STEP_KEYS = {
    "title",
    "text",
    "picture",
    "hear",
    "hear_label",
    "hear_instrument",
    "task",
}
LESSON_KEYS = {
    "id",
    "title",
    "about",
    "summary",
    "category",
    "exercise",
    "related_exercises",
    "icon",
    "steps",
}
TASK_KEYS = {
    "prompt",
    "hint",
    "explanation",
}  # and either choices with an answer, or targets to click
TARGET_LIMIT = 4  # right places in a click question
FINGERBOARD_KEYS = {"instrument", "string", "note"}
PICTURE_KEYS = {
    "instrument",
    "point",
    "marker_size",
    "focus",
    "marker",
    "view",
}
KEY_LIMIT = 4  # keys highlighted in one picture


def inline(text: str) -> str:
    """
    Escape plain text for a lesson page, turning ``**word**`` into bold
    type for a term being defined.

    Parameters
    ----------
    text : str
        Plain text from a manifest.

    Returns
    -------
    str
        Simple HTML.

    Examples
    --------
    >>> inline("The **nut** & the bridge.")
    'The <b>nut</b> &amp; the bridge.'
    """
    return re.sub(
        r"\*\*(.+?)\*\*",
        r"<b>\1</b>",
        html.escape(text, quote=False),
    )


def read_lessons(
    value: object,
    *,
    pack_id: str,
    pack_name: str,
    instruments: Mapping[str, PackInstrument],
    exercises: Mapping[str, str],
    icons: Mapping[str, str] | None = None,
) -> tuple[Lesson, ...]:
    """
    Validate the optional ``lessons`` list of a plugin manifest and
    build its lessons.

    Parameters
    ----------
    value : object
        The manifest's ``lessons`` entry, or None when the plugin has no
        lessons.
    pack_id : str
        The plugin's id, which qualifies each lesson's key.
        Keyword-only.
    pack_name : str
        The plugin's display name, used as a lesson's category when it
        names none. Keyword-only.
    instruments : mapping of str to PackInstrument
        The plugin's instruments by qualified key, which pictures and
        sounds refer to. Keyword-only.
    exercises : mapping of str to str
        The plugin's exercises, from the id the manifest uses to the key
        Alto registers it under. Keyword-only.
    icons : mapping of str to str or None, default None
        The plugin's icons by the file name the manifest uses, already
        read. Keyword-only.

    Returns
    -------
    tuple of Lesson
        The lessons, in the order the manifest lists them.

    Raises
    ------
    ValueError
        If a lesson, step, picture, or question is malformed, or refers
        to something the plugin does not declare.

    Examples
    --------
    >>> read_lessons(
    ...     None,
    ...     pack_id="demo",
    ...     pack_name="Demo",
    ...     instruments={},
    ...     exercises={},
    ... )
    ()
    """
    if value is None:
        return ()
    if not isinstance(value, list) or not value or len(value) > LESSON_LIMIT:
        raise ValueError(f"List between 1 and {LESSON_LIMIT} lessons.")
    lessons: list[Lesson] = []
    for row in value:
        lesson = _read_lesson(
            row,
            pack_id=pack_id,
            pack_name=pack_name,
            instruments=instruments,
            exercises=exercises,
            icons=icons or {},
        )
        if any(earlier.key == lesson.key for earlier in lessons):
            raise ValueError(f"Duplicate lesson id {lesson.key}.")
        lessons.append(lesson)
    return tuple(lessons)


def _read_lesson(
    row: object,
    *,
    pack_id: str,
    pack_name: str,
    instruments: Mapping[str, PackInstrument],
    exercises: Mapping[str, str],
    icons: Mapping[str, str],
) -> Lesson:
    """
    Build one lesson from its manifest entry.

    Parameters
    ----------
    row : object
        The lesson's manifest object.
    pack_id : str
        The plugin's id. Keyword-only.
    pack_name : str
        The plugin's display name. Keyword-only.
    instruments : mapping of str to PackInstrument
        The plugin's instruments by qualified key. Keyword-only.
    exercises : mapping of str to str
        The plugin's exercises, from manifest id to registered key.
        Keyword-only.
    icons : mapping of str to str
        The plugin's icons by file name. Keyword-only.

    Returns
    -------
    Lesson
        The lesson, whose last step offers practice.

    Raises
    ------
    ValueError
        If anything in it is malformed.
    """
    if not isinstance(row, dict) or set(row) - LESSON_KEYS:
        raise ValueError(
            "Each lesson takes only these fields: "
            f"{', '.join(sorted(LESSON_KEYS))}"
            ".",
        )
    key = f"pack.{pack_id}.{identifier(row.get('id'))}"
    where = f"lesson {key}"
    title = read_text(row.get("title"), limit=80, what="title", where=where)
    about = read_text(
        row.get("about"),
        limit=300,
        what="about line",
        where=where,
    )
    summary = read_text(
        row.get("summary"),
        limit=120,
        what="summary",
        where=where,
    )
    category = read_text(
        row.get("category", pack_name),
        limit=40,
        what="category",
        where=where,
    )
    named = row.get("exercise")
    exercise = exercises.get(named) if isinstance(named, str) else None
    if exercise is None:
        raise ValueError(
            "Set the exercise of "
            f"{where}"
            " to the id of one of this plugin's exercises.",
        )
    related_ids = row.get("related_exercises", [])
    if (
        not isinstance(related_ids, list)
        or len(related_ids) > 5
        or len(set(related_ids)) != len(related_ids)
    ):
        raise ValueError(
            f"List up to five distinct related_exercises for {where}.",
        )
    related = []
    for item in related_ids:
        if (
            not isinstance(item, str)
            or item not in exercises
            or exercises[item] == exercise
        ):
            raise ValueError(
                "Each related exercise of "
                f"{where}"
                " must be a different exercise from this plugin.",
            )
        related.append(exercises[item])
    icon = ""
    if "icon" in row:
        if row["icon"] not in icons:
            raise ValueError(
                f"Set the icon of {where} to an SVG file in the plugin.",
            )
        icon = icons[row["icon"]]
    steps = row.get("steps")
    if not isinstance(steps, list) or not steps or len(steps) > STEP_LIMIT:
        raise ValueError(f"Give {where} between 1 and {STEP_LIMIT} steps.")
    built = [
        _read_step(
            step,
            where=f"{where}, step {number}",
            pack_id=pack_id,
            instruments=instruments,
        )
        for number, step in enumerate(steps, 1)
    ]
    built[-1] = replace(built[-1], closing=True)
    return Lesson(
        key=key,
        title=title,
        about=about,
        summary=summary,
        category=category,
        steps=tuple(built),
        exercise=exercise,
        related_exercises=tuple(related),
        icon=icon,
    )


def _given(task: Task, _rng: random.Random) -> Task:
    """
    Offer the same question each time, since a plugin writes its
    knowledge checks out in full.

    Parameters
    ----------
    task : Task
        The question the plugin wrote.
    _rng : random.Random
        The generator a built-in lesson would use to vary its question.
        Not used here.

    Returns
    -------
    Task
        The same question.

    Examples
    --------
    >>> question = Task(
    ...     prompt="?",
    ...     hint="",
    ...     explanation="",
    ...     choices=("A", "B"),
    ...     correct="A",
    ... )
    >>> _given(
    ...     question, random.Random(1)
    ... ) is question
    True
    """
    return task


def _read_step(
    step: object,
    *,
    where: str,
    pack_id: str,
    instruments: Mapping[str, PackInstrument],
) -> Step:
    """
    Build one step from its manifest entry.

    Parameters
    ----------
    step : object
        The step's manifest object.
    where : str
        Which lesson and step this is, for messages. Keyword-only.
    pack_id : str
        The plugin's id. Keyword-only.
    instruments : mapping of str to PackInstrument
        The plugin's instruments by qualified key. Keyword-only.

    Returns
    -------
    Step
        The step.

    Raises
    ------
    ValueError
        If anything in it is malformed.
    """
    if not isinstance(step, dict) or set(step) - STEP_KEYS:
        raise ValueError(
            "Each step takes only these fields: "
            f"{', '.join(sorted(STEP_KEYS))}"
            " ("
            f"{where}"
            ").",
        )
    title = read_text(step.get("title"), limit=80, what="title", where=where)
    paragraphs = step.get("text")
    if (
        not isinstance(paragraphs, list)
        or not paragraphs
        or len(paragraphs) > PARAGRAPH_LIMIT
    ):
        raise ValueError(
            "Give "
            f"{where}"
            " between 1 and "
            f"{PARAGRAPH_LIMIT}"
            " paragraphs of text.",
        )
    text = "".join(
        "<p>"
        f"{inline(read_text(p, limit=700, what='paragraph', where=where))}"
        "</p>"
        for p in paragraphs
    )
    picture = (
        read_picture(
            step["picture"],
            where=where,
            pack_id=pack_id,
            instruments=instruments,
        )
        if "picture" in step
        else None
    )
    hear: list[tuple[str, ...]] = []
    if "hear" in step:
        columns = step["hear"]
        if not isinstance(columns, list) or not columns or len(columns) > 12:
            raise ValueError(
                "Give hear in "
                f"{where}"
                " as a list of up to 12 chords, each a list of note names.",
            )
        for column in columns:
            if not isinstance(column, list) or not column or len(column) > 4:
                raise ValueError(
                    "Give each chord of hear in "
                    f"{where}"
                    " as a list of one to four note names.",
                )
            for name in column:
                pitch(name)
            hear.append(tuple(column))
    hear_label = read_text(
        step.get("hear_label", "Hear it"),
        limit=60,
        what="hear_label",
        where=where,
    )
    hear_instrument = ""
    if "hear_instrument" in step:
        hear_instrument = (
            f"pack.{pack_id}.{identifier(step['hear_instrument'])}"
        )
        model = instruments.get(hear_instrument)
        if model is None or model.sound is None:
            raise ValueError(
                "Set hear_instrument in "
                f"{where}"
                " to an instrument of this plugin that has samples.",
            )
    task = (
        _read_task(
            step["task"],
            where=where,
            picture=picture,
            instruments=instruments,
        )
        if "task" in step
        else None
    )
    return Step(
        title=title,
        text=text,
        hear=tuple(hear),
        hear_label=hear_label,
        make_task=partial(_given, task) if task is not None else None,
        picture=picture,
        hear_instrument=hear_instrument,
    )


def read_picture(
    spec: object,
    *,
    where: str,
    pack_id: str,
    instruments: Mapping[str, PackInstrument],
) -> PicturePosition | FingerboardPosition:
    """
    Build a step's instrument picture: a note on a string, or a marked
    place on the picture.

    Parameters
    ----------
    spec : object
        The picture's manifest object. Give ``string`` and ``note`` for
        a note on a string, or ``point`` for a place.
    where : str
        Which lesson and step this is, for messages. Keyword-only.
    pack_id : str
        The plugin's id. Keyword-only.
    instruments : mapping of str to PackInstrument
        The plugin's instruments by qualified key. Keyword-only.

    Returns
    -------
    PicturePosition or FingerboardPosition
        What the step's picture shows.

    Raises
    ------
    ValueError
        If the picture is malformed or refers to something the plugin
        does not declare.
    """
    if not isinstance(spec, dict):
        raise ValueError(f"Give the picture in {where} as an object.")
    key = f"pack.{pack_id}.{identifier(spec.get('instrument'))}"
    model = instruments.get(key)
    if model is None:
        raise ValueError(
            f"Unknown instrument {key} in the picture of {where}.",
        )
    if "string" in spec or "note" in spec:
        if (
            set(spec) - FINGERBOARD_KEYS
            or "string" not in spec
            or "note" not in spec
        ):
            raise ValueError(
                "Give a note on a string as instrument, string, and note "
                "only ("
                f"{where}"
                ").",
            )
        names = tuple(string.pitch for string in model.strings)
        if spec["string"] not in names:
            raise ValueError(
                "Set string in "
                f"{where}"
                " to one of "
                f"{', '.join(names) or 'no strings'}"
                ".",
            )
        steps = pitch(spec["note"]).midi - pitch(spec["string"]).midi
        if not 0 <= steps <= 36:
            raise ValueError(
                "Choose a note in "
                f"{where}"
                " from the open string up to three octaves above it.",
            )
        return FingerboardPosition(
            names,
            names.index(spec["string"]),
            spec["note"],
            key,
        )
    if "keys" in spec:
        return _read_keys(spec, where=where, key=key, model=model)
    if set(spec) - PICTURE_KEYS:
        raise ValueError(
            "A picture takes only these fields: "
            f"{', '.join(sorted(PICTURE_KEYS))}"
            " ("
            f"{where}"
            ").",
        )
    marker = spec.get("marker", True)
    if not isinstance(marker, bool):
        raise ValueError(f"Set marker in {where} to true or false.")
    view = spec.get("view", "")
    found = model.picture(view) if isinstance(view, str) else None
    if found is None:
        raise ValueError(
            "Set view in "
            f"{where}"
            " to the name of one of this instrument's views, or leave it "
            "out.",
        )
    width, height = found[1]
    if "point" not in spec and marker:
        raise ValueError(
            f"Give the picture in {where} a point, or set marker to false.",
        )
    point = (
        image_point(spec["point"], width=width, height=height)
        if "point" in spec
        else (width / 2, height / 2)
    )
    focus: tuple[float, ...] = ()
    if "focus" in spec:
        focus = read_focus(spec["focus"], width=width, height=height)
        left, top, span_x, span_y = focus
        if marker and not (
            left <= point[0] <= left + span_x
            and top <= point[1] <= top + span_y
        ):
            raise ValueError(
                f"Keep the marked point inside the focus region in {where}.",
            )
    return PicturePosition(
        key,
        point,
        "",
        read_marker_size(spec.get("marker_size", 0)),
        focus,
        marker,
        view,
    )


def _read_keys(
    spec: dict,
    *,
    where: str,
    key: str,
    model: PackInstrument,
) -> PicturePosition:
    """
    Build a step's picture of highlighted keys, drawn on the
    instrument's keyboards.

    Parameters
    ----------
    spec : dict
        The picture's manifest object, with ``keys`` as a list of a
        keyboard's name and a pitch, and an optional ``span``,
        the lowest and highest key to draw.
    where : str
        Which lesson and step this is, for messages. Keyword-only.
    key : str
        The instrument's qualified key. Keyword-only.
    model : PackInstrument
        The instrument, which supplies the keyboards. Keyword-only.

    Returns
    -------
    PicturePosition
        The picture. Alto draws the keyboards instead of the
        instrument's photograph.

    Raises
    ------
    ValueError
        If a key, a keyboard or the span is not valid.

    Examples
    --------
    A step can show C4 and E4 on the lower manual to introduce a third.
    """
    if set(spec) - {"instrument", "keys", "span"}:
        raise ValueError(
            "A picture of keys takes only instrument, keys and span ("
            f"{where}"
            ").",
        )
    rows = spec["keys"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= KEY_LIMIT:
        raise ValueError(
            "Give the keys in "
            f"{where}"
            " as a list of one to "
            f"{KEY_LIMIT}"
            " keys, each a keyboard name and a pitch.",
        )
    keys = []
    for row in rows:
        if (
            not isinstance(row, list)
            or len(row) != 2
            or not all(isinstance(text, str) for text in row)
        ):
            raise ValueError(
                f"Write each key in {where} as [keyboard name, pitch].",
            )
        board = model.keyboard(row[0])
        if board is None or not board.has(row[1]):
            raise ValueError(f"{row[0]!r} has no key {row[1]!r} ({where}).")
        keys.append((row[0], row[1]))
    span: tuple[str, ...] = ()
    if "span" in spec:
        ends = spec["span"]
        if not isinstance(ends, list) or len(ends) != 2:
            raise ValueError(
                "Give the span in "
                f"{where}"
                " as the lowest and the highest key to draw.",
            )
        low, high = pitch(ends[0]), pitch(ends[1])
        if low.midi >= high.midi:
            raise ValueError(
                "Put the lowest key of the span in "
                f"{where}"
                " below its highest key.",
            )
        span = (ends[0], ends[1])
    return PicturePosition(
        key,
        (0.0, 0.0),
        "",
        0.0,
        (),
        False,
        "",
        tuple(keys),
        (),
        span,
    )


def _read_task(
    spec: object,
    *,
    where: str,
    picture: PicturePosition | FingerboardPosition | None = None,
    instruments: Mapping[str, PackInstrument] | None = None,
) -> Task:
    """
    Build a step's knowledge check: a question with buttons and what to
    say after each answer.

    Parameters
    ----------
    spec : object
        The task's manifest object.
    where : str
        Which lesson and step this is, for messages. Keyword-only.
    picture : PicturePosition or FingerboardPosition or None
        The step's instrument picture, which a click question is
        answered on. Keyword-only.
    instruments : mapping of str to PackInstrument or None, default None
        The plugin's instruments by qualified key. Keyword-only.

    Returns
    -------
    Task
        The question: with buttons to press, or with places to click on
        the picture.

    Raises
    ------
    ValueError
        If it is malformed.

    Examples
    --------
    >>> task = _read_task(
    ...     {
    ...         "prompt": "Which?",
    ...         "choices": ["A", "B"],
    ...         "answer": "B",
    ...         "hint": "Look again.",
    ...         "explanation": "It is B.",
    ...     },
    ...     where="demo",
    ... )
    >>> task.check("B"), task.check("A")
    (True, False)
    """
    if (
        not isinstance(spec, dict)
        or not TASK_KEYS <= set(spec)
        or set(spec) - TASK_KEYS - {"choices", "answer", "targets"}
    ):
        raise ValueError(
            "Give the task in "
            f"{where}"
            " these fields: "
            f"{', '.join(sorted(TASK_KEYS))}"
            ", and choices with answer or targets.",
        )
    if "targets" in spec:
        if "choices" in spec or "answer" in spec:
            raise ValueError(
                "Give the task in "
                f"{where}"
                " either choices with an answer, or targets to click, not "
                "both.",
            )
        return Task(
            prompt=inline(
                read_text(
                    spec["prompt"],
                    limit=200,
                    what="prompt",
                    where=where,
                ),
            ),
            hint=inline(
                read_text(spec["hint"], limit=200, what="hint", where=where),
            ),
            explanation=inline(
                read_text(
                    spec["explanation"],
                    limit=300,
                    what="explanation",
                    where=where,
                ),
            ),
            targets=_read_targets(
                spec["targets"],
                where=where,
                picture=picture,
                instruments=instruments or {},
            ),
        )
    if "choices" not in spec or "answer" not in spec:
        raise ValueError(
            "Give the task in "
            f"{where}"
            " choices with an answer, or targets to click.",
        )
    choices = spec["choices"]
    if (
        not isinstance(choices, list)
        or not 2 <= len(choices) <= 6
        or len(set(choices)) != len(choices)
    ):
        raise ValueError(
            f"Give the task in {where} two to six distinct choices.",
        )
    labels = [
        read_text(choice, limit=60, what="choice", where=where)
        for choice in choices
    ]
    answer = spec["answer"]
    if answer not in labels:
        raise ValueError(
            "The answer of the task in "
            f"{where}"
            " must match one of its choices exactly.",
        )
    return Task(
        prompt=inline(
            read_text(spec["prompt"], limit=200, what="prompt", where=where),
        ),
        hint=inline(
            read_text(spec["hint"], limit=200, what="hint", where=where),
        ),
        explanation=inline(
            read_text(
                spec["explanation"],
                limit=300,
                what="explanation",
                where=where,
            ),
        ),
        choices=tuple(labels),
        correct=answer,
    )


def _read_targets(
    value: object,
    *,
    where: str,
    picture: PicturePosition | FingerboardPosition | None,
    instruments: Mapping[str, PackInstrument],
) -> tuple[tuple[float, float, float], ...]:
    """
    Check the places a click question accepts, which are measured on the
    step's picture.

    Parameters
    ----------
    value : object
        The task's ``targets``: a short list of objects with a ``point``
        and a ``radius``.
    where : str
        Which lesson and step this is, for messages. Keyword-only.
    picture : PicturePosition or FingerboardPosition or None
        The step's picture. It must be a picture without a marker, so
        the answer is not shown. Keyword-only.
    instruments : mapping of str to PackInstrument
        The plugin's instruments by qualified key. Keyword-only.

    Returns
    -------
    tuple of tuple of (float, float, float)
        Each place as x, y and radius in the picture's pixels.

    Raises
    ------
    ValueError
        If the step has no suitable picture, or a place is malformed or
        outside the picture.

    Examples
    --------
    >>> _read_targets(
    ...     [],
    ...     where="demo",
    ...     picture=None,
    ...     instruments={},
    ... )
    Traceback (most recent call last):
    ...
    ValueError: A click question in demo needs the step to show an
    instrument picture with marker set to false.
    """
    if not isinstance(picture, PicturePosition) or picture.marker:
        raise ValueError(
            "A click question in "
            f"{where}"
            " needs the step to show an instrument picture with marker set"
            " to false.",
        )
    found = instruments[picture.instrument].picture(picture.view)
    assert (
        found is not None
    )  # the picture was checked against the same instrument
    width, height = found[1]
    if not isinstance(value, list) or not 1 <= len(value) <= TARGET_LIMIT:
        raise ValueError(
            "Give the click question in "
            f"{where}"
            " between 1 and "
            f"{TARGET_LIMIT}"
            " targets.",
        )
    targets = []
    for target in value:
        if not isinstance(target, dict) or set(target) != {"point", "radius"}:
            raise ValueError(
                f"Give each target in {where} a point and a radius.",
            )
        x, y = image_point(target["point"], width=width, height=height)
        radius = target["radius"]
        if (
            isinstance(radius, bool)
            or not isinstance(radius, (int, float))
            or not 0 < radius <= min(width, height)
        ):
            raise ValueError(
                "Give each target radius in "
                f"{where}"
                " as a positive number of picture pixels.",
            )
        targets.append((x, y, float(radius)))
    return tuple(targets)
