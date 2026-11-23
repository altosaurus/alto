"""
Start Alto: `python -m alto` opens the main window for the profile that is practicing.

Examples
--------
>>> from alto.__main__ import main  # doctest: +SKIP
"""

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from alto.exercises.packs import load_packs
from alto.learning import (
    Database,
    Learner,
)
from alto.learning.backup import app_version
from alto.location import (
    alto_home,
    database_path,
    desktop_name,
)
from alto.ui import (
    warmup,
    zoom,
)
from alto.ui.main_window import MainWindow
from alto.ui.profile_dialog import startup_profile
from alto.ui.theme import (
    apply_theme,
    saved_theme,
)
from alto.ui.update_flow import DailyReleaseCheck
from alto.updates import self_check


def main() -> int:
    """
    Run the application.

    Opens the database in the user's data folder (or in `ALTO_HOME`, if that is set), asks for a profile name the first time,
    shows the main window and runs the event loop until the window is closed.

    `alto --version` prints the version and exits without opening anything. A packaged build has no console on Windows, so there
    is nowhere to print to; it still exits with 0, which shows that everything it needs was found.

    `alto --self-test` checks, offline, that what an update needs is there: the certificate list, the signature check and the
    keys. It prints `ok` and exits with 0, or says what is wrong and exits with 1. The build runs it on a packaged copy.

    Returns
    -------
    int
        The exit code: 0 if the profile dialog was canceled or the version was asked for, otherwise what the event loop returned.

    Examples
    --------
    >>> raise SystemExit(main())  # doctest: +SKIP
    """
    if "--version" in sys.argv[1:]:
        if sys.stdout is not None:  # a program with no console, such as the Windows build, has none
            print(f"Alto {app_version()}")
        return 0
    if "--self-test" in sys.argv[1:]:
        problems = self_check()
        if sys.stdout is not None:
            print("ok" if not problems else "\n".join(problems))
        return 1 if problems else 0
    app = QApplication(sys.argv)
    app.setApplicationName("Alto")
    app.setApplicationDisplayName("Alto - Music Theory" if alto_home() is None else "Alto (dev) - Music Theory")
    zoom.load()  # before the theme, whose stylesheet is scaled by it
    apply_theme(saved_theme())
    app.setDesktopFileName(desktop_name())  # lets the desktop match the window to alto.desktop (or alto-dev.desktop) and its icon
    app.setWindowIcon(QIcon(str(Path(__file__).parent / "assets" / "icon.svg")))
    db = Database(database_path())
    profile = startup_profile(db)  # asks for a name the first time
    if profile is None:
        return 0
    learner = Learner(db, profile=profile)
    problems = load_packs(database_path().parent / "plugins")
    window = MainWindow(learner)
    # noinspection PyUnresolvedReferences
    app.learner = learner  # pyright: ignore[reportAttributeAccessIssue]  (kept on the app so a theme change can swap in a fresh window)
    # noinspection PyUnresolvedReferences
    app.main_window = window  # pyright: ignore[reportAttributeAccessIssue]
    window.show()
    warmup.start(window)  # get the fonts the pages need ready while the window sits idle
    if problems:
        QMessageBox.warning(window, "Plugin loading", "Alto skipped these packs.\n\n" + "\n".join(problems))
    DailyReleaseCheck(window)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
