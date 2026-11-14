"""
The colour theme: follow the system, force light or dark, or use a theme with colours of its own.

A theme with colours of its own is a `CustomTheme`: a fixed palette that is light or dark whatever the desktop is set to.

Examples
--------
>>> [key for key, label in THEMES][:4]
['system', 'light', 'dark', 'studio']
"""

from __future__ import annotations

import gc
import json
import uuid
from dataclasses import dataclass
from typing import TypedDict

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QGuiApplication,
    QPalette,
)
from PySide6.QtWidgets import QApplication

from alto.ui.colors import blend
from alto.ui.store import (
    store,
    text_value,
)
from alto.ui.style import app_style


@dataclass(frozen=True)
class CustomTheme:
    """
    A theme with colours of its own.

    Attributes
    ----------
    key : str
        What it is saved as.
    family : str
        The key of the light version of the theme, which its dark version shares.
    label : str
        What the settings call it.
    note : str
        A short line about it, shown under its picture.
    dark : bool
        True if it is a dark theme, so that Qt draws its own parts (such as the title bar) to match.
    window : str
        The colour of the window.
    panel : str
        The colour of lists, boxes and buttons.
    ink : str
        The colour of text.
    muted : str
        The colour of quiet text.
    line : str
        The colour of outlines.
    accent : str
        The colour of what is chosen, and of links.
    track : str
        The colour of the track behind a switch or a slider, a little off the window's own.

    Examples
    --------
    >>> CUSTOM_THEMES[0].key, CUSTOM_THEMES[0].dark, len(CUSTOM_THEMES)
    ('studio', False, 50)
    """

    key: str
    family: str
    label: str
    note: str
    dark: bool
    window: str
    panel: str
    ink: str
    muted: str
    line: str
    accent: str
    track: str


SEEDS: tuple[tuple[str, str, str, float, float, float, float], ...] = (
    ("parchment", "Parchment", "Warm paper with a terracotta accent.", 40, 24, 12, 62),
    ("slate_blue", "Slate Blue", "Blue-grey, calm and serious.", 215, 14, 212, 68),
    ("sage", "Sage", "Soft greens with a leafy accent.", 100, 12, 140, 38),
    ("harbour", "Harbour", "Cool sea-greys, bright cyan accent.", 200, 18, 190, 78),
    ("lavender", "Lavender Hush", "Pale violet neutrals.", 260, 18, 265, 52),
    ("rosewater", "Rosewater", "Blush neutrals, rose accent.", 345, 22, 338, 58),
    ("marigold", "Marigold", "Buttery neutrals, golden accent.", 45, 22, 38, 88),
    ("pine", "Pine", "Deep forest, quiet green.", 150, 14, 155, 56),
    ("indigo", "Indigo Ink", "Blue-black neutrals, indigo accent.", 235, 20, 232, 62),
    ("graphite", "Graphite", "Almost colourless, a hint of steel.", 220, 4, 210, 32),
    ("terracotta", "Terracotta", "Clay neutrals, hot red-orange accent.", 20, 18, 12, 70),
    ("mint", "Mint", "Fresh mint neutrals.", 160, 16, 165, 62),
    ("sky", "Sky", "Light airy blues.", 205, 26, 205, 82),
    ("plum", "Plum", "Dusty purple-greys.", 305, 14, 300, 44),
    ("sand", "Sand", "Beach neutrals, soft brown accent.", 38, 18, 28, 52),
    ("teal", "Teal", "Blue-green throughout.", 180, 14, 176, 72),
    ("copper", "Copper", "Warm metal, burnt orange.", 30, 10, 26, 78),
    ("gold", "Charcoal and Gold", "Neutral greys, a gold accent.", 40, 6, 46, 82),
    ("cherry", "Cherry", "Rosy greys, deep cherry accent.", 355, 10, 352, 68),
    ("moss", "Moss", "Olive neutrals, moss accent.", 85, 14, 95, 48),
    ("arctic", "Arctic", "Icy neutrals, glacier blue.", 195, 12, 200, 56),
    ("dusk", "Dusk", "Purple twilight with a pink accent.", 275, 16, 330, 56),
    ("lime", "Lime Shock", "Neutral greys, one loud lime.", 120, 6, 88, 72),
    ("ember", "Ember", "Warm greys, glowing orange.", 10, 10, 24, 86),
)  # key, name, note, neutral hue, neutral saturation, accent hue, accent saturation: each becomes a light and a dark theme


def hsl_hex(
    hue: float,
    *,
    saturation: float,
    lightness: float,
) -> str:
    """
    Turn a colour given as hue, saturation and lightness into "#rrggbb".

    Parameters
    ----------
    hue : float
        The hue, in degrees.
    saturation : float
        The saturation, from 0 to 100. Keyword-only.
    lightness : float
        The lightness, from 0 to 100. Keyword-only.

    Returns
    -------
    str
        The colour in hexadecimal.

    Examples
    --------
    >>> hsl_hex(0, saturation=100, lightness=50), hsl_hex(210, saturation=0, lightness=100)
    ('#ff0000', '#ffffff')
    """
    saturation, lightness = saturation / 100.0, lightness / 100.0
    spread = saturation * min(lightness, 1.0 - lightness)

    def channel(offset: int) -> str:
        """
        Work out one colour channel.

        Parameters
        ----------
        offset : int
            0 for red, 8 for green, 4 for blue.

        Returns
        -------
        str
            Two hexadecimal digits.

        Examples
        --------
        >>> channel  # doctest: +SKIP
        """
        k = (offset + hue / 30.0) % 12.0
        value = lightness - spread * max(-1.0, min(k - 3.0, min(9.0 - k, 1.0)))
        return f"{int(255 * value + 0.5):02x}"

    return f"#{channel(0)}{channel(8)}{channel(4)}"


def seeded_themes(seed: tuple[str, str, str, float, float, float, float]) -> tuple[CustomTheme, CustomTheme]:
    """
    Make the light and the dark theme of a seed: neutrals tinted by one hue, and an accent of another.

    Parameters
    ----------
    seed : tuple
        The key, name and note, then the neutral hue and saturation and the accent hue and saturation.

    Returns
    -------
    tuple of (CustomTheme, CustomTheme)
        The light theme and the dark theme.

    Examples
    --------
    >>> pale, deep = seeded_themes(SEEDS[0])
    >>> pale.key, deep.key, pale.dark, deep.dark
    ('parchment', 'parchment_dark', False, True)
    """
    family, name, note, hue, sat, accent_hue, accent_sat = seed
    light = CustomTheme(
        key=family,
        family=family,
        label=name,
        note=note,
        dark=False,
        window=hsl_hex(hue, saturation=sat, lightness=94),
        panel=hsl_hex(hue, saturation=sat * 0.8, lightness=98),
        ink=hsl_hex(hue, saturation=min(sat * 3, 30), lightness=14),
        muted=hsl_hex(hue, saturation=sat * 1.2, lightness=42),
        line=hsl_hex(hue, saturation=sat * 1.2, lightness=80),
        accent=hsl_hex(accent_hue, saturation=accent_sat, lightness=42),
        track=hsl_hex(hue, saturation=sat, lightness=88),
    )
    dark = CustomTheme(
        key=f"{family}_dark",
        family=family,
        label=f"{name} (dark)",
        note=note,
        dark=True,
        window=hsl_hex(hue, saturation=sat * 0.9, lightness=11),
        panel=hsl_hex(hue, saturation=sat, lightness=15),
        ink=hsl_hex(hue, saturation=15, lightness=92),
        muted=hsl_hex(hue, saturation=10, lightness=66),
        line=hsl_hex(hue, saturation=sat, lightness=27),
        accent=hsl_hex(accent_hue, saturation=accent_sat, lightness=66),
        track=hsl_hex(hue, saturation=sat, lightness=18),
    )
    return light, dark


STUDIO = (
    CustomTheme(
        key="studio",
        family="studio",
        label="Studio",
        note="Cool greys with a clear blue.",
        dark=False,
        window="#eceef1",
        panel="#f7f8fa",
        ink="#1d2430",
        muted="#6a7585",
        line="#c9ced6",
        accent="#2f7fc1",
        track="#dcdfe4",
    ),
    CustomTheme(
        key="studio_dark",
        family="studio",
        label="Studio (dark)",
        note="Cool greys with a clear blue.",
        dark=True,
        window="#1b1e23",
        panel="#23272d",
        ink="#e8ebef",
        muted="#98a2b0",
        line="#434a54",
        accent="#6db3ea",
        track="#2c3037",
    ),
)
CUSTOM_THEMES: tuple[CustomTheme, ...] = (*STUDIO, *(theme for seed in SEEDS for theme in seeded_themes(seed)))
AUTO = "_auto"  # added to a theme's key for its System version, which is light or dark as the desktop is
FAMILIES: tuple[tuple[str, str, str], ...] = (
    ("default", "Default", "The desktop's own colours."),
    ("studio", "Studio", "Cool greys with a clear blue."),
    *((seed[0], seed[1], seed[2]) for seed in SEEDS),
)  # every card in the gallery of themes: the key of its family, its name and a line about it
THEMES = (
    ("system", "System"),
    ("light", "Light"),
    ("dark", "Dark"),
    *((theme.key, theme.label) for theme in CUSTOM_THEMES),
    *((f"{theme.key}{AUTO}", f"{theme.label} (system)") for theme in CUSTOM_THEMES if not theme.dark),
)
_SCHEMES = {
    "system": Qt.ColorScheme.Unknown,
    "light": Qt.ColorScheme.Light,
    "dark": Qt.ColorScheme.Dark,
    **{theme.key: Qt.ColorScheme.Dark if theme.dark else Qt.ColorScheme.Light for theme in CUSTOM_THEMES},
    **{f"{theme.key}{AUTO}": Qt.ColorScheme.Unknown for theme in CUSTOM_THEMES if not theme.dark},
}


def family_of(key: str) -> tuple[str, str]:
    """
    Split a theme's key into its family and which version of it that is.

    Parameters
    ----------
    key : str
        The key of any theme.

    Returns
    -------
    tuple of (str, str)
        The family's key and "light", "dark" or "system". "system", "light" and "dark" belong to the family "default".

    Examples
    --------
    >>> family_of("sage_dark"), family_of("sage"), family_of("sage_auto"), family_of("dark"), family_of("system")
    (('sage', 'dark'), ('sage', 'light'), ('sage', 'system'), ('default', 'dark'), ('default', 'system'))
    """
    if key in {"system", "light", "dark"}:
        return "default", key
    if key.endswith(AUTO) and custom_theme(key[: -len(AUTO)]) is not None:
        return key[: -len(AUTO)], "system"
    theme = custom_theme(key)
    return (theme.family, "dark" if theme.dark else "light") if theme is not None else ("default", "system")


def variant_key(
    family: str,
    *,
    version: str,
) -> str:
    """
    Give the key of one version of a family.

    Parameters
    ----------
    family : str
        The family's key.
    version : str
        "light", "dark" or "system". Keyword-only.

    Returns
    -------
    str
        The key.

    Examples
    --------
    >>> variant_key("sage", version="dark"), variant_key("sage", version="system"), variant_key("default", version="dark")
    ('sage_dark', 'sage_auto', 'dark')
    """
    if family == "default":
        return version
    return {"light": family, "dark": f"{family}_dark", "system": f"{family}{AUTO}"}[version]


PARTS = (
    "window",
    "panel",
    "ink",
    "muted",
    "line",
    "accent",
    "track",
)  # the colours that make up a theme, in the order they are edited
PART_NAMES = {
    "window": "Window",
    "panel": "Panels",
    "ink": "Text",
    "muted": "Quiet text",
    "line": "Outlines",
    "accent": "Accent",
    "track": "Track",
}  # what the editor calls each of them
USER_PREFIX = "my_"  # the start of the key of a theme the user made
_USER_NOTE = "A theme of your own."
_user_cache: tuple[str, tuple[CustomTheme, ...]] = (
    "",
    (),
)  # the saved text the user's themes were last read from, and what it made


class ThemeRecord(TypedDict):
    """
    A theme the user made, as it is saved: its key, its name, and the colours of its light and dark versions.

    Examples
    --------
    >>> ThemeRecord(id="my_1", name="Mine", light={}, dark={})["name"]
    'Mine'
    """

    id: str
    name: str
    light: dict[str, str]
    dark: dict[str, str]


def _record(raw: object) -> ThemeRecord | None:
    """
    Make a record from what was saved, if what was saved can be used.

    It can be if it has a key of the right kind, a name, and a valid colour for every part of both versions.

    Parameters
    ----------
    raw : object
        What was saved.

    Returns
    -------
    ThemeRecord or None
        The record, or None if what was saved cannot be used.

    Examples
    --------
    >>> grey = {part: "#112233" for part in PARTS}
    >>> made = _record({"id": "my_1", "name": "Mine", "light": grey, "dark": grey})
    >>> made is not None and made["name"]
    'Mine'
    >>> _record({"id": "x"}) is None, _record(3) is None
    (True, True)
    """
    if not isinstance(raw, dict) or not str(raw.get("id", "")).startswith(USER_PREFIX) or not isinstance(raw.get("name"), str):
        return None
    versions: dict[str, dict[str, str]] = {}
    for version in ("light", "dark"):
        colours = raw.get(version)
        if not isinstance(colours, dict) or not all(QColor(str(colours.get(part, ""))).isValid() for part in PARTS):
            return None
        versions[version] = {part: str(colours[part]) for part in PARTS}
    return ThemeRecord(id=str(raw["id"]), name=str(raw["name"]), light=versions["light"], dark=versions["dark"])


def user_records() -> list[ThemeRecord]:
    """
    Read the themes the user has made, as they are saved.

    Returns
    -------
    list of ThemeRecord
        One record for each theme: its "id", its "name", and its "light" and "dark" colours. A saved list that cannot be read, or
        has something else in it, gives only the records that can be used.

    Examples
    --------
    >>> store().remove("ui/userThemes")
    >>> user_records()
    []
    """
    raw = text_value(store(), key="ui/userThemes", default="[]")
    try:
        found = json.loads(raw)
    except ValueError:
        return []
    return [record for record in map(_record, found if isinstance(found, list) else []) if record is not None]


def save_user_records(records: list[ThemeRecord]) -> None:
    """
    Save the themes the user has made.

    Parameters
    ----------
    records : list of ThemeRecord
        The records, as `user_records` gives them.

    Examples
    --------
    >>> save_user_records([])
    >>> user_records()
    []
    """
    store().setValue("ui/userThemes", json.dumps(records))


def new_family_id() -> str:
    """
    Make the key for a new theme of the user's.

    Returns
    -------
    str
        A key that starts with "my_" and is not one that is in use.

    Examples
    --------
    >>> new_family_id().startswith("my_")
    True
    """
    used = {record["id"] for record in user_records()}
    while True:
        key = f"{USER_PREFIX}{uuid.uuid4().hex[:8]}"
        if key not in used:
            return key


def upsert_user_theme(record: ThemeRecord) -> None:
    """
    Save a theme the user made, replacing the one with the same key if there is one.

    Parameters
    ----------
    record : ThemeRecord
        The theme.

    Examples
    --------
    >>> store().remove("ui/userThemes")
    >>> colours = {part: "#112233" for part in PARTS}
    >>> upsert_user_theme(ThemeRecord(id="my_a", name="Mine", light=colours, dark=colours))
    >>> upsert_user_theme(ThemeRecord(id="my_a", name="Renamed", light=colours, dark=colours))
    >>> [(r["id"], r["name"]) for r in user_records()]
    [('my_a', 'Renamed')]
    >>> store().remove("ui/userThemes")
    """
    records = [existing for existing in user_records() if existing["id"] != record["id"]]
    ahead = [existing["id"] for existing in user_records()]
    if record["id"] in ahead:  # keep its place in the list
        records = [record if existing["id"] == record["id"] else existing for existing in user_records()]
    else:
        records.append(record)
    save_user_records(records)


def delete_user_theme(family: str) -> None:
    """
    Remove a theme the user made.

    Parameters
    ----------
    family : str
        The theme's key.

    Examples
    --------
    >>> store().remove("ui/userThemes")
    >>> colours = {part: "#112233" for part in PARTS}
    >>> upsert_user_theme(ThemeRecord(id="my_a", name="Mine", light=colours, dark=colours))
    >>> delete_user_theme("my_a")
    >>> user_records()
    []
    """
    save_user_records([record for record in user_records() if record["id"] != family])


def user_themes() -> tuple[CustomTheme, ...]:
    """
    Give the themes the user has made, light and dark versions of each.

    Returns
    -------
    tuple of CustomTheme
        The light theme and then the dark theme of each record.

    Examples
    --------
    >>> store().remove("ui/userThemes")
    >>> user_themes()
    ()
    """
    global _user_cache
    raw = text_value(store(), key="ui/userThemes", default="[]")
    if _user_cache[0] != raw:
        made = []
        for record in user_records():
            for dark in (False, True):
                colours = record["dark" if dark else "light"]
                made.append(
                    CustomTheme(
                        key=f"{record['id']}_dark" if dark else record["id"],
                        family=record["id"],
                        label=f"{record['name']} (dark)" if dark else record["name"],
                        note=_USER_NOTE,
                        dark=dark,
                        window=colours["window"],
                        panel=colours["panel"],
                        ink=colours["ink"],
                        muted=colours["muted"],
                        line=colours["line"],
                        accent=colours["accent"],
                        track=colours["track"],
                    ),
                )
        _user_cache = (raw, tuple(made))
    return _user_cache[1]


def families() -> tuple[tuple[str, str, str], ...]:
    """
    List every theme there is to choose, the user's own first.

    Returns
    -------
    tuple of tuple of (str, str, str)
        The key of each theme's family, its name and a line about it.

    Examples
    --------
    >>> store().remove("ui/userThemes")
    >>> families() == FAMILIES
    True
    """
    own = tuple((theme.family, theme.label, theme.note) for theme in user_themes() if not theme.dark)
    return *own, *FAMILIES


def custom_theme(key: str) -> CustomTheme | None:
    """
    Find a theme with colours of its own, one of the built-in ones or one the user made.

    Parameters
    ----------
    key : str
        The theme's key.

    Returns
    -------
    CustomTheme or None
        The theme, or None for "system", "light", "dark" or anything that is not one.

    Examples
    --------
    >>> custom_theme("studio_dark") is CUSTOM_THEMES[1], custom_theme("dark")
    (True, None)
    """
    return next((theme for theme in (*CUSTOM_THEMES, *user_themes()) if theme.key == key), None)


def scheme_of(key: str) -> Qt.ColorScheme | None:
    """
    Say which colour scheme a theme uses: light, dark, or the desktop's own.

    Parameters
    ----------
    key : str
        The theme's key.

    Returns
    -------
    Qt.ColorScheme or None
        The scheme; None if there is no theme with that key.

    Examples
    --------
    >>> scheme_of("dark") == Qt.ColorScheme.Dark, scheme_of("sage_auto") == Qt.ColorScheme.Unknown, scheme_of("nonsense")
    (True, True, None)
    """
    fixed = _SCHEMES.get(key)
    if fixed is not None:
        return fixed
    theme = custom_theme(key)
    if theme is not None:
        return Qt.ColorScheme.Dark if theme.dark else Qt.ColorScheme.Light
    if key.endswith(AUTO) and custom_theme(key[: -len(AUTO)]) is not None:
        return Qt.ColorScheme.Unknown
    return None


def preview_colours(theme: CustomTheme) -> dict[str, str]:
    """
    Pick the colours for the small picture of a theme in the settings.

    Parameters
    ----------
    theme : CustomTheme
        The theme.

    Returns
    -------
    dict of str to str
        The window, panel, outline, text, faint and chosen colours, and a tint for the chosen row.

    Examples
    --------
    >>> preview_colours(CUSTOM_THEMES[0])["window"], sorted(preview_colours(CUSTOM_THEMES[0]))[:3]
    ('#eceef1', ['accent', 'faint', 'ink'])
    """
    window, accent = QColor(theme.window), QColor(theme.accent)
    return {
        "window": theme.window,
        "panel": theme.panel,
        "line": theme.line,
        "ink": theme.ink,
        "faint": blend(QColor(theme.muted), b=window, t=0.4).name(),
        "accent": theme.accent,
        "tint": blend(accent, b=window, t=0.75).name(),
    }


def theme_palette(theme: CustomTheme) -> QPalette:
    """
    Build the Qt palette of a theme with colours of its own.

    Parameters
    ----------
    theme : CustomTheme
        The theme.

    Returns
    -------
    QPalette
        The palette: the window, lists and buttons, text, the chosen row and links in the theme's colours, with quiet text for
        what is switched off.

    Examples
    --------
    >>> colours = theme_palette(CUSTOM_THEMES[0])
    >>> colours.color(QPalette.ColorRole.Window).name(), colours.color(QPalette.ColorRole.Highlight).name()
    ('#eceef1', '#2f7fc1')
    """
    window, panel, ink, muted = QColor(theme.window), QColor(theme.panel), QColor(theme.ink), QColor(theme.muted)
    line, accent, track = QColor(theme.line), QColor(theme.accent), QColor(theme.track)
    on_accent = QColor("#ffffff") if accent.lightnessF() < 0.6 else QColor("#101820")
    palette = QPalette()
    roles = QPalette.ColorRole
    for role, colour in (
        (roles.Window, window),
        (roles.WindowText, ink),
        (roles.Base, panel),
        (roles.AlternateBase, track),
        (roles.Text, ink),
        (roles.Button, panel),
        (roles.ButtonText, ink),
        (roles.BrightText, QColor("#ffffff")),
        (roles.Highlight, accent),
        (roles.HighlightedText, on_accent),
        (roles.Link, accent),
        (roles.LinkVisited, accent.darker(130)),
        (roles.Mid, line),
        (roles.Midlight, blend(line, b=window, t=0.5)),
        (roles.Dark, line.darker(140)),
        (roles.Light, blend(panel, b=QColor("#ffffff"), t=0.5)),
        (roles.Shadow, QColor("#000000")),
        (roles.PlaceholderText, muted),
        (roles.ToolTipBase, panel),
        (roles.ToolTipText, ink),
    ):
        palette.setColor(role, colour)
    for role in (roles.WindowText, roles.Text, roles.ButtonText):
        palette.setColor(QPalette.ColorGroup.Disabled, role, muted)
    return palette


def saved_theme() -> str:
    """
    Return the theme the user chose.

    Returns
    -------
    str
        The key of the theme: "system", "light", "dark" or one of the themes with colours of its own; "system" if nothing valid is
        saved.

    Examples
    --------
    >>> save_theme("dark")
    >>> saved_theme()
    'dark'
    >>> save_theme("system")
    """
    key = text_value(store(), key="ui/theme", default="system")
    return key if scheme_of(key) is not None else "system"


def save_theme(key: str) -> None:
    """
    Remember the theme the user chose.

    Parameters
    ----------
    key : str
        "system", "light", "dark" or the key of a theme with colours of its own.

    Examples
    --------
    >>> save_theme("light")
    >>> saved_theme()
    'light'
    >>> save_theme("system")
    """
    store().setValue("ui/theme", key)


_applying = False  # True while a theme is being applied
_watching = False  # True once the app is listening for the desktop changing between light and dark
_custom_palette = False  # True while the application is using the palette of a theme with colours of its own
_custom_window = ""  # the window colour of that palette


def system_is_dark() -> bool:
    """
    Say whether the desktop is set to dark, as long as the app is not forcing a colour scheme of its own.

    A theme that follows the desktop does not force one, so this is what it asks.

    Returns
    -------
    bool
        True if the colour scheme in use is dark.

    Examples
    --------
    >>> system_is_dark() in {True, False}
    True
    """
    return QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark


def _watch_the_desktop() -> None:
    """
    Start listening for the desktop changing between light and dark, once, so a theme that follows it can follow it.

    Examples
    --------
    >>> _watch_the_desktop()
    """
    global _watching
    if not _watching:
        _watching = True
        QGuiApplication.styleHints().colorSchemeChanged.connect(_desktop_changed)


def _desktop_changed() -> None:
    """
    Apply the saved theme again when the desktop changes, if the theme is one that follows the desktop.

    Examples
    --------
    >>> _desktop_changed()
    """
    if saved_theme().endswith(AUTO):
        apply_theme(saved_theme())


def _has_custom_palette() -> bool:
    """
    Say whether the application is still using the palette of a theme with colours of its own.

    Returns
    -------
    bool
        True if one has been applied and not yet taken away.

    Examples
    --------
    >>> apply_theme("studio")
    >>> _has_custom_palette()
    True
    >>> apply_theme("system")
    >>> _has_custom_palette()
    False
    """
    return _custom_palette


def apply_theme(key: str) -> None:
    """
    Switch the application's colour scheme and rebuild the stylesheet from the new palette.

    Parameters
    ----------
    key : str
        "system" to follow the desktop, "light" or "dark", or the key of a theme with colours of its own. Anything else
        follows the system.

    Examples
    --------
    >>> apply_theme("system")
    >>> # noinspection PyUnresolvedReferences
    >>> app.styleSheet() != ""
    True
    >>> apply_theme("studio")
    >>> QApplication.palette().color(QPalette.ColorRole.Window).name()
    '#eceef1'
    >>> apply_theme("system")
    >>> QApplication.palette().color(QPalette.ColorRole.Window).name() != "#eceef1"
    True
    """
    global _applying, _custom_palette, _custom_window
    if _applying:  # changing the colour scheme announces itself, which must not start the change over
        return
    _applying = True
    gc.collect()  # widgets that are only waiting to be collected go now, not in the middle of the changes below
    gc.disable()  # Qt tells every widget about a new palette or style, and a widget freed while it does so would crash it
    try:
        QGuiApplication.styleHints().setColorScheme(scheme_of(key) or Qt.ColorScheme.Unknown)
        app = QApplication.instance()
        assert isinstance(app, QApplication)
        theme = custom_theme(key)
        if key.endswith(AUTO):  # a theme that follows the desktop: its light or its dark version, as the desktop is now
            theme = custom_theme(key[: -len(AUTO)] + ("_dark" if system_is_dark() else ""))
            _watch_the_desktop()
        if theme is not None:
            app.setPalette(theme_palette(theme))
            _custom_palette, _custom_window = True, theme.window
        elif _custom_palette:
            app.setPalette(QPalette())  # back from a theme with colours of its own: the palette is the desktop's again
            if app.palette().color(QPalette.ColorRole.Window).name() == _custom_window:
                app.setPalette(app.style().standardPalette())  # the reset did not take, so use the style's own for the scheme
            _custom_palette = False
        app.setStyleSheet(app_style(app.palette()))
    finally:
        gc.enable()
        _applying = False
