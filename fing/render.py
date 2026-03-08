from __future__ import annotations

import dataclasses as dc
from collections.abc import Sequence
from functools import cached_property
from typing import Any
from xml.etree.ElementTree import Element, SubElement

from .fingering_system import Button, Fingerings
from .layout import Layout
from .note import Note


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
        return Element('svg', d)

    def _add(self, tag: str, parent: Element | None = None, **kwargs: Any) -> Element:
        parent = self.svg if parent is None else parent
        return SubElement(parent, tag, {k: str(v) for k, v in kwargs.items()})

    def __call__(self) -> Element:
        self._add('defs').extend(self.layout.defs)
        styles = '\n    '.join(('', *self.layout.styles.strip().split('\n'))) + '\n  '
        self._add('style').text = styles

        for i, (note, fingering) in enumerate(self.fingerings.items()):
            self._note_fingering(i, note, fingering)

        assert self.rows == 2, self.rows
        for row in range(1, self.rows):
            y = self.layout.scale(0, row)[1] - self.layout.pad_y // 2
            self._add('rect', x=0, y=y, width=self.dims[0], height=3)

        return self.svg

    def _note_fingering(self, i: int, note: Note, fingering: Sequence[Button]) -> None:
        row, column = divmod(i, self.columns)
        x, y = self.layout.scale(column, row)
        sub = self._add('svg', x=x, y=y)
        pieces = self._add('svg', sub, x=str(self.layout.buttons_inset))
        for piece in self.layout.pieces:
            pieces.extend(piece.render(fingering))

        text = self._add('text', sub, **self.layout.caption.asdict())
        text.text = str(note).center(6)

        if self.layout.caption.above:
            text.set('y', str(self.layout.spacing - self.layout.caption.pad))
            pieces.set('y', str(self.layout.spacing))
        else:
            text.set('y', str(self.layout.height))
