---
title: alto.ui.widgets
parent: api
package: alto.ui
api_components: [{"title": "HelpButton", "url": "/api/alto.ui.widgets/class-helpbutton/"}, {"title": "PracticeCounts", "url": "/api/alto.ui.widgets/class-practicecounts/"}, {"title": "SegmentedControl", "url": "/api/alto.ui.widgets/class-segmentedcontrol/"}, {"title": "SidebarToggle", "url": "/api/alto.ui.widgets/class-sidebartoggle/"}, {"title": "busy_progress_bar", "url": "/api/alto.ui.widgets/function-busy_progress_bar/"}, {"title": "vertical_scroll_area", "url": "/api/alto.ui.widgets/function-vertical_scroll_area/"}]
permalink: /api/alto.ui.widgets/
---
{% raw %}
Small widgets shared by several screens: the sidebar toggle, the help
button and a segmented control.

## Classes

- [`PracticeCounts`](class-practicecounts/) — Colored counts for calendar practice on tiles and in the exercise screen.
- [`SidebarToggle`](class-sidebartoggle/) — A button that shows or hides the exercise list.
- [`HelpButton`](class-helpbutton/) — A "?" button that opens a small popover with help text.
- [`SegmentedControl`](class-segmentedcontrol/) — A pill-shaped row of choices of which exactly one is chosen, like the switch between two views.

## Functions

- [`vertical_scroll_area`](function-vertical_scroll_area/) — Put a resizable widget in a frameless vertical scroll area.
- [`busy_progress_bar`](function-busy_progress_bar/) — Create the indeterminate progress indicator used during updates.

<details markdown="1">
<summary>Module notes and examples</summary>

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> SidebarToggle().toolTip()
'Hide exercise list'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"vertical_scroll_area": "function-vertical_scroll_area/", "busy_progress_bar": "function-busy_progress_bar/", "practicecounts": "class-practicecounts/", "practicecountsset_counts": "class-practicecounts/#practicecountsset_counts", "sidebartoggle": "class-sidebartoggle/", "sidebartoggleset_open": "class-sidebartoggle/#sidebartoggleset_open", "helpbutton": "class-helpbutton/", "helpbuttonshow_help": "class-helpbutton/#helpbuttonshow_help", "segmentedcontrol": "class-segmentedcontrol/", "segmentedcontrolset_compact": "class-segmentedcontrol/#segmentedcontrolset_compact", "segmentedcontrolcurrent": "class-segmentedcontrol/#segmentedcontrolcurrent", "segmentedcontrolset_current": "class-segmentedcontrol/#segmentedcontrolset_current", "segmentedcontrolrestyle": "class-segmentedcontrol/#segmentedcontrolrestyle"}</script>
{% include api-fragments.html %}
