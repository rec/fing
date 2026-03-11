from __future__ import annotations

import dataclasses as dc
import os
from collections.abc import Sequence
from functools import cached_property
from typing import Any
from xml.etree.ElementTree import Element, SubElement

from .fingering_system import Button, Fingerings
from .layout import Layout
from .note import Note

HIGHLIGHT_SVGS = 'HIGHLIGHT_SVGS' in os.environ

COLORS = '#FDD', '#DFD', '#DDF', '#FFA', '#FAF', '#AFF'
CLASSES = 'page', 'body', 'note-fingering', 'pieces'

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
        x, y = self.layout.margin
        return self._add(self.svg, 'svg', 'page', x=x, y=y)

    @cached_property
    def body(self) -> Element:
        return self._add(self.page, 'svg', 'body', y=self.layout.title_height)

    def _add(self, parent: Element, tag: str, *classes: str, **kwargs: Any) -> Element:
        if classes:
            kwargs['class'] = ' '.join(classes)
        r = SubElement(parent, tag, {k: str(v) for k, v in kwargs.items()})
        if tag == 'svg' and HIGHLIGHT_SVGS:
            global COLOR
            try:
                ci = CLASSES.index(classes[0])
            except IndexError:
                ci = COLOR
            color = COLORS[ci]
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
            width = self.dims[0]
            self._add(self.body, 'rect', 'large-separator', y=y, width=width, height=3)

        return self.svg

    def _note_fingering(self, i: int, note: Note, fingering: Sequence[Button]) -> None:
        row, column = divmod(i, self.columns)
        x, y = self.layout.scale(column, row)
        note_fingering = self._add(self.body, 'svg', 'note-fingering', x=x, y=y)
        pieces = self._add(note_fingering, 'svg', 'pieces', x=self.layout.buttons_inset)
        for piece in self.layout.pieces:
            pieces.extend(piece.render(fingering))

        text = self._add(
            note_fingering, 'text', 'caption', **self.layout.caption.asdict()
        )
        text.text = str(note).center(6)

        if self.layout.caption.above:
            text.set('y', str(self.layout.caption.font_size))
            pieces.set('y', str(self.layout.caption.height))
        else:
            text.set('y', str(self.layout.height))
