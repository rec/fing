# 🖐️ fing: Represent all fingering systems for wind instruments 🖐️

`fing` is a general representation of fingering systems for woodwinds, reeds, and
keyed brass.

`fing` has three goals:

1. To represent existing and new fingering systems as documents that can easily be
   created, read and understood by humans and computers alike.

2. To easily create classic and new types of fingering charts, tables, images and even
   animations, for existing and new fingering systems.

3. To be adaptable to any keyed monophonic instrument, any human language, and any
   definition of note.


## Example: recorder fingering

Here's a full specification of the Baroque fingerings for the recorder family:

https://github.com/rec/fing/blob/main/fingerings/recorder-fingering.toml

It's written in a format called TOML designed to be straight-forward for both humans
and computers to read and write.

It isn't trying to be good for learners, but `fing` also provides a general system for
making fingering charts without writing Python programs.

[This short layout document](https://github.com/rec/fing/blob/main/fingerings/recorder-fingering.layout.toml)
together with the specification above, created this image:

![Complete but sparse fingering chart for the recorder](https://github.com/rec/fing/blob/main/charts/all-recorder-fingerings.svg?raw=True)

A final chart would have "more stuff" on it; this shows how it can be done in one page
of layout.

# How does `fing` work, in 90 seconds?

`fing` represents fingering systems using Buttons: keys, pads, buttons, or switches that
can be pressed, holes that can be covered, etc.

A Button definition looks like this:

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

General "modifier" Buttons like in electronic wind instruments are also possible.

There's a separate layout system to describe how to render a Fingering System into
graphical Fingering Charts in a simple, standard text-based graphical language called
Scalable Vector Graphics or [SVG](https://en.wikipedia.org/wiki/SVG).

The result can be displayed in any browser or web page, edited by hand as text or with
free and open source tools, embeded in a PDF, Illustrator, Photoshop or other graphical
document, and printed at any resolution.

### Appendix: notes on SVG

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
