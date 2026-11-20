"""Write portable Anki decks from Alto questions and optional calendar review dates."""

from __future__ import annotations

import hashlib
import itertools
import json
import random
import sqlite3
import time
from collections.abc import Callable, Iterator, Sequence
from concurrent.futures import CancelledError
from contextlib import closing
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event, Lock
from zipfile import ZIP_DEFLATED, ZipFile

import genanki
from fsrs import Card

from alto.exercises import Exercise, Question
from alto.learning import Learner
from alto.learning.calendar import CALENDAR_SCHEDULERS
from alto.learning.grading import Sm2State

# Anki review dates are day numbers relative to the collection's creation day.
_EPOCH = date(2000, 1, 1)
_MODEL = genanki.Model(
    1765974231,
    "Alto exercise",
    fields=[{"name": name} for name in ("Question", "Illustration", "Answer", "Explanation")],
    templates=[
        {
            "name": "Practice",
            "qfmt": "{{Question}}<div>{{Illustration}}</div>",
            "afmt": '{{FrontSide}}<hr id="answer">{{Answer}}<div>{{Explanation}}</div>',
        },
    ],
    css=".card { font-family: sans-serif; text-align: center; font-size: 20px; } img { max-width: 100%; height: auto; }",
)


@dataclass
class Review:
    """One practiced example and its calendar schedule in the exporting profile."""

    item_key: str
    signature: str
    payload: str
    scheduler: str
    due: float
    state: str
    seen: int


def profile_reviews(learner: Learner) -> dict[str, list[Review]]:
    """
    Read this profile's graded calendar cards in due order.

    Returns
    -------
    dict of str to list of Review
        Scheduled questions grouped by exercise class name.
    """
    mode = learner.mode
    result: dict[str, list[Review]] = {}
    if mode in CALENDAR_SCHEDULERS:
        rows = learner.db.conn.execute(
            "SELECT s.exercise, s.item_key, c.signature, c.payload, s.scheduler, s.due, s.state, COALESCE(i.seen, 1) "
            "FROM review_schedules s JOIN practice_cards c USING (profile_id, exercise, item_key) "
            "LEFT JOIN items i USING (profile_id, exercise, item_key) "
            "WHERE s.profile_id=? AND s.scheduler=? ORDER BY s.exercise, s.due, s.item_key",
            (learner.profile.id, mode),
        )
        for name, *values in rows:
            result.setdefault(name, []).append(Review(*values))
    return result


def deck_candidates(exercise: Exercise, *, reviews: Sequence[Review]) -> Iterator[tuple[Question, Review | None]]:
    """
    Visit eligible scheduled examples before generating additional questions.

    Yields
    ------
    tuple of Question and optional Review
        Question to render and its matching schedule, if available.
    """
    signature = exercise.settings_signature()
    schedules = {review.item_key: review for review in reviews}
    for review in reviews:
        question = exercise.review_question(
            Question.from_dict(json.loads(review.payload)),
            same_settings=signature == review.signature,
        )
        if question is not None:
            yield question, review
    for question in exercise.daily_candidates(random.Random(type(exercise).__name__)):
        yield question, schedules.get(question.item_key())


def _schedule(review: Review) -> tuple[int, int, int, int, int, int, int, str]:
    """
    Translate a calendar schedule into the scheduling columns of an Anki card.

    Returns
    -------
    tuple
        Type, queue, due date, interval, ease in permille, repetitions, remaining steps, and memory state.
    """
    data = ""
    ease = 2.5
    if review.scheduler == "FSRS":
        card = Card.from_json(review.state)
        last = card.last_review
        interval = round((review.due - last.timestamp()) / 86400) if last else 0
        phase = card.state.name.lower()
        data = json.dumps({"s": card.stability, "d": card.difficulty, "lrt": int(last.timestamp()) if last else None})
    else:
        sm2 = Sm2State.read(review.state)
        interval, ease, phase = sm2.interval, sm2.ease, sm2.phase
    if phase == "review":
        # Day numbers use the collection's rollover at 04:00 local time.
        due = ((datetime.fromtimestamp(review.due) - timedelta(hours=4)).date() - _EPOCH).days
        kind, queue, left = 2, 2, 0
        interval = max(1, interval)
    else:
        # The intraday learning queue stores a Unix timestamp. Resume at the next step.
        due = int(review.due)
        kind, queue, left = 3 if phase == "relearning" else 1, 1, 1001
        interval = max(0, interval)
    return kind, queue, due, interval, round(ease * 1000), max(1, review.seen), left, data


def export_deck(
    path: Path,
    *,
    exercise: Exercise,
    reviews: Sequence[Review],
    render: Callable[[Question, Path], list[str]],
) -> int:
    """
    Write a deck and replace the destination only after the package is complete.

    Parameters
    ----------
    path : Path
        Destination package.
    exercise : Exercise
        Source of questions under the current export settings.
    reviews : sequence of Review
        Eligible schedules to prioritize and transfer when requested.
    render : callable
        Produces Anki fields and writes their PNG illustrations in the working directory.

    Returns
    -------
    int
        Number of exported cards. An empty selection leaves the destination untouched.
    """
    return export_decks(
        path,
        selections=[DeckSelection(exercise, reviews)],
        render=lambda q, folder, _exercise: render(q, folder),
    )


@dataclass
class DeckSelection:
    """One exercise deck and its optional review schedules."""

    exercise: Exercise
    reviews: Sequence[Review]


@dataclass
class PlannedDeck:
    """Distinct questions and their stable export identities for one exercise."""

    exercise: Exercise
    cards: list[tuple[str, Question, Review | None]]


def plan_deck(selection: DeckSelection) -> PlannedDeck:
    """
    Select the exact cards to count in the summary and write to the package.

    Returns
    -------
    PlannedDeck
        Eligible cards in export order, with reviewed cards first.
    """
    exercise = selection.exercise
    deck = PlannedDeck(exercise, [])
    groups = exercise.card_groups() or {}
    seen = set()
    for question, review in deck_candidates(exercise, reviews=selection.reviews):
        key = question.item_key()
        # Each notation term has one identification card and one location card.
        identity = (groups[key] + (":identify" if question.choices else ":locate")) if key in groups else key
        if identity not in seen:
            seen.add(identity)
            deck.cards.append((identity, question, review))
    return deck


def export_decks(
    path: Path,
    *,
    selections: Sequence[DeckSelection],
    render: Callable[[Question, Path, Exercise], list[str]],
    progress: Callable[[str, int, int], None] | None = None,
) -> int:
    """
    Save the selected exercise decks together in one Anki package.

    Parameters
    ----------
    path : Path
        Destination replaced once all selected decks and their media are ready.
    selections : sequence of DeckSelection
        Exercises to export and their optional schedules.
    render : callable
        Renders the fields and writes the media for one exercise question.
    progress : callable, optional
        Receives the current operation, completed work, and a fixed total for the whole package.

    Returns
    -------
    int
        Total cards written across all decks.
    """
    return write_decks(path, plans=[plan_deck(selection) for selection in selections], render=render, progress=progress)


class ExportControl:
    """Coordinate a cancellation decision with the final replacement of the destination."""

    def __init__(self) -> None:
        """Start with a pending export and an untouched destination."""
        self.canceled = Event()
        self._save_lock = Lock()
        self._saved = False

    def confirm_cancel(self, confirm: Callable[[], bool]) -> bool:
        """
        Reserve the destination until the user decides whether to cancel.

        Returns
        -------
        bool
            True if cancellation was confirmed before the package was saved.
        """
        with self._save_lock:
            if self._saved or not confirm():
                return False
            self.canceled.set()
            return True

    def check(self) -> None:
        """
        Stop work and unwind temporary files after confirmed cancellation.

        Raises
        ------
        CancelledError
            When the user has confirmed cancellation.
        """
        if self.canceled.is_set():
            raise CancelledError

    def publish(self, package: Path, *, destination: Path) -> None:
        """Replace the destination only while cancellation is excluded."""
        with self._save_lock:
            self.check()
            package.replace(destination)
            self._saved = True


def write_decks(
    path: Path,
    *,
    plans: Sequence[PlannedDeck],
    render: Callable[[Question, Path, Exercise], list[str]],
    progress: Callable[[str, int, int], None] | None = None,
    control: ExportControl | None = None,
    deck_progress: Callable[[int, bool], None] | None = None,
) -> int:
    """
    Write the cards from a completed export plan into a single package.

    Returns
    -------
    int
        Number of cards written across the selected decks.
    """
    control = control or ExportControl()
    decks = []
    schedules = []
    count = 0
    total_cards = sum(len(plan.cards) for plan in plans)
    deck_count = sum(bool(plan.cards) for plan in plans)
    # Rendering and packing each get one unit per card. The database, compression, and final save get one each.
    total_work = 2 * total_cards + 3
    with TemporaryDirectory(dir=path.parent) as folder:
        work = Path(folder)
        for row, plan in enumerate(plans):
            if not plan.cards:
                continue
            if deck_progress:
                deck_progress(row, False)
            exercise = plan.exercise
            target = len(plan.cards)
            stage = f"Deck {len(decks) + 1} of {deck_count} · {exercise.name}"
            if progress:
                progress(stage, count, total_work)
            name = type(exercise).__name__
            deck_id = int.from_bytes(hashlib.sha256(f"alto:{name}".encode()).digest()[:4], "big")
            parent = f"Alto::{exercise.category}" if deck_count > 1 else "Alto"
            deck = genanki.Deck(deck_id, f"{parent}::{exercise.name}")
            for index, (identity, question, review) in enumerate(plan.cards, start=1):
                control.check()
                guid = genanki.guid_for("Alto", name, identity)
                deck.add_note(genanki.Note(model=_MODEL, fields=render(question, work, exercise), guid=guid, due=index))
                if review is not None:
                    schedules.append((*_schedule(review), guid))
                if progress:
                    progress(f"{stage} · Cards prepared: {index} of {target}", count + index, total_work)
            decks.append(deck)
            count += target
            if deck_progress:
                deck_progress(row, True)
        if not count:
            return 0
        if progress:
            progress("Writing the Anki collection…", count, total_work)
        database = work / "collection.anki2"
        with closing(sqlite3.connect(database)) as conn, conn:
            conn.set_progress_handler(control.canceled.is_set, 1000)
            now = time.time()
            genanki.Package(decks).write_to_db(conn.cursor(), now, itertools.count(int(now * 1000)))
            conn.execute("UPDATE col SET crt=?", (int(datetime(2000, 1, 1, 4).timestamp()),))
            conn.execute("UPDATE col SET conf=json_set(conf, '$.schedVer', 2)")
            conn.executemany(
                "UPDATE cards SET type=?,queue=?,due=?,ivl=?,factor=?,reps=?,left=?,data=? "
                "WHERE nid=(SELECT id FROM notes WHERE guid=?)",
                schedules,
            )
        package = work / "deck.apkg"
        with ZipFile(package, "w", ZIP_DEFLATED) as archive:
            if progress:
                progress("Compressing the collection…", count + 1, total_work)
            with database.open("rb") as source, archive.open(database.name, "w", force_zip64=True) as entry:
                while block := source.read(1024 * 1024):
                    control.check()
                    entry.write(block)
            media = {}
            images = sorted(work.glob("*.png"))
            for index, image in enumerate(images):
                control.check()
                media[str(index)] = image.name
                archive.write(image, str(index))
                if progress:
                    packed = (index + 1) * count // len(images)
                    progress(f"Packing images · {index + 1} of {len(images)}", count + 2 + packed, total_work)
            if progress:
                progress(f"Saving {path.name}…", total_work - 1, total_work)
            archive.writestr("media", json.dumps(media))
        control.publish(package, destination=path)
        if progress:
            progress(f"Saved {path.name}.", total_work, total_work)
    return count
