---
title: UI style guide
parent: developer-guide
order: 4
permalink: /developer-guide/ui-style-guide/
baseline: v0.0.2
screens:
  home: Exercise catalog
  note-identification: Exercise workspace
  lesson-workspace: Lesson reader
  database: Database
  stats: Statistics
palette:
  - name: Window, toolbar, and space between tiles
    screen: home
    light: "#efefef"
    dark: "#2a2a2a"
    points: [[85, 400], [85, 400]]
    detail: The empty space to the left of the exercise tiles shows the window color. The toolbar uses the same background.
  - name: Tile, field, and standard button face
    screen: home
    light: "#ffffff"
    dark: "#2a2a2a"
    points: [[424, 364], [424, 364]]
    detail: Look inside the Interval Identification tile, beside its symbol. Standard buttons and form fields use this face color too.
  - name: Main text and inactive navigation icons
    screen: home
    light: "#000000"
    dark: "#ffffff"
    points: [[549, 30], [548, 27]]
    detail: The letters in the window title use the foreground color. Inactive navigation icons use it too.
  - name: Exercise tile outline
    screen: home
    light: "#b0b0b0"
    dark: "#181818"
    points: [[883, 109], [883, 106]]
    detail: The thin top edge of the Clef Basics tile separates its face from the window.
  - name: Lesson tile and standard button outline
    screen: note-identification
    light: "#b0b0b0"
    dark: "#505050"
    points: [[615, 491], [615, 488]]
    detail: Follow the top edge of the E answer button. Lesson tiles use the same outline as these buttons.
  - name: Toolbar search field
    screen: home
    light: "#e5e5e5"
    dark: "#333333"
    points: [[175, 74], [175, 74]]
    detail: The area behind the search hint is slightly darker than the Light window and slightly lighter than the Dark window.
  - name: Toolbar search outline and divider
    screen: home
    light: "#bababa"
    dark: "#595959"
    points: [[297, 55], [297, 52]]
    detail: The thin top edge encloses the search field. Focusing the field changes this edge to the accent color.
  - name: Accent for selections and focused fields
    screen: database
    light: "#308cc6"
    dark: "#006fe2"
    points: [[35, 118], [35, 118]]
    detail: The filled Answers button shows which database table is open. Its blue fill is the selection accent.
  - name: Selected navigation row background
    screen: note-identification
    light: "#c9dbe7"
    dark: "#22384f"
    points: [[256, 153], [255, 152]]
    detail: The tint behind Note Identification marks the current exercise in the sidebar.
  - name: Panel outline and scrollbar thumb
    screen: note-identification
    light: "#b8b8b8"
    dark: "#2f2f2f"
    points: [[333, 422], [333, 422]]
    detail: The vertical thumb at the right edge of the exercise list shows how far the list can scroll. Panel borders use the same color.
  - name: Alternate database row
    screen: database
    light: "#f7f7f7"
    dark: "#272727"
    points: [[646, 232], [646, 232]]
    detail: Compare the background of this row with the rows directly above and below it. Every other database row uses this shade.
  - name: Lesson knowledge check background
    screen: lesson-workspace
    light: "#e6f1f8"
    dark: "#253240"
    points: [[761, 420], [760, 440]]
    detail: The area behind the knowledge-check question and its two answers has a faint accent tint.
  - name: Staff paper
    screen: note-identification
    light: "#ffffff"
    dark: "#ffffff"
    points: [[636, 202], [636, 202]]
    detail: The open area above the staff stays white in both modes.
  - name: Standard notation ink
    screen: note-identification
    light: "#000000"
    dark: "#000000"
    points: [[769, 256], [764, 262]]
    detail: The black notehead and staff lines use notation ink in both modes.
  - name: Correct answer and correct-attempt bar
    screen: stats
    light: "#2e7d32"
    dark: "#2e7d32"
    points: [[388, 460], [388, 456]]
    detail: Green in the weekly question chart counts correct attempts. Correct-answer feedback uses the same green.
  - name: Incorrect answer and incorrect-attempt bar
    screen: stats
    light: "#c62828"
    dark: "#c62828"
    points: [[205, 429], [205, 417]]
    detail: The red cap on a weekly bar counts incorrect attempts. Incorrect-answer feedback uses the same red.
---
Alto **0.0.2** is the visual reference for future releases. Keep the documented appearance until the project owner requests a change. Select either image in a pair to inspect the original PNG at full size. Both images stay visible in either website theme.

## Component map

{% include reference-map.html %}

## Component colors

Both columns use **Settings → Appearance → Theme → Default**. The Light column uses the release’s light palette. The Dark column shows the release running on Ubuntu GNOME with Qt 6.12.0 on Wayland. Default takes colors from Qt, so desktop settings and the platform can affect exact values. For a cross-platform comparison, check which surfaces share a color, where outlines are visible, and which controls take the accent.

<table>
  <thead><tr><th scope="col">Component</th><th scope="col">Light</th><th scope="col">Dark</th></tr></thead>
  <tbody>{% for row in page.palette %}
    <tr><td><a href="#component-map" data-map-row="{{ forloop.index0 }}">{{ row.name }}</a></td>{% assign colors = "light,dark" | split: "," %}{% for mode in colors %}{% assign color = row[mode] %}<td><span class="reference-swatch" style="background-color: {{ color }}" aria-hidden="true"></span><code>{{ color }}</code></td>{% endfor %}</tr>
  {% endfor %}</tbody>
</table>

### Control states

| Control | Appearance and interaction |
|---|---|
| Standard push button | The resting face uses the tile color and a one-pixel outline. Hover blends 25% accent into the face. Keyboard focus thickens the outline to two pixels. Hover and focus use the accent outline in Light and a lighter graphite outline in Dark. Pressed or checked buttons fill with the accent. Disabled buttons blend into the window and their labels lose contrast. |
| Toolbar and navigation | Inactive toolbar symbols use the window text color. The active view uses an accent-colored symbol. A selected exercise, category, or settings row puts accent text on a soft background made from 80% window color and 20% accent. The toolbar search outline switches to the accent when its text field has focus. |
| Text field, dropdown, and number field | Shared form fields have a base-colored face, rounded corners, and a heavier lower edge. Focus accents the border. The dropdown’s open outer popup is rounded, with a panel-colored list and an accent highlight on the selected item. A number field centers its value beside two stacked arrows. |
| Checkbox and radio button | An empty indicator uses the panel color and a visible outline. Hover accents the outline. A checked box shows a white tick on accent, and a selected radio shows a white dot inside an accent ring. Disabled indicators use a muted outline or a faded accent. |
| Menu and tab | The application menu blends 7% text color into the window color. Its highlighted row uses a solid accent with contrasting text. In a settings tab strip, the active tab uses accent text and a thin accent underline. |

## Profiles

In **Welcome to Alto**, the name field and Create profile button sit on the window gray. In the Light capture, the focused field has a colored edge. In the returning-profile chooser, the list has its own panel surface, and the selected name has a tinted background. Check the empty list area as well as the selected row.

{% include reference-pair.html screen="profile-create" title="Profile creation" alt="Welcome dialog with a focused name field and Create profile button." %}

{% include reference-pair.html screen="profile-picker" title="Profile chooser" alt="Ada selected in the profile list above the new-profile field." %}

## Exercise and lesson catalogs

Compare the gap between cards, the center of a card, and the search field above the grid. In Light these are three distinct grays from white to pale gray. In the Dark capture, the tile face and the window share the same charcoal. The outline separates each tile from the space around it. Exercise cards have a near-black outline. Lesson cards have a lighter graphite outline. Both catalogs use the text color for the central musical icon and gray for the category and description.

{% include reference-pair.html screen="home" title="Exercise catalog" alt="Search bar above a grid of exercise tiles with musical icons." %}

{% include reference-pair.html screen="lesson-tiles" title="Lesson catalog" alt="Two rows of lesson tiles below the active Lessons toolbar icon." %}

The open filter pane shows all three checkbox states. Fully checked groups carry a tick, partially checked groups carry a dash, and empty boxes retain their outline. The filter icon uses the accent while a filter is active.

{% include reference-pair.html screen="filtered-practice" title="Catalog filters" alt="Two exercise tiles beside the open category tree with checked and unchecked items." %}

## Exercise workspace and feedback

In Note Identification, the selected exercise has a softly tinted row in the left sidebar. The staff uses black notation on white paper in both modes. The letter buttons below it use the theme’s button face, so in dark mode the boundary between the paper and the answer controls is particularly clear.

{% include reference-pair.html screen="note-identification" title="Staff exercise" alt="A single note on white staff paper above the letter-name buttons." %}

The **Classic** keyboard has off-white natural keys (`#fbfbfc`), near-black accidentals (`#1c1c20`), and a dark case (`#2b2b30`) in both modes. The key named in the question is highlighted with the accent. The Circle of Fifths provides a second comparison for an exercise with its own colored drawing. Check its labeled segments separately from the themed answer buttons underneath.

{% include reference-pair.html screen="keyboard" title="Keyboard exercise" alt="One piano key highlighted above two rows of answer buttons." %}

{% include reference-pair.html screen="circle-of-fifths" title="Circle of Fifths" alt="Colored sectors of the circle above a grid of answer choices." %}

After a correct answer, the written note turns green (`#2e7d32`) in either theme. In the self-grading view the letter buttons fade, and the grade buttons below them remain available. For exercises that animate correct pitches, the green highlight follows the sounding notes and clears at the end of playback.

{% include reference-pair.html screen="self-grading" title="Correct answer and review grades" alt="Green note, disabled letter choices, and Hard, Good, and Easy review buttons." %}

## Lesson reader and glossary

In the lesson reader, the selected outline row uses the navigation tint. The knowledge check has a lighter accent wash and a narrow solid accent rule at its left edge. In the glossary, the term list, definition, and related-activity area use the window color inside thin panel borders. The harmonic minor example shows the white notation paper, and the practice tiles below it reuse the exercise card styling.

{% include reference-pair.html screen="lesson-workspace" title="Lesson reader" alt="Lesson outline beside High and low pitches, its sound example, and a tinted knowledge check." %}

{% include reference-pair.html screen="glossary" title="Glossary" alt="Harmonic minor scale selected with a definition, staff example, and related practice tiles." %}

## Statistics

The six totals sit on panel-colored tiles. In the volume chart, correct attempts are green (`#2e7d32`) and incorrect attempts are red (`#c62828`). The accuracy line and speed bars use the accent. The calendar uses a neutral square for a day with no reviews and increasingly strong green for busier days. These data colors have the same meanings in both modes.

{% include reference-pair.html screen="stats" title="Statistics overview" alt="Summary tiles, stacked correct and incorrect attempts, daily accuracy, and speed bars." %}

{% include reference-pair.html screen="stats-heatmap" title="Review calendar" alt="Calendar of green review counts above the table of questions needing practice." %}

## Database and question preview

The selected table button uses solid accent. Compare adjacent rows in the body of the table. Light alternates white and `#f7f7f7`, and Dark alternates `#2a2a2a` and `#272727`. Column headings remain distinct above both. Opening a saved answer brings up a separate dialog with white notation paper, ordinary window-colored space for the answer details, and buttons along the bottom.

{% include reference-pair.html screen="database" title="Database · Answers" alt="Recorded attempts with alternating row colors under the selected Answers button." %}

{% include reference-pair.html screen="database-questions" title="Database · Questions" alt="Question summaries with counts and scheduling details under the selected Questions button." %}

{% include reference-pair.html screen="question-preview" title="Saved question" alt="Chord on a staff above the saved answer, timing, and playback controls." %}

## Application settings

In **Appearance → Theme**, compare the selected category, selected family, and selected thumbnail. The two lists use a soft navigation tint. The active theme preview has a strong accent outline. Each miniature depicts its own palette, including the split light/dark preview for System. In **Notation style**, the selected card has a solid accent surround while the sheet inside the card stays white.

{% include reference-pair.html screen="settings-theme" title="Theme chooser" alt="Theme families beside Light, Dark, and split System previews, with an outline around the current choice." %}

{% include reference-pair.html screen="settings" title="Notation style" alt="A selected notation card among white-paper previews of music fonts." %}

**Sound** shows a selected instrument row alongside its detail panel. **Practice** shows checkboxes, editable limits, and a box around the selected profile’s options. The response-time dialog uses the accent for the filled length of each bar and a neutral track for the remaining width. **Updates** shows how enabled and disabled choices read against an open area of window color.

{% include reference-pair.html screen="settings-sound" title="Sound" alt="Instrument list with Viola selected beside its description and test controls." %}

{% include reference-pair.html screen="practice-settings" title="Practice settings" alt="Scheduling options, checkboxes, and daily limits for the selected exercise." %}

{% include reference-pair.html screen="response-times" title="Response-time grading" alt="Two percentile settings and a horizontal distribution of answer times." %}

{% include reference-pair.html screen="settings-updates" title="Updates" alt="Update preferences and dependent controls beside the selected Updates category." %}

## Anki export

The exporter reuses the accent for selected checkboxes and the active export action. Compare those controls against the neutral pane containing the sample question. The export summary places the filename and deck tree on panel-colored surfaces, with a filled primary action and a neutral Cancel button.

{% include reference-pair.html screen="anki-exporter" title="Anki exporter" alt="Exercise selection tree beside a preview of a question to export." %}

{% include reference-pair.html screen="anki-export-summary" title="Export summary" alt="Filename field, deck tree, card count, and final Export button." %}

## Release comparison

1. Open the same screen at the same window size, theme, and display scale. Select a reference image to view it at its original dimensions. Compare solid pixels inside a surface or along a straight border. Rounded corners and glyph edges contain intermediate colors.
2. For a quick check, use the **1100 × 720 exercise catalog**. Measured from the top-left of either PNG, pixel `(10, 10)` is the window and `(85, 65)` is the search fill. Sample the top tile outline and the face just below it at `(200, 109)` and `(200, 110)` in Light, or `(200, 106)` and `(200, 107)` in Dark. Match these to the component table.
3. With Alto set to **System**, switch the desktop from light to dark and back while a lesson tile and the search field are visible. Check the tile face, border, musical glyph, toolbar icons, and search outline after each switch. Repeat with search focused and text entered. Its accent outline, text, and focus should survive the switch.
4. Keep release-candidate captures in a separate directory. On a GNOME Wayland session, run `QT_QPA_PLATFORM=wayland .venv/bin/python scripts/screenshots.py --require-native-theme --only home lesson-tiles stats --out /tmp/alto-candidate`. This option stops the capture if Qt cannot supply the requested mode. The reference PNGs live in `docs/assets/ui-reference/v0.0.2/`, outside the regular screenshot refresh. For an explicitly requested visual change, record the affected component and release, and keep the earlier reference available.

The Light images come from the 0.0.2 release documentation, with the Theme chooser captured separately from the tag. All Dark images were captured from the same tagged source using a temporary profile, the native desktop palette, and one image pixel per logical pixel. The Theme chooser shows **Default → Dark** selected. For the palette and widget implementation, see [Styling beyond QtWidgets]({{ '/guide/styling/' | relative_url }}).
