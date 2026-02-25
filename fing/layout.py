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

    def render(self, fingering: Sequence[str]) -> ET.ElementTree:
        tree = ET.ElementTree()
        root = tree.getroot()
        assert root is not None

        defs = ET.SubElement(root, 'defs')
        defs.extend(self.defs)

        pieces = ET.SubElement(root, 'g')
        pieces.extend(p.render(fingering) for p in self.pieces)
        return tree


@dc.dataclass(frozen=True)
class LayoutSpec:
    defs: dict[str, Any]
    pieces: dict[str, dict[str, Any]]
    size: Sequence[int] = (100, 800)
    spacing: int | list[int] = 0

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
        x, y = 0, 0
        if isinstance(spec.spacing, int):
            dx, dy = 0, spec.spacing
        else:
            dx, dy = spec.spacing

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
            x += dx
            y += dy

        if len(spec.size) != 2:
            err('Bad spec size', spec.size)

        return Layout(list(defs.values()), list(pieces.values()), tuple(spec.size)[:2])


if __name__ == '__main__':
    import sys

    print(make(sys.argv[1], {}))
