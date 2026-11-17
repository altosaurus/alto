---
title: Home
nav_order: 1
permalink: /
toc: false
---
{% include os-icons.html %}
{% include exercise-icons.html %}
<div class="hero">
  <h1>Learn music theory with <span class="hl">Alto</span></h1>
  <p class="lead">Alto provides exercises and lessons on music theory, optimized with spaced repetition.</p>
  {% if site.app_version != "" %}<a class="dl-go" href="#download">Download Alto <svg class="i" width="20" height="20" aria-hidden="true"><use href="#i-arrow"/></svg></a>{% endif %}
</div>

{% include shot.html src="circle-of-fifths.png" alt="The Circle of Fifths exercise, with the list of exercises open on the left" caption="An exercise, here the circle of fifths. The list on the left switches between exercises." %}

## What you can practice

<ul class="cards">
  <li><strong><svg class="ex-icon" width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><use href="#ex-NoteNames"/></svg>Note Identification</strong>Name notes on the grand staff or on any of seven clefs, treble to baritone.</li>
  <li><strong><svg class="ex-icon" width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><use href="#ex-KeyboardNotes"/></svg>Keyboard Identification</strong>Name the highlighted key on a piano keyboard.</li>
  <li><strong><svg class="ex-icon" width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><use href="#ex-NoteConstruction"/></svg>Note Construction</strong>Click the staff where a named note belongs.</li>
  <li><strong><svg class="ex-icon" width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><use href="#ex-ClefBasics"/></svg>Clef Basics</strong>Put the G, C or F clef where it makes the clef you are asked for, or name the clef on a staff.</li>
  <li><strong><svg class="ex-icon" width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><use href="#ex-IntervalNames"/></svg>Interval Identification</strong>Name the interval between two notes.</li>
  <li><strong><svg class="ex-icon" width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><use href="#ex-KeyboardIntervals"/></svg>Keyboard Interval Identification</strong>Identify the interval between two highlighted piano keys.</li>
  <li><strong><svg class="ex-icon" width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><use href="#ex-KeySignatures"/></svg>Key Signature Identification</strong>Name the key from its signature on a staff, in major, minor and the modes.</li>
  <li><strong><svg class="ex-icon" width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><use href="#ex-KeySignatureConstruction"/></svg>Key Signature Construction</strong>Build the key signature of a named key with a fork of sharps and flats.</li>
  <li><strong><svg class="ex-icon" width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><use href="#ex-ScaleIdentification"/></svg>Scale Identification</strong>Identify a scale or mode on the staff.</li>
  <li><strong><svg class="ex-icon" width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><use href="#ex-ScaleConstruction"/></svg>Scale Construction</strong>Place the notes of a named scale on a blank staff, one after another.</li>
  <li><strong><svg class="ex-icon" width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><use href="#ex-CircleOfFifths"/></svg>Circle of Fifths</strong>Find relative majors and minors, and the Roman numerals of a key, on the circle of fifths.</li>
  <li><strong><svg class="ex-icon" width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><use href="#ex-ChordQualities"/></svg>Chord Quality</strong>Tell triads and seventh chords apart.</li>
  <li><strong><svg class="ex-icon" width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><use href="#ex-ArpeggioNames"/></svg>Arpeggio Identification</strong>Name the type and the inversion of a broken chord.</li>
</ul>

## What makes it different

- **It learns from your answers.** Every answer is recorded under your profile. Questions you miss, or take a long time over, come back more often. Questions you answer quickly and correctly fade into the background. [How it works]({{ '/practice/' | relative_url }}).
- **Statistics and a database browser.** Charts of accuracy, speed and volume, plus a calendar heatmap of a year of practice, filterable by exercise and timeframe, plus a table view of everything stored. [Statistics]({{ '/statistics/' | relative_url }}).
- **Notation and keyboards your way.** Eleven notation styles, including Finale Maestro, Leland, Bravura and two handwritten jazz styles, and eleven keyboard looks from a modern piano to a French harpsichord. [Settings]({{ '/settings/' | relative_url }}).
- **Local and private.** Your history is one file on your computer. [Your data]({{ '/data/' | relative_url }}).
- **Free and open source** under the MIT License.

{% include shot.html src="stats.png" alt="The statistics page with summary tiles and charts of accuracy, speed and volume" caption="Statistics for a demo profile: how often you are right, how fast, and how much you practice." %}

{% include shot.html src="stats-heatmap.png" alt="A calendar heatmap of the last twelve months, a square per day in shades of green" caption="The review heatmap: every day you practiced, at a glance." %}

{% assign v = site.app_version %}
{% assign base = "https://github.com/altosaurus/alto/releases/download/v" | append: v | append: "/" %}
{% assign source = '/getting-started/#install-and-run' | relative_url %}
{% if v != "" %}
<section class="dl" id="download" data-version="{{ v }}" data-source="{{ source }}">
  <h2>Download Alto</h2>
  <p class="dl-sub"><b>Version {{ v }}</b>. Free on all platforms.</p>
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
