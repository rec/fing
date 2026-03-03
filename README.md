# 🖐️ fing: Represent all fingering systems for wind instruments 🖐️

`fing` is a general representation of fingering systems for woodwinds, reeds, and
keyed brass.

`fing` has three goals:

1. To represent existing and new fingering systems as documents that can easily be
   created, read and understood by humans and computers alike.

2. To easily create classic and new types of fingering charts, tables, images and even
   animations, for existing and new fingering systems.

3. To be adaptable to any keyed monophonic instrument, any human language, and any
   concept of note.


## Example: recorder fingering

Here's a full specification of the Baroque fingerings for the recorder family:

https://github.com/rec/fing/blob/main/fingerings/recorder-fingering.toml

It's written in a format called TOML designed to be straight-forward for both humans
and computers to read and write.

This is a specification format, and it isn't great for learners, but `fing` also
provides a general system for making fingering charts without writing Python programs.

[This formatting document](https://github.com/rec/fing/blob/main/fingerings/recorder-fingering.layout.toml), together with the specification above, created this image:

![alt text](https://github.com/rec/fing/blob/main/test/all-recorder-fingerings.svg?raw=True)


## What am I looking at? Some quick definitions

A **button** is the basic element in `fing`: a key, pad, button or lever to press, or a
hole to fully or partially cover, or any other
[affordance](https://www.skillshare.com/en/blog/affordance-the-silent-signal-that-divides-art-and-design/)
that controls a wind instrument.

A button is created with four properties:
  * `name`: the full button name, e.g. `left-1` or `octave`
  * `short_name`: usually 2 or 3 characters, e.g. `l1`, `oct`
  * `press`: the finger or other thing that presses or actuates this button, i.e. `left-thumb`
  * `description`: an optional free-form text field with instructions for the player


`fing` buttons have only two states, **on** or **pressed**, and **off**.

Physical holes or pads that can be partly pressed are handled by creating a separate
button for the partial state: in the recorder, there is one button, `left-thumb`,
representing "thumb hole closed" and another button, `octave`, representing "thumb
half-closed".

A **fingering** is a collection of **pressed** buttons.

A **fingering system** is a collection of fingerings for notes.

(A **note** is potentially very general, to include multiphonics, microtones, or just
plain noise, but everything so far uses the standard Western scale using the letters A
through G and the ♯ and ♭ symbols, with # and b accepted on input.)

Within a fingering system, a note **has** a fingering, and a fingering **produces** a
note.

One note might have more than one fingering; one fingering might produce more than one
note (due to overblowing or embouchure).


#
# A key has three parts:
#
#  * "short name": usually 2 or 3 characters, for text-based fingering charts
#
#  * "press": the finger or other thing that presses or actuates this key
#
#  * "description": an optional field with more text information for the player
#
# Multiple keys might share the same physical location.

# For example, the thumb hole on the recorder can be covered in two different ways:
#
# * fullly to produce the lower octave
# * half-covered for the upper octave
#
# This is represented by having two different keys: "left-thumb" and "octave".

# TO MOVE elsewhere
# Wind instruments are played by blowing and fingering. Players control the pictch of
# their instrument using fingering, breath, embouchure and perhaps other actions like
# covering the bell.
