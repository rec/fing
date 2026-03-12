from __future__ import annotations

import dataclasses as dc
from functools import cached_property

from fing.layout import Inset


@dc.dataclass(frozen=True)
class Sizes:
    inset: Inset
    columns: int
    rows: int
    width: int
    height: int

    @cached_property
    def document(self) -> tuple[int, int]:
        w, h = self.page
        dw, dh = self.inset.document
        return w + 2 * dw, h + 2 * dh

    @cached_property
    def page(self) -> tuple[int, int]:
        w, h = self.body
        dw, dh = self.inset.page
        return w + 2 * dw, h + 2 * dh

    @cached_property
    def body(self) -> tuple[int, int]:
        w, h = self.note_fingering
        dw, dh = self.inset.body
        r, c = self.rows, self.columns
        return w * r + 2 * dw, h * c + 2 * dh

    @cached_property
    def note_fingering(self) -> tuple[int, int]:
        w, h = self.width, self.height
        dw, dh = self.inset.note_fingering
        return w + 2 * dw, h + 2 * dh
