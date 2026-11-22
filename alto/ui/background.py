"""
Run slow work, such as a download, on another thread, and hear how it went on the window's thread.

Examples
--------
>>> import time
>>> heard = []
>>> owner = QObject()
>>> _ = run_in_background(lambda: 6 * 7, owner=owner, done=heard.append, failed=heard.append)
>>> deadline = time.monotonic() + 5
>>> while not heard and time.monotonic() < deadline:
...     app.processEvents()
>>> heard
[42]
"""

from __future__ import annotations

import threading
import weakref
from collections.abc import Callable
from typing import (
    TypeVar,
    cast,
)

import shiboken6
from PySide6.QtCore import (
    QObject,
    Signal,
)

T = TypeVar("T")


_relays: set[_Relay] = set()  # relays whose work is still running, kept here so that nothing deletes them


class _Relay(QObject):
    """
    Carry the outcome of background work back to the thread the relay was made on, where its callbacks run.

    The worker emits on the relay, so nothing else may delete the relay while the work runs: it has no parent, and it is kept
    in `_relays` until its outcome arrives. Emitting from another thread on an object that is being deleted can crash the
    program. Whether the object the work is for still exists (a window closed while a download was still going) is checked
    when the outcome arrives, on that object's thread, and if it is gone the outcome is dropped.

    Attributes
    ----------
    finished : Signal
        Emitted, from the worker, with what the work returned.
    crashed : Signal
        Emitted, from the worker, with the exception the work raised.

    Examples
    --------
    >>> heard = []
    >>> owner = QObject()
    >>> relay = _Relay(owner, done=heard.append, failed=heard.append)
    >>> relay._finish("ok")
    >>> heard
    ['ok']
    >>> gone = QObject()
    >>> late = _Relay(gone, done=heard.append, failed=heard.append)
    >>> shiboken6.delete(gone)  # the window closed while the work ran
    >>> late._finish("too late")
    >>> heard
    ['ok']
    """

    finished = Signal(object)
    crashed = Signal(object)

    def __init__(
        self,
        owner: QObject,
        *,
        done: Callable[[object], None],
        failed: Callable[[Exception], None],
    ) -> None:
        """
        Make a relay for one piece of work.

        Parameters
        ----------
        owner : QObject
            The object the work is for. The relay is made on its thread but does not belong to it.
        done : callable
            Called with what the work returned. Keyword-only.
        failed : callable
            Called with the exception the work raised. Keyword-only.

        Examples
        --------
        >>> owner = QObject()
        >>> _Relay(owner, done=print, failed=print).parent() is None
        True
        """
        super().__init__()
        self._owner = weakref.ref(owner)  # not kept alive by the relay
        self._done = done
        self._failed = failed
        self.finished.connect(self._finish)
        self.crashed.connect(self._crash)

    def _owner_exists(self) -> bool:
        """
        Say whether the object the work is for still exists.

        Returns
        -------
        bool
            False once Python or Qt has deleted it.

        Examples
        --------
        >>> owner = QObject()
        >>> _Relay(owner, done=print, failed=print)._owner_exists()
        True
        """
        owner = self._owner()
        return owner is not None and shiboken6.isValid(owner)

    def _finish(self, result: object) -> None:
        """
        Hand on what the work returned, and let the relay go.

        Parameters
        ----------
        result : object
            What the work returned.

        Examples
        --------
        >>> heard = []
        >>> owner = QObject()
        >>> _Relay(owner, done=heard.append, failed=print)._finish(3)
        >>> heard
        [3]
        """
        _relays.discard(self)
        self.deleteLater()
        if self._owner_exists():
            self._done(result)

    def _crash(self, error: Exception) -> None:
        """
        Hand on the exception the work raised, and let the relay go.

        Parameters
        ----------
        error : Exception
            What the work raised.

        Examples
        --------
        >>> heard = []
        >>> owner = QObject()
        >>> _Relay(owner, done=print, failed=heard.append)._crash(ValueError("no"))
        >>> heard
        [ValueError('no')]
        """
        _relays.discard(self)
        self.deleteLater()
        if self._owner_exists():
            self._failed(error)


def run_in_background(
    work: Callable[[], T],
    *,
    owner: QObject,
    done: Callable[[T], None],
    failed: Callable[[Exception], None],
) -> threading.Thread:
    """
    Run work on another thread, then call `done` with its result, or `failed` with its exception, on the owner's thread.

    The window stays responsive while the work runs. If the owner is deleted before the work ends, neither is called. The thread
    does not keep Alto from quitting.

    Parameters
    ----------
    work : callable
        The slow part. It must not touch widgets.
    owner : QObject
        The object the work is for, such as the dialog that started it. Keyword-only.
    done : callable
        Called with what `work` returned. Keyword-only.
    failed : callable
        Called with the exception `work` raised. Keyword-only.

    Returns
    -------
    threading.Thread
        The thread doing the work, already started. Callers need not keep it.

    Examples
    --------
    >>> import time
    >>> heard = []
    >>> owner = QObject()
    >>> def broken():
    ...     raise OSError("offline")
    >>> _ = run_in_background(broken, owner=owner, done=heard.append, failed=lambda error: heard.append(str(error)))
    >>> deadline = time.monotonic() + 5
    >>> while not heard and time.monotonic() < deadline:
    ...     app.processEvents()
    >>> heard
    ['offline']
    """
    relay = _Relay(owner, done=lambda result: done(cast("T", result)), failed=failed)  # the result comes back as it went
    _relays.add(relay)  # kept until its outcome arrives, so the worker never emits on a deleted object

    def run() -> None:
        """
        Do the work and send its outcome to the relay, which hands it on from the owner's thread.

        Examples
        --------
        Called on the worker thread only.
        """
        try:
            outcome = (relay.finished, work())
        except Exception as error:  # every failure is reported, not lost on the thread
            outcome = (relay.crashed, error)
        signal, value = outcome
        signal.emit(value)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread
