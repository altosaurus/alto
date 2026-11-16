"""Sound: the synthesised and recorded instruments, the engine that plays notes, and the volume and fade rules."""

from __future__ import annotations

import io
import os
import time
import wave
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from PySide6.QtCore import QTimer
from PySide6.QtMultimedia import (
    QAudioFormat,
    QAudioSink,
    QSoundEffect,
)
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from alto import audio as audio_module
from alto.audio import (
    ASSET_DIR,
    INSTRUMENT_BY_KEY,
    INSTRUMENTS,
    SAMPLE_RATE,
    Sounds,
    instrument_groups,
    read_wav,
    shift_pitch,
    synth_piano,
    to_wav_bytes,
)
from alto.theory.pitch import Note


def test_melody_highlights_follow_the_audio_clock(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Follow processed audio frames through delayed starts and underruns rather than wall-clock guesses.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    tmp_path : Path
        The rendered clip location.
    monkeypatch : pytest.MonkeyPatch
        Replaces the audio clock and output hardware.
    """
    player = Sounds()
    fmt = QAudioFormat()
    fmt.setSampleRate(SAMPLE_RATE)
    fmt.setChannelCount(1)
    fmt.setSampleFormat(QAudioFormat.SampleFormat.Int16)
    monkeypatch.setattr(
        audio_module.QMediaDevices,
        "defaultAudioOutput",
        lambda: SimpleNamespace(preferredFormat=lambda: fmt),
    )
    sink = QAudioSink(fmt)
    position = [0]
    calls: list[str] = []
    seen: list[int | None] = []
    path = tmp_path / "scale.wav"
    path.write_bytes(to_wav_bytes(np.zeros(SAMPLE_RATE)))
    monkeypatch.setattr(audio_module, "QAudioSink", lambda _format: sink)
    monkeypatch.setattr(sink, "error", lambda: type("NoError", (), {"value": 0})())
    monkeypatch.setattr(sink, "processedUSecs", lambda: position[0])
    monkeypatch.setattr(sink, "start", lambda _buffer: calls.append("play"))
    monkeypatch.setattr(sink, "stop", lambda: calls.append("stop"))
    monkeypatch.setattr(sink, "deleteLater", lambda: None)
    monkeypatch.setattr(player, "_preview_file", lambda *_args, **_kwargs: path)
    player.play_melody([60, 62], gap_ms=280, on_step=seen.append)
    timer = sink.findChild(QTimer)
    assert timer is not None and calls == ["play"] and not seen
    position[0] = 1
    timer.timeout.emit()
    assert seen == [0]
    # A stalled device must not move the highlight, regardless of timer ticks.
    timer.timeout.emit()
    assert seen == [0]
    position[0] = 280_000
    timer.timeout.emit()
    assert seen == [0, 1]
    position[0] = 560_000
    timer.timeout.emit()
    assert seen == [0, 1, None] and not timer.isActive()
    player.stop_all()
    assert calls == ["play", "stop"]


def test_muted_melody_has_the_same_visual_steps_and_cancels_old_callbacks(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Animate without loading audio and ignore steps from a replaced melody.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Captures scheduled steps without waiting in real time.
    """
    player = Sounds()
    player.enabled = False
    pending: list[Callable[[], object]] = []
    old: list[int | None] = []
    current: list[int | None] = []
    monkeypatch.setattr(audio_module.QTimer, "singleShot", lambda _delay, callback: pending.append(callback))
    monkeypatch.setattr(player, "_preview_file", lambda *_args, **_kwargs: pytest.fail("muted melody loaded audio"))
    player.play_melody([60, 62], gap_ms=280, on_step=old.append)
    player.play_melody([64], gap_ms=280, on_step=current.append)
    while pending:
        pending.pop(0)()
    assert old == [0] and current == [0, None]


def test_melody_tail_extends_only_the_last_note(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Keep note onsets fixed while allowing the final note an additional 200 ms before its fade.

    Parameters
    ----------
    tmp_path : Path
        The audio cache directory.
    monkeypatch : pytest.MonkeyPatch
        Supplies a sustained test recording.
    """
    player = Sounds()
    player._dir = tmp_path
    recording = tmp_path / "note.wav"
    recording.write_bytes(to_wav_bytes(np.full(SAMPLE_RATE, 0.1)))
    monkeypatch.setattr(player, "_note_file", lambda *_args, **_kwargs: recording)
    inst = INSTRUMENT_BY_KEY["piano"]
    short = player._preview_file(inst, midis=(60, 62), step_ms=280)
    ringing = player._preview_file(inst, midis=(60, 62), step_ms=280, tail_ms=200)
    original, rate = read_wav(short)
    extended, _ = read_wav(ringing)
    assert short != ringing and len(extended) - len(original) == rate // 5
    assert np.allclose(original[: rate * 280 // 1000], extended[: rate * 280 // 1000])
    assert extended[rate * 750 // 1000] > 0.09
    assert abs(extended[-1]) < 0.001


@pytest.mark.parametrize(
    "kind",
    [
        QAudioFormat.SampleFormat.Float,
        QAudioFormat.SampleFormat.Int32,
        QAudioFormat.SampleFormat.Int16,
        QAudioFormat.SampleFormat.UInt8,
    ],
)
def test_melody_converts_to_the_device_format(
    tmp_path: Path,
    kind: QAudioFormat.SampleFormat,
) -> None:
    """
    Convert 44.1 kHz mono recordings to 48 kHz stereo in each supported device sample format.

    Parameters
    ----------
    tmp_path : Path
        The test recording directory.
    kind : QAudioFormat.SampleFormat
        The output sample representation.
    """
    path = tmp_path / "mono.wav"
    path.write_bytes(to_wav_bytes(np.full(SAMPLE_RATE, 0.25)))
    fmt = QAudioFormat()
    fmt.setSampleRate(48000)
    fmt.setChannelCount(2)
    fmt.setSampleFormat(kind)
    pcm = Sounds._output_pcm(path, audio_format=fmt)
    assert len(pcm) == 48000 * fmt.bytesPerFrame()
    frames = np.frombuffer(pcm, dtype=np.uint8).reshape(48000, 2, fmt.bytesPerSample())
    assert np.array_equal(frames[:, 0], frames[:, 1])
    assert np.any(frames)
    if kind == QAudioFormat.SampleFormat.Int32:
        assert np.frombuffer(pcm, dtype=np.int32)[0] / 2147483647 == pytest.approx(0.25, abs=0.0001)


def test_synth_is_normalized_and_finite() -> None:
    """
    Check that synth is normalized and finite.
    """
    for midi in (
        36,
        60,
        72,
        84,
    ):
        s = synth_piano(midi)
        assert np.isfinite(s).all()
        assert 0.5 < np.max(np.abs(s)) <= 0.8001


def test_dominant_frequency_matches_pitch() -> None:
    """
    Check that dominant frequency matches pitch.
    """
    s = synth_piano(69)[: SAMPLE_RATE // 2]  # A4 = 440 Hz
    spectrum = np.abs(np.fft.rfft(s))
    assert abs(np.argmax(spectrum) * SAMPLE_RATE / len(s) - 440) < 3


def test_wav_roundtrip() -> None:
    """
    Test wav roundtrip.
    """
    with wave.open(io.BytesIO(to_wav_bytes(synth_piano(60)))) as w:
        assert w.getframerate() == SAMPLE_RATE and w.getnchannels() == 1


def test_every_bundled_piano_file_is_a_usable_recording() -> None:
    """
    Check that every bundled piano file is a mono recording at the engine's sample rate, long enough and not silent.
    """
    files = list(ASSET_DIR.glob("*.wav"))
    assert len(files) == 30  # one every minor third, A0 to C8
    for path in files:
        with wave.open(str(path)) as w:
            assert w.getnchannels() == 1 and w.getframerate() == SAMPLE_RATE, path.name
            frames = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")
        assert frames.size > SAMPLE_RATE and np.abs(frames).max() > 1000, path.name


def test_every_instrument_has_recordings_and_covers_the_notes() -> None:
    """
    Check that every instrument has recordings and covers the notes.
    """
    assert len(INSTRUMENTS) >= 7 and INSTRUMENTS[0].key == "piano"
    # instruments whose recordings ship with Alto; any other is still being sourced
    shipped = {
        "piano",
        "marimba",
        "vibraphone",
        "viola_bowed",
        "viola_plucked",
        "flute",
        "horn",
    }
    sounds = Sounds()
    for inst in INSTRUMENTS:
        files = sounds._samples(inst)
        if not files and inst.key not in shipped:
            continue  # no recordings yet: these notes play as the synthesized piano
        assert len(files) >= 15, inst.key
        for midi, path in list(files.items())[:3]:
            audio, rate = read_wav(path)
            assert np.isfinite(audio).all() and np.abs(audio).max() > 0.05 and len(audio) > rate // 2, (inst.key, midi)
        # any staff note gets a file: a recording or a pitch-shifted neighbour
        for midi in (
            40,
            61,
            73,
            90,
        ):
            assert sounds._note_file(inst, midi=midi).exists(), (inst.key, midi)


def test_the_piano_is_recorded_across_the_whole_keyboard() -> None:
    """
    Check that every key from A0 to C8 has a recording or lies within a semitone of one, so none is synthesized.
    """
    have = Sounds().recordings(INSTRUMENT_BY_KEY["piano"])
    assert min(have) == 21 and max(have) == 108
    for midi in range(21, 109):
        assert min(abs(m - midi) for m in have) <= 1, midi


def test_pitch_shift_moves_the_frequency() -> None:
    """
    Check that pitch shift moves the frequency.
    """
    t = np.arange(SAMPLE_RATE) / SAMPLE_RATE
    tone = np.sin(2 * np.pi * 440 * t)
    shifted = shift_pitch(tone, semitones=2)  # up a whole tone: ~493.9 Hz
    peak = np.argmax(np.abs(np.fft.rfft(shifted))) * SAMPLE_RATE / len(shifted)
    assert abs(peak - 493.9) < 3


# -- sustained and ringing notes ------------------------------------------------------------------------------------


class FakeEffect:
    """Stands in for QSoundEffect, so these tests need no audio hardware."""

    def __init__(
        self,
        label: str,
        *,
        log: list[object],
    ) -> None:
        """
        Build the effect.

        Parameters
        ----------
        label : str
            A name for this effect, used in the log.
        log : list of object
            Where every play, stop and release is recorded.
        """
        self.label, self.log, self._volume = label, log, 1.0

    # noinspection PyPep8Naming
    def setVolume(self, v: float) -> None:
        """
        Set the volume, as QSoundEffect does.

        Parameters
        ----------
        v : float
            The volume, 0 to 1.
        """
        self._volume = v

    def volume(self) -> float:
        """
        Return the volume.

        Returns
        -------
        float
            The volume last set.
        """
        return self._volume

    def play(self) -> None:
        """
        Record that the effect was played.
        """
        self.log.append(("play", self.label))

    def stop(self) -> None:
        """
        Record that the effect was stopped.
        """
        self.log.append(("stop", self.label))


def engine(
    monkeypatch: pytest.MonkeyPatch,
    *,
    instrument: str,
) -> tuple[Sounds, list[object]]:
    """
    Build a sound engine whose effects are fakes that record what happens to them.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Swaps in the fake effects.
    instrument : str
        The instrument to play.

    Returns
    -------
    tuple of Sounds and list of object
        The engine, and the log of plays, stops and releases.
    """
    log, effects = [], {}
    s = Sounds()
    s.instrument = instrument
    monkeypatch.setattr(s, "_effect", lambda inst, midi: effects.setdefault(midi, FakeEffect(midi, log=log)))
    monkeypatch.setattr(s, "_release", lambda fx: log.append(("release", fx.label)))
    return s, log


def test_only_bowed_and_blown_instruments_are_sustained() -> None:
    """
    Check that only bowed and blown instruments are sustained.
    """
    sustained = {k for k, i in INSTRUMENT_BY_KEY.items() if i.sustained}
    assert {"viola_bowed", "flute", "horn"} <= sustained
    assert not sustained & {
        "piano",
        "marimba",
        "vibraphone",
        "viola_plucked",
    }


def test_a_bowed_note_ends_when_the_next_one_begins(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that a bowed note ends when the next one begins.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    s, log = engine(monkeypatch, instrument="viola_bowed")
    s.play_midi(60)
    s.play_midi(62)
    assert log == [("play", 60), ("release", 60), ("play", 62)]


def test_struck_and_plucked_notes_ring_on(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that struck and plucked notes ring on.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    for instrument in (
        "marimba",
        "vibraphone",
        "viola_plucked",
    ):
        s, log = engine(monkeypatch, instrument=instrument)
        s.play_midi(60)
        s.play_midi(62)
        assert log == [("play", 60), ("play", 62)], instrument


def test_a_piano_played_without_the_pedal_stops_each_note_as_the_next_begins(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that a piano note is damped when the next one starts, as if the damper pedal were up, and a chord is not cut short.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    s, log = engine(monkeypatch, instrument="piano")
    s.play_midi(60)
    s.play_midi(62)
    assert log == [("play", 60), ("release", 60), ("play", 62)]
    s, log = engine(monkeypatch, instrument="piano")
    s.play_notes([[Note(4, letter=1), Note(4, letter=3), Note(4, letter=5)]])  # D F A together
    assert log == [("play", 62), ("play", 65), ("play", 69)]
    s.play_notes([[Note(4, letter=0)]])
    assert log[3:] == [("release", 62), ("release", 65), ("release", 69), ("play", 60)]
    assert INSTRUMENT_BY_KEY["piano"].damped and not INSTRUMENT_BY_KEY["marimba"].damped


def test_a_piano_scale_hands_over_from_note_to_note_and_leaves_the_last_to_fade(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that in a piano melody each note is stopped as the next starts, and that the last note is not stopped.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    _app = QApplication.instance() or QApplication([])  # kept alive for the timers
    s, log = engine(monkeypatch, instrument="piano")
    s.play_notes([[Note(4, letter=0)], [Note(4, letter=1)], [Note(4, letter=2)]], gap_ms=30)
    QTest.qWait(250)
    assert log == [("play", 60), ("release", 60), ("play", 62), ("release", 62), ("play", 64)]


def test_the_notes_of_a_chord_sound_together_and_end_together(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that the notes of a chord sound together and end together.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    s, log = engine(monkeypatch, instrument="viola_bowed")
    s.play_notes([[Note(4, letter=0), Note(4, letter=2), Note(4, letter=4)]])  # C4 E4 G4 at once
    assert log == [("play", 60), ("play", 64), ("play", 67)]  # none of them cuts off another
    s.play_notes([[Note(4, letter=1)]])
    assert log[3:] == [
        ("release", 60),
        ("release", 64),
        ("release", 67),
        ("play", 62),
    ]


def test_a_melody_hands_over_from_note_to_note(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that a melody hands over from note to note.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    _app = QApplication.instance() or QApplication([])  # kept alive for the timers
    s, log = engine(monkeypatch, instrument="viola_bowed")
    s.play_notes([[Note(4, letter=0)], [Note(4, letter=1)], [Note(4, letter=2)]], gap_ms=30)
    QTest.qWait(250)
    assert log == [
        ("play", 60),
        ("release", 60),
        ("play", 62),
        ("release", 62),
        ("play", 64),
    ]


def test_a_melody_says_which_note_is_sounding_as_each_one_starts(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that the caller is told each note's place as it starts, and then that the melody is over.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    _app = QApplication.instance() or QApplication([])  # kept alive for the timers
    s, log = engine(monkeypatch, instrument="viola_bowed")
    seen: list[tuple[int | None, int]] = []
    s.play_notes(
        [[Note(4, letter=0)], [Note(4, letter=1)], [Note(4, letter=2)]],
        gap_ms=30,
        on_step=lambda i: seen.append((i, len(log))),
    )
    QTest.qWait(250)
    assert [i for i, _ in seen] == [0, 1, 2, None]
    assert [n for _, n in seen][:3] == [1, 3, 5]  # each is told after its own note has started, and not before


def test_a_muted_melody_still_says_which_note_would_be_sounding(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that with the sound off the caller is still told each note's place, on the same timing, so a display can follow.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    _app = QApplication.instance() or QApplication([])  # kept alive for the timers
    s, log = engine(monkeypatch, instrument="viola_bowed")
    s.enabled = False
    seen: list[int | None] = []
    s.play_notes([[Note(4, letter=0)], [Note(4, letter=1)]], gap_ms=30, on_step=seen.append)
    QTest.qWait(200)
    assert seen == [0, 1, None] and log == []


def test_a_melody_that_is_replaced_stops_telling_the_caller(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that a melody replaced by a newer one says nothing more, so the display of the old one cannot spill onto the new.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    _app = QApplication.instance() or QApplication([])  # kept alive for the timers
    s, _ = engine(monkeypatch, instrument="viola_bowed")
    s.enabled = False
    old: list[int | None] = []
    s.play_notes([[Note(4, letter=0)], [Note(4, letter=1)], [Note(4, letter=2)]], gap_ms=60, on_step=old.append)
    QTest.qWait(20)
    s.play_notes([[Note(4, letter=0)]], gap_ms=60)
    QTest.qWait(300)
    assert old == [0]


def test_a_muted_engine_neither_plays_nor_releases(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that a muted engine neither plays nor releases.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    s, log = engine(monkeypatch, instrument="viola_bowed")
    s.enabled = False
    s.play_midi(60)
    s.play_midi(62)
    assert log == []


def test_the_two_ways_of_playing_the_viola_are_listed_together() -> None:
    """
    Check that the two ways of playing the viola are listed together.
    """
    groups = dict(instrument_groups())
    assert [i.key for i in groups["Viola"]] == ["viola_bowed", "viola_plucked"]
    assert [i.variant for i in groups["Viola"]] == ["Arco", "Pizzicato"]
    assert all(len(v) == 1 for k, v in groups.items() if k != "Viola")  # everything else is on its own
    assert len(groups) == 6


# -- hearing an instrument (the preview in the settings) ------------------------------------------------------------
@pytest.mark.parametrize("rate", [22050, 44100])
def test_preview_note_onsets_are_evenly_spaced_in_the_rendered_audio(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    rate: int,
) -> None:
    """
    Check exact note spacing in the first rendered clip, including recordings with a different sample rate.

    Parameters
    ----------
    tmp_path : Path
        A temporary sound cache.
    monkeypatch : pytest.MonkeyPatch
        Replaces the recordings with short impulses.
    rate : int
        The recordings' sample rate.
    """
    player = Sounds()
    player._dir = tmp_path
    midis = (
        74,
        75,
        72,
        71,
    )
    files = {}
    for index, note_number in enumerate(midis):
        samples = np.zeros(rate // 100)
        samples[0] = (index + 1) / 10
        path = tmp_path / f"{note_number}.wav"
        path.write_bytes(to_wav_bytes(samples, rate=rate))
        files[note_number] = path
    monkeypatch.setattr(player, "_note_file", lambda _inst, *, midi: files[midi])
    path = player._preview_file(INSTRUMENT_BY_KEY["flute"], midis=midis, step_ms=300)
    samples, rendered_rate = read_wav(path)
    assert rendered_rate == SAMPLE_RATE
    sounding = np.flatnonzero(np.abs(samples) > 0.01)
    onsets = sounding[np.r_[True, np.diff(sounding) > 1]]
    assert onsets.tolist() == [
        0,
        13230,
        26460,
        39690,
    ]
    assert np.allclose(
        samples[onsets],
        [
            0.1,
            0.2,
            0.3,
            0.4,
        ],
        atol=0.0001,
    )
    monkeypatch.setattr(player, "_note_file", lambda *_args, **_kwargs: pytest.fail("cached preview reread its notes"))
    assert player._preview_file(INSTRUMENT_BY_KEY["flute"], midis=midis, step_ms=300) == path


def test_a_preview_reuses_one_clip_and_stops_it_before_replaying(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that a muted preview starts one clip, reuses it on replay and stops it when another instrument is previewed.

    Parameters
    ----------
    app : QApplication
        The Qt application.
    tmp_path : Path
        A temporary sound cache.
    monkeypatch : pytest.MonkeyPatch
        Records playback without using audio hardware.
    """
    player = Sounds()
    player.enabled = False
    midis = (
        74,
        75,
        72,
        71,
    )
    effect = QSoundEffect()
    calls = []
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(audio_module, "QSoundEffect", lambda: effect)
    monkeypatch.setattr(player, "_preview_file", lambda inst, **_kwargs: tmp_path / f"{inst.key}.wav")
    monkeypatch.setattr(effect, "play", lambda: calls.append(("play", effect.source().fileName())))
    monkeypatch.setattr(effect, "stop", lambda: calls.append(("stop", effect.source().fileName())))
    player.preview("flute", midis=midis)
    player.preview("flute", midis=midis)
    player.preview("piano", midis=midis)
    assert calls[:4] == [
        ("play", "flute.wav"),
        ("stop", "flute.wav"),
        ("play", "flute.wav"),
        ("stop", "flute.wav"),
    ]
    assert calls[-1] == ("play", "piano.wav")
    assert len(player._preview_effects) == 2
    player.play_notes([[Note(4, letter=0)]])
    assert calls[-1] == ("stop", "piano.wav")


def preview_engine(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Sounds, list[tuple[int, float]]]:
    """
    Build an engine whose notes are recorded with the time they were started.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.

    Returns
    -------
    tuple of Sounds and list of tuple
        The engine, and the notes started so far as (note, time) pairs.
    """
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    # noinspection PyGlobalUndefined
    global _preview_app
    _preview_app = QApplication.instance() or QApplication([])  # kept alive for the timers
    s, started = Sounds(), []

    class Quiet(FakeEffect):
        """
        An effect that never reports that it is still playing.
        """

        # noinspection PyMethodMayBeStatic,PyPep8Naming
        def isPlaying(self) -> bool:
            """
            Say that the effect is not playing.

            Returns
            -------
            bool
                Always False.
            """
            return False

    monkeypatch.setattr(s, "_effect", lambda inst, midi: Quiet(midi, log=[]))
    monkeypatch.setattr(s, "play_midi", lambda midi, *a, **k: started.append((midi, time.monotonic())))
    return s, started


def test_a_sequence_plays_its_notes_in_order_one_step_apart(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that a sequence plays its notes in order one step apart.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    s, started = preview_engine(monkeypatch)
    s._play_sequence(
        "viola_bowed",
        steps=[([60], 0.9), ([64], 0.9), ([67], 0.9)],
        gap_ms=60,
        force=True,
    )
    QTest.qWait(400)
    assert [m for m, _ in started] == [60, 64, 67]
    times = [t for _, t in started]
    assert all(b - a >= 0.05 for a, b in zip(times, times[1:]))


def test_a_pause_in_the_program_delays_the_notes_instead_of_making_them_sound_together(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that a pause in the program delays the notes instead of making them sound together.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    s, started = preview_engine(monkeypatch)
    s._play_sequence(
        "viola_bowed",
        steps=[([60], 0.9), ([64], 0.9), ([67], 0.9)],
        gap_ms=80,
        force=True,
    )
    time.sleep(0.5)  # the sound system starting up, say, which blocks the timers
    QTest.qWait(500)
    assert [m for m, _ in started] == [60, 64, 67]
    times = [t for _, t in started]
    assert all(b - a >= 0.07 for a, b in zip(times, times[1:]))


def test_starting_a_second_sequence_ends_the_first(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that starting a second sequence ends the first.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    s, started = preview_engine(monkeypatch)
    s._play_sequence(
        "viola_bowed",
        steps=[([60], 0.9), ([64], 0.9), ([67], 0.9)],
        gap_ms=80,
        force=True,
    )
    QTest.qWait(100)  # the first note, and maybe the second, have started
    s._play_sequence(
        "viola_bowed",
        steps=[([62], 0.9), ([65], 0.9), ([69], 0.9)],
        gap_ms=80,
        force=True,
    )
    QTest.qWait(400)
    played = [m for m, _ in started]
    assert played[-3:] == [62, 65, 69]
    assert 67 not in played  # the old one never reached its last note


# -- the rhythm of a melody (the arpeggio that plays on a right answer) ----------------------------------------------


def melody(n: int) -> list[list[Note]]:
    """
    Make a melody of single notes that rises by a letter each time.

    Parameters
    ----------
    n : int
        How many notes.

    Returns
    -------
    list of list of Note
        One chord (of one note) per step.
    """
    return [[Note(4, letter=i % 7)] for i in range(n)]


def test_the_notes_of_a_melody_are_evenly_spaced(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that the notes of a melody are evenly spaced.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    s, started = preview_engine(monkeypatch)
    s.play_notes(melody(5), gap_ms=70)
    QTest.qWait(600)
    assert len(started) == 5
    gaps = [b - a for (_, a), (_, b) in zip(started, started[1:])]
    assert all(0.06 <= g <= 0.14 for g in gaps), gaps


def test_a_note_that_is_slow_to_start_does_not_upset_the_rhythm(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that a note that is slow to start does not upset the rhythm.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    s, started = preview_engine(monkeypatch)

    def slow_start(
        midi: int,
        *args: object,
        **kwargs: object,
    ) -> None:  # the first note takes 60 ms to get going, as the first one can
        """
        Record a note as started, taking 60 ms over the first one.

        Parameters
        ----------
        midi : int
            The note.
        args : object
            Ignored.
        kwargs : object
            Ignored.
        """
        del args, kwargs  # accepted to match what it stands in for, but not needed
        if not started:
            time.sleep(0.06)
        started.append((midi, time.monotonic()))

    monkeypatch.setattr(s, "play_midi", slow_start)
    s.play_notes(melody(4), gap_ms=100)
    QTest.qWait(700)
    gaps = [b - a for (_, a), (_, b) in zip(started, started[1:])]
    assert len(started) == 4 and all(0.09 <= g <= 0.16 for g in gaps), gaps


def test_a_stall_delays_the_notes_instead_of_bunching_them(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that a stall delays the notes instead of bunching them.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    s, started = preview_engine(monkeypatch)
    s.play_notes(melody(4), gap_ms=80)
    time.sleep(0.4)  # the program is busy, so the timers are late
    QTest.qWait(600)
    gaps = [b - a for (_, a), (_, b) in zip(started, started[1:])]
    assert len(started) == 4 and all(g >= 0.07 for g in gaps), gaps


def test_a_new_melody_cancels_the_notes_still_waiting_from_the_last(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that a new melody cancels the notes still waiting from the last.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    s, started = preview_engine(monkeypatch)
    s.play_notes(melody(5), gap_ms=80)
    QTest.qWait(100)
    s.play_notes([[n] for n in melody(1)[0]] * 3, gap_ms=80)
    QTest.qWait(500)
    first = [m for m, _ in started]
    assert first.count(first[0]) >= 3 and len(started) < 5 + 3  # the old melody never reached its end
    assert len([m for m in first]) <= 2 + 3


def test_a_muted_melody_plays_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that a muted melody plays nothing.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    s, started = preview_engine(monkeypatch)
    s.enabled = False
    s.play_notes(melody(3), gap_ms=30)
    QTest.qWait(150)
    assert started == []
