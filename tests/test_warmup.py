"""
Tests for the warm-up that gets fonts and notes ready while Alto is idle
after it opens.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from alto.ui import warmup


@pytest.mark.parametrize("enabled", [True, False])
def test_a_note_step_makes_its_note_only_while_sound_is_on(
    monkeypatch: pytest.MonkeyPatch,
    enabled: bool,
) -> None:
    """
    Check that a warm-up step makes its note, unless sound was turned
    off after the warm-up began.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces the note maker and sets the sound switch.
    enabled : bool
        Whether sound is on.
    """
    prepare = Mock()
    monkeypatch.setattr(warmup.sounds, "prepare", prepare)
    monkeypatch.setattr(warmup.sounds, "enabled", enabled)
    warmup._note_step(61)()
    assert prepare.call_count == (1 if enabled else 0)
