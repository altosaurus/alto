"""
Tests for what decides whether an installed Alto can update itself, and
for the commands that check and update.
"""

from __future__ import annotations

import base64
import json
import os
import socket
import ssl
import sys
import threading
import urllib.request
from http.server import (
    BaseHTTPRequestHandler,
    HTTPServer,
)
from pathlib import Path

import pytest
from nacl.signing import SigningKey

from alto import updates
from alto.updates import (
    CHECKSUMS_NAME,
    DOWNLOAD_BASE,
    NO_RELEASE,
    NOT_BY_SCRIPT,
    RELEASES_PAGE,
    SIGNATURE_NAME,
    SOURCE_FOLDER,
    Asset,
    InstallKind,
    Release,
    Source,
    cannot_update,
    check_command,
    fetch_text,
    find_asset,
    find_program,
    install_command,
    install_kind,
    installed_source,
    is_frozen,
    is_newer,
    is_tool_install,
    parse_checksums,
    parse_direct_url,
    parse_latest_release,
    parse_ls_remote,
    platform_asset_name,
    release_answer,
    self_check,
    short,
    ssl_context,
    verify_signature,
    version_key,
)

COMMIT = "b6e2091ba08f6b79dcf293d1a77d86f7a812d4fe"
URL = "https://github.com/altosaurus/alto.git"
GIT_INSTALL = json.dumps(
    {"url": URL, "vcs_info": {"vcs": "git", "commit_id": COMMIT}},
)


def test_a_commit_is_shortened_to_seven_characters() -> None:
    """
    Check that a full commit id is cut to the seven characters people
    use.
    """
    assert short(COMMIT) == "b6e2091"
    assert short("abc") == "abc"


def test_a_git_install_records_its_address_commit_and_ref() -> None:
    """
    Check that the file the installer leaves is read, with the default
    branch unless the install named one.
    """
    assert parse_direct_url(GIT_INSTALL) == Source(
        URL,
        commit=COMMIT,
        ref="HEAD",
    )
    named = json.dumps(
        {
            "url": URL,
            "vcs_info": {
                "vcs": "git",
                "commit_id": COMMIT,
                "requested_revision": "dev",
            },
        },
    )
    found = parse_direct_url(named)
    assert found is not None and found.ref == "dev"


@pytest.mark.parametrize(
    "text",
    [
        json.dumps(
            {"url": "file:///home/me/alto", "dir_info": {"editable": True}},
        ),
        json.dumps(
            {"url": URL, "vcs_info": {"vcs": "hg", "commit_id": COMMIT}},
        ),
        json.dumps({"url": URL, "vcs_info": {"vcs": "git"}}),
        json.dumps({"vcs_info": {"vcs": "git", "commit_id": COMMIT}}),
        "[]",
        "null",
        "{}",
        "not json at all",
        "",
    ],
)
def test_anything_that_is_not_a_git_install_has_no_source(text: str) -> None:
    """
    Check that a source folder, another kind of repository and
    unreadable files are all read as having no git source.

    Parameters
    ----------
    text : str
        The contents of a `direct_url.json`.
    """
    assert parse_direct_url(text) is None


class FakeDistribution:
    """
    Stands in for the installed package's record, holding one
    `direct_url.json` or none.
    """

    def __init__(self, text: str | None) -> None:
        """
        Hold the file's text.

        Parameters
        ----------
        text : str or None
            The contents of the file, or None if the package has no such
            file.
        """
        self.text = text

    def read_text(self, filename: str) -> str | None:
        """
        Give the file's text.

        Parameters
        ----------
        filename : str
            The name asked for; only `direct_url.json` is kept.

        Returns
        -------
        str or None
            The text.
        """
        return self.text if filename == "direct_url.json" else None


def test_the_installed_package_is_asked_where_it_came_from(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that the running copy's source comes from its package record,
    and that a missing record means no source.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces the package lookup.
    """
    monkeypatch.setattr(
        updates.metadata,
        "distribution",
        lambda _name: FakeDistribution(GIT_INSTALL),
    )
    assert installed_source() == Source(URL, commit=COMMIT)
    monkeypatch.setattr(
        updates.metadata,
        "distribution",
        lambda _name: FakeDistribution(None),
    )
    assert installed_source() is None


def test_a_copy_installed_by_uv_has_its_receipt_in_its_environment(
    tmp_path: Path,
) -> None:
    """
    Check that an environment made by `uv tool` is told apart by the
    receipt it keeps.

    Parameters
    ----------
    tmp_path : Path
        A new folder standing in for the environment.
    """
    assert not is_tool_install(prefix=tmp_path)
    (tmp_path / "uv-receipt.toml").write_text("[tool]\n")
    assert is_tool_install(prefix=tmp_path)


def test_the_kind_of_copy_comes_from_where_it_was_installed_from_and_how() -> (
    None
):
    """
    Check that a packaged build, a script install, another git install
    and a source folder are told apart.
    """
    here = Source(URL, commit=COMMIT)
    assert install_kind(here, tool=True, frozen=False) is InstallKind.SCRIPT
    assert install_kind(here, tool=False, frozen=False) is InstallKind.OTHER
    assert install_kind(None, tool=False, frozen=False) is InstallKind.SOURCE
    assert install_kind(None, tool=True, frozen=False) is InstallKind.SOURCE
    assert (
        install_kind(here, tool=True, frozen=True) is InstallKind.PACKAGE
    )  # a packaged build is one whatever it records
    assert install_kind(None, tool=False, frozen=True) is InstallKind.PACKAGE


def test_source_folder_and_another_kind_of_install_told_why_they() -> None:
    """
    Check that only the kinds of copy that can be told about updates
    have no reason given.
    """
    assert cannot_update(InstallKind.SOURCE) == SOURCE_FOLDER
    assert cannot_update(InstallKind.OTHER) == NOT_BY_SCRIPT
    assert (
        cannot_update(InstallKind.SCRIPT) is None
        and cannot_update(InstallKind.PACKAGE) is None
    )


def test_a_packaged_build_is_the_one_that_python_marks_as_frozen(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that `is_frozen` follows the flag that PyInstaller sets on
    `sys`.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Sets and removes the flag for the length of the test.
    """
    # noinspection PyUnresolvedReferences
    monkeypatch.delattr(sys, "frozen", raising=False)
    assert not is_frozen()
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    assert is_frozen()


def test_a_program_is_found_on_the_path_or_where_the_installers_put_it(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that `find_program` uses the search path first and then the
    folders that the installers use.

    Parameters
    ----------
    tmp_path : Path
        A new folder, used as the home folder and as a folder on the
        path.
    monkeypatch : pytest.MonkeyPatch
        Sets the search path for the length of the test.
    """
    monkeypatch.setenv("PATH", "")
    assert find_program("uv", home=tmp_path) is None
    local = tmp_path / ".local" / "bin"
    local.mkdir(parents=True)
    (local / "uv").write_text("#!/bin/sh\n")
    assert (
        find_program("uv", home=tmp_path) is None
    )  # present but not something that can be run
    os.chmod(local / "uv", 0o755)
    assert find_program("uv", home=tmp_path) == str(local / "uv")
    on_path = tmp_path / "bin"
    on_path.mkdir()
    (on_path / "git").write_text("#!/bin/sh\n")
    os.chmod(on_path / "git", 0o755)
    monkeypatch.setenv("PATH", str(on_path))
    assert find_program("git", home=tmp_path) == str(on_path / "git")


def test_check_asks_installs_own_address_and_install_command() -> None:
    """
    Check that the check uses the address and ref, and that installing
    names a tag, or none for the default branch.
    """
    source = Source(URL, commit=COMMIT, ref="dev")
    assert check_command(source, git="/usr/bin/git") == (
        "/usr/bin/git",
        ["ls-remote", URL, "dev"],
    )
    assert install_command(source, uv="/usr/bin/uv", tag="v0.1.0") == (
        "/usr/bin/uv",
        ["tool", "install", "--force", f"git+{URL}@v0.1.0"],
    )
    assert install_command(source, uv="/usr/bin/uv") == (
        "/usr/bin/uv",
        ["tool", "install", "--force", f"git+{URL}"],
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (f"{COMMIT}\tHEAD\n", COMMIT),
        (f"{COMMIT}\trefs/heads/main\n{'a' * 40}\trefs/heads/other\n", COMMIT),
        ("", None),
        ("\n", None),
        ("fatal: repository 'https://example.org/' not found\n", None),
        ("b6e2091\tHEAD\n", None),
        (f"{'G' * 40}\tHEAD\n", None),
    ],
)
def test_the_commit_is_read_from_what_ls_remote_prints(
    text: str,
    expected: str | None,
) -> None:
    """
    Check that the first line's commit id is read, and that an error or
    an empty answer gives none.

    Parameters
    ----------
    text : str
        What `git ls-remote` printed.
    expected : str or None
        The commit id that should be read.
    """
    assert parse_ls_remote(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("0.0.0", (0, 0, 0)),
        ("v0.10.2", (0, 10, 2)),
        ("1.0", (1, 0)),
        (" v2 ", (2,)),
        ("1.0.0rc1", None),
        ("1.0.0-beta", None),
        ("unknown", None),
        ("", None),
        ("v", None),
    ],
)
def test_a_version_becomes_numbers_only_if_it_is_plain(
    text: str,
    expected: tuple[int, ...] | None,
) -> None:
    """
    Check that a version, with or without a tag's "v", is read as
    numbers, and that anything else is not.

    Parameters
    ----------
    text : str
        The version.
    expected : tuple of int or None
        The numbers it should become.
    """
    assert version_key(text) == expected


def test_versions_are_compared_as_numbers_and_not_as_text() -> None:
    """
    Check that 0.10.0 is newer than 0.9.0, that trailing zeros do not
    matter, and that unreadable versions are never newer.
    """
    assert (
        is_newer("0.10.0", installed="0.9.0")
        and is_newer("v0.1.0", installed="0.0.0")
        and is_newer("1", installed="0.9.9")
    )
    assert (
        not is_newer("0.0.0", installed="0.0.0")
        and not is_newer("1.0", installed="1.0.0")
        and not is_newer("1.0.0", installed="1.0")
    )
    assert not is_newer("0.9.0", installed="0.10.0") and not is_newer(
        "0.0.0",
        installed="0.1.0",
    )
    assert not is_newer("1.0.0", installed="unknown") and not is_newer(
        "1.0.0rc1",
        installed="0.0.0",
    )


RELEASE_URL = "https://github.com/altosaurus/alto/releases/tag/v0.1.0"
RELEASE = {
    "tag_name": "v0.1.0",
    "html_url": RELEASE_URL,
    "draft": False,
    "prerelease": False,
}


def test_the_latest_release_is_read_from_githubs_answer() -> None:
    """
    Check that the tag becomes a version, with its page, and that a
    missing page falls back to the list of releases.
    """
    assert parse_latest_release(json.dumps(RELEASE)) == Release(
        "0.1.0",
        tag="v0.1.0",
        url=RELEASE_URL,
    )
    without_page = {
        key: value for key, value in RELEASE.items() if key != "html_url"
    }
    found = parse_latest_release(json.dumps(without_page))
    assert found is not None and found.url == RELEASES_PAGE


@pytest.mark.parametrize(
    "text",
    [
        json.dumps({**RELEASE, "prerelease": True}),
        json.dumps({**RELEASE, "draft": True}),
        json.dumps({**RELEASE, "tag_name": "nightly"}),
        json.dumps({**RELEASE, "tag_name": "v1.0.0rc1"}),
        json.dumps({**RELEASE, "tag_name": 5}),
        json.dumps({"message": "Not Found"}),
        "[]",
        "not json",
        "",
    ],
)
def test_an_answer_that_is_not_a_plain_release_is_not_one(text: str) -> None:
    """
    Check that drafts, pre-releases, odd tags and answers that are not
    releases at all give no release.

    Parameters
    ----------
    text : str
        What GitHub answered.
    """
    assert parse_latest_release(text) is None


def test_each_kind_of_answer_gives_release_or_sentence_says_why() -> None:
    """
    Check the release or the reason for success, no release yet, an
    error, no answer, and an answer that makes no sense.
    """
    assert release_answer(200, text=json.dumps(RELEASE)) == Release(
        "0.1.0",
        tag="v0.1.0",
        url=RELEASE_URL,
    )
    assert release_answer(404, text="Not Found") == NO_RELEASE
    assert (
        release_answer(403, text="rate limit exceeded")
        == "GitHub answered with an error (403): rate limit exceeded"
    )
    assert (
        release_answer(500, text="")
        == "GitHub answered with an error (500): no details"
    )
    assert (
        release_answer(0, text="Name or service not known")
        == "Alto could not reach GitHub: Name or service not known"
    )
    assert (
        release_answer(0, text="") == "Alto could not reach GitHub: no answer"
    )
    assert "not understood" in str(release_answer(200, text="<html>"))


class Handler(BaseHTTPRequestHandler):
    """
    Answers a request for `/ok` with a release, and anything else with a
    404.
    """

    def do_GET(self) -> None:  # noqa: N802
        """Answer one request, noting who asked and how."""
        seen.append(
            (
                self.path,
                self.headers.get("User-Agent", ""),
                self.headers.get("Accept", ""),
            ),
        )
        body = (
            json.dumps(RELEASE).encode()
            if self.path == "/ok"
            else b'{"message": "Not Found"}'
        )
        self.send_response(200 if self.path == "/ok" else 404)
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


seen: list[tuple[str, str, str]] = []


def test_fetching_reads_status_and_body_and_says_only_what() -> None:
    """
    Check `fetch_text` against a real server: a 200, a 404, and headers
    that say only what the request is for.
    """
    seen.clear()
    # noinspection PyTypeChecker
    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        status, text = fetch_text(f"{base}/ok", seconds=5)
        assert status == 200 and json.loads(text)["tag_name"] == "v0.1.0"
        status, _ = fetch_text(f"{base}/missing", seconds=5)
        assert status == 404
    finally:
        server.shutdown()
        server.server_close()
    assert [agent for _, agent, _ in seen] == [
        updates.USER_AGENT,
        updates.USER_AGENT,
    ]
    assert all(
        accept == "application/vnd.github+json" for _, _, accept in seen
    )
    assert updates.USER_AGENT == "alto-update-check"


def test_fetching_reports_no_answer_as_status_zero_with_the_reason() -> None:
    """
    Check that a refused connection and a server that never answers both
    give 0 and a reason.
    """
    free = socket.socket()
    free.bind(("127.0.0.1", 0))
    port = free.getsockname()[1]
    free.close()  # nothing listens on this port now
    status, reason = fetch_text(f"http://127.0.0.1:{port}/", seconds=2)
    assert status == 0 and reason
    silent = socket.socket()
    silent.bind(("127.0.0.1", 0))
    silent.listen(
        1,
    )  # connections are accepted by the system, and then nobody answers
    try:
        status, reason = fetch_text(
            f"http://127.0.0.1:{silent.getsockname()[1]}/",
            seconds=1,
        )
    finally:
        silent.close()
    assert status == 0 and "timed out" in reason


# -- what a packaged copy needs to update itself
# --------------------------------------------------------------------


def test_files_of_release_read_from_githubs_answer_and_odd_ones() -> None:
    """
    Check that each file's name, address and size are kept, and that
    entries that are not files are ignored.
    """
    answer = {
        **RELEASE,
        "assets": [
            {
                "name": "alto-0.1.0-linux-x86_64.tar.gz",
                "browser_download_url": DOWNLOAD_BASE + "v0.1.0/a",
                "size": 123,
            },
            {
                "name": "SHA256SUMS",
                "browser_download_url": DOWNLOAD_BASE + "v0.1.0/SHA256SUMS",
            },
            {"name": "no address"},
            {"browser_download_url": "no name"},
            "not a dict",
            {"name": 5, "browser_download_url": "x"},
        ],
    }
    release = parse_latest_release(json.dumps(answer))
    assert release is not None
    assert release.assets == (
        Asset(
            "alto-0.1.0-linux-x86_64.tar.gz",
            url=DOWNLOAD_BASE + "v0.1.0/a",
            size=123,
        ),
        Asset("SHA256SUMS", url=DOWNLOAD_BASE + "v0.1.0/SHA256SUMS", size=0),
    )
    assert parse_latest_release(
        json.dumps({**RELEASE, "assets": "oops"}),
    ) == Release("0.1.0", tag="v0.1.0", url=RELEASE_URL)


@pytest.mark.parametrize(
    ("system", "machine", "expected"),
    [
        ("Linux", "x86_64", "alto-1.2.3-linux-x86_64.tar.gz"),
        ("linux", "AMD64", "alto-1.2.3-linux-x86_64.tar.gz"),
        ("Windows", "AMD64", "alto-1.2.3-windows-x64-setup.exe"),
        ("Windows", "x86_64", "alto-1.2.3-windows-x64-setup.exe"),
        ("Linux", "aarch64", None),
        ("Windows", "ARM64", None),
        ("Darwin", "arm64", None),
    ],
)
def test_the_download_for_a_system_is_named_as_the_release_workflow_names_it(
    system: str,
    machine: str,
    expected: str | None,
) -> None:
    """
    Check the file name for each system and processor, and that
    unsupported ones have none.

    Parameters
    ----------
    system : str
        What `platform.system()` says.
    machine : str
        What `platform.machine()` says.
    expected : str or None
        The name the release workflow gives that package.
    """
    assert (
        platform_asset_name("1.2.3", system=system, machine=machine)
        == expected
    )


def test_file_of_release_found_only_at_address_where_releases() -> None:
    """
    Check that a file by the right name at some other address is not
    found.
    """
    release = Release(
        "0.1.0",
        tag="v0.1.0",
        url="",
        assets=(
            Asset("a", url=DOWNLOAD_BASE + "v0.1.0/a"),
            Asset("b", url="https://evil.example/b"),
            Asset("c", url=DOWNLOAD_BASE + "x/c"),
        ),
    )
    assert (
        find_asset(release, name="a") == release.assets[0]
        and find_asset(release, name="c") == release.assets[2]
    )
    assert (
        find_asset(release, name="b") is None
        and find_asset(release, name="missing") is None
    )
    assert (
        find_asset(release, name="b", base="https://evil.example/")
        == release.assets[1]
    )


def test_list_of_checksums_read_line_by_line_and_only_plain_file() -> None:
    """
    Check the hash and name of each good line, in lower case, with
    binary-mode marks, and that anything else is ignored.
    """
    good = "AB" * 32
    text = "\n".join(
        [
            f"{good}  alto-1.tar.gz",
            f"{'cd' * 32} *alto-2.exe",
            f"{'ef' * 32}  ../escape",
            f"{'ef' * 32}  dir/file",
            f"{'12' * 32}  with space.tar",
            f"{'12' * 31}  short-hash",
            "not a line at all",
            "",
            f"{'34' * 32}   three-spaces",
        ],
    )
    assert parse_checksums(text) == {
        "alto-1.tar.gz": good.lower(),
        "alto-2.exe": "cd" * 32,
    }
    assert parse_checksums("") == {}


def signed(data: bytes) -> tuple[str, str]:
    """
    Sign some data with a new key.

    Parameters
    ----------
    data : bytes
        What to sign.

    Returns
    -------
    tuple of str and str
        The public key and the signature, base64.
    """
    key = SigningKey.generate()
    return base64.b64encode(bytes(key.verify_key)).decode(), base64.b64encode(
        key.sign(data).signature,
    ).decode()


def test_a_signature_verifies_only_for_the_exact_data_and_a_trusted_key() -> (
    None
):
    """
    Check the good case and each way it can go wrong: other data,
    another key, no keys, and either one malformed.
    """
    public, signature = signed(b"the list")
    other_public, _ = signed(b"another")
    assert verify_signature(b"the list", signature=signature, keys=(public,))
    assert verify_signature(
        b"the list",
        signature=signature,
        keys=(other_public, public),
    )  # any trusted key will do
    assert not verify_signature(
        b"the list ",
        signature=signature,
        keys=(public,),
    )
    assert not verify_signature(
        b"the list",
        signature=signature,
        keys=(other_public,),
    )
    assert not verify_signature(b"the list", signature=signature, keys=())
    assert not verify_signature(
        b"the list",
        signature=signature,
        keys=("not base64!", "AAAA", ""),
    )
    assert not verify_signature(
        b"the list",
        signature=signature[:-4],
        keys=(public,),
    )
    assert not verify_signature(
        b"the list",
        signature="not base64!",
        keys=(public,),
    )
    assert not verify_signature(b"the list", signature="", keys=(public,))
    assert not verify_signature(
        b"the list",
        signature=base64.b64encode(b"x" * 64).decode(),
        keys=(public,),
    )


def test_secure_connection_trusts_certificate_authorities_come() -> None:
    """
    Check that the settings for a connection verify the server and carry
    certifi's list, not the system's.
    """
    context = ssl_context()
    assert context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname
    assert len(context.get_ca_certs()) > 100


def test_the_release_check_uses_that_secure_connection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that `fetch_text` hands the secure settings to the connection
    it opens.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces the opening of a connection.
    """
    contexts: list[object] = []

    def open_it(_request: object, **options: object) -> None:
        """
        Note the settings, and refuse the connection.

        Parameters
        ----------
        _request : object
            The request.
        **options : object
            The settings of the connection.

        Raises
        ------
        OSError
            Always.
        """
        contexts.append(options.get("context"))
        raise OSError("no connection in a test")

    monkeypatch.setattr(urllib.request, "urlopen", open_it)
    assert fetch_text("https://api.github.com/x", seconds=1) == (
        0,
        "no connection in a test",
    )
    context = contexts[0]
    assert (
        isinstance(context, ssl.SSLContext)
        and context.verify_mode == ssl.CERT_REQUIRED
    )


def test_the_built_in_self_check_passes_and_notices_a_key_that_is_not_a_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check what `alto --self-test` runs: it finds nothing wrong, and says
    so when a key in the code is not a key.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces the keys in the code.
    """
    assert self_check() == []
    with monkeypatch.context() as changed:
        changed.setattr(
            updates,
            "ssl_context",
            lambda: ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT),
        )
        assert self_check() == [
            (
                "The list of certificate authorities did not load, so a "
                "secure connection could not be made."
            ),
        ]
    public, _ = signed(b"x")
    monkeypatch.setattr(updates, "UPDATE_PUBLIC_KEYS", (public,))
    assert self_check() == []
    monkeypatch.setattr(updates, "UPDATE_PUBLIC_KEYS", (public, "not a key"))
    assert self_check() == [
        "A public key in the code is not a valid Ed25519 key.",
    ]
    monkeypatch.setattr(
        updates,
        "UPDATE_PUBLIC_KEYS",
        (base64.b64encode(b"short").decode(),),
    )
    assert len(self_check()) == 1


def test_two_names_workflow_uploads_for_signature_ones_alto() -> None:
    """
    Check the file names, which the release workflow, the signing script
    and the updater must agree on.
    """
    assert (CHECKSUMS_NAME, SIGNATURE_NAME) == ("SHA256SUMS", "SHA256SUMS.sig")
    assert (
        DOWNLOAD_BASE
        == "https://github.com/altosaurus/alto/releases/download/"
    )
