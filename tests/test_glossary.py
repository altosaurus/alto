"""Check the musical relationships a learner sees and hears in the glossary."""

from itertools import pairwise
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from alto.ui.glossary import TERMS, GlossaryPage


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
    with patch("alto.ui.glossary.sounds.preview") as preview, patch("alto.ui.glossary.sounds.stop_all") as stop:
        for term, entry in TERMS.items():
            page.terms.setCurrentItem(page.terms.findItems(term, Qt.MatchFlag.MatchExactly)[0])
            for example in entry.examples:
                assert page.example_label.text() == example.caption
                page.hear.click()
                midis = preview.call_args.kwargs["midis"]
                if term in {"half step", "whole step"}:
                    assert page.example_keyboard.isVisible() and page.example_staff.isHidden()
                    assert midis == [page.example_keyboard.highlight, *page.example_keyboard.additional_highlights]
                    assert midis[1] - midis[0] == (1 if term == "half step" else 2)
                else:
                    staff = page.example_staff
                    assert staff.isVisible() and page.example_keyboard.isHidden()
                    assert midis == [col[0].midi for col in staff.columns]
                    assert (staff.clef, staff.key) == (example.clef, example.signature)
                    if term in {"major scale", "tetrachord"}:
                        steps = [b - a for a, b in pairwise(midis)]
                        expected = [2, 2, 1] if term == "tetrachord" else [2, 2, 1, 2, 2, 2, 1]
                        assert steps == expected
                        assert staff.wedges == ["H" if step == 1 else "W" for step in expected]
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
            assert page.example_label.text() == entry.examples[0].caption
    page.close()


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
