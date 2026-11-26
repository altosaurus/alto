---
title: alto.ui.backup_flow
parent: api
package: alto.ui
api_components: [{"title": "counted", "url": "/api/alto.ui.backup_flow/function-counted/"}, {"title": "default_name", "url": "/api/alto.ui.backup_flow/function-default_name/"}, {"title": "describe", "url": "/api/alto.ui.backup_flow/function-describe/"}, {"title": "export_backup", "url": "/api/alto.ui.backup_flow/function-export_backup/"}, {"title": "import_backup", "url": "/api/alto.ui.backup_flow/function-import_backup/"}, {"title": "safety_copy", "url": "/api/alto.ui.backup_flow/function-safety_copy/"}]
permalink: /api/alto.ui.backup_flow/
---
{% raw %}
Exporting a backup and importing one: the file dialogs, the questions
asked, and the safety copy made before anything is replaced.

## Functions

- [`default_name`](function-default_name/) — Suggest a file name for a backup made now.
- [`counted`](function-counted/) — Write a count with its noun, in the plural unless there is one.
- [`describe`](function-describe/) — Say what a backup holds and when it was made, for the question asked before importing it.
- [`export_backup`](function-export_backup/) — Ask where to save a backup, and write it.
- [`safety_copy`](function-safety_copy/) — Save a backup of what the database holds now, beside it, before it is replaced.
- [`import_backup`](function-import_backup/) — Ask for a backup file and, once the user has agreed, replace everything with what it holds.

<details markdown="1">
<summary>Module notes and examples</summary>

Everything Alto keeps goes into a backup (the database and the saved
preferences), and importing one replaces everything, so an
import into a clean install leaves it as if nothing had changed. Before
an import replaces what is there, a backup of that is
saved next to the database, so a wrong choice can be undone.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> default_name(now=0.0).endswith(
...     ".altobackup"
... )
True
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"default_name": "function-default_name/", "counted": "function-counted/", "describe": "function-describe/", "export_backup": "function-export_backup/", "safety_copy": "function-safety_copy/", "import_backup": "function-import_backup/"}</script>
{% include api-fragments.html %}
