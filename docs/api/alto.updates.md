---
title: alto.updates
parent: api
package: alto
order: 7
permalink: /api/alto.updates/
---
{% raw %}
What kind of copy of Alto is running, how it can be updated, and the commands and answers that checking involves.

A copy installed with `scripts/alto-install.sh` is a `uv tool` install from a git address. The installed package records that
address and the commit it was built from, so it can follow the newest release (a tag) or the newest commit on the main branch.
A packaged copy (a PyInstaller build) cannot replace itself, so it can only be told that a newer release exists. This module
decides and describes; `alto.ui.update_flow` runs the commands and asks the questions.

A packaged copy replaces itself with a downloaded release. What makes that safe is here: a release carries `SHA256SUMS` and a
signature of it (`SHA256SUMS.sig`, Ed25519, made with a private key that only the release workflow has), and a copy of Alto
trusts only the public keys in `UPDATE_PUBLIC_KEYS`. It installs a file only if the signature verifies, the signed list names the
file, and the file's hash is the one listed.

**Examples**

```pycon
>>> short("b6e2091ba08f6b79dcf293d1a77d86f7a812d4fe")
'b6e2091'
```

## Source

```python
Source(
    url: str,
    commit: str,
    ref: str = 'HEAD',
)
```

Where an installed copy of Alto came from.

**Attributes**

- `url` (*str*): The git address it was installed from.
- `commit` (*str*): The commit it was built from.
- `ref` (*str*): The branch or tag it follows; "HEAD", the address's default branch, unless the install named one.

**Examples**

```pycon
>>> Source("https://github.com/altosaurus/alto.git", commit="b6e2091").ref
'HEAD'
```

## short

```python
def short(commit: str) -> str
```

Shorten a commit id to the seven characters people use for it.

**Parameters**

- `commit` (*str*): The full commit id.

**Returns**

- *str*: Its first seven characters.

**Examples**

```pycon
>>> short("b6e2091ba08f6b79dcf293d1a77d86f7a812d4fe")
'b6e2091'
```

## parse_direct_url

```python
def parse_direct_url(text: str) -> Source | None
```

Read where a package was installed from, out of the `direct_url.json` that the installer leaves with it.

**Parameters**

- `text` (*str*): The contents of the file.

**Returns**

- *Source or None*: The git address, the commit and the ref, or None if the package was not installed from a git address (a copy that runs from a source folder has a folder there instead).

**Examples**

```pycon
>>> parse_direct_url('{"url": "https://example.org/a.git", "vcs_info": {"vcs": "git", "commit_id": "abc1234"}}')
Source(url='https://example.org/a.git', commit='abc1234', ref='HEAD')
>>> named = '{"url": "https://x.org/a.git", "vcs_info": {"vcs": "git", "commit_id": "abc1234", "requested_revision": "dev"}}'
>>> # noinspection PyUnresolvedReferences
>>> parse_direct_url(named).ref
'dev'
>>> parse_direct_url('{"url": "file:///home/me/alto", "dir_info": {"editable": true}}') is None
True
>>> parse_direct_url("not json") is None
True
```

## installed_source

```python
def installed_source() -> Source | None
```

Say where the Alto that is running was installed from.

**Returns**

- *Source or None*: Its git address and commit, or None if it was not installed from a git address.

**Examples**

```pycon
>>> source = installed_source()
>>> source is None or len(source.commit) == COMMIT_LENGTH
True
```

## is_tool_install

```python
def is_tool_install(
    *,
    prefix: Path | None = None,
) -> bool
```

Say whether Alto is running from an environment that `uv tool` made, which is what the install script makes.

**Parameters**

- `prefix` (*Path or None, default None*): The environment to look at; the one that is running if None. Keyword-only.

**Returns**

- *bool*: True if the environment has the receipt that `uv tool install` leaves in it.

**Examples**

```pycon
>>> is_tool_install(prefix=Path("/nowhere"))
False
```

## InstallKind

```python
class InstallKind(Enum)
```

How the running copy of Alto got where it is, which decides how it can be updated.

**Attributes**

- `SCRIPT` (*InstallKind*): Installed with `scripts/alto-install.sh`: it can replace itself, from a release or from the main branch.
- `PACKAGE` (*InstallKind*): A packaged build (a tarball or the Windows installer): it can only be told that a newer release exists.
- `OTHER` (*InstallKind*): Installed from a git address some other way, so there is no `uv tool` to update it with.
- `SOURCE` (*InstallKind*): Run from a source folder, which is updated with git.

**Examples**

```pycon
>>> InstallKind.SCRIPT.name
'SCRIPT'
```

## is_frozen

```python
def is_frozen() -> bool
```

Say whether Alto is running as a packaged build, made with PyInstaller, rather than from Python.

**Returns**

- *bool*: True for a packaged build.

**Examples**

```pycon
>>> is_frozen()
False
```

## install_kind

```python
def install_kind(
    source: Source | None,
    *,
    tool: bool,
    frozen: bool,
) -> InstallKind
```

Decide what kind of copy of Alto this is.

**Parameters**

- `source` (*Source or None*): Where it was installed from, if it was installed from a git address.
- `tool` (*bool*): Whether it runs from an environment that `uv tool` made. Keyword-only.
- `frozen` (*bool*): Whether it is a packaged build. Keyword-only.

**Returns**

- *InstallKind*: The kind.

**Examples**

```pycon
>>> here = Source("https://example.org/a.git", commit="abc1234")
>>> install_kind(here, tool=True, frozen=False).name
'SCRIPT'
>>> install_kind(here, tool=False, frozen=False).name, install_kind(None, tool=False, frozen=False).name
('OTHER', 'SOURCE')
>>> install_kind(None, tool=False, frozen=True).name
'PACKAGE'
```

## cannot_update

```python
def cannot_update(kind: InstallKind) -> str | None
```

Say why a kind of copy cannot update itself at all, if it cannot.

**Parameters**

- `kind` (*InstallKind*): The kind of copy.

**Returns**

- *str or None*: A sentence for a copy run from a source folder or installed some other way; None for one that can be told about updates.

**Examples**

```pycon
>>> cannot_update(InstallKind.SOURCE) == SOURCE_FOLDER, cannot_update(InstallKind.OTHER) == NOT_BY_SCRIPT
(True, True)
>>> cannot_update(InstallKind.SCRIPT) is None and cannot_update(InstallKind.PACKAGE) is None
True
```

## find_program

```python
def find_program(
    name: str,
    *,
    home: Path | None = None,
) -> str | None
```

Find a program to run, also in the places the installers put them, which a program started from the dock may not search.

**Parameters**

- `name` (*str*): The program's name, such as "git" or "uv".
- `home` (*Path or None, default None*): The home folder to look in besides the search path; the user's own if None. Keyword-only.

**Returns**

- *str or None*: Its path, or None if it is nowhere to be found.

**Examples**

```pycon
>>> find_program("no-such-program-anywhere") is None
True
```

## check_command

```python
def check_command(
    source: Source,
    *,
    git: str,
) -> tuple[str, list[str]]
```

Give the command that asks the address Alto came from for the commit at the end of a branch or tag.

**Parameters**

- `source` (*Source*): Where the running copy came from.
- `git` (*str*): The path of the `git` program. Keyword-only.

**Returns**

- *tuple of str and list of str*: The program and its arguments.

**Examples**

```pycon
>>> check_command(Source("https://example.org/a.git", commit="abc1234"), git="git")
('git', ['ls-remote', 'https://example.org/a.git', 'HEAD'])
```

## install_command

```python
def install_command(
    source: Source,
    *,
    uv: str,
    tag: str | None = None,
) -> tuple[str, list[str]]
```

Give the command that installs Alto over the installed copy: a release, or the newest commit of the address.

`uv tool install --force` is used rather than `uv tool upgrade`, because an upgrade stays on the tag or branch the copy was
installed from, and a copy that follows a release must be able to move to the main branch and back.

**Parameters**

- `source` (*Source*): Where the running copy came from.
- `uv` (*str*): The path of the `uv` program. Keyword-only.
- `tag` (*str or None, default None*): The release to install, such as "v0.1.0"; the address's default branch if None. Keyword-only.

**Returns**

- *tuple of str and list of str*: The program and its arguments.

**Examples**

```pycon
>>> here = Source("https://example.org/alto.git", commit="abc1234")
>>> install_command(here, uv="uv", tag="v0.1.0")
('uv', ['tool', 'install', '--force', 'git+https://example.org/alto.git@v0.1.0'])
>>> install_command(here, uv="uv")
('uv', ['tool', 'install', '--force', 'git+https://example.org/alto.git'])
```

## parse_ls_remote

```python
def parse_ls_remote(text: str) -> str | None
```

Read the commit id out of what `git ls-remote` printed.

**Parameters**

- `text` (*str*): The output: a line for each ref, each a commit id, a tab and the ref's name.

**Returns**

- *str or None*: The commit id on the first line, or None if there is none (the ref does not exist, or git printed an error).

**Examples**

```pycon
>>> parse_ls_remote("b6e2091ba08f6b79dcf293d1a77d86f7a812d4fe\tHEAD\n")
'b6e2091ba08f6b79dcf293d1a77d86f7a812d4fe'
>>> parse_ls_remote("") is None, parse_ls_remote("fatal: repository not found") is None
(True, True)
```

## Asset

```python
Asset(
    name: str,
    url: str,
    size: int = 0,
)
```

A file of a release: the installer, the tarball, the checksums or their signature.

**Attributes**

- `name` (*str*): Its name, such as "alto-0.1.0-linux-x86_64.tar.gz".
- `url` (*str*): The address it is downloaded from.
- `size` (*int*): Its size in bytes, as GitHub states it; 0 if it does not.

**Examples**

```pycon
>>> Asset("SHA256SUMS", url="https://example.org/s", size=300).size
300
```

## Release

```python
Release(
    version: str,
    tag: str,
    url: str,
    assets: tuple[Asset, ...] = field(default=()),
)
```

A release of Alto, as published on GitHub.

**Attributes**

- `version` (*str*): Its version, such as "0.1.0".
- `tag` (*str*): The tag it is made from, such as "v0.1.0".
- `url` (*str*): The page where it and its downloads are.
- `assets` (*tuple of Asset*): Its files.

**Examples**

```pycon
>>> Release("0.1.0", tag="v0.1.0", url="https://example.org/r").version
'0.1.0'
```

## version_key

```python
def version_key(text: str) -> tuple[int, ...] | None
```

Turn a version, with or without the "v" of a tag, into numbers that can be compared.

**Parameters**

- `text` (*str*): The version, such as "0.10.2" or "v1.0".

**Returns**

- *tuple of int or None*: Its numbers; None if it is not made only of numbers and dots, as a pre-release such as "1.0.0rc1" is not.

**Examples**

```pycon
>>> version_key("v0.10.2"), version_key("1.0")
((0, 10, 2), (1, 0))
>>> version_key("1.0.0rc1") is None, version_key("") is None, version_key("unknown") is None
(True, True, True)
```

## is_newer

```python
def is_newer(
    candidate: str,
    *,
    installed: str,
) -> bool
```

Say whether one version is newer than another, comparing numbers and not text, so 0.10.0 is newer than 0.9.0.

**Parameters**

- `candidate` (*str*): The version that may be newer.
- `installed` (*str*): The version to compare it with. Keyword-only.

**Returns**

- *bool*: True if the candidate is newer. False if it is the same or older, or if either is not a plain version.

**Examples**

```pycon
>>> is_newer("0.10.0", installed="0.9.0"), is_newer("v0.1.0", installed="0.0.0")
(True, True)
>>> is_newer("1.0", installed="1.0.0"), is_newer("0.0.0", installed="0.1.0")
(False, False)
>>> is_newer("1.0.0", installed="unknown")
False
```

## installed_version

```python
def installed_version() -> str
```

Give the version of Alto that is running.

**Returns**

- *str*: The installed version, or "unknown" if Alto was not installed as a package.

**Examples**

```pycon
>>> installed_version().count(".") >= 1
True
```

## parse_latest_release

```python
def parse_latest_release(text: str) -> Release | None
```

Read GitHub's answer about the latest release.

**Parameters**

- `text` (*str*): The JSON that `releases/latest` answers with.

**Returns**

- *Release or None*: The release, or None if the answer is not one, is a draft or a pre-release, or has a tag that is not a plain version.

**Examples**

```pycon
>>> answer = '{"tag_name": "v0.1.0", "html_url": "https://example.org/r", "draft": false, "prerelease": false}'
>>> parse_latest_release(answer)
Release(version='0.1.0', tag='v0.1.0', url='https://example.org/r', assets=())
>>> parse_latest_release(answer.replace('"prerelease": false', '"prerelease": true')) is None
True
>>> parse_latest_release("not json") is None
True
```

## release_answer

```python
def release_answer(
    status: int,
    *,
    text: str,
) -> Release | str
```

Make sense of what came back when the latest release was asked for.

**Parameters**

- `status` (*int*): The HTTP status, or 0 if no answer came at all.
- `text` (*str*): The body of the answer, or the reason there was none. Keyword-only.

**Returns**

- *Release or str*: The release, or a sentence that says why there is none to offer.

**Examples**

```pycon
>>> release_answer(404, text="") == NO_RELEASE
True
>>> release_answer(0, text="Name or service not known")
'Alto could not reach GitHub: Name or service not known'
>>> release_answer(403, text="rate limit exceeded")
'GitHub answered with an error (403): rate limit exceeded'
```

## fetch_text

```python
def fetch_text(
    url: str,
    *,
    seconds: int,
) -> tuple[int, str]
```

Fetch a web address, waiting at most a number of seconds. It blocks, so the interface runs it on another thread.

**Parameters**

- `url` (*str*): The address.
- `seconds` (*int*): How long to wait for the server. Keyword-only.

**Returns**

- *tuple of int and str*: The HTTP status and the body. If the server was not reached, 0 and the reason.

**Examples**

```pycon
>>> fetch_text("http://127.0.0.1:9/", seconds=2)[0]  # nothing listens there
0
```

## ssl_context

```python
def ssl_context() -> ssl.SSLContext
```

Make the settings for a secure connection, trusting the certificate authorities that come with Alto.

A packaged copy cannot count on the system's: the Python inside it may look for them where the computer it was built on keeps
them, and a connection would then fail on a distribution that keeps them somewhere else.

**Returns**

- *ssl.SSLContext*: A context that checks the server's certificate and name against certifi's list.

**Examples**

```pycon
>>> ssl_context().verify_mode == ssl.CERT_REQUIRED, len(ssl_context().get_ca_certs()) > 100
(True, True)
```

## platform_asset_name

```python
def platform_asset_name(
    version: str,
    *,
    system: str,
    machine: str,
) -> str | None
```

Give the name of the file that updates a packaged copy on this system, as the release workflow names it.

**Parameters**

- `version` (*str*): The version, such as "0.1.0". Keyword-only after the first.
- `system` (*str*): The operating system, as `platform.system()` says it ("Linux", "Windows"). Keyword-only.
- `machine` (*str*): The processor, as `platform.machine()` says it ("x86_64", "AMD64"). Keyword-only.

**Returns**

- *str or None*: The name, or None if there is no package for this system.

**Examples**

```pycon
>>> platform_asset_name("0.1.0", system="Linux", machine="x86_64")
'alto-0.1.0-linux-x86_64.tar.gz'
>>> platform_asset_name("0.1.0", system="Windows", machine="AMD64")
'alto-0.1.0-windows-x64-setup.exe'
>>> platform_asset_name("0.1.0", system="Linux", machine="aarch64") is None
True
```

## find_asset

```python
def find_asset(
    release: Release,
    *,
    name: str,
    base: str = DOWNLOAD_BASE,
) -> Asset | None
```

Find a file of a release by its name, if it is at the address where a release keeps its files.

**Parameters**

- `release` (*Release*): The release.
- `name` (*str*): The file's name. Keyword-only.
- `base` (*str, default DOWNLOAD_BASE*): What the address must start with. Keyword-only.

**Returns**

- *Asset or None*: The file, or None if the release has none by that name or it is somewhere else.

**Examples**

```pycon
>>> files = (Asset("a", url=DOWNLOAD_BASE + "v1/a"), Asset("b", url="https://example.org/b"))
>>> found = find_asset(Release("1", tag="v1", url="", assets=files), name="a")
>>> found.name if found else None
'a'
>>> find_asset(Release("1", tag="v1", url="", assets=files), name="b") is None
True
```

## parse_checksums

```python
def parse_checksums(text: str) -> dict[str, str]
```

Read a `SHA256SUMS` file: a line for each file, with its SHA-256 hash and its name.

**Parameters**

- `text` (*str*): The file's contents, as `sha256sum` writes them.

**Returns**

- *dict of str to str*: The hash of each named file, in lower case. Lines that are not a hash and a plain file name are left out.

**Examples**

```pycon
>>> entry = "ab" * 32 + "  alto-0.1.0-linux-x86_64.tar.gz"
>>> parse_checksums(entry + "\nnot a line\n" + "cd" * 32 + "  ../evil")
{'alto-0.1.0-linux-x86_64.tar.gz': 'abababababababababababababababababababababababababababababababab'}
```

## verify_signature

```python
def verify_signature(
    data: bytes,
    *,
    signature: str,
    keys: tuple[str, ...],
) -> bool
```

Say whether an Ed25519 signature of some data was made with one of the keys.

**Parameters**

- `data` (*bytes*): What was signed.
- `signature` (*str*): The signature, base64. Keyword-only.
- `keys` (*tuple of str*): The public keys (base64) that are trusted. Keyword-only.

**Returns**

- *bool*: True only if the signature is well formed and one of the keys made it. No key, a key that is not a key, and a signature that is not one all give False.

**Examples**

```pycon
>>> from nacl.signing import SigningKey
>>> pair = SigningKey.generate()
>>> public = base64.b64encode(bytes(pair.verify_key)).decode()
>>> signed = base64.b64encode(pair.sign(b"the list").signature).decode()
>>> verify_signature(b"the list", signature=signed, keys=(public,))
True
>>> verify_signature(b"another list", signature=signed, keys=(public,))
False
>>> verify_signature(b"the list", signature=signed, keys=())
False
```

## self_check

```python
def self_check() -> list[str]
```

Check, without any network, that what a copy needs to check an update is there and works.

It is what `alto --self-test` runs, so that the build can tell that a packaged copy carries the certificate list and the
signature library (which PyInstaller must be told about), and that the keys in the code are keys.

**Returns**

- *list of str*: What is wrong, one sentence each; empty if all is well.

**Examples**

```pycon
>>> self_check()
[]
```
{% endraw %}
