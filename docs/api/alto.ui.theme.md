---
title: alto.ui.theme
parent: api
package: alto.ui
api_components: [{"title": "CustomTheme", "url": "/api/alto.ui.theme/class-customtheme/"}, {"title": "ThemeRecord", "url": "/api/alto.ui.theme/class-themerecord/"}, {"title": "apply_theme", "url": "/api/alto.ui.theme/function-apply_theme/"}, {"title": "custom_theme", "url": "/api/alto.ui.theme/function-custom_theme/"}, {"title": "delete_user_theme", "url": "/api/alto.ui.theme/function-delete_user_theme/"}, {"title": "families", "url": "/api/alto.ui.theme/function-families/"}, {"title": "family_of", "url": "/api/alto.ui.theme/function-family_of/"}, {"title": "hsl_hex", "url": "/api/alto.ui.theme/function-hsl_hex/"}, {"title": "new_family_id", "url": "/api/alto.ui.theme/function-new_family_id/"}, {"title": "preview_colors", "url": "/api/alto.ui.theme/function-preview_colors/"}, {"title": "save_theme", "url": "/api/alto.ui.theme/function-save_theme/"}, {"title": "save_user_records", "url": "/api/alto.ui.theme/function-save_user_records/"}, {"title": "saved_theme", "url": "/api/alto.ui.theme/function-saved_theme/"}, {"title": "scheme_of", "url": "/api/alto.ui.theme/function-scheme_of/"}, {"title": "seeded_themes", "url": "/api/alto.ui.theme/function-seeded_themes/"}, {"title": "system_is_dark", "url": "/api/alto.ui.theme/function-system_is_dark/"}, {"title": "theme_of", "url": "/api/alto.ui.theme/function-theme_of/"}, {"title": "theme_palette", "url": "/api/alto.ui.theme/function-theme_palette/"}, {"title": "upsert_user_theme", "url": "/api/alto.ui.theme/function-upsert_user_theme/"}, {"title": "user_records", "url": "/api/alto.ui.theme/function-user_records/"}, {"title": "user_themes", "url": "/api/alto.ui.theme/function-user_themes/"}, {"title": "variant_key", "url": "/api/alto.ui.theme/function-variant_key/"}]
permalink: /api/alto.ui.theme/
---
{% raw %}
The color theme: follow the system, force light or dark, or use a theme
with colors of its own.

## Classes

- [`CustomTheme`](class-customtheme/) — A theme with colors of its own.
- [`ThemeRecord`](class-themerecord/) — A theme the user made, as it is saved: its key, its name, and the colors of its light and dark versions.

## Functions

- [`hsl_hex`](function-hsl_hex/) — Turn a color given as hue, saturation and lightness into "#rrggbb".
- [`seeded_themes`](function-seeded_themes/) — Make the light and the dark theme of a seed: neutrals tinted by one hue, and an accent of another.
- [`family_of`](function-family_of/) — Split a theme's key into its family and which version of it that is.
- [`variant_key`](function-variant_key/) — Give the key of one version of a family.
- [`user_records`](function-user_records/) — Read the themes the user has made, as they are saved.
- [`save_user_records`](function-save_user_records/) — Save the themes the user has made.
- [`new_family_id`](function-new_family_id/) — Make the key for a new theme of the user's.
- [`upsert_user_theme`](function-upsert_user_theme/) — Save a theme the user made, replacing the one with the same key if there is one.
- [`delete_user_theme`](function-delete_user_theme/) — Remove a theme the user made.
- [`theme_of`](function-theme_of/) — Build a custom theme from its saved or preview colors.
- [`user_themes`](function-user_themes/) — Give the themes the user has made, light and dark versions of each.
- [`families`](function-families/) — List every theme there is to choose, the user's own first.
- [`custom_theme`](function-custom_theme/) — Find a theme with colors of its own, one of the built-in ones or one the user made.
- [`scheme_of`](function-scheme_of/) — Say which color scheme a theme uses: light, dark, or the desktop's own.
- [`preview_colors`](function-preview_colors/) — Pick the colors for the small picture of a theme in the settings.
- [`theme_palette`](function-theme_palette/) — Build the Qt palette of a theme with colors of its own.
- [`saved_theme`](function-saved_theme/) — Return the theme the user chose.
- [`save_theme`](function-save_theme/) — Remember the theme the user chose.
- [`system_is_dark`](function-system_is_dark/) — Say whether the desktop is set to dark, as long as the app is not forcing a color scheme of its own.
- [`apply_theme`](function-apply_theme/) — Switch the application's color scheme and rebuild the stylesheet from the new palette.

<details markdown="1">
<summary>Module notes and examples</summary>

A theme with colors of its own is a `CustomTheme`: a fixed palette that
is light or dark whatever the desktop is set to.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> [key for key, label in THEMES][:4]
['system', 'light', 'dark', 'studio']
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"customtheme": "class-customtheme/", "hsl_hex": "function-hsl_hex/", "seeded_themes": "function-seeded_themes/", "family_of": "function-family_of/", "variant_key": "function-variant_key/", "themerecord": "class-themerecord/", "user_records": "function-user_records/", "save_user_records": "function-save_user_records/", "new_family_id": "function-new_family_id/", "upsert_user_theme": "function-upsert_user_theme/", "delete_user_theme": "function-delete_user_theme/", "theme_of": "function-theme_of/", "user_themes": "function-user_themes/", "families": "function-families/", "custom_theme": "function-custom_theme/", "scheme_of": "function-scheme_of/", "preview_colors": "function-preview_colors/", "theme_palette": "function-theme_palette/", "saved_theme": "function-saved_theme/", "save_theme": "function-save_theme/", "system_is_dark": "function-system_is_dark/", "apply_theme": "function-apply_theme/"}</script>
{% include api-fragments.html %}
