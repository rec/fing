from __future__ import annotations

from collections.abc import Sequence
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element

from .fingering_system import FingeringSystem, Key
from .layout import Layout


def render(layout: Layout, fingering: Sequence[Key], note: str) -> Element:
    svg = _svg(layout, layout.width, layout.height)
    return _add(svg, layout, fingering, note)


def render_all(fs: FingeringSystem, layout: Layout) -> Element:
    N = len(fs.fingerings)
    rows = 2  # :-)
    columns = N // rows
    columns += columns * rows < N

    dx = layout.width + layout.pad_x
    dy = layout.height + layout.pad_y

    def scale(c: int, r: int) -> tuple[int, int]:
        return c * dx + layout.pad_x, r * dy + layout.pad_y

    width, height = scale(columns, rows)
    svg = _svg(layout, width, height)

    for i, (note, fingering) in enumerate(fs.fingerings.items()):
        row, column = divmod(i, columns)
        x, y = scale(column, row)
        if row and not column:
            attr = {
                'x': str(x),
                'y': str(y - layout.pad_y // 2),
                'width': str(width),
                'height': '3',
            }
            ET.SubElement(svg, 'rect', attr)
        attrs = {'transform': f'translate({x},{y})'}
        g = ET.SubElement(svg, 'g', attrs)
        _add(g, layout, fingering, str(note))

    return svg


def _add(e: Element, layout: Layout, fingering: Sequence[Key], note: str) -> Element:
    for p in layout.pieces:
        e.extend(p.render(fingering))

    y = layout.height
    ET.SubElement(e, 'text', layout.caption.asdict(y)).text = note.center(5)
    return e


def _fix_styles(s: str) -> str:
    return '\n    '.join(('', *s.strip().split('\n'))) + '\n  '


def _svg(layout: Layout, width: int, height: int) -> ET.Element:
    attrs = {'viewBox': f'0 0 {width} {height}', 'xmlns': 'http://www.w3.org/2000/svg'}
    svg = ET.Element('svg', attrs)
    ET.SubElement(svg, 'defs').extend(layout.defs)
    ET.SubElement(svg, 'style').text = _fix_styles(layout.styles)
    return svg
