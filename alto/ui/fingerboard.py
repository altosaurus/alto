"""
Render a pack's instrument portrait using its calibrated string
endpoints.
"""

from __future__ import annotations

from dataclasses import replace
from math import dist, hypot

from PySide6.QtCore import QLineF, QPointF, QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import (
    QColor,
    QHideEvent,
    QMouseEvent,
    QMovie,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPalette,
    QPen,
    QPixmap,
    QResizeEvent,
)
from PySide6.QtWidgets import QVBoxLayout, QWidget

from alto.audio import DEFAULT_NOTE_GAP_MS, sounds
from alto.exercises.base import FingerboardPosition, PicturePosition
from alto.instrument_packs import INSTALLED, PackInstrument
from alto.theory.pitch import Note
from alto.ui import keyboard_styles
from alto.ui.colors import CORRECT_ANSWER_COLOR
from alto.ui.keyboard import KeyboardWidget
from alto.ui.keyboard_styles import KeyboardStyle
from alto.ui.zoom import px

OCTAVE = 12  # half steps: the ruler always reaches at least this far
# string spacings beyond the highest string: clear of the fingerboard's
# edge
RULER_OFFSET = 1.8
# the smallest height, on screen, at which a position name is still
# readable
LABEL_PIXELS = 7
FRAME_RADIUS = 8  # pixels: corners of the framed neck view
# key widths: how long a drawn manual's natural keys are, unless the
# plugin says otherwise
MANUAL_KEY_LENGTH = 4.5
MANUAL_KEY_WIDTH = (
    30.0  # pixels: the widest a drawn manual's natural key may be
)
MANUAL_GAP = 6  # pixels between two drawn manuals
MANUAL_PAD = 6.0  # pixels around a drawn manual's keys


def ruler_reach(model: PackInstrument) -> int:
    """
    Find how many half steps the ruler covers: an octave, or further if
    the pack names a position beyond it.

    Parameters
    ----------
    model : PackInstrument
        The instrument whose positions, if any, the ruler labels.

    Returns
    -------
    int
        The highest half step with a tick.

    Examples
    --------
    >>> from pathlib import Path
    >>> bare = PackInstrument(
    ...     "pack.x.y",
    ...     Path("a.png"),
    ...     (10, 10),
    ...     (),
    ...     None,
    ... )
    >>> ruler_reach(bare)
    12
    >>> ruler_reach(
    ...     PackInstrument(
    ...         "pack.x.y",
    ...         Path("a.png"),
    ...         (10, 10),
    ...         (),
    ...         None,
    ...         positions=((14, "9th"),),
    ...     )
    ... )
    14
    """
    return max([OCTAVE, *(steps for steps, _ in model.positions)])


def ruler_base(
    model: PackInstrument,
    *,
    step: int,
) -> tuple[QPointF, QPointF, float]:
    """
    Locate where a ruler tick for one half step starts, beside the
    fingerboard rather than on it.

    Parameters
    ----------
    model : PackInstrument
        The instrument whose string endpoints give the geometry.
    step : int
        Half steps above the open string.

    Returns
    -------
    tuple of QPointF, QPointF and float
        The tick's starting point in image pixels, the unit vector
        pointing away from the strings, and the local distance
        between neighboring strings at that step.

    Examples
    --------
    >>> from pathlib import Path
    >>> from alto.instrument_packs import PackString
    >>> strings = (
    ...     PackString("C3", (0, 10), (100, 10)),
    ...     PackString("G3", (0, 0), (100, 0)),
    ... )
    >>> viola = PackInstrument(
    ...     "pack.x.y",
    ...     Path("a.png"),
    ...     (100, 10),
    ...     strings,
    ...     None,
    ... )
    >>> start, away, apart = ruler_base(
    ...     viola, step=0
    ... )
    >>> (start.x(), start.y(), away.y(), apart)
    (0.0, -18.0, -1.0, 10.0)
    """
    low = QPointF(*model.strings[0].point(step))
    high = QPointF(*model.strings[-1].point(step))
    width = hypot(high.x() - low.x(), high.y() - low.y())
    count = max(len(model.strings) - 1, 1)
    if width == 0:
        return high, QPointF(0, -1), 1.0
    unit = QPointF((high.x() - low.x()) / width, (high.y() - low.y()) / width)
    spacing = width / count
    return high + unit * (spacing * RULER_OFFSET), unit, spacing


def neck_view(model: PackInstrument, *, gap: float) -> QRectF:
    """
    Choose the part of the picture a note question needs: the nut, the
    neck with its ruler, and the bridge.

    The scroll, the pegs and everything past the bridge are left out,
    since the question never refers to them.

    Parameters
    ----------
    model : PackInstrument
        The instrument whose string endpoints give the geometry.
    gap : float
        The smallest distance between strings at the nut, in image
        pixels. Keyword-only.

    Returns
    -------
    QRectF
        The region to show, in image pixels. It can extend past the
        picture, so intersect it with the picture's rectangle.

    Examples
    --------
    >>> from pathlib import Path
    >>> from alto.instrument_packs import PackString
    >>> strings = (
    ...     PackString("C3", (100, 60), (900, 60)),
    ...     PackString("G3", (100, 40), (900, 40)),
    ... )
    >>> board = PackInstrument(
    ...     "pack.x.y",
    ...     Path("a.png"),
    ...     (1000, 100),
    ...     strings,
    ...     None,
    ... )
    >>> view = neck_view(board, gap=20.0)
    >>> (
    ...     view.left() < 100
    ...     and view.right() > 900
    ...     and view.top() < 40
    ...     and view.bottom() > 60
    ... )
    True
    """
    points = [
        point
        for string in model.strings
        for point in (string.nut, string.bridge)
    ]
    for step in (0, ruler_reach(model)):
        base, unit, spacing = ruler_base(model, step=step)
        top = base + unit * (spacing * 3.6 + gap * 1.5)
        points.append((top.x(), top.y()))
    xs = [x for x, _ in points]
    ys = [y for _, y in points]
    length = dist(model.strings[0].nut, model.strings[0].bridge)
    box = QRectF(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
    return box.adjusted(
        -0.025 * length,
        -0.03 * length,
        0.08 * length,
        0.06 * length,
    )


def manual_style(model: PackInstrument) -> tuple[KeyboardStyle | None, float]:
    """
    Build the look of an instrument's drawn keyboards from its plugin's
    ``keyboard_style``.

    Parameters
    ----------
    model : PackInstrument
        The instrument whose keyboards are drawn.

    Returns
    -------
    tuple of KeyboardStyle or None and float
        The style, or None to use the learner's own keyboard style, and
        how long a natural key is, in key widths.

    Examples
    --------
    >>> from pathlib import Path
    >>> bare = PackInstrument(
    ...     "pack.x.y",
    ...     Path("a.png"),
    ...     (10, 10),
    ...     (),
    ...     None,
    ... )
    >>> manual_style(bare)
    (None, 4.5)
    >>> from alto.instrument_packs import (
    ...     PackKeyboardStyle,
    ... )
    >>> look = PackKeyboardStyle(
    ...     (("cap", "#eee3c8"),),
    ...     (("length", 5.0),),
    ... )
    >>> styled = PackInstrument(
    ...     "pack.x.y",
    ...     Path("a.png"),
    ...     (10, 10),
    ...     (),
    ...     None,
    ...     keyboard_style=look,
    ... )
    >>> look_style, look_length = manual_style(
    ...     styled
    ... )
    >>> # noinspection PyUnresolvedReferences
    >>> look_style.cap, look_length
    ('#eee3c8', 5.0)
    """
    spec = model.keyboard_style
    if spec is None:
        return None, MANUAL_KEY_LENGTH
    numbers = dict(spec.numbers)
    length = numbers.pop("length", MANUAL_KEY_LENGTH)
    style = replace(
        keyboard_styles.BY_KEY["classic"],
        key=model.key,
        label=model.key,
        note="",
        **dict(spec.colors),
        **numbers,
    )
    return style, length


class FingerboardWidget(QWidget):
    """
    Draw the instrument and keep the teaching overlays on the same
    scale.
    """

    picked = Signal(
        float,
        float,
        # a click on the picture while it can be clicked: the point in
        # the
        # picture's own pixels
    )

    def __init__(self) -> None:
        """Create an empty fingerboard display."""
        super().__init__()
        self._pickable = False  # a click on the picture is an answer
        self._reveal: QPointF | None = (
            None  # where to show the right place on a picture with no marker
        )
        self._to_picture: tuple[QPointF, float, QPointF] | None = (
            None  # pane centre, scale and source centre of the last paint
        )
        self.position: FingerboardPosition | PicturePosition | None = None
        self.model: PackInstrument | None = None
        self._view = ""  # which of the instrument's pictures is loaded
        self._image = QPixmap()
        self._movie = QMovie(self)
        self._movie.frameChanged.connect(self._refresh_frame)
        self._frame = QPixmap()
        self._silent_timer = QTimer(self)
        self._silent_timer.setSingleShot(True)
        self._silent_timer.timeout.connect(lambda: self.set_sounding(False))
        self.sounding = False
        self.sound_key: str | None = None
        self._manuals: dict[
            str,
            KeyboardWidget,
        ] = {}  # the drawn keyboards of the current instrument, by name
        self._manual_layout = QVBoxLayout(self)
        self._manual_layout.setContentsMargins(0, 0, 0, 0)
        self._manual_layout.setSpacing(px(MANUAL_GAP))
        self.setAccessibleName("Instrument picture")
        self.setMinimumHeight(px(155))

    def sizeHint(self) -> QSize:
        """
        Reserve space for the whole instrument.

        Returns
        -------
        QSize
            Preferred dimensions of the diagram.
        """
        shown = [
            widget
            for widget in self._manuals.values()
            if not widget.isHidden()
        ]
        # the height the manuals need at their widest keys, whatever
        # size they have been squeezed to
        if shown:
            tall = sum(
                2 * widget.pad
                + widget.style.rail
                + px(MANUAL_KEY_WIDTH) * widget.key_length
                for widget in shown
            )
            return QSize(
                px(720),
                round(tall + px(MANUAL_GAP) * (len(shown) - 1)),
            )
        return QSize(px(720), px(270))

    def show_position(
        self,
        position: FingerboardPosition | PicturePosition | None,
    ) -> None:
        """
        Resolve the saved pack identity and clear the previous playback
        highlight.
        """
        self.set_sounding(False)
        self._reveal = None
        self.position = position
        model = INSTALLED.get(position.instrument) if position else None
        self._show_manuals(model, position=position)
        view = position.view if isinstance(position, PicturePosition) else ""
        if model is not self.model or view != self._view:
            found = model.picture(view) if model else None
            self._image = QPixmap(str(found[0])) if found else QPixmap()
            self.model = model
            self._view = view
        animation = model.correct_answer_animation if model else None
        filename = (
            str(animation.file)
            if animation
            and (
                (animation.anchor == "image" and not view)
                or isinstance(position, FingerboardPosition)
            )
            else ""
        )
        if self._movie.fileName() != filename:
            self._movie.setFileName(filename)
        self.sound_key = (
            self.model.sound.key if self.model and self.model.sound else None
        )
        self.update()

    def _manuals_shown(self) -> bool:
        """
        Report whether the widget is drawing keyboards in place of the
        picture.

        Returns
        -------
        bool
            True while the current question or step highlights keys.
        """
        return any(not widget.isHidden() for widget in self._manuals.values())

    def _show_manuals(
        self,
        model: PackInstrument | None,
        *,
        position: FingerboardPosition | PicturePosition | None,
    ) -> None:
        """
        Draw the instrument's keyboards, one above the other, with the
        question's keys highlighted, or hide them.

        Parameters
        ----------
        model : PackInstrument or None
            The instrument the position belongs to.
        position : FingerboardPosition or PicturePosition or None
            What to show. Keyboards are drawn only for a picture
            position that names keys. Keyword-only.
        """
        drawn = (
            isinstance(position, PicturePosition)
            and bool(position.keys)
            and model is not None
            and bool(model.keyboards)
        )
        if (
            not drawn
            or model is None
            or not isinstance(position, PicturePosition)
        ):
            for widget in self._manuals.values():
                widget.hide()
            self.updateGeometry()
            return
        style, length = manual_style(model)
        wanted = {board.name for board in model.keyboards}
        for name in list(self._manuals):
            if name not in wanted:
                self._manuals.pop(name).deleteLater()
        for index, board in enumerate(model.keyboards):
            widget = self._manuals.get(board.name)
            if widget is None:
                widget = self._manuals[board.name] = KeyboardWidget(self)
                widget.max_key_width = px(MANUAL_KEY_WIDTH)
                self._manual_layout.insertWidget(index, widget)
            widget.style_override = style
            widget.key_length = length
            widget.pad = px(MANUAL_PAD)
            low, high = position.span or (board.lowest, board.highest)
            widget.show_keys(
                [
                    Note.parse(key).midi
                    for name, key in position.keys
                    if name == board.name
                ],
                span=(
                    max(Note.parse(low).midi, Note.parse(board.lowest).midi),
                    min(Note.parse(high).midi, Note.parse(board.highest).midi),
                ),
            )
            widget.show()
        self._fit_manuals()
        self._color_manuals()
        self.updateGeometry()

    def _fit_manuals(self) -> None:
        """
        Size the drawn keys so that every manual fits the height the
        widget has, up to the widest key allowed.
        """
        shown = [
            widget
            for widget in self._manuals.values()
            if not widget.isHidden()
        ]
        if not shown:
            return
        room = (self.height() - px(MANUAL_GAP) * (len(shown) - 1)) / len(shown)
        for widget in shown:
            rail = widget.style.rail
            by_height = (room - 2 * widget.pad - rail) / widget.key_length
            widget.max_key_width = max(
                px(8.0),
                min(px(MANUAL_KEY_WIDTH), by_height),
            )
            widget.refit()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Fit the drawn keyboards to the new height.

        Parameters
        ----------
        event : QResizeEvent
            The resize that happened.
        """
        super().resizeEvent(event)
        self._fit_manuals()

    def _color_manuals(self) -> None:
        """
        Color the highlighted keys: the palette's highlight, or the
        correct-answer color while the answer sounds.
        """
        color = (
            QColor(CORRECT_ANSWER_COLOR)
            if self.sounding
            else self.palette().color(QPalette.ColorRole.Highlight)
        )
        for widget in self._manuals.values():
            widget.set_highlight_color(color)

    def set_pickable(self, pickable: bool) -> None:
        """
        Let a click on the picture be an answer, and say so with the
        pointer.

        Parameters
        ----------
        pickable : bool
            True to emit `picked` for each click on the picture.

        Examples
        --------
        >>> board = FingerboardWidget()
        >>> board.set_pickable(True)
        >>> board.cursor().shape() == Qt.CursorShape.PointingHandCursor
        True
        """
        self._pickable = pickable
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
            if pickable
            else Qt.CursorShape.ArrowCursor,
        )

    def show_target(self, point: tuple[float, float] | None) -> None:
        """
        Mark the right place on a picture that has no marker, or clear
        the mark.

        Parameters
        ----------
        point : tuple of float, or None
            The place in the picture's own pixels, or None to clear it.

        Examples
        --------
        >>> board = FingerboardWidget()
        >>> board.show_target((10.0, 20.0))
        >>> board.show_target(None)
        """
        self._reveal = None if point is None else QPointF(*point)
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Turn a click into a point on the picture when the picture is
        being used for an answer.

        Parameters
        ----------
        event : QMouseEvent
            The click.
        """
        if (
            not self._pickable
            or self._to_picture is None
            or event.button() != Qt.MouseButton.LeftButton
        ):
            super().mousePressEvent(event)
            return
        centre, scale, source = self._to_picture
        point = (event.position() - centre) / scale + source
        self.picked.emit(point.x(), point.y())

    def set_sounding(self, sounding: bool) -> None:
        """Mark the pitch during answer playback."""
        self._silent_timer.stop()
        self.sounding = sounding
        if sounding and self._movie.fileName():
            self._movie.stop()
            self._movie.start()
        else:
            self._movie.stop()
            self._frame = QPixmap()
        self._color_manuals()
        self.update()

    def feedback_gap_ms(self) -> int:
        """
        Use the sounding note's full length for an animated single-note
        question.

        Returns
        -------
        int
            Feedback duration in milliseconds.
        """
        if self._movie.fileName() and self.position and self.position.note:
            return sounds.note_duration_ms(
                Note.parse(self.position.note).midi,
                instrument=self.sound_key,
            )
        return DEFAULT_NOTE_GAP_MS

    def animate_silent_answer(self, duration_ms: int) -> None:
        """
        Show an image-anchored overlay during the usual silent picture
        feedback interval.
        """
        if self._movie.fileName():
            self.set_sounding(True)
            self._silent_timer.start(duration_ms)

    def _refresh_frame(self) -> None:
        """
        Tint the author's current transparency mask with Alto's shared
        feedback color.
        """
        self._frame = self._movie.currentPixmap().copy()
        if not self._frame.isNull():
            painter = QPainter(self._frame)
            painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_SourceIn,
            )
            painter.fillRect(self._frame.rect(), QColor(CORRECT_ANSWER_COLOR))
            painter.end()
        self.update()

    def hideEvent(self, event: QHideEvent) -> None:
        """
        End any silent or sounding overlay when leaving the diagram.
        """
        self.set_sounding(False)
        super().hideEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Draw the whole picture for a marked location, or only the neck
        and ruler for a note on a string.
        """
        del event
        position = self.position
        if position is None or self._manuals_shown():
            return
        painter = QPainter(self)
        model = self.model
        if model is None or (
            isinstance(position, FingerboardPosition)
            and tuple(s.pitch for s in model.strings) != position.strings
        ):
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "Install the matching instrument pack to see this position.",
            )
            return
        image = self._image
        if image.isNull():
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "Instrument image unavailable.",
            )
            return
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.SmoothPixmapTransform,
        )
        full = QRectF(image.rect())
        if isinstance(position, PicturePosition):
            zoom = (
                QRectF(*position.focus).intersected(full)
                if position.focus
                else full
            )
            self._draw_view(
                painter,
                image=image,
                source=zoom if not zoom.isEmpty() else full,
                pane=QRectF(self.rect()),
                marker=QPointF(*position.point),
                gap=position.size or min(full.width(), full.height()) * 0.045,
            )
            return
        steps = (
            Note.parse(position.note).midi
            - Note.parse(position.strings[position.string]).midi
        )
        marker = QPointF(*model.strings[position.string].point(steps))
        gap = min(
            dist(a.nut, b.nut)
            for a, b in zip(model.strings, model.strings[1:])
        )
        source = neck_view(model, gap=gap).intersected(full)
        if source.isEmpty():
            return
        pane = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        scale = min(
            pane.width() / source.width(),
            pane.height() / source.height(),
        )
        if scale <= 0:
            return
        frame = QRectF(0, 0, source.width() * scale, source.height() * scale)
        frame.moveCenter(pane.center())
        outline = QPainterPath()
        outline.addRoundedRect(frame, FRAME_RADIUS, FRAME_RADIUS)
        painter.save()
        painter.setClipPath(outline)
        painter.fillRect(frame, self.palette().color(QPalette.ColorRole.Base))
        self._draw_view(
            painter,
            image=image,
            source=source,
            pane=frame,
            marker=marker,
            gap=gap,
        )
        painter.restore()
        painter.setPen(QPen(self.palette().color(QPalette.ColorRole.Mid), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(frame, FRAME_RADIUS, FRAME_RADIUS)

    def _draw_ruler(
        self,
        painter: QPainter,
        *,
        gap: float,
        marker: QPointF,
        scale: float,
    ) -> None:
        """
        Draw a ruler beside the fingerboard: a short tick for each half
        step and a labeled tick for each position.

        Parameters
        ----------
        painter : QPainter
            Already scaled so that its units are source-image pixels.
        gap : float
            The smallest distance between strings at the nut, in image
            pixels. Keyword-only.
        marker : QPointF
            Where the dot sits, so a faint line can lead from it to its
            place on the ruler. Keyword-only.
        scale : float
            Screen pixels per image pixel, used to leave out position
            names too small to read. Keyword-only.
        """
        model = self.model
        position = self.position
        if model is None or not isinstance(position, FingerboardPosition):
            return
        palette = self.palette()
        ink = palette.color(QPalette.ColorRole.WindowText)
        paper = palette.color(QPalette.ColorRole.Window)
        names = dict(model.positions)
        font = painter.font()
        font.setPixelSize(max(1, round(gap)))
        painter.setFont(font)
        steps = (
            Note.parse(position.note).midi
            - Note.parse(position.strings[position.string]).midi
        )
        base, _, _ = ruler_base(model, step=steps)
        lead = QColor(palette.color(QPalette.ColorRole.Highlight))
        lead.setAlpha(150)
        painter.setPen(QPen(lead, gap * 0.1, Qt.PenStyle.DotLine))
        painter.drawLine(QLineF(marker, base))
        for step in range(ruler_reach(model) + 1):
            base, unit, spacing = ruler_base(model, step=step)
            major = step in names
            length = spacing * (0.95 if major else 0.45)
            if (step - 1) in names:
                length += (
                    gap * 1.5
                    # a position a half step after another sits higher,
                    # so
                    # the names do not touch
                )
            ink.setAlpha(255 if major else 150)
            painter.setPen(QPen(ink, gap * (0.14 if major else 0.1)))
            painter.drawLine(QLineF(base, base + unit * length))
            if not major or scale * gap < LABEL_PIXELS:
                continue
            width = (
                painter.fontMetrics().horizontalAdvance(names[step])
                + gap * 0.5
            )
            height = gap * 1.3
            centre = base + unit * (length + height * 0.65)
            box = QRectF(
                centre.x() - width / 2,
                centre.y() - height / 2,
                width,
                height,
            )
            pill = QColor(paper)
            pill.setAlpha(235)
            painter.setBrush(pill)
            border = QColor(ink)
            border.setAlpha(110)
            painter.setPen(QPen(border, gap * 0.06))
            painter.drawRoundedRect(box, height / 2, height / 2)
            ink.setAlpha(255)
            painter.setPen(QPen(ink))
            painter.drawText(box, Qt.AlignmentFlag.AlignCenter, names[step])
            painter.setBrush(Qt.BrushStyle.NoBrush)

    def _draw_view(
        self,
        painter: QPainter,
        *,
        image: QPixmap,
        source: QRectF,
        pane: QRectF,
        marker: QPointF,
        gap: float,
    ) -> None:
        """
        Fit one region uniformly and draw the marker and guides in
        source-image pixels.
        """
        scale = min(
            pane.width() / source.width(),
            pane.height() / source.height(),
        )
        if scale <= 0:
            return
        assert self.model is not None
        self._to_picture = (pane.center(), scale, source.center())
        painter.save()
        painter.translate(pane.center())
        painter.scale(scale, scale)
        painter.translate(-source.center())
        painter.setClipRect(source, Qt.ClipOperation.IntersectClip)
        painter.drawPixmap(0, 0, image)
        if isinstance(self.position, FingerboardPosition):
            self._draw_ruler(painter, gap=gap, marker=marker, scale=scale)
        animation = self.model.correct_answer_animation
        if self.sounding and animation and not self._frame.isNull():
            frame = QRectF(self._frame.rect())
            if animation.anchor == "image":
                painter.drawPixmap(QRectF(image.rect()), self._frame, frame)
            elif isinstance(self.position, FingerboardPosition):
                line = QLineF(
                    marker,
                    QPointF(*self.model.strings[self.position.string].bridge),
                )
                height = min(
                    gap * 0.9,
                    line.length() * frame.height() / frame.width(),
                )
                painter.save()
                painter.translate(marker)
                painter.rotate(-line.angle())
                painter.drawPixmap(
                    QRectF(0, -height / 2, line.length(), height),
                    self._frame,
                    frame,
                )
                painter.restore()
        if (
            isinstance(self.position, PicturePosition)
            and not self.position.marker
        ):
            if self._reveal is None:
                painter.restore()
                return
            # a picture with no marker shows the right place once the
            # question is answered
            marker = self._reveal
        color = (
            QColor(CORRECT_ANSWER_COLOR)
            if self.sounding
            else self.palette().color(QPalette.ColorRole.Highlight)
        )
        painter.setBrush(color)
        painter.setPen(QPen(QColor("white"), gap * 0.15))
        painter.drawEllipse(marker, gap / 2, gap / 2)
        painter.restore()
