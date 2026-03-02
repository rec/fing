from __future__ import annotations

import dataclasses as dc
from functools import cached_property
from typing import Any, TypeAlias
from xml.etree import ElementTree as ET

import tomlkit

from fing.chart_piece import ChartPiece, Part

from .error_maker import ErrorMaker
from .fingering_system import Key
from .fix_input_variables import fix_input_variables

Element: TypeAlias = ET.Element


@dc.dataclass(frozen=True)
class Caption:
    pad: int = 20
    x: int = 50
    font_size: int = 40
    above: bool = False

    def asdict(self, y: int) -> dict[str, str]:
        # TODO: why does this work in a stylesheet in emacs, but not for Chrome and FF?
        return {
            'x': str(self.x),
            'y': str(y),
            'class': 'caption',
            'font-size': str(self.font_size),
            'font-family': 'monospace',
            'text-anchor': 'middle',
            'dominant-baseline': 'middle',
        }


@dc.dataclass(frozen=True)
class Layout:
    defs_: dict[str, Any]
    pieces_: dict[str, dict[str, Any]]
    to_key: dict[str, Key]
    spacing: int = 0
    styles: str = ''
    width: int = 0  # TODO: do we use this?
    pad_x: int = 100
    pad_y: int = 180
    caption_: dict[str, int | bool] = dc.field(default_factory=dict)
    err: ErrorMaker = dc.field(default_factory=ErrorMaker)

    @staticmethod
    def make(filename: str, to_key: dict[str, Any]) -> Layout:
        with open(filename) as fp:
            data = tomlkit.load(fp)

        with ErrorMaker(reraise=True) as err:
            if not isinstance(d := data.get('layout'), dict):
                raise err.fail('No layout dictionary')
            assert isinstance(d, dict)

            fix_input_variables(d, Layout)
            if bad := set(d) - _NAMES:
                err('Unknown arg', *bad)
            if missing := _REQUIRED - set(d) - {'to_key'}:
                err('Missing arg', *missing)

        layout = Layout(err=err, to_key=to_key, **d)
        layout.err.check()
        return layout

    @cached_property
    def caption(self) -> Caption:
        ## TODO: more checking or more general checking
        return Caption(**self.caption_)  # ty: ignore[invalid-argument-type]

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
        return self._pieces_and_height[0]

    @cached_property
    def height(self) -> int:
        return self._pieces_and_height[1]

    @cached_property
    def _pieces_and_height(self) -> tuple[list[ChartPiece], int]:
        pieces = []
        x, y = 0, 0
        for name, key in self.pieces_.items():
            if not isinstance(key.get('parts'), dict):
                self.err('Missing parts section', name, key)
                continue
            if not (name.startswith('_') or name in self.to_key):
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

        return pieces, y + self.caption.pad


_NAMES = {f.name for f in dc.fields(Layout)}
_REQUIRED = {
    f.name
    for f in dc.fields(Layout)
    if f.default == dc.MISSING and f.default_factory == dc.MISSING
}
