from __future__ import annotations

import dataclasses as dc
from xml.etree import ElementTree


@dc.dataclass(frozen=True)
class ChartPiece:
    location: tuple[int, int]
    image: dict[str, str]
    svg: str = ''


@dc.dataclass(frozen=True)
class LayoutSpec:
    defs: dict[str, str]
    pieces: dict[str, ChartPiece]
    svg: dict[str, str]


def add_ids(refs: dict[str, str]) -> dict[str, ElementTree.Element]:
    r = {}
    for k, v in refs.items():
        r[k] = ElementTree.fromstring(v)
        r[k].set('id', k)
    return r
