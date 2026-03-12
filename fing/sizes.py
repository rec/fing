from __future__ import annotations

import dataclasses as dc
from functools import cached_property

from .layout import Inset, Layout


@dc.dataclass
class Rect:
    x: int
    y: int
    width: int
    height: int


@dc.dataclass(frozen=True)
class Sizes:
    layout: Layout
    columns: int
    rows: int

    @cached_property
    def inset(self) -> Inset:
        return self.layout.inset

    @cached_property
    def document(self) -> Rect:
        return Rect(0, 0, *self._col_row('page'))

    @cached_property
    def page(self) -> Rect:
        return Rect(*self.inset.page, *self._col_row('body'))

    @cached_property
    def body(self) -> Rect:
        w, h = self._col_row('charts')
        return Rect(*self.inset.body, w, h + self.layout.title_height)

    @cached_property
    def charts(self) -> Rect:
        r = self.note_fingering
        dw, dh = self.inset.note_fingering
        w = r.width * self.columns + 2 * dw
        h = r.height * self.rows + 2 * dh + self.layout.fingering_pad * (self.rows - 1)
        x, y = self.inset.charts

        return Rect(x, y + self.layout.title_height, w, h)

    @cached_property
    def note_fingering(self) -> Rect:
        w, h = self._col_row('fingering')
        return Rect(*self.inset.note_fingering, w, h + self.layout.caption.height)

    @cached_property
    def fingering(self) -> Rect:
        return Rect(*self.inset.fingering, self.layout.width, self.layout.height)

    def _col_row(self, name: str, columns: int = 1, rows: int = 1) -> tuple[int, int]:
        r = getattr(self, name)
        dw, dh = getattr(self.inset, name)
        return r.width * columns + 2 * dw, r.height * rows + 2 * dh
