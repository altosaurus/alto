"""
A bouncing spectrum display for the metronome preview.

Examples
--------
>>> display = MetronomeSpectrum()
>>> display.set_sound("low-pip")
"""

from __future__ import annotations

import math
import wave
from functools import lru_cache

from PySide6.QtCore import QPointF, QRectF, QVariantAnimation
from PySide6.QtGui import (
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPen,
)
from PySide6.QtWidgets import QWidget

from alto.audio import METRONOME_CLICKS, metronome_preview_pcm
from alto.ui.zoom import px

BANDS = 24
FPS = 60
RELEASE_MS = 220
SILENCE = (0.0,) * BANDS


@lru_cache(maxsize=len(METRONOME_CLICKS))
def _spectrum(key: str) -> tuple[list[tuple[float, ...]], int]:
    """
    Measure frequency bands in the preview and smooth their release.

    Parameters
    ----------
    key : str
        The bundled metronome sound.

    Returns
    -------
    tuple of list and int
        Band levels by frame and clip duration in milliseconds.

    Examples
    --------
    >>> frames, duration = _spectrum("high-pip")
    >>> len(frames[0]) == BANDS and duration > 1500
    True
    """
    pcm, rate = metronome_preview_pcm(key)
    samples = memoryview(pcm).cast("h")
    hop = round(rate / FPS)
    # Short Hann windows give the higher bands the same relative
    # bandwidth as the lower ones and capture the attack of each click.
    filters = []
    for band in range(BANDS):
        hz = 300 * (8000 / 300) ** (band / (BANDS - 1))
        size = min(hop, round(5 * rate / hz))
        weights = [math.sin(math.pi * i / size) ** 2 for i in range(size)]
        filters.append((2 * math.cos(math.tau * hz / rate), weights))

    frames = []
    previous = SILENCE
    for start in range(0, len(samples) + rate * RELEASE_MS // 1000, hop):
        chunk = samples[start : start + hop]
        levels = [
            max(0.0, level - 1000 / (RELEASE_MS * FPS)) for level in previous
        ]
        if any(chunk):
            for band, (coefficient, weights) in enumerate(filters):
                # Goertzel measures just this band's energy.
                a = b = 0.0
                for sample, weight in zip(chunk, weights, strict=False):
                    a, b = sample * weight + coefficient * a - b, a
                power = max(0.0, a * a + b * b - coefficient * a * b)
                amplitude = 4 * math.sqrt(power) / (len(weights) * 32768)
                # Map -48 to -6 dBFS onto the height of the display.
                db = 20 * math.log10(max(amplitude, 1e-6))
                levels[band] = max(levels[band], min(1.0, (db + 48) / 42))
        previous = tuple(levels)
        frames.append(previous)
    return frames, round(len(samples) * 1000 / rate)


class MetronomeSpectrum(QWidget):
    """
    Show a smooth frequency curve that rises with each click.

    Examples
    --------
    >>> MetronomeSpectrum().accessibleName()
    'Metronome spectrum'
    """

    def __init__(self) -> None:
        """
        Create the level display at rest.

        Examples
        --------
        >>> display = MetronomeSpectrum()
        """
        super().__init__()
        self.setFixedHeight(px(92))
        self.setAccessibleName("Metronome spectrum")
        self._frames: list[tuple[float, ...]] = []
        self._key = ""
        self._playing = False
        self._duration = 0
        self.animation = QVariantAnimation(self)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.valueChanged.connect(lambda _: self.update())
        self.animation.finished.connect(self.update)

    def set_sound(self, key: str) -> None:
        """
        Load the levels for the selected sound.

        Parameters
        ----------
        key : str
            The sound selected in the list.

        Examples
        --------
        >>> MetronomeSpectrum().set_sound("pencil-click")
        """
        if key == self._key:
            return
        self._key = key
        self._playing = False
        self.animation.stop()
        try:
            self._frames, duration = _spectrum(key)
        except (OSError, wave.Error):
            self._frames, duration = [], 0
        self._duration = duration
        self.animation.setDuration(duration + RELEASE_MS)
        self.setAccessibleDescription(
            f"Frequency levels for {METRONOME_CLICKS[key][0]}, "
            "from low on the left to high on the right.",
        )
        self.update()

    def set_playing(self, playing: bool) -> None:
        """
        Follow the audio backend's playback state.

        Parameters
        ----------
        playing : bool
            Whether the loaded preview is playing.

        Examples
        --------
        >>> MetronomeSpectrum().set_playing(False)
        """
        if playing and self.isVisible() and self._frames:
            if not self._playing:
                self.animation.stop()
                self.animation.start()
        elif self.animation.currentTime() < self._duration - 1000 / FPS:
            # Clear interruptions immediately. Let the last beat decay.
            self.animation.stop()
        self._playing = playing
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Draw a continuous curve through the current spectrum.

        Parameters
        ----------
        event : QPaintEvent
            The requested paint region.

        Examples
        --------
        >>> MetronomeSpectrum().grab().isNull()
        False
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        palette = self.palette()
        painter.setBrush(palette.alternateBase())
        painter.setPen(QPen(palette.mid(), 1))
        panel = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        painter.drawRoundedRect(panel, 7, 7)
        levels = SILENCE
        if (
            self._frames
            and self.animation.state() != QVariantAnimation.State.Stopped
        ):
            frame = self.animation.currentTime() * FPS // 1000
            levels = self._frames[min(frame, len(self._frames) - 1)]
        margin = px(10)
        area = panel.adjusted(margin, margin, -margin, -margin)
        if area.isEmpty():
            return
        step = area.width() / len(levels)
        base = area.bottom()
        previous = QPointF(area.left(), base)
        curve = QPainterPath(previous)
        for band, level in enumerate(levels):
            point = QPointF(
                area.left() + (band + 0.5) * step,
                base - area.height() * level,
            )
            # Joining at midpoints keeps the tangent continuous.
            curve.quadTo(previous, (previous + point) / 2)
            previous = point
        end = QPointF(area.right(), base)
        curve.quadTo(previous, end)

        fill = QPainterPath(curve)
        fill.closeSubpath()
        tint = palette.highlight().color()
        gradient = QLinearGradient(area.topLeft(), area.bottomLeft())
        tint.setAlpha(95)
        gradient.setColorAt(0, tint)
        tint.setAlpha(12)
        gradient.setColorAt(1, tint)
        painter.fillPath(fill, gradient)
        painter.strokePath(curve, QPen(palette.highlight(), px(2)))
