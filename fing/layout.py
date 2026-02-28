from __future__ import annotations

import dataclasses as dc
from typing import Any, TypeAlias
from xml.etree import ElementTree as ET

import tomlkit

from fing.chart_piece import ChartPiece, Part

from .error_maker import ErrorMaker

Element: TypeAlias = ET.Element


@dc.dataclass(frozen=True)
class Layout:
    defs_: list[Element]
    pieces_: list[ChartPiece]
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

    @staticmethod
    def make(filename: str, err: ErrorMaker) -> LayoutSpec:
        with open(filename) as fp:
            data = tomlkit.load(fp)

        if not isinstance(d := data.get('layout'), dict):
            raise err.fail('No layout dictionary')

        assert isinstance(d, dict)
        if bad := set(d) - _NAMES:
            err('Unknown arg', *bad)
        if missing := _REQUIRED - set(d):
            err('Missing arg', *missing)
        err.check()
        return LayoutSpec(**d)


_NAMES = {f.name for f in dc.fields(LayoutSpec)}
_REQUIRED = {
    f.name
    for f in dc.fields(LayoutSpec)
    if f.default == dc.MISSING and f.default_factory == dc.MISSING
}


def make(filename: str, key_names: dict[str, Any]) -> Layout:
    with ErrorMaker() as err:
        spec = LayoutSpec.make(filename, err)
        defs = _defs(spec.defs, err)
        pieces = _pieces(spec.pieces, defs, spec.spacing, key_names, err)
        size = spec.width, (len(pieces) + 1) * spec.spacing + 20

    return Layout(
        defs_=list(defs.values()),
        pieces_=pieces,
        size=size,
        spacing=spec.spacing,
        style=spec.style,
    )


def _defs(defs: dict[str, str], err: ErrorMaker) -> dict[str, ET.Element]:
    defs_ = {}
    for k, v in defs.items():
        try:
            defs_[k] = ET.fromstring(v)
        except Exception as e:
            err('Bad XML in def', e, k, v)
        else:
            defs_[k].set('id', k)
    return defs_


def _pieces(
    pieces: dict[str, dict[str, Any]],
    defs: dict[str, ET.Element],
    spacing: int,
    key_names: dict[str, Any],
    err: ErrorMaker,
) -> list[ChartPiece]:
    pieces_ = []
    x, y = 0, 0
    for name, key in pieces.items():
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
        pieces_.append(ChartPiece(parts, x, y))
        y += spacing

    return pieces_


if __name__ == '__main__':
    import sys

    print(make(sys.argv[1], {}))
