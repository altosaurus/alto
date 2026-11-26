---
title: alto.ui.settings_menu
parent: api
package: alto.ui
api_components: [{"title": "ChoiceChecklist", "url": "/api/alto.ui.settings_menu/class-choicechecklist/"}, {"title": "ClefsPanel", "url": "/api/alto.ui.settings_menu/class-clefspanel/"}, {"title": "ExerciseSettingsPanel", "url": "/api/alto.ui.settings_menu/class-exercisesettingspanel/"}, {"title": "KeyChecklist", "url": "/api/alto.ui.settings_menu/class-keychecklist/"}, {"title": "KeyDiagram", "url": "/api/alto.ui.settings_menu/class-keydiagram/"}, {"title": "KeySignaturePage", "url": "/api/alto.ui.settings_menu/class-keysignaturepage/"}, {"title": "KeyboardRangePanel", "url": "/api/alto.ui.settings_menu/class-keyboardrangepanel/"}, {"title": "MenuRow", "url": "/api/alto.ui.settings_menu/class-menurow/"}, {"title": "NoteAnswerSettingsPanel", "url": "/api/alto.ui.settings_menu/class-noteanswersettingspanel/"}, {"title": "RangeEditor", "url": "/api/alto.ui.settings_menu/class-rangeeditor/"}, {"title": "ScaleKeyPicker", "url": "/api/alto.ui.settings_menu/class-scalekeypicker/"}, {"title": "SlideStack", "url": "/api/alto.ui.settings_menu/class-slidestack/"}, {"title": "StaffRangePanel", "url": "/api/alto.ui.settings_menu/class-staffrangepanel/"}, {"title": "Switch", "url": "/api/alto.ui.settings_menu/class-switch/"}, {"title": "ToggleRow", "url": "/api/alto.ui.settings_menu/class-togglerow/"}, {"title": "arrow_button", "url": "/api/alto.ui.settings_menu/function-arrow_button/"}, {"title": "buttons_page", "url": "/api/alto.ui.settings_menu/function-buttons_page/"}, {"title": "clef_choice_page", "url": "/api/alto.ui.settings_menu/function-clef_choice_page/"}, {"title": "direction_choices", "url": "/api/alto.ui.settings_menu/function-direction_choices/"}, {"title": "guard_last", "url": "/api/alto.ui.settings_menu/function-guard_last/"}, {"title": "label_with_picture", "url": "/api/alto.ui.settings_menu/function-label_with_picture/"}, {"title": "scrolling", "url": "/api/alto.ui.settings_menu/function-scrolling/"}, {"title": "show_keys", "url": "/api/alto.ui.settings_menu/function-show_keys/"}, {"title": "subpage", "url": "/api/alto.ui.settings_menu/function-subpage/"}]
permalink: /api/alto.ui.settings_menu/
---
{% raw %}
The building blocks of the settings panels that slide in beside an
exercise.

## Classes

- [`RangeEditor`](class-rangeeditor/) — A staff showing the lowest and highest note asked for a clef.
- [`KeyDiagram`](class-keydiagram/) — A small fork showing which key signatures are selected.
- [`MenuRow`](class-menurow/) — A menu row: title on the left, current value and a chevron on the right.
- [`Switch`](class-switch/) — A pill-shaped on/off switch whose knob slides across when toggled.
- [`ToggleRow`](class-togglerow/) — A menu row with a switch that changes a setting in place instead of opening a page.
- [`SlideStack`](class-slidestack/) — A stacked widget whose pages slide in from the right (going deeper) or the left (going back).
- [`ExerciseSettingsPanel`](class-exercisesettingspanel/) — What every exercise's settings pane has in common: it says when a setting has been edited.
- [`KeyboardRangePanel`](class-keyboardrangepanel/) — Settings for selecting a practice range on a keyboard.
- [`ClefsPanel`](class-clefspanel/) — A settings pane with a Clefs page, whose checkboxes choose the clefs that are asked about.
- [`StaffRangePanel`](class-staffrangepanel/) — Shared navigation and per-clef pitch range editors.
- [`NoteAnswerSettingsPanel`](class-noteanswersettingspanel/) — Staff range settings for note names and optional octaves.
- [`KeyChecklist`](class-keychecklist/) — Checkboxes for the 15 major keys, flats on the left and sharps on the right.
- [`KeySignaturePage`](class-keysignaturepage/) — The key signature sub-page: a switch for using key signatures at all, and the keys to draw from.
- [`ScaleKeyPicker`](class-scalekeypicker/) — Select major and minor keys independently.
- [`ChoiceChecklist`](class-choicechecklist/) — Checkboxes for a list of choices, optionally under headings and allowing an empty selection.

## Functions

- [`guard_last`](function-guard_last/) — Disable the only checked box, so that at least one choice always stays selected.
- [`arrow_button`](function-arrow_button/) — Make a small arrow button that repeats while it is held.
- [`label_with_picture`](function-label_with_picture/) — Label a checkbox or radio button with a picture instead of text.
- [`clef_choice_page`](function-clef_choice_page/) — Build the "Clefs" page that every exercise with a choice of clefs shares.
- [`show_keys`](function-show_keys/) — Show the selected keys as a diagram in a menu row, or "Off" when key signatures are switched off.
- [`subpage`](function-subpage/) — Build a second-layer page: a Back button and title above a body.
- [`buttons_page`](function-buttons_page/) — Build the shared Limited and All answer-button submenu.
- [`direction_choices`](function-direction_choices/) — Choose the direction of a scale.
- [`scrolling`](function-scrolling/) — Put a page's body in a scroll area, so a long page scrolls inside the pane and never makes the window taller.

<details markdown="1">
<summary>Module notes and examples</summary>

A panel is a menu of rows (Clefs, Range, Key signatures ...) that each
lead to a page, in a `SlideStack`. This module has the
rows, switches, checklists and editors those pages are made of, and the
panels' shared base classes: `ExerciseSettingsPanel`
(navigation and saving), `ClefsPanel` (a Clefs page) and
`StaffRangePanel` (a Range page per clef). The panels themselves are
in `alto.ui.settings_panel` and `alto.ui.pack_settings_panel`.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> _key_label(2)
'D  ·  2♯'
>>> row = MenuRow("Clefs")
>>> row.title.text()
'<b>Clefs</b>'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"guard_last": "function-guard_last/", "arrow_button": "function-arrow_button/", "rangeeditor": "class-rangeeditor/", "keydiagram": "class-keydiagram/", "keydiagramset_keys": "class-keydiagram/#keydiagramset_keys", "keydiagrampaintevent": "class-keydiagram/#keydiagrampaintevent", "label_with_picture": "function-label_with_picture/", "clef_choice_page": "function-clef_choice_page/", "show_keys": "function-show_keys/", "menurow": "class-menurow/", "menurowattach": "class-menurow/#menurowattach", "menurowfit": "class-menurow/#menurowfit", "switch": "class-switch/", "switchsetchecked": "class-switch/#switchsetchecked", "switchpaintevent": "class-switch/#switchpaintevent", "switchsizehint": "class-switch/#switchsizehint", "togglerow": "class-togglerow/", "togglerowison": "class-togglerow/#togglerowison", "togglerowseton": "class-togglerow/#togglerowseton", "subpage": "function-subpage/", "slidestack": "class-slidestack/", "slidestacksliding": "class-slidestack/#slidestacksliding", "slidestackslide_to": "class-slidestack/#slidestackslide_to", "exercisesettingspanel": "class-exercisesettingspanel/", "exercisesettingspanelrefresh_limits": "class-exercisesettingspanel/#exercisesettingspanelrefresh_limits", "keyboardrangepanel": "class-keyboardrangepanel/", "clefspanel": "class-clefspanel/", "staffrangepanel": "class-staffrangepanel/", "noteanswersettingspanel": "class-noteanswersettingspanel/", "keychecklist": "class-keychecklist/", "keychecklistselected": "class-keychecklist/#keychecklistselected", "keysignaturepage": "class-keysignaturepage/", "keysignaturepageenabled": "class-keysignaturepage/#keysignaturepageenabled", "keysignaturepageselected": "class-keysignaturepage/#keysignaturepageselected", "scalekeypicker": "class-scalekeypicker/", "choicechecklist": "class-choicechecklist/", "choicechecklistselected": "class-choicechecklist/#choicechecklistselected", "buttons_page": "function-buttons_page/", "direction_choices": "function-direction_choices/", "scrolling": "function-scrolling/"}</script>
{% include api-fragments.html %}
