#!/usr/bin/env python
"""Build hits.png for a curated score. Run with the project Python and the versioned excerpt directory as an argument."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PySide6.QtCore import QByteArray, QRectF
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication


def build_hit_map(folder: Path) -> QImage:
    """
    Rasterize marker ownership from the same artwork used by the exercise.

    Each pass measures three components in the red, green, and blue channels. Black ink from surrounding music
    still occludes the measured shapes. At crossings a foreground symbol takes precedence over a staff or ledger line.

    Parameters
    ----------
    folder : Path
        Versioned passage containing score.svg and excerpt.json.

    Returns
    -------
    QImage
        Sixteen-bit grayscale image. Zero denotes background and one is the first marker.

    Raises
    ------
    ValueError
        If a marker is missing, duplicated, or completely obscured.

    Examples
    --------
    Run with QT_QPA_PLATFORM=offscreen when regenerating the maps on a headless system.
    """
    terms = json.loads((folder / "excerpt.json").read_text(encoding="utf-8"))["targets"]
    svg = (folder / "score.svg").read_bytes()
    bounds = QSvgRenderer(QByteArray(svg)).viewBoxF()
    width = 1500
    height = round(width * bounds.height() / bounds.width())
    ids = np.zeros((height, width), dtype=np.uint16)
    strongest = np.zeros((height, width), dtype=np.uint8)
    image = QImage(width, height, QImage.Format.Format_RGBX8888)
    for first in range(0, len(terms), 3):
        data = svg
        batch = terms[first : first + 3]
        for index, color in enumerate(("red", "lime", "blue")[: len(batch)], first):
            marker = f'id="mark-{index}"'.encode()
            if data.count(marker) != 1:
                raise ValueError(f"Expected one SVG element named mark-{index} in {folder}")
            data = data.replace(marker, marker + f' fill="{color}" color="{color}"'.encode())
        image.fill(QColor("black"))
        with QPainter(image) as painter:
            QSvgRenderer(QByteArray(data)).render(painter, QRectF(image.rect()))
        pixels = np.frombuffer(image.constBits(), dtype=np.uint8).reshape(height, width, 4)
        for channel, term in enumerate(batch):
            coverage = pixels[:, :, channel]
            if term in {"Staff line", "Ledger line"}:
                coverage = coverage // 3
            visible = (coverage > 9) & (coverage > strongest)
            ids[visible] = first + channel + 1
            strongest[visible] = coverage[visible]
    if set(np.unique(ids)) != set(range(len(terms) + 1)):
        raise ValueError(f"Every marker in {folder} needs visible ink")
    return QImage(ids.data, width, height, ids.strides[0], QImage.Format.Format_Grayscale16).copy()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    args = parser.parse_args()
    app = QApplication([])
    if not build_hit_map(args.folder).save(str(args.folder / "hits.png")):
        raise SystemExit("Could not save the hit map.")
