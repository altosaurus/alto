"""
Application-wide stylesheet: rounded corners on buttons, panes, lists and scroll bars.

Colors come from the palette so it follows the system light/dark theme.

Examples
--------
>>> RADIUS
10
"""

from pathlib import Path

from PySide6.QtGui import QColor, QPalette

from alto.ui.colors import blend_name

RADIUS = 10


def _button_colors(palette: QPalette) -> dict[str, str]:
    """
    Mix the outline, hover, pressed, and disabled colors for rounded hairline buttons.

    Parameters
    ----------
    palette : QPalette
        Colors of the surface hosting the button.

    Returns
    -------
    dict of str to str
        Hex colors for the button stylesheet.

    Examples
    --------
    >>> _button_colors(QPalette())["button_border"].startswith("#")
    True
    """
    base, text = palette.base().color(), palette.text().color()
    accent = palette.highlight().color()
    return {
        "button_border": blend_name(base, b=text, t=0.31),
        "button_hover": blend_name(base, b=accent, t=0.25),
        "button_pressed_border": blend_name(text, b=accent, t=0.35),
        "button_disabled_text": blend_name(palette.window().color(), b=text, t=0.44),
    }


def app_style(palette: QPalette, *, paper_palette: QPalette | None = None) -> str:
    """
    Build the stylesheet for a palette.

    Push buttons use rounded hairline borders. In dark mode, exercise tiles have near-black outlines and
    other standard buttons have graphite-gray outlines.

    Parameters
    ----------
    palette : QPalette
        The palette to take colors from, so the style follows the light or dark theme.
    paper_palette : QPalette or None, default None
        The theme's light variant for playback on white staff paper. Dark desktop themes use Qt light colors
        with the desktop accent when no light variant is supplied.

    Returns
    -------
    str
        Qt style sheet text.

    Examples
    --------
    >>> from PySide6.QtWidgets import QApplication
    >>> sheet = app_style(QApplication.palette())
    >>> "QPushButton" in sheet and "border-radius" in sheet
    True
    """
    base, dark, midlight = (
        palette.color(r).name() for r in (QPalette.ColorRole.Base, QPalette.ColorRole.Dark, QPalette.ColorRole.Midlight)
    )
    base_c, text_c, accent_c = (
        palette.color(QPalette.ColorRole.Base),
        palette.color(QPalette.ColorRole.Text),
        palette.color(QPalette.ColorRole.Highlight),
    )
    window_c = palette.color(QPalette.ColorRole.Window)
    dark_surface = base_c.lightness() < 128
    dark_hairlines = ""
    if dark_surface:
        for selector, border in (("QPushButton", QColor("#505050")), ("ExerciseCard", QColor("#181818"))):
            dark_hairlines += _DARK_HAIRLINE.format(
                button=selector,
                border=border.name(),
                active=blend_name(border, b=text_c, t=0.36),
                disabled=blend_name(window_c, b=border, t=0.40),
            )
    sheet = _TEMPLATE.format(
        RADIUS=RADIUS,
        r2=RADIUS - 2,
        r3=RADIUS - 3,
        rp=RADIUS + 2,
        dark_hairlines=dark_hairlines,
        **_button_colors(palette),
        callout_fill=blend_name(base_c, b=accent_c, t=0.12),
        callout_heading=blend_name(text_c, b=accent_c, t=0.32),
        fill=base,
        fill_hover=base,
        fill_pressed=midlight,
        menu_surface=blend_name(window_c, b=text_c, t=0.07),
        edge=dark,
        box_edge=blend_name(base_c, b=text_c, t=0.45),
        box_edge_off=blend_name(base_c, b=text_c, t=0.2),
        accent=accent_c.name(),
        accent_dim=blend_name(accent_c, b=base_c, t=0.55),
        nav_hover=blend_name(window_c, b=text_c, t=0.07),
        nav_selected=blend_name(window_c, b=accent_c, t=0.2),
        check=(Path(__file__).resolve().parent.parent / "assets" / "ui" / "check.svg").as_posix(),
        chevron=(Path(__file__).resolve().parent.parent / "assets" / "ui" / "chevron.svg").as_posix(),
    )
    if paper_palette is None:
        paper_palette = palette
        if dark_surface:
            paper_palette = QPalette(QColor("#efefef"))
            paper_palette.setColor(QPalette.ColorRole.Highlight, accent_c)
            paper_palette.setColor(QPalette.ColorRole.HighlightedText, palette.highlightedText().color())
    return sheet + _PAPER_BUTTON.format(
        button='QFrame#lessonExample[staffPaper="true"] > QPushButton#lessonPlayback',
        base=paper_palette.base().color().name(),
        ink=blend_name(paper_palette.buttonText().color(), b=paper_palette.mid().color(), t=0.32),
        accent=paper_palette.highlight().color().name(),
        on_accent=paper_palette.highlightedText().color().name(),
        window=paper_palette.window().color().name(),
        mid=paper_palette.mid().color().name(),
        **_button_colors(paper_palette),
    )


_DARK_HAIRLINE = """
{button} {{ border-color: {border}; }}
{button}:hover, {button}:focus {{ border-color: {active}; }}
{button}:pressed, {button}:checked {{ border-color: {border}; }}
{button}:disabled {{ border-color: {disabled}; }}
"""


_PAPER_BUTTON = """
{button} {{ background: {base}; color: {ink}; border-color: {button_border}; }}
{button}:hover {{ background: {button_hover}; border-color: {accent}; }}
{button}:focus {{ border-color: {accent}; }}
{button}:pressed, {button}:checked {{ background: {accent}; color: {on_accent}; border-color: {button_pressed_border}; }}
{button}:disabled {{ background: {window}; color: {button_disabled_text}; border-color: {mid}; }}
"""


_TEMPLATE = """
QPushButton {{
    border: 1px solid {button_border};
    border-radius: {RADIUS}px;
    background: palette(base);
    color: palette(button-text);
    padding: 6px 12px;
}}
QPushButton:hover {{ background: {button_hover}; border-color: palette(highlight); }}
QPushButton:focus {{ border: 2px solid palette(highlight); padding: 5px 11px; }}
QPushButton:pressed, QPushButton:checked {{
    background: {accent};
    color: palette(highlighted-text);
    border: 1px solid {button_pressed_border};
    padding: 7px 12px 5px;
}}
QPushButton:disabled {{ background: palette(window); color: {button_disabled_text}; border-color: palette(mid); }}
{dark_hairlines}

/* The main button of a form, such as Save: filled with the accent color. */
QPushButton[primary="true"] {{ background: {accent}; border-color: {accent}; color: palette(highlighted-text); font-weight: 600; }}
QPushButton[primary="true"]:hover {{ background: {accent}; border-color: palette(text); }}
QPushButton[primary="true"]:disabled {{ background: {accent_dim}; border-color: {accent_dim}; color: palette(highlighted-text); }}

/* A thin accent underline marks the active settings tab. */
QTabWidget#settingsTabs::pane {{
    top: -1px;
    border: 0;
    border-top: 1px solid palette(mid);
}}
QTabWidget#settingsTabs QTabBar::tab {{
    border: 0;
    border-bottom: 2px solid transparent;
    padding: 6px 14px;
    background: transparent;
    color: palette(text);
}}
QTabWidget#settingsTabs QTabBar::tab:hover {{ color: palette(highlight); }}
QTabWidget#settingsTabs QTabBar::tab:selected {{
    border-bottom-color: palette(highlight);
    color: palette(highlight);
}}
QTabWidget#settingsTabs QTabBar::tab:focus {{ background: {nav_hover}; }}

/* Fields have rounded corners and a heavier lower edge. */
QLineEdit[field="true"], QComboBox[field="true"] {{
    border: 1px solid {edge};
    border-bottom-width: 2px;
    border-radius: {RADIUS}px;
    background: {fill};
    padding: 5px 10px;
    selection-background-color: palette(highlight);
    selection-color: palette(highlighted-text);
}}
QComboBox[field="true"] {{ combobox-popup: 0; }}  /* the list drops down below the box, and does not cover it and what is around it */
QLineEdit[field="true"]:focus, QComboBox[field="true"]:focus, QComboBox[field="true"]:on {{ border-color: palette(highlight); }}
QComboBox[field="true"]::drop-down {{ border: none; width: 28px; }}
QComboBox[field="true"]::down-arrow {{ image: url({chevron}); width: 16px; height: 16px; }}
QFrame#dropdownPopup {{
    border: 1px solid palette(mid);
    border-radius: {RADIUS}px;
    background: palette(base);
}}
QComboBox[field="true"] QAbstractItemView {{
    border: 1px solid palette(mid);
    border-radius: {RADIUS}px;
    padding: 4px;
    background: palette(base);
    selection-background-color: palette(highlight);
    selection-color: palette(highlighted-text);
    outline: 0;
}}

/* Check boxes and radio buttons: rounded, soft-edged, and filled with the accent color when selected. */
QCheckBox, QRadioButton {{ spacing: 10px; }}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 1.5px solid {box_edge};
    background: palette(base);
}}
QCheckBox::indicator {{ border-radius: 6px; }}
QRadioButton::indicator {{ border-radius: 10px; }}
QCheckBox::indicator:hover, QRadioButton::indicator:hover {{ border-color: {accent}; }}
QCheckBox::indicator:checked {{ background: {accent}; border-color: {accent}; image: url({check}); }}
QRadioButton::indicator:checked {{
    border-color: {accent};
    background: qradialgradient(cx: .5, cy: .5, radius: .5, fx: .5, fy: .5,
                                stop: 0 #ffffff, stop: .36 #ffffff, stop: .42 {accent}, stop: 1 {accent});
}}
QCheckBox::indicator:disabled {{ border-color: {box_edge_off}; background: palette(window); border-radius: 6px; }}
QRadioButton::indicator:disabled {{ border-color: {box_edge_off}; background: palette(window); border-radius: 10px; }}
QCheckBox::indicator:checked:disabled {{ background: {accent_dim}; border-color: {accent_dim}; border-radius: 6px; image: url({check}); }}
QRadioButton::indicator:checked:disabled {{
    border-radius: 10px;
    border-color: {accent_dim};
    background: qradialgradient(cx: .5, cy: .5, radius: .5, fx: .5, fy: .5,
                                stop: 0 #ffffff, stop: .36 #ffffff, stop: .42 {accent_dim}, stop: 1 {accent_dim});
}}

QToolButton {{
    border: 1px solid transparent;
    border-radius: {r2}px;
    padding: 3px 6px;
}}
QToolButton:hover {{ background: palette(midlight); border-color: palette(mid); }}
QToolButton:pressed {{ background: palette(mid); }}
QToolButton:checked {{ background: palette(mid); }}
QToolButton:disabled {{ color: gray; }}
QToolButton[arrowButton="true"] {{
    border-color: {edge};
    border-bottom-width: 2px;
    border-radius: {RADIUS}px;
    background: {fill};
}}
QToolButton[arrowButton="true"]:hover {{ background: {fill_hover}; border-color: palette(highlight); }}
QToolButton[arrowButton="true"]:focus {{ border-color: palette(highlight); }}
QToolButton[arrowButton="true"]:pressed {{ background: {fill_pressed}; border-bottom-width: 1px; padding-top: 4px; }}
QToolButton[arrowButton="true"]:disabled {{ background: palette(window); border-color: palette(midlight); }}

QFrame#settingsPane {{
    border: 1px solid palette(mid);
    border-radius: {rp}px;
}}

/* The exercise list: flat and borderless, with soft rounded highlights instead of a hard selection bar. */
QListWidget#nav {{
    border: none;
    background: transparent;
    outline: 0;
    padding: 0px;
}}
QListWidget#nav::item {{ padding: 4px 8px; margin: 1px 6px; border-radius: {rp}px; color: palette(text); }}
QListWidget#nav::item:hover {{ background: {nav_hover}; }}
QListWidget#nav::item:selected, QListWidget#nav::item:selected:active, QListWidget#nav::item:selected:!active {{
    background: {nav_selected};
    color: {accent};
}}

/* The category list in the settings dialog: the same soft highlights as the exercise list, inside a rounded box. */
QListWidget#categories {{
    background: palette(base);
    border: 1px solid palette(mid);
    border-radius: {rp}px;
    outline: 0;
    padding: 6px 0px;
}}
QListWidget#categories::item {{ padding: 4px 8px; margin: 1px 6px; border-radius: {r2}px; color: palette(text); }}
QScrollArea#glossaryDefinition, QScrollArea#glossaryActivities {{
    background: palette(window);
    border: 1px solid palette(mid);
    border-radius: {rp}px;
}}
QScrollArea#glossaryDefinition, QScrollArea#glossaryActivities {{ padding: 6px; }}
QTextBrowser#glossaryText {{ background: palette(window); border: 0; }}
QListWidget#categories[glossaryBox="true"] {{ background: palette(window); }}
QLineEdit#glossarySearch {{ background: palette(window); }}
QListWidget#categories::item:hover {{ background: {nav_hover}; }}
QListWidget#categories::item:selected, QListWidget#categories::item:selected:active,
QListWidget#categories::item:selected:!active {{ background: {nav_selected}; color: {accent}; }}

QMenu#appMenu {{
    background: {menu_surface};
    border: 1px solid palette(mid);
    border-radius: {rp}px;
    padding: 6px;
}}
QMenu::item {{ padding: 8px 30px 8px 14px; border-radius: {r3}px; margin: 1px 0; }}
QMenu::item:selected {{ background: palette(highlight); color: palette(highlighted-text); }}
QMenu::item:disabled {{ color: gray; }}
QMenu::separator {{ height: 1px; background: palette(midlight); margin: 5px 10px; }}

QSplitter::handle {{ background: transparent; }}
QSplitter::handle:hover {{ background: palette(mid); border-radius: 2px; margin: 0 3px; }}

QFrame#lessonKnowledgeCheck {{
    background: {callout_fill};
    border: none;
    border-left: 3px solid {accent};
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
}}
QLabel#knowledgeCheckHeading {{ color: {callout_heading}; font-weight: bold; }}

QFrame#lessonExampleDivider {{ background: palette(mid); border: none; }}
QFrame#helpCard, QFrame#keyGroup, QFrame#detailPane, QFrame#lessonExample {{
    background: palette(base);
    border: 1px solid palette(mid);
    border-radius: {rp}px;
}}
/* Extend the white notation paper through the gutters and padding to the panel border. */
QFrame#lessonExample[staffPaper="true"] {{ background: white; }}

QScrollBar:vertical {{ background: transparent; width: 12px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: palette(mid); border-radius: 4px; min-height: 28px; }}
QScrollBar::handle:vertical:hover {{ background: palette(dark); }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
"""
