---
title: alto.ui.main_window
parent: api
package: alto.ui
permalink: /api/alto.ui.main_window/
---
{% raw %}
The main window: tile browsing or a workspace with an independently selected exercise or lesson list.

Navigation stays on the left of the top bar, with data tools on the right. Browsing tiles retains the active activity.

**Examples**

```pycon
>>> window = MainWindow()
>>> window.title_label.text()
'Alto - Music Theory'
```

## default_size

```python
def default_size() -> tuple[int, int]
```

Return the size a new window opens at.

It is big enough for a lesson step, with its circle, to show without scrolling, but never more than most of the screen.

**Returns**

- *tuple of (int, int)*: The width and height in pixels.

**Examples**

```pycon
>>> width, height = default_size()
>>> 0 < width <= DEFAULT_WIDTH and 0 < height <= DEFAULT_HEIGHT
True
```

## MainWindow

```python
MainWindow(learner: Learner | None = None)
```

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

```pycon
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

```pycon
>>> from alto.learning import Database
>>> db = Database()
>>> window_ = MainWindow(Learner(db, profile=db.add_profile("Ada")))
>>> window_.stats_button.isVisibleTo(window_)
True
>>> MainWindow().stats_button.isVisibleTo(window_)  # no profile, no statistics
False
```

### MainWindow.closeEvent

```python
def closeEvent(event: QCloseEvent) -> None
```

Remember the window's size and position when the app closes.

**Parameters**

- `event` (*QCloseEvent*): The window close event.

**Examples**

```pycon
>>> closeEvent()  # doctest: +SKIP
```

### MainWindow.eventFilter

```python
def eventFilter(
    watched: QObject,
    event: QEvent,
) -> bool
```

Highlight the search field's outline while it has keyboard focus.

**Parameters**

- `watched` (*QObject*): The search field.
- `event` (*QEvent*): The event being delivered.

**Returns**

- *bool*: Whether the base window consumes the event; focus changes are allowed through.

**Examples**

```pycon
>>> window = MainWindow()
>>> window.eventFilter(window.search_field, QEvent(QEvent.Type.FocusIn))
False
>>> window.search_row.property("focusWithin")
True
```

### MainWindow.sidebar_width

```python
def sidebar_width() -> int
```

Return how wide the exercise list is.

**Returns**

- *int*: The width in pixels; 0 when the list is collapsed, as it always is on the start screen.

**Examples**

```pycon
>>> MainWindow().sidebar_width()
0
```

### MainWindow.toggle_sidebar

```python
def toggle_sidebar() -> None
```

Slide the list closed, or back open, for the user's button. The choice is remembered for next time.

**Examples**

```pycon
>>> window = MainWindow()
>>> window.toggle_sidebar()
>>> window._sidebar_pref
True
```

### MainWindow.open_exercise

```python
def open_exercise(cls: type[Exercise] | None) -> None
```

Show an exercise.

**Parameters**

- `cls` (*type of Exercise or None*): The exercise class; None (a category heading in the list, which has no class) does nothing.

**Examples**

```pycon
>>> from alto.exercises.library import KeySignatures
>>> window = MainWindow()
>>> window.open_exercise(KeySignatures)
>>> window.title_label.text()
'Key Signature Identification'
```

### MainWindow.show_about

```python
def show_about() -> None
```

Show the application name, installed version and purpose.

**Examples**

```pycon
>>> window.show_about()  # doctest: +SKIP
```

### MainWindow.open_settings

```python
def open_settings() -> None
```

Open the application settings without blocking the window, or bring them forward if they are already open.

If the theme was changed, the window is rebuilt in it once the settings are closed.

**Examples**

```pycon
>>> window = MainWindow()
>>> window.open_settings()
>>> # noinspection PyUnresolvedReferences
>>> window._settings is not None and not window._settings.isModal()
True
>>> # noinspection PyUnresolvedReferences
>>> window._settings.close()
True
```

### MainWindow.rebuild

```python
def rebuild() -> None
```

Make the window's contents again in the same window, so every icon and color is drawn in the new theme.

The window itself stays, so it does not vanish and reappear. The page that was open is shown again, with the list
already open or closed as it was, not sliding.

**Examples**

```pycon
>>> window = MainWindow()
>>> old_root = window.centralWidget()
>>> window.rebuild()
>>> window.centralWidget() is old_root
False
```

### MainWindow.open_glossary

```python
def open_glossary() -> None
```

Toggle the glossary from its toolbar button.

**Examples**

```pycon
>>> open_glossary()  # doctest: +SKIP
```

### MainWindow.open_stats

```python
def open_stats() -> None
```

Show the statistics in place of the current page. Nothing happens without a profile.

**Examples**

```pycon
>>> from alto.learning import Database
>>> db = Database()
>>> window = MainWindow(Learner(db, profile=db.add_profile("Ada")))
>>> window.open_stats()
>>> window.title_label.text()
'Statistics'
>>> window.close_overlay()
```

### MainWindow.toggle_navigation

```python
def toggle_navigation() -> None
```

Open the workspace from tiles, or toggle its navigation pane without leaving the activity.

**Examples**

```pycon
>>> window = MainWindow()
>>> window.toggle_navigation()
>>> window.stack.currentWidget() is window.empty_page, window.view_button.accessibleName()
(True, 'Tiles')
```

### MainWindow.show_lessons

```python
def show_lessons() -> None
```

Go to the start screen showing the lessons.

**Examples**

```pycon
>>> window = MainWindow()
>>> window.show_lessons()
>>> window.home.mode
'lessons'
>>> window.home.set_mode("exercises")
```

### MainWindow.open_lessons

```python
def open_lessons(lesson: str) -> None
```

Open a lesson in place of the current page, at the step it was left at, with the lesson list on the left.

**Parameters**

- `lesson` (*str*): The key of the lesson.

**Examples**

```pycon
>>> window = MainWindow()
>>> window.open_lessons("circle-of-fifths")
>>> window.title_label.text(), window.nav_stack.currentWidget() is window.lesson_nav
('The Circle of Fifths', True)
>>> window.close_overlay()
```

### MainWindow.open_database

```python
def open_database() -> None
```

Show the database browser in place of the current page. Nothing happens without a profile.

**Examples**

```pycon
>>> from alto.learning import Database
>>> db = Database()
>>> window = MainWindow(Learner(db, profile=db.add_profile("Ada")))
>>> window.open_database()
>>> window.title_label.text()
'Database'
>>> window.close_overlay()
```

### MainWindow.close_overlay

```python
def close_overlay() -> None
```

Leave the statistics or database page and show the page that was open before it.

**Examples**

```pycon
>>> from alto.learning import Database
>>> db = Database()
>>> window = MainWindow(Learner(db, profile=db.add_profile("Ada")))
>>> window.open_stats()
>>> window.close_overlay()
>>> window.title_label.text()
'Alto - Music Theory'
```

### MainWindow.switch_profile

```python
def switch_profile() -> None
```

Choose or add a profile.

Their history and questions are kept apart; the next question comes from theirs.

**Examples**

```pycon
>>> window = MainWindow()
>>> window.switch_profile()  # without a profile there is nothing to switch
```

### MainWindow.export_backup

```python
def export_backup() -> None
```

Save a backup of everything: ask where, then write profiles, history and settings to one file.

**Examples**

```pycon
>>> MainWindow().export_backup()  # does nothing without a profile
```

### MainWindow.check_for_updates

```python
def check_for_updates() -> None
```

Ask whether a newer Alto is available; if so and the person agrees, install it and restart.

**Examples**

```pycon
>>> MainWindow().check_for_updates()  # doctest: +SKIP
```

### MainWindow.import_backup

```python
def import_backup() -> None
```

Replace everything with a backup: ask for the file, check it, ask again, and reload the whole window from it.

**Examples**

```pycon
>>> MainWindow().import_backup()  # does nothing without a profile
```

### MainWindow.show_home

```python
def show_home() -> None
```

Go back to the start screen, closing the statistics or database and hiding the exercise list.

**Examples**

```pycon
>>> from alto.exercises.library import NoteNames
>>> window = MainWindow()
>>> window.open_exercise(NoteNames)
>>> window.show_home()
>>> window.title_label.text()
'Alto - Music Theory'
```

### MainWindow.restart_app

```python
def restart_app() -> None
```

Launch a fresh copy of the app, then close this one.

**Examples**

```pycon
>>> MainWindow().restart_app()  # doctest: +SKIP
```
{% endraw %}
