---
title: alto.ui.main_window
parent: api
package: alto.ui
permalink: /api/alto.ui.main_window/
---
{% raw %}
The main window: tile browsing or a workspace with an independently
selected exercise or lesson list.

Navigation stays on the left of the top bar, with data tools on the
right. Browsing tiles retains the active activity.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> window = MainWindow()
>>> window.title_label.text()
'Alto - Music Theory'
```

## default_size

<div class="api-signature" markdown="1">

```python
def default_size() -> tuple[int, int]
```

{% endraw %}{% include api-source.html name="default_size" line=153 %}{% raw %}

</div>

Return the size a new window opens at.

It is big enough for a lesson step, with its circle, to show without
scrolling, but never more than most of the screen.

**Returns**

- *tuple of (int, int)*: The width and height in pixels.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> width, height = default_size()
>>> 0 < width <= DEFAULT_WIDTH and 0 < height <= DEFAULT_HEIGHT
True
```

## MainWindow

<div class="api-signature" markdown="1">

```python
MainWindow(learner: Learner | None = None)
```

{% endraw %}{% include api-source.html name="MainWindow" line=416 %}{% raw %}

</div>

Bases: `QMainWindow`

The application window.

**Attributes**

- `SIDEBAR_MIN` (*int*): The narrowest the exercise list can be before it collapses, in pixels.
- `SIDEBAR_DEFAULT` (*int*): The list's width the first time.
- `APP_TITLE` (*str*): The title shown on the start screen.
- `learner` (*Learner or None*): Who is practicing, and their history; None practices without recording.
- `nav` (*QListWidget*): The exercise list.
- `stack` (*QStackedWidget*): The pages: the start screen, then exercises and the statistics or database while they are open.
- `home` (*HomePage*): The start screen.
- `splitter` (*QSplitter*): Holds the list and the pages, so the list can be dragged narrower or wider.
- `title_label` (*QLabel*): The title in the top bar.
- `view_button` (*QToolButton*): Returns to the tiles without discarding the current activity.
- `pane_button` (*SidebarToggle*): Opens or closes the navigation pane beside the current activity.
- `empty_page` (*QLabel*): The selected section's prompt before an activity starts.
- `search_field` (*QLineEdit*): Filters tiles and navigation lists without leaving the current activity.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> window = MainWindow()
>>> window.open_exercise(NoteNames)
>>> window.title_label.text()
'Note Identification'
>>> window.show_home()
```

**Constructor**

Build the window and load every saved setting.

**Parameters**

- `learner` (*Learner or None, default None*): Who is practicing. Without one, nothing is recorded and the statistics buttons are hidden.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.learning import Database
>>> db = Database()
>>> window_ = MainWindow(
...     Learner(
...         db, profile=db.add_profile("Ada")
...     )
... )
>>> window_.stats_button.isVisibleTo(window_)
True
>>> MainWindow().stats_button.isVisibleTo(
...     window_
... )  # no profile, no statistics
False
```

### MainWindow.closeEvent

<div class="api-signature" markdown="1">

```python
def closeEvent(event: QCloseEvent) -> None
```

{% endraw %}{% include api-source.html name="MainWindow.closeEvent" line=548 %}{% raw %}

</div>

Remember the window's size and position when the app closes.

**Parameters**

- `event` (*QCloseEvent*): The window close event.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> closeEvent()  # doctest: +SKIP
```

### MainWindow.eventFilter

<div class="api-signature" markdown="1">

```python
def eventFilter(
    watched: QObject,
    event: QEvent,
) -> bool
```

{% endraw %}{% include api-source.html name="MainWindow.eventFilter" line=1076 %}{% raw %}

</div>

Highlight the search field's outline while it has keyboard
focus.

**Parameters**

- `watched` (*QObject*): The search field.
- `event` (*QEvent*): The event being delivered.

**Returns**

- *bool*: Whether the base window consumes the event; focus changes are allowed through.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> window = MainWindow()
>>> window.eventFilter(
...     window.search_field,
...     QEvent(QEvent.Type.FocusIn),
... )
False
>>> window.search_row.property("focusWithin")
True
```

### MainWindow.sidebar_width

<div class="api-signature" markdown="1">

```python
def sidebar_width() -> int
```

{% endraw %}{% include api-source.html name="MainWindow.sidebar_width" line=1123 %}{% raw %}

</div>

Return how wide the exercise list is.

**Returns**

- *int*: The width in pixels; 0 when the list is collapsed, as it always is on the start screen.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> MainWindow().sidebar_width()
0
```

### MainWindow.toggle_sidebar

<div class="api-signature" markdown="1">

```python
def toggle_sidebar() -> None
```

{% endraw %}{% include api-source.html name="MainWindow.toggle_sidebar" line=1222 %}{% raw %}

</div>

Slide the list closed, or back open, for the user's button. The
choice is remembered for next time.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> window = MainWindow()
>>> window.toggle_sidebar()
>>> window._sidebar_pref
True
```

### MainWindow.open_exercise

<div class="api-signature" markdown="1">

```python
def open_exercise(cls: type[Exercise] | None) -> None
```

{% endraw %}{% include api-source.html name="MainWindow.open_exercise" line=1438 %}{% raw %}

</div>

Show an exercise.

**Parameters**

- `cls` (*type of Exercise or None*): The exercise class; None (a category heading in the list, which has no class) does nothing.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import (
...     KeySignatures,
... )
>>> window = MainWindow()
>>> window.open_exercise(KeySignatures)
>>> window.title_label.text()
'Key Signature Identification'
```

### MainWindow.show_about

<div class="api-signature" markdown="1">

```python
def show_about() -> None
```

{% endraw %}{% include api-source.html name="MainWindow.show_about" line=1485 %}{% raw %}

</div>

Show the installed version, development status, and purpose of
Alto.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> window.show_about()  # doctest: +SKIP
```

### MainWindow.open_anki_exporter

<div class="api-signature" markdown="1">

```python
def open_anki_exporter() -> None
```

{% endraw %}{% include api-source.html name="MainWindow.open_anki_exporter" line=1515 %}{% raw %}

</div>

Open the modeless exporter with a private copy of the current
exercise settings.

**Examples**

```text
Choose Anki Exporter from Tools to prepare a deck while keeping
the exercise open.
```

### MainWindow.open_settings

<div class="api-signature" markdown="1">

```python
def open_settings() -> None
```

{% endraw %}{% include api-source.html name="MainWindow.open_settings" line=1539 %}{% raw %}

</div>

Open the application settings without blocking the window, or
bring them forward if they are already open.

If the theme was changed, the window is rebuilt in it once the
settings are closed.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> window = MainWindow()
>>> window.open_settings()
>>> # noinspection PyUnresolvedReferences
>>> (
...     window._settings is not None
...     and not window._settings.isModal()
... )
True
>>> # noinspection PyUnresolvedReferences
>>> window._settings.close()
True
```

### MainWindow.rebuild

<div class="api-signature" markdown="1">

```python
def rebuild() -> None
```

{% endraw %}{% include api-source.html name="MainWindow.rebuild" line=1763 %}{% raw %}

</div>

Make the window's contents again in the same window, so every
icon and color is drawn in the new theme.

The window itself stays, so it does not vanish and reappear. The
page that was open is shown again, with the list
already open or closed as it was, not sliding.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> window = MainWindow()
>>> old_root = window.centralWidget()
>>> window.rebuild()
>>> window.centralWidget() is old_root
False
```

### MainWindow.open_glossary

<div class="api-signature" markdown="1">

```python
def open_glossary() -> None
```

{% endraw %}{% include api-source.html name="MainWindow.open_glossary" line=2004 %}{% raw %}

</div>

Toggle the glossary from its toolbar button.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> open_glossary()  # doctest: +SKIP
```

### MainWindow.open_stats

<div class="api-signature" markdown="1">

```python
def open_stats() -> None
```

{% endraw %}{% include api-source.html name="MainWindow.open_stats" line=2020 %}{% raw %}

</div>

Show the statistics in place of the current page. Nothing
happens without a profile.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.learning import Database
>>> db = Database()
>>> window = MainWindow(
...     Learner(
...         db, profile=db.add_profile("Ada")
...     )
... )
>>> window.open_stats()
>>> window.title_label.text()
'Statistics'
>>> window.close_overlay()
```

### MainWindow.toggle_navigation

<div class="api-signature" markdown="1">

```python
def toggle_navigation() -> None
```

{% endraw %}{% include api-source.html name="MainWindow.toggle_navigation" line=2195 %}{% raw %}

</div>

Open the workspace from tiles, or toggle its navigation pane
without leaving the activity.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> window = MainWindow()
>>> window.toggle_navigation()
>>> (
...     window.stack.currentWidget()
...     is window.empty_page,
...     window.view_button.accessibleName(),
... )
(True, 'Tiles')
```

### MainWindow.show_lessons

<div class="api-signature" markdown="1">

```python
def show_lessons() -> None
```

{% endraw %}{% include api-source.html name="MainWindow.show_lessons" line=2283 %}{% raw %}

</div>

Go to the start screen showing the lessons.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> window = MainWindow()
>>> window.show_lessons()
>>> window.home.mode
'lessons'
>>> window.home.set_mode("exercises")
```

### MainWindow.open_lessons

<div class="api-signature" markdown="1">

```python
def open_lessons(lesson: str) -> None
```

{% endraw %}{% include api-source.html name="MainWindow.open_lessons" line=2298 %}{% raw %}

</div>

Open a lesson in place of the current page, at the step it was
left at, with the lesson list on the left.

**Parameters**

- `lesson` (*str*): The key of the lesson.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> window = MainWindow()
>>> window.open_lessons("circle-of-fifths")
>>> (
...     window.title_label.text(),
...     window.nav_stack.currentWidget()
...     is window.lesson_nav,
... )
('The Circle of Fifths', True)
>>> window.close_overlay()
```

### MainWindow.open_database

<div class="api-signature" markdown="1">

```python
def open_database() -> None
```

{% endraw %}{% include api-source.html name="MainWindow.open_database" line=2529 %}{% raw %}

</div>

Show the database browser in place of the current page. Nothing
happens without a profile.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.learning import Database
>>> db = Database()
>>> window = MainWindow(
...     Learner(
...         db, profile=db.add_profile("Ada")
...     )
... )
>>> window.open_database()
>>> window.title_label.text()
'Database'
>>> window.close_overlay()
```

### MainWindow.close_overlay

<div class="api-signature" markdown="1">

```python
def close_overlay() -> None
```

{% endraw %}{% include api-source.html name="MainWindow.close_overlay" line=2652 %}{% raw %}

</div>

Leave the statistics or database page and show the page that was
open before it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.learning import Database
>>> db = Database()
>>> window = MainWindow(
...     Learner(
...         db, profile=db.add_profile("Ada")
...     )
... )
>>> window.open_stats()
>>> window.close_overlay()
>>> window.title_label.text()
'Alto - Music Theory'
```

### MainWindow.switch_profile

<div class="api-signature" markdown="1">

```python
def switch_profile() -> None
```

{% endraw %}{% include api-source.html name="MainWindow.switch_profile" line=2684 %}{% raw %}

</div>

Choose or add a profile.

Their history and questions are kept apart; the next question
comes from theirs.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> window = MainWindow()
>>> # without a profile there is nothing to switch
>>> window.switch_profile()
```

### MainWindow.export_backup

<div class="api-signature" markdown="1">

```python
def export_backup() -> None
```

{% endraw %}{% include api-source.html name="MainWindow.export_backup" line=2725 %}{% raw %}

</div>

Save a backup of everything: ask where, then write profiles,
history and settings to one file.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> # does nothing without a profile
>>> MainWindow().export_backup()
```

### MainWindow.check_for_updates

<div class="api-signature" markdown="1">

```python
def check_for_updates() -> None
```

{% endraw %}{% include api-source.html name="MainWindow.check_for_updates" line=2738 %}{% raw %}

</div>

Ask whether a newer Alto is available; if so and the person
agrees, install it and restart.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> MainWindow().check_for_updates()  # doctest: +SKIP
```

### MainWindow.import_backup

<div class="api-signature" markdown="1">

```python
def import_backup() -> None
```

{% endraw %}{% include api-source.html name="MainWindow.import_backup" line=2749 %}{% raw %}

</div>

Replace everything with a backup: ask for the file, check it,
ask again, and reload the whole window from it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> # does nothing without a profile
>>> MainWindow().import_backup()
```

### MainWindow.show_home

<div class="api-signature" markdown="1">

```python
def show_home() -> None
```

{% endraw %}{% include api-source.html name="MainWindow.show_home" line=2788 %}{% raw %}

</div>

Go back to the start screen, closing the statistics or database
and hiding the exercise list.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> window = MainWindow()
>>> window.open_exercise(NoteNames)
>>> window.show_home()
>>> window.title_label.text()
'Alto - Music Theory'
```

### MainWindow.open_plugins

<div class="api-signature" markdown="1">

```python
def open_plugins() -> None
```

{% endraw %}{% include api-source.html name="MainWindow.open_plugins" line=2852 %}{% raw %}

</div>

Manage installed plugins, install by code or ZIP, and update
from registered releases.

**Examples**

```text
Choose Plugins in Tools to see the installed viola pack.
```

### MainWindow.install_plugin

<div class="api-signature" markdown="1">

```python
def install_plugin(
    *,
    parent: QWidget | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="MainWindow.install_plugin" line=2872 %}{% raw %}

</div>

Install a downloaded instrument pack and offer to restart Alto.

**Parameters**

- `parent` (*QWidget or None, default None*): The window that owns the file chooser and messages. Defaults to this window. Keyword-only.

**Examples**

```text
Press Install plugin from file in the Plugins dialog and open
viola.zip.
```

### MainWindow.uninstall_plugin

<div class="api-signature" markdown="1">

```python
def uninstall_plugin(
    plugin: InstalledPlugin,
    *,
    parent: QWidget | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="MainWindow.uninstall_plugin" line=2919 %}{% raw %}

</div>

Move a plugin to the system trash after confirming, then restart
Alto.

**Parameters**

- `plugin` (*InstalledPlugin*): The plugin selected in the Plugins dialog.
- `parent` (*QWidget or None, default None*): The window that owns the confirmation and messages. Defaults to this window. Keyword-only.

**Examples**

```text
Select Viola Instrument Pack in the Plugins dialog and press
Uninstall plugin.
```

### MainWindow.restart_app

<div class="api-signature" markdown="1">

```python
def restart_app(
    *,
    quit_on_failure: bool = False,
) -> None
```

{% endraw %}{% include api-source.html name="MainWindow.restart_app" line=2998 %}{% raw %}

</div>

Launch a fresh copy of the app, then close this one.

**Parameters**

- `quit_on_failure` (*bool*): Close after a failed relaunch if an uninstalled pack's assets are already gone.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> MainWindow().restart_app()  # doctest: +SKIP
```
{% endraw %}
