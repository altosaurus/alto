"""Check the musical relationships a learner sees and hears in the glossary."""

from itertools import pairwise
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from alto.audio import sounds
from alto.theory.pitch import Note
from alto.ui.glossary import TERMS, GlossaryPage

_STEPS = {
    "major scale": [(2, 2, 1, 2, 2, 2, 1)] * 2,
    "tetrachord": [(2, 2, 1)] * 2,
    "natural minor scale": [(2, 1, 2, 2, 1, 2, 2)] * 2,
    "harmonic minor scale": [(2, 1, 2, 2, 1, 3, 1)] * 2,
    "melodic minor scale": [(2, 1, 2, 2, 2, 2, 1), (-2, -2, -1, -2, -2, -1, -2)],
    "minor pentachord": [(2, 1, 2, 2)] * 2,
}


def test_glossary_examples_show_and_play_the_same_pitches(app: QApplication) -> None:
    """
    Cycle every term, checking each diagram, its musical intervals, and the pitches sent to playback.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    page = GlossaryPage()
    page.show()
    with (
        patch.object(sounds, "preview") as preview,
        patch.object(sounds, "play_notes") as notes,
        patch.object(sounds, "stop_all", wraps=sounds.stop_all) as stop,
    ):
        for term, entry in TERMS.items():
            page.terms.setCurrentItem(page.terms.findItems(term, Qt.MatchFlag.MatchExactly)[0])
            for index, example in enumerate(entry.examples):
                assert page.example_label.text() == example.caption
                assert page.example_circle.isVisible() == (term == "circle of fifths")
                if term == "circle of fifths":
                    assert page.example_circle.cell == ("outer", example.signature % 12)
                    assert page.example_circle.signature == example.signature
                page.hear.click()
                if entry.keyboard:
                    midis = preview.call_args.kwargs["midis"]
                    assert page.example_keyboard.isVisible() and page.example_staff.isHidden()
                    assert midis == [page.example_keyboard.highlight, *page.example_keyboard.additional_highlights]
                    assert midis[1] - midis[0] == (1 if term == "half step" else 2)
                else:
                    midis = [col[0].midi for col in notes.call_args.args[0]]
                    assert notes.call_args.kwargs["force"]
                    staff = page.example_staff
                    highlight = notes.call_args.kwargs["on_step"]
                    for column in range(len(midis)):
                        highlight(column)
                        assert staff.playback_column == column
                    assert staff.isVisible() and page.example_keyboard.isHidden()
                    assert midis == [col[0].midi for col in staff.columns]
                    assert (staff.clef, staff.key) == (example.clef, example.signature)
                    if term in _STEPS:
                        expected = _STEPS[term][index]
                        assert tuple(b - a for a, b in pairwise(midis)) == expected
                        assert staff.wedges == [{1: "H", 2: "W", 3: "3H"}[abs(step)] for step in expected]
                    else:
                        assert not staff.wedges
                    if term == "octave":
                        assert midis[1] - midis[0] == 12
                    if term == "accidental":
                        before, after = (col[0] for col in staff.columns)
                        assert before.diatonic == after.diatonic and abs(after.midi - before.midi) == 1
                stop.reset_mock()
                page.next_example.click()
                stop.assert_called_once()
                assert page.example_staff.playback_column is None
            assert page.example_label.text() == entry.examples[0].caption
    page.close()


def test_glossary_comparison_pairs() -> None:
    """Check the pitch and key relationships that changing examples demonstrates."""

    def phrases(term: str) -> list[list[Note]]:
        return [[Note.parse(name) for name in example.pitches.split()] for example in TERMS[term].examples]

    for first, second in phrases("enharmonically equivalent"):
        assert first.midi == second.midi and first.letter != second.letter
    rising, falling = phrases("enharmonic")
    assert rising[1].midi == falling[1].midi and rising[1].letter != falling[1].letter
    original, transposed = phrases("transpose")
    assert all((b.diatonic - a.diatonic, b.midi - a.midi) == (1, 2) for a, b in zip(original, transposed, strict=True))
    major, minor = phrases("relative keys")
    assert major[-1].midi - minor[-1].midi == 3
    assert len({ex.signature for ex in TERMS["relative keys"].examples}) == 1
    major, minor = phrases("parallel keys")
    assert major[-1] == minor[-1] and major[2].midi - minor[2].midi == 1
    assert len({ex.signature for ex in TERMS["parallel keys"].examples}) == 2


def test_glossary_scale_fits_after_resizing(app: QApplication) -> None:
    """
    Keep both the longest staff and the complete definition reachable when the pane changes shape.

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


def test_search_without_matches_clears_the_example_and_recovers(app: QApplication) -> None:
    """
    Clear the example and practice links for an empty search result and restore them for the next match.

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
