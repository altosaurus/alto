#!/usr/bin/env python
"""
Make the key pair that signs Alto's releases. Run it once.

    python scripts/make_signing_key.py

It prints two things and writes nothing:

- the PRIVATE key. Store it as the GitHub secret `ALTO_SIGNING_KEY` (the
repository's Settings, Secrets and variables, Actions),
  keep an offline copy somewhere safe (a password manager is fine), and
  tell nobody. Anyone who has it can sign an update that
  every copy of Alto will install, and if it is lost no copy can be
  updated by a release signed with a new key.
- the PUBLIC key. Put it in `UPDATE_PUBLIC_KEYS` in `alto/updates.py`
and commit it; every copy of Alto built from then on trusts
  it.

The release workflow signs `SHA256SUMS` with the private key
(`scripts/sign_release.py`) and refuses to publish a release whose
signature does not verify against the public key in the code.
"""

from __future__ import annotations

import base64

from nacl.signing import SigningKey


def main() -> int:
    """
    Make a key pair and say what to do with each half.

    Returns
    -------
    int
        0.

    Examples
    --------
    >>> main()  # doctest: +SKIP
    0
    """
    key = SigningKey.generate()
    private = base64.b64encode(bytes(key)).decode()
    public = base64.b64encode(bytes(key.verify_key)).decode()
    print(
        (
            "PRIVATE key (secret). Store it as the GitHub secret "
            "ALTO_SIGNING_KEY, and keep an offline copy. Tell nobody:"
        ),
    )
    print(f"    {private}")
    print()
    print(
        (
            "PUBLIC key. Put it in UPDATE_PUBLIC_KEYS in alto/updates.py "
            "and commit it:"
        ),
    )
    print(f'    "{public}",')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
