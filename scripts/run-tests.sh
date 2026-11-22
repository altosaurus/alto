#!/bin/sh
# Run the full pytest suite before pushing, as GitHub does for code changes.
# GitHub can pass explicit test targets for a documentation-only change.
#
# The tests run on every core at once (pytest-xdist), except the performance budgets, which time real operations and so
# run afterwards on their own, on a quiet machine. ALTO_TEST_WORKERS sets the number of processes (default: one per core).
cd "$(dirname "$0")/.." || exit 1
py=.venv/bin/python
[ -x "$py" ] || py=.venv/Scripts/python.exe
[ -x "$py" ] || py=python
export QT_QPA_PLATFORM=offscreen
workers=${ALTO_TEST_WORKERS:-auto}

# Run pytest twice: everything but the budgets in parallel, then the budgets alone. A run that finds no tests to run (exit 5,
# when the targets have no budgets in them) is not a failure.
run_suite() {
  "$py" -m pytest -q -o faulthandler_timeout=120 -n "$workers" --dist worksteal -m "not perf" "$@" || return $?
  "$py" -m pytest -q -o faulthandler_timeout=120 -m perf "$@"
  status=$?
  [ "$status" -eq 5 ] && return 0
  return "$status"
}

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
  "$py" -m pytest -q -o faulthandler_timeout=120 -n "$workers" --dist worksteal -m "not perf" --cov --cov-report= "$@" || exit $?
  "$py" -m pytest -q -o faulthandler_timeout=120 -m perf --cov --cov-append --cov-report=xml --cov-report=term "$@"
  status=$?
  if [ "$status" -eq 5 ]; then  # no budgets among the targets: report the coverage of the parallel run alone
    "$py" -m coverage xml -q && "$py" -m coverage report >/dev/null || exit $?
  elif [ "$status" -ne 0 ]; then
    exit "$status"
  fi
  exec "$py" -m diff_cover.diff_cover_tool coverage.xml --compare-branch "$base" --fail-under 100
fi
run_suite "$@"
