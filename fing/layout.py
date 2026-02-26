from __future__ import annotations

import dataclasses as dc
from collections.abc import Sequence
from typing import Any, TypeAlias
from xml.etree import ElementTree as ET

import tomlkit

from .error_maker import ErrorMaker

Element: TypeAlias = ET.Element


@dc.dataclass(frozen=True)
class ChartPiece:
    image: dict[str, str]
    x: int
    y: int

    def render(self, fingering: Sequence[str]) -> Element:
        im = next((v for p in fingering if (v := self.image.get(p))), self.image['off'])
        return Element('use', {'href': f'#{im}', 'x': str(self.x), 'y': str(self.y)})


@dc.dataclass(frozen=True)
class Layout:
    defs: Sequence[Element]
    pieces: Sequence[ChartPiece]
    size: tuple[int, int] = (100, 800)
    style: str = ''

    def render(self, fingering: Sequence[str], name: str) -> ET.ElementTree:
        w, h = self.size
        svg = ET.Element(
            'svg', {'viewBox': f'0 0 {w} {h}', 'xmlns': 'http://www.w3.org/2000/svg'}
        )
        assert self.style
        if self.style:
            svg.append(ET.fromstring(self.style))

        defs = ET.SubElement(svg, 'defs')
        defs.extend(self.defs)

        pieces = ET.SubElement(svg, 'g')
        pieces.extend(p.render(fingering) for p in self.pieces)

        tree = ET.ElementTree(svg)
        return tree


@dc.dataclass(frozen=True)
class LayoutSpec:
    defs: dict[str, Any]
    pieces: dict[str, dict[str, Any]]
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
            if missing := {'defs', 'pieces'} - set(d):
                err('missing', *missing)
        return LayoutSpec(**d)


def make(filename: str, key_names: dict[str, Any]) -> Layout:
    with ErrorMaker() as err:
        spec = LayoutSpec.make(filename)
        defs = {}
        for k, v in spec.defs.items():
            try:
                defs[k] = ET.fromstring(v)
            except Exception:
                err('Bad def', f'{k}: {v}')
                continue
            defs[k].set('id', k)

        pieces = {}
        x, y, dy = 0, 0, spec.spacing

        for name, piece in spec.pieces.items():
            try:
                image = piece['image']
            except KeyError:
                err('No image section', name, piece)
                continue
            if not isinstance(image, dict):
                err('Bad image section', name, piece)
                continue
            if not (off := image.get('off')):
                err('Missing image.off section', name, off)
            if unknown := [v for v in image.values() if v not in defs]:
                err('Unknown def in image', name, unknown)
            if not (name.startswith('_') or name in key_names):
                err('Unknown key name', name)
            x = x if (x_ := piece.get('x')) is None else x_
            y = y if (y_ := piece.get('y')) is None else y_
            pieces[name] = ChartPiece(image, x, y)
            y += dy

        return Layout(
            list(defs.values()), list(pieces.values()), (spec.width, y), spec.style
        )


if __name__ == '__main__':
    import sys

    print(make(sys.argv[1], {}))
