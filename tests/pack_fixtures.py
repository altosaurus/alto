"""
Make the recordings, pictures and icons of the example plugins that the plugin tests install, read and edit.

The packs' manifests are kept in `tests/packs/`, but their recordings, photographs and icons are not: the real ones are in the
tutorial repositories, and the plugin's author provides them. The tests only need sound files of the right names, lengths and
pitches, pictures of the right size, and icons that Alto accepts. This module writes a plucked sine tone for each pitch a
manifest names, a plain picture for each photograph and a plain icon for each tile icon, the first time it is asked, and
`.gitignore` keeps the files out of the repository. A pack's `image-sizes.json` gives the pixel size of each picture, because the
manifest's points and regions are checked against it.
"""

from __future__ import annotations

import json
import math
import os
import re
import struct
import wave
from pathlib import Path

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QPolygonF

RATE = 32_000  # the rate of the recordings the packs ship
# A plain tile icon: a ring, with the even-odd fill rule that the icon reader keeps.
ICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
    '<path fill-rule="evenodd" d="M12 4a8 8 0 1 0 0 16 8 8 0 0 0 0-16zM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10z"/></svg>\n'
)


def midi(name: str) -> int:
    """
    Read a pitch name such as ``Bb6`` or ``F#1`` as a MIDI number.

    Parameters
    ----------
    name : str
        A letter, an optional sharp (#) or flat (b), and an octave.

    Returns
    -------
    int
        The MIDI number, with C4 at 60.

    Examples
    --------
    >>> midi("A4"), midi("Bb3"), midi("F#1")
    (69, 58, 30)
    """
    match = re.fullmatch(r"([A-G])([#b]?)(-?\d+)", name)
    assert match is not None, name
    letter, accidental, octave = match.groups()
    semitone = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[letter] + {"#": 1, "b": -1, "": 0}[accidental]
    return 12 * (int(octave) + 1) + semitone


def tone(pitch: str, *, seconds: float) -> bytes:
    """
    Make a plucked tone, as 16-bit mono PCM.

    Parameters
    ----------
    pitch : str
        The pitch to sound, such as ``D4``.
    seconds : float
        The length. Keyword-only.

    Returns
    -------
    bytes
        The samples, which start loud, die away and end in silence.

    Examples
    --------
    >>> len(tone("A4", seconds=0.5))
    32000
    """
    frequency = 440 * 2 ** ((midi(pitch) - 69) / 12)
    count = round(RATE * seconds)
    samples = []
    for index in range(count):
        time = index / RATE
        attack = min(1.0, time / 0.004)
        fade = min(1.0, (seconds - time) / 0.05)
        samples.append(
            round(0.5 * 32767 * attack * fade * math.exp(-3 * time / seconds) * math.sin(2 * math.pi * frequency * time)),
        )
    return struct.pack(f"<{count}h", *samples)


def ensure_sounds(folder: Path, *, seconds: float) -> None:
    """
    Write the recording of every pitch the folder's manifest names, unless it is there already.

    Parameters
    ----------
    folder : Path
        An example pack's folder, holding `pack.json`.
    seconds : float
        How long each recording lasts. Keyword-only.

    Examples
    --------
    >>> import tempfile
    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     _ = (Path(tmp) / "pack.json").write_text('{"instruments": [{"samples": {"A4": "sounds/A4.wav"}}]}')
    ...     ensure_sounds(Path(tmp), seconds=0.1)
    ...     (Path(tmp) / "sounds/A4.wav").is_file()
    True
    """
    manifest = json.loads((folder / "pack.json").read_text(encoding="utf-8"))
    for instrument in manifest["instruments"]:
        for pitch, relative in instrument["samples"].items():
            target = folder / relative
            if target.is_file():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            partial = target.with_name(f"{target.name}.{os.getpid()}.part")
            with wave.open(str(partial), "wb") as sound:
                sound.setnchannels(1)
                sound.setsampwidth(2)
                sound.setframerate(RATE)
                sound.writeframes(tone(pitch, seconds=seconds))
            partial.replace(target)  # when tests run in several processes, one of them wins and the rest find the finished file


def ensure_pictures(folder: Path) -> None:
    """
    Write a plain picture of the right size for every photograph the folder's `image-sizes.json` lists, unless it is there.

    A photograph that an instrument's strings are calibrated on gets a dark band under them, where the neck would be, because
    some tests look at what is drawn over the neck. Another photograph is a different shade, so that views differ.

    Parameters
    ----------
    folder : Path
        An example pack's folder, holding `pack.json` and `image-sizes.json`.

    Examples
    --------
    >>> import tempfile
    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     _ = (Path(tmp) / "pack.json").write_text('{"instruments": []}')
    ...     _ = (Path(tmp) / "image-sizes.json").write_text('{"images/a.png": [40, 30]}')
    ...     ensure_pictures(Path(tmp))
    ...     QImage(str(Path(tmp) / "images/a.png")).size().width()
    40
    """
    sizes = json.loads((folder / "image-sizes.json").read_text(encoding="utf-8"))
    manifest = json.loads((folder / "pack.json").read_text(encoding="utf-8"))
    necks = {instrument["image"]: instrument["strings"] for instrument in manifest["instruments"] if instrument.get("strings")}
    for number, (relative, (width, height)) in enumerate(sizes.items()):
        target = folder / relative
        if target.is_file():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        picture = QImage(width, height, QImage.Format.Format_RGB32)
        picture.fill(QColor("#c8c8c8" if relative in necks else f"#{0xA0 + 16 * number:02x}a0a0"))
        if relative in necks:
            first, last = necks[relative][0], necks[relative][-1]
            band = QPolygonF([QPointF(*first["nut"]), QPointF(*first["bridge"]), QPointF(*last["bridge"]), QPointF(*last["nut"])])
            painter = QPainter(picture)
            painter.setBrush(QColor("#101010"))
            pen = QPen(QColor("#101010"), 28)  # a few pixels of margin around the strings
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPolygon(band)
            painter.end()
        partial = target.with_name(f"{os.getpid()}.part{target.suffix}")
        assert picture.save(str(partial)), relative
        partial.replace(target)


def ensure_icons(folder: Path) -> None:
    """
    Write a plain icon for every tile icon the folder's manifest names, unless it is there already.

    The real icons belong to the plugin and its author. The tests only need files that Alto accepts as icons.

    Parameters
    ----------
    folder : Path
        An example pack's folder, holding `pack.json`.

    Examples
    --------
    >>> import tempfile
    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     text = '{"exercises": [{"icon": "icons/a.svg"}], "lessons": [{"icon": "icons/b.svg"}]}'
    ...     _ = (Path(tmp) / "pack.json").write_text(text)
    ...     ensure_icons(Path(tmp))
    ...     sorted(path.name for path in (Path(tmp) / "icons").iterdir())
    ['a.svg', 'b.svg']
    """
    manifest = json.loads((folder / "pack.json").read_text(encoding="utf-8"))
    wanted = {item["icon"] for key in ("exercises", "lessons") for item in manifest.get(key, []) if "icon" in item}
    for relative in wanted:
        target = folder / relative
        if target.is_file():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        partial = target.with_name(f"{os.getpid()}.part{target.suffix}")
        partial.write_text(ICON)
        partial.replace(target)
