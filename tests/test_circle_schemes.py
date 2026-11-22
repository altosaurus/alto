"""
The color schemes of the circle of fifths: the presets, the schemes of the user's own, and the settings pages that choose them.
"""

from __future__ import annotations

import random

from PySide6.QtCore import QPoint
from PySide6.QtGui import (
    QColor,
    QPalette,
)
from PySide6.QtWidgets import QApplication

from alto import settings
from alto.circle_schemes import (
    CUSTOM_LIMIT,
    DEFAULT_SCHEME,
    MAX_BRIGHTNESS,
    PRESETS,
    CustomRecord,
    clean_record,
    custom_scheme,
    dump_customs,
    hex_of,
    hsl_of,
    load_customs,
    next_custom_key,
    record_of,
    resolve,
)
from alto.exercises.library import CircleOfFifths
from alto.ui import exercise_settings as es
from alto.ui import settings_panel as sp
from alto.ui.circle import (
    FifthsCircle,
    wedge_color,
    wedge_middle,
)
from alto.ui.circle_colors import SchemeEditor
from alto.ui.exercise_view import ExerciseView
from alto.ui.store import store

MINE = record_of("custom-1", name="Mine", mode="rings", colors=["#2f6bd0", "#18a0c0"])


def test_legacy_color_settings_survive_the_spelling_change() -> None:
    """
    Check that earlier preset choices and custom schemes retain their colors after loading.
    """
    legacy = dict(MINE)
    legacy["colours"] = legacy.pop("colors")
    assert clean_record(legacy) == MINE
    assert resolve("colour-blind", customs=[]).key == "color-blind"
    assert resolve("chequer", customs=[]).key == "checker"
    store().setValue("circle/scheme", "colour-blind")
    store().setValue(
        "circle/customSchemes",
        '[{"id":"custom-1","name":"Sea","mode":"single","colours":["#00ffff"],"light":false}]',
    )
    try:
        es.load_circle()
        assert settings.circle.scheme == "color-blind"
        assert settings.circle.customs[0]["colors"] == ["#00ffff"]
    finally:
        store().remove("circle")
        es.load_circle()


def test_there_are_fourteen_presets_and_cyan_to_indigo_is_the_default_and_comes_first() -> None:
    """
    Check the list of presets: their number, their keys and names, and the default.
    """
    assert len(PRESETS) == 14 and next(iter(PRESETS)) == DEFAULT_SCHEME == "cyan-indigo"
    assert len({scheme.name for scheme in PRESETS.values()}) == 14
    for key, scheme in PRESETS.items():
        assert scheme.key == key and scheme.description and len(scheme.cells["outer"]) == len(scheme.cells["inner"]) == 12


def test_a_cell_is_never_too_bright_for_white_names_on_dark_wedges_and_a_lit_one_differs_from_a_quiet_one() -> None:
    """
    Check every preset: on dark wedges no cell is brighter than white names can be read on, and lighting a cell changes it.
    """
    for scheme in PRESETS.values():
        for ring in ("outer", "inner"):
            for place in range(12):
                quiet, lit = scheme.color(ring, place=place, lift=0.0), scheme.color(ring, place=place, lift=1.0)
                assert quiet != lit, (scheme.key, ring, place)
                for lift in (0.0, 0.5, 1.0):
                    red, green, blue = scheme.color(ring, place=place, lift=lift)
                    assert scheme.light or 0.299 * red + 0.587 * green + 0.114 * blue <= MAX_BRIGHTNESS + 0.01, (
                        scheme.key,
                        place,
                    )


def test_in_cyan_to_indigo_the_flat_keys_are_cyan_the_sharp_keys_indigo_and_c_between() -> None:
    """
    Check the default scheme's idea: hue goes from cyan through royal blue at C to indigo as sharps are added.
    """
    scheme = PRESETS["cyan-indigo"]
    hue = {place: hsl_of(hex_of(scheme.color("outer", place=place, lift=1.0)))[0] for place in range(12)}
    assert 185 < hue[7] < 200  # five flats: cyan
    assert 214 < hue[0] < 222  # C: royal blue
    assert 250 < hue[6] < 258  # six sharps: indigo
    assert (
        hue[7] < hue[9] < hue[11] < hue[0] < hue[1] < hue[3] < hue[6]
    )  # steadily from cyan to indigo along the circle's sharps and flats


def test_light_presets_have_light_wedges_with_dark_names_and_the_others_the_opposite() -> None:
    """
    Check that the colors of the names follow the wedges.
    """
    assert {key for key, scheme in PRESETS.items() if scheme.light} == {"glacier", "paper"}
    assert PRESETS["paper"].names()["ink"] == "#1b2030" and PRESETS["midnight"].names()["ink"] == "#f5f5f5"


def test_a_saved_choice_that_is_gone_falls_back_to_the_default_and_a_custom_one_is_found() -> None:
    """
    Check how a key is turned into a scheme.
    """
    assert resolve("gone", customs=[]).key == DEFAULT_SCHEME
    assert resolve("midnight", customs=[MINE]).name == "Midnight"
    assert resolve("custom-1", customs=[MINE]).name == "Mine"
    assert resolve("custom-2", customs=[MINE]).key == DEFAULT_SCHEME


def test_records_that_are_not_valid_are_refused_and_the_rest_are_tidied() -> None:
    """
    Check the validation of what is read back from the saved settings.
    """
    assert clean_record(MINE) == MINE
    assert clean_record({**MINE, "name": "  " + "x" * 80})["name"] == "x" * 40  # type: ignore[index]
    assert clean_record({**MINE, "name": "   "})["name"] == "My colors"  # type: ignore[index]
    for bad in (
        None,
        [],
        {**MINE, "mode": "nope"},
        {**MINE, "colors": ["#2f6bd0"]},
        {**MINE, "colors": ["#2f6bd0", "blue"]},
        {**MINE, "colors": ["#2f6bd0", 5]},
        {**MINE, "light": "no"},
        {**MINE, "id": 3},
        {key: value for key, value in MINE.items() if key != "name"},
    ):
        assert clean_record(bad) is None, bad


def test_saved_schemes_survive_a_round_trip_and_bad_ones_and_clashing_keys_are_left_out() -> None:
    """
    Check writing and reading the user's schemes, including the limit.
    """
    assert load_customs(dump_customs([MINE])) == [MINE]
    assert load_customs("not json") == [] and load_customs('{"a": 1}') == []
    clash = {**MINE, "id": "midnight"}  # a preset's key would hide the preset
    assert load_customs(dump_customs([clash, MINE, MINE])) == [MINE]  # type: ignore[list-item]
    many = [{**MINE, "id": f"custom-{n}"} for n in range(CUSTOM_LIMIT + 5)]
    assert len(load_customs(dump_customs(many))) == CUSTOM_LIMIT  # type: ignore[arg-type]
    assert next_custom_key([MINE]) == "custom-2" and next_custom_key([]) == "custom-1"


def test_each_way_of_making_a_scheme_gives_the_colors_it_promises() -> None:
    """
    Check the five modes of the editor: what hue each cell gets.
    """

    def lit(
        record: CustomRecord,
        *,
        ring: str,
        place: int,
    ) -> float:
        """
        Return the hue of a cell when it is lit.

        Parameters
        ----------
        record : CustomRecord
            The scheme.
        ring : str
            "outer" or "inner". Keyword-only.
        place : int
            The cell. Keyword-only.

        Returns
        -------
        float
            Its hue, from 0 to 360.
        """
        return custom_scheme(record).cells[ring][place][1][0]

    single = record_of("custom-1", name="Mine", mode="single", colors=["#ff0000"])
    assert {lit(single, ring=ring, place=place) for ring in ("outer", "inner") for place in range(12)} == {0.0}
    assert lit(MINE, ring="outer", place=3) != lit(MINE, ring="inner", place=3)
    signature = record_of("custom-1", name="Mine", mode="signature", colors=["#00ffff", "#0000ff", "#ff00ff"])
    assert (
        lit(signature, ring="outer", place=0) == 240.0
        and lit(signature, ring="outer", place=6) == 300.0
        and lit(signature, ring="outer", place=7) < 240.0
    )
    distance = record_of("custom-1", name="Mine", mode="distance", colors=["#ff0000", "#00ff00"])
    assert (
        lit(distance, ring="outer", place=0) == 0.0
        and lit(distance, ring="outer", place=6) == 120.0
        and lit(distance, ring="outer", place=5)
        == lit(distance, ring="outer", place=7)  # five sharps and five flats are as far from C
    )
    wheel = record_of("custom-1", name="Mine", mode="wheel", colors=["#ff0000"])
    assert [lit(wheel, ring="outer", place=place) for place in (0, 1, 6)] == [0.0, 30.0, 180.0]


def test_a_light_scheme_of_your_own_has_light_wedges_that_darken_when_lit() -> None:
    """
    Check the direction of the glow for a light custom scheme.
    """
    scheme = custom_scheme(record_of("custom-1", name="Mine", mode="rings", colors=["#2f6bd0", "#18a0c0"], light=True))
    assert scheme.light
    quiet, lit = scheme.cells["outer"][0]
    assert lit[2] < quiet[2]


def test_the_wedges_take_the_scheme_chosen_and_the_disc_in_the_middle_takes_the_apps_background(app: QApplication) -> None:
    """
    Check by looking at the pixels: choosing a scheme changes the wedges, and the disc is the window color, light or dark.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    circle = FifthsCircle()
    circle.setAutoFillBackground(False)
    circle.resize(500, 500)
    center, radius = circle.geometry_of()
    wedge = wedge_middle(center=center, radius=0.87 * radius, index=3)
    middle = QPoint(int(center.x() + 0.15 * radius), int(center.y() - 0.1 * radius))  # inside the disc, clear of the words
    seen = {}
    for key in ("midnight", "paper"):
        settings.circle.scheme = key
        seen[key] = circle.grab().toImage().pixelColor(int(wedge.x()), int(wedge.y()))
        assert seen[key].name() == wedge_color(3, inner=False).name()
    assert seen["midnight"] != seen["paper"]
    for window in ("#f4f4f6", "#202124"):  # a light theme and a dark one
        palette = circle.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(window))
        circle.setPalette(palette)
        for key in ("midnight", "paper"):
            settings.circle.scheme = key
            assert circle.grab().toImage().pixelColor(middle).name() == window, (key, window)


def test_the_colors_page_chooses_creates_edits_and_deletes_and_it_all_survives_a_restart(
    app: QApplication,
) -> None:
    """
    Check the whole path through the settings: choose a preset, make a scheme, change it, delete it, and load it all back.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.circle.scheme = DEFAULT_SCHEME
    settings.circle.customs = []

    def chosen() -> str:
        """
        Return the key of the scheme in the settings now.

        Returns
        -------
        str
            The key.
        """
        return settings.circle.scheme

    view = ExerciseView(CircleOfFifths(), rng=random.Random(4))
    pane = view.settings_panel
    assert isinstance(pane, sp.CircleSettingsPanel) and pane.colors_row.value.text() == "Cyan to indigo"
    assert len(pane.schemes.thumbs) == 14 and pane.schemes.thumbs[DEFAULT_SCHEME].isChecked()
    asked, restyled = [], []
    question = view.question
    pane.restyled.connect(lambda: restyled.append(1))
    pane.changed.connect(lambda: asked.append(1))
    pane.schemes.thumbs["ember"].click()
    assert chosen() == "ember" and store().value("circle/scheme") == "ember"
    assert (
        pane.colors_row.value.text() == "Ember" and restyled == [1] and asked == [] and view.question is question
    )  # same question
    pane.schemes.new.emit()
    pane.editor.name.setText("Sea")
    pane.editor.set_color(0, color="#00ffff")
    pane.editor.saved.emit(pane.editor.record())
    assert chosen() == "custom-1" and [r["name"] for r in settings.circle.customs] == ["Sea"]
    assert "custom-1" in pane.schemes.thumbs and pane.colors_row.value.text() == "Sea"
    settings.circle.scheme, settings.circle.customs = DEFAULT_SCHEME, []
    es.load_circle()
    assert chosen() == "custom-1" and settings.circle.customs[0]["colors"][0] == "#00ffff"  # a restart finds it
    pane.schemes.edit_asked.emit("custom-1")
    assert pane.editor.name.text() == "Sea" and not pane.editor.delete_button.isHidden()
    pane.editor.deleted.emit("custom-1")
    assert settings.circle.customs == [] and chosen() == DEFAULT_SCHEME and "custom-1" not in pane.schemes.thumbs
    store().remove("circle")


def test_a_saved_scheme_that_no_longer_exists_loads_as_the_default() -> None:
    """
    Check that loading never leaves the circle without a scheme.
    """
    settings.circle.scheme = "midnight"
    store().setValue("circle/scheme", "custom-9")
    es.load_circle()
    assert settings.circle.scheme == DEFAULT_SCHEME
    store().setValue("circle/customSchemes", "garbage")
    es.load_circle()
    assert settings.circle.customs == []
    store().remove("circle")


def test_the_editor_shows_only_the_colors_its_way_of_making_a_scheme_takes() -> None:
    """
    Check the number of color buttons for each way of making a scheme.
    """
    editor = SchemeEditor()
    editor.load(None, taken=[])
    for mode, count in {"single": 1, "rings": 2, "signature": 3, "distance": 2, "wheel": 1}.items():
        editor.mode.setCurrentIndex(editor.mode.findData(mode))
        assert [not button.isHidden() for button in editor.swatches] == [number < count for number in range(3)], mode
        assert len(editor.record()["colors"]) == count


def test_opening_the_colors_pages_never_makes_the_exercise_or_its_window_bigger(app: QApplication) -> None:
    """
    Check that the long list of color schemes and the editor scroll inside the settings pane instead of growing the window.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(CircleOfFifths(), rng=random.Random(4))
    pane = view.settings_panel
    assert isinstance(pane, sp.CircleSettingsPanel) and view.gear is not None
    view.resize(900, 600)
    view.show()
    app.processEvents()
    smallest = view.minimumSizeHint().height()
    size = view.size()
    view.gear.setChecked(True)
    app.processEvents()
    for page in (0, 1, 2, 3):
        pane.stack.setCurrentIndex(page)
        pane.schemes.load(
            current="ember",
            customs=[record_of(f"custom-{n}", name="Mine", mode="single", colors=["#2f6bd0"]) for n in range(1, 9)],
        )
        app.processEvents()
        assert view.minimumSizeHint().height() <= smallest + 4, page  # no page asks for more room than the exercise needs
        assert view.size() == size, page
