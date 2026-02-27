from __future__ import annotations

import dataclasses as dc
from collections.abc import Sequence
from typing import NamedTuple
from xml.etree.ElementTree import Element


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

    def asdict(self) -> dict[str, str]:
        return {'x': str(self.x), 'y': str(self.y)}

    def render(self, fingering: Sequence[str]) -> Element:
        for p in fingering:
            if parts := self.parts.get(p):
                break
        else:
            parts = self.parts['_off']
        elems = [Element('use', self.asdict() | p.asdict()) for p in parts]
        if len(elems) == 1:
            return elems[0]

        g = Element('g')
        g.extend(elems)
        return g
