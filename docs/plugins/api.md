---
title: Plugin API
parent: plugins
order: 1
permalink: /plugins/api/
---

Alto’s plugin API is the contract between an instrument pack and the app. The author describes the instrument, its media, and its exercises in a UTF-8 JSON file named `pack.json`. Alto reads that file to draw the instrument, generate questions, check answers, and play feedback. You can build a pack with a text editor and your media files.

## Minimum working pack

Start with a folder containing `pack.json` and a picture named `instrument.png`. The example below assumes the picture shows a keyboard with a key at pixel `[100, 80]`. Choose a point on a key in your own picture, measured from its top-left corner.

```json
{
  "format": 2,
  "id": "keyboard-parts",
  "name": "Keyboard Parts",
  "instruments": [
    {"id": "keyboard", "name": "Keyboard", "image": "instrument.png"}
  ],
  "exercises": [
    {
      "id": "name-the-part",
      "title": "Parts of a Keyboard",
      "type": "image-choice",
      "instrument": "keyboard",
      "questions": [
        {
          "prompt": "Which part is marked?",
          "point": [100, 80],
          "choices": ["Key", "Case"],
          "answer": "Key"
        }
      ]
    }
  ]
}
```

## What Alto checks

- **Manifest.** Use the integer `2` for `format`, a nonblank pack `name`, and a pack `id` unique among installed packs. Include at least one instrument and one exercise. A pack ID such as `keyboard-parts` uses lowercase letters and digits, with single hyphens between words.
- **Instruments and media.** Each instrument needs its own ID, a name, and a readable PNG, WebP, or JPEG. Write paths relative to `pack.json` and include every file you reference. Recordings are optional. When you supply them, map each pitch to a mono 16-bit PCM WAV file.
- **Exercises.** Give each exercise a unique ID, a plain-text title, and the ID of an instrument in the same pack. For `image-choice`, each question needs a prompt, a point inside the picture, at least two distinct choices, and an answer that matches one choice exactly. For `fingerboard-notes`, calibrate at least two strings on the instrument and list the pitches to practice on each selected string. For `keyboard-intervals`, declare at least one keyboard on the instrument.
- **Optional content.** Alto also validates any lessons, glossary entries, and links you include. Use IDs from the same pack when linking these activities. An invalid entry prevents the whole pack from loading.

To try the example, zip `pack.json` and `instrument.png` together so both appear at the root of the ZIP. Install it through **Menu → Tools → Plugins… → Install plugin from file…** and restart Alto. Open **Instruments → Parts of a Keyboard** and choose **Key**. Loading a pack locally requires no listing in the registered plugins table.

## Plugin registration

To request a listing in the [registered plugins table]({{ '/plugins/' | relative_url }}#registered-plugins), open an issue in Alto’s GitHub repository. In the issue, describe what your plugin does and include a link to its repository. [Open a registration issue](https://github.com/altosaurus/alto/issues/new?template=plugin-registration.yml).

Choose a plugin name and a Pack ID that are available in Alto’s registry. Names are compared without regard to capitalization or extra spaces, so “Viola Studio” and “viola  studio” clash. Use the exact top-level `id` from `pack.json` as the Pack ID. It can contain lowercase letters and digits, with single hyphens between words. If either field belongs to another plugin, choose a different value before registration. If you change the Pack ID, update the manifest in your release ZIP as well.

### Registry updates between releases

1. Submit the registration form and check the **Rights and licenses** statement. The issue number is the proposed install code. For example, issue **#1001** corresponds to code **1001**.
2. A maintainer reviews the submission and applies the `plugin-approved` label. The **Register plugin** workflow checks the approved form and verifies the name, Pack ID, and code against current and historical registrations. It prepares a branch with the entry for `docs/site-root/plugins.json`.
3. In **Actions → Register plugin**, open the run for the issue. Select **Open registration pull request** in the run summary, review the change, and select **Create pull request**. If the author corrects the form, remove and reapply the label after reviewing the edits. The workflow refreshes the same branch and any open pull request.
4. A maintainer merges the reviewed change. After the docs deployment, the code appears in the registry and works in Alto. The same code and Pack ID carry forward across plugin releases.

For repository setup, create the `plugin-approved` label. The workflow uses **Contents: write** to publish its registration branch. A maintainer opens the pull request with their own GitHub account.

Earlier names and Pack IDs stay reserved to their original registration after a rename or removal. To check a proposed registry change locally, run `python3 scripts/check_plugin_registry.py --base main` from the repository root. A registry entry for issue **#1001** could look like this.

```json
{
  "id": "example-strings",
  "code": "1001",
  "name": "Example Strings",
  "description": "Practice naming notes on open strings.",
  "repository": "https://github.com/example/strings",
  "metadata": "https://raw.githubusercontent.com/example/strings/main/alto-plugin.json"
}
```

The docs workflow publishes the registry at `/alto/plugins.json`. Each version of the Plugins page that supports the registry reads it when opened. After deployment, refresh the page to see a new registration. Each name opens a details page inside Alto’s docs.

### Release ZIPs for installation and updates

Attach the installable pack ZIP to the repository’s latest published GitHub release. Put `pack.json` at the root of the ZIP and set its `id` to the registered pack ID. If the release has several ZIP assets, name the pack asset `<pack-id>.zip` so Alto can select it. [GitHub releases](https://docs.github.com/en/rest/releases/releases#get-the-latest-release).

In **Menu → Tools → Plugins…**, enter the code under **Install plugin by code…**. To update, select the installed ZIP and choose **Update selected plugin**. Alto looks up the registration, checks the latest release, and validates the new pack before replacing the installed ZIP. Existing ZIP installs with the registered pack ID can update the same way. Editable folders stay under the author’s control. A successful install or update offers a restart.

### Plugin details and releases

Alto’s plugin details page displays the README from the default branch of your registered GitHub repository. It also shows your registration code and a link to the repository. Update the README in your repository to revise what readers see in Alto’s docs.

To keep the details page current, publish a JSON file in your plugin repository and include its raw HTTPS URL in your registration issue. Use a URL that follows your release branch so the same address serves each update. The file must be publicly readable by a browser on the Alto docs site. A raw GitHub file URL works for a public repository. If you host the file yourself, allow cross-origin reads from the docs site.

```json
{
  "about": "Identify the four open strings by ear, then practice finding them on the fingerboard.",
  "version": "1.2.0",
  "compatible_alto": "0.4.x",
  "documentation": "https://example.org/strings/guide/",
  "download": "https://example.org/strings/releases/1.2.0/strings.zip"
}
```

All five fields are optional. Use plain text for the description and versions, and absolute HTTPS URLs for the links. When you release a new plugin version, update this file along with the ZIP. Alto’s details page requests the file each time a reader opens it, so your release information can change between Alto releases. The registered description and repository link remain available if the file is missing or temporarily unavailable.

## Manifest reference

| Field | Meaning |
| --- | --- |
| `format` | The integer `2` selects this version of the pack API. |
| Pack `name` | Required. Enter a nonblank text string at the top level, such as `"name": "Viola Instrument Pack"`. Alto shows it during installation and removal. |
| Pack `id` | Unique among installed packs. Use lowercase letters, digits, and single hyphens between words. The same spelling rules apply to instrument and exercise IDs. |
| `instruments` | A nonempty list. Each instrument requires `id`, `name`, and `image`. Instrument IDs are unique within the pack. |
| `strings` | Required for `fingerboard-notes`. Two or more distinct open pitches in ascending order. Each entry requires `open`, `nut`, and `bridge`. Coordinates must lie inside the source image. |
| Pitch spelling | Uppercase A through G, optional `#` or `b`, then an octave from 0 through 8. Examples include `C4` (middle C), `F#4`, and `Bb3`. |
| `correct_answer_animation` | Optional per instrument. Set `file` to a pack-relative animated GIF and `anchor` to `image` or `string`. A string anchor requires calibrated strings. |
| `views` | Optional per instrument. An object from a view name to a pack-relative picture, such as `{"back": "images/viola-back.webp"}`, for up to four extra pictures of the instrument. Each is a PNG, WebP, or JPEG of at most 16 megapixels, and it can have its own size. A picture question or lesson picture names one with `view`, and its `point` and `focus` are then in that picture's pixels. Strings, the ruler, and the correct-answer animation always use the main `image`. |
| `positions` | Optional per instrument with strings. A list of up to 12 objects, each with a plain-text `name` of at most 12 characters and a whole number of `half_steps` above the open string, from 1 to 36, in ascending order. Alto labels the ruler above the neck with them. The ruler always shows a tick for each half step up to the octave. Without `positions` it shows only those ticks. The viola example lists `1st` at 2, `2nd` at 3, `3rd` at 5, `4th` at 7, `5th` at 8, `6th` at 10, and `7th` at 12. Choose positions that match your instrument. |
| `keyboards` | Optional per instrument. A list of up to four keyboards that Alto draws itself, for exercises that highlight keys. Each needs a plain-text `name` (at most 40 characters, unique on the instrument) and `lowest` and `highest`, the natural keys at either end, such as `E1` and `F6`. Alto stacks the keyboards in the order you list them, top to bottom, so list an upper manual before a lower one. |
| `keyboard_style` | Optional per instrument with keyboards. How the drawn keys look. Any of `white` and `black`, each a list of two `#rrggbb` colors for the top and the bottom of a natural or a sharp key; `white_edge`, `black_edge`, `case` and `cap` (the cap over each sharp key), each one `#rrggbb` color; and the numbers `narrow` (how wide sharp keys are compared with a piano's, 0.5 to 1.5), `gap` (pixels between natural keys, 0 to 4), `round` (how much the keys' lower corners are rounded, 0 to 10) and `length` (how long a natural key is, in key widths, 2 to 6.5). Fields you leave out use Alto's classic keyboard. Without `keyboard_style`, the keys are drawn in the learner's own keyboard style. The harpsichord example draws ebony naturals and bone-capped sharps. |
| `lessons` | Optional list of up to six lessons for Alto's Lessons page. See [Lessons](#lessons) for the fields. Each lesson's `exercise` must be an `id` in this pack's `exercises`. |
| `kind` | Optional per instrument. Plain text of at most 30 characters that says what sort of instrument it is, such as `harpsichord` or `viola`. Alto uses it to group sounds of the same kind when a learner chooses the sound for an exercise. Without it, the instrument is grouped with no others. |
| `sustained` | Optional per instrument, `true` or `false` (default `false`). Set it to `true` for bowed or blown sounds, so each note ends as the next begins. Leave it off for struck or plucked sounds, which ring on. |
| `samples` and `gain` | Optional per instrument. Exact recorded pitches play directly. Other notes use the nearest recording. Omitting samples uses the learner’s selected Alto sound. Gain sets the instrument’s playback level, greater than 0 and at most 1 (default 1). |
| `sound_info` | Optional per instrument, for the summary under **Menu → Settings → Sound → Instruments**. Use plain text, at most 800 characters each, in any of `summary`, `source`, `source_url` (an `https` link), `performer`, `recorded`, `includes`, `terms`, and `note`. Say "not stated" when you do not know the performer. Alto adds the pack name, the note range, and the size itself. The viola example credits TinySOL, its recording location and years, its CC BY 4.0 terms, and how the takes were prepared. |
| Exercise `description` and `prompt` | Optional. `description` is one to a few sentences of plain text, at most 400 characters, shown with the exercise. `prompt` is the question on each card of a `fingerboard-notes` exercise, at most 120 characters. Without them Alto uses short neutral wording that names the strings. Image-choice questions always carry their own `prompt`. |
| Picture question `view`, `marker_size`, and `focus` | Optional on each `image-choice` question. `view` names one of the instrument's `views`; leave it out for the main picture. `marker_size` is the dot's diameter in picture pixels, from 6 to 200; leave it out for a large part. `focus` is `[left, top, width, height]` in picture pixels, at least 40 wide and tall and inside the picture, and it must contain the marked `point`. Alto shows only that region, so a small part such as a nut or a string is easy to see. Without `focus` the whole picture is shown. |
| `exercises` | A nonempty list. Each exercise requires a unique `id`, a plain-text `title`, a `type`, and an `instrument` ID from the same pack. Use `notes` for `fingerboard-notes`, `questions` for `image-choice`, and the fields described under [Keyboard intervals](#keyboard-intervals) for `keyboard-intervals`. |
| Exercise `icon` and `lessons` | Optional. `icon` is an SVG file for the exercise's tile. `lessons` lists up to five lesson `id`s that teach it. See [Linking lessons and exercises](#linking-lessons-and-exercises). |
| `glossary` | Optional list of up to 40 glossary entries. See [Glossary entries](#glossary-entries). |
| Exercise `settings` | Optional on `fingerboard-notes`. An object with any of `sound` (a label of at most 30 characters), `range` (one clef name), `accidentals` and `octave` (each `true`). See [Settings for a note exercise](#settings-for-a-note-exercise). |
| `notes` | Each key is an open pitch from the selected instrument. Its list contains the notes to practice on that string, from open through one octave above it. The same pitch on two strings makes two distinct cards. |
| `questions` | One or more questions. Each has a plain-text `prompt`, a `point` in original image pixels from the top left, at least two distinct plain-text `choices`, and an `answer` exactly matching a choice. Optional `note` sets the pitch for correct-answer playback. |
| Asset paths | Relative to `pack.json`, using forward slashes. Keep all files inside the pack. Each referenced file can be up to 64 MiB, with 256 MiB total. Images can be up to 16 megapixels. |

You can change the pack’s display name. Keep the pack, instrument, and exercise IDs when updating existing content. Alto uses them to resolve assets and associate practice history with the same exercise. A new title or file location can use the same IDs.

## Settings for a note exercise

A `fingerboard-notes` exercise can offer its learners settings. Alto draws them in the same pane as its own exercises' settings, remembers each learner's choices, and applies them to the questions. You choose which of four controls appear by listing them under `settings` in the exercise:

```json
"settings": {"sound": "Viola sound", "range": "alto", "accidentals": true, "octave": true}
```

- **`sound`** adds a row with the label you give (at most 30 characters) that opens a list of instruments. The exercise plays your instrument's recordings until the learner picks another. The list shows the instruments that came with your plugin first, then other installed instruments of the same `kind` (other harpsichords for a harpsichord), then every other installed instrument, each group under its own heading.
- **`range`** adds a Range row for one clef, such as `"alto"`, where the learner moves the lowest and highest note asked. The selector never goes beyond the notes you list under `notes`, and Reset restores all of them.
- **`accidentals`** adds an Accidentals switch. On, Alto also asks each note between the ones you list on a string, written as a sharp and accepted as its flat, and offers sharps and flats as answers.
- **`octave`** adds an Octave switch. On, the answer includes the written octave, as in **D4**, and Alto asks for the octave after the note name.

List only the controls your exercise needs. Without `settings`, an exercise has none, and a picture exercise cannot have any. Alto keeps the learner's practice history for the defaults: switches that start off, your own sound, and every listed note.

## Lessons

A pack can add lessons to Alto's **Lessons** page. A plugin lesson works like Alto's own: a short list of steps, each with a heading, a few paragraphs, and optionally a picture of your instrument, notes to hear, and a **Knowledge check**. Your lessons are listed after Alto's, under the category you name, and the last step offers practice in one of your exercises. The viola example adds **Parts of the Viola** and **Finding Notes on the Viola**.

```json
"lessons": [
  {
    "id": "finding-notes",
    "title": "Finding Notes on the Viola",
    "about": "Learn where the notes fall on each string.",
    "summary": "Name the note at any spot on the strings.",
    "category": "Viola",
    "exercise": "first-position",
    "steps": [
      {
        "title": "The open strings",
        "picture": {"instrument": "bowed-viola", "string": "D4", "note": "D4"},
        "hear": [["C3"], ["G3"], ["D4"], ["A4"]],
        "hear_label": "Hear the four open strings",
        "hear_instrument": "bowed-viola",
        "text": ["A string played without pressing it down is an **open string**."],
        "task": {
          "prompt": "Which open string sounds the highest?",
          "choices": ["C string", "G string", "D string", "A string"],
          "answer": "A string",
          "hint": "Listen again.",
          "explanation": "The A string is the highest."
        }
      }
    ]
  }
]
```

| Field | Meaning |
| --- | --- |
| Lesson `id`, `title`, `about`, `summary`, `category` | Required except `category`. The title is at most 80 characters, `about` at most 300, `summary` at most 120, and `category` at most 40. A lesson with no `category` is listed under the pack's name. A pack can have up to six lessons. |
| Lesson `exercise` and `related_exercises` | `exercise` is the `id` of one of this pack's exercises, which the last step offers for practice. `related_exercises` optionally lists up to five other exercises from the pack. |
| Lesson `steps` | From 1 to 14 steps. Alto adds the practice buttons to the last one. |
| Step `title` and `text` | The heading, and 1 to 8 paragraphs of plain text of at most 700 characters. Wrap a term you are defining in double asterisks, such as `**nut**`, to show it in bold. Markup is not allowed. |
| Step `picture` | Optional. Give `instrument`, `string`, and `note` to show a note on a string, with Alto's ruler and dot. Or give `instrument` and `point`, with the optional `view`, `marker_size`, `focus`, and `marker`, to mark a place on the picture as an exercise question does. Set `marker` to `false` to show the picture with no dot. |
| Step `hear`, `hear_label`, `hear_instrument` | Optional. `hear` is up to 12 chords, each a list of one to four note names, played by the **Hear** button. `hear_instrument` is the `id` of one of this pack's instruments that has samples. Without it, Alto plays the learner's own choice of sound. |
| Step `task` | Optional knowledge check, with a `prompt`, a `hint` for a wrong answer, an `explanation`, and either two to six `choices` with the `answer` that matches one exactly, or `targets` to click on the step's picture (see below). A wrong answer gets the hint, a second wrong answer gets the answer, and nothing is scored. |
| Lesson `icon` | Optional. An SVG file for the lesson's tile (see [Icons](#icons-for-tiles)). Without it, the tile uses its primary exercise's icon. |

Write lessons by the same rules as Alto's own: teach one musical idea, aim for twenty minutes or less, define each new term in plain language where it first appears, and order your lessons from beginner to advanced. See [Designing lessons and exercises]({{ '/development/' | relative_url }}#designing-lessons-and-exercises).

### Click the picture

A knowledge check can ask the learner to click a place on the step's picture instead of choosing a button. Give the task `targets` in place of `choices` and `answer`:

```json
"task": {
  "prompt": "Click one of the pegs.",
  "targets": [
    {"point": [192, 282], "radius": 45},
    {"point": [287, 274], "radius": 45}
  ],
  "hint": "The pegs are the dark knobs on either side of the pegbox.",
  "explanation": "That is a peg."
}
```

Each target is a circle: its `point` and its `radius` are in the picture's own pixels, in the `view` the step shows. A click inside any target is right. List up to four. The step's picture must set `marker` to `false`, so the dot does not give the answer away. After a right answer, or the second wrong one, Alto marks the target.

### Linking lessons and exercises

A lesson names its exercises with `exercise` and `related_exercises`. An exercise can name its lessons from the other end with `lessons`, a list of up to five lesson `id`s:

```json
{"id": "first-position", "type": "fingerboard-notes", "lessons": ["finding-notes", "parts-of-the-viola"]}
```

Alto shows both: the lesson's last step offers each linked exercise as practice, and the exercise gets a **Reference** pane (the book button beside Help) with a button for each linked lesson, as Alto's own exercises do. An exercise with no linked lesson has no Reference pane.

### Icons for tiles

Set an exercise or lesson's `icon` to the path of an SVG file in the pack. Alto uses the same SVG for its tile and navigation row. Draw it as a single shape so it stays legible at the smaller navigation size. Alto renders it in the current theme's text color.

- The root must be `<svg viewBox="0 0 24 24">`, and the file at most 100 KB.
- Use only `g`, `path`, `circle`, `ellipse`, `rect`, `line`, `polyline`, and `polygon`, with geometry and paint attributes. Scripts, styles, images, links, and entity declarations are refused.
- Every color is replaced by the theme's ink. Use `fill="none"` for a part that is not filled.

A lesson with no `icon` uses its primary exercise's. The viola's icon is the outline of its own photograph, with its f-holes, fingerboard, and tailpiece cut out.

## Glossary entries

A pack can add terms to Alto's **Glossary**. Entries are listed alphabetically with Alto's own, and each links to the lessons and exercises that go with it, shown as tiles under the entry. List them under `glossary`:

```json
"glossary": [
  {
    "term": "scroll",
    "definition": "The **scroll** is the curled, carved end of the viola.",
    "guide": "Look at the far left of the picture.",
    "picture": {"instrument": "bowed-viola", "point": [100, 385], "marker_size": 80, "focus": [0, 220, 480, 330]},
    "caption": "The scroll",
    "exercises": ["viola-parts"],
    "lessons": ["parts-of-the-viola"]
  }
]
```

| Field | Meaning |
| --- | --- |
| `term` and `definition` | Required. The term is at most 40 characters, listed as you write it. The definition is at most 500 characters of plain text, with `**bold**` for the term itself. |
| `guide` | Optional, at most 500 characters: how to recognize or use the term. |
| `picture` and `caption` | Optional. `picture` takes the same fields as a lesson picture, except a note on a string: `instrument`, `point`, `view`, `marker_size`, `focus`, and `marker`. `caption` is at most 120 characters and goes under it. An entry without a picture shows text alone. |
| `exercises` and `lessons` | Optional. Up to five `id`s each from this pack. The exercise tiles and the lesson tiles open that activity directly. |

A pack can have up to 40 entries. If two plugins supply the same term, Alto skips the second pack at startup and reports the conflict. A term that Alto already has is listed twice, the plugin's with the plugin's name after it.

## Keyboard intervals

A `keyboard-intervals` exercise highlights two keys on the instrument's drawn keyboards and asks for the interval between them. The instrument must declare `keyboards`, and it can give them a `keyboard_style`. Alto draws the keyboards instead of the instrument's picture, so no photograph or measurement is needed. It plays the lower and the higher note together, as a chord, on the plugin's sound when the answer is right.

```json
{
  "id": "intervals-on-two-manuals",
  "title": "Harpsichord Interval Identification",
  "type": "keyboard-intervals",
  "instrument": "flemish-harpsichord",
  "keyboards": ["Lower manual", "Upper manual"],
  "lowest": "E1",
  "highest": "F6",
  "default_range": ["C3", "C5"],
  "intervals": ["m2", "M2", "m3", "M3", "P4", "A4 / d5", "P5", "m6", "M6", "m7", "M7", "P8"],
  "placements": ["same", "across"],
  "settings": {"sound": "Harpsichord sound", "range": true, "intervals": true, "manuals": true}
}
```

| Field | Meaning |
| --- | --- |
| `keyboards` | The names of the instrument's keyboards to use. Without it, every keyboard is used. |
| `lowest` and `highest` | The widest range of keys the exercise has questions for, such as `E1` and `F6`. Both must be keys on the keyboards in use. Alto draws each keyboard over the range being asked, so a shorter range gives larger keys. |
| `default_range` | Optional. The lowest and highest key asked until the learner chooses another range, such as `["C3", "C5"]`. It must lie within `lowest` and `highest`. Without it, the whole range is asked. |
| `settings` | Optional. What the learner can change: `sound` (the label of a row that opens the list of instruments to sound, as for other exercises), `range` (`true` adds a Range page with a draggable keyboard and a lowest and highest key) `intervals` (`true` adds a page of checkboxes for the intervals) and `manuals` (`true` adds a page of checkboxes for the keyboards, so a learner can have both highlighted keys on the upper manual, on the lower manual, or on either). Intervals too wide for the chosen range cannot be checked, and the answer buttons follow the checked intervals. |
| `intervals` | The answers to offer, from `m2`, `M2`, `m3`, `M3`, `P4`, `A4 / d5`, `P5`, `m6`, `M6`, `m7`, `M7` and `P8`. Without it, all twelve are asked. Every listed interval is also an answer button. |
| `placements` | `"same"` puts both keys on one keyboard, and `"across"` puts one key on each of two keyboards. Without it, both are used. `"across"` needs two or more keyboards. Alto treats all the keyboards as playing the same pitches. |
| `prompt` | Optional. A plain-text question of at most 120 characters that replaces the default. |

Alto asks every combination of interval, lowest key, and placement once. A pack with two keyboards and a five-octave range therefore has thousands of cards, though Alto asks only those inside the chosen range and intervals, and remembers each card separately. Narrow `lowest`, `highest`, `intervals`, or `placements` for a smaller exercise.

A lesson step or a glossary entry can highlight keys too. Give its `picture` the `instrument`, `keys`, and an optional `span`. `keys` is a list of one to four `[keyboard name, pitch]` pairs, such as `[["Lower manual", "C4"], ["Upper manual", "A4"]]`, and `span` is the lowest and highest key to draw, such as `["C3", "C5"]`. Without `span`, each keyboard is drawn over its whole range. Write a sharp key with a sharp, as in `C#4`.

## Correct-answer animations

An instrument can supply a transparent animated GIF. Draw the moving shape on a transparent background, export at least two frames, and include the GIF in the pack. Alto reads the frame timing from the GIF and draws the visible pixels in the correct-answer color. Export a looping GIF for motion that continues throughout a sustained note.

The viola example uses `"correct_answer_animation": {"file": "animations/string.gif", "anchor": "string"}`. Its GIF shows a horizontal string with both ends fixed at the middle of the left and right edges. Alto rotates and scales it from the learner’s finger position to the bridge on the marked string. On an open string, the vibration starts at the nut. The same GIF works at every position and in the magnified view. [Preview a correct E4 answer]({{ '/assets/plugins/viola-correct-answer.gif' | relative_url }}) · [Download the viola’s animation]({{ '/assets/plugins/viola/animations/string.gif' | relative_url }}).

For an overlay aligned to the entire picture, use `"correct_answer_animation": {"file": "animations/keys.gif", "anchor": "image"}`. Give the GIF the same proportions as the instrument picture and draw the moving parts in their corresponding positions. The `image` anchor is the default. A string-anchored effect applies only to fingerboard questions.

**Wait** plays the animation and leaves the answered question on screen. **After Animation** advances after feedback. **Immediately** plays the answer audio and skips the overlay. Muting keeps the same timing. On a picture question without a note, an image overlay plays for the usual 600 ms of visual feedback.

## Distribution and troubleshooting

Select `pack.json` **and its sibling asset folders** and compress them into a ZIP. Opening the ZIP should show `pack.json` immediately. Include credits and permissions for the files you distribute. Test the resulting ZIP by moving your working folder outside the plugins folder, installing the ZIP, and restarting. A recipient needs only that ZIP and a build of Alto with instrument pack support.

| Symptom | What to check |
| --- | --- |
| Missing exercise tile | Install the ZIP with **Tools → Plugins… → Install plugin from file…** and restart Alto. For an editable pack, check that its folder contains `pack.json` and restart after edits. |
| Missing picture or recording | Match the relative path, extension, and capitalization to the actual file inside the ZIP. Verify the file opens and that recordings are mono 16-bit PCM. |
| Unknown instrument | The exercise’s `instrument` must exactly match an `id` in this pack’s `instruments` list. |
| Missing pack name | Add a top-level `name` next to the pack `id` in `pack.json`. Existing format 2 packs also need this field. |
| Duplicate ID | Move the previous ZIP or extracted copy out of the plugins folder before installing an update. Give an independent pack a new pack ID. |
| Dot on the wrong string | Pair each string’s own nut and bridge points. Recalibrate after cropping, rotating, or resizing the source picture. |
| Older JSON-only example | Start with the example ZIP from the latest release of the [viola plugin tutorial](https://github.com/altosaurus/viola-plugin-tutorial/releases/latest) and copy your exercise titles and note lists into it. Add an `instrument` reference to every exercise. |

## Plugin removal

Choose **Menu → Tools → Plugins…**, select the installed ZIP or pack folder in the list, and press **Uninstall plugin**. Confirm the question, and Alto moves the selected item to the system trash and restarts. Selecting an editable pack folder moves the entire folder, including your edits.

After Alto restarts, the pack’s exercises disappear from the exercise list. Alto keeps each profile’s practice history. To reinstall a downloaded ZIP, press **Install plugin from file…** in the Plugins dialog again. To recover an editable folder, restore it from the system trash and restart Alto.
