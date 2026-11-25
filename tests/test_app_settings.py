"""
The settings dialog: its sections, the choices it saves and the pictures
it shows.
"""

from __future__ import annotations

import gc
import json
import os
from typing import TYPE_CHECKING
from unittest.mock import Mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")
from PySide6.QtCore import (
    QEvent,
    QPoint,
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

from alto import audio, updates
from alto.ui import (
    app_settings,
    keyboard_styles,
    metronome_spectrum,
    notation,
    theme,
    theme_editor,
)
from alto.ui.app_settings import AppSettingsDialog
from alto.ui.store import store
from alto.ui.theme_cards import ThemeCard
from alto.ui.theme_editor import ThemeEditor
from alto.ui.update_flow import (
    save_channel,
    saved_channel,
)

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
        Replaces settings, functions or attributes for the length of the
        test.

    Yields
    ------
    AppSettingsDialog
        The dialog; it is closed afterwards.
    """
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(app_settings, "saved_theme", lambda: "dark")
    dlg = AppSettingsDialog()
    dlg.categories.setCurrentRow(1)
    yield dlg
    # gone before the application, or Qt crashes when Python exits
    dlg.deleteLater()
    QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_each_theme_has_a_preview_card_and_the_saved_one_is_chosen(
    dialog: AppSettingsDialog,
) -> None:
    """
    Check that each theme has a preview card and the saved one is
    chosen.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    assert list(dialog.theme_items) == [
        family for family, _label, _note in theme.FAMILIES
    ]
    assert list(dialog.card("default").thumbs) == ["light", "dark", "system"]
    assert [
        key for key, thumb in dialog.theme_thumbs.items() if thumb.isChecked()
    ] == ["dark"]
    assert list(dialog.theme_cards) == [
        "default",
    ]  # the cards of the other themes are built when they are chosen


def test_every_theme_card_has_three_pictures_and_the_system_one_is_cut_in_two(
    dialog: AppSettingsDialog,
) -> None:
    """
    Check that each card has a Light, a Dark and a System picture, and
    that only the System one is drawn in two halves.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    for family in dialog.theme_items:
        card = dialog.card(family)
        assert [thumb.other is not None for thumb in card.thumbs.values()] == [
            False,
            False,
            True,
        ], family
        light, dark, system = card.thumbs.values()
        assert system.colors == light.colors and system.other == dark.colors
        assert not light.grab().isNull() and not system.grab().isNull()


def test_the_segmented_control_switches_between_theme_and_notation_style(
    dialog: AppSettingsDialog,
) -> None:
    """
    Check that the segmented control switches between theme and notation
    style.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    assert dialog.appearance_pages.currentIndex() == 0
    dialog.categories.setCurrentRow(2)
    assert dialog.appearance_pages.currentIndex() == 1
    dialog.categories.setCurrentRow(1)
    assert dialog.appearance_pages.currentIndex() == 0


def test_hidden_settings_pages_are_built_on_first_visit_and_reused(
    dialog: AppSettingsDialog,
) -> None:
    """
    Check that unused previews do not exist and that revisiting a page
    preserves its widgets and selection.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    assert not dialog.findChildren(app_settings.StyleCard)
    assert not dialog.findChildren(app_settings.KeyboardCard)
    assert not dialog.findChildren(app_settings.InstrumentPicker)
    assert not dialog.findChildren(app_settings.TransitionPreview)
    dialog.categories.setCurrentRow(2)
    page = dialog.appearance_pages.currentWidget()
    assert len(dialog.findChildren(app_settings.StyleCard)) == len(
        notation.STYLES,
    )
    dialog.categories.setCurrentRow(1)
    dialog.categories.setCurrentRow(2)
    assert dialog.appearance_pages.currentWidget() is page
    dialog.categories.setCurrentRow(6)
    sound = dialog.pages.currentWidget()
    dialog.instruments.select("flute")
    dialog.categories.setCurrentRow(8)
    dialog.categories.setCurrentRow(6)
    assert (
        dialog.pages.currentWidget() is sound
        and dialog.instruments.shown == "Flute"
    )


def test_a_page_first_opened_after_a_theme_change_uses_the_new_palette(
    dialog: AppSettingsDialog,
) -> None:
    """
    Check that a page built after changing themes inherits the current
    colors.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    try:
        dialog.choose_theme("studio_dark")
        dialog.categories.setCurrentRow(6)
        role = QPalette.ColorRole.Window
        assert dialog.instruments.palette().color(
            role,
        ) == QApplication.palette().color(role)
        assert dialog.instruments.palette().color(role).name() == "#1b1e23"
    finally:
        theme.apply_theme("system")


def test_clicking_the_current_theme_does_not_apply_it_again(
    dialog: AppSettingsDialog,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that the current theme stays selected without an unnecessary
    palette update or window rebuild.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    monkeypatch : pytest.MonkeyPatch
        Records theme applications.
    """
    applied = []
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(app_settings, "apply_theme", applied.append)
    dialog.thumb("dark").click()
    assert (
        applied == []
        and not dialog.theme_changed
        and dialog.thumb("dark").isChecked()
    )


@pytest.mark.parametrize("enabled", [False, True])
def test_applying_theme_protects_qt_from_collection_and_restores(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    enabled: bool,
) -> None:
    """
    Check that Qt is restyled without cyclic collection and that a
    caller's disabled collector stays disabled.

    Parameters
    ----------
    app : QApplication
        The application whose stylesheet changes.
    monkeypatch : pytest.MonkeyPatch
        Records collection state while Qt changes the stylesheet.
    enabled : bool
        Whether collection is enabled before changing the theme.
    """
    before = gc.isenabled()
    states = []
    original = app.setStyleSheet

    def restyle(sheet: str) -> None:
        """
        Observe collection state during the real stylesheet update.

        Parameters
        ----------
        sheet : str
            The new stylesheet.
        """
        states.append(gc.isenabled())
        original(sheet)

    monkeypatch.setattr(app, "setStyleSheet", restyle)
    try:
        if enabled:
            gc.enable()
        else:
            gc.disable()
        theme.apply_theme("studio")
        assert states and not any(states)
        assert gc.isenabled() == enabled
    finally:
        theme.apply_theme("system")
        if before:
            gc.enable()
        else:
            gc.disable()


def test_a_palette_change_restyles_the_segmented_control(
    dialog: AppSettingsDialog,
) -> None:
    """
    Check that a palette change restyles the segmented control.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    before = dialog.categories.currentRow()
    QApplication.sendEvent(dialog, QEvent(QEvent.Type.PaletteChange))
    assert (
        dialog.categories.currentRow() == before
    )  # same palette, same style: redrawn without error


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
        Replaces settings, functions or attributes for the length of the
        test.
    """
    applied = []
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(app_settings, "apply_theme", applied.append)
    assert not dialog.theme_changed
    dialog.thumb("light").click()
    assert (
        theme.saved_theme() == "light"
        and applied == ["light"]
        and dialog.theme_changed
    )


def test_each_keyboard_style_card_and_classic_one_chosen_by(
    dialog: AppSettingsDialog,
) -> None:
    """
    Check that each keyboard style has a card and the classic one is
    chosen by default.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    dialog.categories.setCurrentRow(3)
    assert list(dialog.keyboard_cards) == [
        *(s.key for s in keyboard_styles.STYLES),
        "custom",
    ]
    assert [k for k, c in dialog.keyboard_cards.items() if c.isChecked()] == [
        "classic",
    ]
    dialog.categories.setCurrentRow(3)
    assert dialog.appearance_pages.currentIndex() == 2
    for card in dialog.keyboard_cards.values():
        pix = QPixmap(card.size())
        card.render(pix)
        assert not pix.isNull()


def test_clicking_a_keyboard_card_applies_the_style(
    dialog: AppSettingsDialog,
) -> None:
    """
    Check that clicking a keyboard card applies the style.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    dialog.categories.setCurrentRow(3)
    dialog.keyboard_cards["harpsichord-french"].click()
    assert keyboard_styles.current().key == "harpsichord-french"


def test_the_builder_colors_each_part_and_selects_the_custom_style(
    dialog: AppSettingsDialog,
) -> None:
    """
    Check that the builder colors each part and selects the custom
    style.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    dialog.categories.setCurrentRow(3)
    dialog.builder._set("naturals", color="#ead9aa")  # boxwood
    assert (
        keyboard_styles.current().key == "custom"
        and keyboard_styles.custom_colors()["naturals"] == "#ead9aa"
    )
    assert dialog.keyboard_cards["custom"].isChecked()
    assert (
        dialog.keyboard_cards["custom"].keys.style_override.white[0]
        == "#ead9aa"
    )  # the card previews it
    dialog.builder._set("felt", color="#7d1f27")
    dialog.builder._set("felt", color=None)  # an optional part can be left out
    assert (
        keyboard_styles.custom_colors()["felt"] is None
        and keyboard_styles.current().felt is None
    )
    assert dialog.builder.swatches["felt"].text() == "none"


def test_the_builder_has_a_chip_for_every_material_and_none_for_optional_parts(
    dialog: AppSettingsDialog,
) -> None:
    """
    Check that the builder has a chip for every material and none for
    optional parts.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    dialog.categories.setCurrentRow(3)
    chips = dialog.builder.findChildren(QToolButton)
    required = sum(
        1 for _, _, optional in keyboard_styles.COMPONENTS if not optional
    )
    optional = len(keyboard_styles.COMPONENTS) - required
    assert (
        len(chips)
        == len(keyboard_styles.COMPONENTS) * len(keyboard_styles.MATERIALS)
        + optional
    )
    next(c for c in chips if c.toolTip().startswith("Ebony  ")).click()
    assert keyboard_styles.current().key == "custom"


def test_the_builder_opens_the_color_picker_and_keeps_a_chosen_color(
    dialog: AppSettingsDialog,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that the builder opens the color picker and keeps a chosen
    color.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the
        test.
    """
    dialog.categories.setCurrentRow(3)
    picked = iter([QColor("#336699"), QColor()])  # then the dialog is canceled
    monkeypatch.setattr(
        app_settings.QColorDialog,
        "getColor",
        lambda *a, **k: next(picked),
    )
    dialog.builder.swatches["case"].click()
    assert keyboard_styles.custom_colors()["case"] == "#336699"
    dialog.builder.swatches["case"].click()
    assert (
        keyboard_styles.custom_colors()["case"] == "#336699"
    )  # canceled: unchanged


def test_a_theme_with_colors_of_its_own_sets_the_palette_and_gives_it_back(
    app: QApplication,
) -> None:
    """
    Check that Studio sets the application's palette, that Studio Night
    is dark, and that going back to System lets go of it.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    window = QPalette.ColorRole.Window
    try:
        theme.apply_theme("studio")
        assert QApplication.palette().color(window).name() == "#eceef1"
        assert (
            QApplication.palette().color(QPalette.ColorRole.Highlight).name()
            == "#2f7fc1"
        )
        theme.apply_theme("studio_dark")
        assert QApplication.palette().color(window).name() == "#1b1e23"
        assert (
            QApplication.palette()
            .color(QPalette.ColorRole.WindowText)
            .lightness()
            > 200
        )  # light text on the dark window
        theme.apply_theme("system")
        assert QApplication.palette().color(window).name() not in {
            "#eceef1",
            "#1b1e23",
        }
    finally:
        theme.apply_theme("system")


def test_theme_list_on_left_and_card_of_chosen_row_on_right(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check the Theme section: the list on the left, the card on the
    right, and that the version last chosen is kept down the list.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the
        test.
    """
    applied: list[str] = []
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(app_settings, "apply_theme", applied.append)
    theme.save_theme("system")
    dialog = AppSettingsDialog()
    dialog.categories.setCurrentRow(1)
    dialog.resize(1100, 700)
    dialog.show()
    try:
        listing, pages = dialog.theme_list, dialog.theme_pages
        assert (
            listing.mapTo(dialog, listing.rect().topLeft()).x()
            < pages.mapTo(dialog, pages.rect().topLeft()).x()
        )
        # two section labels and the row that makes a new theme, as well
        # as a row for each theme
        assert listing.count() == len(theme.FAMILIES) + 3 and all(
            len(dialog.card(family).thumbs) == 3
            for family in dialog.theme_items
        )
        assert dialog.new_theme_item.text().endswith("New theme…")
        tops = [
            thumb.mapTo(dialog, thumb.rect().topLeft()).y()
            for thumb in dialog.card("default").thumbs.values()
        ]
        assert (
            tops == sorted(tops) and len(set(tops)) == 3
        )  # the three pictures are one above another
        assert (
            pages.currentWidget() is dialog.card_page("default")
            and dialog.thumb("system").isChecked()
        )
        # choosing a row shows its card and uses the theme, in the
        # version last chosen: System, to begin with
        listing.setCurrentItem(dialog.theme_items["sage"])
        assert pages.currentWidget() is dialog.card_page("sage")
        assert (
            theme.saved_theme() == "sage_auto"
            and applied == ["sage_auto"]
            and dialog.thumb("sage_auto").isChecked()
        )
        assert (
            dialog.theme_items["sage"].font().bold()
            and not dialog.theme_items["default"].font().bold()
        )
        dialog.thumb(
            "sage_dark",
        ).click()  # a click chooses a version, which is then kept
        assert (
            theme.saved_theme() == "sage_dark"
            and not dialog.thumb("sage_auto").isChecked()
        )
        listing.setCurrentItem(dialog.theme_items["pine"])
        assert (
            theme.saved_theme() == "pine_dark"
            and applied[-1] == "pine_dark"
            and dialog.thumb("pine_dark").isChecked()
        )
        dialog.thumb(
            "pine",
        ).click()  # now the light version is the one that is kept
        listing.setCurrentItem(dialog.theme_items["default"])
        assert (
            theme.saved_theme() == "light"
            and dialog.thumb("light").isChecked()
        )
        dialog.thumb("dark").click()
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
    Check that the list opens on the row of the theme in use, with that
    version marked on its card.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the
        test.
    """
    monkeypatch.setattr(theme, "system_is_dark", lambda: False)
    theme.save_theme("pine_dark")
    try:
        dialog = AppSettingsDialog()
        dialog.categories.setCurrentRow(1)
        assert dialog.theme_list.currentItem() is dialog.theme_items["pine"]
        assert dialog.theme_pages.currentWidget() is dialog.card_page("pine")
        assert dialog.thumb("pine_dark").isChecked()
    finally:
        theme.save_theme("system")


def test_a_system_version_of_a_theme_is_light_or_dark_as_the_desktop_is(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that the System version of a theme uses its light colors on a
    light desktop and its dark colors on a dark one.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the
        test.
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
        # the desktop changing makes a theme that follows it apply again
        theme._desktop_changed()
        monkeypatch.setattr(theme, "system_is_dark", lambda: False)
        theme._desktop_changed()
        assert QApplication.palette().color(window).name() == light.window
    finally:
        theme.save_theme("system")
        theme.apply_theme("system")


def test_the_themes_are_made_from_their_seeds_in_a_light_and_a_dark_version(
    app: QApplication,
) -> None:
    """
    Check the generated themes: a pair each, unique keys, dark ones
    dark, and the colors the preview page showed.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    keys = [custom.key for custom in theme.CUSTOM_THEMES]
    assert len(set(keys)) == len(keys) == 2 * (len(theme.SEEDS) + 1)
    for custom in theme.CUSTOM_THEMES:
        assert custom.dark == custom.key.endswith("_dark")
        assert (
            QColor(custom.window).lightness() < QColor(custom.ink).lightness()
            if custom.dark
            else True
        )
        assert (
            QColor(custom.window).lightness() > QColor(custom.ink).lightness()
            if not custom.dark
            else True
        )
    parchment = theme.custom_theme("parchment")
    assert parchment is not None and (
        parchment.window,
        parchment.accent,
        parchment.ink,
    ) == ("#f3f1ec", "#ae4329", "#2e2719")
    assert (
        theme.family_of("sage_dark") == ("sage", "dark")
        and theme.variant_key("sage", version="dark") == "sage_dark"
    )
    assert (
        theme.family_of("sage_auto") == ("sage", "system")
        and theme.variant_key("default", version="system") == "system"
    )


def test_the_card_writes_out_the_window_accent_and_ink_colors_of_each_version(
    app: QApplication,
) -> None:
    """
    Check that the Light and Dark rows of a card say the window, accent
    and ink colors in hexadecimal, and the others do not.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    card = ThemeCard("parchment")
    texts = [label.text() for label in card.findChildren(QLabel)]
    light, dark = (
        theme.custom_theme("parchment"),
        theme.custom_theme("parchment_dark"),
    )
    assert light is not None and dark is not None
    assert (
        f"window {light.window}   accent {light.accent}   ink {light.ink}"
        in texts
    )
    assert (
        f"window {dark.window}   accent {dark.accent}   ink {dark.ink}"
        in texts
    )
    assert (
        sum(text.startswith("window #") for text in texts) == 2
    )  # not for System, which is both
    assert not any(
        text.startswith("window #")
        for text in [
            label.text() for label in ThemeCard("default").findChildren(QLabel)
        ]
    )


def test_the_squares_of_a_theme_are_beside_its_pictures_and_not_at_the_bottom(
    app: QApplication,
) -> None:
    """
    Check that the Light and Dark rows of a card have the squares of
    their colors.

    "Always light" and "Always dark" are gone from a theme that has its
    own colors.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    card = ThemeCard("sage")
    card.show()
    squares = [
        frame
        for frame in card.findChildren(QFrame)
        if frame.width() == 18 and frame.height() == 18
    ]
    assert (
        len(squares) == 14
    )  # seven for the light version, seven for the dark
    light, dark = card.thumbs["sage"], card.thumbs["sage_dark"]
    light_top, dark_top = (
        light.mapTo(card, light.rect().topLeft()).y(),
        dark.mapTo(card, dark.rect().topLeft()).y(),
    )
    for frame in squares[:7]:  # level with the Light picture
        assert (
            light_top
            <= frame.mapTo(card, frame.rect().center()).y()
            <= light_top + light.height()
        )
    for frame in squares[7:]:  # level with the Dark picture
        assert (
            dark_top
            <= frame.mapTo(card, frame.rect().center()).y()
            <= dark_top + dark.height()
        )
    texts = [label.text() for label in card.findChildren(QLabel)]
    assert (
        "Always light." not in texts
        and "Always dark." not in texts
        and "Light or dark as the desktop is." in texts
    )
    plain = [
        label.text() for label in ThemeCard("default").findChildren(QLabel)
    ]
    assert (
        "Always light." in plain and "Always dark." in plain
    )  # the desktop's own colors have no squares to show


@pytest.fixture
def no_user_themes() -> Iterator[None]:
    """
    Start a test with no themes of the user's own saved, and leave none
    behind.

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
    Check that the row that makes a new theme opens the editor, that a
    theme made there is saved, appears in the list and is used.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    no_user_themes : None
        Clears the themes of the user's own.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the
        test.
    """
    dialog = AppSettingsDialog()
    dialog.categories.setCurrentRow(1)
    dialog.resize(1100, 700)
    dialog.show()
    editor = dialog.theme_editor
    dialog.theme_list.setCurrentItem(dialog.new_theme_item)
    assert (
        dialog.theme_pages.currentWidget() is editor
        and theme.saved_theme() == "system"
    )  # nothing is used while it is made
    editor.name_edit.setText("Harbor Lights")
    editor.colors["light"]["accent"] = "#ff00aa"
    sage_row = editor.start_from.findData("sage")
    editor.start_from.setCurrentIndex(sage_row)
    editor.start_from.activated.emit(
        sage_row,
    )  # choosing a theme in the list takes its colors, with no button to press
    editor.colors["dark"]["accent"] = "#00ffcc"
    editor.save_button.click()
    records = theme.user_records()
    assert len(records) == 1 and records[0]["name"] == "Harbor Lights"
    sage = theme.custom_theme("sage")
    assert (
        sage is not None
        and records[0]["dark"]["accent"] == "#00ffcc"
        and records[0]["light"]["window"] == sage.window
    )
    family = records[0]["id"]
    assert (
        family.startswith("my_")
        and family in dialog.theme_items
        and family in dialog.theme_cards
    )
    assert (
        dialog.theme_list.item(0).text() == "MY THEMES"
        and dialog.theme_items[family].text() == "Harbor Lights"
    )
    assert dialog.theme_pages.currentWidget() is dialog.card_page(family)
    assert (
        theme.saved_theme() == f"{family}_auto"
    )  # in the version that was last chosen: System
    assert (
        theme.custom_theme(f"{family}_dark") is not None
        and theme.scheme_of(f"{family}_dark") == Qt.ColorScheme.Dark
    )
    dialog.thumb(f"{family}_dark").click()
    assert (
        QApplication.palette().color(QPalette.ColorRole.Highlight).name()
        == "#00ffcc"
    )
    dialog.close()
    again = AppSettingsDialog()  # and it is still there the next time
    again.categories.setCurrentRow(1)
    assert (
        theme.family_of(theme.saved_theme()) == (family, "dark")
        and family in again.theme_items
    )
    assert again.theme_list.currentItem() is again.theme_items[family]


def test_a_theme_that_was_made_can_be_changed_and_deleted(
    app: QApplication,
    no_user_themes: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that a theme of the user's own has a Change colors button, and
    that the color picker changes a color.

    Deleting a theme asks first, and goes back to the desktop's colors
    if it was in use.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    no_user_themes : None
        Clears the themes of the user's own.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the
        test.
    """
    colors = {part: "#112233" for part in theme.PARTS}
    theme.upsert_user_theme(
        theme.ThemeRecord(
            id="my_test",
            name="Mine",
            light=dict(colors),
            dark=dict(colors),
        ),
    )
    dialog = AppSettingsDialog()
    dialog.categories.setCurrentRow(1)
    dialog.show()
    assert (
        theme.custom_theme("my_test") is not None
        and dialog.card("my_test").change_button is not None
    )
    assert (
        dialog.card("sage").change_button is None
    )  # only a theme of the user's own can be changed
    dialog.theme_list.setCurrentItem(dialog.theme_items["my_test"])
    change = dialog.card("my_test").change_button
    assert change is not None
    change.click()
    editor = dialog.theme_editor
    assert (
        dialog.theme_pages.currentWidget() is editor
        and editor.name_edit.text() == "Mine"
        and not editor.delete_button.isHidden()
    )
    monkeypatch.setattr(
        theme_editor.QColorDialog,
        "getColor",
        lambda *args, **kwargs: QColor("#abcdef"),
    )
    editor.buttons["light"][
        "accent"
    ].click()  # the picker answers with a color
    assert editor.colors["light"]["accent"] == "#abcdef"
    editor.name_edit.setText("Mine, changed")
    editor.save_button.click()
    assert [
        (r["name"], r["light"]["accent"]) for r in theme.user_records()
    ] == [("Mine, changed", "#abcdef")]
    # asked first, and "No" keeps it
    monkeypatch.setattr(
        app_settings.QMessageBox,
        "question",
        lambda *args, **kwargs: app_settings.QMessageBox.StandardButton.No,
    )
    change.click()
    editor.delete_button.click()
    assert len(theme.user_records()) == 1
    monkeypatch.setattr(
        app_settings.QMessageBox,
        "question",
        lambda *args, **kwargs: app_settings.QMessageBox.StandardButton.Yes,
    )
    assert theme.family_of(theme.saved_theme())[0] == "my_test"
    editor.delete_button.click()
    assert theme.user_records() == [] and "my_test" not in dialog.theme_items
    assert (
        theme.saved_theme() == "system"
    )  # it was in use, so the desktop's own colors are back
    dialog.close()


def test_a_saved_theme_that_cannot_be_read_is_left_out(
    app: QApplication,
    no_user_themes: None,
) -> None:
    """
    Check that damaged saved themes give nothing, and that a good one
    beside a bad one is kept.

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
    damaged = [
        3,
        {"id": "my_x"},
        {"id": "other", "name": "No", "light": {}, "dark": {}},
        kept,
    ]
    theme.store().setValue("ui/userThemes", json.dumps(damaged))
    assert [record["id"] for record in theme.user_records()] == ["my_ok"]
    assert [item.key for item in theme.user_themes()] == [
        "my_ok",
        "my_ok_dark",
    ]
    assert (
        theme.saved_theme() == "system"
    )  # nothing that is saved can make this a theme that does not exist


def test_editors_buttons_stay_in_view_at_top_and_fields_take(
    app: QApplication,
    no_user_themes: None,
) -> None:
    """
    Check that Save and Cancel are above the form, so that scrolling the
    form does not take them away.

    The name and the "Start from" box are marked for the rounded style
    of the app.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    no_user_themes : None
        Clears the themes of the user's own.
    """
    theme.apply_theme("system")
    dialog = AppSettingsDialog()
    dialog.categories.setCurrentRow(1)
    dialog.resize(1000, 480)  # short, so that the form has to scroll
    dialog.show()
    dialog.theme_list.setCurrentItem(dialog.new_theme_item)
    editor = dialog.theme_editor
    scroll = editor.findChild(QScrollArea)
    assert (
        scroll is not None and scroll.verticalScrollBar().maximum() > 0
    )  # the form is taller than the room it has
    save_top = editor.save_button.mapTo(
        editor,
        editor.save_button.rect().topLeft(),
    ).y()
    assert (
        save_top < scroll.mapTo(editor, scroll.rect().topLeft()).y()
    )  # above the form, not inside it
    scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())
    assert (
        editor.save_button.isVisible()
        and editor.save_button.mapTo(
            editor,
            editor.save_button.rect().topLeft(),
        ).y()
        == save_top
    )
    assert editor.save_button.property("primary") is True
    assert (
        editor.name_edit.property("field") is True
        and editor.start_from.property("field") is True
    )
    sheet = QApplication.instance().styleSheet()  # type: ignore[union-attr]
    assert (
        'QLineEdit[field="true"]' in sheet
        and 'QComboBox[field="true"]' in sheet
        and 'QPushButton[primary="true"]' in sheet
    )
    dialog.close()


def test_choosing_in_start_from_takes_colors_at_once_and_there(
    app: QApplication,
    no_user_themes: None,
) -> None:
    """
    Check that picking a theme in "Start from" changes the colors right
    away, and that the button that did it is gone.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    no_user_themes : None
        Clears the themes of the user's own.
    """
    editor = ThemeEditor()
    assert "Copy its colors" not in [
        button.text() for button in editor.findChildren(QPushButton)
    ]
    studio, pine = (
        theme.custom_theme("studio"),
        theme.custom_theme("pine_dark"),
    )
    assert studio is not None and pine is not None
    assert (
        editor.colors["light"]["window"] == studio.window
    )  # a new theme starts as Studio
    row = editor.start_from.findData("pine")
    editor.start_from.setCurrentIndex(row)
    editor.start_from.activated.emit(row)
    assert (
        editor.colors["dark"]["window"] == pine.window
        and editor.pictures["dark"].colors["window"] == pine.window
    )
    editor.load(
        theme.ThemeRecord(
            id="my_x",
            name="X",
            light=dict(editor.colors["light"]),
            dark=dict(editor.colors["dark"]),
        ),
    )
    offered = [
        editor.start_from.itemData(row)
        for row in range(editor.start_from.count())
    ]
    assert (
        editor.start_from.currentData() is None and "my_x" not in offered
    )  # it does not offer itself
    editor.start_from.activated.emit(
        0,
    )  # the line that asks for a choice takes nothing
    assert editor.colors["dark"]["window"] == pine.window
    editor.show()
    name_left = editor.name_edit.mapTo(
        editor,
        editor.name_edit.rect().topLeft(),
    ).x()
    assert (
        name_left
        == editor.start_from.mapTo(
            editor,
            editor.start_from.rect().topLeft(),
        ).x()
    )  # the fields line up


def test_the_editors_color_buttons_light_up_on_hover_and_show_a_hand(
    app: QApplication,
    no_user_themes: None,
) -> None:
    """
    Check that every color button has a hover ring that shows on its
    color, a pointing hand, and a tooltip that says to click.

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
            ring = (
                "#ffffff"
                if QColor(editor.colors[version][part]).lightness() < 140
                else "#1a1a1a"
            )
            assert (
                f"QPushButton:hover {{ border: 3px solid {ring}; }}"
                in button.styleSheet()
            )  # a ring that shows on its color
            assert button.cursor().shape() == Qt.CursorShape.PointingHandCursor
            assert button.toolTip().startswith("Click to change")
    first = editor.buttons["light"]["window"]
    assert (
        editor.colors["light"]["window"] in first.styleSheet()
    )  # and it still shows its own color


def test_the_code_beside_a_color_lights_up_with_the_color(
    app: QApplication,
    no_user_themes: None,
) -> None:
    """
    Check that pointing at a color button makes the hex code beside it
    bold and dark, and that leaving puts it back.

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
    button, code = (
        editor.buttons["dark"]["accent"],
        editor._values["dark"]["accent"],
    )
    other = editor._values["light"]["accent"]
    assert "bold" not in code.styleSheet()
    # Ensure a real enter event even if an earlier test left the pointer
    # at this screen position.
    QTest.mouseMove(editor, QPoint(1, 1))
    app.processEvents()
    QTest.mouseMove(button, button.rect().center())
    QTest.qWait(50)
    assert "bold" in code.styleSheet() and "palette(text)" in code.styleSheet()
    assert "bold" not in other.styleSheet()  # only the one that is pointed at
    QApplication.sendEvent(
        button,
        QEvent(QEvent.Type.Leave),
    )  # the pointer goes away
    assert "bold" not in code.styleSheet()
    editor.close()


def test_updates_page_shows_version_and_remembers_whether_to(
    dialog: AppSettingsDialog,
) -> None:
    """
    Check that Settings has an Updates page that names the running
    version, follows releases by default, and saves the choice.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    """
    names = [
        dialog.categories.item(row).text()
        for row in range(dialog.categories.count())
    ]
    assert names == [
        "",
        "\u2003Theme",
        "\u2003Notation style",
        "\u2003Keyboard style",
        "\u2003Transitions",
        "",
        "\u2003Instruments",
        "\u2003Metronome",
        "Updates",
    ]
    dialog.categories.setCurrentRow(names.index("Updates"))
    page = dialog.pages.currentWidget()
    assert page is not None
    texts = [label.text() for label in page.findChildren(QLabel)]
    assert f"You have Alto {updates.installed_version()}." in texts
    assert any(
        "a packaged copy always follows releases" in text for text in texts
    )
    assert dialog.auto_updates.isChecked()
    dialog.auto_updates.click()
    assert not store().value("updates/automatic", True, type=bool)
    assert (
        not dialog.main_channel.isChecked() and saved_channel() == "releases"
    )
    dialog.main_channel.click()
    assert saved_channel() == "main"
    dialog.main_channel.click()
    assert saved_channel() == "releases"


def test_a_dialog_opens_with_the_main_branch_ticked_if_that_was_chosen(
    dialog: AppSettingsDialog,
) -> None:
    """
    Check that the box shows what was saved when the dialog is opened
    again.

    Parameters
    ----------
    dialog : AppSettingsDialog
        A dialog, which makes sure the settings are isolated from the
        real ones.
    """
    save_channel("main")
    following = AppSettingsDialog()
    following.categories.setCurrentRow(1)
    following.categories.setCurrentRow(8)
    assert following.main_channel.isChecked()
    save_channel("releases")
    releases = AppSettingsDialog()
    releases.categories.setCurrentRow(1)
    releases.categories.setCurrentRow(8)
    assert not releases.main_channel.isChecked()
    assert dialog is not None


def test_collapsing_appearance_selects_the_parent(
    dialog: AppSettingsDialog,
) -> None:
    """
    Keep the selection visible when hiding the appearance subpages.

    Parameters
    ----------
    dialog : AppSettingsDialog
        Settings with an appearance subpage selected.
    """
    parent = dialog.categories.item(0)
    child = dialog.categories.item(1)
    assert parent is not None and child is not None
    dialog.categories.setCurrentItem(child)
    dialog.appearance_toggle.click()
    assert child.isHidden() and dialog.categories.currentItem() == parent
    dialog.appearance_toggle.click()
    assert not child.isHidden()


def test_metronome_choices_preview_save_and_restore(
    dialog: AppSettingsDialog,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Browse and preview clicks independently of the saved choice.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The dialog under test.
    monkeypatch : pytest.MonkeyPatch
        Isolates the player and records explicit previews.
    """
    player = app_settings.sounds
    monkeypatch.setattr(player, "metronome_click", "high-pip")
    preview = Mock()
    monkeypatch.setattr(player, "preview_metronome", preview)
    dialog.categories.setCurrentRow(5)
    dialog.sound_toggle.click()
    summary = dialog.sound_pages.currentWidget()
    assert summary is not None
    link = next(
        button
        for button in summary.findChildren(QPushButton)
        if button.accessibleName() == "Metronome"
    )
    link.click()
    assert dialog.sound_toggle.isChecked()
    assert not dialog.findChildren(app_settings.InstrumentPicker)
    page = dialog.sound_pages.currentWidget()
    assert page is not None
    picker = page.findChild(app_settings._MetronomePicker)
    assert picker is not None
    assert picker.key == "high-pip"
    assert not picker.use.isEnabled()
    preview.assert_not_called()
    for row, (key, (label, _)) in enumerate(
        app_settings.METRONOME_CLICKS.items(),
    ):
        picker.list.setCurrentRow(row)
        assert picker.title.text() == label
        assert picker.description.text()
        assert picker.list.item(0).font().bold()
        picker.preview.click()
        preview.assert_called_with(key)
        assert player.metronome_click == "high-pip"
    assert preview.call_count == 3
    assert picker.use.isEnabled()
    picker.use.click()
    assert not picker.use.isEnabled()
    assert picker.list.item(2).font().bold()
    assert not picker.list.item(0).font().bold()
    assert store().value("audio/metronomeClick") == "pencil-click"
    picker.list.setCurrentRow(1)
    picker.list.itemDoubleClicked.emit(picker.list.currentItem())
    assert store().value("audio/metronomeClick") == "low-pip"
    player.metronome_click = "high-pip"
    app_settings.load_metronome_click()
    assert player.metronome_click == "low-pip"
    dialog.sound_toggle.click()
    assert dialog.sound_pages.currentWidget() is summary
    store().setValue("audio/metronomeClick", "unknown")
    app_settings.load_metronome_click()
    assert player.metronome_click == "high-pip"


def test_metronome_curve_rises_on_each_click_and_clears_on_stop(
    dialog: AppSettingsDialog,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check loading, the attack and fall of each beat, and interruption.

    Parameters
    ----------
    dialog : AppSettingsDialog
        The settings dialog containing the spectrum display.
    monkeypatch : pytest.MonkeyPatch
        Simulates the audio backend's loading and playback events.
    """
    player = audio.Sounds()
    monkeypatch.setattr(app_settings, "sounds", player)
    status = audio.QSoundEffect.Status
    factory = Mock(Status=status)
    monkeypatch.setattr(audio, "QSoundEffect", factory)
    effect = factory.return_value
    dialog.categories.setCurrentRow(7)
    dialog.show()
    picker = dialog.findChild(app_settings._MetronomePicker)
    assert picker is not None
    curve = picker.spectrum
    idle = curve.grab().toImage()
    picker.preview.click()
    playing_changed = effect.playingChanged.connect.call_args.args[0]
    status_changed = effect.statusChanged.connect.call_args.args[0]
    effect.isPlaying.return_value = True
    effect.status.return_value = status.Loading
    playing_changed()
    assert curve.grab().toImage() == idle
    effect.status.return_value = status.Ready
    status_changed()
    assert curve.animation.state() == curve.animation.State.Running
    strike = curve.grab().toImage()
    assert strike != idle
    for beat in (0, 500, 1000):
        curve.animation.setCurrentTime(beat)
        assert curve.grab().toImage() == strike
        curve.animation.setCurrentTime(beat + 100)
        falling = curve.grab().toImage()
        assert falling != idle and falling != strike
        curve.animation.setCurrentTime(beat + 350)
        assert curve.grab().toImage() == idle
    curve.animation.setCurrentTime(1500)
    assert curve.grab().toImage() == strike
    curve.animation.setCurrentTime(1542)
    effect.isPlaying.return_value = False
    playing_changed()
    curve.animation.setCurrentTime(1600)
    assert curve.grab().toImage() == falling
    picker.list.setCurrentRow(2)
    assert curve.grab().toImage() == idle
    effect.isPlaying.return_value = True
    playing_changed()
    assert curve.animation.currentTime() == 0
    assert curve.grab().toImage() != strike
    curve.animation.setCurrentTime(20)
    effect.isPlaying.return_value = False
    playing_changed()
    assert curve.grab().toImage() == idle
    dialog.hide()
    effect.stop.assert_called()


def test_spectrum_stays_idle_without_audio(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Keep the preview usable if the selected click cannot be read.

    Parameters
    ----------
    app : QApplication
        The shared application.
    monkeypatch : pytest.MonkeyPatch
        Simulates a missing preview file.
    """
    monkeypatch.setattr(
        metronome_spectrum,
        "_spectrum",
        Mock(side_effect=OSError),
    )
    curve = metronome_spectrum.MetronomeSpectrum()
    curve.set_sound("low-pip")
    curve.resize(8, curve.height())
    curve.show()
    curve.set_playing(True)
    assert curve.animation.state() == curve.animation.State.Stopped
    assert not curve.grab().isNull()
    curve.close()
