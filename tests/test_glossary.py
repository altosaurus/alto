"""
Check the musical relationships a learner sees and hears in the
glossary.
"""

from dataclasses import replace
from itertools import pairwise
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from alto.audio import sounds
from alto.theory.pitch import Note
from alto.ui import engraving
from alto.ui.glossary import TERMS, GlossaryPage
from alto.ui.meter_staff import MeterStaff

_STEPS = {
    "major scale": [(2, 2, 1, 2, 2, 2, 1)] * 2,
    "tetrachord": [(2, 2, 1)] * 2,
    "natural minor scale": [(2, 1, 2, 2, 1, 2, 2)] * 2,
    "harmonic minor scale": [(2, 1, 2, 2, 1, 3, 1)] * 2,
    "melodic minor scale": [
        (2, 1, 2, 2, 2, 2, 1),
        (-2, -2, -1, -2, -2, -1, -2),
    ],
    "minor pentachord": [(2, 1, 2, 2)] * 2,
}

_RHYTHMS_MS = {
    "rhythm": [(1200, 600, 600), (600, 600, 1200)],
    "tie": [(600, 600, 600), (1200, 600)],
    "dot": [(600, 600), (900, 300)],
    "beat": [(600, 600, 600, 600), (1200, 1200)],
    "tempo": [(1000,) * 4, (500,) * 4],
}


def test_glossary_playback_matches_the_displayed_music(
    app: QApplication,
) -> None:
    """
    Cycle every term and check its diagram, pitches, and click rhythm.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    page = GlossaryPage()
    page.show()
    with (
        patch.object(sounds, "preview") as preview,
        patch.object(sounds, "play_rhythm") as clicks,
        patch.object(sounds, "play_notes") as notes,
        patch.object(sounds, "stop_all", wraps=sounds.stop_all) as stop,
    ):
        for term, entry in TERMS.items():
            page.terms.setCurrentItem(
                page.terms.findItems(term, Qt.MatchFlag.MatchExactly)[0],
            )
            for index, example in enumerate(entry.examples):
                assert page.example_label.text() == example.caption
                assert page.example_circle.isVisible() == (
                    term == "circle of fifths"
                )
                if term == "circle of fifths":
                    assert page.example_circle.cell == (
                        "outer",
                        example.signature % 12,
                    )
                    assert page.example_circle.signature == example.signature
                clicks.reset_mock()
                preview.reset_mock()
                notes.reset_mock()
                page.hear.click()
                assert page.meter_staff.isVisible() == bool(example.rhythm)
                click_only = bool(example.rhythm) and term != "tie"
                assert (page.hear.text() == "▶  Hear rhythm") == bool(
                    example.rhythm,
                )
                if click_only:
                    assert not preview.called and not notes.called
                    durations = example.durations_ms()
                    expected = _RHYTHMS_MS.get(term)
                    if expected:
                        assert durations == expected[index]
                    assert clicks.call_args.args == (durations,)
                    assert clicks.call_args.kwargs["force"]
                    assert clicks.call_args.kwargs["levels"] == (
                        example.click_levels or (1.0,) * len(durations)
                    )
                    highlight = clicks.call_args.kwargs["on_step"]
                    sounds._sample_step = highlight
                else:
                    clicks.assert_not_called()
                if example.rhythm:
                    score = page.meter_staff
                    assert score.meter == (example.meter or (4, 4))
                    assert score.values == tuple(example.rhythm.split())
                    if term == "bar line":
                        assert (
                            score.bar_line
                            == ("Barline", "Double barline")[index]
                        )
                    if not click_only:
                        assert (
                            preview.call_args.kwargs["step_ms"]
                            == _RHYTHMS_MS[term][index]
                        )
                        assert preview.call_args.kwargs["beat_ms"] == 600
                        assert preview.call_args.kwargs["midis"] == [
                            Note.parse(name).midi
                            for name in example.pitches.split()
                        ]
                    highlight = (
                        clicks if click_only else preview
                    ).call_args.kwargs["on_step"]
                    sounds._sample_step = highlight
                    for column in range(len(score.values)):
                        highlight(column)
                        assert score.playback_column == column
                    assert not page.example_staff.isVisible()
                elif entry.keyboard:
                    midis = preview.call_args.kwargs["midis"]
                    assert (
                        page.example_keyboard.isVisible()
                        and page.example_staff.isHidden()
                    )
                    assert midis == [
                        page.example_keyboard.highlight,
                        *page.example_keyboard.additional_highlights,
                    ]
                    if term in {"half step", "whole step"}:
                        assert midis[1] - midis[0] == (
                            1 if term == "half step" else 2
                        )
                    if term == "piano keyboard":
                        assert midis == [(60, 65)[index]]
                else:
                    midis = [col[0].midi for col in notes.call_args.args[0]]
                    assert notes.call_args.kwargs["force"]
                    assert notes.call_args.kwargs["warmup"]
                    staff = page.example_staff
                    highlight = notes.call_args.kwargs["on_step"]
                    for column in range(len(midis)):
                        highlight(column)
                        assert staff.playback_column == column
                    assert (
                        staff.isVisible() and page.example_keyboard.isHidden()
                    )
                    written = [
                        [Note.parse(pitch) for pitch in chord.split("+")]
                        for chord in example.pitches.split()
                    ]
                    assert notes.call_args.args[0] == staff.columns == written
                    assert (staff.clef, staff.key) == (
                        example.clef,
                        example.signature,
                    )
                    if term in _STEPS:
                        expected = _STEPS[term][index]
                        assert (
                            tuple(b - a for a, b in pairwise(midis))
                            == expected
                        )
                        assert staff.wedges == [
                            {1: "H", 2: "W", 3: "3H"}[abs(step)]
                            for step in expected
                        ]
                    else:
                        assert not staff.wedges
                    if term == "octave":
                        assert midis[1] - midis[0] == 12
                    if term == "accidental":
                        before, after = (col[0] for col in staff.columns)
                        assert (
                            before.diatonic == after.diatonic
                            and abs(after.midi - before.midi) == 1
                        )
                stop.reset_mock()
                page.next_example.click()
                stop.assert_called_once()
                assert page.example_staff.playback_column is None
                assert page.meter_staff.playback_column is None
            assert page.example_label.text() == entry.examples[0].caption
    page.close()


def test_meter_counts_match_the_pulse_divisions_and_accented_clicks() -> None:
    """Match printed counts to the click levels at those onsets."""
    for name, beats in (("duple", 2), ("triple", 3), ("quadruple", 4)):
        assert TERMS[name] == TERMS[f"{name} meter"]
        for divisions, example in zip(
            (2, 3),
            TERMS[name].examples,
            strict=True,
        ):
            assert example.durations_ms() == (600 // divisions,) * (
                2 * beats * divisions
            )
            counts = example.counts[: beats * divisions]
            levels = example.click_levels
            assert levels[: len(counts)] == levels[len(counts) :]
            assert counts[::divisions] == tuple(
                str(i + 1) for i in range(beats)
            )
            for i, level in enumerate(levels[: len(counts)]):
                if i % divisions:
                    assert level == 0.35
                elif i == 0:
                    assert level == 1.0
                elif beats == 4 and i == 2 * divisions:
                    assert level == 0.8
                else:
                    assert level == 0.6
    for bars, example in zip(
        (2, 4),
        TERMS["hypermeter"].examples,
        strict=True,
    ):
        assert example.counts == ("1", "2") * (bars * 2)
        assert (
            example.click_levels == (1.0, 0.6, *((0.8, 0.6) * (bars - 1))) * 2
        )


def test_simple_and_compound_beams_fit_on_the_staff(app: QApplication) -> None:
    """
    Keep every eighth note in its beat group at both glossary widths.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    page = GlossaryPage()
    page.search.setText("quadruple meter")
    page.show()
    for width in (575, 1100):
        page.resize(width, 560)
        for divisions in (2, 3):
            app.processEvents()
            staff = page.meter_staff
            with patch.object(
                engraving,
                "draw_beamed_eighths",
                wraps=engraving.draw_beamed_eighths,
            ) as beams:
                staff.grab()
            assert len(beams.call_args_list) == 8
            for call in beams.call_args_list:
                heads = call.kwargs["heads"]
                assert len(heads) == divisions
                assert all(staff.rect().contains(pt.toPoint()) for pt in heads)
            assert page.definition_area.horizontalScrollBar().maximum() == 0
            page.next_example.click()
    page.close()


def test_tied_rhythm_highlights_both_upward_stems(app: QApplication) -> None:
    """
    Keep tied symbols on one baseline and one playback step.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    page = GlossaryPage()
    page.search.setText("tie")
    page.show()
    page.next_example.click()
    score = page.meter_staff
    score.highlight_column(0)
    height_with_counts = score.height()
    page.counts.click()
    assert score.height() < height_with_counts
    with (
        patch.object(
            engraving,
            "draw_note",
            wraps=engraving.draw_note,
        ) as notes,
        patch.object(engraving, "draw_clef") as clef,
    ):
        score.grab()
    clef.assert_not_called()
    symbols = [call.kwargs for call in notes.call_args_list]
    assert len(symbols) == 3 and score.meter == (3, 4)
    assert len({s["y"] for s in symbols}) == 1
    assert not any(s.get("stem_down") for s in symbols)
    assert symbols[0]["color"] == symbols[1]["color"] != symbols[2]["color"]
    page.close()


def test_glossary_comparison_pairs() -> None:
    """
    Check the pitch and key relationships that changing examples
    demonstrates.
    """

    def phrases(term: str) -> list[list[Note]]:
        """
        Read each glossary example as a sequence of written pitches.

        Parameters
        ----------
        term : str
            Name of the glossary entry.

        Returns
        -------
        list of list of Note
            The notes of each example in display order.
        """
        return [
            [Note.parse(name) for name in example.pitches.split()]
            for example in TERMS[term].examples
        ]

    for first, second in phrases("enharmonically equivalent"):
        assert first.midi == second.midi and first.letter != second.letter
    rising, falling = phrases("enharmonic")
    assert (
        rising[1].midi == falling[1].midi
        and rising[1].letter != falling[1].letter
    )
    original, transposed = phrases("transpose")
    assert all(
        (b.diatonic - a.diatonic, b.midi - a.midi) == (1, 2)
        for a, b in zip(original, transposed, strict=True)
    )
    major, minor = phrases("relative keys")
    assert major[-1].midi - minor[-1].midi == 3
    assert len({ex.signature for ex in TERMS["relative keys"].examples}) == 1
    major, minor = phrases("parallel keys")
    assert major[-1] == minor[-1] and major[2].midi - minor[2].midi == 1
    assert len({ex.signature for ex in TERMS["parallel keys"].examples}) == 2


def test_glossary_scale_fits_after_resizing(app: QApplication) -> None:
    """
    Keep both the longest staff and the complete definition reachable
    when the pane changes shape.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    page = GlossaryPage()
    page.search.setText("major scale")
    page.show()
    for width in (1100, 575, 1100):
        page.resize(width, 560)
        for _ in range(3):
            app.processEvents()
        text = page.definition.geometry()
        demo = page.demo.geometry()
        assert not text.intersects(demo)
        assert page.definition_area.horizontalScrollBar().maximum() == 0
        assert page.definition.verticalScrollBar().maximum() == 0
        assert page.example_staff.width() >= 280
        assert page.definition_area.widget().rect().contains(demo)
    page.close()


def test_search_without_matches_clears_the_example_and_recovers(
    app: QApplication,
) -> None:
    """
    Clear the example and practice links for an empty search result and
    restore them for the next match.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    page = GlossaryPage()
    page.search.setText("unlisted term")
    assert page.demo.isHidden()
    assert "No matching terms" in page.definition.toPlainText()
    assert page.activity_tiles.count() == 0
    page.search.setText("major scale")
    assert not page.demo.isHidden()
    assert page.activity_tiles.count() > 0


def test_interval_entries_describe_what_their_examples_show() -> None:
    """
    Check each interval example against the number and half steps its
    caption and entry claim.
    """
    sizes = {
        "interval": None,
        "unison": {(1, 0), (1, 1)},
        "simple intervals": None,
        "compound intervals": None,
        "perfect": {(4, 5), (5, 7), (8, 12)},
        "major": {(2, 2), (3, 4), (6, 9)},
        "minor": {(2, 1), (3, 3), (6, 8)},
    }
    for term, expected in sizes.items():
        found = set()
        for example in TERMS[term].examples:
            columns = [
                [Note.parse(name) for name in column.split("+")]
                for column in example.pitches.split()
            ]
            low, high = columns[0][0], columns[1][0]
            found.add(
                (
                    abs(high.diatonic - low.diatonic) + 1,
                    abs(high.midi - low.midi),
                ),
            )
            number = abs(high.diatonic - low.diatonic) + 1
            if term == "simple intervals":
                assert number <= 8
            if term == "compound intervals":
                assert number >= 9
        if expected is not None:
            assert found == expected, term
    for example in TERMS["harmonic interval"].examples:
        columns = [column.split("+") for column in example.pitches.split()]
        assert len(columns) == 1 and len(columns[0]) == 2
    for example in TERMS["melodic interval"].examples:
        columns = [column.split("+") for column in example.pitches.split()]
        assert len(columns) == 2 and all(
            len(column) == 1 for column in columns
        )


def test_compound_meter_wraps_and_draws_dots_rests_and_double_bars(
    app: QApplication,
) -> None:
    """
    Draw three bars of compound rhythm across narrow and wide systems.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    score = MeterStaff()
    bar = ("eighth", "eighth", "eighth-rest", "dotted-quarter")
    score.show_score(bar * 3, meter=(6, 8), bar_line="Double barline")
    score.set_counts_visible(True)
    assert [symbol.count for symbol in score._measures[0]] == [
        "1",
        "la",
        "li",
        "2",
    ]
    example = replace(TERMS["tie"].examples[0], meter=(6, 8), bpm=100)
    assert example.beat_ms == 900
    score.resize(score.sizeHint())
    score.show()
    wide = score.grab()
    score.resize(int(wide.width() * 0.8), wide.height())
    app.processEvents()
    assert score.grab().height() == 3 * wide.height()
    score.close()
