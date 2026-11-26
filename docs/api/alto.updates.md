---
title: alto.updates
parent: api
package: alto
api_components: [{"title": "Asset", "url": "/api/alto.updates/class-asset/"}, {"title": "InstallKind", "url": "/api/alto.updates/class-installkind/"}, {"title": "Release", "url": "/api/alto.updates/class-release/"}, {"title": "Source", "url": "/api/alto.updates/class-source/"}, {"title": "cannot_update", "url": "/api/alto.updates/function-cannot_update/"}, {"title": "check_command", "url": "/api/alto.updates/function-check_command/"}, {"title": "fetch_text", "url": "/api/alto.updates/function-fetch_text/"}, {"title": "find_asset", "url": "/api/alto.updates/function-find_asset/"}, {"title": "find_program", "url": "/api/alto.updates/function-find_program/"}, {"title": "install_command", "url": "/api/alto.updates/function-install_command/"}, {"title": "install_kind", "url": "/api/alto.updates/function-install_kind/"}, {"title": "installed_source", "url": "/api/alto.updates/function-installed_source/"}, {"title": "installed_version", "url": "/api/alto.updates/function-installed_version/"}, {"title": "is_frozen", "url": "/api/alto.updates/function-is_frozen/"}, {"title": "is_newer", "url": "/api/alto.updates/function-is_newer/"}, {"title": "is_tool_install", "url": "/api/alto.updates/function-is_tool_install/"}, {"title": "parse_checksums", "url": "/api/alto.updates/function-parse_checksums/"}, {"title": "parse_direct_url", "url": "/api/alto.updates/function-parse_direct_url/"}, {"title": "parse_latest_release", "url": "/api/alto.updates/function-parse_latest_release/"}, {"title": "parse_ls_remote", "url": "/api/alto.updates/function-parse_ls_remote/"}, {"title": "platform_asset_name", "url": "/api/alto.updates/function-platform_asset_name/"}, {"title": "release_answer", "url": "/api/alto.updates/function-release_answer/"}, {"title": "self_check", "url": "/api/alto.updates/function-self_check/"}, {"title": "short", "url": "/api/alto.updates/function-short/"}, {"title": "ssl_context", "url": "/api/alto.updates/function-ssl_context/"}, {"title": "verify_signature", "url": "/api/alto.updates/function-verify_signature/"}, {"title": "version_key", "url": "/api/alto.updates/function-version_key/"}]
permalink: /api/alto.updates/
---
{% raw %}
What kind of copy of Alto is running, how it can be updated, and the
commands and answers that checking involves.

## Classes

- [`Source`](class-source/) — Where an installed copy of Alto came from.
- [`InstallKind`](class-installkind/) — How the running copy of Alto got where it is, which decides how it can be updated.
- [`Asset`](class-asset/) — A file of a release: the installer, the tarball, the checksums or their signature.
- [`Release`](class-release/) — A release of Alto, as published on GitHub.

## Functions

- [`short`](function-short/) — Shorten a commit id to the seven characters people use for it.
- [`parse_direct_url`](function-parse_direct_url/) — Read where a package was installed from, out of the `direct_url.json` that the installer leaves with it.
- [`installed_source`](function-installed_source/) — Say where the Alto that is running was installed from.
- [`is_tool_install`](function-is_tool_install/) — Say whether Alto is running from an environment that `uv tool` made, which is what the install script makes.
- [`is_frozen`](function-is_frozen/) — Say whether Alto is running as a packaged build, made with PyInstaller, rather than from Python.
- [`install_kind`](function-install_kind/) — Decide what kind of copy of Alto this is.
- [`cannot_update`](function-cannot_update/) — Say why a kind of copy cannot update itself at all, if it cannot.
- [`find_program`](function-find_program/) — Find a program to run, also in the places the installers put them, which a program started from the dock may not search.
- [`check_command`](function-check_command/) — Give the command that asks the address Alto came from for the commit at the end of a branch or tag.
- [`install_command`](function-install_command/) — Give the command that installs Alto over the installed copy: a release, or the newest commit of the address.
- [`parse_ls_remote`](function-parse_ls_remote/) — Read the commit id out of what `git ls-remote` printed.
- [`version_key`](function-version_key/) — Turn a version, with or without the "v" of a tag, into numbers that can be compared.
- [`is_newer`](function-is_newer/) — Say whether one version is newer than another, comparing numbers and not text, so 0.10.0 is newer than 0.9.0.
- [`installed_version`](function-installed_version/) — Give the version of Alto that is running.
- [`parse_latest_release`](function-parse_latest_release/) — Read GitHub's answer about the latest release.
- [`release_answer`](function-release_answer/) — Make sense of what came back when the latest release was asked for.
- [`fetch_text`](function-fetch_text/) — Fetch a web address, waiting at most a number of seconds. It blocks, so the interface runs it on another thread.
- [`ssl_context`](function-ssl_context/) — Make the settings for a secure connection, trusting the certificate authorities that come with Alto.
- [`platform_asset_name`](function-platform_asset_name/) — Give the name of the file that updates a packaged copy on this system, as the release workflow names it.
- [`find_asset`](function-find_asset/) — Find a file of a release by its name, if it is at the address where a release keeps its files.
- [`parse_checksums`](function-parse_checksums/) — Read a `SHA256SUMS` file: a line for each file, with its SHA-256 hash and its name.
- [`verify_signature`](function-verify_signature/) — Say whether an Ed25519 signature of some data was made with one of the keys.
- [`self_check`](function-self_check/) — Check, without any network, that what a copy needs to check an update is there and works.

<details markdown="1">
<summary>Module notes and examples</summary>

A copy installed with `scripts/alto-install.sh` is a `uv tool` install
from a git address. The installed package records that
address and the commit it was built from, so it can follow the newest
release (a tag) or the newest commit on the main branch.
A packaged copy (a PyInstaller build) cannot replace itself, so it can
only be told that a newer release exists. This module
decides and describes; `alto.ui.update_flow` runs the commands and asks
the questions.

A packaged copy replaces itself with a downloaded release. What makes
that safe is here: a release carries `SHA256SUMS` and a
signature of it (`SHA256SUMS.sig`, Ed25519, made with a private key that
only the release workflow has), and a copy of Alto
trusts only the public keys in `UPDATE_PUBLIC_KEYS`. It installs a file
only if the signature verifies, the signed list names the
file, and the file's hash is the one listed.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> short(
...     "b6e2091ba08f6b79dcf293d1a77d86f7a812d4fe"
... )
'b6e2091'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"source": "class-source/", "short": "function-short/", "parse_direct_url": "function-parse_direct_url/", "installed_source": "function-installed_source/", "is_tool_install": "function-is_tool_install/", "installkind": "class-installkind/", "is_frozen": "function-is_frozen/", "install_kind": "function-install_kind/", "cannot_update": "function-cannot_update/", "find_program": "function-find_program/", "check_command": "function-check_command/", "install_command": "function-install_command/", "parse_ls_remote": "function-parse_ls_remote/", "asset": "class-asset/", "release": "class-release/", "version_key": "function-version_key/", "is_newer": "function-is_newer/", "installed_version": "function-installed_version/", "parse_latest_release": "function-parse_latest_release/", "release_answer": "function-release_answer/", "fetch_text": "function-fetch_text/", "ssl_context": "function-ssl_context/", "platform_asset_name": "function-platform_asset_name/", "find_asset": "function-find_asset/", "parse_checksums": "function-parse_checksums/", "verify_signature": "function-verify_signature/", "self_check": "function-self_check/"}</script>
{% include api-fragments.html %}
