---
title: Home
nav_order: 1
permalink: /
toc: false
topics:
  - title: Circle of Fifths
    icon: CircleOfFifths
    image: circle-of-fifths.png
    description: Find relative keys and the chords that belong to a key.
    alt: The Circle of Fifths exercise, with the list of exercises open on the left
  - title: Scales
    icon: ScaleIdentification
    image: scales.png
    description: Identify scales and modes by their patterns, or build them on the staff.
    alt: Scale Identification showing a scale on the staff with answer choices below
  - title: Chords
    icon: ChordQualities
    image: chords.png
    description: Tell triads and seventh chords apart and recognize inversions in arpeggios.
    alt: Chord Quality showing notes stacked on a staff and a choice of chord qualities
  - title: Intervals
    icon: IntervalNames
    image: intervals.png
    description: Name the distance between two notes on a staff or a keyboard.
    alt: Interval Identification showing two notes on the staff with interval names below
  - title: Keyboard Identification
    icon: KeyboardNotes
    image: keyboard.png
    description: Name highlighted piano keys and identify the intervals between them.
    alt: Keyboard Note Identification showing a highlighted piano key and note-name buttons
  - title: Notation
    icon: NotationIdentification
    image: notation.png
    description: Identify written symbols, from noteheads and clefs to ornaments and playing techniques.
    alt: Notation Identification showing a highlighted marking in a short musical phrase
---
{% include os-icons.html %}
{% include exercise-icons.html %}
<div class="hero">
  <h1>Learn music theory with <span class="hl">Alto</span></h1>
  <p class="lead">Study music theory in short lessons and practice what you learn with spaced repetition.</p>
  {% if site.app_version != "" %}<a class="dl-go" href="#download">Download Alto <svg class="i" width="20" height="20" aria-hidden="true"><use href="#i-arrow"/></svg></a>{% endif %}
</div>

<div class="practice-gallery" role="radiogroup" aria-labelledby="what-you-can-practice">
  <h2 id="what-you-can-practice">What you can practice</h2>
  {% for topic in page.topics %}
  <label class="practice-card">
    <input type="radio" name="practice-topic" aria-controls="preview-{{ topic.icon }}"{% if forloop.first %} checked{% endif %}>
    <strong><svg class="ex-icon" width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><use href="#ex-{{ topic.icon }}"/></svg>{{ topic.title }}</strong>
    <span>{{ topic.description }}</span>
  </label>
  <div class="practice-preview" id="preview-{{ topic.icon }}">
    {% include shot.html src=topic.image alt=topic.alt %}
  </div>
  {% endfor %}
</div>

## What makes it different

- **Spaced repetition.** ASRS and ARTS use your accuracy and response time to choose the next exercise question. SM-2 and FSRS schedule a due date for each review. [Compare the four algorithms]({{ '/practice/' | relative_url }}).
- **Statistics and a database browser.** Charts of accuracy, speed and volume, plus a calendar heatmap of a year of practice, filterable by exercise and timeframe, plus a table view of everything stored. [Statistics]({{ '/statistics/' | relative_url }}).
- **Notation and keyboards your way.** Eleven notation styles, including Finale Maestro, Leland, Bravura and two handwritten jazz styles, and eleven keyboard looks from a modern piano to a French harpsichord. [Settings]({{ '/settings/' | relative_url }}).
- **Local and private.** Your history is one file on your computer. [Your data]({{ '/data/' | relative_url }}).
- **Free and open source** under the MIT License.

{% include shot.html src="stats.png" alt="The statistics page with summary tiles and charts of accuracy, speed and volume" caption="Statistics for a demo profile: how often you are right, how fast, and how much you practice." %}

{% include shot.html src="stats-heatmap.png" alt="A calendar heatmap of the last twelve months, a square per day in shades of green" caption="The review heatmap: every day you practiced, at a glance." %}

## Development Status

Alto is in alpha. You can work through the lessons and practice with the exercises now, but their content and layout may change between releases.
The [roadmap]({{ '/roadmap/' | relative_url }}) lists current features and planned exercises.

{% assign v = site.app_version %}
{% assign base = "https://github.com/altosaurus/alto/releases/download/v" | append: v | append: "/" %}
{% assign source = '/getting-started/#install-and-run' | relative_url %}
{% if v != "" %}
<section class="dl" id="download" data-version="{{ v }}" data-source="{{ source }}">
  <h2>Download Alto</h2>
  <p class="dl-sub"><b>Version {{ v }}&nbsp;<span class="dl-alpha">Alpha</span></b><br>
    <small>Free for Desktop</small></p>
  <div class="dl-main" id="dl-main"></div>
  <div id="dl-all">
    <div class="dl-os" data-os="windows" data-name="Windows" data-req="64-bit installer" data-file="alto-{{ v }}-windows-x64-setup.exe" data-url="{{ base }}alto-{{ v }}-windows-x64-setup.exe">
      <span class="dl-logo" aria-hidden="true"><svg viewBox="0 0 24 24" width="40" height="40"><use href="#os-windows"/></svg></span>
      <div class="dl-txt"><span class="dl-name">Windows</span><span class="dl-file">alto-{{ v }}-windows-x64-setup.exe</span></div>
      <div class="dl-act"><a class="dl-pill" href="{{ base }}alto-{{ v }}-windows-x64-setup.exe"><svg class="i" width="18" height="18" aria-hidden="true"><use href="#i-download"/></svg>Download</a></div>
    </div>
    <div class="dl-os" data-os="linux" data-name="Linux" data-req="x86-64" data-file="alto-{{ v }}-linux-x86_64.tar.gz" data-url="{{ base }}alto-{{ v }}-linux-x86_64.tar.gz">
      <span class="dl-logo" aria-hidden="true"><svg viewBox="0 0 24 24" width="40" height="40"><use href="#os-linux"/></svg></span>
      <div class="dl-txt"><span class="dl-name">Linux</span><span class="dl-file">alto-{{ v }}-linux-x86_64.tar.gz</span><span class="dl-note">Unpack it, then run <code>sh install.sh install</code>.</span></div>
      <div class="dl-act"><a class="dl-pill" href="{{ base }}alto-{{ v }}-linux-x86_64.tar.gz"><svg class="i" width="18" height="18" aria-hidden="true"><use href="#i-download"/></svg>Download</a></div>
    </div>
    <div class="dl-os" data-os="macos" data-name="macOS">
      <span class="dl-logo" aria-hidden="true"><svg viewBox="0 0 24 24" width="40" height="40"><use href="#os-apple"/></svg></span>
      <div class="dl-txt"><span class="dl-name">macOS</span><span class="dl-note">There is no installer yet. You can <a href="{{ source }}">run Alto from its source code</a>.</span></div>
      <div class="dl-act"><a class="dl-pill" href="{{ source }}">Run from source</a></div>
    </div>
  </div>
  <p class="dl-more"><a href="{{ '/release-notes/' | relative_url }}">Release notes</a> &middot; <a href="https://github.com/altosaurus/alto/releases">Older releases</a> &middot; <a href="{{ '/getting-started/' | relative_url }}">Getting started</a></p>
</section>
<script src="{{ '/assets/js/downloads.js' | relative_url }}?v={{ site.time | date: '%s' }}" defer></script>
{% endif %}
