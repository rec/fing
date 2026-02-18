# 🖐️ fing: A universal representation of fingering systems for winds, reeds, and brass 🖐️

## Abstract

`fing` is a universal representation of fingering systemss for monophonic
keyed instruments, including but not limited to winds, reeds, and keyed brass.

## Definitions

**Monophonic** (mono) instruments only play a single note or tone at a time, like wind and
brass instruments.

A **key** is a button that can be pressed and held, or a hole that can be covered on an
instrument.

A **fingering** is a set of keys being pressed at the same time.

A **note-fingering** is a note with a fingering that can play it. (**Note** and
**scale** are used informally and generally here: see the `tuney` project for a full
specification of tunings and scales.)

A **fingering system** is a set of note-fingerings. In one sytem, one note can
correspond to many fingerings, and one fingering can correspond to multiple notes (a
**multi-note fingering** or **multi**), like in brass instruments or overblown winds.

(The final choice of note from a multi might depend on almost anything: breath,
embouchure, control information, randomness, or the state of the instrument
itself. Mostly this can't be formally represented, but there will be a special case for
the harmonic series, and a field for free-form text instructions to the performer, like
"overblow very hard, medium-tight embouchure".)

## Can we do better than just listing note fingerings?

Listing all the note-fingerings individually is the simplest way to go, and in many
cases will be the best way: looking at, say, the fingering charts of the varieties of
ocarina, there doesn't seem to be a clear organizing principle, and there are only a
small number of fingerings in brass.

But most wind instruments fingerings have a linearity to them, taking advantage of the
natural smoothness and speed of raising or lowering successive fingers in sequence.

Keys naturally divide into **main keys** (finger keys) and **modifier keys** (palm and octave keys).

Each main key has its own unique human finger that presses it. There seem to be 6 to 10
main keys in existing wind instruments.







## Tricky edge cases

* Partly covered holes
* Brass instruments
