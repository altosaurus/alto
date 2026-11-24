"""
Time every operation once, and print the table: `python -m
benchmarks.survey`.
"""

from __future__ import annotations

import sys

from benchmarks.operations import (
    Workbench,
    isolate,
    measure,
)


def main() -> None:
    """
    Measure each operation, slowest first, and print how long it took in
    milliseconds.
    """
    isolate()
    bench = Workbench()
    rows = []
    for name, operation in bench.operations.items():
        try:
            rows.append((measure(operation) * 1000, name))
        except Exception as error:  # noqa: BLE001  (the survey says what failed and goes on)
            print(f"FAILED {name}: {error!r}", file=sys.stderr)
    for milliseconds, name in sorted(rows, reverse=True):
        print(f"{milliseconds:9.2f} ms  {name}")
    bench.close()


if __name__ == "__main__":
    main()
