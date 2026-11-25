# Third-party material

Alto bundles the following. Each item is used under the terms stated by its author. The source files and license
texts are in the folders named below.

## Music fonts (`alto/assets/fonts/`)

All are under the SIL Open Font License 1.1 (OFL), whose texts are kept beside the fonts. The fonts are used unmodified.
`engraving.json` holds measurements read from each font's published SMuFL metadata; it is not a font.

| Font | Author | Source |
|---|---|---|
| Bravura | Steinberg Media Technologies GmbH | https://github.com/steinbergmedia/bravura |
| Petaluma | Steinberg Media Technologies GmbH | https://github.com/steinbergmedia/petaluma |
| Leland | MuseScore Limited | https://github.com/musescore/MuseScore/tree/main/fonts/leland |
| MuseJazz | Torsten Hämmerle and Abraham Lee | https://github.com/musescore/MuseScore/tree/main/fonts/musejazz |
| Eugene | Mikko Patama | https://github.com/mikkopatama/eugenefont |
| Leipzig | Etienne Darbellay, Jean-François Marti and Laurent Pugin | https://github.com/rism-digital/leipzig |
| Sebastian | Florian Kretlow and Ben Byram-Wigfield | https://github.com/fkretlow/sebastian |
| Golden Age | Don Rice | https://github.com/benwiggy/GoldenAge |
| Finale Maestro, Finale Broadway | MakeMusic, Inc. | https://github.com/musescore/MuseScore/tree/main/fonts |

The font names are the names their authors gave them. Alto is not affiliated with or endorsed by any of them, nor by
Dorico, Finale, MuseScore or Verovio, which are mentioned only to say where a font is used.

## Notation Identification excerpts

Alto includes eight piano passages from free CC0 transcriptions in the [OpenScore Lieder catalogue](https://fourscoreandmore.org/openscore/lieder/).
OpenScore distributes the transcriptions under its [CC0 1.0 public-domain dedication](https://github.com/OpenScore/Lieder/blob/main/LICENSE.txt).
The historical editions used for these transcriptions are listed below. The OpenScore file for *Die Lotosblume* credits flutemouse as its transcriber.

| Work | Source edition | Piano measures |
| --- | --- | --- |
| Franz Schubert, *Erlkönig*, D. 328, fourth version | Eusebius Mandyczewski, ed., Breitkopf & Härtel, 1895. [IMSLP 15041](https://imslp.org/wiki/Special:ReverseLookup/15041) | 1–2 and 3–4 |
| Robert Schumann, *Schöne Fremde*, Op. 39 No. 6 | Clara Schumann, ed., Breitkopf & Härtel, 1885. [IMSLP 270920](https://imslp.org/wiki/Special:ReverseLookup/270920) | 2–3, 5, 19, and 29–30 |
| Robert Schumann, *Die Lotosblume*, Op. 25 No. 7 | Clara Schumann, ed., Breitkopf & Härtel, plate R.S. 120. [IMSLP 270905](https://imslp.org/wiki/Special:ReverseLookup/270905) | 1–2 and 4–5 |

Each passage in `alto/assets/excerpts/` includes its MusicXML, the source URL and SHA-256 digest of the downloaded MusicXML archive.
The exercise engraving was made with Verovio 6.4.1 and Bravura. The excerpt begins with its clefs, key and meter.
Ties, slurs, and hairpins with an endpoint outside the passage are omitted.

## Piano recordings (`alto/assets/piano/`)

The piano is the Salamander Grand Piano V3 by Alexander Holm: a Yamaha C5 grand recorded with two AKG C414 microphones
(https://sfzinstruments.github.io/pianos/salamander, https://github.com/sfzinstruments/SalamanderGrandPiano). It is used under the
Creative Commons Attribution 3.0 Unported license (CC BY 3.0, https://creativecommons.org/licenses/by/3.0/), whose text is in
`alto/assets/piano/LICENSE-CC-BY-3.0.txt`. Alto uses 30 recordings from one dynamic layer, converted to mono 44.1 kHz, trimmed
and faded to 2.5 s, and levelled. Details are in `alto/assets/piano/SOURCE.txt`. Alexander Holm does not endorse Alto.

## Other instrument recordings (`alto/assets/samples/`: marimba, vibraphone, flute, horn, viola_bowed, viola_plucked)

Lawrence Fritts created the University of Iowa Electronic Music Studios’ Musical Instrument Samples collection.
The studio permits the recordings to be downloaded and used in any project without restrictions. Alto converted the samples
to mono, trimmed them, and added fades. [University of Iowa collection and use terms](https://theremin.music.uiowa.edu/MIS.html)

Andrew Thierauf played marimba and vibraphone, Manuel Tabora played viola, Sonja Feig played flute, and Jessica Wiskus
played French horn. The recording dates, sources, and edits are documented in `alto/assets/samples/SOURCE.txt`.

## App icons (`alto/assets/icon.svg`, `alto/assets/icon-treble.svg`)

The clef in each icon is an outline from the Noto Music font (Google, SIL Open Font License 1.1), set on a rounded
square: the alto clef in `icon.svg` and the treble clef in `icon-treble.svg`.

## Fonts used from the system, not bundled

- Noto Music (Google, SIL OFL 1.1) draws the "Noto Music" notation style, and DejaVu Sans (Bitstream Vera license with
  DejaVu changes, free to redistribute) draws a few sharp and flat signs. Alto asks the operating system for them by name.

## SuperMemo SM-2

Alto’s SM-2 review scheduler is based on the spaced repetition algorithm Piotr Woźniak developed for SuperMemo in 1987.
Algorithm SM-2, © SuperMemo World, 1991. [SuperMemo](https://www.supermemo.com/) · [Original SM-2 specification](https://super-memory.com/english/ol/sm2.htm) · [SuperMemo’s attribution policy](https://www.supermemo.com/en/blog/licensing-and-copyrighting-of-supermemo-algorithms)

## Software dependencies

- The desktop installers use Qt, PySide6, and Shiboken under LGPL-3.0. The installed `licenses/Qt/` directory
  contains the license texts, upstream credits, source archive names and checksums, and instructions for replacing
  the libraries. On macOS, open Alto.app with **Show Package Contents** and look in `Contents/Resources`. The matching
  source archives accompany the Mac test image in its workflow download and the release installers on the [Alto releases page](https://github.com/altosaurus/alto/releases).
- The Linux download contains system libraries from Ubuntu, copied unchanged from Ubuntu's packages, among them GLib,
  PulseAudio, libsndfile, the X11 and XCB libraries, OpenSSL, and GCC's C++ runtime. Each keeps its own license. The
  installed `licenses/Linux/` directory lists every library with its package, version, and checksum, and contains each
  package's copyright file and the license texts they refer to. The Ubuntu source packages of the libraries under the LGPL
  or GPL accompany the download on the [Alto releases page](https://github.com/altosaurus/alto/releases).
- Alto uses genanki to export Anki decks. Copyright © 2017 Kerrick Staley. The MIT license is installed at
  `licenses/genanki/LICENSE.txt`.
- Alto uses PyNaCl to verify update signatures. Its Apache License 2.0 is installed at `licenses/PyNaCl/LICENSE`.
  PyNaCl bundles Frank Denis’s libsodium library. Its ISC license is installed at `licenses/libsodium/LICENSE.libsodium.txt`.
- The desktop installers contain the Python interpreter and its standard library (Python Software Foundation License,
  with the licenses of the software CPython incorporates, among them the HACL* hash functions (MIT)), and these Python
  packages, each with its license installed under `licenses/`: FSRS (MIT), typing_extensions (PSF License), Chevron
  (MIT), cached-property (BSD-3-Clause), PyYAML (MIT) with the LibYAML library compiled into it (MIT), and cffi (MIT-0)
  with embedded libffi (MIT) on Linux and Windows. The Mac build uses the system libffi. Its interpreter extensions
  include Expat, libmpdec, liblzma, and SQLite, listed in `licenses/README.txt`.
- Alto checks update downloads with the certificate authorities in certifi, under the Mozilla Public License 2.0. Its
  license and where to get the source of the version in the installers are installed at `licenses/certifi/`.
- The Linux Qt libraries use ICU (Unicode License), and the Windows and Mac installers contain OpenSSL (Apache License 2.0). `licenses/README.txt` lists each of these components with its version and the files of its
  license.
- The documentation uses Temml by Ron Kok (MIT) to show mathematical notation. Temml is derived from KaTeX, by Khan Academy
  and other contributors (MIT). Both licenses are in `docs/assets/vendor/temml-0.14.0/`.
- pytest (MIT) and NumPy (BSD-3-Clause) are used for tests only, and neither is part of the desktop installers.
- On Windows, Alto uses the Microsoft Visual C++ Runtime but does not include it: if Windows lacks it, the installer downloads
  Microsoft's own installer from Microsoft, which asks the user to accept Microsoft's license. Programs built with Microsoft's
  compiler, including the Python and Qt in the Windows installer, contain small parts of Microsoft code; the terms that protect
  that code are shown by the installer and installed at `licenses/Microsoft/microsoft-components.txt`.

## Iconoir icons (`alto/ui/icons.py`)

The GitHub and music-double-note (Exercises) icons are from [Iconoir](https://github.com/iconoir-icons/iconoir), under the
[MIT license](alto/assets/licenses/LICENSE-iconoir.txt).
Their paths are unchanged; their colors follow the application theme. The music-double-note icon's note heads are filled.

Copyright (c) 2021 Luca Burgio. The full license is bundled at the path linked above.
