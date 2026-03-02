from __future__ import annotations

from collections.abc import Sequence
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element

from .fingering_system import FingeringSystem
from .layout import Layout


def render(layout: Layout, fingering: Sequence[str], note: str) -> Element:
    svg = _svg(layout, layout.width, layout.height)
    return _add(svg, layout, fingering, note)


def render_all(fs: FingeringSystem, layout: Layout) -> Element:
    N = len(fs.fingerings)
    rows = 2  # :-)
    columns = N // rows
    columns += columns * rows < N

    dx = layout.width + layout.pad
    dy = layout.height + layout.pad

    svg = _svg(layout, dx * columns, dy * rows)
    elements = []

    for i, (note, fingering) in enumerate(fs.fingerings.items()):
        fi = [f.short_name for f in fingering]
        row, column = divmod(i, columns)
        attrs = {'transform': f'translate({column * dx},{row * dy})'}
        g = ET.SubElement(svg, 'g', attrs)
        elements.append(_add(g, layout, fi, str(note)))
    return svg


def _add(e: Element, layout: Layout, fingering: Sequence[str], note: str) -> Element:
    for p in layout.pieces:
        e.extend(p.render(fingering))

    y = layout.height - layout.spacing
    ET.SubElement(e, 'text', layout.caption.asdict(y)).text = note
    return e


def _fix_styles(s: str) -> str:
    return '\n    '.join(('', *s.strip().split('\n'))) + '\n  '


def _svg(layout: Layout, width: int, height: int) -> ET.Element:
    attrs = {'viewBox': f'0 0 {width} {height}', 'xmlns': 'http://www.w3.org/2000/svg'}
    svg = ET.Element('svg', attrs)
    ET.SubElement(svg, 'defs').extend(layout.defs)
    ET.SubElement(svg, 'style').text = _fix_styles(layout.styles)
    return svg
