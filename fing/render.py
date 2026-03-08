from __future__ import annotations

import dataclasses as dc
from functools import cached_property
from typing import Any
from xml.etree.ElementTree import Element, SubElement

from .fingering_system import FingeringSystem
from .layout import Layout


@dc.dataclass(frozen=True)
class Renderer:
    layout: Layout
    fingerings: FingeringSystem

    @cached_property
    def columns_rows(self) -> tuple[int, int]:
        N = len(self.fingerings.fingerings)
        rows = self.layout.rows
        columns = N // rows
        columns += N > (columns * rows)
        return columns, rows

    @cached_property
    def dims(self) -> tuple[int, int]:
        w, h = self.layout.scale(*self.columns_rows)
        return w, h + self.layout.buttons_inset

    @cached_property
    def svg(self) -> Element:
        width, height = self.dims
        d = {'viewBox': f'0 0 {width} {height}', 'xmlns': 'http://www.w3.org/2000/svg'}
        return Element('svg', d)

    def __call__(self) -> Element:
        self._add('defs').extend(self.layout.defs)
        styles = '\n    '.join(('', *self.layout.styles.strip().split('\n'))) + '\n  '
        self._add('style').text = styles

        for i, (note, fingering) in enumerate(self.fingerings.fingerings.items()):
            row, column = divmod(i, self.columns_rows[0])
            x, y = self.layout.scale(column, row)
            if row and not column:
                yr = y - self.layout.pad_y // 2
                self._add('rect', x=x, y=yr, width=self.dims[0], height=3)
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

        return self.svg

    def _add(self, tag: str, parent: Element | None = None, **kwargs: Any) -> Element:
        parent = self.svg if parent is None else parent
        return SubElement(parent, tag, {k: str(v) for k, v in kwargs.items()})
