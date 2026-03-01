from __future__ import annotations

from collections.abc import Sequence
from xml.etree import ElementTree as ET

from .fingering_system import FingeringSystem
from .layout import Layout


def render(layout: Layout, fingering: Sequence[str], note: str) -> ET.Element:
    svg = _svg(layout)
    _add(svg, layout, fingering, note)
    return svg


def _add(e: ET.Element, layout: Layout, fingering: Sequence[str], note: str) -> None:
    for p in layout.pieces_:
        e.extend(p.render(fingering))

    y = layout.size[1] - layout.spacing
    ET.SubElement(e, 'text', layout.caption_.asdict(y)).text = note


def render_all(fs: FingeringSystem, layout: Layout) -> None:
    svg = _svg(layout)
    g = ET.SubElement(svg, 'g')
    note_fingerings = [(n, f) for n, ff in fs.fingerings.items() for f in ff]

    N = len(note_fingerings)
    rows = 3  # :-)
    columns = N // rows
    columns += columns * rows < N

    w, h = layout.size

    assert w and h and g


def _svg(layout: Layout) -> ET.Element:
    w, h = layout.size
    attrs = {'viewBox': f'0 0 {w} {h}', 'xmlns': 'http://www.w3.org/2000/svg'}
    svg = ET.Element('svg', attrs)
    ET.SubElement(svg, 'defs').extend(layout.defs_)
    ET.SubElement(svg, 'style').text = _fix_styles(layout.styles)
    return svg


def _fix_styles(s: str) -> str:
    return '\n    '.join(('', *s.strip().split('\n'))) + '\n  '
