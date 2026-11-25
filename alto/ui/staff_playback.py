"""
Connect a displayed music sample to the notes sounding on its staff.
"""

from collections.abc import Callable, Sequence

from PySide6.QtCore import QEvent, QObject, Signal
from PySide6.QtWidgets import QWidget

from alto.audio import DEFAULT_NOTE_GAP_MS, sounds
from alto.settings import RHYTHM_DURATIONS
from alto.theory.pitch import Note


class StaffPlayback(QObject):
    """
    Follow a sample's audio onsets and end playback when its view
    closes.
    """

    step = Signal(
        object,
    )  # a column index, or None when the highlight should clear

    def __init__(
        self,
        parent: QWidget,
        *,
        highlight: Callable[[int | None], object] | None = None,
    ) -> None:
        """
        Attach playback to its view.

        Parameters
        ----------
        parent : QWidget
            The view containing the sample.
        highlight : callable or None
            Draw the current step on the displayed staff or staves. Omit
            for audio-only playback.
        """
        super().__init__(parent)
        if highlight is not None:
            self.step.connect(highlight)
        self._notify = self.step.emit
        parent.installEventFilter(self)
        parent.destroyed.connect(self.stop)

    def play(
        self,
        columns: Sequence[Sequence[Note]],
        *,
        gap_ms: int = DEFAULT_NOTE_GAP_MS,
        force: bool = False,
        warmup: bool = False,
        instrument: str | None = None,
    ) -> None:
        """
        Play the displayed notes in order.

        Parameters
        ----------
        columns : sequence of sequence of Note
            Notes grouped by onset.
        gap_ms : int
            Time between onsets in milliseconds.
        force : bool
            Allow explicit auditions even when exercise sounds are
            muted.
        instrument : str or None
            Sound registered by the active pack, or the learner’s
            default.
        warmup : bool
            Prepare the audio streams before the first note.
        """
        sounds.play_sample(
            columns,
            gap_ms=gap_ms,
            force=force,
            on_step=self._notify,
            warmup=warmup,
            instrument=instrument,
        )

    def play_rhythm(self, values: Sequence[str]) -> None:
        """
        Click at each note onset and leave rests silent.

        Parameters
        ----------
        values : sequence of str
            Written note and rest values. A quarter note gets one beat.
        """
        beat_ms = 600
        quarter = RHYTHM_DURATIONS["quarter"]
        sounds.play_rhythm(
            tuple(
                round(beat_ms * RHYTHM_DURATIONS[v] / quarter) for v in values
            ),
            levels=tuple(0.0 if v.endswith("-rest") else 1.0 for v in values),
            on_step=self._notify,
        )

    def stop(self) -> None:
        """
        Clear this view's sounding note and cancel its pending audio.
        """
        sounds.stop_sample(self._notify)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: PLR0917 (Qt passes both arguments positionally)
        """
        End the sample when the learner leaves its view.

        Parameters
        ----------
        watched : QObject
            The sample's containing view.
        event : QEvent
            The pending Qt event.

        Returns
        -------
        bool
            Whether the event was consumed.
        """
        if event.type() == QEvent.Type.Hide:
            self.stop()
        return super().eventFilter(watched, event)
