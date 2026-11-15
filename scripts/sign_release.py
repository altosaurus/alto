#!/usr/bin/env python
"""
Sign the list of checksums of a release, so that a copy of Alto can tell that an update is the one that was published.

    ALTO_SIGNING_KEY=<private key> python scripts/sign_release.py dist/SHA256SUMS

It writes `dist/SHA256SUMS.sig`, an Ed25519 signature (base64) of the file's exact bytes. The private key comes from the
environment and is made by `scripts/make_signing_key.py`. Before it succeeds it checks the signature against the public keys in
`alto/updates.py`, so a secret that does not belong to the key in the code stops the release, instead of publishing one that no
copy of Alto would install.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import os
import sys
from pathlib import Path

from nacl.signing import SigningKey

from alto import updates


def sign(
    data: bytes,
    *,
    private: str,
) -> str:
    """
    Sign some data.

    Parameters
    ----------
    data : bytes
        What to sign.
    private : str
        The private key (base64), as `make_signing_key.py` printed it. Keyword-only.

    Returns
    -------
    str
        The signature, base64.

    Raises
    ------
    ValueError
        If the private key is not a valid key.

    Examples
    --------
    >>> from nacl.signing import SigningKey
    >>> pair = SigningKey.generate()
    >>> signature = sign(b"list", private=base64.b64encode(bytes(pair)).decode())
    >>> public = base64.b64encode(bytes(pair.verify_key)).decode()
    >>> updates.verify_signature(b"list", signature=signature, keys=(public,))
    True
    """
    try:
        key = SigningKey(base64.b64decode(private.strip(), validate=True))
    except (binascii.Error, ValueError, TypeError) as error:
        raise ValueError("The private key is not a valid Ed25519 key.") from error
    return base64.b64encode(key.sign(data).signature).decode()


def main(argv: list[str] | None = None) -> int:
    """
    Sign the file named on the command line.

    Parameters
    ----------
    argv : list of str or None, default None
        The arguments after the program's name; those the program was started with if None.

    Returns
    -------
    int
        0 if the signature was written, 1 if there is no key, the key is not valid, or the signature does not verify against the
        public keys in the code.

    Examples
    --------
    >>> main(["/no/such/file"])
    1
    """
    parser = argparse.ArgumentParser(description="Sign the list of checksums of a release.")
    parser.add_argument("file", type=Path, help="the file to sign, such as dist/SHA256SUMS")
    arguments = parser.parse_args(argv)
    private = os.environ.get("ALTO_SIGNING_KEY", "")
    if not private:
        print("ALTO_SIGNING_KEY is not set, so nothing was signed.", file=sys.stderr)
        return 1
    if not updates.UPDATE_PUBLIC_KEYS:
        print("UPDATE_PUBLIC_KEYS in alto/updates.py is empty, so a signature could not be checked.", file=sys.stderr)
        return 1
    try:
        data = arguments.file.read_bytes()
        signature = sign(data, private=private)
    except (OSError, ValueError) as error:
        print(f"Could not sign {arguments.file}: {error}", file=sys.stderr)
        return 1
    if not updates.verify_signature(data, signature=signature, keys=updates.UPDATE_PUBLIC_KEYS):
        print(
            "The signature does not verify against the public keys in alto/updates.py: the secret is not that key's.",
            file=sys.stderr,
        )
        return 1
    arguments.file.with_name(arguments.file.name + ".sig").write_text(signature + "\n", encoding="utf-8")
    print(f"Signed {arguments.file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
