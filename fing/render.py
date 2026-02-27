from __future__ import annotations

from collections.abc import Sequence
from xml.etree import ElementTree as ET

from .fingering_system import FingeringSystem
from .layout import Layout


def render(layout: Layout, fingering: Sequence[str], name: str) -> ET.Element:
    w, h = layout.size
    attrs = {'viewBox': f'0 0 {w} {h}', 'xmlns': 'http://www.w3.org/2000/svg'}
    svg = ET.Element('svg', attrs)
    style = ET.SubElement(svg, 'style')
    style.text = layout.style

    ET.SubElement(svg, 'defs').extend(layout.defs)
    ET.SubElement(svg, 'g').extend(p.render(fingering) for p in layout.pieces)

    h = layout.size[1]
    attrs = {'x': '40', 'y': str(20 + h - layout.spacing), 'font-size': '60'}
    ET.SubElement(svg, 'text', attrs).text = name
    return svg


def render_all(fs: FingeringSystem, layout: Layout) -> None:
    w, h = layout.size
    attrs = {'viewBox': f'0 0 {w} {h}', 'xmlns': 'http://www.w3.org/2000/svg'}
    svg = ET.Element('svg', attrs)
    style = ET.SubElement(svg, 'style')
    style.text = layout.style

    ET.SubElement(svg, 'defs').extend(layout.defs)
    g = ET.SubElement(svg, 'g')
    note_fingerings = [(n, f) for n, ff in fs.fingerings.items() for f in ff]

    N = len(note_fingerings)
    rows = 3  # :-)
    columns = N // rows
    columns += columns * rows < N

    w, h = layout.size

    assert w and h and g
