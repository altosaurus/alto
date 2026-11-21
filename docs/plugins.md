---
title: Plugins
nav_order: 8.5
nav_group: Using Alto
children: plugins
permalink: /plugins/
---

An Alto plugin adds an instrument and practice material to the app. Each plugin is an instrument pack that pairs artwork with exercises. It can also include recordings, lessons, and glossary entries. For example, a learner can identify a note marked on a fingerboard, hear its pitch, or open a lesson about that instrument.

Find the registration code in the table below. In Alto, choose **Menu → Tools → Plugins… → Install plugin by code…** and enter the code. Alto downloads the latest release from the registered repository. Restart Alto to use the plugin. To get a newer release later, select the installed plugin and choose **Update selected plugin**. You can also install a downloaded ZIP with **Install plugin from file…**. Installed exercises appear under **Instruments**.

To build a plugin, start with the [Plugin API]({{ '/plugins/api/' | relative_url }}) to see what Alto requires. Then follow the [viola plugin tutorial]({{ '/plugins/viola/' | relative_url }}) to build and test a playable exercise on a string instrument, or the [harpsichord plugin tutorial]({{ '/plugins/harpsichord/' | relative_url }}) to build one for a keyboard. Each tutorial lives in its own repository, [viola-plugin-tutorial](https://github.com/altosaurus/viola-plugin-tutorial) and [harpsichord-plugin-tutorial](https://github.com/altosaurus/harpsichord-plugin-tutorial), with the finished plugin as an editable folder and as a ZIP on its Releases page.

## Registered plugins

To register your plugin, [open an issue on Alto’s GitHub repository](https://github.com/altosaurus/alto/issues/new?template=plugin-registration.yml). In the issue, include your plugin’s name, its Pack ID from `pack.json`, a description, and a repository link. Confirm that you have the rights to distribute the plugin and its contents. Once the registration is approved and published, the issue number is your install code.

Select a plugin’s name to see its details in Alto’s docs.

<table id="plugin-list" data-registry="{{ site.site_root }}/plugins.json" data-details="{{ '/plugins/detail/' | relative_url }}">
  <thead><tr><th scope="col">Plugin</th><th scope="col">Code</th><th scope="col">Description</th></tr></thead>
  <tbody><tr><td colspan="3" id="plugin-status" role="status">Loading registered plugins…</td></tr></tbody>
</table>
<noscript><p>Enable JavaScript to view the <a href="{{ site.site_root }}/plugins.json">plugin registry</a> as a table.</p></noscript>
<script src="{{ site.site_root }}/plugins.js" defer></script>
