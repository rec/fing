from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from xml.etree.ElementTree import Element, SubElement

from .fingering_system import Button, FingeringSystem
from .layout import Layout


def render_all(layout: Layout, fs: FingeringSystem) -> Element:
    N = len(fs.fingerings)
    columns = N // layout.rows
    columns += N > (columns * layout.rows)

    width, height = layout.scale(columns, layout.rows)
    svg = _svg(layout, width + layout.buttons_inset, height)

    for i, (note, fingering) in enumerate(fs.fingerings.items()):
        row, column = divmod(i, columns)
        x, y = layout.scale(column, row)
        if row and not column:
            _add_element(
                svg, 'rect', x=x, y=y - layout.pad_y // 2, width=width, height=3
            )
        sub = _add_element(svg, 'svg', x=x, y=y)
        _add_caption(layout, sub, str(note), _add_pieces(layout, sub, fingering))

    return svg


def _add_element(parent: Element, tag: str, **kwargs: Any) -> Element:
    return SubElement(parent, tag, {k: str(v) for k, v in kwargs.items()})


def _add_pieces(layout: Layout, e: Element, fingering: Sequence[Button]) -> Element:
    pieces = _add_element(e, 'svg', x=str(layout.buttons_inset))
    for piece in layout.pieces:
        pieces.extend(piece.render(fingering))
    return pieces


def _add_caption(layout: Layout, e: Element, note: str, pieces: Element) -> None:
    text = _add_element(e, 'text', **layout.caption.asdict())
    text.text = note.center(6)
    if layout.caption.above:
        text.set('y', str(layout.spacing - layout.caption.pad))
        pieces.set('y', str(layout.spacing))
    else:
        text.set('y', str(layout.height))


def _svg(layout: Layout, width: int, height: int) -> Element:
    attrs = {'viewBox': f'0 0 {width} {height}', 'xmlns': 'http://www.w3.org/2000/svg'}
    svg = Element('svg', attrs)
    SubElement(svg, 'defs').extend(layout.defs)
    styles = '\n    '.join(('', *layout.styles.strip().split('\n'))) + '\n  '
    SubElement(svg, 'style').text = styles
    return svg
