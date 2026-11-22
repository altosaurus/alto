#!/bin/sh
# Run the full pytest suite before pushing, as GitHub does for code changes.
# GitHub can pass explicit test targets for a documentation-only change.
#
# The tests run on every core at once (pytest-xdist). ALTO_TEST_WORKERS sets the number of processes (default: one per core).
# The performance budgets (marked perf) are left out: they time real operations, so the Performance workflow runs them on a
# machine of their own after each merge, and opens an issue if one is missed. Run them here with `pytest -m perf`.
cd "$(dirname "$0")/.." || exit 1
py=.venv/bin/python
[ -x "$py" ] || py=.venv/Scripts/python.exe
[ -x "$py" ] || py=python
export QT_QPA_PLATFORM=offscreen
workers=${ALTO_TEST_WORKERS:-auto}

if [ "${1:-}" = "--patch-coverage" ]; then
  shift
  base=${ALTO_COVERAGE_BASE:-origin/main}
  if [ -n "${PRE_COMMIT_REMOTE_NAME:-}" ] && [ -n "${PRE_COMMIT_TO_REF:-}" ]; then
    if [ "$(git rev-parse HEAD)" != "$(git rev-parse "$PRE_COMMIT_TO_REF")" ] || ! git diff --quiet HEAD --; then
      echo "Check out the commit being pushed and commit or stash pending changes before measuring its coverage." >&2
      exit 1
    fi
  fi
  if [ -n "${PRE_COMMIT_REMOTE_NAME:-}" ] && [ -n "$(git ls-files --others --exclude-standard -- 'tests/*.py' 'alto/*.py' 'benchmarks/*.py')" ]; then
    echo "The checkout contains untracked application or test modules. Commit or move them before pushing." >&2
    exit 1
  fi
  git merge-base "$base" HEAD >/dev/null || exit 1
  "$py" -m pytest -q -o faulthandler_timeout=120 -n "$workers" --dist worksteal -m "not perf" --cov --cov-report=xml --cov-report=term "$@" || exit $?
  exec "$py" -m diff_cover.diff_cover_tool coverage.xml --compare-branch "$base" --fail-under 100
fi
exec "$py" -m pytest -q -o faulthandler_timeout=120 -n "$workers" --dist worksteal -m "not perf" "$@"
