---
title: alto.ui.update_flow
parent: api
package: alto.ui
api_components: [{"title": "CheckDialog", "url": "/api/alto.ui.update_flow/class-checkdialog/"}, {"title": "CommandRunner", "url": "/api/alto.ui.update_flow/class-commandrunner/"}, {"title": "DailyReleaseCheck", "url": "/api/alto.ui.update_flow/class-dailyreleasecheck/"}, {"title": "ReleaseDialog", "url": "/api/alto.ui.update_flow/class-releasedialog/"}, {"title": "ReleaseFetcher", "url": "/api/alto.ui.update_flow/class-releasefetcher/"}, {"title": "UpdateDialog", "url": "/api/alto.ui.update_flow/class-updatedialog/"}, {"title": "WaitDialog", "url": "/api/alto.ui.update_flow/class-waitdialog/"}, {"title": "brief", "url": "/api/alto.ui.update_flow/function-brief/"}, {"title": "check_for_updates", "url": "/api/alto.ui.update_flow/function-check_for_updates/"}, {"title": "check_main", "url": "/api/alto.ui.update_flow/function-check_main/"}, {"title": "check_release", "url": "/api/alto.ui.update_flow/function-check_release/"}, {"title": "install", "url": "/api/alto.ui.update_flow/function-install/"}, {"title": "offer_release", "url": "/api/alto.ui.update_flow/function-offer_release/"}, {"title": "save_channel", "url": "/api/alto.ui.update_flow/function-save_channel/"}, {"title": "saved_channel", "url": "/api/alto.ui.update_flow/function-saved_channel/"}, {"title": "update_package", "url": "/api/alto.ui.update_flow/function-update_package/"}]
permalink: /api/alto.ui.update_flow/
---
{% raw %}
Checking for a newer Alto and installing it: the questions asked, the
progress shown, and the restart afterwards.

## Classes

- [`CommandRunner`](class-commandrunner/) — Run one program without freezing the window, handing on what it prints as it prints it, and how it ended.
- [`WaitDialog`](class-waitdialog/) — A small window with a bar that keeps moving and a Cancel button, shown while something is asked for.
- [`CheckDialog`](class-checkdialog/) — A waiting window while the address Alto came from is asked for the newest commit of its main branch.
- [`ReleaseFetcher`](class-releasefetcher/) — Ask GitHub for the latest release on another thread, so that the window never freezes while it waits.
- [`DailyReleaseCheck`](class-dailyreleasecheck/) — Check for published releases in the background and honor the learner’s reminder choice at the exercise grid.
- [`ReleaseDialog`](class-releasedialog/) — A waiting window while GitHub is asked for the latest release.
- [`UpdateDialog`](class-updatedialog/) — The window that shows an update being installed: a bar that keeps moving, what `uv` prints, and then what comes next.

## Functions

- [`brief`](function-brief/) — Cut what a program printed down to what is worth showing in a message: the end of it, without the blank space around it.
- [`saved_channel`](function-saved_channel/) — Return what the update check follows, as chosen in Settings.
- [`save_channel`](function-save_channel/) — Remember what the update check follows.
- [`check_for_updates`](function-check_for_updates/) — Ask whether a newer Alto is available and, if the person agrees, install it and restart.
- [`check_release`](function-check_release/) — Ask GitHub for the latest release and compare it with the version that is running.
- [`offer_release`](function-offer_release/) — Ask whether to upgrade using the installation's supported update path.
- [`check_main`](function-check_main/) — Ask the address Alto came from for the newest commit on its main branch and compare it with the one that is running.
- [`install`](function-install/) — Install a release, or the newest commit of the main branch, showing the progress, and restart if it worked.
- [`update_package`](function-update_package/) — Replace a packaged copy after the user agrees: download and check it, say that Alto will restart, and hand over.

<details markdown="1">
<summary>Module notes and examples</summary>

The menu's "Check for updates…" follows one of two channels, chosen in
Settings: the newest release (the default), or the
newest commit on the main branch. A copy installed with
`scripts/alto-install.sh` can replace itself, from either, with
`uv tool install`, showing its output, and restarts when OK is pressed.
A packaged copy cannot replace itself, so it is told
that a newer release exists and offered the page where it can be
downloaded; it always follows releases. A copy run from a
source folder is told to update with git.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> brief(
...     "fatal: unable to access 'https://example.org/': Could not "
...     "resolve host\n"
... )
"fatal: unable to access 'https://example.org/': Could not resolve host"
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"brief": "function-brief/", "commandrunner": "class-commandrunner/", "commandrunnerrunning": "class-commandrunner/#commandrunnerrunning", "commandrunnerstart": "class-commandrunner/#commandrunnerstart", "commandrunnerstop": "class-commandrunner/#commandrunnerstop", "saved_channel": "function-saved_channel/", "save_channel": "function-save_channel/", "waitdialog": "class-waitdialog/", "waitdialogreject": "class-waitdialog/#waitdialogreject", "checkdialog": "class-checkdialog/", "checkdialogrun": "class-checkdialog/#checkdialogrun", "releasefetcher": "class-releasefetcher/", "releasefetcherstart": "class-releasefetcher/#releasefetcherstart", "releasefetchercancel": "class-releasefetcher/#releasefetchercancel", "dailyreleasecheck": "class-dailyreleasecheck/", "releasedialog": "class-releasedialog/", "releasedialogrun": "class-releasedialog/#releasedialogrun", "updatedialog": "class-updatedialog/", "updatedialogrun": "class-updatedialog/#updatedialogrun", "updatedialogreject": "class-updatedialog/#updatedialogreject", "updatedialogcloseevent": "class-updatedialog/#updatedialogcloseevent", "check_for_updates": "function-check_for_updates/", "check_release": "function-check_release/", "offer_release": "function-offer_release/", "check_main": "function-check_main/", "install": "function-install/", "update_package": "function-update_package/"}</script>
{% include api-fragments.html %}
