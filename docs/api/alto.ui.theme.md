---
title: alto.ui.theme
parent: api
package: alto.ui
permalink: /api/alto.ui.theme/
---
{% raw %}
The color theme: follow the system, force light or dark, or use a theme
with colors of its own.

A theme with colors of its own is a `CustomTheme`: a fixed palette that
is light or dark whatever the desktop is set to.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> [key for key, label in THEMES][:4]
['system', 'light', 'dark', 'studio']
```

## CustomTheme

<div class="api-signature" markdown="1">

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

{% endraw %}{% include api-source.html name="CustomTheme" line=40 %}{% raw %}

</div>

A theme with colors of its own.

**Attributes**

- `key` (*str*): What it is saved as.
- `family` (*str*): The key of the light version of the theme, which its dark version shares.
- `label` (*str*): What the settings call it.
- `note` (*str*): A short line about it, shown under its picture.
- `dark` (*bool*): True if it is a dark theme, so that Qt draws its own parts (such as the title bar) to match.
- `window` (*str*): The color of the window.
- `panel` (*str*): The color of lists, boxes and buttons.
- `ink` (*str*): The color of text.
- `muted` (*str*): The color of quiet text.
- `line` (*str*): The color of outlines.
- `accent` (*str*): The color of what is chosen, and of links.
- `track` (*str*): The color of the track behind a switch or a slider, a little off the window's own.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     CUSTOM_THEMES[0].key,
...     CUSTOM_THEMES[0].dark,
...     len(CUSTOM_THEMES),
... )
('studio', False, 50)
```

## hsl_hex

<div class="api-signature" markdown="1">

```python
def hsl_hex(
    hue: float,
    *,
    saturation: float,
    lightness: float,
) -> str
```

{% endraw %}{% include api-source.html name="hsl_hex" line=201 %}{% raw %}

</div>

Turn a color given as hue, saturation and lightness into "#rrggbb".

**Parameters**

- `hue` (*float*): The hue, in degrees.
- `saturation` (*float*): The saturation, from 0 to 100. Keyword-only.
- `lightness` (*float*): The lightness, from 0 to 100. Keyword-only.

**Returns**

- *str*: The color in hexadecimal.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     hsl_hex(
...         0, saturation=100, lightness=50
...     ),
...     hsl_hex(
...         210, saturation=0, lightness=100
...     ),
... )
('#ff0000', '#ffffff')
```

## seeded_themes

<div class="api-signature" markdown="1">

```python
def seeded_themes(seed: tuple[str, str, str, float, float, float, float]) -> tuple[CustomTheme, CustomTheme]
```

{% endraw %}{% include api-source.html name="seeded_themes" line=264 %}{% raw %}

</div>

Make the light and the dark theme of a seed: neutrals tinted by one
hue, and an accent of another.

**Parameters**

- `seed` (*tuple*): The key, name and note, then the neutral hue and saturation and the accent hue and saturation.

**Returns**

- *tuple of (CustomTheme, CustomTheme)*: The light theme and the dark theme.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> pale, deep = seeded_themes(SEEDS[0])
>>> pale.key, deep.key, pale.dark, deep.dark
('parchment', 'parchment_dark', False, True)
```

## family_of

<div class="api-signature" markdown="1">

```python
def family_of(key: str) -> tuple[str, str]
```

{% endraw %}{% include api-source.html name="family_of" line=393 %}{% raw %}

</div>

Split a theme's key into its family and which version of it that is.

**Parameters**

- `key` (*str*): The key of any theme.

**Returns**

- *tuple of (str, str)*: The family's key and "light", "dark" or "system". "system", "light" and "dark" belong to the family "default".

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     family_of("sage_dark"),
...     family_of("sage"),
...     family_of("sage_auto"),
...     family_of("dark"),
...     family_of("system"),
... )
(('sage', 'dark'), ('sage', 'light'), ('sage', 'system'),
('default', 'dark'), ('default', 'system'))
```

## variant_key

<div class="api-signature" markdown="1">

```python
def variant_key(
    family: str,
    *,
    version: str,
) -> str
```

{% endraw %}{% include api-source.html name="variant_key" line=432 %}{% raw %}

</div>

Give the key of one version of a family.

**Parameters**

- `family` (*str*): The family's key.
- `version` (*str*): "light", "dark" or "system". Keyword-only.

**Returns**

- *str*: The key.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     variant_key("sage", version="dark"),
...     variant_key("sage", version="system"),
...     variant_key("default", version="dark"),
... )
('sage_dark', 'sage_auto', 'dark')
```

## ThemeRecord

<div class="api-signature" markdown="1">

```python
class ThemeRecord(TypedDict)
```

{% endraw %}{% include api-source.html name="ThemeRecord" line=496 %}{% raw %}

</div>

A theme the user made, as it is saved: its key, its name, and the
colors of its light and dark versions.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ThemeRecord(
...     id="my_1",
...     name="Mine",
...     light={},
...     dark={},
... )["name"]
'Mine'
```

## user_records

<div class="api-signature" markdown="1">

```python
def user_records() -> list[ThemeRecord]
```

{% endraw %}{% include api-source.html name="user_records" line=576 %}{% raw %}

</div>

Read the themes the user has made, as they are saved.

**Returns**

- *list of ThemeRecord*: One record for each theme: its "id", its "name", and its "light" and "dark" colors. A saved list that cannot be read, or has something else in it, gives only the records that can be used.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().remove("ui/userThemes")
>>> user_records()
[]
```

## save_user_records

<div class="api-signature" markdown="1">

```python
def save_user_records(records: list[ThemeRecord]) -> None
```

{% endraw %}{% include api-source.html name="save_user_records" line=606 %}{% raw %}

</div>

Save the themes the user has made.

**Parameters**

- `records` (*list of ThemeRecord*): The records, as `user_records` gives them.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_user_records([])
>>> user_records()
[]
```

## new_family_id

<div class="api-signature" markdown="1">

```python
def new_family_id() -> str
```

{% endraw %}{% include api-source.html name="new_family_id" line=624 %}{% raw %}

</div>

Make the key for a new theme of the user's.

**Returns**

- *str*: A key that starts with "my_" and is not one that is in use.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new_family_id().startswith("my_")
True
```

## upsert_user_theme

<div class="api-signature" markdown="1">

```python
def upsert_user_theme(record: ThemeRecord) -> None
```

{% endraw %}{% include api-source.html name="upsert_user_theme" line=645 %}{% raw %}

</div>

Save a theme the user made, replacing the one with the same key if
there is one.

**Parameters**

- `record` (*ThemeRecord*): The theme.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().remove("ui/userThemes")
>>> colors = {part: "#112233" for part in PARTS}
>>> upsert_user_theme(
...     ThemeRecord(
...         id="my_a",
...         name="Mine",
...         light=colors,
...         dark=colors,
...     )
... )
>>> upsert_user_theme(
...     ThemeRecord(
...         id="my_a",
...         name="Renamed",
...         light=colors,
...         dark=colors,
...     )
... )
>>> [
...     (r["id"], r["name"])
...     for r in user_records()
... ]
[('my_a', 'Renamed')]
>>> store().remove("ui/userThemes")
```

## delete_user_theme

<div class="api-signature" markdown="1">

```python
def delete_user_theme(family: str) -> None
```

{% endraw %}{% include api-source.html name="delete_user_theme" line=698 %}{% raw %}

</div>

Remove a theme the user made.

**Parameters**

- `family` (*str*): The theme's key.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().remove("ui/userThemes")
>>> colors = {part: "#112233" for part in PARTS}
>>> upsert_user_theme(
...     ThemeRecord(
...         id="my_a",
...         name="Mine",
...         light=colors,
...         dark=colors,
...     )
... )
>>> delete_user_theme("my_a")
>>> user_records()
[]
```

## theme_of

<div class="api-signature" markdown="1">

```python
def theme_of(
    colors: dict[str, str],
    *,
    dark: bool,
    key: str = '',
    family: str = '',
    label: str = '',
    note: str = '',
) -> CustomTheme
```

{% endraw %}{% include api-source.html name="theme_of" line=728 %}{% raw %}

</div>

Build a custom theme from its saved or preview colors.

**Parameters**

- `colors` (*dict of str to str*): A color for every part, as "#rrggbb".
- `dark` (*bool*): True if it is the dark version. Keyword-only.
- `key` (*str*): Saved theme identifier, or empty for a preview.
- `family` (*str*): Identifier shared by the light and dark versions.
- `label` (*str*): Name displayed in settings.
- `note` (*str*): Description displayed with the theme.

**Returns**

- *CustomTheme*: The theme with the supplied colors and identifiers.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> theme_of(
...     {part: "#102030" for part in PARTS},
...     dark=True,
... ).window
'#102030'
```

## user_themes

<div class="api-signature" markdown="1">

```python
def user_themes() -> tuple[CustomTheme, ...]
```

{% endraw %}{% include api-source.html name="user_themes" line=784 %}{% raw %}

</div>

Give the themes the user has made, light and dark versions of each.

**Returns**

- *tuple of CustomTheme*: The light theme and then the dark theme of each record.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().remove("ui/userThemes")
>>> user_themes()
()
```

## families

<div class="api-signature" markdown="1">

```python
def families() -> tuple[tuple[str, str, str], ...]
```

{% endraw %}{% include api-source.html name="families" line=822 %}{% raw %}

</div>

List every theme there is to choose, the user's own first.

**Returns**

- *tuple of tuple of (str, str, str)*: The key of each theme's family, its name and a line about it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().remove("ui/userThemes")
>>> families() == FAMILIES
True
```

## custom_theme

<div class="api-signature" markdown="1">

```python
def custom_theme(key: str) -> CustomTheme | None
```

{% endraw %}{% include api-source.html name="custom_theme" line=845 %}{% raw %}

</div>

Find a theme with colors of its own, one of the built-in ones or one
the user made.

**Parameters**

- `key` (*str*): The theme's key.

**Returns**

- *CustomTheme or None*: The theme, or None for "system", "light", "dark" or anything that is not one.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     custom_theme("studio_dark")
...     is CUSTOM_THEMES[1],
...     custom_theme("dark"),
... )
(True, None)
```

## scheme_of

<div class="api-signature" markdown="1">

```python
def scheme_of(key: str) -> Qt.ColorScheme | None
```

{% endraw %}{% include api-source.html name="scheme_of" line=880 %}{% raw %}

</div>

Say which color scheme a theme uses: light, dark, or the desktop's
own.

**Parameters**

- `key` (*str*): The theme's key.

**Returns**

- *Qt.ColorScheme or None*: The scheme; None if there is no theme with that key.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     scheme_of("dark")
...     == Qt.ColorScheme.Dark,
...     scheme_of("sage_auto")
...     == Qt.ColorScheme.Unknown,
...     scheme_of("nonsense"),
... )
(True, True, None)
```

## preview_colors

<div class="api-signature" markdown="1">

```python
def preview_colors(theme: CustomTheme) -> dict[str, str]
```

{% endraw %}{% include api-source.html name="preview_colors" line=917 %}{% raw %}

</div>

Pick the colors for the small picture of a theme in the settings.

**Parameters**

- `theme` (*CustomTheme*): The theme.

**Returns**

- *dict of str to str*: The window, panel, outline, text, faint and chosen colors, and a tint for the chosen row.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     preview_colors(CUSTOM_THEMES[0])[
...         "window"
...     ],
...     sorted(
...         preview_colors(CUSTOM_THEMES[0])
...     )[:3],
... )
('#eceef1', ['accent', 'faint', 'ink'])
```

## theme_palette

<div class="api-signature" markdown="1">

```python
def theme_palette(theme: CustomTheme) -> QPalette
```

{% endraw %}{% include api-source.html name="theme_palette" line=956 %}{% raw %}

</div>

Build the Qt palette of a theme with colors of its own.

**Parameters**

- `theme` (*CustomTheme*): The theme.

**Returns**

- *QPalette*: The palette: the window, lists and buttons, text, the chosen row and links in the theme's colors, with quiet text for what is switched off.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> colors = theme_palette(CUSTOM_THEMES[0])
>>> (
...     colors.color(
...         QPalette.ColorRole.Window
...     ).name(),
...     colors.color(
...         QPalette.ColorRole.Highlight
...     ).name(),
... )
('#eceef1', '#2f7fc1')
```

## saved_theme

<div class="api-signature" markdown="1">

```python
def saved_theme() -> str
```

{% endraw %}{% include api-source.html name="saved_theme" line=1029 %}{% raw %}

</div>

Return the theme the user chose.

**Returns**

- *str*: The key of the theme: "system", "light", "dark" or one of the themes with colors of its own; "system" if nothing valid is saved.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_theme("dark")
>>> saved_theme()
'dark'
>>> save_theme("system")
```

## save_theme

<div class="api-signature" markdown="1">

```python
def save_theme(key: str) -> None
```

{% endraw %}{% include api-source.html name="save_theme" line=1051 %}{% raw %}

</div>

Remember the theme the user chose.

**Parameters**

- `key` (*str*): "system", "light", "dark" or the key of a theme with colors of its own.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_theme("light")
>>> saved_theme()
'light'
>>> save_theme("system")
```

## system_is_dark

<div class="api-signature" markdown="1">

```python
def system_is_dark() -> bool
```

{% endraw %}{% include api-source.html name="system_is_dark" line=1086 %}{% raw %}

</div>

Say whether the desktop is set to dark, as long as the app is not
forcing a color scheme of its own.

A theme that follows the desktop does not force one, so this is what
it asks.

**Returns**

- *bool*: True if the color scheme in use is dark.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> system_is_dark() in {True, False}
True
```

## apply_theme

<div class="api-signature" markdown="1">

```python
def apply_theme(key: str) -> None
```

{% endraw %}{% include api-source.html name="apply_theme" line=1161 %}{% raw %}

</div>

Switch the application's color scheme and rebuild the stylesheet
from the new palette.

**Parameters**

- `key` (*str*): "system" to follow the desktop, "light" or "dark", or the key of a theme with colors of its own. Anything else follows the system.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> apply_theme("system")
>>> # noinspection PyUnresolvedReferences
>>> app.styleSheet() != ""
True
>>> apply_theme("studio")
>>> QApplication.palette().color(
...     QPalette.ColorRole.Window
... ).name()
'#eceef1'
>>> apply_theme("system")
>>> QApplication.palette().color(
...     QPalette.ColorRole.Window
... ).name() != "#eceef1"
True
```
{% endraw %}
