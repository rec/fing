from __future__ import annotations

import dataclasses as dc
from collections.abc import Sequence
from typing import Any, NamedTuple, TypeAlias
from xml.etree import ElementTree as ET

import tomlkit

from .error_maker import ErrorMaker

Element: TypeAlias = ET.Element


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


@dc.dataclass(frozen=True)
class Layout:
    defs: Sequence[Element]
    keys: Sequence[ChartPiece]
    size: tuple[int, int]
    spacing: int
    style: str

    def render(self, fingering: Sequence[str], name: str) -> ET.ElementTree:
        w, h = self.size
        attrs = {'viewBox': f'0 0 {w} {h}', 'xmlns': 'http://www.w3.org/2000/svg'}
        svg = ET.Element('svg', attrs)
        style = ET.SubElement(svg, 'style')
        style.text = self.style

        ET.SubElement(svg, 'defs').extend(self.defs)
        ET.SubElement(svg, 'g').extend(p.render(fingering) for p in self.keys)

        h = self.size[1]
        attrs = {'x': '40', 'y': str(20 + h - self.spacing), 'font-size': '60'}
        ET.SubElement(svg, 'text', attrs).text = name

        tree = ET.ElementTree(svg)
        return tree


@dc.dataclass(frozen=True)
class LayoutSpec:
    defs: dict[str, Any]
    keys: dict[str, dict[str, Any]]
    spacing: int = 0
    style: str = ''
    width: int = 0

    @staticmethod
    def make(filename: str) -> LayoutSpec:
        with open(filename) as fp:
            data = tomlkit.load(fp)

        with ErrorMaker() as err:
            if not isinstance(d := data.get('layout'), dict):
                err.fail('No layout dictionary')
            assert isinstance(d, dict)
            names = {f.name for f in dc.fields(LayoutSpec)}
            if bad := set(d) - names:
                err('Unknown name', *bad)
            if missing := {'defs', 'keys'} - set(d):
                err('missing', *missing)
        return LayoutSpec(**d)


def make(filename: str, key_names: dict[str, Any]) -> Layout:
    spec = LayoutSpec.make(filename)
    defs, keys = {}, {}
    x, y, dy = 0, 0, spec.spacing

    with ErrorMaker() as err:
        for k, v in spec.defs.items():
            try:
                defs[k] = ET.fromstring(v)
            except Exception as e:
                err('Bad XML in def', e, k, v)
            else:
                defs[k].set('id', k)

        for name, key in spec.keys.items():
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
            keys[name] = ChartPiece(parts, x, y)
            y += dy

    return Layout(
        defs=list(defs.values()),
        keys=list(keys.values()),
        size=(spec.width, y + dy + 20),
        spacing=spec.spacing,
        style=spec.style,
    )


if __name__ == '__main__':
    import sys

    print(make(sys.argv[1], {}))
