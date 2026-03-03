from __future__ import annotations

import dataclasses as dc
from collections.abc import Sequence
from functools import cached_property
from typing import Any

import tomlkit

from .error_maker import ErrorMaker
from .fix_input_variables import fix_input_variables
from .note import Note


@dc.dataclass(frozen=True)
class Button:
    name: str
    short_name: str
    press: str
    description: str = ''


@dc.dataclass(frozen=True)
class FingeringSystem:
    fingerings_: dict[str, str]
    buttons_: dict[str, dict[str, str]]
    lowest_c_: dict[str, str]
    metadata: dict[str, str]
    document: tomlkit.TOMLDocument | None = None
    err: ErrorMaker = dc.field(default_factory=ErrorMaker)

    @cached_property
    def all(self) -> Sequence[Button]:
        return self._all_fingerings[0]

    @cached_property
    def fingerings(self) -> dict[Note, Sequence[Button]]:
        return self._all_fingerings[1]

    @cached_property
    def buttons(self) -> dict[str, Button]:
        buttons: dict[str, Button] = {}
        for k, v in self.buttons_.items():
            try:
                buttons[k] = Button(name=k, **v)
            except Exception as e:
                self.err('Invalid button', v, e)
        return buttons

    @cached_property
    def lowest_c(self) -> dict[str, Note]:
        lowest_c: dict[str, Note] = {}
        for k, v in self.lowest_c_.items():
            try:
                note = Note(v)
            except Exception:
                self.err('Invalid note', k)
                continue
            lowest_c[k] = note
        return lowest_c

    @cached_property
    def to_button(self) -> dict[str, Button]:
        return {v.short_name: v for v in self.buttons.values()} | self.buttons

    def check(self, check_button_order: bool = False) -> None:
        with self.err:
            shorts = (k.short_name for k in self.buttons.values())
            self.err.test_dupes('Duplicate short_name', shorts)

            if check_button_order:
                self.test_button_order()
            for v in vars(self).values():
                if isinstance(v, cached_property):
                    getattr(self, v)

    def test_button_order(self) -> None:
        inv = {k: i for i, k in enumerate(self.all)}
        for fingering in self.fingerings.values():
            previous = -1
            for button in fingering:
                last = previous
                previous = inv[button]
                if last >= previous:
                    self.err('Button out of order', button.short_name)
                    break

    @cached_property
    def _all_fingerings(self) -> tuple[Sequence[Button], dict[Note, Sequence[Button]]]:
        all_: Sequence[Button] = ()
        fingerings: dict[Note, Sequence[Button]] = {}

        for k, fingering in self.fingerings_.items():
            pressed = fingering.split()
            self.err.test_dupes('Duplicate buttons in fingering', pressed, k)
            if bad_notes := [i for i in pressed if i not in self.to_button]:
                self.err('Unknown note', k, bad_notes)
                continue
            buttons_pressed = [self.to_button[n] for n in pressed]
            if k == 'all':
                all_ = buttons_pressed
                continue
            try:
                note = Note(k)
            except Exception as e:
                self.err('Invalid note', k, e)
            else:
                fingerings[note] = buttons_pressed
        return all_, fingerings


def make(filename: str, check_button_order: bool = True) -> FingeringSystem:
    with ErrorMaker() as err:
        with open(filename) as fp:
            doc: dict[str, Any] = tomlkit.load(fp)

        fix_input_variables(doc, FingeringSystem)
        names = {f.name for f in dc.fields(FingeringSystem)}
        if bad := [k for k in doc if k == 'document' or k not in names]:
            raise ValueError(f'Do not understand field{"s" * (len(bad) != 1)} {bad}')

        assert isinstance(doc, dict)
        fs = FingeringSystem(err=err, document=doc, **doc)  # ty: ignore[invalid-argument-type]
        fs.check(check_button_order)
        return fs
