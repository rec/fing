from __future__ import annotations

import dataclasses as dc
from functools import cached_property
from typing import (
    NamedTuple,
)

from .layout import Layout


class Dims(NamedTuple):
    width: int
    height: int

    def asdict(self) -> dict[str, int]:
        return {'width': self.width, 'height': self.height}


@dc.dataclass(frozen=True)
class Sizes:
    layout: Layout
    columns: int
    rows: int

    @cached_property
    def document(self) -> Dims:
        w, h = self.page
        dw, dh = self.layout.inset.page
        return Dims(w + 2 * dw, h + 2 * dh)

    @cached_property
    def page(self) -> Dims:
        w, h = self.body
        dw, dh = self.layout.inset.body
        return Dims(w + 2 * dw, h + 2 * dh)

    @cached_property
    def body(self) -> Dims:
        w, h = self.charts
        dw, dh = self.layout.inset.charts
        return Dims(w + 2 * dw, h + 2 * dh + self.layout.title_height)

    @cached_property
    def charts(self) -> Dims:
        w, h = self.note_fingering
        dw, dh = self.layout.inset.note_fingering
        c, r = self.columns, self.rows
        return Dims(w * c + 2 * dw, h * r + 2 * dh)

    @cached_property
    def note_fingering(self) -> Dims:
        w, h = self.fingering
        dw, dh = self.layout.inset.fingering
        return Dims(w + 2 * dw, h + 2 * dh + self.layout.caption.height)

    @cached_property
    def fingering(self) -> Dims:
        return Dims(self.layout.width, self.layout.height)
