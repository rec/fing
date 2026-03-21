from __future__ import annotations

import dataclasses as dc
from enum import StrEnum, auto
from functools import cached_property

from .layout import Inset, Layout


@dc.dataclass
class Rect:
    x: int
    y: int
    width: int
    height: int


class Region(StrEnum):
    page = auto()
    body = auto()
    charts = auto()
    note_fingering = auto()
    fingering = auto()


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
        r = self.page
        dw, dh = self.inset.page
        result = r.width + 2 * dw, r.height + 2 * dh
        return Rect(0, 0, *result)

    @cached_property
    def page(self) -> Rect:
        r = self.body
        dw, dh = self.inset.body
        result = r.width + 2 * dw, r.height + 2 * dh
        return Rect(*self.inset.page, *result)

    @cached_property
    def body(self) -> Rect:
        r = self.charts
        dw, dh = self.inset.charts
        result = r.width + 2 * dw, r.height + 2 * dh
        w, h = result
        return Rect(*self.inset.body, w, h + self.layout.title_height)

    @cached_property
    def charts(self) -> Rect:
        r = self.note_fingering
        w = r.width * self.columns
        h = r.height * self.rows + self.layout.fingering_pad * (self.rows - 1)
        x, y = self.inset.charts

        return Rect(x, y + self.layout.title_height, w, h)

    @cached_property
    def note_fingering(self) -> Rect:
        r = self.fingering
        dw, dh = self.inset.fingering
        result = r.width + 2 * dw, r.height + 2 * dh
        w, h = result
        return Rect(*self.inset.note_fingering, w, h + self.layout.caption.height)

    @cached_property
    def fingering(self) -> Rect:
        return Rect(*self.inset.fingering, self.layout.width, self.layout.height)


_REGIONS = {s.name for s in Region}
_PROPERTIES = {k for k, v in vars(Sizes).items() if isinstance(v, cached_property)}
assert _REGIONS | {'inset', 'document'} == _PROPERTIES, (_REGIONS, _PROPERTIES)
