from __future__ import annotations

from collections.abc import Sequence
from xml.etree import ElementTree as ET

from .fingering_system import FingeringSystem
from .layout import Layout


def render(layout: Layout, fingering: Sequence[str], name: str) -> ET.Element:
    svg = _svg(layout)
    for p in layout.pieces_:
        svg.extend(p.render(fingering))

    y = 20 + layout.size[1] - layout.spacing
    ET.SubElement(svg, 'text', {'x': '40', 'y': str(y), 'font-size': '60'}).text = name
    return svg


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
    ET.SubElement(svg, 'style').text = _fix_style(layout.style)
    return svg


def _fix_style(s: str) -> str:
    return '\n    '.join(('', *s.strip().split('\n'))) + '\n  '
