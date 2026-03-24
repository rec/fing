from __future__ import annotations

import dataclasses as dc
from enum import StrEnum, auto
from functools import cached_property
from typing import NamedTuple

from .layout import Inset, Layout


class Size(NamedTuple):
    width: int
    height: int

    def add(self, width: int = 0, height: int = 0) -> Size:
        return Size(self.width + width, self.height + height)

    def asdict(self) -> dict[str, int]:
        return {'width': self.width, 'height': self.height}


class SizedRegion(StrEnum):
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
        return self._size('body')

    @cached_property
    def body(self) -> Size:
        return self._size('chart').add(height=self.layout.title_height)

    @cached_property
    def chart(self) -> Size:
        w, h = self.note_fingering
        h += self.layout.fingering_pad
        width, height = w * (self.columns - 1), h * (self.rows - 1)
        return self._size('note_fingering').add(width=width, height=height)

    @cached_property
    def note_fingering(self) -> Size:
        return self._size('fingering').add(height=self.layout.caption.height)

    @cached_property
    def fingering(self) -> Size:
        return Size(self.layout.width, self.layout.height)

    def _size(self, name: str) -> Size:
        w, h = getattr(self, name)
        dw, dh = getattr(self.inset, name)
        return Size(w + 2 * dw, h + 2 * dh)


_REGIONS = {s.name for s in SizedRegion}
_PROPERTIES = {k for k, v in vars(Sizes).items() if isinstance(v, cached_property)}
assert _REGIONS | {'inset'} == _PROPERTIES, (_REGIONS, _PROPERTIES)
