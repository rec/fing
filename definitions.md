# Definitions of terms used in `fing`

A **Button** is the basic element in `fing`: a key, pad, Button or lever to press, or a
hole to fully or partially cover, or any other
[affordance](https://www.skillshare.com/en/blog/affordance-the-silent-signal-that-divides-art-and-design/)
that controls a wind instrument.

A Button is defined with four properties:
  * `name`: the full Button name, e.g. `left-1` or `octave`
  * `short_name`: usually 2 or 3 characters, e.g. `l1`, `oct`
  * `press`: the finger or other thing that presses or actuates this Button, i.e. `left-thumb`
  * `description`: an optional free-form text field with instructions for the player

[Here's](https://github.com/rec/fing/blob/162384854add21d460578b93a923776d5a1b069c/fingerings/recorder-fingering.toml#L20-L23)
the definition of the `octave` Button.

Buttons have only two states, **on**/**pressed**, and **off**.

Physical holes or pads that can be partly pressed are handled by creating a separate
Button for the partial state: in recorder fingering, there is one Button, `left-thumb`,
representing "thumb hole closed", and another Button, `octave`, representing "thumb
half-closed".

--------

A **Fingering** is a collection of **pressed** Buttons.

A **Note Fingering** is a Note, together with a Fingering that can produce that note.

A **Note** is potentially very general, to include multiphonics, microtones, or just
plain noise, but the work so far uses the standard Western scale, the letters A through
G and the ♯ and ♭ symbols, with # and b accepted on input.

-------

A **Fingering System** is a collection of Fingerings for Notes.

Within a Fingering System, we'll say that a Note **has** a Fingering, and a Fingering
can **produce** a Note. One Note might have more than one Fingering; one Fingering might
produce more than one Note, controlled by e.g. overblowing or embouchure.

And finally, a **Chart** is an image or other graphical representation of one or more
Note Fingerings.
