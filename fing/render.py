from __future__ import annotations

import dataclasses as dc
from collections.abc import Sequence
from functools import cached_property
from typing import Any
from xml.etree.ElementTree import Element, SubElement

from .fingering_system import Button, Fingerings
from .layout import Layout
from .note import Note

HIGHLIGHT_SVGS = False

COLORS = '#FDD', '#DFD', '#DDF', '#FFA', '#FAF', '#AFF'
COLOR = 0


@dc.dataclass(frozen=True)
class Renderer:
    layout: Layout
    fingerings: Fingerings

    @cached_property
    def columns(self) -> int:
        N = len(self.fingerings)
        columns = N // self.rows
        return columns + (N > columns * self.rows)

    @cached_property
    def rows(self) -> int:
        return self.layout.rows

    @cached_property
    def dims(self) -> tuple[int, int]:
        w, h = self.layout.scale(self.columns, self.rows)
        return w, h + self.layout.buttons_inset

    @cached_property
    def svg(self) -> Element:
        width, height = self.dims
        d = {'viewBox': f'0 0 {width} {height}', 'xmlns': 'http://www.w3.org/2000/svg'}
        svg = Element('svg', d)
        self._add(svg, 'defs').extend(self.layout.defs)

        styles = '\n    '.join(('', *self.layout.styles.strip().split('\n'))) + '\n  '
        self._add(svg, 'style').text = styles
        return svg

    @cached_property
    def page(self) -> Element:
        return self._add(self.svg, 'svg', x=self.layout.margin, y=self.layout.margin)

    @cached_property
    def body(self) -> Element:
        return self._add(self.page, 'svg', y=self.layout.title_height)

    def _add(self, parent: Element, tag: str, **kwargs: Any) -> Element:
        r = SubElement(parent, tag, {k: str(v) for k, v in kwargs.items()})
        if tag == 'svg' and HIGHLIGHT_SVGS:
            global COLOR
            color = COLORS[COLOR]
            COLOR = (COLOR + 1) % len(COLORS)

            SubElement(r, 'rect', {'width': '100%', 'height': '100%', 'fill': color})
        return r

    def __call__(self) -> Element:
        self.page.append(self.layout.title)

        for i, (note, fingering) in enumerate(self.fingerings.items()):
            self._note_fingering(i, note, fingering)

        assert self.rows == 2, self.rows
        for row in range(1, self.rows):
            y = self.layout.scale(0, row)[1] - self.layout.pad_y // 2
            self._add(self.body, 'rect', x=0, y=y, width=self.dims[0], height=3)

        return self.svg

    def _note_fingering(self, i: int, note: Note, fingering: Sequence[Button]) -> None:
        row, column = divmod(i, self.columns)
        x, y = self.layout.scale(column, row)
        note_fingering = self._add(self.body, 'svg', x=x, y=y)
        pieces = self._add(note_fingering, 'svg', x=self.layout.buttons_inset)
        for piece in self.layout.pieces:
            pieces.extend(piece.render(fingering))

        text = self._add(note_fingering, 'text', **self.layout.caption.asdict())
        text.text = str(note).center(6)

        if self.layout.caption.above:
            text.set('y', str(self.layout.caption.font_size))
            pieces.set('y', str(self.layout.caption.height))
        else:
            text.set('y', str(self.layout.height))
