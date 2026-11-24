#!/bin/sh
# Compare all application modules together so a change can match code in an unchanged file.
cd "$(dirname "$0")/.." || exit 1
py=.venv/bin/python
[ -x "$py" ] || py=.venv/Scripts/python.exe
[ -x "$py" ] || py=python
exec "$py" -m pylint --disable=all --enable=R0801 --reports=n --score=n --persistent=n alto
