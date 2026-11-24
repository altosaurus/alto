"""
Keep the test suite fast: no new fixed waits in tests, except in tests
about timing (the time limit is in conftest.py).
"""

from __future__ import annotations

import ast
from pathlib import Path

TESTS = Path(__file__).resolve().parent
WAITS = ("QTest.qWait", "time.sleep")
ALLOWED_MARKS = ("mark.motion", "mark.slow")

# The fixed waits each file has outside tests marked motion or slow, as
# they were when this check began. Most wait for real
# audio, subprocesses or network timeouts. A file may have fewer; lower
# its number when one goes.
BASELINE = {
    "test_anki_exporter.py": 1,
    "test_app_settings.py": 1,
    "test_audio.py": 19,
    "test_audio_edges.py": 2,
    "test_background.py": 1,
    "test_charts.py": 1,
    "test_exercise_view.py": 10,
    "test_instrument_packs.py": 1,
    "test_key_construction.py": 2,
    "test_keyboard_access.py": 1,
    "test_lessons.py": 2,
    "test_main_window.py": 1,
    "test_navigation.py": 12,
    "test_order_of_keys.py": 3,
    "test_pack_ui_gaps.py": 2,
    "test_package_update.py": 3,
    "test_registered_plugins.py": 1,
    "test_rendering.py": 2,
    "test_settings_panels.py": 1,
    "test_update_flow.py": 4,
    "test_zoom.py": 4,
}


def fixed_waits(path: Path) -> int:
    """
    Count the fixed waits in a test file, leaving out those in tests
    marked motion or slow.

    Each call is counted once, by the function at the top of the file
    that holds it, so a helper defined inside a test is not
    counted twice.

    Parameters
    ----------
    path : Path
        The test file.

    Returns
    -------
    int
        How many `QTest.qWait` and `time.sleep` calls it makes outside
        tests about timing.
    """
    count = 0
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if any(
            mark in ast.unparse(decorator)
            for decorator in node.decorator_list
            for mark in ALLOWED_MARKS
        ):
            continue
        count += sum(
            isinstance(call, ast.Call) and ast.unparse(call.func) in WAITS
            for call in ast.walk(node)
        )
    return count


def test_no_test_gains_a_fixed_wait() -> None:
    """
    Fail when a file has more fixed waits than it had, so the suite does
    not slow down one wait at a time.

    A screen test lets animations and feedback finish with
    `motion.settle()`, which takes no time. A test about how long
    something takes is marked `motion` and may wait.
    """
    grown = {}
    for path in sorted(TESTS.glob("test_*.py")):
        count = fixed_waits(path)
        if count > BASELINE.get(path.name, 0):
            grown[path.name] = (BASELINE.get(path.name, 0), count)
    assert not grown, (
        (
            "These test files wait a fixed time more often than before "
            "(before, now): "
        )
        + ", ".join(
            f"{name} {before} -> {now}"
            for name, (before, now) in grown.items()
        )
        + (
            ". Use motion.settle() to let animations and feedback finish, "
            "or mark a test about timing with @pytest.mark.motion."
        )
    )


def test_the_count_of_fixed_waits_skips_tests_about_timing(
    tmp_path: Path,
) -> None:
    """
    Count the waits in ordinary tests and helpers, once each, and not
    those in tests marked motion or slow.

    Parameters
    ----------
    tmp_path : Path
        A folder for the example file.
    """
    example = tmp_path / "test_example.py"
    example.write_text(
        "import time\n"
        "import pytest\n"
        "def test_a():\n"
        "    def helper():\n"
        "        time.sleep(1)\n"
        "    QTest.qWait(300)\n"
        "    helper()\n"
        "@pytest.mark.motion\n"
        "def test_b():\n"
        "    QTest.qWait(300)\n"
        "def wait():\n"
        "    time.sleep(0.1)\n",
        encoding="utf-8",
    )
    assert fixed_waits(example) == 3
