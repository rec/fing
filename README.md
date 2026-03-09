# 🖐️ fing: Represent all fingering systems for wind instruments 🖐️

`fing` is a general representation of fingering systems for woodwinds, reeds, and keyed
brass.

It's primarily aimed at electronic wind instrument programmers and users, and wind
players wanting to notate alternative fingering systems such as multiphonics, but could
be useful to almost any instrumentalist wanting to teach others, or to delve deeply into
fingering patterns.

`fing` has three goals:

1. To represent new and existing fingering systems as documents that can easily be
   written, read and understood by humans and computers alike.

2. To easily create classic and new types of fingering charts - tables, images and even
   animations - for players at all levels.

3. To be usable on any keyed monophonic instrument, any human language, and any
   definition of note.


## Example: recorder fingering

Here's a full specification of the Baroque fingerings for the recorder family:

https://github.com/rec/fing/blob/main/fingerings/recorder-fingering.toml

It's written in a format called TOML designed to be straight-forward for both humans
and computers to read and write.

[This short layout document](https://github.com/rec/fing/blob/main/fingerings/recorder-fingering.layout.toml)
together with the specification above, created this image:

![Complete but sparse fingering chart for the recorder](https://github.com/rec/fing/blob/main/charts/recorder-fingerings.svg?raw=True)

## How does `fing` work?

### `Button`s and `Fingering`s

A `Button` is a key, pad, button, switch or lever that can be pressed, or a hole that
can be covered fully or partially, and a `Fingering` is a collection of zero or more
pressed `Button`s.

here's the `Button` definition for the octave hole on the recorder:

```
[buttons.octave]
short_name = 'oct'
press = "left-thumb"
description = 'Half-cover the thumb hole with the nail'
```

Fingerings are defined in terms of those Buttons, [like
this]([here](https://github.com/rec/fing/blob/162384854add21d460578b93a923776d5a1b069c/fingerings/recorder-fingering.toml#L80-L109)):

```
[fingerings]
all = 'oct lt l1 l2 l3 r1 r2 r3 r3h r4 r4h cb  '

C_1 = 'lt  l1  l2  l3  r1  r2  r3  r4      '
Db1 = 'lt  l1  l2  l3  r1  r2  r3  r4h     '
D_1 = 'lt  l1  l2  l3  r1  r2  r3          '
Eb1 = 'lt  l1  l2  l3  r1  r2  r3h         '

... many more ...
```

General modifier `Button`s which lower or raise all notes by a semitone, an
octave or some other value are also possible. It appears that every electronic
wind instrument has at least one modifier `Button`, if only an octave key.

### The `Layout`

There's a separate layout system to describe how to render a `FingeringSystem` into
graphical fingering `Chart`s using a simple, standard text-based graphical language called
Scalable Vector Graphics or [SVG](https://en.wikipedia.org/wiki/SVG).

You can have many different `Charts` for one fingering system and it's open-ended, so any
conceivable `Chart` can be created.

The resulting SVG can be displayed in any browser or web page, edited by hand as text or
with free and open source tools, embeded in a PDF, Illustrator, Photoshop or other
graphical document, and printed at any resolution.

## Development roadmap

### A change of plans

As of this writing, the representation of `Fingering` is stable and unlikely to change
in such a way as to break existing things.

One instrument, the recorder, has been completely specified, and also has a `Layout` that's
fairly neat and near completion.

The initial plan was to next go to saxophone next, but this is "more of the same", much
more graphic work, and doesn't bring any new features to the table.

And the primary motivation for this project was to represent new electronic wind
instrument fingerings.

### WX-7 and then "Simple"

The new plan is to first represent the WX-7 fingering, because it has _three_ types of
modifier `Button`s: "up or down N octaves", "up a semitone", and what I call a "lift":
in this case, where lifting the right index finger raises the pitch by an octave in
certain fingerings.

(On a personal note, even though I have played the WX-7 for almost forty years and feel
I know every detail of the fingering, I still expect to learn some details - like, what
does happen if you hold down multiple octave keys?)

Once all the modifier `Button` types exist, the next step is `Simple` - a general
fingering that is a perfect or close superset of almost every wind instrument that has
an octave key that goes up by an octave. excluding the clarinet, for example.
("Superset" means "the fingering you know works, but there are many others".)

As a teaser, `Simple` has three characteristics:

* Octave keys
* Each `Button` is either a "pad" or a modifier `Button`
* All "lifts" work as extra octave keys

Full definitions later!

Thanks for reading.

Feel free to start a discussion [here](https://github.com/rec/fing/discussions) or [open
an issue here](https://github.com/rec/fing/issues).


### Appendix: poorly-organized notes on SVG

If you're thinking of creating new fingering chart formats, the SVG snippets aren't so
terrible - here's all of them from the recorder fingering chart.

```
[layout]
styles = '''
.outline { fill: white; stroke: black; stroke-width: 1.5; }
'''
[layout.defs]
pad = '<circle cx="50" cy="50" r="50" />'
little-hole = '<circle cx="80" cy="55" r="20" />'
big-hole = '<circle cx="30" cy="30" r="30" />'
horizontal-line = '<rect x="0" y="50" width="120" height="1" style="fill: black;"/>'
octave = '<path d="  M 0,50   A 50,50 0 0 0 100,50   Z  " fill="black" />'
```

and then you re-use them like this:

```
[layout.pieces.left-thumb.parts]
_off = 'pad @ outline'
oct = 'pad @ outline + octave'
left-thumb = 'pad'

[layout.pieces.right-3.parts]
_off = 'little-hole @ outline + big-hole @ outline'
right-3 = 'little-hole + big-hole'
right-3-half = 'little-hole @ outline + big-hole'
```

where the image for the `oct` key is the circular `pad` Def with the `outline` style, plus
the `octave` Def, a half-filled circle.

The `path` instruction can be tricky, but this is something that LLMs do very well,
though that single line `octave` above is the only part of this whole project that was
done with an LLM (which, in fairness, came up with a better solution than I did, so I
used it.)
