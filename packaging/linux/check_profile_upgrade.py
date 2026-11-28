#!/usr/bin/env python3
"""Resume a released learner profile in the packaged app."""

import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from collections.abc import Iterator
from contextlib import closing, contextmanager
from datetime import datetime
from pathlib import Path

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib  # noqa: E402

FIXTURE = (
    Path(__file__).resolve().parents[2] / "tests/fixtures/alto-0.0.3/profile"
)
CARD = "165f354b1932dbbcd193"  # E3 on the treble staff.
CLOCK = "2026-11-25 12:02:00"
NOW = datetime.fromisoformat(CLOCK + "+00:00").timestamp()


class Desktop:
    """Operate the controls exposed by the running Qt application."""

    def __init__(self, process: subprocess.Popen) -> None:
        """
        Watch the candidate process during each UI interaction.

        Parameters
        ----------
        process : subprocess.Popen
            The learner's running copy of Alto.
        """
        self.process = process

    def control(self, name: str, *, role: Atspi.Role) -> Atspi.Accessible:
        """
        Wait for a visible control in Alto’s accessibility tree.

        Parameters
        ----------
        name : str
            Accessible name of the control.
        role : Atspi.Role
            Accessible role, such as button or label.

        Returns
        -------
        Atspi.Accessible
            The control in the candidate window.

        Raises
        ------
        RuntimeError
            If Alto exits or the control does not appear.
        """
        deadline = time.monotonic() + 30
        visible = set()
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError(f"Alto exited while waiting for {name}")
            try:
                for app in Atspi.get_desktop(0):
                    if app.get_process_id() != self.process.pid:
                        continue
                    app.clear_cache()
                    pending = list(app)
                    while pending:
                        node = pending.pop()
                        pending.extend(node)
                        if node.get_role() == role and (
                            node.get_state_set().contains(
                                Atspi.StateType.SHOWING,
                            )
                        ):
                            label = node.get_name()
                            visible.add(label)
                            if label == name:
                                return node
            except GLib.Error:
                # Qt may replace the page during a transition.
                pass
            while GLib.MainContext.default().iteration(False):
                pass
            time.sleep(0.1)
        raise RuntimeError(f"Missing {role} {name!r}. Found {visible}")

    def press(
        self,
        name: str,
        *,
        role: Atspi.Role = Atspi.Role.PUSH_BUTTON,
    ) -> None:
        """
        Activate the same control a learner uses.

        Parameters
        ----------
        name : str
            Accessible control name.
        role : Atspi.Role
            Accessible control role.
        """
        control = self.control(name, role=role)
        assert control.do_action(0), f"Could not activate {name}"


@contextmanager
def launch(executable: Path, *, home: Path) -> Iterator[Desktop]:
    """
    Run and close the packaged application on the private X display.

    Parameters
    ----------
    executable : Path
        Candidate executable from the installed Linux archive.
    home : Path
        Disposable profile copy shared across the two launches.

    Yields
    ------
    Desktop
        Controls for the running instance.
    """
    env = {
        **os.environ,
        "ALTO_HOME": str(home),
        "TZ": "UTC",
        "LC_ALL": "C.UTF-8",
        "QT_QPA_PLATFORM": "xcb",
        "QT_LINUX_ACCESSIBILITY_ALWAYS_ON": "1",
        "LD_PRELOAD": "libfaketime.so.1",
        "FAKETIME": CLOCK,
        "FAKETIME_DONT_FAKE_MONOTONIC": "1",
    }
    with subprocess.Popen([executable], env=env) as process:
        try:
            desktop = Desktop(process)
            desktop.control(
                "Note Identification, Notation",
                role=Atspi.Role.PUSH_BUTTON,
            )
            yield desktop
            subprocess.run(
                [
                    "xdotool",
                    "search",
                    "--onlyvisible",
                    "--pid",
                    str(process.pid),
                    "--name",
                    "Music Theory",
                    "windowfocus",
                    "key",
                    "ctrl+q",
                ],
                check=True,
            )
            assert process.wait(timeout=15) == 0
        finally:
            if process.poll() is None:
                process.kill()


def check(executable: Path, *, home: Path) -> None:
    """
    Review the released card and verify the learner's history on reopen.

    Parameters
    ----------
    executable : Path
        Packaged Alto executable.
    home : Path
        Fresh destination for the released profile.

    Raises
    ------
    RuntimeError
        If the answer has not been recorded before the timeout.
    """
    shutil.copytree(FIXTURE, home)
    uri = (home / "data/alto.db").as_uri() + "?mode=ro"
    history = (
        "SELECT item_key, answer, correct, answered_at, duration_ms "
        "FROM attempts WHERE profile_id=1 AND exercise='NoteNames' ORDER BY id"
    )
    schedule = (
        "SELECT due FROM review_schedules WHERE profile_id=1 AND "
        "exercise='NoteNames' AND item_key=? AND scheduler='SM-2'"
    )
    with closing(sqlite3.connect(uri, uri=True)) as db:
        original = db.execute(history).fetchall()
    assert len(original) == 1 and original[0][:4] == (CARD, "C", 0, NOW - 120)

    with launch(executable, home=home) as alto:
        with closing(sqlite3.connect(uri, uri=True)) as db:
            assert db.execute(
                "SELECT name, scheduler FROM profiles WHERE id=1",
            ).fetchone() == ("Upgrade Learner", "SM-2")
            assert db.execute(history).fetchall() == original
            assert db.execute(schedule, (CARD,)).fetchall() == [(NOW - 60,)]
        alto.press("Note Identification, Notation")
        alto.press("Exercise settings", role=Atspi.Role.CHECK_BOX)
        alto.press("Clefs")
        for name, checked in (("Treble", True), ("Bass", False)):
            box = alto.control(name, role=Atspi.Role.CHECK_BOX)
            assert (
                box.get_state_set().contains(Atspi.StateType.CHECKED)
                == checked
            )
        alto.press("‹ Back")
        alto.press("Range")
        alto.control("D3 – E7", role=Atspi.Role.LABEL)
        alto.press("Collapse exercise settings")
        alto.press("E")
        # Qt activates an accessible button asynchronously. Let the
        # answer finish before issuing the learner's Quit shortcut.
        deadline = time.monotonic() + 10
        with closing(sqlite3.connect(uri, uri=True)) as db:
            while db.execute(history).fetchall() == original:
                if time.monotonic() >= deadline:
                    raise RuntimeError("Alto did not record the answer")
                time.sleep(0.1)

    with (
        launch(executable, home=home),
        closing(
            sqlite3.connect(uri, uri=True),
        ) as db,
    ):
        reviews = db.execute(history).fetchall()
        assert reviews[:-1] == original, reviews
        assert reviews[-1][:4] == (CARD, "E", 1, NOW), reviews[-1]
        [(due,)] = db.execute(schedule, (CARD,)).fetchall()
        assert due > NOW


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as folder:
        check(Path(sys.argv[1]).resolve(), home=Path(folder) / "learner")
    print("Verified the v0.0.3 learner profile and its resumed review.")
