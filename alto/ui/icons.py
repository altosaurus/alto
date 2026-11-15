"""
Small monochrome icons drawn from SVG, tinted with the current theme's text colour.

Each icon is the inside of a 24 by 24 SVG, written with the word COLOR where the theme colour goes. `svg_icon` turns one
into a `QIcon`.

Examples
--------
>>> svg_icon(HELP, color=QColor("black")).isNull()
False
"""

from __future__ import annotations

import math

from PySide6.QtCore import (
    QByteArray,
    Qt,
)
from PySide6.QtGui import (
    QColor,
    QIcon,
    QPainter,
    QPixmap,
)
from PySide6.QtSvg import QSvgRenderer

_BODY = '<path d="M3 9h4l5-4v14l-5-4H3z" fill="COLOR"/>'
_STROKE = 'fill="none" stroke="COLOR" stroke-width="2" stroke-linecap="round"'
_SPEAKER_ON = _BODY + f'<path d="M15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13" {_STROKE}/>'
_SPEAKER_MUTED = _BODY + f'<path d="M16 9.5l5 5M21 9.5l-5 5" {_STROKE}/>'

SPEAKER_ON, SPEAKER_MUTED = _SPEAKER_ON, _SPEAKER_MUTED

# Settings: three thin vertical tracks with solid pill-shaped knobs.
SLIDERS = (
    '<path d="M6 3V21M12 3V21M18 3V21" fill="none" stroke="COLOR" stroke-width="1.6" stroke-linecap="round"/>'
    '<rect x="3" y="12.75" width="6" height="4.5" rx="2.25" fill="COLOR"/>'
    '<rect x="9" y="5.75" width="6" height="4.5" rx="2.25" fill="COLOR"/>'
    '<rect x="15" y="10.75" width="6" height="4.5" rx="2.25" fill="COLOR"/>'
)


def svg_icon(
    inner: str,
    *,
    color: QColor,
    size: int = 24,
    scale: float = 2.0,
) -> QIcon:
    """
    Render 24 by 24 SVG shapes into a crisp icon.

    Parameters
    ----------
    inner : str
        The SVG shapes, using COLOR wherever the colour goes.
    color : QColor
        The colour to draw in. Keyword-only.
    size : int, default 24
        The icon's size in logical pixels. Keyword-only.
    scale : float, default 2.0
        How many device pixels to render per logical pixel, so it stays sharp on high-resolution screens. Keyword-only.

    Returns
    -------
    QIcon
        The icon.

    Examples
    --------
    >>> icon = svg_icon(PLAY, color=QColor("#336699"), size=16)
    >>> icon.isNull()
    False
    """
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">{inner.replace("COLOR", color.name())}</svg>'
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    px = QPixmap(int(size * scale), int(size * scale))
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(p)
    p.end()
    px.setDevicePixelRatio(scale)
    return QIcon(px)


# Sidebar toggle: an edge bar with a chevron pointing toward the edge while the list is shown
# (click to hide) and away from it while hidden (click to show).
_SIDEBAR_STROKE = 'fill="none" stroke="COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
SIDEBAR_OPEN = f'<path d="M5 4v16M15 7l-5 5 5 5" {_SIDEBAR_STROKE}/>'
SIDEBAR_CLOSED = f'<path d="M5 4v16M10 7l5 5-5 5" {_SIDEBAR_STROKE}/>'

# Exercise icons for the home screen (24x24, drawn with outlines like the controls above).
_LINE = 'fill="none" stroke="COLOR" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"'
_STAFF = '<path d="M2 6H22M2 9.5H22M2 13H22M2 16.5H22M2 20H22" fill="none" stroke="COLOR" stroke-width="1.1" opacity=".5"/>'


def _ring(
    x: float,
    *,
    y: float,
    rx: float = 3.3,
    ry: float = 2.3,
) -> str:
    """
    Return the SVG for an outlined oval, used as a note head.

    Parameters
    ----------
    x : float
        The centre's x position in the 24 by 24 drawing.
    y : float
        The centre's y position. Keyword-only.
    rx : float, default 3.3
        The horizontal radius. Keyword-only.
    ry : float, default 2.3
        The vertical radius. Keyword-only.

    Returns
    -------
    str
        An `<ellipse>` element.

    Examples
    --------
    >>> _ring(13, y=18.5).startswith('<ellipse cx="13" cy="18.5"')
    True
    """
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" {_LINE}/>'


EXERCISE_NOTE_NAMES = _STAFF + _ring(
    12,
    y=11.25,
    rx=3.4,
    ry=2.1,
)
# Two stacked notes with a bracket spanning the distance between them.
EXERCISE_INTERVALS = (
    _ring(
        7,
        y=6,
        rx=3.2,
        ry=2.2,
    )
    + _ring(
        7,
        y=18,
        rx=3.2,
        ry=2.2,
    )
    + f'<path d="M15.5 6h4v12h-4" {_LINE}/>'
)
EXERCISE_KEY_SIGNATURES = f'<path d="M9 4v16M15 3.5v16M5 9.5l14-3M5 16.5l14-3" {_LINE}/>'
# Key signature construction: a fork on its side, a stem and two tines, with a dot on one of them.
EXERCISE_KEY_CONSTRUCTION = (
    f'<path d="M2.5 12H8M8 6.5v11M8 6.5h13M8 17.5h13" {_LINE}/><circle cx="15" cy="6.5" r="2.6" fill="COLOR"/>'
)
# Scale construction: a staff with notes climbing across it.
EXERCISE_SCALE_CONSTRUCTION = (
    '<path d="M2 6.5H22M2 10H22M2 13.5H22M2 17H22" fill="none" stroke="COLOR" stroke-width="1.1" opacity=".5"/>'
    + "".join(
        _ring(
            x,
            y=y,
            rx=2.2,
            ry=1.6,
        )
        for x, y in ((4.5, 18.8), (9.5, 14.8), (14.5, 10.8), (19.5, 6.8))
    )
)


def _cells(
    radius: float,
    *,
    gap: float,
) -> str:
    """
    Return the SVG for a ring cut into twelve cells, with the gap between cells centred at the top.

    Parameters
    ----------
    radius : float
        The ring's radius in the 24 by 24 drawing.
    gap : float
        The length of the gap between neighbouring cells, along the ring. Keyword-only.

    Returns
    -------
    str
        A dashed `<circle>` element.

    Examples
    --------
    >>> _cells(9, gap=1).startswith('<circle cx="12" cy="12" r="9"')
    True
    """
    per_cell = 2 * math.pi * radius / 12
    start = -90 - math.degrees(gap / radius) / 2
    return (
        f'<circle cx="12" cy="12" r="{radius}" fill="none" stroke="COLOR" stroke-width="2.4" '
        f'stroke-dasharray="{per_cell - gap:.2f} {gap}" transform="rotate({start:.2f} 12 12)"/>'
    )


# Circle of fifths: two rings, each cut into twelve cells.
EXERCISE_CIRCLE = _cells(9, gap=1.0) + _cells(5, gap=0.8)
EXERCISE_SCALES = "".join(
    _ring(
        x,
        y=y,
        rx=2.4,
        ry=1.7,
    )
    for x, y in (
        (4.5, 18.5),
        (9.5, 14.8),
        (14.5, 11.1),
        (19.5, 7.4),
    )
)
EXERCISE_CHORDS = (
    _ring(
        12,
        y=18.5,
        rx=3.6,
        ry=2.4,
    )
    + _ring(
        12,
        y=12,
        rx=3.6,
        ry=2.4,
    )
    + _ring(
        12,
        y=5.5,
        rx=3.6,
        ry=2.4,
    )
)
# Three eighth notes rising under one beam.
_NOTE = 'fill="COLOR" stroke="COLOR" stroke-width="1" stroke-linejoin="round"'


def _beamed_notes() -> str:
    """
    Return the SVG for three eighth notes rising under one beam, the arpeggio exercise's icon.

    Returns
    -------
    str
        Note heads, stems and a beam as SVG shapes.

    Examples
    --------
    >>> _beamed_notes().count("<ellipse")
    3
    """
    heads = ((4.6, 19.0), (11.8, 15.0), (19.0, 11.0))  # note heads rise to the right
    beam_start, beam_end = (7.0, 6.2), (21.6, 2.2)  # the beam follows them
    out = []
    for x, y in heads:
        stem = x + 2.4  # the stem rises from the right edge of the head to the beam
        top = beam_start[1] + (stem - beam_start[0]) * (beam_end[1] - beam_start[1]) / (beam_end[0] - beam_start[0])
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="2.7" ry="1.9" transform="rotate(-20 {x} {y})" {_NOTE}/>')
        out.append(f'<path d="M{stem} {y - 0.3}V{top:.2f}" {_LINE}/>')
    out.append(
        f'<path d="M{beam_start[0]} {beam_start[1]}L{beam_end[0]} {beam_end[1]}" stroke="COLOR" stroke-width="2.6" '
        'stroke-linecap="butt" fill="none"/>',
    )
    return "".join(out)


EXERCISE_ARPEGGIOS = _beamed_notes()

# A play triangle, for the "hear it" buttons.
PLAY = '<path d="M8 5.5v13l11-6.5z" fill="COLOR" stroke="COLOR" stroke-width="1.6" stroke-linejoin="round"/>'

# Keyboard: four white keys with black keys on top, in real proportions (a white key is 6.2 times as long as it is
# wide; a black key is 0.58 as wide and 0.63 as long) and in their real colours, not tinted to the theme.
EXERCISE_KEYBOARD = (
    '<path d="M5.20 1.46H8.60V21.94Q8.60 22.54 8.00 22.54H5.80Q5.20 22.54 5.20 21.94Z" fill="#ffffff" stroke="#5c5c64" stroke-width="0.7" stroke-linejoin="miter"/>'
    '<path d="M8.60 1.46H12.00V21.94Q12.00 22.54 11.40 22.54H9.20Q8.60 22.54 8.60 21.94Z" fill="#ffffff" stroke="#5c5c64" stroke-width="0.7" stroke-linejoin="miter"/>'
    '<path d="M12.00 1.46H15.40V21.94Q15.40 22.54 14.80 22.54H12.60Q12.00 22.54 12.00 21.94Z" fill="#ffffff" stroke="#5c5c64" stroke-width="0.7" stroke-linejoin="miter"/>'
    '<path d="M15.40 1.46H18.80V21.94Q18.80 22.54 18.20 22.54H16.00Q15.40 22.54 15.40 21.94Z" fill="#ffffff" stroke="#5c5c64" stroke-width="0.7" stroke-linejoin="miter"/>'
    '<rect x="7.38" y="1.46" width="1.97" height="13.28" rx="0.25" fill="#1a1a1a"/>'
    '<rect x="11.25" y="1.46" width="1.97" height="13.28" rx="0.25" fill="#1a1a1a"/>'
    '<rect x="14.41" y="1.46" width="1.97" height="13.28" rx="0.25" fill="#1a1a1a"/>'
)

# Help: a question mark in a circle.
HELP = (
    '<circle cx="12" cy="12" r="9" fill="none" stroke="COLOR" stroke-width="2"/>'
    '<path d="M9.4 9.6a2.7 2.7 0 1 1 3.9 2.4c-.9.5-1.3 1.1-1.3 2" fill="none" stroke="COLOR" stroke-width="2" stroke-linecap="round"/>'
    '<circle cx="12" cy="16.9" r="1.15" fill="COLOR"/>'
)

# Reference: an open book.
BOOK = (
    '<path d="M12 6.5C10 5 7 4.6 3.5 5v13c3.5-.4 6.5 0 8.5 1.5M12 6.5c2-1.5 5-1.9 8.5-1.5v13c-3.5-.4-6.5 0-8.5 1.5M12 6.5v13" '
    'fill="none" stroke="COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
)

# Exercises: a checklist.
EXERCISES = (
    '<path d="M4 6.5l1.6 1.6L8.4 5M4 12.5l1.6 1.6L8.4 11M4 18.5l1.6 1.6L8.4 17M12.5 7h8M12.5 13h8M12.5 19h8" '
    'fill="none" stroke="COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
)

# Lessons: a mortarboard.
LESSONS = (
    '<path d="M2 9.5l10-5 10 5-10 5zM6 12v4.5c0 1.4 2.7 2.8 6 2.8s6-1.4 6-2.8V12M22 9.5v5.5" '
    'fill="none" stroke="COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
)

# Note construction: a staff with a note being dropped onto it.
EXERCISE_CONSTRUCTION = (
    '<path d="M2 11.5H22M2 14.3H22M2 17.1H22M2 19.9H22M2 22.7H22" fill="none" stroke="COLOR" stroke-width="1.1" opacity=".5"/>'
    + _ring(
        13,
        y=18.5,
        rx=3.3,
        ry=1.9,
    )
    + f'<path d="M13 1.6V8M10.2 5.2L13 8L15.8 5.2" {_LINE}/>'
)

# Menu icons (24x24, outlined like the others): restart and the application's settings.
_MENU = 'fill="none" stroke="COLOR" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
RESTART = f'<path d="M19 12a7 7 0 1 1-2.05-4.95M17.6 3.6v4h-4" {_MENU}/>'
GEAR = (
    f'<circle cx="12" cy="12" r="3" {_MENU}/><circle cx="12" cy="12" r="6.4" {_MENU}/>'
    '<path d="M12 3.2v2.4M12 18.4v2.4M3.2 12h2.4M18.4 12h2.4M5.8 5.8l1.7 1.7M16.5 16.5l1.7 1.7M5.8 18.2l1.7-1.7M16.5 7.5l1.7-1.7" '
    'fill="none" stroke="COLOR" stroke-width="2.6" stroke-linecap="round"/>'
)
# Quit: a power symbol, a broken ring with a line through the gap.
QUIT = f'<path d="M12 3.5v8M7.2 6.6a7.2 7.2 0 1 0 9.6 0" {_MENU}/>'
# Export and import: a tray with an arrow going out of it, or into it.
_TRAY = f'<path d="M4.5 15v4.5h15V15" {_MENU}/>'
EXPORT = _TRAY + f'<path d="M12 15V4.2M7.8 8.2L12 4l4.2 4.2" {_MENU}/>'
IMPORT = _TRAY + f'<path d="M12 4v10.8M7.8 10.8L12 15l4.2-4.2" {_MENU}/>'
# Check for updates: an arrow going up inside a circle.
UPDATE = f'<circle cx="12" cy="12" r="8.2" {_MENU}/><path d="M12 16.2V8M8.6 11.4L12 8l3.4 3.4" {_MENU}/>'
# Profile: a head and shoulders.
PROFILE = f'<circle cx="12" cy="8.2" r="3.6" {_MENU}/><path d="M4.6 20c.7-4 3.7-6 7.4-6s6.7 2 7.4 6" {_MENU}/>'
# Statistics: a line graph, a rising line with its points over a pair of axes.
CHART = (
    f'<path d="M4 4v16h16" {_MENU}/><path d="M8 15l3.6-4.4 3 2.6 4.4-6" {_MENU}/>'
    '<circle cx="8" cy="15" r="1.2" fill="COLOR"/><circle cx="11.6" cy="10.6" r="1.2" fill="COLOR"/>'
    '<circle cx="14.6" cy="13.2" r="1.2" fill="COLOR"/><circle cx="19" cy="7.2" r="1.2" fill="COLOR"/>'
)
# Database: a stack of discs, drawn as a cylinder.
DATABASE = (
    f'<ellipse cx="12" cy="6" rx="7" ry="2.6" {_MENU}/>'
    f'<path d="M5 6v12c0 1.45 3.1 2.6 7 2.6s7-1.15 7-2.6V6M5 12c0 1.45 3.1 2.6 7 2.6s7-1.15 7-2.6" {_MENU}/>'
)
