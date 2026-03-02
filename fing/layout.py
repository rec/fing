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
class Caption:
    pad: int = 30  # TODO: not used now?
    x: int = 20

    def asdict(self, y: int) -> dict[str, str]:
        return {'x': str(self.x), 'y': str(y), 'class': 'caption'}


@dc.dataclass(frozen=True)
class Layout:
    defs_: dict[str, Any]
    key_names: dict[str, Any]
    pieces_: dict[str, dict[str, Any]]
    spacing: int = 0
    styles: str = ''
    width: int = 0
    pad: int = 20  # Between individual charts
    caption_: dict[str, int] = dc.field(default_factory=dict)
    err: ErrorMaker = dc.field(default_factory=ErrorMaker)

    @staticmethod
    def make(filename: str, key_names: dict[str, Any]) -> Layout:
        with open(filename) as fp:
            data = tomlkit.load(fp)

        with ErrorMaker(reraise=True) as err:
            if not isinstance(d := data.get('layout'), dict):
                raise err.fail('No layout dictionary')
            assert isinstance(d, dict)

            for r in _REWRITES:
                if old := d.pop(r[:-1], None):
                    d[r] = old

            if bad := set(d) - _NAMES:
                err('Unknown arg', *bad)
            if missing := _REQUIRED - set(d) - {'key_names'}:
                err('Missing arg', *missing)

        layout = Layout(err=err, key_names=key_names, **d)
        layout.err.check()
        return layout

    @cached_property
    def caption(self) -> Caption:
        ## TODO: more checking or more general checking
        return Caption(**self.caption_)

    @cached_property
    def defs(self) -> list[ET.Element]:
        defs = []
        for k, v in self.defs_.items():
            try:
                defs.append(ET.fromstring(v))
            except Exception as e:
                self.err('Bad XML in def', e, k, v)
            else:
                defs[-1].set('id', k)
        return defs

    @cached_property
    def pieces(self) -> list[ChartPiece]:
        pieces = []
        x, y = 0, 0
        for name, key in self.pieces_.items():
            if not isinstance(key.get('parts'), dict):
                self.err('Missing parts section', name, key)
                continue
            if not (name.startswith('_') or name in self.key_names):
                self.err('Unknown key name', name)

            parts = {k: Part.to_parts(v) for k, v in key['parts'].items()}

            if '_off' not in parts:
                self.err('Missing parts.off section', name)
            if u := [q for p in parts.values() for q in p if q.def_ not in self.defs_]:
                self.err('Unknown def in parts', name, u)

            x = x if (x_ := key.get('x')) is None else x_
            y = y if (y_ := key.get('y')) is None else y_
            pieces.append(ChartPiece(parts, x, y))
            y += self.spacing

        return pieces

    @cached_property
    def height(self) -> int:
        return (len(self.pieces) + 1) * self.spacing + self.caption.pad


_NAMES = {f.name for f in dc.fields(Layout)}
_REQUIRED = {
    f.name
    for f in dc.fields(Layout)
    if f.default == dc.MISSING and f.default_factory == dc.MISSING
}
_REWRITES = {n for n in _NAMES if n.endswith('_')}
