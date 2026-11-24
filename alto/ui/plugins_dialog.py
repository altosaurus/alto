"""
The Plugins dialog: the installed plugins on the left, and the buttons
that add or remove one on the right.

Examples
--------
>>> from pathlib import Path
>>> PluginsDialog(
...     Path("no-such-plugins-folder")
... ).windowTitle()
'Plugins'
"""

from __future__ import annotations

from html import escape
from pathlib import Path

from PySide6.QtCore import (
    QSize,
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from alto.exercises.packs import (
    InstalledPlugin,
    installed_plugins,
)
from alto.plugin_registry import install_registered
from alto.ui.background import run_in_background
from alto.ui.zoom import px

ROW_HEIGHT = 32  # pixels: one line of text with the list style's padding


class PluginsDialog(QDialog):
    """
    List the installed plugins and offer to install one from a file or
    uninstall the selected one.

    Registered releases are downloaded in the background. The parent
    window handles local file installs, removal, and restarts.

    Attributes
    ----------
    folder : Path
        The plugins folder that is listed.
    list : QListWidget
        The installed plugins, one row each.
    install_button : QPushButton
        Asks for a plugin to install from a ZIP file.
    uninstall_button : QPushButton
        Asks to remove the selected plugin. Disabled while nothing is
        selected.
    empty : QLabel
        The message shown inside the list while no plugin is installed.
    problems : QLabel
        Names any plugin that could not be read.
    install_requested : Signal
        Emitted when Install is pressed.
    uninstall_requested : Signal
        Emitted with the selected InstalledPlugin when Uninstall is
        pressed.

    Examples
    --------
    >>> from pathlib import Path
    >>> dialog = PluginsDialog(
    ...     Path("no-such-plugins-folder")
    ... )
    >>> (
    ...     dialog.list.count(),
    ...     dialog.uninstall_button.isEnabled(),
    ... )
    (0, False)
    """

    restart_requested = Signal()
    install_requested = Signal()
    uninstall_requested = Signal(object)

    def __init__(self, folder: Path, *, parent: QWidget | None = None) -> None:
        """
        Build the dialog for the plugins in a folder.

        Parameters
        ----------
        folder : Path
            The plugins folder to list.
        parent : QWidget or None, default None
            The widget that owns the dialog. Keyword-only.

        Examples
        --------
        >>> from pathlib import Path
        >>> PluginsDialog(
        ...     Path("no-such-plugins-folder")
        ... ).minimumWidth() > 0
        True
        """
        super().__init__(parent)
        self.folder = folder
        self._busy = False
        self.setWindowTitle("Plugins")
        self.setModal(True)
        self.setMinimumSize(px(560), px(340))

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        columns = QHBoxLayout()
        columns.setSpacing(14)

        left = QVBoxLayout()
        left.setSpacing(6)
        heading = QLabel("<b>Installed plugins</b>")
        left.addWidget(heading)
        self.list = QListWidget()
        self.list.setObjectName(
            "categories",
        )  # the rounded list style used in the settings dialog
        self.list.setAccessibleName("Installed plugins")
        self.list.setSpacing(2)
        self.list.currentItemChanged.connect(lambda *_: self._update_buttons())
        self.empty = QLabel("No plugins are installed.", self.list)
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty.setStyleSheet("color: gray; background: transparent;")
        # The message sits inside the list's frame, so the box looks the
        # same with or without plugins.
        frame = QVBoxLayout(self.list)
        frame.addWidget(self.empty)
        left.addWidget(self.list, 1)
        self.problems = QLabel()
        self.problems.setWordWrap(True)
        self.problems.setStyleSheet("color: #c62828;")
        left.addWidget(self.problems)
        columns.addLayout(left, 1)

        right = QVBoxLayout()
        right.setSpacing(8)
        right.addSpacing(
            heading.sizeHint().height() + 6,
        )  # level the first button with the top of the list
        self.code_button = QPushButton("Install plugin by code…")
        self.code_button.clicked.connect(self._ask_code)
        right.addWidget(self.code_button)
        self.install_button = QPushButton("Install plugin from file…")
        self.install_button.setToolTip("Add a downloaded plugin ZIP")
        self.install_button.setAccessibleName("Install plugin from file")
        self.install_button.clicked.connect(self._install)
        right.addWidget(self.install_button)
        self.update_button = QPushButton("Update selected plugin")
        self.update_button.clicked.connect(self._update_selected)
        right.addWidget(self.update_button)
        self.uninstall_button = QPushButton("Uninstall plugin")
        self.uninstall_button.setToolTip(
            "Move the selected plugin to the system trash",
        )
        self.uninstall_button.setAccessibleName("Uninstall plugin")
        self.uninstall_button.clicked.connect(self._uninstall)
        right.addWidget(self.uninstall_button)
        right.addStretch(1)
        columns.addLayout(right)
        layout.addLayout(columns, 1)

        self.status = QLabel()
        self.status.setTextFormat(Qt.TextFormat.PlainText)
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.status.hide()
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.close_button = buttons.button(
            QDialogButtonBox.StandardButton.Close,
        )
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.refresh()

    def selected(self) -> InstalledPlugin | None:
        """
        Return the plugin selected in the list.

        Returns
        -------
        InstalledPlugin or None
            The selected plugin, or None while nothing is selected.

        Examples
        --------
        >>> from pathlib import Path
        >>> PluginsDialog(
        ...     Path("no-such-plugins-folder")
        ... ).selected() is None
        True
        """
        item = self.list.currentItem()
        return None if item is None else item.data(Qt.ItemDataRole.UserRole)

    def refresh(self) -> None:
        """
        Read the plugins folder again and keep the same plugin selected
        if it is still there.

        Examples
        --------
        >>> from pathlib import Path
        >>> dialog = PluginsDialog(
        ...     Path("no-such-plugins-folder")
        ... )
        >>> dialog.refresh()
        >>> dialog.empty.isHidden()
        False
        """
        keep = self.selected()
        plugins, problems = installed_plugins(self.folder)
        self.list.clear()
        for plugin in plugins:
            item = QListWidgetItem(plugin.title)
            item.setData(Qt.ItemDataRole.UserRole, plugin)
            item.setToolTip(str(plugin.path))
            item.setSizeHint(
                QSize(0, px(ROW_HEIGHT)),
            )  # room for the name, the same for every row
            self.list.addItem(item)
            if keep is not None and plugin.path == keep.path:
                self.list.setCurrentItem(item)
        if plugins and self.list.currentItem() is None:
            self.list.setCurrentRow(0)
        self.empty.setVisible(not plugins)
        self.problems.setText("\n".join(problems))
        self.problems.setVisible(bool(problems))
        self._update_buttons()

    def _update_buttons(self) -> None:
        """
        Allow Uninstall only while a plugin is selected.

        Examples
        --------
        >>> from pathlib import Path
        >>> dialog = PluginsDialog(
        ...     Path("no-such-plugins-folder")
        ... )
        >>> dialog._update_buttons()
        >>> dialog.uninstall_button.isEnabled()
        False
        """
        selected = self.selected()
        self.code_button.setEnabled(not self._busy)
        self.install_button.setEnabled(not self._busy)
        self.close_button.setEnabled(not self._busy)
        self.update_button.setEnabled(
            not self._busy
            and selected is not None
            and selected.path == selected.manifest
            and not selected.path.is_symlink(),
        )
        self.uninstall_button.setEnabled(
            not self._busy and selected is not None,
        )

    def done(self, result: int) -> None:
        """
        Keep the dialog available until a requested install or update
        finishes.

        Parameters
        ----------
        result : int
            The requested QDialog result.
        """
        if not self._busy:
            super().done(result)

    def _ask_code(self) -> None:
        """
        Start an installation when the user submits a registration code.
        """
        code, accepted = QInputDialog.getText(
            self,
            "Install plugin by code",
            "Registration code",
        )
        if accepted and code.strip():
            self._start_release(code, selected=None)

    def _update_selected(self) -> None:
        """
        Check the current ZIP against the latest release in its
        registered repository.
        """
        selected = self.selected()
        if selected is not None:
            self._start_release("", selected=selected)

    def _start_release(
        self,
        code: str,
        *,
        selected: InstalledPlugin | None,
    ) -> None:
        """
        Resolve and install the release on a worker while the dialog
        remains responsive.
        """
        self._busy = True
        self._update_buttons()
        self.status.setText(
            "Checking the plugin registry and downloading the latest release…",
        )
        self.status.show()

        run_in_background(
            lambda: install_registered(
                code,
                folder=self.folder,
                selected=selected,
            ),
            owner=self,
            done=lambda result: self._finish_release(result, ""),
            failed=lambda error: self._finish_release(None, str(error)),
        )

    def _finish_release(self, result: str | None, error: str) -> None:  # noqa: PLR0917 (Qt signal arguments)
        """
        Show the result, refresh the installed list, and offer a restart
        after a change.
        """
        self._busy = False
        self.refresh()
        if error:
            self.status.setText(error)
        elif result is None:
            self.status.setText("This plugin is already up to date.")
        else:
            self.status.setText(
                f"Installed {result}. Restart Alto to use this release.",
            )
            answer = QMessageBox.question(
                self,
                "Plugin installed",
                f"<p>Installed {escape(result)}. Restart Alto now?</p>",
            )
            if answer == QMessageBox.StandardButton.Yes:
                self.restart_requested.emit()

    def _install(self) -> None:
        """
        Ask for a plugin to be installed, then show the folder as it is
        afterwards.

        Examples
        --------
        >>> from pathlib import Path
        >>> dialog = PluginsDialog(
        ...     Path("no-such-plugins-folder")
        ... )
        >>> dialog._install()
        >>> dialog.list.count()
        0
        """
        self.install_requested.emit()
        self.refresh()

    def _uninstall(self) -> None:
        """
        Ask for the selected plugin to be uninstalled, then show the
        folder as it is afterwards.

        Examples
        --------
        >>> from pathlib import Path
        >>> dialog = PluginsDialog(
        ...     Path("no-such-plugins-folder")
        ... )
        >>> # nothing selected, so nothing is requested
        >>> dialog._uninstall()
        """
        plugin = self.selected()
        if plugin is not None:
            self.uninstall_requested.emit(plugin)
            self.refresh()
