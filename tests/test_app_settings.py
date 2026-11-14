"""The settings dialog: its sections, the choices it saves and the pictures it shows."""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")
from PySide6.QtCore import (
    QEvent,
    Qt,
)
from PySide6.QtGui import (
    QColor,
    QPalette,
    QPixmap,
)
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QPushButton,
    QScrollArea,
    QToolButton,
)

from alto.ui import (
    app_settings,
    keyboard_styles,
    theme,
    theme_editor,
)
from alto.ui.app_settings import AppSettingsDialog
from alto.ui.theme_cards import ThemeCard
from alto.ui.theme_editor import ThemeEditor

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture
def dialog(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[AppSettingsDialog]:
    """
    Provide a settings dialog that never touches the saved settings.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.

    Yields
    ------
    AppSettingsDialog
        The dialog; it is closed afterwards.
    """
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(app_settings, "saved_theme", lambda: "dark")
    dlg = AppSettingsDialog()
    yield dlg
    dlg.deleteLater()  # gone before the application, or Qt crashes when Python exits
    QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_each_theme_has_a_preview_card_and_the_saved_one_is_chosen(dialog: AppSettingsDialog) -> None:
    """
    Check that each theme has a preview card and the saved one is chosen.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    assert list(dialog.theme_cards) == [family for family, _label, _note in theme.FAMILIES]
    assert list(dialog.theme_cards["default"].thumbs) == ["light", "dark", "system"]
    assert [key for key, thumb in dialog.theme_thumbs.items() if thumb.isChecked()] == ["dark"]


def test_every_theme_card_has_three_pictures_and_the_system_one_is_cut_in_two(dialog: AppSettingsDialog) -> None:
    """
    Check that each card has a Light, a Dark and a System picture, and that only the System one is drawn in two halves.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    for family, card in dialog.theme_cards.items():
        assert [thumb.other is not None for thumb in card.thumbs.values()] == [False, False, True], family
        light, dark, system = card.thumbs.values()
        assert system.colours == light.colours and system.other == dark.colours
        assert not light.grab().isNull() and not system.grab().isNull()


def test_the_segmented_control_switches_between_theme_and_notation_style(dialog: AppSettingsDialog) -> None:
    """
    Check that the segmented control switches between theme and notation style.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    assert dialog.appearance_pages.currentIndex() == 0
    dialog.segment_buttons[1].click()
    assert dialog.appearance_pages.currentIndex() == 1
    dialog.segment_buttons[0].click()
    assert dialog.appearance_pages.currentIndex() == 0


def test_a_palette_change_restyles_the_segmented_control(dialog: AppSettingsDialog) -> None:
    """
    Check that a palette change restyles the segmented control.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    before = dialog.segments.styleSheet()
    QApplication.sendEvent(dialog, QEvent(QEvent.Type.PaletteChange))
    assert dialog.segments.styleSheet() == before  # same palette, same style: redrawn without error


def test_choosing_a_theme_saves_and_applies_it(
    dialog: AppSettingsDialog,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that choosing a theme saves and applies it.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    applied = []
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(app_settings, "apply_theme", applied.append)
    assert not dialog.theme_changed
    dialog.theme_thumbs["light"].click()
    assert theme.saved_theme() == "light" and applied == ["light"] and dialog.theme_changed


def test_each_keyboard_style_has_a_card_and_the_classic_one_is_chosen_by_default(dialog: AppSettingsDialog) -> None:
    """
    Check that each keyboard style has a card and the classic one is chosen by default.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    assert list(dialog.keyboard_cards) == [*(s.key for s in keyboard_styles.STYLES), "custom"]
    assert [k for k, c in dialog.keyboard_cards.items() if c.isChecked()] == ["classic"]
    dialog.segment_buttons[2].click()
    assert dialog.appearance_pages.currentIndex() == 2
    for card in dialog.keyboard_cards.values():
        pix = QPixmap(card.size())
        card.render(pix)
        assert not pix.isNull()


def test_clicking_a_keyboard_card_applies_the_style(dialog: AppSettingsDialog) -> None:
    """
    Check that clicking a keyboard card applies the style.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    dialog.keyboard_cards["harpsichord-french"].click()
    assert keyboard_styles.current().key == "harpsichord-french"


def test_the_builder_colours_each_part_and_selects_the_custom_style(dialog: AppSettingsDialog) -> None:
    """
    Check that the builder colours each part and selects the custom style.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    dialog.builder._set("naturals", colour="#ead9aa")  # boxwood
    assert keyboard_styles.current().key == "custom" and keyboard_styles.custom_colours()["naturals"] == "#ead9aa"
    assert dialog.keyboard_cards["custom"].isChecked()
    assert dialog.keyboard_cards["custom"].keys.style_override.white[0] == "#ead9aa"  # the card previews it
    dialog.builder._set("felt", colour="#7d1f27")
    dialog.builder._set("felt", colour=None)  # an optional part can be left out
    assert keyboard_styles.custom_colours()["felt"] is None and keyboard_styles.current().felt is None
    assert dialog.builder.swatches["felt"].text() == "none"


def test_the_builder_has_a_chip_for_every_material_and_none_for_optional_parts(dialog: AppSettingsDialog) -> None:
    """
    Check that the builder has a chip for every material and none for optional parts.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    chips = dialog.builder.findChildren(QToolButton)
    required = sum(1 for _, _, optional in keyboard_styles.COMPONENTS if not optional)
    optional = len(keyboard_styles.COMPONENTS) - required
    assert len(chips) == len(keyboard_styles.COMPONENTS) * len(keyboard_styles.MATERIALS) + optional
    next(c for c in chips if c.toolTip().startswith("Ebony  ")).click()
    assert keyboard_styles.current().key == "custom"


def test_the_builder_opens_the_colour_picker_and_keeps_a_chosen_colour(
    dialog: AppSettingsDialog,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that the builder opens the colour picker and keeps a chosen colour.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    picked = iter([QColor("#336699"), QColor()])  # then the dialog is cancelled
    monkeypatch.setattr(app_settings.QColorDialog, "getColor", lambda *a, **k: next(picked))
    dialog.builder.swatches["case"].click()
    assert keyboard_styles.custom_colours()["case"] == "#336699"
    dialog.builder.swatches["case"].click()
    assert keyboard_styles.custom_colours()["case"] == "#336699"  # cancelled: unchanged


def test_a_theme_with_colours_of_its_own_sets_the_palette_and_gives_it_back(app: QApplication) -> None:
    """
    Check that Studio sets the application's palette, that Studio Night is dark, and that going back to System lets go of it.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    window = QPalette.ColorRole.Window
    try:
        theme.apply_theme("studio")
        assert QApplication.palette().color(window).name() == "#eceef1"
        assert QApplication.palette().color(QPalette.ColorRole.Highlight).name() == "#2f7fc1"
        theme.apply_theme("studio_dark")
        assert QApplication.palette().color(window).name() == "#1b1e23"
        assert QApplication.palette().color(QPalette.ColorRole.WindowText).lightness() > 200  # light text on the dark window
        theme.apply_theme("system")
        assert QApplication.palette().color(window).name() not in {"#eceef1", "#1b1e23"}
    finally:
        theme.apply_theme("system")


def test_the_theme_list_is_on_the_left_and_the_card_of_the_chosen_row_on_the_right(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check the Theme section: the list on the left, the card on the right, and that the version last chosen is kept down the list.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    applied: list[str] = []
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(app_settings, "apply_theme", applied.append)
    theme.save_theme("system")
    dialog = AppSettingsDialog()
    dialog.resize(1100, 700)
    dialog.show()
    try:
        listing, pages = dialog.theme_list, dialog.theme_pages
        assert listing.mapTo(dialog, listing.rect().topLeft()).x() < pages.mapTo(dialog, pages.rect().topLeft()).x()
        # two section labels and the row that makes a new theme, as well as a row for each theme
        assert listing.count() == len(theme.FAMILIES) + 3 and len(dialog.theme_thumbs) == 3 * len(theme.FAMILIES)
        assert dialog.new_theme_item.text().endswith("New theme…")
        tops = [thumb.mapTo(dialog, thumb.rect().topLeft()).y() for thumb in dialog.theme_cards["default"].thumbs.values()]
        assert tops == sorted(tops) and len(set(tops)) == 3  # the three pictures are one above another
        assert pages.currentWidget() is dialog.theme_scrolls["default"] and dialog.theme_thumbs["system"].isChecked()
        # choosing a row shows its card and uses the theme, in the version last chosen: System, to begin with
        listing.setCurrentItem(dialog.theme_items["sage"])
        assert pages.currentWidget() is dialog.theme_scrolls["sage"]
        assert theme.saved_theme() == "sage_auto" and applied == ["sage_auto"] and dialog.theme_thumbs["sage_auto"].isChecked()
        assert dialog.theme_items["sage"].font().bold() and not dialog.theme_items["default"].font().bold()
        dialog.theme_thumbs["sage_dark"].click()  # a click chooses a version, which is then kept
        assert theme.saved_theme() == "sage_dark" and not dialog.theme_thumbs["sage_auto"].isChecked()
        listing.setCurrentItem(dialog.theme_items["pine"])
        assert theme.saved_theme() == "pine_dark" and applied[-1] == "pine_dark" and dialog.theme_thumbs["pine_dark"].isChecked()
        dialog.theme_thumbs["pine"].click()  # now the light version is the one that is kept
        listing.setCurrentItem(dialog.theme_items["default"])
        assert theme.saved_theme() == "light" and dialog.theme_thumbs["light"].isChecked()
        dialog.theme_thumbs["dark"].click()
        listing.setCurrentItem(dialog.theme_items["marigold"])
        assert theme.saved_theme() == "marigold_dark"
    finally:
        theme.save_theme("system")
        dialog.close()


def test_the_dialog_opens_on_the_theme_in_use(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that the list opens on the row of the theme in use, with that version marked on its card.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    monkeypatch.setattr(theme, "system_is_dark", lambda: False)
    theme.save_theme("pine_dark")
    try:
        dialog = AppSettingsDialog()
        assert dialog.theme_list.currentItem() is dialog.theme_items["pine"]
        assert dialog.theme_pages.currentWidget() is dialog.theme_scrolls["pine"]
        assert dialog.theme_thumbs["pine_dark"].isChecked()
    finally:
        theme.save_theme("system")


def test_a_system_version_of_a_theme_is_light_or_dark_as_the_desktop_is(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that the System version of a theme uses its light colours on a light desktop and its dark colours on a dark one.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    window = QPalette.ColorRole.Window
    light, dark = theme.custom_theme("sage"), theme.custom_theme("sage_dark")
    assert light is not None and dark is not None
    try:
        monkeypatch.setattr(theme, "system_is_dark", lambda: False)
        theme.apply_theme("sage_auto")
        assert QApplication.palette().color(window).name() == light.window
        monkeypatch.setattr(theme, "system_is_dark", lambda: True)
        theme.apply_theme("sage_auto")
        assert QApplication.palette().color(window).name() == dark.window
        theme.save_theme("sage_auto")
        theme._desktop_changed()  # the desktop changing makes a theme that follows it apply again
        monkeypatch.setattr(theme, "system_is_dark", lambda: False)
        theme._desktop_changed()
        assert QApplication.palette().color(window).name() == light.window
    finally:
        theme.save_theme("system")
        theme.apply_theme("system")


def test_the_themes_are_made_from_their_seeds_in_a_light_and_a_dark_version(app: QApplication) -> None:
    """
    Check the generated themes: a pair each, unique keys, dark ones dark, and the colours the preview page showed.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    keys = [custom.key for custom in theme.CUSTOM_THEMES]
    assert len(set(keys)) == len(keys) == 2 * (len(theme.SEEDS) + 1)
    for custom in theme.CUSTOM_THEMES:
        assert custom.dark == custom.key.endswith("_dark")
        assert QColor(custom.window).lightness() < QColor(custom.ink).lightness() if custom.dark else True
        assert QColor(custom.window).lightness() > QColor(custom.ink).lightness() if not custom.dark else True
    parchment = theme.custom_theme("parchment")
    assert parchment is not None and (parchment.window, parchment.accent, parchment.ink) == ("#f3f1ec", "#ae4329", "#2e2719")
    assert theme.family_of("sage_dark") == ("sage", "dark") and theme.variant_key("sage", version="dark") == "sage_dark"
    assert theme.family_of("sage_auto") == ("sage", "system") and theme.variant_key("default", version="system") == "system"


def test_the_card_writes_out_the_window_accent_and_ink_colours_of_each_version(app: QApplication) -> None:
    """
    Check that the Light and Dark rows of a card say the window, accent and ink colours in hexadecimal, and the others do not.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    card = ThemeCard("parchment")
    texts = [label.text() for label in card.findChildren(QLabel)]
    light, dark = theme.custom_theme("parchment"), theme.custom_theme("parchment_dark")
    assert light is not None and dark is not None
    assert f"window {light.window}   accent {light.accent}   ink {light.ink}" in texts
    assert f"window {dark.window}   accent {dark.accent}   ink {dark.ink}" in texts
    assert sum(text.startswith("window #") for text in texts) == 2  # not for System, which is both
    assert not any(text.startswith("window #") for text in [label.text() for label in ThemeCard("default").findChildren(QLabel)])


def test_the_squares_of_a_theme_are_beside_its_pictures_and_not_at_the_bottom(app: QApplication) -> None:
    """
    Check that the Light and Dark rows of a card have the squares of their colours.

    "Always light" and "Always dark" are gone from a theme that has its own colours.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    card = ThemeCard("sage")
    card.show()
    squares = [frame for frame in card.findChildren(QFrame) if frame.width() == 18 and frame.height() == 18]
    assert len(squares) == 14  # seven for the light version, seven for the dark
    light, dark = card.thumbs["sage"], card.thumbs["sage_dark"]
    light_top, dark_top = light.mapTo(card, light.rect().topLeft()).y(), dark.mapTo(card, dark.rect().topLeft()).y()
    for frame in squares[:7]:  # level with the Light picture
        assert light_top <= frame.mapTo(card, frame.rect().center()).y() <= light_top + light.height()
    for frame in squares[7:]:  # level with the Dark picture
        assert dark_top <= frame.mapTo(card, frame.rect().center()).y() <= dark_top + dark.height()
    texts = [label.text() for label in card.findChildren(QLabel)]
    assert "Always light." not in texts and "Always dark." not in texts and "Light or dark as the desktop is." in texts
    plain = [label.text() for label in ThemeCard("default").findChildren(QLabel)]
    assert "Always light." in plain and "Always dark." in plain  # the desktop's own colours have no squares to show


@pytest.fixture
def no_user_themes() -> Iterator[None]:
    """
    Start a test with no themes of the user's own saved, and leave none behind.

    Yields
    ------
    None
        Once any that were saved are cleared.
    """
    theme.save_user_records([])
    yield
    theme.save_theme("system")
    theme.apply_theme("system")
    theme.save_user_records([])


def test_a_theme_can_be_made_saved_and_used(
    app: QApplication,
    no_user_themes: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that the row that makes a new theme opens the editor, that a theme made there is saved, appears in the list and is used.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    no_user_themes : None
        Clears the themes of the user's own.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    dialog = AppSettingsDialog()
    dialog.resize(1100, 700)
    dialog.show()
    editor = dialog.theme_editor
    dialog.theme_list.setCurrentItem(dialog.new_theme_item)
    assert dialog.theme_pages.currentWidget() is editor and theme.saved_theme() == "system"  # nothing is used while it is made
    editor.name_edit.setText("Harbour Lights")
    editor.colours["light"]["accent"] = "#ff00aa"
    sage_row = editor.start_from.findData("sage")
    editor.start_from.setCurrentIndex(sage_row)
    editor.start_from.activated.emit(sage_row)  # choosing a theme in the list takes its colours, with no button to press
    editor.colours["dark"]["accent"] = "#00ffcc"
    editor.save_button.click()
    records = theme.user_records()
    assert len(records) == 1 and records[0]["name"] == "Harbour Lights"
    sage = theme.custom_theme("sage")
    assert sage is not None and records[0]["dark"]["accent"] == "#00ffcc" and records[0]["light"]["window"] == sage.window
    family = records[0]["id"]
    assert family.startswith("my_") and family in dialog.theme_items and family in dialog.theme_cards
    assert dialog.theme_list.item(0).text() == "MY THEMES" and dialog.theme_items[family].text() == "Harbour Lights"
    assert dialog.theme_pages.currentWidget() is dialog.theme_scrolls[family]
    assert theme.saved_theme() == f"{family}_auto"  # in the version that was last chosen: System
    assert theme.custom_theme(f"{family}_dark") is not None and theme.scheme_of(f"{family}_dark") == Qt.ColorScheme.Dark
    dialog.theme_thumbs[f"{family}_dark"].click()
    assert QApplication.palette().color(QPalette.ColorRole.Highlight).name() == "#00ffcc"
    dialog.close()
    again = AppSettingsDialog()  # and it is still there the next time
    assert theme.family_of(theme.saved_theme()) == (family, "dark") and family in again.theme_items
    assert again.theme_list.currentItem() is again.theme_items[family]


def test_a_theme_that_was_made_can_be_changed_and_deleted(
    app: QApplication,
    no_user_themes: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that a theme of the user's own has a Change colours button, and that the colour picker changes a colour.

    Deleting a theme asks first, and goes back to the desktop's colours if it was in use.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    no_user_themes : None
        Clears the themes of the user's own.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    colours = {part: "#112233" for part in theme.PARTS}
    theme.upsert_user_theme(theme.ThemeRecord(id="my_test", name="Mine", light=dict(colours), dark=dict(colours)))
    dialog = AppSettingsDialog()
    dialog.show()
    assert theme.custom_theme("my_test") is not None and dialog.theme_cards["my_test"].change_button is not None
    assert dialog.theme_cards["sage"].change_button is None  # only a theme of the user's own can be changed
    dialog.theme_list.setCurrentItem(dialog.theme_items["my_test"])
    dialog.theme_cards["my_test"].change_button.click()
    editor = dialog.theme_editor
    assert (
        dialog.theme_pages.currentWidget() is editor and editor.name_edit.text() == "Mine" and not editor.delete_button.isHidden()
    )
    monkeypatch.setattr(theme_editor.QColorDialog, "getColor", lambda *args, **kwargs: QColor("#abcdef"))
    editor.buttons["light"]["accent"].click()  # the picker answers with a colour
    assert editor.colours["light"]["accent"] == "#abcdef"
    editor.name_edit.setText("Mine, changed")
    editor.save_button.click()
    assert [(r["name"], r["light"]["accent"]) for r in theme.user_records()] == [("Mine, changed", "#abcdef")]
    # asked first, and "No" keeps it
    monkeypatch.setattr(app_settings.QMessageBox, "question", lambda *args, **kwargs: app_settings.QMessageBox.StandardButton.No)
    dialog.theme_cards["my_test"].change_button.click()
    editor.delete_button.click()
    assert len(theme.user_records()) == 1
    monkeypatch.setattr(app_settings.QMessageBox, "question", lambda *args, **kwargs: app_settings.QMessageBox.StandardButton.Yes)
    assert theme.family_of(theme.saved_theme())[0] == "my_test"
    editor.delete_button.click()
    assert theme.user_records() == [] and "my_test" not in dialog.theme_items
    assert theme.saved_theme() == "system"  # it was in use, so the desktop's own colours are back
    dialog.close()


def test_a_saved_theme_that_cannot_be_read_is_left_out(app: QApplication, no_user_themes: None) -> None:
    """
    Check that damaged saved themes give nothing, and that a good one beside a bad one is kept.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    no_user_themes : None
        Clears the themes of the user's own.
    """
    good = {part: "#112233" for part in theme.PARTS}
    theme.store().setValue("ui/userThemes", "not json at all")
    assert theme.user_records() == [] and theme.user_themes() == ()
    kept = {"id": "my_ok", "name": "Ok", "light": good, "dark": good}
    damaged = [3, {"id": "my_x"}, {"id": "other", "name": "No", "light": {}, "dark": {}}, kept]
    theme.store().setValue("ui/userThemes", json.dumps(damaged))
    assert [record["id"] for record in theme.user_records()] == ["my_ok"]
    assert [item.key for item in theme.user_themes()] == ["my_ok", "my_ok_dark"]
    assert theme.saved_theme() == "system"  # nothing that is saved can make this a theme that does not exist


def test_the_editors_buttons_stay_in_view_at_the_top_and_its_fields_take_the_apps_style(
    app: QApplication,
    no_user_themes: None,
) -> None:
    """
    Check that Save and Cancel are above the form, so that scrolling the form does not take them away.

    The name and the "Start from" box are marked for the rounded style of the app.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    no_user_themes : None
        Clears the themes of the user's own.
    """
    theme.apply_theme("system")
    dialog = AppSettingsDialog()
    dialog.resize(1000, 480)  # short, so that the form has to scroll
    dialog.show()
    dialog.theme_list.setCurrentItem(dialog.new_theme_item)
    editor = dialog.theme_editor
    scroll = editor.findChild(QScrollArea)
    assert scroll is not None and scroll.verticalScrollBar().maximum() > 0  # the form is taller than the room it has
    save_top = editor.save_button.mapTo(editor, editor.save_button.rect().topLeft()).y()
    assert save_top < scroll.mapTo(editor, scroll.rect().topLeft()).y()  # above the form, not inside it
    scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())
    assert (
        editor.save_button.isVisible() and editor.save_button.mapTo(editor, editor.save_button.rect().topLeft()).y() == save_top
    )
    assert editor.save_button.property("primary") is True
    assert editor.name_edit.property("field") is True and editor.start_from.property("field") is True
    sheet = QApplication.instance().styleSheet()  # type: ignore[union-attr]
    assert 'QLineEdit[field="true"]' in sheet and 'QComboBox[field="true"]' in sheet and 'QPushButton[primary="true"]' in sheet
    dialog.close()


def test_choosing_in_start_from_takes_the_colours_at_once_and_there_is_no_copy_button(
    app: QApplication,
    no_user_themes: None,
) -> None:
    """
    Check that picking a theme in "Start from" changes the colours straight away, and that the button that did it is gone.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    no_user_themes : None
        Clears the themes of the user's own.
    """
    editor = ThemeEditor()
    assert "Copy its colours" not in [button.text() for button in editor.findChildren(QPushButton)]
    studio, pine = theme.custom_theme("studio"), theme.custom_theme("pine_dark")
    assert studio is not None and pine is not None
    assert editor.colours["light"]["window"] == studio.window  # a new theme starts as Studio
    row = editor.start_from.findData("pine")
    editor.start_from.setCurrentIndex(row)
    editor.start_from.activated.emit(row)
    assert editor.colours["dark"]["window"] == pine.window and editor.pictures["dark"].colours["window"] == pine.window
    editor.load(theme.ThemeRecord(id="my_x", name="X", light=dict(editor.colours["light"]), dark=dict(editor.colours["dark"])))
    offered = [editor.start_from.itemData(row) for row in range(editor.start_from.count())]
    assert editor.start_from.currentData() is None and "my_x" not in offered  # it does not offer itself
    editor.start_from.activated.emit(0)  # the line that asks for a choice takes nothing
    assert editor.colours["dark"]["window"] == pine.window
    editor.show()
    name_left = editor.name_edit.mapTo(editor, editor.name_edit.rect().topLeft()).x()
    assert name_left == editor.start_from.mapTo(editor, editor.start_from.rect().topLeft()).x()  # the fields line up


def test_the_editors_colour_buttons_light_up_on_hover_and_show_a_hand(app: QApplication, no_user_themes: None) -> None:
    """
    Check that every colour button has a hover ring that shows on its colour, a pointing hand, and a tooltip that says to click.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    no_user_themes : None
        Clears the themes of the user's own.
    """
    editor = ThemeEditor()
    for version in ("light", "dark"):
        for part in theme.PARTS:
            button = editor.buttons[version][part]
            ring = "#ffffff" if QColor(editor.colours[version][part]).lightness() < 140 else "#1a1a1a"
            assert f"QPushButton:hover {{ border: 3px solid {ring}; }}" in button.styleSheet()  # a ring that shows on its colour
            assert button.cursor().shape() == Qt.CursorShape.PointingHandCursor
            assert button.toolTip().startswith("Click to change")
    first = editor.buttons["light"]["window"]
    assert editor.colours["light"]["window"] in first.styleSheet()  # and it still shows its own colour


def test_the_code_beside_a_colour_lights_up_with_the_colour(app: QApplication, no_user_themes: None) -> None:
    """
    Check that pointing at a colour button makes the hex code beside it bold and dark, and that leaving puts it back.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    no_user_themes : None
        Clears the themes of the user's own.
    """
    editor = ThemeEditor()
    editor.resize(700, 600)
    editor.show()
    button, code = editor.buttons["dark"]["accent"], editor._values["dark"]["accent"]
    other = editor._values["light"]["accent"]
    assert "bold" not in code.styleSheet()
    QTest.mouseMove(button, button.rect().center())
    QTest.qWait(50)
    assert "bold" in code.styleSheet() and "palette(text)" in code.styleSheet()
    assert "bold" not in other.styleSheet()  # only the one that is pointed at
    QApplication.sendEvent(button, QEvent(QEvent.Type.Leave))  # the pointer goes away
    assert "bold" not in code.styleSheet()
    editor.close()
