from __future__ import annotations

import dataclasses as dc
from collections.abc import Sequence
from typing import NamedTuple
from xml.etree.ElementTree import Element

from .fingering_system import Button


class Part(NamedTuple):
    def_: str
    style: str = ''

    def asdict(self) -> dict[str, str]:
        return {'href': f'#{self.def_}'} | ({'class': self.style} if self.style else {})

    @staticmethod
    def to_parts(s: str) -> list[Part]:
        pieces = s.split('+')
        return [Part(*(i.strip() for i in p.split('@', maxsplit=1))) for p in pieces]


@dc.dataclass(frozen=True)
class ChartPiece:
    parts: dict[str, list[Part]]
    x: int
    y: int

    def render(self, fingering: Sequence[Button]) -> list[Element]:
        for f in fingering:
            if parts := self.parts.get(f.name) or self.parts.get(f.short_name):
                break
        else:
            parts = self.parts['_off']
        d = {'x': str(self.x), 'y': str(self.y)}
        return [Element('use', d | p.asdict()) for p in parts]
