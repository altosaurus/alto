---
title: alto.ui.theme
parent: api
package: alto.ui
order: 52
permalink: /api/alto.ui.theme/
---
{% raw %}
The colour theme: follow the system, force light or dark, or use a theme with colours of its own.

A theme with colours of its own is a `CustomTheme`: a fixed palette that is light or dark whatever the desktop is set to.

**Examples**

```pycon
>>> [key for key, label in THEMES][:4]
['system', 'light', 'dark', 'studio']
```

## CustomTheme

```python
CustomTheme(
    key: str,
    family: str,
    label: str,
    note: str,
    dark: bool,
    window: str,
    panel: str,
    ink: str,
    muted: str,
    line: str,
    accent: str,
    track: str,
)
```

A theme with colours of its own.

**Attributes**

- `key` (*str*): What it is saved as.
- `family` (*str*): The key of the light version of the theme, which its dark version shares.
- `label` (*str*): What the settings call it.
- `note` (*str*): A short line about it, shown under its picture.
- `dark` (*bool*): True if it is a dark theme, so that Qt draws its own parts (such as the title bar) to match.
- `window` (*str*): The colour of the window.
- `panel` (*str*): The colour of lists, boxes and buttons.
- `ink` (*str*): The colour of text.
- `muted` (*str*): The colour of quiet text.
- `line` (*str*): The colour of outlines.
- `accent` (*str*): The colour of what is chosen, and of links.
- `track` (*str*): The colour of the track behind a switch or a slider, a little off the window's own.

**Examples**

```pycon
>>> CUSTOM_THEMES[0].key, CUSTOM_THEMES[0].dark, len(CUSTOM_THEMES)
('studio', False, 50)
```

## hsl_hex

```python
def hsl_hex(
    hue: float,
    *,
    saturation: float,
    lightness: float,
) -> str
```

Turn a colour given as hue, saturation and lightness into "#rrggbb".

**Parameters**

- `hue` (*float*): The hue, in degrees.
- `saturation` (*float*): The saturation, from 0 to 100. Keyword-only.
- `lightness` (*float*): The lightness, from 0 to 100. Keyword-only.

**Returns**

- *str*: The colour in hexadecimal.

**Examples**

```pycon
>>> hsl_hex(0, saturation=100, lightness=50), hsl_hex(210, saturation=0, lightness=100)
('#ff0000', '#ffffff')
```

## seeded_themes

```python
def seeded_themes(seed: tuple[str, str, str, float, float, float, float]) -> tuple[CustomTheme, CustomTheme]
```

Make the light and the dark theme of a seed: neutrals tinted by one hue, and an accent of another.

**Parameters**

- `seed` (*tuple*): The key, name and note, then the neutral hue and saturation and the accent hue and saturation.

**Returns**

- *tuple of (CustomTheme, CustomTheme)*: The light theme and the dark theme.

**Examples**

```pycon
>>> pale, deep = seeded_themes(SEEDS[0])
>>> pale.key, deep.key, pale.dark, deep.dark
('parchment', 'parchment_dark', False, True)
```

## family_of

```python
def family_of(key: str) -> tuple[str, str]
```

Split a theme's key into its family and which version of it that is.

**Parameters**

- `key` (*str*): The key of any theme.

**Returns**

- *tuple of (str, str)*: The family's key and "light", "dark" or "system". "system", "light" and "dark" belong to the family "default".

**Examples**

```pycon
>>> family_of("sage_dark"), family_of("sage"), family_of("sage_auto"), family_of("dark"), family_of("system")
(('sage', 'dark'), ('sage', 'light'), ('sage', 'system'), ('default', 'dark'), ('default', 'system'))
```

## variant_key

```python
def variant_key(
    family: str,
    *,
    version: str,
) -> str
```

Give the key of one version of a family.

**Parameters**

- `family` (*str*): The family's key.
- `version` (*str*): "light", "dark" or "system". Keyword-only.

**Returns**

- *str*: The key.

**Examples**

```pycon
>>> variant_key("sage", version="dark"), variant_key("sage", version="system"), variant_key("default", version="dark")
('sage_dark', 'sage_auto', 'dark')
```

## ThemeRecord

```python
class ThemeRecord(TypedDict)
```

A theme the user made, as it is saved: its key, its name, and the colours of its light and dark versions.

**Examples**

```pycon
>>> ThemeRecord(id="my_1", name="Mine", light={}, dark={})["name"]
'Mine'
```

## user_records

```python
def user_records() -> list[ThemeRecord]
```

Read the themes the user has made, as they are saved.

**Returns**

- *list of ThemeRecord*: One record for each theme: its "id", its "name", and its "light" and "dark" colours. A saved list that cannot be read, or has something else in it, gives only the records that can be used.

**Examples**

```pycon
>>> store().remove("ui/userThemes")
>>> user_records()
[]
```

## save_user_records

```python
def save_user_records(records: list[ThemeRecord]) -> None
```

Save the themes the user has made.

**Parameters**

- `records` (*list of ThemeRecord*): The records, as `user_records` gives them.

**Examples**

```pycon
>>> save_user_records([])
>>> user_records()
[]
```

## new_family_id

```python
def new_family_id() -> str
```

Make the key for a new theme of the user's.

**Returns**

- *str*: A key that starts with "my_" and is not one that is in use.

**Examples**

```pycon
>>> new_family_id().startswith("my_")
True
```

## upsert_user_theme

```python
def upsert_user_theme(record: ThemeRecord) -> None
```

Save a theme the user made, replacing the one with the same key if there is one.

**Parameters**

- `record` (*ThemeRecord*): The theme.

**Examples**

```pycon
>>> store().remove("ui/userThemes")
>>> colours = {part: "#112233" for part in PARTS}
>>> upsert_user_theme(ThemeRecord(id="my_a", name="Mine", light=colours, dark=colours))
>>> upsert_user_theme(ThemeRecord(id="my_a", name="Renamed", light=colours, dark=colours))
>>> [(r["id"], r["name"]) for r in user_records()]
[('my_a', 'Renamed')]
>>> store().remove("ui/userThemes")
```

## delete_user_theme

```python
def delete_user_theme(family: str) -> None
```

Remove a theme the user made.

**Parameters**

- `family` (*str*): The theme's key.

**Examples**

```pycon
>>> store().remove("ui/userThemes")
>>> colours = {part: "#112233" for part in PARTS}
>>> upsert_user_theme(ThemeRecord(id="my_a", name="Mine", light=colours, dark=colours))
>>> delete_user_theme("my_a")
>>> user_records()
[]
```

## user_themes

```python
def user_themes() -> tuple[CustomTheme, ...]
```

Give the themes the user has made, light and dark versions of each.

**Returns**

- *tuple of CustomTheme*: The light theme and then the dark theme of each record.

**Examples**

```pycon
>>> store().remove("ui/userThemes")
>>> user_themes()
()
```

## families

```python
def families() -> tuple[tuple[str, str, str], ...]
```

List every theme there is to choose, the user's own first.

**Returns**

- *tuple of tuple of (str, str, str)*: The key of each theme's family, its name and a line about it.

**Examples**

```pycon
>>> store().remove("ui/userThemes")
>>> families() == FAMILIES
True
```

## custom_theme

```python
def custom_theme(key: str) -> CustomTheme | None
```

Find a theme with colours of its own, one of the built-in ones or one the user made.

**Parameters**

- `key` (*str*): The theme's key.

**Returns**

- *CustomTheme or None*: The theme, or None for "system", "light", "dark" or anything that is not one.

**Examples**

```pycon
>>> custom_theme("studio_dark") is CUSTOM_THEMES[1], custom_theme("dark")
(True, None)
```

## scheme_of

```python
def scheme_of(key: str) -> Qt.ColorScheme | None
```

Say which colour scheme a theme uses: light, dark, or the desktop's own.

**Parameters**

- `key` (*str*): The theme's key.

**Returns**

- *Qt.ColorScheme or None*: The scheme; None if there is no theme with that key.

**Examples**

```pycon
>>> scheme_of("dark") == Qt.ColorScheme.Dark, scheme_of("sage_auto") == Qt.ColorScheme.Unknown, scheme_of("nonsense")
(True, True, None)
```

## preview_colours

```python
def preview_colours(theme: CustomTheme) -> dict[str, str]
```

Pick the colours for the small picture of a theme in the settings.

**Parameters**

- `theme` (*CustomTheme*): The theme.

**Returns**

- *dict of str to str*: The window, panel, outline, text, faint and chosen colours, and a tint for the chosen row.

**Examples**

```pycon
>>> preview_colours(CUSTOM_THEMES[0])["window"], sorted(preview_colours(CUSTOM_THEMES[0]))[:3]
('#eceef1', ['accent', 'faint', 'ink'])
```

## theme_palette

```python
def theme_palette(theme: CustomTheme) -> QPalette
```

Build the Qt palette of a theme with colours of its own.

**Parameters**

- `theme` (*CustomTheme*): The theme.

**Returns**

- *QPalette*: The palette: the window, lists and buttons, text, the chosen row and links in the theme's colours, with quiet text for what is switched off.

**Examples**

```pycon
>>> colours = theme_palette(CUSTOM_THEMES[0])
>>> colours.color(QPalette.ColorRole.Window).name(), colours.color(QPalette.ColorRole.Highlight).name()
('#eceef1', '#2f7fc1')
```

## saved_theme

```python
def saved_theme() -> str
```

Return the theme the user chose.

**Returns**

- *str*: The key of the theme: "system", "light", "dark" or one of the themes with colours of its own; "system" if nothing valid is saved.

**Examples**

```pycon
>>> save_theme("dark")
>>> saved_theme()
'dark'
>>> save_theme("system")
```

## save_theme

```python
def save_theme(key: str) -> None
```

Remember the theme the user chose.

**Parameters**

- `key` (*str*): "system", "light", "dark" or the key of a theme with colours of its own.

**Examples**

```pycon
>>> save_theme("light")
>>> saved_theme()
'light'
>>> save_theme("system")
```

## system_is_dark

```python
def system_is_dark() -> bool
```

Say whether the desktop is set to dark, as long as the app is not forcing a colour scheme of its own.

A theme that follows the desktop does not force one, so this is what it asks.

**Returns**

- *bool*: True if the colour scheme in use is dark.

**Examples**

```pycon
>>> system_is_dark() in {True, False}
True
```

## apply_theme

```python
def apply_theme(key: str) -> None
```

Switch the application's colour scheme and rebuild the stylesheet from the new palette.

**Parameters**

- `key` (*str*): "system" to follow the desktop, "light" or "dark", or the key of a theme with colours of its own. Anything else follows the system.

**Examples**

```pycon
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
```
{% endraw %}
