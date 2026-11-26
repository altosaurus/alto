---
title: alto.ui.instrument_picker
parent: api
package: alto.ui
api_components: [{"title": "InstrumentPicker", "url": "/api/alto.ui.instrument_picker/class-instrumentpicker/"}, {"title": "format_size", "url": "/api/alto.ui.instrument_picker/function-format_size/"}, {"title": "load_instrument", "url": "/api/alto.ui.instrument_picker/function-load_instrument/"}, {"title": "save_instrument", "url": "/api/alto.ui.instrument_picker/function-save_instrument/"}, {"title": "sound_picker_layout", "url": "/api/alto.ui.instrument_picker/function-sound_picker_layout/"}, {"title": "tokens", "url": "/api/alto.ui.instrument_picker/function-tokens/"}]
permalink: /api/alto.ui.instrument_picker/
---
{% raw %}
Choosing the instrument that plays notes, with a summary of what each
one is made from.

## Classes

- [`InstrumentPicker`](class-instrumentpicker/) — The instruments in a box on the left; on the right, what the selected one is made from.

## Functions

- [`sound_picker_layout`](function-sound_picker_layout/) — Place sound choices beside their detail card in Settings.
- [`load_instrument`](function-load_instrument/) — Apply the saved instrument.
- [`save_instrument`](function-save_instrument/) — Remember the instrument in use.
- [`tokens`](function-tokens/) — Return the summary page's colors.
- [`format_size`](function-format_size/) — Write a file size the way the instrument page shows it.

<details markdown="1">
<summary>Module notes and examples</summary>

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> format_size(2_500_000)
'2.5 MB'
>>> list(PREVIEW)
[74, 75, 72, 71]
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"sound_picker_layout": "function-sound_picker_layout/", "load_instrument": "function-load_instrument/", "save_instrument": "function-save_instrument/", "tokens": "function-tokens/", "format_size": "function-format_size/", "instrumentpicker": "class-instrumentpicker/", "instrumentpickerselect": "class-instrumentpicker/#instrumentpickerselect", "instrumentpickershow_group": "class-instrumentpicker/#instrumentpickershow_group", "instrumentpickerchangeevent": "class-instrumentpicker/#instrumentpickerchangeevent", "instrumentpickeruse": "class-instrumentpicker/#instrumentpickeruse", "instrumentpickerpreview": "class-instrumentpicker/#instrumentpickerpreview"}</script>
{% include api-fragments.html %}
