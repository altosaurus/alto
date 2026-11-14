"""
Start Alto: `python -m alto` opens the main window for the profile that is practising.

Examples
--------
>>> from alto.__main__ import main  # doctest: +SKIP
"""

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from alto.learning import (
    Database,
    Learner,
)
from alto.location import (
    alto_home,
    database_path,
    desktop_name,
)
from alto.ui.main_window import MainWindow
from alto.ui.profile_dialog import startup_profile
from alto.ui.theme import (
    apply_theme,
    saved_theme,
)


def main() -> int:
    """
    Run the application.

    Opens the database in the user's data folder (or in `ALTO_HOME`, if that is set), asks for a profile name the first time,
    shows the main window and runs the event loop until the window is closed.

    Returns
    -------
    int
        The exit code: 0 if the profile dialog was cancelled, otherwise what the event loop returned.

    Examples
    --------
    >>> raise SystemExit(main())  # doctest: +SKIP
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Alto")
    app.setApplicationDisplayName("Alto - Music Theory" if alto_home() is None else "Alto (dev) - Music Theory")
    apply_theme(saved_theme())
    app.setDesktopFileName(desktop_name())  # lets the desktop match the window to alto.desktop (or alto-dev.desktop) and its icon
    app.setWindowIcon(QIcon(str(Path(__file__).parent / "assets" / "icon.svg")))
    db = Database(database_path())
    profile = startup_profile(db)  # asks for a name the first time
    if profile is None:
        return 0
    learner = Learner(db, profile=profile)
    window = MainWindow(learner)
    # noinspection PyUnresolvedReferences
    app.learner = learner  # pyright: ignore[reportAttributeAccessIssue]  (kept on the app so a theme change can swap in a fresh window)
    # noinspection PyUnresolvedReferences
    app.main_window = window  # pyright: ignore[reportAttributeAccessIssue]
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
