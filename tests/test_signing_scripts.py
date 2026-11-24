"""
Tests for the two scripts that sign releases: the one that makes the key
pair, and the one the release workflow signs with.

The release workflow trusts `sign_release.py` to refuse a secret that
does not belong to the key in the code, so that a release
no copy of Alto would install is never published. These tests keep that
refusal.
"""

from __future__ import annotations

import base64
import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from nacl.signing import SigningKey

from alto import updates

if TYPE_CHECKING:
    from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent


def load(name: str) -> ModuleType:
    """
    Load a script of `scripts/` as a module, without running it.

    Parameters
    ----------
    name : str
        The script's name, without `.py`.

    Returns
    -------
    ModuleType
        The loaded module.
    """
    spec = importlib.util.spec_from_file_location(
        name,
        ROOT / "scripts" / f"{name}.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pair() -> tuple[str, str]:
    """
    Make a key pair.

    Returns
    -------
    tuple of str and str
        The private key and the public key, base64.
    """
    key = SigningKey.generate()
    return base64.b64encode(bytes(key)).decode(), base64.b64encode(
        bytes(key.verify_key),
    ).decode()


def test_the_key_script_prints_a_private_and_a_public_key_that_belong_together(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    Check that it prints both halves, says where each goes, and that the
    public key is the private key's.

    Parameters
    ----------
    capsys : pytest.CaptureFixture
        Captures what is printed.
    """
    assert load("make_signing_key").main() == 0
    out = capsys.readouterr().out
    lines = [line.strip() for line in out.splitlines()]
    private = lines[
        lines.index(next(line for line in lines if line.startswith("PRIVATE")))
        + 1
    ]
    public = lines[
        lines.index(next(line for line in lines if line.startswith("PUBLIC")))
        + 1
    ].strip('",')
    assert "ALTO_SIGNING_KEY" in out and "UPDATE_PUBLIC_KEYS" in out
    assert (
        base64.b64encode(
            bytes(SigningKey(base64.b64decode(private)).verify_key),
        ).decode()
        == public
    )


def test_a_signature_made_by_the_script_verifies_in_alto(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check the whole signing step as the workflow runs it: a `.sig` is
    written next to the file, and Alto's own check accepts it.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    monkeypatch : pytest.MonkeyPatch
        Sets the secret and the keys in the code.
    """
    private, public = pair()
    monkeypatch.setenv("ALTO_SIGNING_KEY", private)
    monkeypatch.setattr(updates, "UPDATE_PUBLIC_KEYS", (public,))
    listing = tmp_path / "SHA256SUMS"
    listing.write_bytes(b"abc  alto-1.tar.gz\n")
    assert load("sign_release").main([str(listing)]) == 0
    signature = (tmp_path / "SHA256SUMS.sig").read_text()
    assert updates.verify_signature(
        listing.read_bytes(),
        signature=signature,
        keys=(public,),
    )
    assert not updates.verify_signature(
        b"another list",
        signature=signature,
        keys=(public,),
    )


@pytest.mark.parametrize(
    "problem",
    [
        "no secret",
        "no key in the code",
        "wrong secret",
        "secret is not a key",
        "no such file",
    ],
)
def test_signing_step_refuses_anything_would_publish_release(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    problem: str,
) -> None:
    """
    Check that each way the setup can be wrong stops the release, writes
    no signature, and says why.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    monkeypatch : pytest.MonkeyPatch
        Sets the secret and the keys in the code.
    capsys : pytest.CaptureFixture
        Captures what is printed.
    problem : str
        What is wrong.
    """
    private, public = pair()
    other_private, _ = pair()
    secret = {
        "no secret": "",
        "wrong secret": other_private,
        "secret is not a key": "this is not a key",
    }.get(problem, private)
    monkeypatch.setenv("ALTO_SIGNING_KEY", secret)
    monkeypatch.setattr(
        updates,
        "UPDATE_PUBLIC_KEYS",
        () if problem == "no key in the code" else (public,),
    )
    listing = tmp_path / (
        "missing" if problem == "no such file" else "SHA256SUMS"
    )
    if problem != "no such file":
        listing.write_bytes(b"abc  alto-1.tar.gz\n")
    assert load("sign_release").main([str(listing)]) == 1
    assert capsys.readouterr().err.strip() and not list(tmp_path.glob("*.sig"))
