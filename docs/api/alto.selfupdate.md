---
title: alto.selfupdate
parent: api
package: alto
api_components: [{"title": "Prepared", "url": "/api/alto.selfupdate/class-prepared/"}, {"title": "Target", "url": "/api/alto.selfupdate/class-target/"}, {"title": "UpdateCanceled", "url": "/api/alto.selfupdate/class-updatecanceled/"}, {"title": "UpdateError", "url": "/api/alto.selfupdate/class-updateerror/"}, {"title": "clean_environment", "url": "/api/alto.selfupdate/function-clean_environment/"}, {"title": "download", "url": "/api/alto.selfupdate/function-download/"}, {"title": "extract_tarball", "url": "/api/alto.selfupdate/function-extract_tarball/"}, {"title": "ignore_progress", "url": "/api/alto.selfupdate/function-ignore_progress/"}, {"title": "log_path", "url": "/api/alto.selfupdate/function-log_path/"}, {"title": "new_work_folder", "url": "/api/alto.selfupdate/function-new_work_folder/"}, {"title": "prepare_update", "url": "/api/alto.selfupdate/function-prepare_update/"}, {"title": "remove_leftovers", "url": "/api/alto.selfupdate/function-remove_leftovers/"}, {"title": "self_update_target", "url": "/api/alto.selfupdate/function-self_update_target/"}, {"title": "start_handoff", "url": "/api/alto.selfupdate/function-start_handoff/"}, {"title": "windows_handoff_command", "url": "/api/alto.selfupdate/function-windows_handoff_command/"}]
permalink: /api/alto.selfupdate/
---
{% raw %}
Replacing a packaged copy of Alto with a newer release: whether it can,
getting the update, checking it, and handing over.

## Classes

- [`UpdateError`](class-updateerror/) — Something went wrong in getting or checking an update. The message says what, in words for the person.
- [`UpdateCanceled`](class-updatecanceled/) — The person canceled the update before it was ready.
- [`Target`](class-target/) — A packaged copy that can replace itself, and where it is.
- [`Prepared`](class-prepared/) — An update that has been downloaded and checked, and is ready to be handed over.

## Functions

- [`self_update_target`](function-self_update_target/) — Say whether the running copy can replace itself, and if so where it is.
- [`download`](function-download/) — Fetch a file, checking the address, the size and the connection, and give its SHA-256 hash.
- [`extract_tarball`](function-extract_tarball/) — Unpack the Linux download, refusing anything that would land outside the folder.
- [`ignore_progress`](function-ignore_progress/) — Take a note of progress and do nothing with it, for a download whose progress nobody watches.
- [`prepare_update`](function-prepare_update/) — Download a release for this copy and check it: its signed list of checksums, then the file against its listed hash.
- [`clean_environment`](function-clean_environment/) — Undo what PyInstaller did to the environment, for a program that this one starts.
- [`log_path`](function-log_path/) — Give the file the Linux helper writes to, so that a failed update can be looked into.
- [`windows_handoff_command`](function-windows_handoff_command/) — Give the command that waits for Alto to end, runs the installer, and starts the old Alto again if the installer fails.
- [`start_handoff`](function-start_handoff/) — Start the program that installs the update, and return at once so that Alto can quit.
- [`new_work_folder`](function-new_work_folder/) — Make a new temporary folder for an update, whose name says what it is for.
- [`remove_leftovers`](function-remove_leftovers/) — Remove the temporary folders of earlier updates that were never cleaned up, such as a Windows installer that was run and left.

<details markdown="1">
<summary>Module notes and examples</summary>

A packaged copy is Alto frozen with PyInstaller, in a folder the user
owns: `~/.local/opt/alto` on Linux, made by `install.sh`,
and a folder under `%LOCALAPPDATA%\Programs` on Windows, made by the
installer. Neither needs administrator rights, so Alto can
fetch the new package, check it, and start the program that installs it.
Nothing is installed unless the signature on the list of
checksums verifies against a key that came with Alto, the list names the
file, and the file's hash is the one listed (see
`alto.updates`). This module has no Qt, so the interface runs it on a
worker thread and shows its progress.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> self_update_target(
...     executable=Path("/nowhere/alto"),
...     system="linux",
... ) is None
True
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"updateerror": "class-updateerror/", "updatecanceled": "class-updatecanceled/", "target": "class-target/", "prepared": "class-prepared/", "self_update_target": "function-self_update_target/", "download": "function-download/", "extract_tarball": "function-extract_tarball/", "ignore_progress": "function-ignore_progress/", "prepare_update": "function-prepare_update/", "clean_environment": "function-clean_environment/", "log_path": "function-log_path/", "windows_handoff_command": "function-windows_handoff_command/", "start_handoff": "function-start_handoff/", "new_work_folder": "function-new_work_folder/", "remove_leftovers": "function-remove_leftovers/"}</script>
{% include api-fragments.html %}
