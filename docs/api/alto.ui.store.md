---
title: alto.ui.store
parent: api
package: alto.ui
permalink: /api/alto.ui.store/
---
{% raw %}
The application's saved settings (a thin layer over `QSettings`).

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings = store()
>>> settings.setValue("demo/count", 3)
>>> int_value(
...     settings, key="demo/count", default=0
... )
3
>>> settings.remove("demo")
```

## store

```python
def store() -> QSettings
```

Return the app's saved settings.

The first time it is opened under the name "alto" it brings across
anything saved under the old name ("mtheory"), so a
rename does not reset anyone's preferences. If `ALTO_HOME` is set
the settings are kept in a file in that folder instead,
and nothing is brought across from the system's own.

**Returns**

- *QSettings*: The settings, kept in the user's configuration folder or in `ALTO_HOME`.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings = store()
>>> settings.setValue("demo/name", "Ada")
>>> str(store().value("demo/name"))
'Ada'
>>> settings.remove("demo")
```

## int_value

```python
def int_value(
    settings: QSettings,
    *,
    key: str,
    default: int,
) -> int
```

Read an integer setting.

`QSettings` hands back whatever was saved, which may be a number or
its text.

**Parameters**

- `settings` (*QSettings*): The settings to read.
- `key` (*str*): The setting's name. Keyword-only.
- `default` (*int*): What to return if nothing is saved. Keyword-only.

**Returns**

- *int*: The saved value, or `default` if there is none (or it is not a number, text or similar).

**Raises**

- *ValueError*: If the saved text is not a whole number.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_ = store()
>>> settings_.setValue("demo/count", "42")
>>> int_value(
...     settings_, key="demo/count", default=0
... )
42
>>> int_value(
...     settings_, key="demo/missing", default=7
... )
7
>>> settings_.setValue("demo/count", "many")
>>> int_value(
...     settings_, key="demo/count", default=0
... )
Traceback (most recent call last):
    ...
ValueError: invalid literal for int() with base 10: 'many'
>>> settings_.remove("demo")
```

## text_value

```python
def text_value(
    settings: QSettings,
    *,
    key: str,
    default: str,
) -> str
```

Read a saved setting as text.

**Parameters**

- `settings` (*QSettings*): The settings to read.
- `key` (*str*): The setting's name. Keyword-only.
- `default` (*str*): What to return if nothing is saved. Keyword-only.

**Returns**

- *str*: The saved text, or `default` if there is none (or it is not text).

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_ = store()
>>> settings_.setValue("demo/name", "viola")
>>> text_value(
...     settings_,
...     key="demo/name",
...     default="piano",
... )
'viola'
>>> text_value(
...     settings_,
...     key="demo/missing",
...     default="piano",
... )
'piano'
>>> settings_.remove("demo")
```

## bool_value

```python
def bool_value(
    settings: QSettings,
    *,
    key: str,
    default: bool,
) -> bool
```

Read a switch saved as the text "true" or "false".

**Parameters**

- `settings` (*QSettings*): The settings to read.
- `key` (*str*): The setting's name. Keyword-only.
- `default` (*bool*): What to return if nothing is saved, or if the saved text is neither "true" nor "false". Keyword-only.

**Returns**

- *bool*: The saved switch.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_ = store()
>>> save_bool(
...     settings_, key="demo/on", value=True
... )
>>> (
...     bool_value(
...         settings_,
...         key="demo/on",
...         default=False,
...     ),
...     bool_value(
...         settings_,
...         key="demo/missing",
...         default=True,
...     ),
... )
(True, True)
>>> settings_.setValue("demo/on", "FALSE")
>>> bool_value(
...     settings_, key="demo/on", default=True
... )
False
>>> settings_.remove("demo")
```

## save_bool

```python
def save_bool(
    settings: QSettings,
    *,
    key: str,
    value: bool,
) -> None
```

Save a switch as the text "true" or "false", the form `bool_value`
reads.

**Parameters**

- `settings` (*QSettings*): The settings to write.
- `key` (*str*): The setting's name. Keyword-only.
- `value` (*bool*): The switch. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_ = store()
>>> save_bool(
...     settings_, key="demo/on", value=False
... )
>>> settings_.value("demo/on")
'false'
>>> settings_.remove("demo")
```

## list_value

```python
def list_value(
    settings: QSettings,
    *,
    key: str,
    separator: str = ',',
) -> list[str]
```

Read a saved list of words, such as "treble,bass".

`QSettings` may hand back text that contains commas as a list of its
parts, so both forms are read.

**Parameters**

- `settings` (*QSettings*): The settings to read.
- `key` (*str*): The setting's name. Keyword-only.
- `separator` (*str, default ","*): What separates the words in the saved text. Keyword-only.

**Returns**

- *list of str*: The words in their saved order, without empty ones; empty if nothing is saved.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_ = store()
>>> settings_.setValue(
...     "demo/clefs", "treble,,bass"
... )
>>> (
...     list_value(settings_, key="demo/clefs"),
...     list_value(
...         settings_, key="demo/missing"
...     ),
... )
(['treble', 'bass'], [])
>>> settings_.setValue(
...     "demo/modes", ["major|minor"]
... )
>>> list_value(
...     settings_,
...     key="demo/modes",
...     separator="|",
... )
['major', 'minor']
>>> settings_.remove("demo")
```

## choices_value

```python
def choices_value(
    settings: QSettings,
    *,
    key: str,
    allowed: Iterable[str],
    separator: str = ',',
) -> set[str]
```

Read a saved set of choices, keeping only the ones that are still
offered.

**Parameters**

- `settings` (*QSettings*): The settings to read.
- `key` (*str*): The setting's name. Keyword-only.
- `allowed` (*iterable of str*): The choices that exist now. Keyword-only.
- `separator` (*str, default ","*): What separates the choices in the saved text. Keyword-only.

**Returns**

- *set of str*: The saved choices that are allowed; empty if nothing is saved or none of them exists any more.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_ = store()
>>> settings_.setValue(
...     "demo/clefs", "treble,gone,bass"
... )
>>> sorted(
...     choices_value(
...         settings_,
...         key="demo/clefs",
...         allowed=("treble", "bass", "alto"),
...     )
... )
['bass', 'treble']
>>> settings_.remove("demo")
```

## keys_value

```python
def keys_value(
    settings: QSettings,
    *,
    key: str,
) -> set[int]
```

Read a saved set of key signatures, each a number of sharps
(positive) or flats (negative) up to seven.

**Parameters**

- `settings` (*QSettings*): The settings to read.
- `key` (*str*): The setting's name. Keyword-only.

**Returns**

- *set of int*: The saved key signatures that exist; empty if nothing usable is saved.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_ = store()
>>> settings_.setValue(
...     "demo/keys", "-2,0,9,x,3"
... )
>>> sorted(
...     keys_value(settings_, key="demo/keys")
... )
[-2, 0, 3]
>>> settings_.remove("demo")
```

## joined

```python
def joined(
    values: Iterable[object],
    *,
    separator: str = ',',
) -> str
```

Write values as the text that `list_value`, `choices_value` and
`keys_value` read back.

**Parameters**

- `values` (*iterable of object*): The values, in the order to save them.
- `separator` (*str, default ","*): What to put between them. Keyword-only.

**Returns**

- *str*: The values as text, joined by the separator.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     joined([-1, 0, 2]),
...     joined(
...         ["major", "minor"], separator="|"
...     ),
... )
('-1,0,2', 'major|minor')
```

## export_settings

```python
def export_settings() -> dict[str, object]
```

Return every saved preference, by key, for a backup.

**Returns**

- *dict of str to object*: Each key Alto has saved and its value. Qt byte arrays come back as `bytes` and lists as lists.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_ = store()
>>> settings_.setValue("demo/name", "Ada")
>>> export_settings()["demo/name"]
'Ada'
>>> settings_.remove("demo")
```

## import_settings

```python
def import_settings(values: Mapping[str, object]) -> None
```

Replace every saved preference with the ones from a backup, so the
preferences are exactly as they were.

Preferences saved now that the backup does not have are removed. The
marker that stops old "mtheory" preferences being
brought across again is kept, so an old installation's leftovers
cannot leak back in.

**Parameters**

- `values` (*mapping of str to object*): The preferences, by key, as `export_settings` returned them.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> import_settings(
...     {"demo/name": "Ada", "demo/count": 3}
... )
>>> (
...     store().value("demo/name"),
...     int_value(
...         store(), key="demo/count", default=0
...     ),
... )
('Ada', 3)
>>> store().remove("demo")
>>> store().remove("")
```
{% endraw %}
