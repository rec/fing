# 🖐️ fing: A universal representation of fingering systems for winds, reeds, and brass 🖐️

## Abstract

`fing` is a universal representation of fingering systemss for monophonic keyed
instruments, including but not limited to winds, reeds, and keyed brass.

The two motivating goals are to make it convenient and clear to represent a fingering
system as a document that can be read by computers and humans, like TOML or JSON, and to
be able to automatically create all sorts of fingering tables for any individual
fingering system beyond the standard single one.

There's quite a lot of ideas here, none really hard, and at the end there is a fairly
simple format which can represent both all existing fingerings, and new ones, perhaps
simplified, or optimized, or even just plain weird, designed to be as hard as possible
or to play backwards or sideways.

## Definitions

**Monophonic** (mono) instruments only play a single note or tone at a time, like wind and
brass instruments.

A **key** is a button that can be pressed and held, or a hole that can be covered on an
instrument.

A **fingering** is a set of keys being pressed at the same time.

A **note-fingering** is a note with a fingering that can play it. (**Note** and
**scale** are used informally and generally here: see the `tuney` project for a full
specification of tunings and scales.)

A **fingering system** is a set of note-fingerings.

In a fingering system, a note can correspond to many fingerings, and a fingering can
also correspond to multiple notes, a **multi-note fingering**, like in brass instruments
or overblown winds, and an **invalid fingering** is one that does not appear anywhere in
the system.

## Doing better than just listing note fingerings

Listing all the note-fingerings individually is the simplest way to go, and in many
cases will be the best way for small numbers of keys. Any complete fingering system will
have to allow a list of key fingerings as part of it.

But most wind instruments have a linearity to many of their keys, taking
advantage of the natural smoothness and speed of raising or lowering successive fingers
in linear sequence.

These more-or-less linear keys are called **main keys** because that seems to be a
common name this in existing instruments.

Other keys like palm and octave keys change the result of the main keys for one, a few,
or in the case of octave keys, many notes: these are called **modifier keys** or **mods**.

The final note that the instrument makes is, conceptually, set by the base keys, and
then changed by the modifiers.

## Main keys.

Some keys are **main keys** or finger keys. Each key has its own unique human
finger that presses it. An ocarina fingering system might have no main keys and one for
a recorder might have only main keys.

Main keys have numbers: they are numbered sequentially starting at 1, the lowest key
in pitch.

By default, the names of main keys start with C and continue through whole notes in
the C scale, but this can all be customized.

**Main fingerings** are fingerings that use only main keys. A saxophone has seven main
keys and therefore 128 or 2 to the power of 7 possible main fingerings, though many or
most of them aren't useful.

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
fingering systems, adding a single modifier to a fingering either:

* Adds a semitone
* Adds two semitones (for lifts only)
* Goes to a completely different note
* Does nothing
* Makes it invalid

Modifier keys are either **specific** and only apply to one or a few specific
fingerings, like palm keys on a saxophone, or **general**, and work everywhere or almost
everywhere, like octave keys.

### Mod sequences

Mod sequences are a convenience for representing running sequences like the very top
saxophone fingerings, with a chromatic scale

## Lifts

The idea of lifted main keys or lifts simplifies representing and learning the main
fingerings that are not on the main sequence - in the case of the sax, that's 120
fingerings, 128 main fingerings minus 8 in the main sequence.

Lifts allow the fingering system to easily represent fingerings like F# and one-finger
C on the sax, as well as the feature on Yamaha wind instruments where raising the index
finger on the left hand can raise the note an octave, useful for playing smooth runs
across the octave break.

Define the **base key** as the lowest main key that is pressed, and the "lifts" to be
all the main keys above the base key that are _not_ pressed.

The base key determines the **base note**, and lifts become modifiers.

## How it looks for the saxophone



(The final note that actually gets played from a multi-note fingering might depend on
almost anything: breath, embouchure, digital control information, randomness, or the
current state of the instrument itself at the time it is played. Mostly this can't be
formally represented, but there will be a special case for the harmonic series, and a
field for free-form text instructions to the performer, like "overblow very hard,
medium-tight embouchure".)
