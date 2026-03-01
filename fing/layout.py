from __future__ import annotations

import dataclasses as dc
from functools import cached_property
from typing import Any, TypeAlias
from xml.etree import ElementTree as ET

import tomlkit

from fing.chart_piece import ChartPiece, Part

from .error_maker import ErrorMaker

Element: TypeAlias = ET.Element


@dc.dataclass(frozen=True)
class Layout:
    defs: dict[str, Any]
    key_names: dict[str, Any]
    pieces: dict[str, dict[str, Any]]
    spacing: int = 0
    style: str = ''
    width: int = 0
    err: ErrorMaker = dc.field(default_factory=ErrorMaker)

    @staticmethod
    def make(filename: str, key_names: dict[str, Any]) -> Layout:
        with open(filename) as fp:
            data = tomlkit.load(fp)

        with ErrorMaker(reraise=True) as err:
            if not isinstance(d := data.get('layout'), dict):
                raise err.fail('No layout dictionary')

            assert isinstance(d, dict)
            if bad := set(d) - _NAMES:
                err('Unknown arg', *bad)
            if missing := _REQUIRED - set(d) - {'key_names'}:
                err('Missing arg', *missing)

        return Layout(err=err, key_names=key_names, **d)

    @cached_property
    def defs_(self) -> list[ET.Element]:
        defs = []
        for k, v in self.defs.items():
            try:
                defs.append(ET.fromstring(v))
            except Exception as e:
                self.err('Bad XML in def', e, k, v)
            else:
                defs[-1].set('id', k)
        return defs

    @cached_property
    def pieces_(self) -> list[ChartPiece]:
        pieces = []
        x, y = 0, 0
        for name, key in self.pieces.items():
            if not isinstance(key.get('parts'), dict):
                self.err('Missing parts section', name, key)
                continue
            if not (name.startswith('_') or name in self.key_names):
                self.err('Unknown key name', name)

            parts = {k: Part.to_parts(v) for k, v in key['parts'].items()}

            if '_off' not in parts:
                self.err('Missing parts.off section', name)
            if u := [p for pp in parts.values() for p in pp if p.def_ not in self.defs]:
                self.err('Unknown def in parts', name, u)

            x = x if (x_ := key.get('x')) is None else x_
            y = y if (y_ := key.get('y')) is None else y_
            pieces.append(ChartPiece(parts, x, y))
            y += self.spacing

        return pieces

    @cached_property
    def size(self) -> tuple[int, int]:
        return self.width, (len(self.pieces) + 1) * self.spacing + 20


_NAMES = {f.name for f in dc.fields(Layout)}
_REQUIRED = {
    f.name
    for f in dc.fields(Layout)
    if f.default == dc.MISSING and f.default_factory == dc.MISSING
}
