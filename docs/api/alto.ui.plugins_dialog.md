---
title: alto.ui.plugins_dialog
parent: api
package: alto.ui
permalink: /api/alto.ui.plugins_dialog/
---
{% raw %}
The Plugins dialog: the installed plugins on the left, and the buttons that add or remove one on the right.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from pathlib import Path
>>> PluginsDialog(Path("no-such-plugins-folder")).windowTitle()
'Plugins'
```

## PluginsDialog

```python
PluginsDialog(
    folder: Path,
    *,
    parent: QWidget | None = None,
)
```

Bases: `QDialog`

List the installed plugins and offer to install one from a file or uninstall the selected one.

Registered releases are downloaded in the background. The parent window handles local file installs, removal, and restarts.

**Attributes**

- `folder` (*Path*): The plugins folder that is listed.
- `list` (*QListWidget*): The installed plugins, one row each.
- `install_button` (*QPushButton*): Asks for a plugin to install from a ZIP file.
- `uninstall_button` (*QPushButton*): Asks to remove the selected plugin. Disabled while nothing is selected.
- `empty` (*QLabel*): The message shown inside the list while no plugin is installed.
- `problems` (*QLabel*): Names any plugin that could not be read.
- `install_requested` (*Signal*): Emitted when Install is pressed.
- `uninstall_requested` (*Signal*): Emitted with the selected InstalledPlugin when Uninstall is pressed.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from pathlib import Path
>>> dialog = PluginsDialog(Path("no-such-plugins-folder"))
>>> dialog.list.count(), dialog.uninstall_button.isEnabled()
(0, False)
```

**Constructor**

Build the dialog for the plugins in a folder.

**Parameters**

- `folder` (*Path*): The plugins folder to list.
- `parent` (*QWidget or None, default None*): The widget that owns the dialog. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from pathlib import Path
>>> PluginsDialog(Path("no-such-plugins-folder")).minimumWidth() > 0
True
```

### PluginsDialog.selected

```python
def selected() -> InstalledPlugin | None
```

Return the plugin selected in the list.

**Returns**

- *InstalledPlugin or None*: The selected plugin, or None while nothing is selected.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from pathlib import Path
>>> PluginsDialog(Path("no-such-plugins-folder")).selected() is None
True
```

### PluginsDialog.refresh

```python
def refresh() -> None
```

Read the plugins folder again and keep the same plugin selected if it is still there.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from pathlib import Path
>>> dialog = PluginsDialog(Path("no-such-plugins-folder"))
>>> dialog.refresh()
>>> dialog.empty.isHidden()
False
```

### PluginsDialog.done

```python
def done(result: int) -> None
```

Keep the dialog available until a requested install or update finishes.

**Parameters**

- `result` (*int*): The requested QDialog result.
{% endraw %}
