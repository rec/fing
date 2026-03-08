from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from xml.etree import ElementTree as ET

from .fingering_system import Button, FingeringSystem
from .layout import Layout


def render(layout: Layout, fingering: Sequence[Button], note: str) -> ET.Element:
    svg = _svg(layout, layout.width, layout.height)
    _render_one_fingering(svg, layout, fingering, note)
    return svg


def render_all(fs: FingeringSystem, layout: Layout) -> ET.Element:
    N = len(fs.fingerings)
    columns = N // layout.rows
    columns += N > (columns * layout.rows)

    width, height = layout.scale(columns, layout.rows)
    svg = _svg(layout, width + layout.buttons_inset, height)

    for i, (note, fingering) in enumerate(fs.fingerings.items()):
        row, column = divmod(i, columns)
        x, y = layout.scale(column, row)
        if row and not column:
            _add_rule(layout, svg, width, x, y)
        sub = ET.SubElement(svg, 'svg', _to_str_dict(x=x, y=y))
        _render_one_fingering(sub, layout, fingering, str(note))

    return svg


def _add_rule(layout: Layout, svg: ET.Element, width: int, x: int, y: int) -> None:
    attrs = _to_str_dict(x=x, y=y - layout.pad_y // 2, width=width, height=3)
    ET.SubElement(svg, 'rect', attrs)


def _render_one_fingering(
    e: ET.Element, layout: Layout, fingering: Sequence[Button], note: str
) -> None:
    _add_caption(e, layout, note, _add_pieces(e, fingering, layout))


def _add_pieces(
    e: ET.Element, fingering: Sequence[Button], layout: Layout
) -> ET.Element:
    pieces = ET.SubElement(e, 'svg', _to_str_dict(x=str(layout.buttons_inset)))
    for piece in layout.pieces:
        pieces.extend(piece.render(fingering))
    return pieces


def _add_caption(e: ET.Element, layout: Layout, note: str, pieces: ET.Element) -> None:
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


def _to_str_dict(**kwargs: Any) -> dict[str, str]:
    return {k: str(v) for k, v in kwargs.items()}
