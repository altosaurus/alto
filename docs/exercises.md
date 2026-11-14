---
title: Exercises
nav_order: 3
permalink: /exercises/
---
Alto has eleven exercises. Each one has a **?** button with a short explanation, and eight of them have their own
settings (the sliders button). The others use fixed rules, described below.

**Every exercise can be done with the keyboard alone, and without clicking on the staff.** The answer buttons have keys,
and where you place notes on a staff there are buttons and keys to move the note, choose its sign and place it, so the
mouse is never needed. The keys are listed on the [Shortcuts]({{ '/shortcuts/' | relative_url }}) page, and each button
shows its key when you hover over it.

## Note Identification

A note is drawn on a staff. Press the button with its name.

In the exercise settings you can choose:

- **Clefs:** the grand staff, or any of the seven single-staff clefs, listed in three groups: treble, bass, alto and
  tenor; then soprano, mezzo-soprano and baritone (written as an F clef, or as a C clef if you choose that in
  [Settings]({{ '/settings/' | relative_url }})). Each clef is shown with its name beside it. The same list is used by every
  exercise that has a clef setting, apart from the grand staff, which only Note Identification and Note Construction use.
- **Range:** the lowest and highest note that can appear, per clef.
- **Key signatures:** which keys appear. When a key is on, the note's name has to agree with the signature.
- **Note values:** whole notes up to thirty-second notes, and the breve.
- **Note names:** letters (C D E) or solfège (Do Re Mi).
- **Accidentals:** whether notes with their own sharp, flat or natural sign appear.

The settings open in a pane on the right of the exercise. Each row names an option, and clicking it opens a page for
that option. Changes apply to the next question straight away.

## Keyboard Identification

One key on a piano keyboard is highlighted. Press the button with its name.

- **Black keys:** include them. A black key has two names, such as C♯ and D♭, and either one is accepted.
- **Octave number:** also choose the octave from a second row. Octaves count up from C, so middle C is C4.
- **Range:** which part of the keyboard is asked.
- **Key signatures:** show a key signature above the keyboard. The name then has to follow that signature. F♯ and G♭ are no longer interchangeable.

{% include shot.html src="keyboard.png" alt="Keyboard Identification with one highlighted key and the note name buttons" %}

## Note Construction

The reverse of note identification. A note name is shown, and you click the staff where that note belongs.

- The octave counts: middle C is C4. On a grand staff, click the upper staff for notes from middle C up and the lower staff for the notes below.
- With **Accidentals** on, pick ♭, ♮ or ♯ first, or right-click the staff to step through them.
- With **Key signatures** on, a signature is drawn at the start of the staff. It already applies to every note of that letter, so in G major you place F♯ on the F line with no extra sign.
- A wrong click shows the note you placed so you can adjust and try again. Only the exact spelling counts, so G♯ is not A♭.
- **Without the mouse:** the **Higher** and **Lower** buttons (or the <kbd>↑</kbd> and <kbd>↓</kbd> keys) move the note a line or
  space, and **Octave ↑** and **Octave ↓** (<kbd>Page Up</kbd> and <kbd>Page Down</kbd>) an octave. Typing a letter from
  <kbd>A</kbd> to <kbd>G</kbd> jumps to the nearest note with that name, and <kbd>←</kbd> and <kbd>→</kbd> step through the signs.
  **Place note** (<kbd>Return</kbd>) places it. A line under the staff says which note is chosen, in words a screen reader can read.

{% include shot.html src="note-construction.png" alt="Note Construction asking to place a note on a staff" %}

## Interval identification

Two notes are shown. Name the interval from the lower note to the higher one, up to an octave.

An interval has a quality and a number. The number counts the letter names it spans, including both notes. The quality
is **P** (perfect), **M** (major), **m** (minor), **A** (augmented) or **d** (diminished). So C to E is M3, and C to E♭
is m3.

{% include shot.html src="intervals.png" alt="Interval identification showing two notes and the interval buttons" %}

## Key Signature Identification

A key signature is drawn on a staff and you press the tonic of the scale it belongs to. The kind of scale is written
under the staff with a blank for the tonic: "_ Major", "_ minor" or, for a mode, "_ Dorian".

This exercise makes no sound: a right answer plays no tone. The speaker button is a mute for the whole app, so it works here
as everywhere else, but has nothing to silence in this exercise.

A mode uses the key signature of a major key and starts from another note of it, so D Dorian has the signature of C major
(no sharps or flats), started from D. By default Alto asks major and natural minor keys, on the treble and bass staves.
In the exercise settings you can choose:

- **Clefs:** any of the seven clefs (treble, bass, alto, tenor, soprano, mezzo-soprano and baritone), for the signature that is drawn.
- **Scales:** major (Ionian), Dorian, Phrygian, Lydian, Mixolydian, minor (Aeolian) and Locrian.
- **Key signatures:** which of the fifteen signatures, from seven flats to seven sharps, can appear.

{% include shot.html src="key-signatures.png" alt="Key Signature Identification showing three flats on an alto clef staff, with the caption _ Major under the staff" %}

## Key Signature Construction

The reverse of the exercise above. A blank staff is shown with the name of a key under it, such as "D Major", "A♯ minor" or
"E Dorian". Build that key's signature with the fork under the staff, then press **Answer** (or <kbd>Return</kbd>).

The fork is shaped like a tuning fork lying on its side. Its stem, on the left, ends in a natural sign: no sharps or flats,
C major. The stem opens into two tines: the top one has the sharps, 1 to 7, and the bottom one the flats, 1 to 7. A circle
marks what you have chosen, and the staff shows that many sharps or flats as you move it. To choose:

- **Click** a number, or the natural sign.
- **Turn the mouse wheel** to move the circle along the fork, one number for each notch: up towards more sharps, down
  towards more flats, passing through the natural sign on the way from one side to the other.
- **Press the arrow keys** (<kbd>↑</kbd> or <kbd>→</kbd> for a sharp, <kbd>↓</kbd> or <kbd>←</kbd> for a flat) wherever the
  keyboard is on the exercise screen, and <kbd>Home</kbd> to go back to the natural sign. Then press <kbd>Return</kbd>.

A wrong signature turns the circle red and puts it back on the natural sign so you can try again; only your first try
counts towards your score. Like Key Signature Identification, this exercise makes no sound.

In the exercise settings you can choose:

- **Clefs:** any of the seven clefs, for the staff the signature is built on.
- **Scales:** major (Ionian), Dorian, Phrygian, Lydian, Mixolydian, minor (Aeolian) and Locrian.
- **Key signatures:** which of the fifteen signatures, from seven flats to seven sharps, can be asked.

The settings are kept apart from those of Key Signature Identification.

## Scale spelling

A question such as "In B♭ Dorian, what is scale degree 3?" Press the note's name. Each scale uses every letter name
once, so use a sharp or flat where the pattern needs one. Alto asks about:

Major (Ionian), Dorian, Phrygian, Lydian, Mixolydian, natural minor (Aeolian), Locrian, harmonic minor and melodic minor.

## Scale Construction

A blank staff is shown with the name of a scale under it, such as "D Major", "E♭ minor" or "A Dorian". Click the staff to
place the scale's notes from left to right, going up from the first note to the same note an octave higher: eight notes in
all. The next note follows the pointer, snapped to a line or space, and each click puts it in the next place, so the notes
do not move as you add more. Any octave will do, as long as the whole scale is in the same one.

You never have to click the staff. **Higher**, **Lower**, **Octave ↑** and **Octave ↓** under it move the next note, the sign
buttons choose its sign, and **Place note** puts it in the next place; the same things are on the keys (see
[Shortcuts]({{ '/shortcuts/' | relative_url }})), and <kbd>Return</kbd> places the note and, when everything is placed,
answers.

By default the staff has no key signature, so a note that needs a sharp or a flat needs its own sign (see
[the staff's key signature](#the-staffs-key-signature) below for a staff that has one). To choose the sign for the next
note:

- **Right click** the staff to step through no sign, ♯ and ♭, and round again.
- **Turn the mouse wheel** over the staff to step through them the same way: up goes no sign, ♯, ♭, and down goes the other
  way round.
- **Press one of the sign buttons** under the staff.

Then click to place the note. A sign is used up by the note it goes on. Only the exact spelling counts, so G♯ is not A♭.

- **Undo** (or Backspace) takes back the last thing you placed.
- **Answer** (or Enter) hands in the scale once everything is placed.

A wrong scale is cleared so that you can try again, and only your first try counts towards your score. A right one plays
the scale: the notes start black and each one turns green as the instrument sounds it. They turn green even with the
sound muted, and the next question comes when the scale has finished.

In the exercise settings you can choose:

- **Clefs:** any of the seven clefs, for the staff the scale is placed on.
- **Scales:** major (Ionian), Dorian, Phrygian, Lydian, Mixolydian, minor (Aeolian) and Locrian.
- **Staff keys:** which key signatures may be drawn on the staff, from seven flats to seven sharps. It is separate from
  the scale's own signature (below). By default only the blank staff, with no sharps or flats, is chosen.
- **Scale keys:** which of the fifteen signatures the scales have. G major and E minor, for example, both have one sharp.
- **Octave:** a switch, off by default. When it is on, the scale has to start in the octave named (below).
- **Steps:** a switch, off by default. When it is on, you also mark the whole and half steps between the notes (below).

The settings are kept apart from those of the other exercises.

### Starting in the right octave

By default any octave will do, as long as all eight notes are in the same one, and the scale is named without an octave,
such as "G Major". With **Octave** on, the name says which octave the first note is in, such as "G2 Major" or "B♭4 minor",
using the same numbers as note names everywhere in Alto (middle C is C4). The scale then has to be placed there: the right
notes an octave higher or lower are wrong.

The octave is part of the question, so scales are asked from well below to well above the staff. Alto only asks a scale
that can be placed in full: all eight notes lie on the staff or on its ledger lines, within the furthest ledger line the
staff can be clicked on. A bass clef G2 Major, which starts on the bottom line, can be asked; a scale that would run off
the top of the ledger lines cannot.

### The staff's key signature

The key signature on the staff and the key signature of the scale are two separate settings, so a scale can be asked on a
staff whose signature is not its own. Each question picks one of each. For example, with two flats on the staff (the
signature of B♭ major) and a C major scale to place:

- A note you place with no sign takes the sign the staff's signature gives its letter, as it would when you read music.
  With two flats, B and E are flat.
- So C major needs a **natural** (♮) on its E and its B, which you choose with the sign buttons, a right click or the
  wheel. Right click and the wheel step through no sign, ♯, ♭ and ♮ when the staff has a signature.
- Going the other way, a scale that has a flat the staff does not give needs that flat written as a sign.

The notes the staff's signature already covers are written with no sign, as in any score; only the notes that differ from it
get one. Only the exact spelling counts, as ever.

### Marking the steps

With **Steps** on, once the eight notes are placed two lines rise from each pair of neighbouring notes to a point above
them, starting with the first pair, with the step written over the point. The step that a click would mark is shown there in
blue, as **W** (a whole step, two semitones) or **H** (a half step, one semitone). It starts as W. To choose:

- **Turn the mouse wheel** over the staff to switch between W and H (the wheel is for the signs until all the notes are
  placed).
- **Right click** the staff to switch between W and H.
- **Press the W or H button** under the staff.

Then **left click** the staff to mark the step and move on to the next pair. Each new pair starts as W again, since most
steps are whole. Undo takes back the steps, last first, before it takes back any notes. The scale is right when the notes
and every step are right: a major scale is W W H W W W H, and a natural minor scale is W H W W H W W. The lines and letters turn
green with the notes as the right scale plays.

## Circle of Fifths

A circle of fifths, drawn as two rings of twelve wedges. The outer ring holds the major keys, with C at the top and each
step clockwise a fifth higher: G, D, A, E, B, then F♯ at the bottom, and round through the flats back to F. The inner ring
holds their relative minors, so A minor sits under C major, E minor under G major, and so on. Each wedge has its own colour.
The disc in the middle shows the staff.

Every question lights one cell and leaves its answer blank. There are three kinds, and the exercise settings (the sliders
button) switch each on or off:

- **Relative major.** A minor key is shown, such as "F♯ minor", with the wedge of the outer ring beside it blank. Press the
  name of its relative major, which has the same key signature: A, in this case.
- **Relative minor.** A major key is shown and the inner wedge beside it is blank. Press the name of its relative minor.
- **Roman numerals.** A key is in the middle with its staff and signature, and the six chords of the key that fit on the
  circle are lit. One of them is outlined. Press its Roman numeral.

All of them are on buttons at the bottom, laid out like the Keyboard Identification screen: the letters in the middle row,
the sharps above them and the flats below. For the minor keys the buttons read Am, F♯m and so on. You can also type: a letter,
<kbd>Shift</kbd> and a letter for a sharp, or <kbd>Ctrl</kbd> and a letter for a flat. The numerals are on <kbd>1</kbd> to <kbd>6</kbd>.

### Keys with two names

Three of the wedges have two names on the circle: B and C♭, F♯ and G♭, and D♭ and C♯, with their minors G♯m and A♭m, D♯m and
E♭m, and B♭m and A♯m. For these you press **both** names, in either order. A right first name is marked and its button is
switched off, the middle of the circle says "and its other name", and nothing is scored until the second is pressed. A wrong
button at any point counts as a miss, and you can carry on until both are found.

### Roman numerals on the circle

A key has seven chords, and the circle has room for six of them: its own wedge and the wedge on each side, on both rings. The
**outer** ring holds the **major** chords, so it gets the capitals: I (the key itself), IV (one step counterclockwise) and V
(one step clockwise). The **inner** ring holds the **minor** chords, so it gets the small letters: vi (under the key), ii (under
IV) and iii (under V). In C major that is I = C, ii = Dm, iii = Em, IV = F, V = G and vi = Am.

If you have seen pictures of this with two sets of numerals, one outer and one inner, they are one set shared between the two
rings. The seventh chord, vii° (B diminished in C major), is diminished and does not sit on the circle, so it is never asked.
A chord is spelt as its key spells it: in F♯ major the V is C♯, although that wedge is labeled D♭ with C♯ as its other name.

### Right and wrong answers

- **A right answer** brightens the cell and writes its name in it, and puts the key's staff and signature in the middle: "A major,
  3 sharps". For a numeral question all six numerals appear.
- **The book button** (experimental), beside the help button, opens a reference in a pane on the right: a short description and
  an interactive circle with every key named. Click a key on either ring, or move with the arrow keys (Left and Right go round,
  Up and Down switch rings, Escape or a click in the middle starts again). The circle lights that key's six chords, shows its
  key signature in the middle, and the text underneath explains it: its sharps or flats, which key it follows, its relative
  minor or major, and its chords. It shares the right-hand side with the settings, so opening one closes the other. It is a
  study aid, so it also gives away the answers. A button at the top of the pane opens the circle of fifths
  [lesson]({{ '/lessons/' | relative_url }}).
- **A wrong answer** flashes the cell in the same red as the wrong button, striped so that it still shows on the red wedge at
  the top. The button is switched off and you can try again.
  Only your first try counts toward your score.

This exercise makes no sound.

## Chord quality

A chord is drawn in root position on a treble or bass staff. Press its type:

major, minor, diminished, augmented, major 7th, dominant 7th, minor 7th, half-diminished 7th and diminished 7th.

Check the size of the intervals stacked above the lowest note to tell the types apart.

## Arpeggio identification

A chord is drawn one note at a time, rising from its lowest note to the same note an octave higher. Press its type, then
press its inversion. The answer counts once you have chosen both, in either order, and a wrong pair is cleared so you can
try again.

The inversion is which chord tone is lowest:

| Inversion | Lowest note |
|---|---|
| Root position | the root |
| 1st inversion | the third |
| 2nd inversion | the fifth |
| 3rd inversion | the seventh (seventh chords only) |

By default Alto asks major, minor, dominant 7th and diminished 7th arpeggios on the treble and bass staves, in every
inversion. In the exercise settings you can choose:

- **Clefs:** any of the seven clefs, from treble to baritone.
- **Arpeggio types:** any of major, minor, diminished and augmented triads, and dominant 7th, major 7th, minor 7th,
  half-diminished 7th and diminished 7th chords. The type buttons below the staff follow your choice.
- **Inversions:** root position and the first three inversions. A triad has no 3rd inversion, so that choice only applies to seventh chords.
- **Key signatures:** draw a key signature from the keys you pick. The arpeggio then only gets a sign where it differs
  from the signature, so a natural sign appears where the chord needs one.

{% include shot.html src="arpeggios.png" alt="Arpeggio identification showing four notes rising on a staff, with a row of type buttons and a row of inversion buttons" %}
