from __future__ import annotations

from collections.abc import Sequence
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element

from .fingering_system import Button, FingeringSystem
from .layout import Layout


def render(layout: Layout, fingering: Sequence[Button], note: str) -> Element:
    svg = _svg(layout, layout.width, layout.height)
    _render_one_fingering(svg, layout, fingering, note)
    return svg


def render_all(fs: FingeringSystem, layout: Layout) -> Element:
    N = len(fs.fingerings)
    columns = N // layout.rows
    columns += columns * layout.rows < N

    start_x, start_y = layout.pad_x, layout.pad_y
    dx = layout.width + layout.pad_x
    dy = layout.height + layout.pad_y

    def scale(c: int, r: int) -> tuple[int, int]:
        return c * dx + start_x, r * dy + start_y

    width, height = scale(columns, layout.rows)
    svg = _svg(layout, width + layout.buttons_inset, height)

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
        sub = ET.SubElement(svg, 'svg', {'x': str(x), 'y': str(y)})
        _render_one_fingering(sub, layout, fingering, str(note))

    return svg


def _render_one_fingering(
    e: Element, layout: Layout, fingering: Sequence[Button], note: str
) -> None:
    pieces = ET.SubElement(e, 'svg', {'x': str(layout.buttons_inset)})
    for piece in layout.pieces:
        pieces.extend(piece.render(fingering))

    text = ET.SubElement(e, 'text', layout.caption.asdict())
    text.text = note.center(6)
    caption_size = layout.spacing
    if layout.caption.above:
        text.set('y', str(layout.spacing - layout.caption.pad))
        pieces.set('y', str(caption_size))
    else:
        text.set('y', str(layout.height))


def _fix_styles(s: str) -> str:
    return '\n    '.join(('', *s.strip().split('\n'))) + '\n  '


def _svg(layout: Layout, width: int, height: int) -> ET.Element:
    attrs = {'viewBox': f'0 0 {width} {height}', 'xmlns': 'http://www.w3.org/2000/svg'}
    svg = ET.Element('svg', attrs)
    ET.SubElement(svg, 'defs').extend(layout.defs)
    ET.SubElement(svg, 'style').text = _fix_styles(layout.styles)
    return svg
