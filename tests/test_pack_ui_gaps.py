"""
Tests for the plugin windows and widgets in cases the other tests do not reach.

They cover refused installs, a locked folder, a picture that cannot be drawn, a lesson step with nothing to answer, and the
range steps of a keyboard exercise.
"""

from __future__ import annotations

import shutil
import time
from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QLockFile, QPointF, QRectF
from PySide6.QtGui import QImage, QPainter, QPixmap
from PySide6.QtWidgets import QApplication

from alto.audio import INSTRUMENT_BY_KEY
from alto.exercises.base import REGISTRY, FingerboardPosition, PicturePosition
from alto.exercises.packs import InstalledPlugin, installed_plugins, load_packs
from alto.instrument_packs import INSTALLED, PackKeyboard, PackString
from alto.lessons import LESSONS
from alto.ui import glossary, main_window, plugins_dialog
from alto.ui.exercise_settings import load_pack_options
from alto.ui.fingerboard import FingerboardWidget, ruler_base
from alto.ui.glossary import GlossaryPage
from alto.ui.instrument_picker import InstrumentPicker
from alto.ui.lesson import LessonsPage
from alto.ui.pack_settings_panel import PackKeyboardSettingsPanel
from alto.ui.plugins_dialog import PluginsDialog
from alto.ui.store import store
from test_harpsichord_pack import _install as install_harpsichord
from test_harpsichord_pack import _intervals
from test_instrument_packs import isolated_packs  # noqa: F401  # the autouse fixture that keeps registrations local
from viola_pack import FOLDER as VIOLA_FOLDER
from viola_pack import ZIP as VIOLA_ZIP

VIOLA_KEY = "pack.viola.bowed-viola"
HARPSICHORD_KEY = "pack.harpsichord.flemish-harpsichord"


def install_viola(tmp_path: Path) -> None:
    """
    Install the viola example into an isolated plugins folder.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder's parent.
    """
    shutil.copytree(VIOLA_FOLDER, tmp_path / "plugins" / "viola")
    assert load_packs(tmp_path / "plugins") == []


def test_a_ruler_over_one_point_still_has_a_direction(tmp_path: Path, app: QApplication) -> None:
    """
    Draw a ruler on strings whose nut and bridge are the same point, without dividing by their distance.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder's parent.
    app : QApplication
        Shared Qt application.
    """
    del app
    install_viola(tmp_path)
    model = INSTALLED[VIOLA_KEY]
    point = PackString("C3", (10.0, 10.0), (10.0, 10.0))
    base, unit, spacing = ruler_base(replace(model, strings=(point, point)), step=3)
    assert (unit.x(), unit.y(), spacing) == (0.0, -1.0, 1.0) and base.x() == 10.0


def test_a_picture_that_cannot_be_drawn_says_so_or_draws_nothing(tmp_path: Path, app: QApplication) -> None:
    """
    Cover the ways a fingerboard picture can fail: no image, a neck outside the picture, a window too small, a ruler on a picture.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder's parent.
    app : QApplication
        Shared Qt application.
    """
    del app
    install_viola(tmp_path)
    model = INSTALLED[VIOLA_KEY]
    position = FingerboardPosition(("C3", "G3", "D4", "A4"), 0, "E3", instrument=VIOLA_KEY)

    def fresh(width: int, height: int) -> FingerboardWidget:
        """
        Make a fingerboard showing the position at a size.

        Parameters
        ----------
        width : int
            The width in pixels.
        height : int
            The height in pixels.

        Returns
        -------
        FingerboardWidget
            The widget.
        """
        widget = FingerboardWidget()
        widget.resize(width, height)
        widget.show_position(position)
        return widget

    blank = fresh(720, 270)
    blank._image = QPixmap()  # noqa: SLF001
    assert blank.grab().size().width() == 720  # "Instrument image unavailable."
    outside = fresh(720, 270)
    elsewhere = tuple(
        PackString(string.pitch, (-90000.0 - i, -90000.0), (-80000.0 - i, -90000.0)) for i, string in enumerate(model.strings)
    )
    outside.model = replace(model, strings=elsewhere)
    assert not outside.grab().isNull()  # the neck is outside the picture, so there is nothing to show of it
    assert not fresh(2, 2).grab().isNull()  # too small for the picture to have a size
    widget = fresh(720, 270)
    drawn = QImage(10, 10, QImage.Format.Format_RGB32)
    painter = QPainter(drawn)
    marked = PicturePosition(VIOLA_KEY, (100.0, 100.0), "", 40.0)
    widget.show_position(marked)
    widget._draw_ruler(painter, gap=10.0, marker=QPointF(1, 1), scale=1.0)  # noqa: SLF001  # a picture has no ruler
    widget._draw_view(  # noqa: SLF001
        painter,
        image=QPixmap(),
        source=QRectF(0, 0, 10, 10),
        pane=QRectF(0, 0, 0, 0),
        marker=QPointF(1, 1),
        gap=1.0,
    )
    painter.end()


def test_a_picture_without_a_marker_shows_the_right_place_once_it_is_known(tmp_path: Path, app: QApplication) -> None:
    """
    Show the right place on a picture that has no marker after the learner has answered.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder's parent.
    app : QApplication
        Shared Qt application.
    """
    del app
    install_viola(tmp_path)
    widget = FingerboardWidget()
    widget.resize(720, 270)
    widget.show_position(PicturePosition(VIOLA_KEY, (500.0, 300.0), "", 40.0, (), False))
    assert not widget.grab().isNull()
    widget.show_target((500.0, 300.0))
    assert not widget.grab().isNull()


def test_manuals_the_next_picture_lacks_are_removed(tmp_path: Path, app: QApplication) -> None:
    """
    Remove the drawn manuals that the next instrument does not have.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder's parent.
    app : QApplication
        Shared Qt application.
    """
    del app
    assert install_harpsichord(tmp_path) == []
    model = INSTALLED[HARPSICHORD_KEY]
    picture = _intervals().cards[0].picture
    assert picture is not None
    widget = FingerboardWidget()
    widget.show_position(picture)
    assert set(widget._manuals) == {"Upper manual", "Lower manual"}  # noqa: SLF001
    solo = replace(model, keyboards=(PackKeyboard("Solo", "C3", "C5"),))
    widget._show_manuals(solo, position=replace(picture, keys=(("Solo", "C4"), ("Solo", "E4")), notes=("C4", "E4")))  # noqa: SLF001
    assert set(widget._manuals) == {"Solo"}  # noqa: SLF001


def test_an_unlisted_installed_sound_is_described_by_its_plugin(tmp_path: Path, app: QApplication) -> None:
    """
    Describe an installed instrument that has no sound information of its own by the plugin that supplies it.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder's parent.
    app : QApplication
        Shared Qt application.
    """
    del app
    member = replace(INSTRUMENT_BY_KEY["flute"], key="pack.demo.flute", pack_name="Demo plugin")
    info = InstrumentPicker()._info(member)  # noqa: SLF001
    assert info.source == "Demo plugin" and "installed instrument pack" in info.summary


def test_a_term_whose_lessons_are_gone_says_so(tmp_path: Path, app: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Say that no lessons go with a glossary term when none of its lessons is installed.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder's parent.
    app : QApplication
        Shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        List no lessons.
    """
    del app
    install_viola(tmp_path)
    page = GlossaryPage()
    page.search.setText("scroll")
    monkeypatch.setattr(glossary, "LESSONS", [])
    page._show_activities(1)  # noqa: SLF001
    labels = [page.activity_tiles.itemAt(i).widget() for i in range(page.activity_tiles.count())]
    assert any(getattr(label, "text", lambda: "")() == "No lessons go with this term yet." for label in labels)


def test_a_step_with_no_task_ignores_answers_and_clicks(tmp_path: Path, app: QApplication) -> None:
    """
    Ignore an answer or a click on a lesson step that asks nothing.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder's parent.
    app : QApplication
        Shared Qt application.
    """
    del app
    install_viola(tmp_path)
    lesson = next(item for item in LESSONS if item.key == "pack.viola.parts-of-the-viola")
    page = LessonsPage(lesson.key, step=0)
    number = next(n for n, step in enumerate(lesson.steps) if step.make_task is None)
    page.view.go(to=number)
    view = page.view._views[number]  # noqa: SLF001
    assert view.task is None
    view._answered("anything", button=None)  # noqa: SLF001
    view._clicked(1.0, 1.0)  # noqa: SLF001
    assert not view._done  # noqa: SLF001


def test_installing_a_file_that_is_not_a_pack_is_reported(
    tmp_path: Path,
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Tell the learner why a chosen file could not be installed.

    Parameters
    ----------
    tmp_path : Path
        Isolated Alto data folder.
    app : QApplication
        Shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Choose the file and observe the warning.
    """
    del app
    monkeypatch.setattr(main_window, "database_path", lambda: tmp_path / "alto.db")
    window = main_window.MainWindow()
    warning = Mock()
    monkeypatch.setattr(main_window.QMessageBox, "warning", warning)
    notes = tmp_path / "notes.zip"
    notes.write_bytes(b"not a zip")
    monkeypatch.setattr(main_window.QFileDialog, "getOpenFileName", lambda *args, **kwargs: (str(notes), ""))
    window.install_plugin()
    assert "Could not read the pack ZIP" in warning.call_args.args[2]


def test_uninstalling_waits_for_another_change_and_reports_a_disk_error(
    tmp_path: Path,
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Refuse to remove a plugin while another change holds the folder, and report a disk error as a message.

    Parameters
    ----------
    tmp_path : Path
        Isolated plugins folder.
    app : QApplication
        Shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Confirm the question and observe the warnings.
    """
    del app
    plugins = tmp_path / "plugins"
    plugins.mkdir()
    monkeypatch.setattr(main_window, "database_path", lambda: tmp_path / "alto.db")
    window = main_window.MainWindow()
    warning, restart = Mock(), Mock()
    monkeypatch.setattr(window, "restart_app", restart)
    monkeypatch.setattr(main_window.QMessageBox, "warning", warning)
    monkeypatch.setattr(main_window.QMessageBox, "question", lambda *args: main_window.QMessageBox.StandardButton.Yes)
    shutil.copyfile(VIOLA_ZIP, plugins / "viola.zip")
    plugin = installed_plugins(plugins)[0][0]
    lock = QLockFile(str(plugins / ".install.lock"))
    assert lock.tryLock(0)
    window.uninstall_plugin(plugin)
    lock.unlock()
    assert "in progress" in warning.call_args.args[2]
    real = Path.is_file

    def is_file(self: Path) -> bool:
        """
        Fail for the plugin's ZIP only.

        Parameters
        ----------
        self : Path
            The path being checked.

        Returns
        -------
        bool
            What the real check says.

        Raises
        ------
        OSError
            For the plugin's ZIP.
        """
        if self.name == "viola.zip":
            raise OSError("Input/output error")
        return real(self)

    monkeypatch.setattr(Path, "is_file", is_file)
    window.uninstall_plugin(plugin)
    assert warning.call_args.args[2] == "Input/output error"
    restart.assert_not_called()


def test_the_plugins_dialog_closes_and_reports_a_failed_worker(
    tmp_path: Path,
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Close when idle, and show the message of a release worker that failed unexpectedly or reported an error.

    Parameters
    ----------
    tmp_path : Path
        Isolated plugins folder.
    app : QApplication
        Shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Make the release worker fail.
    """
    dialog = PluginsDialog(tmp_path / "plugins")
    dialog.done(0)
    assert dialog.result() == 0

    def broken(code: str, *, folder: Path, selected: InstalledPlugin | None = None) -> None:
        """
        Fail in a way nobody planned for.

        Parameters
        ----------
        code : str
            The registration code.
        folder : Path
            The plugins folder.
        selected : InstalledPlugin or None
            The plugin to update.

        Raises
        ------
        RuntimeError
            Always.
        """
        raise RuntimeError("the network is down")

    monkeypatch.setattr(plugins_dialog, "install_registered", broken)
    dialog._start_release("42", selected=None)  # noqa: SLF001
    deadline = time.monotonic() + 5
    while dialog._busy and time.monotonic() < deadline:  # noqa: SLF001
        app.processEvents()
        time.sleep(0.005)
    assert dialog.status.text() == "the network is down"
    dialog._finish_release(None, "The registry is unreadable.")  # noqa: SLF001
    assert dialog.status.text() == "The registry is unreadable."


def test_a_saved_range_that_is_not_a_range_is_ignored(tmp_path: Path, app: QApplication) -> None:
    """
    Fall back to the whole range when the saved range cannot be read.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder's parent.
    app : QApplication
        Shared Qt application.
    """
    del app
    install_viola(tmp_path)
    cls = next(c for c in REGISTRY if c.__name__.endswith("first-position"))
    store().setValue(f"packExercises/{cls.__name__}/range", "wide")
    load_pack_options()
    assert cls.options().ranges[cls.range_clef] == cls.span  # type: ignore[attr-defined]


def test_the_keyboard_settings_step_and_slide(tmp_path: Path, app: QApplication) -> None:
    """
    Step the range by a key at either end, slide to a page, and ignore edits for pages the exercise does not offer.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder's parent.
    app : QApplication
        Shared Qt application.
    """
    del app
    assert install_harpsichord(tmp_path) == []
    cls = type(_intervals())
    panel = PackKeyboardSettingsPanel(cls)
    low, high = cls.chosen_keys()
    panel._step("low", delta=1)  # noqa: SLF001
    panel._step("high", delta=-1)  # noqa: SLF001
    assert cls.chosen_keys() == (low + 1, high - 1)
    panel._set_keys(60, 60)  # noqa: SLF001  # a range of no keys is refused
    assert cls.chosen_keys() == (low + 1, high - 1)
    panel._go(1)  # noqa: SLF001
    assert panel.stack.sliding
    plain = type("Plain", (cls,), {"controls": {"sound": "Sound"}})
    bare = PackKeyboardSettingsPanel(plain)
    bare._manuals_edited()  # noqa: SLF001
    bare._intervals_edited()  # noqa: SLF001
    assert bare.manual_page is None and bare.interval_page is None


def test_the_release_worker_reports_each_outcome(tmp_path: Path, app: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Report an installed release, an up-to-date plugin and a failure through the dialog's signal, from the thread that ran it.

    Parameters
    ----------
    tmp_path : Path
        Isolated plugins folder.
    app : QApplication
        Shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Supply the outcomes.
    """
    del app
    monkeypatch.setattr(plugins_dialog.QMessageBox, "question", lambda *args: plugins_dialog.QMessageBox.StandardButton.No)
    dialog = PluginsDialog(tmp_path / "plugins")
    heard: list[tuple[str | None, str]] = []
    dialog._release_finished.connect(lambda result, error: heard.append((result, error)))  # noqa: SLF001
    outcomes: list[str | None | Exception] = [
        "Viola Instrument Pack (summer)",
        None,
        ValueError("No registered plugin has code 9."),
    ]

    def answer(code: str, *, folder: Path, selected: InstalledPlugin | None = None) -> str | None:
        """
        Give the next planned outcome.

        Parameters
        ----------
        code : str
            The registration code.
        folder : Path
            The plugins folder.
        selected : InstalledPlugin or None
            The plugin to update.

        Returns
        -------
        str or None
            The installed plugin, or None if it was up to date.

        Raises
        ------
        ValueError
            When the planned outcome is a failure.
        """
        outcome = outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(plugins_dialog, "install_registered", answer)
    for _ in range(3):
        dialog._run_release("9", selected=None)  # noqa: SLF001
    assert heard == [("Viola Instrument Pack (summer)", ""), (None, ""), (None, "No registered plugin has code 9.")]
