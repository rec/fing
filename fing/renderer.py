from __future__ import annotations

import dataclasses as dc
from collections.abc import Sequence
from functools import cached_property
from typing import Any
from xml.etree.ElementTree import Element, SubElement

from .fingering_system import Button, Fingerings
from .layout import Inset, Layout
from .note import Note
from .sizes import SizedRegion, Sizes

NOTE_WIDTH = len('C#/D-1')
_SVG = {'xmlns': 'http://www.w3.org/2000/svg'}

DEFAULT_STYLES = {
    f'{k}_background': {'fill': 'transparent'}
    for k in SizedRegion
    if k is not SizedRegion.document
}


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
        return self.layout.inset

    @cached_property
    def rows(self) -> int:
        return self.layout.rows

    @cached_property
    def svg(self) -> Element:
        s = self.sizes.document
        svg = Element('svg', {'viewBox': f'0 0 {s.width} {s.height}'} | _SVG)
        _add(svg, 'defs').extend(self.layout.defs)

        def render_style(name: str, d: dict[str, Any]) -> str:
            parts = ' '.join(f'{k}: {v};' for k, v in d.items())
            return f'  .{name} {{ {parts} }}'

        styles = DEFAULT_STYLES | self.layout.styles
        styles = '\n  '.join(render_style(k, v) for k, v in styles.items())

        _add(svg, 'style').text = '\n  ' + styles + '\n  '
        return svg

    @cached_property
    def body(self) -> Element:
        return self._add_svg(self.svg, 'body')

    @cached_property
    def sizes(self) -> Sizes:
        return Sizes(self.layout, self.columns, self.rows)

    def __call__(self) -> Element:
        self.body.append(self.layout.title)

        fingerings = list(self.fingerings.items())
        height = self.sizes.chart.height + self.layout.fingering_pad
        for row in range(self.rows):
            y = self.layout.title_height + row * height
            chart = self._add_svg(self.body, 'chart', y=y)
            if row:
                _add(
                    self.body,
                    'rect',
                    'large-separator',
                    x=self.layout.rule_x,
                    y=y + self.layout.rule_y,
                    width=self.sizes.body.width - 2 * self.layout.rule_x,
                    height=3,
                )
            row_items = fingerings[row * self.columns : (row + 1) * self.columns]
            for column, (note, fingering) in enumerate(row_items):
                self._note_fingering(chart, column, note, fingering)

        self.body.append(self.layout.footer)
        return self.svg

    def _note_fingering(
        self, chart: Element, column: int, note: Note, fingering: Sequence[Button]
    ) -> None:
        dx, dy = self.inset.note_fingering
        x = self.sizes.note_fingering.width * column + dx + self.layout.caption_width
        note_fingering = self._add_svg(chart, 'note_fingering', x=x)
        fingering_ = self._add_svg(
            note_fingering, 'fingering', y=self.layout.note_label.height
        )
        for p in self.layout.pieces:
            fingering_.extend(p.render(fingering))

        note_label = dc.asdict(self.layout.note_label)
        text = _add(note_fingering, 'text', 'note_label', **note_label)
        text.text = str(note).center(NOTE_WIDTH)

    def _add_svg(self, parent: Element, class_: str, **kwargs: Any) -> Element:
        if size := getattr(self.sizes, class_, None):
            x, y = getattr(self.inset, class_)
            if class_ == 'chart':
                y += self.layout.title_height
            kwargs = {'x': x, 'y': y} | size.asdict() | kwargs

        r = _add(parent, 'svg', class_, **kwargs)
        _add(r, 'rect', class_ + '_background', width='100%', height='100%')
        return r


def _add(parent: Element, tag: str, *classes: str, **kwargs: Any) -> Element:
    if classes:
        kwargs = {'class': ' '.join(classes)} | kwargs
    return SubElement(parent, tag, {k: str(v) for k, v in kwargs.items()})
