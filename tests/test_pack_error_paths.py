"""
Tests for the ways a plugin can be wrong, or an install can fail, that
the other plugin tests do not reach.

Each case damages the manifest of an example pack, or an installation,
in one way and checks that Alto says why.
"""

from __future__ import annotations

import json
import os
import shutil
from collections.abc import Callable
from pathlib import Path

import pytest
from PySide6.QtCore import QLockFile

from alto.audio import DEFAULT_NOTE_GAP_MS, Sounds, sounds
from alto.exercises import packs
from alto.exercises.base import PicturePosition, Question
from alto.exercises.packs import (
    InstalledPlugin,
    _keyboard_subset,
    install_pack,
    installed_plugins,
    pack_manifests,
    read_pack,
)
from alto.lessons.packs import read_lessons
from alto.theory.pitch import Note
from test_harpsichord_pack import PACK as HARPSICHORD
from test_instrument_packs import isolated_packs  # noqa: F401  # the autouse fixture that keeps registrations local
from viola_pack import MANIFEST as VIOLA
from viola_pack import ZIP as VIOLA_ZIP


def edited(
    tmp_path: Path,
    *,
    source: Path,
    edit: Callable[[dict], None],
) -> Path:
    """
    Copy an example pack with its manifest changed by ``edit``.

    Parameters
    ----------
    tmp_path : Path
        Where the copy goes.
    source : Path
        The pack's `pack.json`. Keyword-only.
    edit : Callable[[dict], None]
        Changes the parsed manifest in place. Keyword-only.

    Returns
    -------
    Path
        The copy's `pack.json`.
    """
    folder = tmp_path / "edited"
    shutil.copytree(source.parent, folder)
    manifest = json.loads((folder / "pack.json").read_text())
    edit(manifest)
    (folder / "pack.json").write_text(json.dumps(manifest))
    return folder / "pack.json"


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        (lambda m: m.update(lessons=[]), "between 1 and"),
        (
            lambda m: m["lessons"][0]["steps"][0].update(hear=[[]]),
            "one to four note names",
        ),
        (
            lambda m: m["lessons"][0]["steps"][0].update(picture="the front"),
            "as an object",
        ),
        (
            lambda m: m["lessons"][0]["steps"][0]["picture"].update(
                marker="yes",
            ),
            "true or false",
        ),
        (
            lambda m: m["lessons"][0]["steps"][2]["picture"].pop("point"),
            "a point, or set marker",
        ),
        (
            lambda m: m["lessons"][1]["steps"][0]["task"].pop("choices"),
            "choices with an answer",
        ),
    ],
)
def test_bad_lessons_say_why(
    tmp_path: Path,
    edit: Callable[[dict], None],
    message: str,
) -> None:
    """
    Refuse a lesson with a missing icon, a malformed chord, picture or
    task, and name the fault.

    Parameters
    ----------
    tmp_path : Path
        Isolated copy of the example pack.
    edit : Callable[[dict], None]
        Damages the parsed manifest in place.
    message : str
        Part of the expected diagnostic.
    """
    with pytest.raises(ValueError, match=message):
        read_pack(edited(tmp_path, source=VIOLA, edit=edit))


def test_a_lesson_key_must_be_a_keyboard_and_a_pitch(tmp_path: Path) -> None:
    """
    Refuse a highlighted key that is not written as a keyboard name and
    a pitch.

    Parameters
    ----------
    tmp_path : Path
        Isolated copy of the example pack.
    """
    picture = lambda m: m["lessons"][1]["steps"][1]["picture"]  # noqa: E731
    path = edited(
        tmp_path,
        source=HARPSICHORD,
        edit=lambda m: picture(m).update(keys=[["Lower manual"]]),
    )
    with pytest.raises(ValueError, match="Write each key"):
        read_pack(path)


def test_an_exercise_can_name_other_exercises_as_related(
    tmp_path: Path,
) -> None:
    """
    Accept a lesson that lists another exercise of the plugin as
    related.

    Parameters
    ----------
    tmp_path : Path
        Isolated copy of the example pack.
    """
    path = edited(
        tmp_path,
        source=VIOLA,
        edit=lambda m: m["lessons"][0].update(
            related_exercises=["first-position"],
        ),
    )
    assert read_pack(path)


def test_a_lesson_icon_must_be_one_the_plugin_supplies() -> None:
    """
    Refuse a lesson whose icon is not among the icons the pack loaded.
    """
    row = {
        "id": "a",
        "title": "A",
        "about": "About A.",
        "summary": "Summary of A.",
        "exercise": "first",
        "icon": "icons/a.svg",
        "steps": [{"title": "One", "text": ["First."]}],
    }
    with pytest.raises(ValueError, match="icon of"):
        read_lessons(
            [row],
            pack_id="demo",
            pack_name="Demo",
            instruments={},
            exercises={"first": "pack.demo.first"},
            icons={},
        )


def _plain_instrument(manifest: dict) -> None:
    """
    Add a second instrument with the harpsichord's picture and nothing
    else, and an exercise of each type that needs more.

    Parameters
    ----------
    manifest : dict
        The parsed harpsichord manifest, changed in place.
    """
    picture = manifest["instruments"][0]["image"]
    manifest["instruments"].append(
        {"id": "plain", "name": "Plain", "image": picture},
    )
    manifest["exercises"].append(
        {
            "id": "no-strings",
            "title": "No Strings",
            "type": "fingerboard-notes",
            "instrument": "plain",
            "notes": {},
        },
    )


def _short_upper_manual(manifest: dict) -> None:
    """
    Let the upper manual end an octave and a half below where the
    exercise's range ends.

    Parameters
    ----------
    manifest : dict
        The parsed harpsichord manifest, changed in place.
    """
    manifest["instruments"][0]["keyboards"][0]["highest"] = "C5"


def _one_octave_range(manifest: dict) -> None:
    """
    Ask only octaves in a range that is narrower than an octave.

    Parameters
    ----------
    manifest : dict
        The parsed harpsichord manifest, changed in place.
    """
    exercise = manifest["exercises"][0]
    exercise.pop("default_range")
    exercise.update(intervals=["P8"], lowest="E1", highest="F1")


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        (
            lambda m: m["exercises"][0]["settings"].update(range="alto"),
            "Set range in the settings",
        ),
        (_plain_instrument, "Declare strings"),
        (
            lambda m: m["exercises"][0].update(default_range="C3"),
            "default_range of",
        ),
        (
            lambda m: m["exercises"][0].update(default_range=["D1", "C3"]),
            "Keep the default_range",
        ),
        (_one_octave_range, "no pair of keys"),
    ],
)
def test_bad_keyboard_exercises_say_why(
    tmp_path: Path,
    edit: Callable[[dict], None],
    message: str,
) -> None:
    """
    Refuse a keyboard exercise with a malformed setting or range, or one
    that asks nothing, and name the fault.

    Parameters
    ----------
    tmp_path : Path
        Isolated copy of the example pack.
    edit : Callable[[dict], None]
        Damages the parsed manifest in place.
    message : str
        Part of the expected diagnostic.
    """
    with pytest.raises(ValueError, match=message):
        read_pack(edited(tmp_path, source=HARPSICHORD, edit=edit))


def test_a_keyboard_exercise_needs_keyboards(tmp_path: Path) -> None:
    """
    Refuse a keyboard interval exercise on an instrument that declares
    no keyboards.

    Parameters
    ----------
    tmp_path : Path
        Isolated copy of the example pack.
    """

    def edit(manifest: dict) -> None:
        """
        Point the interval exercise at an instrument without keyboards.

        Parameters
        ----------
        manifest : dict
            The parsed harpsichord manifest, changed in place.
        """
        _plain_instrument(manifest)
        manifest["exercises"].pop()
        manifest["exercises"][0].update(
            instrument="plain",
            keyboards=["Lower manual"],
        )

    with pytest.raises(ValueError, match="Declare keyboards"):
        read_pack(edited(tmp_path, source=HARPSICHORD, edit=edit))


def test_keys_a_manual_lacks_are_not_asked(tmp_path: Path) -> None:
    """
    Skip the pairs of keys that one of the manuals does not have.

    Parameters
    ----------
    tmp_path : Path
        Isolated copy of the example pack.
    """
    exercise = read_pack(
        edited(tmp_path, source=HARPSICHORD, edit=_short_upper_manual),
    )[0]
    assert exercise.cards
    for card in exercise.cards:
        assert card.picture is not None
        for (board, _), name in zip(
            card.picture.keys,
            card.picture.notes,
            strict=True,
        ):
            assert (
                board != "Upper manual"
                or Note.parse(name).midi <= Note.parse("C5").midi
            )


def test_the_choice_cache_does_not_grow_without_end() -> None:
    """
    Forget the cards chosen for earlier ranges once many ranges have
    been tried.
    """
    card = Question(
        "?",
        choices=["M3"],
        answer="M3",
        picture=PicturePosition("a", (0, 0), notes=("C4", "E4")),
    )
    cache: dict = {}
    for top in range(64, 100):
        _keyboard_subset((card,), keys=(48, top), names=("M3",), cache=cache)
    assert len(cache) <= 26


ONE_FRAME = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,"
    b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


def test_an_instrument_kind_must_be_plain_text(tmp_path: Path) -> None:
    """
    Refuse an instrument kind that is not text.

    Parameters
    ----------
    tmp_path : Path
        Isolated copy of the example pack.
    """
    with pytest.raises(ValueError, match="kind of"):
        read_pack(
            edited(
                tmp_path,
                source=VIOLA,
                edit=lambda m: m["instruments"][0].update(kind=5),
            ),
        )


def test_an_animation_needs_more_than_one_frame(tmp_path: Path) -> None:
    """
    Refuse a correct-answer animation that is a single picture.

    Parameters
    ----------
    tmp_path : Path
        Isolated copy of the example pack.
    """
    path = edited(tmp_path, source=VIOLA, edit=lambda m: None)
    (path.parent / "animations/string.gif").write_bytes(ONE_FRAME)
    with pytest.raises(ValueError, match="animated GIF"):
        read_pack(path)


def test_an_icon_is_drawn_in_the_theme_s_ink_and_kept_small(
    tmp_path: Path,
) -> None:
    """
    Redraw an icon's fills and strokes in the theme's ink, and refuse
    one over the size limit.

    Parameters
    ----------
    tmp_path : Path
        Isolated copy of the example pack.
    """
    path = edited(tmp_path, source=VIOLA, edit=lambda m: None)
    icon = path.parent / "icons/viola.svg"
    box = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">{}</svg>'
    )
    icon.write_text(
        box.format('<path d="M1 1h4v4z" fill="#f00" stroke="#00f"/>'),
    )
    assert (
        'fill="COLOR"' in read_pack(path)[0].icon
        and 'stroke="COLOR"' in read_pack(path)[0].icon
    )
    icon.write_text(box.format("<!-- " + "x" * 120_000 + " -->"))
    with pytest.raises(ValueError, match="under 100 KB"):
        read_pack(path)


def test_an_exercise_without_settings_keeps_its_history_signature() -> None:
    """
    Keep the practice signature of an exercise that offers no settings
    the same as its catalog's.
    """
    parts = next(
        cls for cls in read_pack(VIOLA) if cls.__name__.endswith("viola-parts")
    )
    assert parts().practice_signature() == parts.catalog_signature


def test_a_missing_recording_gives_the_usual_feedback_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Use the usual interval between notes when a note's recording cannot
    be read.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Point the note at a file that is not there.
    """
    monkeypatch.setattr(
        Sounds,
        "_note_file",
        lambda self, instrument, *, midi: Path("/no/such/recording.wav"),
    )
    assert sounds.note_duration_ms(60) == DEFAULT_NOTE_GAP_MS


def test_an_entry_that_cannot_be_read_is_reported(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Report a plugins-folder entry that raises while it is checked, and
    keep listing the others.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder.
    monkeypatch : pytest.MonkeyPatch
        Make one entry fail.
    """
    shutil.copyfile(VIOLA_ZIP, tmp_path / "viola.zip")
    (tmp_path / "broken.zip").write_bytes(b"")
    real = Path.is_file

    def is_file(self: Path) -> bool:
        """
        Fail for the broken entry only.

        Parameters
        ----------
        self : Path
            The entry being checked.

        Returns
        -------
        bool
            What the real check says.

        Raises
        ------
        OSError
            For the broken entry.
        """
        if self.name == "broken.zip":
            raise OSError("Input/output error")
        return real(self)

    monkeypatch.setattr(Path, "is_file", is_file)
    manifests, problems = pack_manifests(tmp_path)
    assert [path.name for path in manifests] == ["viola.zip"]
    assert problems == ["broken.zip — Input/output error"]


def test_plugin_whose_manifest_or_state_cannot_be_read_still(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    List a plugin by its file name when its manifest cannot be opened,
    and report one that cannot be inspected at all.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder.
    monkeypatch : pytest.MonkeyPatch
        Make the manifest unreadable, then a file unreachable.
    """
    shutil.copyfile(VIOLA_ZIP, tmp_path / "viola.zip")
    shutil.copyfile(VIOLA_ZIP, tmp_path / "other.zip")

    def unreadable(path: Path) -> None:
        """
        Fail as a disk error would.

        Parameters
        ----------
        path : Path
            The plugin being read.

        Raises
        ------
        OSError
            Always.
        """
        raise OSError("unreadable")

    monkeypatch.setattr(packs, "installed_pack_info", unreadable)
    plugins, problems = installed_plugins(tmp_path)
    assert problems == [] and sorted(plugin.title for plugin in plugins) == [
        "other",
        "viola",
    ]
    real = Path.lstat

    def lstat(self: Path, **kwargs: bool) -> os.stat_result:
        """
        Fail for one file.

        Parameters
        ----------
        self : Path
            The file being inspected.
        **kwargs : bool
            What the real call takes.

        Returns
        -------
        os.stat_result
            What the real call says.

        Raises
        ------
        OSError
            For the file named other.zip.
        """
        if self.name == "other.zip":
            raise OSError("gone")
        return real(self, **kwargs)

    monkeypatch.setattr(Path, "lstat", lstat)
    plugins, problems = installed_plugins(tmp_path)
    assert [plugin.title for plugin in plugins] == ["viola"] and problems == [
        "other.zip — gone",
    ]


def test_installing_refuses_what_is_not_a_zip(tmp_path: Path) -> None:
    """
    Refuse a source that is not a ZIP file.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder's parent.
    """
    (tmp_path / "pack.txt").write_text("not a pack")
    with pytest.raises(ValueError, match="ZIP file"):
        install_pack(tmp_path / "pack.txt", folder=tmp_path / "plugins")


def test_installing_waits_for_nobody_else_installing(tmp_path: Path) -> None:
    """
    Refuse to install while another installation holds the plugins
    folder's lock.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder's parent.
    """
    folder = tmp_path / "plugins"
    folder.mkdir()
    lock = QLockFile(str(folder / ".install.lock"))
    assert lock.tryLock(0)
    try:
        with pytest.raises(OSError, match="lock"):
            install_pack(VIOLA_ZIP, folder=folder)
    finally:
        lock.unlock()


def test_installing_stops_at_an_unreadable_plugins_folder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Report the entries of the plugins folder that could not be checked,
    and install nothing.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder's parent.
    monkeypatch : pytest.MonkeyPatch
        Make the folder's listing report a problem.
    """
    monkeypatch.setattr(
        packs,
        "pack_manifests",
        lambda folder: ([], ["trouble — Input/output error"]),
    )
    with pytest.raises(OSError, match="trouble"):
        install_pack(VIOLA_ZIP, folder=tmp_path / "plugins")
    assert not (tmp_path / "plugins/viola.zip").exists()


def test_only_an_installed_zip_in_the_folder_can_be_updated(
    tmp_path: Path,
) -> None:
    """
    Refuse to update a plugin that is not a ZIP at the top of the
    plugins folder.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder's parent.
    """
    folder = tmp_path / "plugins"
    folder.mkdir()
    elsewhere = tmp_path / "viola.zip"
    shutil.copyfile(VIOLA_ZIP, elsewhere)
    shape = InstalledPlugin(
        title="Viola",
        path=elsewhere,
        manifest=elsewhere,
        snapshot=elsewhere.lstat(),
    )
    with pytest.raises(ValueError, match="Only an installed plugin ZIP"):
        install_pack(VIOLA_ZIP, folder=folder, replacing=shape)


def test_a_failed_move_into_place_is_reported(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Report the reason when the checked ZIP cannot be moved into the
    plugins folder.

    Parameters
    ----------
    tmp_path : Path
        The plugins folder's parent.
    monkeypatch : pytest.MonkeyPatch
        Make the move fail.
    """

    class Refusing:
        """A file that cannot be moved."""

        def __init__(self, name: str) -> None:
            """
            Remember the name.

            Parameters
            ----------
            name : str
                The file's name.
            """
            self.name = name

        def rename(self, target: str) -> bool:
            """
            Fail.

            Parameters
            ----------
            target : str
                Where the file was to go.

            Returns
            -------
            bool
                False, as Qt says when a move fails.
            """
            return False

        def errorString(self) -> str:  # noqa: N802
            """
            Say why, as Qt does.

            Returns
            -------
            str
                The reason.
            """
            return "Permission denied"

    monkeypatch.setattr(packs, "QFile", Refusing)
    with pytest.raises(OSError, match="Permission denied"):
        install_pack(VIOLA_ZIP, folder=tmp_path / "plugins")
