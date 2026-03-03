# 🖐️ fing: A universal representation of fingering systems for winds, reeds, and brass 🖐️

## Abstract

`fing` is a universal representation of fingering systems for monophonic keyed
musical instruments, including winds, reeds, and keyed brass.

The motivating goals:

1. To represent any fingering system as a document that can easily be created, read and
   understood by humans and computers alike.

2. To represent these fingering systems using new types of fingering charts and tables
   as well as the standard one.

The result is a fairly simple format which can represent all existing fingerings for
wind instruments, but also new, dramatically different fingerings, perhaps simplified,
or optimized, or even just plain weird.

## Definitions

**Monophonic** (mono) instruments only play a single note or tone at a time, like wind and
brass instruments.

A **key** is a button that can be pressed and held, or a hole that can be covered on an
instrument.

A **fingering** is a set of keys being pressed at the same time.

A **note-fingering** is a note together with a fingering that can play it.

**Note** and **scale** are used informally and generally here: see the `tuney` project
for a full specification of tunings and scales. Techniques like microtonalism and
multiphonics should also fit in well.

A **fingering system** is a set of note-fingerings. If a note or a fingering doesn't
appear anywhere in a fingering system, we call it an **unreachable note** or an
**invalid fingering**.

In a fingering system, one note can correspond to many fingerings, and one fingering can
also correspond to multiple notes, like in brass instruments or overblown winds,

## Why not just list note fingerings by note?

Listing all the note-fingerings individually is the simplest way to go, and in many
cases will be the best way for small numbers of keys. Any complete fingering system will
have to allow a simple list of key fingerings as part of it.

But most wind instruments have a linearity to many of their keys, taking advantage of
the natural smoothness and speed of raising or lowering successive fingers in linear
sequence.

We'll call these linear-ish keys **main keys**.

Also, many keys have specific conceptual meanings: as a player, you know in your heart that
the octave key goes up an octave (with some exceptions like the clarinet), you don't memorize
E1 and E2 separately, but think of them as the same note but with the octave key pressed.

Other keys like palm and octave keys change the note set by the main keys in one, a few,
or in the case of octave keys, many cases: we'll call these **modifier keys** or
**mods**.

The big picture is that the instrument's note is set by the main keys and then changed
by the modifier keys.

## Main keys

Main keys depend entirely on the instrument.  An ocarina fingering system might have no
main keys but in a recorder, every key can be a main key.

By default, the names of main keys start with C and continue through whole notes in
the C scale, but this can all be customized.

Main keys have numbers: they are numbered sequentially starting at 1, the lowest key
in pitch.


The **main sequence** is the list of main key fingerings that starts with all fingers down and continues
by lifting successive fingers: for example, on a saxophone, the main keys are
1234567/CDEFGAB, and the main sequence is:

* 1 (C): 1234567: all main keys pressed, lowest pitch
* 2 (D): 234567
* 3 (E): 34567
* 4 (F): 4567
* 5 (G): 567
* 6 (A): 67
* 7 (B): 7
* 8 (C#): no main keys pressed, highest pitch

The main sequence is a reference: some of its notes may not appear in any specific
fingering system, like on the standard recorder fingering, where main sequence entry 4
is an invalid fingering.

## Mods

Modifier keys or mods include all the keys that aren't main keys - palm keys, keys
between notes, octave keys, as well as some main keys called lifts.

Modifiers could potentially do anything, but in existing instruments and standard
fingering systems, adding a modifier to a fingering either:

* Adds a semitone
* Adds an octave
* Goes to a completely different note
* Does nothing
* Makes the fingering invalid

Modifier keys are either **specific** and only apply to one or a few specific
fingerings, like palm keys on a saxophone, or **general**, and work everywhere or almost
everywhere, like octave keys.

### Mod sequences

Mod sequences are a convenience for representing running sequences like the very top
saxophone fingerings, where the fingers adds successive palm keys to move up by
semitones.

The fingering specification allows a sequence of mods, and then automatically builds all
the separate fingerings.

## Lifts

The idea of lifted main keys or lifts simplifies representing and learning the main
fingerings that are not on the main sequence - in the case of the sax, that's 120
fingerings, 128 main fingerings minus 8 in the main sequence.

Lifts allow the fingering system to easily represent fingerings like F# and one-finger
C on the sax, as well as the feature on Yamaha wind instruments where raising the index
finger on the left hand can raise the note an octave, useful for playing smooth runs
across the octave break.

The **base key** as the lowest main key that is pressed, and the "lifts" are all the
main keys above the base key that are _not_ pressed.

The base key determines the **base note**, and the lifts are available as modifiers.


## Possible types of fingering charts and displays

### Classic

The classic fingering chart starts with the lowest note and goes upward; it displays which keys
are pressed in black on a schematic of the instrument.

### Trill chart

There's one trill chart for each interval from a minor second to an octave. It shows the
classic fingering, but adds two color overlays showing the fingering to perform trills
up and down by some interval.

### Key chart

Charts by key instead of by note! For each key on the instrument, show all the
fingerings that use it, sorted by note.

### The fingering solver

Given a sequence of notes and a fingering systemw, print an optimal series of fingerings
to play the notes.

What "optimal" might mean is not obvious - "reducing number of fingers moved at each
step" is probably a good start, and would probably cover the break.

### Animated charts

For a piece of music, show the fingering as an animated chart.


## How it looks for the recorder




 a **multi-note fingering**,

(The final note that actually gets played from a multi-note fingering might depend on
almost anything: breath, embouchure, digital control information, randomness, or the
current state of the instrument itself at the time it is played. Mostly this can't be
formally represented, but there will be a special case for the harmonic series, and a
field for free-form text instructions to the performer, like "overblow very hard,
medium-tight embouchure".)


**Main fingerings** are fingerings that use only main keys. A saxophone has seven main
keys and therefore 2<sup>7</sup> or 128 possible main fingerings, though many or most of
them aren't useful.

(If you take into account all the keys, a 23-key saxophones has 2<sup>23</sup> or
8,388,608 conceivable fingerings, though many or most of them will be physically
unplayable, and few of them will generate useful sounds.)
