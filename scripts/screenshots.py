#!/usr/bin/env python
"""
Regenerate the screenshots in docs/assets/img, in the light and the dark theme.

    .venv/bin/python scripts/screenshots.py              # every picture, both themes
    .venv/bin/python scripts/screenshots.py --only home stats
    .venv/bin/python scripts/screenshots.py --theme dark --out /tmp/shots

Each picture is written as name.png (light) and name-dark.png. The docs page picks the right one with the theme
toggle, so both must exist. The script runs against a throwaway profile with made-up answers, and a temporary
settings and data folder, so it never reads or changes your own profile, history or settings.

It needs a display or Qt's offscreen platform (QT_QPA_PLATFORM=offscreen). Fonts are rendered a little differently
on each machine, so regenerate on the machine you normally use and check the pictures before committing them.

Never add a picture of the exercise-level settings (the pane behind the sliders button) here. See CLAUDE.md.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

import argparse
import json
import os
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QScrollArea,
)

import alto.ui.exercise_view as ev
from alto import settings
from alto.audio import sounds
from alto.exercises import REGISTRY
from alto.exercises.base import Question
from alto.exercises.library import ClefBasics, KeyboardNotes, NoteNames
from alto.learning import (
    Database,
    Learner,
)
from alto.learning.calendar import UNLIMITED
from alto.ui.app_settings import AppSettingsDialog
from alto.ui.database_page import (
    ROW_ROLE,
    DatabasePage,
)
from alto.ui.glossary import GlossaryPage
from alto.ui.main_window import MainWindow
from alto.ui.profile_dialog import ProfileDialog
from alto.ui.question_preview import QuestionPreview
from alto.ui.stats_dialog import StatsPage
from alto.ui.store import store
from alto.ui.theme import apply_theme

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "assets" / "img"
THEMES = ("light", "dark")
# The pictures this script makes. A docs page includes each of them with shot.html.
SHOTS = (
    "profile-create",
    "profile-picker",
    "home",
    "lesson-tiles",
    "lesson-workspace",
    "glossary",
    "note-identification",
    "keyboard",
    "note-construction",
    "intervals",
    "scales",
    "chords",
    "notation",
    "arpeggios",
    "key-signatures",
    "circle-of-fifths",
    "filtered-practice",
    "filtered-exercise",
    "keyboard-review",
    "self-grading",
    "waiting-for-review",
    "practice-settings",
    "database-questions",
    "stats",
    "stats-heatmap",
    "database",
    "question-preview",
    "settings",
    "settings-sound",
)


def main() -> int:
    """
    Parse the command line and make the pictures, one process for each theme.

    Returns
    -------
    int
        0 if every picture was written, 1 if a capture failed.

    Examples
    --------
    >>> main()  # doctest: +SKIP
    wrote 26 pictures to docs/assets/img
    0
    """
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--theme", choices=THEMES, help="only this theme (default: both)")
    ap.add_argument(
        "--only",
        nargs="+",
        choices=SHOTS,
        metavar="NAME",
        help=f"only these pictures: {', '.join(SHOTS)}",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=OUT,
        help="folder to write to (default: docs/assets/img)",
    )
    args = ap.parse_args()
    names = tuple(args.only or SHOTS)
    args.out.mkdir(parents=True, exist_ok=True)
    if args.theme:
        capture(args.theme, names=names, out=args.out)
        return 0
    # One process for each theme, each with its own throwaway settings and data folder.
    for theme in THEMES:
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, XDG_CONFIG_HOME=f"{tmp}/config", XDG_DATA_HOME=f"{tmp}/data")
            env.setdefault("QT_QPA_PLATFORM", "xcb" if os.environ.get("DISPLAY") else "offscreen")
            cmd = [
                sys.executable,
                str(Path(__file__).resolve()),
                "--theme",
                theme,
                "--out",
                str(args.out),
                "--only",
                *names,
            ]
            if subprocess.run(cmd, env=env, cwd=ROOT).returncode:
                return 1
    print(f"wrote {len(names) * len(THEMES)} pictures to {args.out}")
    return 0


def capture(
    theme: str,
    *,
    names: tuple[str, ...],
    out: Path,
) -> None:
    """
    Take the pictures of one theme, in this process, using a made-up profile.

    Parameters
    ----------
    theme : str
        "light" or "dark".
    names : tuple of str
        The pictures to make, from `SHOTS`.
    out : Path
        The folder to write them to.

    Examples
    --------
    >>> capture("dark", names=("home",), out=Path("/tmp/shots"))  # doctest: +SKIP
    """
    suffix = "" if theme == "light" else "-dark"
    app = QApplication([])
    apply_theme(theme)
    app.processEvents()
    if (app.palette().window().color().lightness() < 128) != (theme == "dark"):
        # Some platform plugins, including offscreen, ignore Qt's native color-scheme request.
        apply_theme("studio_dark" if theme == "dark" else "studio")

    original = ev.ExerciseView.__init__
    # noinspection PyShadowingNames
    ev.ExerciseView.__init__ = lambda self, exercise, *, rng=None, parent=None, learner=None: original(
        self,
        exercise,
        rng=random.Random(5),
        parent=parent,
        learner=learner,
    )

    def wait(ms: int = 450) -> None:
        """
        Keep the application busy for a while, so animations and layout settle.

        Parameters
        ----------
        ms : int
            How many milliseconds to run the event loop.

        Examples
        --------
        >>> wait(250)  # doctest: +SKIP
        """
        end = time.time() + ms / 1000
        while time.time() < end:
            app.processEvents()

    # noinspection PyShadowingNames
    def save(
        widget: QWidget,
        *,
        name: str,
        width: int = 1400,
    ) -> None:
        """
        Save a picture of a widget, if this picture was asked for.

        Parameters
        ----------
        widget : QWidget
            The widget to grab.
        name : str
            The picture's name; it is skipped unless it is in `names`.
        width : int
            The widest the picture may be; wider ones are scaled down.

        Raises
        ------
        RuntimeError
            If the captured window uses the wrong theme.

        Examples
        --------
        >>> save(window, name="home")  # doctest: +SKIP
        """
        if name not in names:
            return
        wait(250)
        pixmap = widget.grab()
        if (pixmap.toImage().pixelColor(10, 10).lightness() < 128) != (theme == "dark"):
            raise RuntimeError(f"The {name} window did not render in the requested {theme} theme.")
        if pixmap.width() > width:
            pixmap = pixmap.scaledToWidth(width, Qt.TransformationMode.SmoothTransformation)
        pixmap.save(str(out / f"{name}{suffix}.png"), "PNG")

    # A made-up profile: five weeks of answers that slowly get better, after about a year of lighter practice.
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    rng = random.Random(11)
    now = time.time()
    for day in range(34, -1, -1):
        if rng.random() < 0.3:
            continue
        for _ in range(rng.randint(8, 28)):
            ex = rng.choice(REGISTRY)()
            q = ex.generate(rng)
            t, attempt = now - day * 86400 - rng.randint(0, 20000), 1
            accuracy = min(0.95, 0.55 + (34 - day) * 0.011)
            seconds = max(0.7, rng.gauss(ex.par_seconds * (1.7 - (34 - day) * 0.018), 1))
            while True:
                ok = rng.random() < accuracy if attempt == 1 else True
                learner.record(
                    ex,
                    question=q,
                    answer=q.answer if ok else "?",
                    correct=ok,
                    attempt_no=attempt,
                    seconds=seconds,
                    now=t + attempt * 5,
                )
                if ok:
                    break
                attempt += 1
                seconds = rng.uniform(1, 4)
    # The year before that, from its own generator so the recent weeks above come out the same as ever: mostly short
    # sessions on a few days a week, with a lull in the summer, which is what a real heatmap looks like.
    old = random.Random(12)
    for day in range(364, 34, -1):
        month = time.localtime(now - day * 86400).tm_mon
        chance = 0.22 if month in (6, 7) else 0.55
        if old.random() > chance:
            continue
        for _ in range(
            old.choice(
                (
                    3,
                    6,
                    10,
                    14,
                    20,
                    28,
                    38,
                ),
            ),
        ):
            ex = old.choice(REGISTRY)()
            q = ex.generate(old)
            t = now - day * 86400 - old.randint(0, 20000)
            ok = old.random() < 0.5 + 0.3 * (364 - day) / 330
            learner.record(
                ex,
                question=q,
                answer=q.answer if ok else "?",
                correct=ok,
                attempt_no=1,
                seconds=max(0.7, old.gauss(ex.par_seconds * 1.5, 1)),
                now=t,
            )

    store().setValue("ui/sidebarWidth", 330)  # wide enough for the longest exercise name, so that none is cut off in a picture
    window = MainWindow(learner)
    window.resize(1100, 720)
    window.show()
    wait()
    save(window, name="home")
    by_class = {c.__name__: c for c in REGISTRY}
    for cls, name in (
        ("NoteNames", "note-identification"),
        ("KeyboardNotes", "keyboard"),
        ("NoteConstruction", "note-construction"),
        ("IntervalNames", "intervals"),
        ("ScaleIdentification", "scales"),
        ("ChordQualities", "chords"),
        ("NotationIdentification", "notation"),
        ("ArpeggioNames", "arpeggios"),
        ("KeySignatures", "key-signatures"),
        ("CircleOfFifths", "circle-of-fifths"),
    ):
        if cls == "NotationIdentification":
            settings.notation.terms = {"Clef", "Notehead", "Stem", "Flag"}
        if cls == "KeySignatures":  # show a signature on an alto clef staff, whatever the default is
            settings.key_signatures.clefs = {"alto"}
            settings.key_signatures.modes = {"Major (Ionian)"}
            settings.key_signatures.keys = {-3}  # three flats, so there is something to read
        window.open_exercise(by_class[cls])
        wait(500)
        save(window, name=name)
    window.show_home()
    wait()
    # A few recent FSRS answers give the calendar controls actual new, missed, and due cards.
    learner.set_mode("FSRS")
    for ex in (NoteNames(), KeyboardNotes()):
        for minutes_ago, correct in ((25, True), (15, False), (2, True)):
            question = ex.generate(rng)
            learner.record(
                ex,
                question=question,
                answer=question.answer if correct else "Incorrect",
                correct=correct,
                attempt_no=1,
                seconds=3.1,
                now=now - minutes_ago * 60,
            )

    window.open_stats()
    wait(400)
    stats_page = window._overlay
    assert isinstance(stats_page, StatsPage)
    stats_page.granularity.setCurrentText("Week")
    save(window, name="stats", width=1500)
    if "stats-heatmap" in names:  # scroll down to the calendar of reviews and show it with the table under it
        # noinspection PyProtectedMember
        scroller = stats_page.findChild(QScrollArea)
        assert scroller is not None
        scroller.verticalScrollBar().setValue(stats_page.heatmap.y() - 16)
        wait(300)
        save(window, name="stats-heatmap", width=1500)
    window.open_database()
    wait(400)
    # noinspection PyProtectedMember
    page = window._overlay
    assert isinstance(page, DatabasePage)
    save(window, name="database")
    if "database-questions" in names:
        page.tabs["questions"].click()
        page.view.sortByColumn(page.model.headers.index("Last seen"), Qt.SortOrder.DescendingOrder)
        save(window, name="database-questions")
    page.tabs["answers"].click()
    wait(200)
    row = next(page.proxy.index(r, 0) for r in range(page.proxy.rowCount()) if "Chord" in page.proxy.index(r, 1).data())
    answer = row.data(ROW_ROLE)
    # noinspection PyProtectedMember
    preview = QuestionPreview(
        page._names[answer["exercise"]],
        question=Question.from_dict(json.loads(answer["payload"])),
        details=answer["details"],
        parent=window,
    )
    preview.show()
    wait(300)
    save(preview, name="question-preview", width=900)
    preview.close()
    window.show_home()

    if {"filtered-practice", "filtered-exercise", "keyboard-review", "self-grading", "waiting-for-review"}.intersection(names):
        window.home.restore_tile_filters({"exercises": frozenset({NoteNames.name, KeyboardNotes.name})}, expanded=True)
        window.shuffle_button.setChecked(True)
        window.home.refresh_counts()
        wait(1200)
        save(window, name="filtered-practice")
        window.home.category_filter.click()
        window.open_exercise(NoteNames)
        wait(500)
        save(window, name="filtered-exercise")
        window.shuffle_button.setChecked(False)
        window.home.restore_tile_filters({}, expanded=False)

        window.open_exercise(KeyboardNotes)
        save(window, name="keyboard-review")

        sounds.enabled = False  # capture answer feedback without opening an audio device
        learner.set_self_grading(True)
        learner.calendar.set_limits(learner.profile.id, exercise="NoteNames", new_cards=None, reviews=0)
        window.open_exercise(NoteNames)
        view = window._exercise_page
        assert view is not None and view.question is not None
        view.submit(view.question.answer, button=None)
        save(window, name="self-grading")
        if "waiting-for-review" in names:
            learner.set_self_grading(False)
            learner.calendar.set_limits(learner.profile.id, exercise="ClefBasics", new_cards=1, reviews=None)
            window.open_exercise(ClefBasics)
            view = window._exercise_page
            assert view is not None
            view.submit("Incorrect", button=None)
            wait(800)
            assert view.question is None
            save(window, name="waiting-for-review")
        window.show_home()

    # The app-wide settings: the Notation style section, and the Sound page showing the viola.
    dialog = AppSettingsDialog(window, learner=learner)
    dialog.resize(1000, 640)
    dialog.show()
    dialog.categories.setCurrentRow(2)
    wait(300)
    save(dialog, name="settings")
    dialog.categories.setCurrentRow(5)
    dialog.instruments.select("viola_bowed")
    wait(200)
    save(dialog, name="settings-sound", width=1000)
    if "practice-settings" in names:
        learner.set_self_grading(True)
        learner.calendar.set_limits(learner.profile.id, new_cards=10, reviews=UNLIMITED)
        dialog.categories.setCurrentItem(dialog.categories.findItems("Practice", Qt.MatchFlag.MatchExactly)[0])
        save(dialog, name="practice-settings")
    dialog.close()

    if {"lesson-tiles", "lesson-workspace", "glossary"}.intersection(names):
        window.show_home()
        window.home.mode_control.buttons[1].click()
        wait(1200)  # let the tile transition finish before capturing the catalog
        save(window, name="lesson-tiles")
        window.open_lessons("pitches-and-notes")
        save(window, name="lesson-workspace")
    if "glossary" in names:
        window.show_home()
        window.open_glossary()
        glossary = window._overlay
        assert isinstance(glossary, GlossaryPage)
        glossary.search.setText("minor")
        glossary.terms.setCurrentItem(glossary.terms.findItems("harmonic minor scale", Qt.MatchFlag.MatchExactly)[0])
        wait(500)
        save(window, name="glossary")
    if "profile-create" in names or "profile-picker" in names:
        profiles = Database()
        for name in ("profile-create", "profile-picker"):
            if name == "profile-picker":
                profiles.add_profile("Ada")
                profiles.add_profile("Sam")
            picker = ProfileDialog(profiles)
            picker.show()
            save(picker, name=name)
            picker.close()
        profiles.close()


if __name__ == "__main__":
    raise SystemExit(main())
