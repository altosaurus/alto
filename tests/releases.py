"""
Helpers for tests of the updater: a local web server that plays GitHub,
and a signed fake release for it to serve.

Nothing here goes online. The server is on 127.0.0.1, the keys are made
for the test, and the packages are small files built on
the spot, so the real download, signature and checksum code runs against
them.
"""

from __future__ import annotations

import base64
import hashlib
import io
import tarfile
import threading
from http.server import (
    BaseHTTPRequestHandler,
    HTTPServer,
)
from pathlib import Path
from typing import TYPE_CHECKING

from nacl.signing import SigningKey

from alto import updates

if TYPE_CHECKING:
    from types import TracebackType

ROOT = Path(__file__).resolve().parent.parent
VERSION = "9.9.9"


class Keys:
    """
    A key pair made for one test.

    Attributes
    ----------
    private : str
        The private key, base64, as `scripts/make_signing_key.py` prints
        it.
    public : str
        The public key, base64, as `UPDATE_PUBLIC_KEYS` holds it.
    """

    def __init__(self) -> None:
        """Make a new key pair."""
        key = SigningKey.generate()
        self.private = base64.b64encode(bytes(key)).decode()
        self.public = base64.b64encode(bytes(key.verify_key)).decode()
        self._key = key

    def sign(self, data: bytes) -> str:
        """
        Sign some data.

        Parameters
        ----------
        data : bytes
            What to sign.

        Returns
        -------
        str
            The signature, base64.
        """
        return base64.b64encode(self._key.sign(data).signature).decode()


class Server:
    """
    A web server on this computer that serves files from a dictionary,
    for the length of a `with` block.

    Attributes
    ----------
    files : dict of str to bytes
        What is served, by path (such as
        "/releases/download/v9.9.9/SHA256SUMS").
    redirects : dict of str to str
        Paths that answer with a redirect to another address.
    requests : list of str
        The path of each request that was made, in order.
    port : int
        The port it listens on.
    """

    def __init__(self) -> None:
        """Start listening, on a port the system chooses."""
        self.files: dict[str, bytes] = {}
        self.redirects: dict[str, str] = {}
        self.requests: list[str] = []
        outer = self

        class Handler(BaseHTTPRequestHandler):
            """Answers each request from the server's dictionaries."""

            # noinspection PyPep8Naming
            def do_GET(self) -> None:  # noqa: N802
                """Answer one request."""
                outer.requests.append(self.path)
                if self.path in outer.redirects:
                    self.send_response(302)
                    self.send_header("Location", outer.redirects[self.path])
                    self.end_headers()
                    return
                body = outer.files.get(self.path)
                if body is None:
                    self.send_response(404)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            # noinspection PyShadowingBuiltins
            def log_message(self, format: str, *args: object) -> None:  # noqa: A002
                """
                Say nothing, so that the test output stays quiet.

                Parameters
                ----------
                format : str
                    The format of the message, ignored.
                *args : object
                    Its values, ignored.
                """

        # noinspection PyTypeChecker
        self._server = HTTPServer(("127.0.0.1", 0), Handler)
        self.port = self._server.server_port
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            daemon=True,
        )

    def __enter__(self) -> Server:
        """
        Start serving.

        Returns
        -------
        Server
            This server.
        """
        self._thread.start()
        return self

    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        trace: TracebackType | None,
    ) -> None:
        """
        Stop serving.

        Parameters
        ----------
        kind : type or None
            The kind of error that ended the block, if any.
        error : BaseException or None
            The error, if any.
        trace : TracebackType or None
            Where it was raised, if any.
        """
        self._server.shutdown()
        self._server.server_close()

    @property
    def base(self) -> str:
        """
        Give the address the release's files are under, ending in a
        slash.

        Returns
        -------
        str
            `http://127.0.0.1:<port>/releases/download/`.
        """
        return f"http://127.0.0.1:{self.port}/releases/download/"


def linux_package(
    version: str = VERSION,
    *,
    install_script: bytes | None = None,
    program: bytes = b'#!/bin/sh\necho "Alto 9.9.9"\n',
) -> bytes:
    """
    Build a small Linux download: a folder with the real `install.sh`, a
    stand-in program, and the icons.

    Parameters
    ----------
    version : str, default VERSION
        The version in the folder's name.
    install_script : bytes or None, default None
        What `install.sh` holds; the real one if None. Keyword-only.
    program : bytes
        What the program holds. Keyword-only.

    Returns
    -------
    bytes
        The `.tar.gz`.
    """
    top = f"alto-{version}-linux-x86_64"
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        files = {
            f"{top}/install.sh": (
                ROOT / "packaging" / "linux" / "install.sh"
            ).read_bytes()
            if install_script is None
            else install_script,
            f"{top}/alto/alto": program,
            f"{top}/icons/icon-256.png": (
                ROOT / "alto" / "assets" / "icon-256.png"
            ).read_bytes(),
            f"{top}/icons/icon.png": (
                ROOT / "alto" / "assets" / "icon.png"
            ).read_bytes(),
        }
        for name, data in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = (
                0o755 if name.endswith(("alto/alto", "install.sh")) else 0o644
            )
            tar.addfile(info, io.BytesIO(data))
    return buffer.getvalue()


def publish(
    server: Server,
    *,
    keys: Keys,
    package: bytes,
    name: str,
    version: str = VERSION,
    sign_with: Keys | None = None,
    sums_for: bytes | None = None,
    leave_out: tuple[str, ...] = (),
) -> updates.Release:
    """
    Put a release on the server: the package, the list of checksums, and
    the signature of the list.

    Parameters
    ----------
    server : Server
        Where to put it.
    keys : Keys
        The keys the release is signed with, unless `sign_with` says
        another. Keyword-only.
    package : bytes
        The package. Keyword-only.
    name : str
        The package's file name. Keyword-only.
    version : str, default VERSION
        The release's version. Keyword-only.
    sign_with : Keys or None, default None
        Sign with these instead, to make a signature that does not
        verify. Keyword-only.
    sums_for : bytes or None, default None
        Write the hash of these bytes in the list instead of the
        package's, to make a list that does not match. Keyword-only.
    leave_out : tuple of str
        Names of files not to put on the release. Keyword-only.

    Returns
    -------
    updates.Release
        The release, with the addresses of its files on the server.
    """
    tag = f"v{version}"
    digest = hashlib.sha256(package if sums_for is None else sums_for)
    listing = (f"{digest.hexdigest()}  {name}\n").encode()
    signature = (sign_with or keys).sign(listing).encode()
    contents = {
        name: package,
        updates.CHECKSUMS_NAME: listing,
        updates.SIGNATURE_NAME: signature,
    }
    assets = []
    for file, data in contents.items():
        if file in leave_out:
            continue
        server.files[f"/releases/download/{tag}/{file}"] = data
        assets.append(
            updates.Asset(
                file,
                url=f"{server.base}{tag}/{file}",
                size=len(data),
            ),
        )
    return updates.Release(
        version,
        tag=tag,
        url="https://example.org/release",
        assets=tuple(assets),
    )
