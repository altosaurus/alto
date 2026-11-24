"""
The downloadable example and the plugin author's walkthrough work in
Alto.
"""

from __future__ import annotations

import json
import random
import re
import shutil
import wave
from collections.abc import Callable, Iterator
from dataclasses import replace
from math import dist
from pathlib import Path
from unittest.mock import Mock
from zipfile import ZipFile

import pytest
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QImage, QMovie
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QMenu, QPushButton

from alto import settings
from alto.audio import INSTRUMENT_BY_KEY, Sounds, read_wav, sounds
from alto.exercises.base import (
    REGISTRY,
    FingerboardPosition,
    PicturePosition,
    Question,
)
from alto.exercises.packs import (
    PackExercise,
    install_pack,
    installed_plugins,
    load_packs,
    read_pack,
)
from alto.instrument_packs import INSTALLED, read_positions, read_sound_info
from alto.learning import Database, Learner
from alto.lessons import LESSONS
from alto.terms import PLUGIN_TERMS
from alto.theory.pitch import Note
from alto.ui import database_page, instrument_picker, main_window
from alto.ui.anki_exporter import card_fields
from alto.ui.exercise_settings import (
    load_pack_options,
    save_pack_options,
)
from alto.ui.exercise_view import ExerciseView
from alto.ui.fingerboard import (
    FingerboardWidget,
    neck_view,
    ruler_base,
    ruler_reach,
)
from alto.ui.pack_settings_panel import PackSettingsPanel
from alto.ui.plugins_dialog import PluginsDialog
from alto.ui.question_preview import QuestionPreview
from alto.ui.settings_panel import settings_panel_for
from viola_pack import (
    MANIFEST,
    TUTORIAL,
    ZIP,
    needs_tutorial,
)

VIOLA = MANIFEST
VIOLA_ZIP = ZIP


@pytest.mark.parametrize("restart_now", [False, True])
def test_install_from_file(
    tmp_path: Path,
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    restart_now: bool,
) -> None:
    """
    Install the downloadable ZIP through Tools and activate it at the
    chosen restart.

    Parameters
    ----------
    tmp_path : Path
        Isolated Alto data directory.
    app : QApplication
        Shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Supply the user's selections and intercept relaunch.
    restart_now : bool
        Choice at the restart prompt.
    """
    del app
    folder = tmp_path / "plugins"
    source = VIOLA_ZIP
    window = main_window.MainWindow()
    restart, warning, question = Mock(), Mock(), Mock()
    pick = Mock(side_effect=[("", ""), (str(source), "")])
    buttons = main_window.QMessageBox.StandardButton
    question.return_value = buttons.Yes if restart_now else buttons.No
    monkeypatch.setattr(
        main_window,
        "database_path",
        lambda: tmp_path / "alto.db",
    )
    monkeypatch.setattr(main_window.QFileDialog, "getOpenFileName", pick)
    monkeypatch.setattr(main_window.QMessageBox, "question", question)
    monkeypatch.setattr(main_window.QMessageBox, "warning", warning)
    monkeypatch.setattr(window, "restart_app", restart)
    window.install_plugin()
    assert not folder.exists() and not question.called and not restart.called
    window.install_plugin()
    assert (folder / source.name).read_bytes() == source.read_bytes()
    assert load_packs(folder) == []
    sound = INSTALLED["pack.viola.bowed-viola"].sound
    assert sound is not None and len(sound.samples) == 49
    assert restart.call_count == int(restart_now)
    question.assert_called_once()
    assert "Viola Instrument Pack" in question.call_args.args[2]
    warning.assert_not_called()


def test_installed_pack_sound_in_settings(
    tmp_path: Path,
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Preview and select the downloadable viola independently of the
    built-in viola.

    Parameters
    ----------
    tmp_path : Path
        Temporary installation and preview cache.
    app : QApplication
        Shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Isolate the selected sound and observe the preview request.
    """
    del app
    install_pack(VIOLA_ZIP, folder=tmp_path)
    assert load_packs(tmp_path) == []
    key = "pack.viola.bowed-viola"
    preview = Mock()
    monkeypatch.setattr(sounds, "preview", preview)
    monkeypatch.setattr(sounds, "instrument", "piano")
    monkeypatch.setattr(instrument_picker, "save_instrument", Mock())
    picker = instrument_picker.InstrumentPicker()
    picker.select(key)
    assert picker.title.text() == "Bowed viola"
    facts = [label.text() for label in picker.findChildren(QLabel)]
    assert (
        "Viola Instrument Pack" in facts
        and "49 notes, C3 to C7, every semitone" in facts
    )
    assert (
        "Each note ends as the next begins" in facts
    )  # the pack marks its bowed notes as sustained
    text = " ".join(facts)
    for expected in (
        "TinySOL v6.0 (2020)",
        "doi.org/10.5281/zenodo.3685367",
        "Not named by TinySOL",
        "between 1996 and 1999",
        "mezzo-forte",
        "CC BY 4.0",
        "17 of these 49 takes",
    ):
        assert expected in text
    use, hear = picker.buttons[key]
    hear.click()
    preview.assert_called_once_with(key, midis=instrument_picker.PREVIEW)
    use.click()
    assert sounds.instrument == key
    picker.select("viola_bowed")
    assert picker.title.text() == "Viola"

    player = Sounds()
    player._dir = tmp_path / "cache"
    inst = INSTRUMENT_BY_KEY[key]
    rendered = player._preview_file(inst, midis=(62,), step_ms=300)
    assert max(abs(value) for value in read_wav(rendered)[0]) > 0.02
    other_take = replace(inst, samples=((62, VIOLA.parent / "sounds/C3.wav"),))
    assert (
        player._preview_file(other_take, midis=(62,), step_ms=300) != rendered
    )


def test_install_rejects_invalid_or_conflicting_packs(tmp_path: Path) -> None:
    """
    Preserve installed ZIPs and editable folders when a download is
    invalid or already installed.

    Parameters
    ----------
    tmp_path : Path
        Directory for downloads and installations.
    """
    folder = tmp_path / "plugins"
    source = tmp_path / "new.zip"
    source.write_bytes(b"unreadable")
    with pytest.raises(ValueError, match="pack ZIP"):
        install_pack(source, folder=folder)
    with ZipFile(source, "w") as archive:
        archive.write(VIOLA, "pack.json")
    with pytest.raises(ValueError, match="Missing file"):
        install_pack(source, folder=folder)
    assert not list(folder.iterdir())
    shutil.copyfile(VIOLA_ZIP, source)
    existing = folder / source.name
    existing.write_bytes(b"existing file")
    with pytest.raises(ValueError, match="filename"):
        install_pack(source, folder=folder)
    assert existing.read_bytes() == b"existing file"
    shutil.copytree(VIOLA.parent, folder / "editable")
    with pytest.raises(ValueError, match="already installed as editable"):
        install_pack(source, folder=folder)
    (folder / "editable").rename(tmp_path / "editable")
    shutil.copyfile(source, folder / "renamed.zip")
    with pytest.raises(ValueError, match="already installed as renamed.zip"):
        install_pack(source, folder=folder)
    assert sorted(p.name for p in folder.iterdir()) == [
        "new.zip",
        "renamed.zip",
    ]


def test_unnamed_pack_cannot_install_or_load(tmp_path: Path) -> None:
    """
    Require a top-level name even when a pack already has instrument
    names and exercise titles.

    Parameters
    ----------
    tmp_path : Path
        Temporary download and plugins directory.
    """
    data = json.loads(VIOLA.read_text())
    del data["name"]
    source = tmp_path / "unnamed.zip"
    with ZipFile(source, "w") as archive:
        archive.writestr("pack.json", json.dumps(data))
    folder = tmp_path / "plugins"
    with pytest.raises(ValueError, match='top-level "name"'):
        install_pack(source, folder=folder)
    assert not list(folder.iterdir())
    shutil.copyfile(source, folder / source.name)
    assert 'top-level "name"' in load_packs(folder)[0]
    assert "pack.viola.bowed-viola" not in INSTALLED


@pytest.mark.parametrize(
    "value",
    [
        "TinySOL",
        {"licence": "CC BY 4.0"},
        {"terms": 5},
        {"note": "<b>bold</b>"},
        {"summary": "x" * 801},
        {"source_url": "javascript:alert(1)"},
        {"source_url": "ftp://example.org/a"},
        {"source_url": "https://example.org/a b"},
    ],
)
def test_sound_info_rejects_bad_entries(value: object) -> None:
    """
    Refuse entries that are not plain text or whose link is not a web
    address.

    Parameters
    ----------
    value : object
        A malformed sound_info entry.
    """
    with pytest.raises(ValueError, match="sound_info"):
        read_sound_info(
            value,
            where="pack.viola.bowed-viola",
            pack_name="Viola Instrument Pack",
        )


def test_sound_info_defaults_to_the_plugin_name() -> None:
    """
    Name the plugin as the source when a pack gives only some facts, and
    none when it gives no entry.
    """
    info = read_sound_info(
        {"performer": " A. Player "},
        where="pack.viola.bowed-viola",
        pack_name="Viola Instrument Pack",
    )
    assert (
        info is not None
        and info.source == "Viola Instrument Pack"
        and info.performer == "A. Player"
    )
    assert (
        info.summary == "Recordings supplied by an installed instrument pack."
        and info.source_url == ""
    )
    assert (
        read_sound_info(
            None,
            where="pack.viola.bowed-viola",
            pack_name="Viola Instrument Pack",
        )
        is None
    )


@pytest.mark.parametrize(
    "value",
    [
        "1st",
        [{"name": "1st"}],
        [{"name": "1st", "half_steps": 2, "color": "red"}],
        [{"name": "", "half_steps": 2}],
        [{"name": "<b>1st</b>", "half_steps": 2}],
        [{"name": "a very long position name", "half_steps": 2}],
        [{"name": "1st", "half_steps": 2.5}],
        [{"name": "1st", "half_steps": 0}],
        [{"name": "1st", "half_steps": 99}],
        [{"name": "1st", "half_steps": True}],
        [{"name": "2nd", "half_steps": 3}, {"name": "1st", "half_steps": 2}],
        [{"name": "1st", "half_steps": 2}, {"name": "again", "half_steps": 2}],
        [{"name": str(i), "half_steps": i} for i in range(1, 14)],
    ],
)
def test_positions_reject_bad_entries(value: object) -> None:
    """
    Refuse positions that are not short, plain-text names at ascending
    whole half steps.

    Parameters
    ----------
    value : object
        A malformed positions entry.
    """
    with pytest.raises(ValueError, match="osition"):
        read_positions(value, where="pack.viola.bowed-viola")


def _edited_pack(
    tmp_path: Path,
    *,
    edit: Callable[[dict], None],
    pack_id: str = "edited-viola",
) -> Path:
    """
    Copy the example pack into a folder with its manifest changed by
    ``edit``.

    Parameters
    ----------
    tmp_path : Path
        Where the copy goes.
    edit : Callable[[dict], None]
        Changes the parsed manifest in place. Keyword-only.
    pack_id : str, default "edited-viola"
        The copy's pack id, so it does not clash with the example.
        Keyword-only.

    Returns
    -------
    Path
        The copy's pack.json.
    """
    folder = tmp_path / pack_id
    shutil.copytree(VIOLA.parent, folder)
    manifest = json.loads((folder / "pack.json").read_text())
    manifest["id"] = pack_id
    edit(manifest)
    (folder / "pack.json").write_text(json.dumps(manifest))
    return folder / "pack.json"


def test_positions_and_wording_come_from_the_pack(
    tmp_path: Path,
    app: QApplication,
) -> None:
    """
    Take positions, descriptions and prompts from the manifest, and fall
    back to neutral text when a pack gives none.

    Parameters
    ----------
    tmp_path : Path
        Isolated copies of the example pack.
    app : QApplication
        Shared Qt application.
    """
    del app
    named = read_pack(VIOLA)[0]
    assert (
        named.description == "Name the note marked on the viola's fingerboard."
    )  # the viola pack's own words
    assert named.cards[0].prompt == "Name the note at the dot."

    def strip(manifest: dict) -> None:
        """
        Remove everything instrument-specific that the example supplies.

        Parameters
        ----------
        manifest : dict
            The parsed manifest, changed in place.
        """
        del manifest["instruments"][0]["positions"]
        del manifest["exercises"][0]["description"]

    bare = read_pack(_edited_pack(tmp_path, edit=strip))[0]
    model = bare.instruments["pack.edited-viola.bowed-viola"]
    assert (
        model.positions == ()
        and "ruler" not in bare.description
        and "C3, G3, D4, A4" in bare.description
    )
    far = replace(model, positions=((14, "9th"),))
    assert ruler_reach(model) == 12 and ruler_reach(far) == 14

    def reword(manifest: dict) -> None:
        """
        Give the exercise its own prompt.

        Parameters
        ----------
        manifest : dict
            The parsed manifest, changed in place.
        """
        manifest["exercises"][0]["prompt"] = "Which pitch is under the dot?"

    assert (
        read_pack(
            _edited_pack(tmp_path, edit=reword, pack_id="reworded-viola"),
        )[0]
        .cards[0]
        .prompt
        == "Which pitch is under the dot?"
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("description", "<b>bold</b>"),
        ("description", "x" * 401),
        ("description", 5),
        ("prompt", ""),
        ("prompt", "x" * 121),
        ("prompt", "<i>what</i>"),
    ],
)
def test_exercise_wording_is_plain_text(
    tmp_path: Path,
    app: QApplication,
    field: str,
    value: object,
) -> None:
    """
    Refuse exercise wording that is not plain text of a sensible length.

    Parameters
    ----------
    tmp_path : Path
        An isolated copy of the example pack.
    app : QApplication
        Shared Qt application.
    field : str
        The manifest field under test.
    value : object
        A bad value for it.
    """
    del app

    def damage(manifest: dict) -> None:
        """
        Put the bad value on the fingerboard exercise.

        Parameters
        ----------
        manifest : dict
            The parsed manifest, changed in place.
        """
        manifest["exercises"][0][field] = value

    with pytest.raises(ValueError, match="plain-text"):
        read_pack(_edited_pack(tmp_path, edit=damage))


def test_sustained_notes_come_from_the_pack(
    tmp_path: Path,
    app: QApplication,
) -> None:
    """
    Let a pack say whether its notes are sustained, as a bowed
    instrument's are, and refuse anything but true or false.

    Parameters
    ----------
    tmp_path : Path
        Isolated copies of the example pack.
    app : QApplication
        Shared Qt application.
    """
    del app
    key = "pack.viola.bowed-viola"
    sound = read_pack(VIOLA)[0].instruments[key].sound
    assert sound is not None and sound.sustained

    def plucked(manifest: dict) -> None:
        """
        Leave the flag out, as a plucked instrument's pack would.

        Parameters
        ----------
        manifest : dict
            The parsed manifest, changed in place.
        """
        del manifest["instruments"][0]["sustained"]

    ringing = (
        read_pack(_edited_pack(tmp_path, edit=plucked))[0]
        .instruments["pack.edited-viola.bowed-viola"]
        .sound
    )
    assert ringing is not None and not ringing.sustained

    def wrong(manifest: dict) -> None:
        """
        Give the flag a value that is not true or false.

        Parameters
        ----------
        manifest : dict
            The parsed manifest, changed in place.
        """
        manifest["instruments"][0]["sustained"] = "yes"

    with pytest.raises(ValueError, match="sustained"):
        read_pack(_edited_pack(tmp_path, edit=wrong, pack_id="wrong-viola"))


@pytest.mark.parametrize("selected", ["viola.zip", "editable"])
def test_uninstall_plugin(
    tmp_path: Path,
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    selected: str,
) -> None:
    """
    Remove only the chosen installation, after confirming, and restart
    only after a successful move.

    Parameters
    ----------
    tmp_path : Path
        Isolated plugins folder and simulated trash.
    app : QApplication
        Shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Keep dialogs, trash, and restarts inside the test.
    selected : str
        Name of the selected installation.
    """
    del app
    plugins = tmp_path / "plugins"
    plugins.mkdir()
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(
        main_window,
        "database_path",
        lambda: tmp_path / "alto.db",
    )
    window = main_window.MainWindow()
    restart, warning, question = Mock(), Mock(), Mock()
    monkeypatch.setattr(window, "restart_app", restart)
    monkeypatch.setattr(main_window.QMessageBox, "warning", warning)
    monkeypatch.setattr(main_window.QMessageBox, "question", question)
    (plugins / "notes.txt").touch()
    assert installed_plugins(plugins) == ([], [])
    shutil.copy(VIOLA_ZIP, plugins / "viola.zip")
    shutil.copytree(VIOLA.parent, plugins / "editable")
    manifest = plugins / "editable" / "pack.json"
    data = json.loads(manifest.read_text())
    data["id"] = "student-strings"
    manifest.write_text(json.dumps(data))
    (plugins / "editable" / "draft.txt").write_text("Work in progress")
    listed = {
        plugin.path.name: plugin for plugin in installed_plugins(plugins)[0]
    }
    assert sorted(listed) == ["editable", "viola.zip"]
    plugin = listed[selected]
    assert plugin.title == "Viola Instrument Pack"
    file = Mock()
    make_file = Mock(return_value=file)
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(main_window, "QFile", make_file)
    buttons = main_window.QMessageBox.StandardButton
    question.return_value = buttons.No
    window.uninstall_plugin(plugin)
    make_file.assert_not_called()
    assert (
        "Viola Instrument Pack" in question.call_args.args[2]
        and selected in question.call_args.args[2]
    )
    question.return_value = buttons.Yes
    window.uninstall_plugin(
        replace(plugin, snapshot=plugins.lstat()),
    )  # the entry was replaced since it was listed
    make_file.assert_not_called()
    assert warning.call_count == 1
    file.moveToTrash.return_value = False
    window.uninstall_plugin(plugin)
    assert warning.call_count == 2
    restart.assert_not_called()
    file.moveToTrash.side_effect = lambda: (plugins / selected).rename(
        tmp_path / selected,
    )
    window.uninstall_plugin(plugin)
    make_file.assert_called_with(str(plugins / selected))
    restart.assert_called_once_with(quit_on_failure=True)
    assert (tmp_path / selected).exists() and (plugins / "notes.txt").is_file()
    assert load_packs(plugins) == []
    remaining = "student-strings" if selected == "viola.zip" else "viola"
    assert set(INSTALLED) == {f"pack.{remaining}.bowed-viola"}
    assert {
        cls.__name__ for cls in REGISTRY if cls.__name__.startswith("pack.")
    } == {
        f"pack.{remaining}.first-position",
        f"pack.{remaining}.viola-parts",
    }
    editable = (
        tmp_path / "editable"
        if selected == "editable"
        else plugins / "editable"
    )
    assert (editable / "draft.txt").read_text() == "Work in progress"


def test_plugins_dialog_lists_and_asks(
    tmp_path: Path,
    app: QApplication,
) -> None:
    """
    List installed plugins on the left and enable Uninstall only for a
    selection.

    Parameters
    ----------
    tmp_path : Path
        Isolated plugins folder.
    app : QApplication
        Shared Qt application.
    """
    del app
    plugins = tmp_path / "plugins"
    dialog = PluginsDialog(plugins)
    assert dialog.windowTitle() == "Plugins"
    assert (
        not dialog.empty.isHidden()
        and dialog.list.count() == 0
        and not dialog.uninstall_button.isEnabled()
    )
    install, uninstall = Mock(), Mock()
    dialog.install_requested.connect(install)
    dialog.uninstall_requested.connect(uninstall)
    dialog.uninstall_button.click()  # disabled, so nothing is asked
    uninstall.assert_not_called()
    install_pack(VIOLA_ZIP, folder=plugins)
    (plugins / "damaged.zip").write_bytes(b"not a zip")
    dialog.refresh()
    assert dialog.empty.isHidden() and dialog.list.count() == 2
    assert [dialog.list.item(row).text() for row in range(2)] == [
        "damaged",
        "Viola Instrument Pack",
    ]
    chosen = dialog.selected()
    assert chosen is not None and chosen.path.name == "damaged.zip"
    dialog.list.setCurrentRow(1)
    assert dialog.uninstall_button.isEnabled()
    dialog.refresh()  # the same plugin stays selected
    chosen = dialog.selected()
    assert chosen is not None and chosen.path.name == "viola.zip"
    dialog.install_button.click()
    install.assert_called_once_with()
    dialog.uninstall_button.click()
    assert uninstall.call_args.args[0].path == plugins / "viola.zip"
    dialog.list.setCurrentRow(-1)
    assert not dialog.uninstall_button.isEnabled()
    assert (
        dialog.install_button.text() == "Install plugin from file…"
        and dialog.uninstall_button.text() == "Uninstall plugin"
    )


def test_plugins_menu_item_runs_the_dialog(
    tmp_path: Path,
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Install, list, and uninstall a plugin through the one Plugins dialog
    that Tools opens.

    Parameters
    ----------
    tmp_path : Path
        Isolated Alto data directory.
    app : QApplication
        Shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Supply the user's selections, the trash, and relaunch.
    """
    del app
    plugins = tmp_path / "plugins"
    source = VIOLA_ZIP
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(
        main_window,
        "database_path",
        lambda: tmp_path / "alto.db",
    )
    window = main_window.MainWindow()
    restart, question = Mock(), Mock()
    buttons = main_window.QMessageBox.StandardButton
    question.side_effect = [
        buttons.No,
        buttons.Yes,
    ]  # keep running after installing, then confirm the uninstall
    monkeypatch.setattr(window, "restart_app", restart)
    monkeypatch.setattr(main_window.QMessageBox, "question", question)
    monkeypatch.setattr(
        main_window.QFileDialog,
        "getOpenFileName",
        Mock(return_value=(str(source), "")),
    )
    file = Mock()
    file.moveToTrash.side_effect = lambda: (plugins / "viola.zip").rename(
        tmp_path / "viola.zip",
    )
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(main_window, "QFile", Mock(return_value=file))
    seen: list[str] = []

    def run(dialog: PluginsDialog) -> int:
        """
        Press each button in turn instead of showing the dialog.

        Parameters
        ----------
        dialog : PluginsDialog
            The dialog the window built.

        Returns
        -------
        int
            The result code of a closed dialog.
        """
        assert dialog.parent() is window
        dialog.install_button.click()
        seen.append(dialog.list.item(0).text())
        dialog.uninstall_button.click()
        seen.append(str(dialog.list.count()))
        return 0

    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(PluginsDialog, "exec", run)
    tools = next(
        action
        for action in window.menu_button.menu().actions()
        if action.text() == "Tools"
    ).menu()
    assert isinstance(tools, QMenu)
    next(
        action for action in tools.actions() if action.text() == "Plugins…"
    ).trigger()
    assert seen == ["Viola Instrument Pack", "0"]
    restart.assert_called_once_with(quit_on_failure=True)
    assert (tmp_path / "viola.zip").exists() and not (
        plugins / "viola.zip"
    ).exists()


@pytest.fixture(autouse=True)
def isolated_packs() -> Iterator[None]:
    """
    Keep pack registrations local to each test.

    Yields
    ------
    None
        The test can install packs in the regular app registries.
    """
    exercises, instruments, recordings, lessons = (
        REGISTRY.copy(),
        INSTALLED.copy(),
        INSTRUMENT_BY_KEY.copy(),
        LESSONS.copy(),
    )
    terms = PLUGIN_TERMS.copy()
    yield
    REGISTRY[:] = exercises
    LESSONS[:] = lessons
    PLUGIN_TERMS.clear()
    PLUGIN_TERMS.update(terms)
    INSTALLED.clear()
    INSTALLED.update(instruments)
    INSTRUMENT_BY_KEY.clear()
    INSTRUMENT_BY_KEY.update(recordings)


def test_downloadable_viola_cards() -> None:
    """
    Keep the two ways to play G3 distinct across a database round trip.
    """
    exercise = read_pack(VIOLA)[0]()
    cards = list(exercise.daily_candidates(random.Random(1)))
    assert len({q.item_key() for q in cards}) == exercise.card_count() == 20
    gs = [q for q in cards if q.fingerboard and q.fingerboard.note == "G3"]
    assert len(gs) == 2
    assert {q.fingerboard.string for q in gs if q.fingerboard} == {0, 1}
    db = Database()
    learner = Learner(db, profile=db.add_profile("Violist"))
    for q in gs:
        learner.record(
            exercise,
            question=q,
            answer="G",
            correct=True,
            seconds=2.0,
            attempt_no=1,
        )
        item = db.get_item(
            learner.profile.id,
            exercise="pack.viola.first-position",
            item_key=q.item_key(),
        )
        assert (
            item is not None
            and Question.from_dict(json.loads(item.payload)) == q
        )


@needs_tutorial
def test_author_walkthrough(
    tmp_path: Path,
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Exercise the exact custom pack printed in the guide and render it
    for replay and export.

    Parameters
    ----------
    tmp_path : Path
        The author's pack folder.
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Observe the normal correct-answer playback.
    """
    del app
    folder = tmp_path / "my-strings"
    shutil.copytree(VIOLA.parent, folder)
    pack = folder / "pack.json"
    pack.write_text(TUTORIAL.read_text().split("```json\n")[1].split("```")[0])
    assert load_packs(tmp_path) == []
    exercise = REGISTRY[-1]()
    view = ExerciseView(exercise, rng=random.Random(1))
    q = view.question
    assert q is not None and q.answer == "E"
    assert (
        view.fingerboard.position == q.fingerboard
        and not view.fingerboard.isHidden()
    )
    assert "D4" in exercise.instructions()
    assert view.settings_panel.choice_buttons_row is not None
    view.settings_panel.next_question_mode = "Wait"
    played = []
    monkeypatch.setattr(
        view._answer_playback,
        "play",
        lambda notes, **kwargs: played.append((notes, kwargs["instrument"])),
    )
    view.submit("E", button=next(b for b in view.buttons if b.text() == "E"))
    assert played == [([[Note.parse("E4")]], "pack.my-strings.studio-viola")]
    view._light_answer_notes(0)
    assert view.fingerboard.sounding
    view._light_answer_notes(None)
    assert not view.fingerboard.sounding and not view.next_button.isHidden()
    preview = QuestionPreview(exercise.name, question=q)
    board = preview.findChild(FingerboardWidget)
    assert board is not None and board.position == q.fingerboard
    next(
        b for b in preview.findChildren(QPushButton) if b.text() == "Play"
    ).click()
    assert board.sounding
    board.show_position(None)
    assert not board.grab().isNull()
    picture = card_fields(q, folder=tmp_path, exercise=exercise)[1]
    assert "Marked fingerboard position" in picture and list(
        tmp_path.glob("*.png"),
    )


def test_packs_are_registered_atomically(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    A bad later exercise, a duplicate pack, and a JSON error leave valid
    packs available.

    Parameters
    ----------
    tmp_path : Path
        A plugins folder with valid and invalid neighbors.
    monkeypatch : pytest.MonkeyPatch
        Isolate registrations from the built-in exercises.
    """
    registry = REGISTRY.copy()
    monkeypatch.setattr("alto.exercises.base.REGISTRY", registry)
    monkeypatch.setattr("alto.exercises.packs.REGISTRY", registry)
    data = json.loads(VIOLA.read_text())
    broken = {
        **data,
        "exercises": [*data["exercises"], {"type": "unsupported"}],
    }
    for name, content in (
        ("a", broken),
        ("b", data),
        ("c", data),
        ("d", None),
    ):
        folder = tmp_path / name
        shutil.copytree(VIOLA.parent, folder)
        (folder / "pack.json").write_text(
            json.dumps(content) if content else "{",
        )
    (tmp_path / "empty").mkdir()
    assert load_packs(tmp_path / "absent") == []
    assert load_packs(tmp_path / "b" / "pack.json")
    problems = load_packs(tmp_path)
    assert [s.split("/")[0] for s in problems] == ["a", "c", "d"]
    assert [cls.__name__ for cls in registry[len(REGISTRY) :]] == [
        "pack.viola.first-position",
        "pack.viola.viola-parts",
    ]


@pytest.mark.parametrize(
    ("edits", "message"),
    [
        ({"instruments": []}, "at least one instrument"),
        ({"instruments": [None]}, "Each instrument must be an object"),
        ({"id": "bad id"}, "lowercase"),
        ({"name": "   "}, 'top-level "name"'),
        ({"name": False}, 'top-level "name"'),
        ({"format": True}, "format"),
        ({"exercises": []}, "at least one entry"),
    ],
)
def test_invalid_pack_fields(
    tmp_path: Path,
    edits: dict,
    message: str,
) -> None:
    """
    Report a correction for an unsupported field value.

    Parameters
    ----------
    tmp_path : Path
        Location of the invalid pack.
    edits : dict
        Changes to apply to a valid pack.
    message : str
        Expected part of the diagnostic.
    """
    shutil.copytree(VIOLA.parent, tmp_path, dirs_exist_ok=True)
    path = tmp_path / "pack.json"
    path.write_text(json.dumps(json.loads(VIOLA.read_text()) | edits))
    with pytest.raises(ValueError, match=re.escape(message)):
        read_pack(path)


@pytest.mark.parametrize(
    ("edits", "message"),
    [
        ({"id": "first-position"}, "Duplicate exercise id"),
        ({"title": ""}, "plain-text title"),
        ({"instrument": "unknown"}, "Unknown instrument"),
        ({"type": "image-choice"}, "questions list"),
        ({"type": "image-choice", "questions": [None]}, "must be an object"),
        ({"notes": {}}, "List the notes"),
        ({"notes": {"D5": ["D5"]}}, "from the tuning"),
        ({"notes": {"D4": ["C4"]}}, "one octave"),
        ({"notes": {"D4": ["F#4", "Gb4"]}}, "same position"),
    ],
)
def test_invalid_exercise_fields(
    tmp_path: Path,
    edits: dict,
    message: str,
) -> None:
    """
    Check corrections for the second exercise in a pack.

    Parameters
    ----------
    tmp_path : Path
        The pack's location.
    edits : dict
        Fields the author has changed.
    message : str
        Expected diagnostic.
    """
    pack = json.loads(VIOLA.read_text())
    pack["exercises"].append(pack["exercises"][0] | {"id": "second"} | edits)
    shutil.copytree(VIOLA.parent, tmp_path, dirs_exist_ok=True)
    path = tmp_path / "pack.json"
    path.write_text(json.dumps(pack))
    with pytest.raises(ValueError, match=message):
        read_pack(path)


def test_position_ruler_sits_beside_the_neck(
    tmp_path: Path,
    app: QApplication,
) -> None:
    """
    Mark the positions on a ruler above the fingerboard and leave the
    fingerboard itself free of guide lines.

    Parameters
    ----------
    tmp_path : Path
        Isolated plugins folder.
    app : QApplication
        Shared Qt application.
    """
    del app
    install_pack(VIOLA_ZIP, folder=tmp_path)
    load_packs(tmp_path)
    model = INSTALLED["pack.viola.bowed-viola"]
    assert [step for step, _ in model.positions] == [
        2,
        3,
        5,
        7,
        8,
        10,
        12,
    ]  # the pack puts 2nd and 5th a half step above 1st and 4th
    assert [name for _, name in model.positions] == [
        "1st",
        "2nd",
        "3rd",
        "4th",
        "5th",
        "6th",
        "7th",
    ]
    base, unit, spacing = ruler_base(model, step=5)  # the 3rd position's tick
    assert (
        base.y() < model.strings[-1].point(5)[1] - spacing and unit.y() < 0
    )  # clear of the neck, on the high-string side
    widget = FingerboardWidget()
    widget.resize(1000, 380)
    widget.show_position(
        FingerboardPosition(
            ("C3", "G3", "D4", "A4"),
            0,
            "E3",
            instrument="pack.viola.bowed-viola",
        ),
    )
    image = widget.grab().toImage()
    gap = min(
        dist(a.nut, b.nut) for a, b in zip(model.strings, model.strings[1:])
    )
    source = neck_view(model, gap=gap).intersected(QRectF(0, 0, *model.size))
    assert (
        source.right() < 0.8 * model.size[0] and source.left() > 0
    )  # the scroll and the body past the bridge are left out
    scale = min(998 / source.width(), 378 / source.height())
    left, top = (
        500 - source.center().x() * scale,
        190 - source.center().y() * scale,
    )

    def lightest(point: QPointF, *, reach: int) -> int:
        """
        Find the brightest pixel in a small box around an image point.

        Parameters
        ----------
        point : QPointF
            A location in image pixels.
        reach : int
            Pixels on screen to look in each direction. Keyword-only.

        Returns
        -------
        int
            The highest lightness found, from 0 to 255.
        """
        x, y = round(left + point.x() * scale), round(top + point.y() * scale)
        return max(
            image.pixelColor(x + dx, y + dy).lightness()
            for dx in range(-reach, reach + 1)
            for dy in range(-reach, reach + 1)
        )

    tick = base + unit * (spacing * 0.5)
    assert (
        min(
            image.pixelColor(
                round(left + tick.x() * scale) + dx,
                round(top + tick.y() * scale),
            ).lightness()
            for dx in (-1, 0, 1)
        )
        < 130
    )
    low, high = (
        model.strings[1].point(3),
        model.strings[2].point(3),
    )  # the old half-step line crossed the neck between strings
    assert (
        lightest(
            QPointF((low[0] + high[0]) / 2, (low[1] + high[1]) / 2),
            reach=1,
        )
        < 110
    )


@pytest.mark.parametrize("width,height", [(360, 210), (720, 270)])
def test_viola_playback_highlight(
    width: int,
    height: int,
    app: QApplication,
    tmp_path: Path,
) -> None:
    """
    Keep the green playback dot in the neck view and clear it when
    playback ends.

    Parameters
    ----------
    width, height : int
        Narrow or wide exercise pane size.
    app : QApplication
        Shared Qt application.
    tmp_path : Path
        Installed example ZIP.
    """
    del app
    shutil.copy(VIOLA_ZIP, tmp_path)
    assert not load_packs(tmp_path)
    exercise = next(
        cls()
        for cls in REGISTRY
        if cls.__name__ == "pack.viola.first-position"
    )
    widget = FingerboardWidget()
    widget.resize(width, height)
    widget.show_position(
        next(
            q.fingerboard
            for q in exercise.daily_candidates(random.Random(2))
            if q.fingerboard
            and q.fingerboard.string == 2
            and q.fingerboard.note == "E4"
        ),
    )
    idle = widget.grab().toImage()
    widget.set_sounding(True)
    sounding = widget.grab().toImage()
    assert sounding != idle
    assert widget.feedback_gap_ms() == 1000
    assert widget._movie.jumpToNextFrame()
    assert widget.grab().toImage() != sounding
    widget.set_sounding(False)
    assert widget.grab().toImage() == idle
    INSTALLED.clear()
    widget.show_position(widget.position)
    assert widget.grab().toImage() != idle


@pytest.mark.parametrize("mode", ["Immediately", "Wait", "After Animation"])
@pytest.mark.motion  # about the answer animation's timing in each answer mode
def test_animation_follows_answer_mode(
    tmp_path: Path,
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
) -> None:
    """
    Drive the installed animation through an actual correct answer and
    the muted playback clock.

    Parameters
    ----------
    tmp_path : Path
        Plugin installation directory.
    app : QApplication
        Shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Restore the app's mute setting after the test.
    mode : str
        Next Question preference.
    """
    del app
    install_pack(VIOLA_ZIP, folder=tmp_path)
    assert load_packs(tmp_path) == []
    exercise = next(
        cls()
        for cls in REGISTRY
        if cls.__name__ == "pack.viola.first-position"
    )
    monkeypatch.setattr(sounds, "enabled", False)
    view = ExerciseView(exercise, rng=random.Random(42))
    view.show()
    view.settings_panel.next_question_mode = mode
    board = view.fingerboard
    question = view.question
    assert question and not board.sounding
    view.submit(
        question.answer,
        button=next(b for b in view.buttons if b.text() == question.answer),
    )
    if mode == "Immediately":
        assert (
            not board.sounding
            and board._movie.state() == QMovie.MovieState.NotRunning
        )
    else:
        assert (
            board.sounding
            and board._movie.state() == QMovie.MovieState.Running
        )
        QTest.qWait(100)
        assert board._movie.currentFrameNumber() > 0
        assert view.question is question
    QTest.qWait(1250)
    assert (
        not board.sounding
        and board._movie.state() == QMovie.MovieState.NotRunning
    )
    assert (view.question is question) == (mode == "Wait")
    view.close()


def test_third_party_zip_owns_art_audio_and_exercises(
    tmp_path: Path,
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Load two independent instruments from a ZIP and use the second one's
    picture and sound.

    Parameters
    ----------
    tmp_path : Path
        An installation containing the ZIP alone.
    app : QApplication
        Shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Capture the instrument entering the shared audio sequencer.
    """
    del app
    data = json.loads(VIOLA.read_text())
    data["id"] = "test-studio"
    foreign = {
        "id": "two-string",
        "name": "Practice monochord pair",
        "image": "art/board.png",
        "strings": [
            {"open": "D3", "nut": [30, 20], "bridge": [270, 30]},
            {"open": "A3", "nut": [30, 45], "bridge": [270, 65]},
        ],
        "samples": {"D3": "media/string.wav"},
        "gain": 0.4,
    }
    data["instruments"].append(foreign)
    data["exercises"].append(
        {
            "id": "octave",
            "instrument": "two-string",
            "title": "String octave",
            "type": "fingerboard-notes",
            "notes": {"D3": ["D4"]},
        },
    )
    image = QImage(300, 90, QImage.Format.Format_RGB32)
    image.fill(0xFFBA157A)
    assert image.save(str(tmp_path / "custom.png"))
    with ZipFile(tmp_path / "studio.zip", "w") as archive:
        for path in VIOLA.parent.rglob("*"):
            if path.is_file() and path != VIOLA:
                archive.write(path, path.relative_to(VIOLA.parent))
        archive.write(tmp_path / "custom.png", "art/board.png")
        archive.write(VIOLA.parent / "sounds/D4.wav", "media/string.wav")
        archive.writestr("pack.json", json.dumps(data))
    assert load_packs(tmp_path) == []
    cls = REGISTRY[-1]
    exercise = cls()
    model = INSTALLED["pack.test-studio.two-string"]
    assert model.strings[0].point(12) == (150, 25)
    view = ExerciseView(exercise, rng=random.Random(3))
    assert view.fingerboard.model is model
    view.fingerboard.resize(300, 155)
    board = view.fingerboard.grab().toImage()
    assert any(
        board.pixelColor(x, y).name() == "#ba157a"
        for x in range(0, 300, 5)
        for y in range(0, 155, 5)
    )  # the pack's own art
    q = view.question
    assert (
        q is not None
        and Question.from_dict(json.loads(json.dumps(q.to_dict()))) == q
    )
    assert model.sound and model.sound.playback_volume() == 0.4
    player = Sounds()
    files = player.recordings(model.sound)
    (sample,) = files.values()
    assert sample.read_bytes() == (VIOLA.parent / "sounds/D4.wav").read_bytes()
    shifted = player._note_file(model.sound, midi=62)
    assert shifted.exists() and shifted != sample
    seen = Mock()
    monkeypatch.setattr(sounds, "_play_sequence", seen)
    old_instrument = sounds.instrument
    view.settings_panel.next_question_mode = "Wait"
    view.submit("D", button=next(b for b in view.buttons if b.text() == "D"))
    assert (
        seen.call_args.args == (model.key,)
        and sounds.instrument == old_instrument
    )


def test_parts_exercise_is_comprehensive(app: QApplication) -> None:
    """
    Cover the viola's parts from the scroll to the tailpiece, each with
    its answer among its choices and a visible marker.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    del app
    parts = next(
        cls for cls in read_pack(VIOLA) if cls.name == "Parts of the Viola"
    )
    answers = {card.answer for card in parts.cards}
    assert {
        "Scroll",
        "Pegbox",
        "Peg",
        "Nut",
        "Fingerboard",
        "C string",
        "G string",
        "D string",
        "A string",
        "Bridge",
        "F-hole",
        "Tailpiece",
        "Fine tuner",
        "Upper bout",
        "C-bout",
        "Lower bout",
        "Corner",
        "Purfling",
        "Top plate",
        "Neck",
        "Button",
        "Back plate",
        "Ribs",
    } <= answers
    assert {card.picture.view for card in parts.cards if card.picture} == {
        "",
        "back",
    }  # the front, and the rear photograph
    assert len(parts.cards) >= 20 and all(
        card.answer in card.choices and len(card.choices) == 4
        for card in parts.cards
    )
    for card in parts.cards:
        assert card.picture is not None
        if card.picture.focus:
            left, top, width, height = card.picture.focus
            assert (
                left <= card.picture.point[0] <= left + width
                and top <= card.picture.point[1] <= top + height
            )


def test_views_come_from_the_pack(tmp_path: Path, app: QApplication) -> None:
    """
    Show an instrument's extra picture when a question names its view,
    and keep the main picture otherwise.

    Parameters
    ----------
    tmp_path : Path
        An isolated plugins folder.
    app : QApplication
        Shared Qt application.
    """
    del app
    install_pack(VIOLA_ZIP, folder=tmp_path)
    assert load_packs(tmp_path) == []
    model = INSTALLED["pack.viola.bowed-viola"]
    front, back = model.picture(), model.picture("back")
    assert (
        front is not None
        and back is not None
        and front[0] != back[0]
        and model.picture("side") is None
    )
    widget = FingerboardWidget()
    widget.resize(720, 270)
    widget.show_position(
        PicturePosition(
            model.key,
            (1300.0, 400.0),
            "",
            56.0,
            (),
            True,
            "back",
        ),
    )
    behind = widget.grab().toImage()
    widget.show_position(PicturePosition(model.key, (1300.0, 400.0), "", 56.0))
    ahead = widget.grab().toImage()
    assert behind != ahead and widget._view == ""
    widget.show_position(
        PicturePosition(
            model.key,
            (1300.0, 400.0),
            "",
            56.0,
            (),
            True,
            "back",
        ),
    )
    assert widget._view == "back" and widget.grab().toImage() == behind


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"views": {"back": "images/nothing.webp"}}, "nothing.webp"),
        ({"views": {}}, "views"),
        ({"views": ["images/viola-back.webp"]}, "views"),
        ({"views": {"Back": "images/viola-back.webp"}}, "lowercase"),
        (
            {"views": {f"v{i}": "images/viola-back.webp" for i in range(5)}},
            "views",
        ),
        ({"views": {"back": "sounds/C3.wav"}}, "Use .png"),
    ],
)
def test_bad_views_are_refused(
    tmp_path: Path,
    change: dict,
    message: str,
) -> None:
    """
    Refuse an instrument whose extra pictures are missing, unreadable,
    or badly named.

    Parameters
    ----------
    tmp_path : Path
        An isolated copy of the example pack.
    change : dict
        Fields that replace the instrument's views.
    message : str
        Part of the expected diagnostic.
    """

    def damage(manifest: dict) -> None:
        """
        Replace the views.

        Parameters
        ----------
        manifest : dict
            The parsed manifest, changed in place.
        """
        manifest["instruments"][0].update(change)

    with pytest.raises(ValueError, match=message):
        read_pack(_edited_pack(tmp_path, edit=damage))


def _viola_notes() -> type[PackExercise]:
    """
    Read the example's note exercise, with its options at their
    defaults.

    Returns
    -------
    type
        The exercise class, whose options are reset before it is
        returned.
    """
    cls = next(
        c for c in read_pack(VIOLA) if c.__name__.endswith("first-position")
    )
    settings.pack_exercises.pop(cls.__name__, None)
    REGISTRY.append(
        cls,
    )  # the fixture that isolates packs restores the registry afterward
    return cls


def test_settings_change_the_cards() -> None:
    """
    Ask the sharps, the octave, and only the chosen range, as the
    learner switches each on.
    """
    cls = _viola_notes()
    exercise = cls()
    assert (
        set(cls.controls) == {"sound", "range", "accidentals", "octave"}
        and cls.range_clef == "alto"
    )
    plain = exercise.active_cards()
    assert plain == cls.cards and len(plain) == 20 and plain[0].octaves is None
    options = cls.options()
    options.accidentals = True
    sharps = exercise.active_cards()
    assert (
        len(sharps) == 32
        and sharps[0].grid is not None
        and len(sharps[0].choices) == 21
    )
    black = next(card for card in sharps if card.answer == "C♯")
    assert black.accept == ("D♭",)
    options.require_octave = True
    with_octave = exercise.active_cards()
    card = next(card for card in with_octave if card.answer == "C♯3")
    assert (
        card.accept == ("D♭3",)
        and card.octaves == ["3", "4", "5"]
        and card.check("C♯3")
        and card.check("D♭3")
        and not card.check("C♯4")
    )
    options.ranges["alto"] = (cls.span[0], cls.span[0] + 3)  # C3 to F3
    narrow = exercise.active_cards()
    assert {Note.parse(c.fingerboard.note).diatonic for c in narrow} <= set(
        range(cls.span[0], cls.span[0] + 4),
    )
    assert exercise.card_count() == len(narrow) and 0 < len(narrow) < len(
        with_octave,
    )
    assert exercise.make_question(random.Random(1)).fingerboard in {
        c.fingerboard for c in narrow
    }
    settings.pack_exercises.pop(cls.__name__)


def test_settings_signature_keeps_history_for_the_defaults() -> None:
    """
    Leave the catalog signature alone until the learner changes an
    option that changes the questions.
    """
    cls = _viola_notes()
    exercise = cls()
    assert exercise.practice_signature() == cls.catalog_signature
    cls.options().sound = "piano"
    assert exercise.practice_signature() == cls.catalog_signature
    cls.options().accidentals = True
    assert exercise.practice_signature() != cls.catalog_signature
    settings.pack_exercises.pop(cls.__name__)


def test_sound_setting_chooses_the_instrument() -> None:
    """
    Play the pack's sound by default and the instrument the learner
    chooses once they choose one.
    """
    cls = _viola_notes()
    exercise = cls()
    assert (
        exercise.sound_instrument("pack.viola.bowed-viola")
        == "pack.viola.bowed-viola"
    )
    cls.options().sound = "piano"
    assert exercise.sound_instrument("pack.viola.bowed-viola") == "piano"
    cls.options().sound = "not-installed"
    assert (
        exercise.sound_instrument("pack.viola.bowed-viola")
        == "pack.viola.bowed-viola"
    )
    plain = next(
        c for c in read_pack(VIOLA) if c.__name__.endswith("viola-parts")
    )()
    assert (
        plain.sound_instrument("pack.viola.bowed-viola")
        == "pack.viola.bowed-viola"
    )
    settings.pack_exercises.pop(cls.__name__)


def test_settings_panel_edits_and_saves(app: QApplication) -> None:
    """
    Show the declared controls, apply each edit to the exercise, and
    restore the choices at the next start.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    del app
    cls = _viola_notes()
    panel = settings_panel_for(cls())
    assert (
        isinstance(panel, PackSettingsPanel)
        and panel.range_row.isVisible() is not None
    )
    assert panel.sound_row and panel.accidentals_row and panel.octave_row
    assert (
        panel.sound_row.value.text() == "Bowed viola"
        and not panel.accidentals_row.isOn()
    )
    changes = []
    panel.changed.connect(lambda: changes.append(1))
    panel._sound_chosen("piano")
    panel.accidentals_row.click()
    panel.octave_row.click()
    options = cls.options()
    assert (options.sound, options.accidentals, options.require_octave) == (
        "piano",
        True,
        True,
    ) and len(changes) == 3
    assert panel.sound_row.value.text() == "Piano"
    panel._build_range_rows()
    editor = panel.range_editors["alto"]
    assert editor.limits == cls.span
    editor.low_up.click()
    assert (
        options.range_for("alto")[0] == cls.span[0] + 1 and len(changes) == 4
    )
    options.accidentals = options.require_octave = False
    options.sound = None
    save_pack_options(
        cls.__name__,
        # only the range was edited since the others were written at
        # their
        # change
    )
    settings.pack_exercises.pop(cls.__name__)
    load_pack_options()
    again = cls.options()
    assert again.range_for("alto") == (cls.span[0] + 1, cls.span[1])
    panel._reset_ranges()
    assert options.range_for("alto") == cls.span
    settings.pack_exercises.pop(cls.__name__)
    store = settings.pack_exercises  # nothing else keeps state between tests
    assert cls.__name__ not in store


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ({}, "settings"),
        ([], "settings"),
        ({"volume": True}, "settings"),
        ({"sound": ""}, "sound"),
        ({"sound": "<b>Viola</b>"}, "sound"),
        ({"range": "wide"}, "range"),
        ({"accidentals": False}, "accidentals"),
        ({"octave": "yes"}, "octave"),
    ],
)
def test_bad_settings_are_refused(
    tmp_path: Path,
    value: object,
    message: str,
) -> None:
    """
    Refuse an exercise whose declared settings are unknown or malformed.

    Parameters
    ----------
    tmp_path : Path
        An isolated copy of the example pack.
    value : object
        The replacement ``settings`` entry.
    message : str
        Part of the expected diagnostic.
    """

    def damage(manifest: dict) -> None:
        """
        Replace the settings.

        Parameters
        ----------
        manifest : dict
            The parsed manifest, changed in place.
        """
        manifest["exercises"][0]["settings"] = value

    with pytest.raises(ValueError, match=message):
        read_pack(_edited_pack(tmp_path, edit=damage))


def test_settings_belong_to_note_exercises(tmp_path: Path) -> None:
    """
    Refuse settings on a picture exercise, which has fixed questions.

    Parameters
    ----------
    tmp_path : Path
        An isolated copy of the example pack.
    """

    def damage(manifest: dict) -> None:
        """
        Give the parts exercise a setting.

        Parameters
        ----------
        manifest : dict
            The parsed manifest, changed in place.
        """
        manifest["exercises"][1]["settings"] = {"octave": True}

    with pytest.raises(ValueError, match="fingerboard-notes"):
        read_pack(_edited_pack(tmp_path, edit=damage))


def test_marker_size_and_focus_survive_storage() -> None:
    """
    Keep a picture question's size and region through storage, and keep
    the old key for questions that use neither.
    """
    plain = Question(
        "Which?",
        choices=["A", "B"],
        answer="A",
        picture=PicturePosition("pack.x.y", (10.0, 20.0)),
    )
    sized = replace(
        plain,
        picture=PicturePosition(
            "pack.x.y",
            (10.0, 20.0),
            "",
            18.0,
            (0.0, 0.0, 100.0, 80.0),
            True,
            "back",
        ),
    )
    assert Question.from_dict(json.loads(json.dumps(sized.to_dict()))) == sized
    assert Question.from_dict(json.loads(json.dumps(plain.to_dict()))) == plain
    assert plain.item_key() != sized.item_key()
    legacy = plain.to_dict()
    for name in ("size", "focus", "marker", "view"):
        del legacy["picture"][name]  # what an earlier version stored
    assert (
        Question.from_dict(legacy) == plain
        and Question.from_dict(legacy).item_key() == plain.item_key()
    )


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"image": "../viola.webp"}, "inside the pack"),
        ({"image": "images/missing.png"}, "Missing file"),
        ({"samples": {"D4": "sounds/missing.wav"}}, "Missing file"),
        ({"strings": [{"open": "A4"}, {}]}, "image pixels"),
        ({"gain": -1}, "gain"),
        ({"correct_answer_animation": "animation.gif"}, "object"),
        (
            {"correct_answer_animation": {"file": "images/missing.gif"}},
            "Missing file",
        ),
        (
            {"correct_answer_animation": {"file": "../overlay.gif"}},
            "inside the pack",
        ),
        (
            {"correct_answer_animation": {"file": "images/viola-front.webp"}},
            ".gif",
        ),
        ({"correct_answer_animation": {"anchor": "unknown"}}, "anchor"),
        ({"samples": []}, "Map each recorded pitch"),
        (
            {"samples": {"F#4": "sounds/A4.wav", "Gb4": "sounds/A4.wav"}},
            "Duplicate recorded pitch",
        ),
        ({"id": "bowed-viola"}, "Duplicate instrument"),
        ({"name": ""}, "instrument name"),
        ({"image": None}, "relative file path"),
        ({"image": "notes.txt"}, "Use .png"),
        ({"strings": [None]}, "at least two strings"),
        ({"strings": [None, None]}, "Each string needs"),
        (
            {"strings": [{"open": "D4", "nut": [2, 1], "bridge": [2, 1]}, {}]},
            "different points",
        ),
        (
            {
                "strings": [
                    {"open": n, "nut": [2, 1], "bridge": [6, 1]}
                    for n in ("D4", "A4")
                ],
            },
            "own nut and bridge",
        ),
        (
            {
                "strings": [
                    {"open": n, "nut": [2, 1], "bridge": [6, 1]}
                    for n in ("D4", "D4")
                ],
            },
            "distinct strings",
        ),
    ],
)
def test_invalid_media_skips_entire_pack(
    tmp_path: Path,
    change: dict,
    message: str,
) -> None:
    """
    Check that an invalid second instrument registers neither the first
    instrument nor its exercise.

    Parameters
    ----------
    tmp_path : Path
        The installation folder.
    change : dict
        Invalid changes to the second instrument.
    message : str
        Expected diagnostic.
    """
    folder = tmp_path / "test"
    shutil.copytree(VIOLA.parent, folder)
    data = json.loads(VIOLA.read_text())
    data["instruments"].append(
        data["instruments"][0] | {"id": "other"} | change,
    )
    (folder / "pack.json").write_text(json.dumps(data))
    before = REGISTRY.copy()
    problems = load_packs(tmp_path)
    assert len(problems) == 1 and message in problems[0]
    assert REGISTRY == before and "pack.viola.bowed-viola" not in INSTALLED


@needs_tutorial
def test_picture_questions_without_strings(
    tmp_path: Path,
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Use a pack-owned image and optional pitched sample without any
    string geometry.

    Parameters
    ----------
    tmp_path : Path
        The installed authoring folder and exported pictures.
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Observe the selected playback instrument.
    """
    del app
    folder = tmp_path / "studio"
    shutil.copytree(VIOLA.parent, folder)
    pack = json.loads(VIOLA.read_text())
    del pack["instruments"][0]["strings"]
    pack["instruments"][0]["correct_answer_animation"]["anchor"] = "image"
    exercise_entry = json.loads(
        TUTORIAL.read_text().split("```json\n")[2].split("```")[0],
    )
    exercise_entry["instrument"] = pack["instruments"][0]["id"]
    question = exercise_entry["questions"][0]
    exercise_entry["questions"].append(
        question
        | {"note": "C3", "prompt": "Which part supports the strings?"},
    )
    pack["exercises"] = [exercise_entry]
    del (
        pack["lessons"],
        pack["glossary"],
    )  # they link to exercises that this pack no longer has
    (folder / "pack.json").write_text(json.dumps(pack))
    assert load_packs(tmp_path) == []
    exercise = REGISTRY[-1]()
    assert exercise.card_count() == 2
    for card in exercise.daily_candidates(random.Random(1)):
        assert card.picture and card.picture.point == (1500, 400)
        assert (
            Question.from_dict(json.loads(json.dumps(card.to_dict()))) == card
        )
        preview = QuestionPreview(exercise.name, question=card)
        board = preview.findChild(FingerboardWidget)
        assert board and board.model and not board.model.strings
        idle = board.grab().toImage()
        board.set_sounding(True)
        assert board.grab().toImage() != idle
        assert (
            "Marked instrument picture"
            in card_fields(card, folder=tmp_path, exercise=exercise)[1]
        )
        buttons = [
            b for b in preview.findChildren(QPushButton) if b.text() == "Play"
        ]
        if card.picture.note:
            seen = Mock()
            monkeypatch.setattr(sounds, "_play_sequence", seen)
            buttons[0].click()
            assert seen.call_args.args == (card.picture.instrument,)
        else:
            assert not buttons
            view = ExerciseView(exercise, rng=random.Random(1))
            view.question = card
            view.fingerboard.show_position(card.picture)
            view.settings_panel.next_question_mode = "Wait"
            view.submit(
                card.answer,
                button=next(
                    b for b in view.buttons if b.text() == card.answer
                ),
            )
            assert view.fingerboard._movie.state() == QMovie.MovieState.Running
            QTest.qWait(700)
            assert not view.fingerboard.sounding and view.question is card


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"point": [-1, 0]}, "outside"),
        ({"prompt": None}, "plain text"),
        ({"choices": []}, "at least two"),
        (
            {
                "point": [250, 392],
                "choices": ["Scroll", "Peg", "Pegbox", "Nut"],
                "answer": "Pegbox",
            },
            "Duplicate image-choice",
        ),
        ({"answer": "Bridge"}, "exactly matches"),
        ({"view": "side"}, "views"),
        ({"view": "back", "point": [2100, 10]}, "outside"),
        ({"marker_size": 3}, "marker_size"),
        ({"marker_size": 500}, "marker_size"),
        ({"marker_size": "large"}, "marker_size"),
        ({"focus": [0, 220, 480]}, "four numbers"),
        ({"focus": [0, 220, 480, "tall"]}, "four numbers"),
        ({"focus": [0, 220, 10, 10]}, "at least 40"),
        ({"focus": [0, 220, 5000, 330]}, "inside the picture"),
        ({"focus": [1000, 220, 400, 300]}, "inside its focus region"),
        ({"choices": ["Bridge", "Bridge"]}, "distinct choices"),
        ({"note": "D"}, "Expected a note"),
    ],
)
def test_invalid_picture_question(
    tmp_path: Path,
    change: dict,
    message: str,
) -> None:
    """
    Reject an invalid picture question before registering any exercise
    in the same pack.

    Parameters
    ----------
    tmp_path : Path
        Location of the edited pack.
    change : dict
        Invalid question fields.
    message : str
        Part of the expected diagnostic.
    """
    folder = tmp_path / "viola"
    shutil.copytree(VIOLA.parent, folder)
    pack = json.loads(VIOLA.read_text())
    pack["exercises"][1]["questions"][0].update(change)
    (folder / "pack.json").write_text(json.dumps(pack))
    problems = load_packs(tmp_path)
    assert len(problems) == 1 and message in problems[0]
    assert "pack.viola.bowed-viola" not in INSTALLED


def test_legacy_fingerboard_review(
    tmp_path: Path,
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Resolve an old saved card against its installed exercise for
    practice and database previews.

    Parameters
    ----------
    tmp_path : Path
        Installation containing the example ZIP.
    app : QApplication
        Shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Read the preview without opening a modal dialog.
    """
    del app
    shutil.copy(VIOLA_ZIP, tmp_path)
    assert load_packs(tmp_path) == []
    key = "pack.viola.first-position"
    exercise = next(cls() for cls in REGISTRY if cls.__name__ == key)
    question = exercise.generate(random.Random(1))
    assert question.fingerboard
    old = replace(
        question,
        fingerboard=replace(question.fingerboard, instrument=""),
    )
    assert old.item_key() == question.item_key()
    assert exercise.refresh(old) == exercise.refresh(question) == question
    payload = old.to_dict()
    del payload["fingerboard"]["instrument"]
    model = database_page.RowsModel(
        ["Answer"],
        rows=[[("E", "E")]],
        extras=[{"exercise": key, "payload": json.dumps(payload)}],
    )
    preview = Mock()
    monkeypatch.setattr(database_page, "QuestionPreview", preview)
    database_page.open_preview(
        model.index(0, 0),
        names={},
        parent=FingerboardWidget(),
    )
    assert preview.call_args.kwargs["question"] == question


@pytest.mark.parametrize(
    ("asset", "contents", "message"),
    [
        ("images/viola-front.webp", b"broken", "Cannot read"),
        ("sounds/C3.wav", b"broken", "Invalid WAV"),
        ("sounds/C3.wav", None, "Incomplete WAV"),
    ],
)
def test_unreadable_pack_media(
    tmp_path: Path,
    asset: str,
    contents: bytes | None,
    message: str,
) -> None:
    """
    Diagnose unreadable artwork and damaged recordings by filename at
    installation.

    Parameters
    ----------
    tmp_path : Path
        Installation containing the edited pack.
    asset : str
        The pack-relative asset to damage.
    contents : bytes or None
        Replacement bytes, or None to truncate the existing file.
    message : str
        Expected reason for skipping the pack.
    """
    folder = tmp_path / "viola"
    shutil.copytree(VIOLA.parent, folder)
    path = folder / asset
    path.write_bytes(
        contents if contents is not None else path.read_bytes()[:50],
    )
    (problem,) = load_packs(tmp_path)
    assert message in problem and asset in problem


@pytest.mark.parametrize(
    ("member", "message"),
    [
        ("viola/pack.json", "root of the ZIP"),
        ("pack.json", "Missing file in ZIP"),
    ],
)
def test_incomplete_distribution(
    tmp_path: Path,
    member: str,
    message: str,
) -> None:
    """
    Give beginners a diagnostic for zipping the parent folder or
    omitting the art.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder.
    member : str
        The path where the author put the manifest.
    message : str
        Expected part of the startup message.
    """
    with ZipFile(tmp_path / "viola.zip", "w") as archive:
        archive.write(VIOLA, member)
    (problem,) = load_packs(tmp_path)
    assert problem.startswith("viola.zip") and message in problem


def test_asset_size_and_format_errors(tmp_path: Path) -> None:
    """
    Check author diagnostics for an oversized image, a stereo sample,
    and missing string definitions.

    Parameters
    ----------
    tmp_path : Path
        The edited working folder.
    """
    folder = tmp_path / "viola"
    shutil.copytree(VIOLA.parent, folder)
    sample = folder / "sounds/C3.wav"
    with wave.open(str(sample), "wb") as output:
        output.setparams((2, 2, 44100, 0, "NONE", "not compressed"))
        output.writeframes(bytes(4))
    (problem,) = load_packs(tmp_path)
    assert "mono 16-bit PCM" in problem
    data = json.loads(VIOLA.read_text())
    del data["instruments"][0]["strings"]
    del data["instruments"][0]["samples"]
    (folder / "pack.json").write_text(json.dumps(data))
    (problem,) = load_packs(tmp_path)
    assert "Declare strings" in problem
    with (folder / data["instruments"][0]["image"]).open("rb+") as image:
        image.truncate(64 * 1024**2 + 1)
    (problem,) = load_packs(tmp_path)
    assert "64 MiB" in problem
