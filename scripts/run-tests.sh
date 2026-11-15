#!/bin/sh
# Run the tests for the pre-push hook, using the project's virtual environment if there is one.
# Only the tests that the change could affect run (see scripts/changed_tests.py); ALTO_TEST_ALL=1 runs them all.
# The widget tests use Qt's offscreen platform, so no display is needed.
cd "$(dirname "$0")/.." || exit 1
py=.venv/bin/python
[ -x "$py" ] || py=.venv/Scripts/python.exe
[ -x "$py" ] || py=python
export QT_QPA_PLATFORM=offscreen
if [ "${ALTO_TEST_ALL:-0}" = 1 ]; then
  exec "$py" -m pytest -q
fi
targets=$("$py" scripts/changed_tests.py) || exec "$py" -m pytest -q
if [ "$targets" = all ]; then
  exec "$py" -m pytest -q
elif [ -z "$targets" ]; then
  echo "Nothing has changed since origin/main, so there is nothing to test."
else
  echo "Running the tests the change could affect (ALTO_TEST_ALL=1 runs them all):"
  # shellcheck disable=SC2086
  exec "$py" -m pytest -q $targets
fi
