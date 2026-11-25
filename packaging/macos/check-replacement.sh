#!/bin/sh
# Run the recipient's library-replacement procedure on a disposable app.
set -eu
original=$1
work=$2
python=$3
app="$work/modified/Alto.app"
mkdir "$work/modified"
ditto "$original" "$app"
core="$app/Contents/Frameworks/PySide6/Qt/lib/QtCore.framework/Versions/A/QtCore"
expected=$("$python" - "$core" <<'PY'
from pathlib import Path
import sys
from PySide6.QtCore import qVersion

path = Path(sys.argv[1])
data = path.read_bytes()
version = qVersion().encode()
modified = version[:-1] + (b"1" if version[-1:] == b"0" else b"0")
original = b"\0" + version + b"\0"
assert data.count(original) == 1, "Review the native qVersion string"
path.write_bytes(data.replace(original, b"\0" + modified + b"\0"))
print(modified.decode())
PY
)
cat >> "$app/Contents/Resources/PySide6/__init__.py" <<'PY'

# Exists only in the disposable replacement test.
from PySide6.QtCore import qVersion
print("Modified PySide6 loaded Qt", qVersion(), flush=True)
PY
codesign --force --deep --sign - --timestamp=none "$app"
codesign --verify --deep --strict "$app"
output=$("$app/Contents/MacOS/alto" --self-test)
echo "$output"
echo "$output" | grep -Fx "Modified PySide6 loaded Qt $expected"
echo "$output" | grep -Fx ok

# Exercise the same WAV playback API used by Alto from the modified app.
cat >> "$app/Contents/Resources/PySide6/__init__.py" <<'PY'
from pathlib import Path
from PySide6.QtCore import QEventLoop, QTimer, QUrl
from PySide6.QtWidgets import QApplication
from PySide6.QtMultimedia import QMediaDevices, QSoundEffect

application = QApplication([])
sample = Path(__file__).resolve().parents[1] / "alto/assets/metronome/high-pip.wav"
effect = QSoundEffect()
effect.setSource(QUrl.fromLocalFile(str(sample)))
if QMediaDevices.defaultAudioOutput().isNull():
    print("No audio output on this runner. Physical playback remains a Mac hardware check.")
else:
    loop = QEventLoop()
    played = []
    def record_playback():
        played.append(effect.isPlaying())
        if played == [True, False]:
            loop.quit()
    effect.playingChanged.connect(record_playback)
    QTimer.singleShot(15000, loop.quit)
    effect.play()
    loop.exec()
    assert effect.status() == QSoundEffect.Status.Ready and played == [True, False], played
    print("Completed playback of Alto's bundled metronome sample.")
PY
codesign --force --deep --sign - --timestamp=none "$app"
"$app/Contents/MacOS/alto" --self-test
