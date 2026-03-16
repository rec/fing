from __future__ import annotations

import dataclasses as dc
from functools import cached_property
from typing import Any, NamedTuple, TypeAlias
from xml.etree.ElementTree import Element, fromstring

import tomlkit

from fing.chart_piece import ChartPiece, Part

from .error_maker import ErrorMaker
from .fingering_system import Button
from .fix_input_variables import fix_input_variables

Dims: TypeAlias = int | tuple[int, int]


@dc.dataclass(frozen=True)
class Caption:
    height: int = 70
    x: int = 80
    y: int = 30


class XY(NamedTuple):
    x: int
    y: int


@dc.dataclass(frozen=True)
class Inset:
    page: XY = XY(30, 30)
    body: XY = XY(30, 30)
    charts: XY = XY(30, 30)
    note_fingering: XY = XY(30, 30)
    fingering: XY = XY(30, 30)


@dc.dataclass(frozen=True)
class Layout:
    defs_: dict[str, Any]
    pieces_: dict[str, dict[str, Any]]
    to_button: dict[str, Button]
    styles: str = ''
    caption_: dict[str, int | bool] = dc.field(default_factory=dict)
    caption_above: bool = True
    title_: str = ''
    err: ErrorMaker = dc.field(default_factory=ErrorMaker)

    rows: int = 2

    button_height: int = 120
    width: int = 135
    title_height: int = 150
    fingering_pad: int = 150

    inset: Inset = Inset()

    @cached_property
    def caption(self) -> Caption:
        ## TODO: more checking or more general checking
        return Caption(**self.caption_)

    @cached_property
    def defs(self) -> list[Element]:
        defs = []
        for k, v in self.defs_.items():
            try:
                defs.append(fromstring(v))
            except Exception as e:
                self.err('Bad XML in def', e, k, v)
            else:
                defs[-1].set('id', k)
        return defs

    @cached_property
    def pieces(self) -> list[ChartPiece]:
        pieces = []
        x, y = 1, 1
        for name, button in self.pieces_.items():
            if not isinstance(button.get('parts'), dict):
                self.err('Missing parts section', name, button)
                continue
            if not (name.startswith('_') or name in self.to_button):
                self.err('Unknown button name', name)

            parts = {k: Part.to_parts(v) for k, v in button['parts'].items()}

            if '_off' not in parts:
                self.err('Missing parts.off section', name)
            if u := [q for p in parts.values() for q in p if q.def_ not in self.defs_]:
                self.err('Unknown def in parts', name, u)

            x = button.get('x', x)
            y = button.get('y', y)
            height = button.get('height', self.button_height)
            pieces.append(ChartPiece(parts, x, y, height))
            y += height
        return pieces

    @cached_property
    def height(self) -> int:
        return sum(p.height for p in self.pieces) + self.caption.height

    @cached_property
    def title(self) -> Element:
        return fromstring(self.title_)

    @staticmethod
    def make(data: tomlkit.TOMLDocument, to_button: dict[str, Any]) -> Layout:
        with ErrorMaker(reraise=True) as err:
            if not isinstance(d := data.get('layout'), dict):
                raise err.fail('No layout dictionary')
            assert isinstance(d, dict)

            fix_input_variables(d, Layout)
            if bad := set(d) - _NAMES:
                err('Unknown arg', *bad)
            if missing := _REQUIRED - set(d) - {'to_button'}:
                err('Missing arg', *missing)

        layout = Layout(err=err, to_button=to_button, **d)
        layout.err.check()
        return layout


_NAMES = {f.name for f in dc.fields(Layout)}
_REQUIRED = {
    f.name
    for f in dc.fields(Layout)
    if f.default == dc.MISSING and f.default_factory == dc.MISSING
}
