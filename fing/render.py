from __future__ import annotations

import dataclasses as dc
import os
from collections.abc import Sequence
from functools import cached_property
from typing import Any, NamedTuple
from xml.etree.ElementTree import Element, SubElement

from .fingering_system import Button, Fingerings
from .layout import Layout
from .note import Note

HIGHLIGHT_SVGS = 'HIGHLIGHT_SVGS' in os.environ

COLORS = '#FDD', '#DFD', '#DDF', '#FFA', '#FAF', '#AFF'

COLOR = 0
NOTE_WIDTH = len('C#/D1')


CONTAINERS = 'document', 'page', 'body', 'note-fingering', 'fingering'


@dc.dataclass(frozen=True)
class Inset:
    document: int = 0
    page: int = 0
    body: int = 0
    note_fingering: int = 0


@dc.dataclass(frozen=True)
class Size:
    inset: Contain
    offset: Contain
    row: int
    columns: int
    width: int
    height: int

    @cached_property
    def to_size(self) -> dict[str, tuple[int, int]]:
        t = {}
        for f in reversed(dc.fields(Inset)):
            if f.name = 'note_fingering':
                w, h = self.width, self.height
            elif f.name == 'body':
                w, h = self.columns * w, self.rows * h
            di = 2 * getattr(self.inset(f.name))
            w, h = w + di`, h + di
            t[f.name] = (w, h)

        return dict(it())


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
        return w + 500, h + 500

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
    def document(self) -> Element:
        x, y = self.layout.margin
        return self._add(self.svg, 'svg', 'document', x=x, y=y)

    @cached_property
    def page(self) -> Element:
        x, y = self.layout.margin
        return self._add(self.document, 'svg', 'page', x=x, y=y)

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
                ci = CONTAINERS.index(classes[0])
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
            y = self.layout.scale(0, row)[1]
            width = self.dims[0]
            self._add(self.body, 'rect', 'large-separator', y=y, width=width, height=3)

        return self.svg

    def _note_fingering(self, i: int, note: Note, fingering: Sequence[Button]) -> None:
        row, column = divmod(i, self.columns)
        x, y = self.layout.scale(column, row)
        note_fingering = self._add(self.body, 'svg', 'note-fingering', x=x, y=y)
        pieces = self._add(note_fingering, 'svg', 'fingering')
        for piece in self.layout.pieces:
            pieces.extend(piece.render(fingering))

        d = self.layout.caption.asdict()
        text = self._add(note_fingering, 'text', 'caption', **d)
        text.text = str(note).center(NOTE_WIDTH)

        if self.layout.caption_above:
            text.set('y', str(self.layout.caption.font_size))
            pieces.set('y', str(self.layout.caption.height))
        else:
            text.set('y', str(self.layout.height))
