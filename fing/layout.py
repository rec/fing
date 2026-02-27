from __future__ import annotations

import dataclasses as dc
from collections.abc import Sequence
from typing import Any, TypeAlias
from xml.etree import ElementTree as ET

import tomlkit

from fing.chart_piece import ChartPiece, Part

from .error_maker import ErrorMaker

Element: TypeAlias = ET.Element


@dc.dataclass(frozen=True)
class Layout:
    defs: Sequence[Element]
    pieces: Sequence[ChartPiece]
    size: tuple[int, int]
    spacing: int
    style: str


@dc.dataclass(frozen=True)
class LayoutSpec:
    defs: dict[str, Any]
    pieces: dict[str, dict[str, Any]]
    spacing: int = 0
    style: str = ''
    width: int = 0


_NAMES = {f.name for f in dc.fields(LayoutSpec)}
_REQUIRED = {
    f.name
    for f in dc.fields(LayoutSpec)
    if f.default == dc.MISSING and f.default_factory == dc.MISSING
}


def make(filename: str, key_names: dict[str, Any]) -> Layout:
    defs, pieces = {}, {}

    with ErrorMaker() as err:
        with open(filename) as fp:
            data = tomlkit.load(fp)
        if not isinstance(d := data.get('layout'), dict):
            err.fail('No layout dictionary')

        assert isinstance(d, dict)
        if bad := set(d) - _NAMES:
            err('Unknown arg', *bad)
        if missing := _REQUIRED - set(d):
            err('Missing arg', *missing)
        err.check()

        assert isinstance(d, dict)
        spec = LayoutSpec(**d)

        for k, v in spec.defs.items():
            try:
                defs[k] = ET.fromstring(v)
            except Exception as e:
                err('Bad XML in def', e, k, v)
            else:
                defs[k].set('id', k)

        x, y, dy = 0, 0, spec.spacing
        for name, key in spec.pieces.items():
            if not isinstance(key.get('parts'), dict):
                err('Missing parts section', name, key)
                continue
            if not (name.startswith('_') or name in key_names):
                err('Unknown key name', name)

            parts = {k: Part.to_parts(v) for k, v in key['parts'].items()}

            if '_off' not in parts:
                err('Missing parts.off section', name)
            if u := [p for pp in parts.values() for p in pp if p.def_ not in defs]:
                err('Unknown def in parts', name, u)

            x = x if (x_ := key.get('x')) is None else x_
            y = y if (y_ := key.get('y')) is None else y_
            pieces[name] = ChartPiece(parts, x, y)
            y += dy

    return Layout(
        defs=list(defs.values()),
        pieces=list(pieces.values()),
        size=(spec.width, y + dy + 20),
        spacing=spec.spacing,
        style=spec.style,
    )


if __name__ == '__main__':
    import sys

    print(make(sys.argv[1], {}))
