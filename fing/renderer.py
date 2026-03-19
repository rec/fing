from __future__ import annotations

import dataclasses as dc
from collections.abc import Sequence
from functools import cached_property
from typing import Any
from xml.etree.ElementTree import Element, SubElement

from .fingering_system import Button, Fingerings
from .layout import Inset, Layout
from .note import Note
from .sizes import Sizes

NOTE_WIDTH = len('C#/D-1')
_SVG = {'xmlns': 'http://www.w3.org/2000/svg'}


@dc.dataclass(frozen=True)
class Renderer:
    layout: Layout
    fingerings: Fingerings

    @cached_property
    def columns(self) -> int:
        N = len(self.fingerings)
        columns = N // self.rows
        return columns + (N > columns * self.rows)

    @cached_property
    def inset(self) -> Inset:
        return self.inset

    @cached_property
    def rows(self) -> int:
        return self.layout.rows

    @cached_property
    def svg(self) -> Element:
        s = self.sizes.document
        svg = Element('svg', {'viewBox': f'0 0 {s.width} {s.height}'} | _SVG)
        self._add(svg, 'defs').extend(self.layout.defs)

        def render_style(name: str, d: dict[str, Any]) -> str:
            parts = ' '.join(f'{k}: {v};' for k, v in d.items())
            return f'  .{name} {{ {parts} }}'

        styles = '\n  '.join(render_style(k, v) for k, v in self.layout.styles.items())
        self._add(svg, 'style').text = '\n  ' + styles + '\n  '
        return svg

    @cached_property
    def body(self) -> Element:
        return self._add_svg(self.svg, 'body')

    @cached_property
    def page(self) -> Element:
        return self._add_svg(self.body, 'page')

    @cached_property
    def charts(self) -> Element:
        return self._add_svg(self.page, 'charts')

    @cached_property
    def sizes(self) -> Sizes:
        return Sizes(self.layout, self.columns, self.rows)

    def __call__(self) -> Element:
        self.page.append(self.layout.title)

        for i, (note, fingering) in enumerate(self.fingerings.items()):
            self._note_fingering(i, note, fingering)

        self._draw_rules()
        return self.svg

    def _draw_rules(self):
        if True:
            return
        for row in range(1, self.rows):
            y = row * (self.layout.height + self.layout.fingering_pad)
            width = self.sizes.page.width
            y -= 80  # HACK!
            width -= 950  # HACK!
            self._add(
                self.charts, 'rect', 'large-separator', y=y, width=width, height=3
            )

    def _note_fingering(self, i: int, note: Note, fingering: Sequence[Button]) -> None:
        row, column = divmod(i, self.columns)
        x = self.sizes.note_fingering.width * column
        y = (self.layout.height + self.layout.fingering_pad) * row
        note_fingering = self._add_svg(self.charts, 'note-fingering', x=x, y=y)
        pieces = self._add_svg(
            note_fingering, 'fingering', y=self.layout.caption.height
        )
        for piece in self.layout.pieces:
            pieces.extend(piece.render(fingering))

        caption = dc.asdict(self.layout.caption)
        text = self._add(note_fingering, 'text', 'caption', **caption)
        text.text = str(note).center(NOTE_WIDTH)

    def _add(self, parent: Element, tag: str, *classes: str, **kwargs: Any) -> Element:
        if classes:
            kwargs = {'class': ' '.join(classes)} | kwargs
        return SubElement(parent, tag, {k: str(v) for k, v in kwargs.items()})

    def _add_svg(self, parent: Element, class_: str, **kwargs: Any) -> Element:
        # TODO: get rid of kwargs - get all spacing through Insets
        if size := getattr(self.sizes, class_, None):
            kwargs |= dc.asdict(size)

        r = self._add(parent, 'svg', class_, **kwargs)
        if (style := class_ + '_background') in self.layout.styles:
            ka = {'class': style}
        else:
            ka = {'fill': 'transparent'}
        SubElement(r, 'rect', ka | {'width': '100%', 'height': '100%'})
        return r
