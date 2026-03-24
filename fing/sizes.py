from __future__ import annotations

import dataclasses as dc
from enum import StrEnum, auto
from functools import cached_property

from .layout import Inset, Layout


@dc.dataclass
class Size:
    width: int
    height: int


class Region(StrEnum):
    document = auto()
    body = auto()
    chart = auto()
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
    def document(self) -> Size:
        dw, dh = self.inset.body
        return Size(self.body.width + 2 * dw, self.body.height + 2 * dh)

    @cached_property
    def body(self) -> Size:
        dw, dh = self.inset.chart
        w = self.chart.width + 2 * dw
        h = self.chart.height + 2 * dh + self.layout.title_height
        return Size(w, h)

    @cached_property
    def chart(self) -> Size:
        dw, dh = self.inset.note_fingering
        w = self.note_fingering.width * self.columns + 2 * dw
        pad = self.layout.fingering_pad * (self.rows - 1)
        h = self.note_fingering.height * self.rows + pad + 2 * dh
        return Size(w, h)

    @cached_property
    def note_fingering(self) -> Size:
        dw, dh = self.inset.fingering
        w, h = self.fingering.width + 2 * dw, self.fingering.height + 2 * dh
        return Size(w, h + self.layout.caption.height)

    @cached_property
    def fingering(self) -> Size:
        return Size(self.layout.width, self.layout.height)


_REGIONS = {s.name for s in Region}
_PROPERTIES = {k for k, v in vars(Sizes).items() if isinstance(v, cached_property)}
assert _REGIONS | {'inset'} == _PROPERTIES, (_REGIONS, _PROPERTIES)
