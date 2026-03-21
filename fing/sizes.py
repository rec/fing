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
        dw, dh = self.inset.page
        return Rect(0, 0, self.page.width + 2 * dw, self.page.height + 2 * dh)

    @cached_property
    def page(self) -> Rect:
        dw, dh = self.inset.body
        return Rect(
            *self.inset.page, self.body.width + 2 * dw, self.body.height + 2 * dh
        )

    @cached_property
    def body(self) -> Rect:
        dw, dh = self.inset.charts
        w, h = self.charts.width + 2 * dw, self.charts.height + 2 * dh
        return Rect(*self.inset.body, w, h + self.layout.title_height)

    @cached_property
    def charts(self) -> Rect:
        w = self.note_fingering.width * self.columns
        h = self.note_fingering.height * self.rows + self.layout.fingering_pad * (
            self.rows - 1
        )
        x, y = self.inset.charts

        return Rect(x, y + self.layout.title_height, w, h)

    @cached_property
    def note_fingering(self) -> Rect:
        dw, dh = self.inset.fingering
        w, h = self.fingering.width + 2 * dw, self.fingering.height + 2 * dh
        return Rect(*self.inset.note_fingering, w, h + self.layout.caption.height)

    @cached_property
    def fingering(self) -> Rect:
        return Rect(*self.inset.fingering, self.layout.width, self.layout.height)


_REGIONS = {s.name for s in Region}
_PROPERTIES = {k for k, v in vars(Sizes).items() if isinstance(v, cached_property)}
assert _REGIONS | {'inset', 'document'} == _PROPERTIES, (_REGIONS, _PROPERTIES)
