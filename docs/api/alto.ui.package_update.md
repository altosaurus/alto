---
title: alto.ui.package_update
parent: api
package: alto.ui
api_components: [{"title": "PackageUpdateDialog", "url": "/api/alto.ui.package_update/class-packageupdatedialog/"}, {"title": "UpdatePreparer", "url": "/api/alto.ui.package_update/class-updatepreparer/"}]
permalink: /api/alto.ui.package_update/
---
{% raw %}
The window that updates a packaged copy of Alto: the download and its
checks with their progress, then what happens next.

## Classes

- [`UpdatePreparer`](class-updatepreparer/) — Download and check an update on another thread, and report how it goes through signals.
- [`PackageUpdateDialog`](class-packageupdatedialog/) — The window that downloads and checks an update for a packaged copy, and then says what happens next.

<details markdown="1">
<summary>Module notes and examples</summary>

The work is in `alto.selfupdate`, which has no Qt, and runs on another
thread here so that the window keeps moving. Until the
download has been checked nothing has been installed, and Cancel (or
closing the window) throws it away. When it is ready the
window says that Alto will close, install the update and open again, and
OK hands over; the caller starts the installer and quits.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.updates import Release
>>> PackageUpdateDialog  # doctest: +ELLIPSIS
<class '...PackageUpdateDialog'>
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"updatepreparer": "class-updatepreparer/", "updatepreparerstart": "class-updatepreparer/#updatepreparerstart", "updatepreparercancel": "class-updatepreparer/#updatepreparercancel", "updateprepareris_canceled": "class-updatepreparer/#updateprepareris_canceled", "packageupdatedialog": "class-packageupdatedialog/", "packageupdatedialogrun": "class-packageupdatedialog/#packageupdatedialogrun", "packageupdatedialogreject": "class-packageupdatedialog/#packageupdatedialogreject"}</script>
{% include api-fragments.html %}
