from __future__ import annotations

import dataclasses as dc
from collections.abc import Sequence
from functools import cached_property
from typing import Any

import tomlkit

from .error_maker import ErrorMaker
from .fix_input_variables import fix_input_variables


@dc.dataclass(frozen=True)
class Key:
    short_name: str
    press: str
    description: str = ''


class Note:
    def __init__(self, s: str) -> None:
        for k, v in REPLACEMENTS.items():
            s = s.replace(k, v)
        self.name = s
        self.note = s[: 1 if s[1].isnumeric() else 2]
        self.octave = int(s[len(self.note) :])
        self.note_number = 12 * self.octave + NOTE_TO_OFFSET[self.note]

    def __str__(self) -> str:
        return self.name


@dc.dataclass(frozen=True)
class FingeringSystem:
    fingerings_: dict[str, str]
    keys_: dict[str, dict[str, str]]
    lowest_c_: dict[str, str]
    metadata: dict[str, str]
    document: tomlkit.TOMLDocument | None = None
    err: ErrorMaker = dc.field(default_factory=ErrorMaker)

    @cached_property
    def all(self) -> Sequence[Key]:
        return self._all_fingerings[0]

    @cached_property
    def fingerings(self) -> dict[Note, Sequence[Key]]:
        return self._all_fingerings[1]

    @cached_property
    def keys(self) -> dict[str, Key]:
        keys: dict[str, Key] = {}
        for k, v in self.keys_.items():
            try:
                keys[k] = Key(**v)
            except Exception as e:
                self.err('Invalid key', v, e)
        return keys

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
    def to_key(self) -> dict[str, Key]:
        return {v.short_name: v for v in self.keys.values()} | self.keys

    def check(self, check_key_order: bool = False) -> None:
        with self.err:
            shorts = (k.short_name for k in self.keys.values())
            self.err.test_dupes('Duplicate short_name', shorts)

            if check_key_order:
                self.check_key_order()
            for v in vars(self).values():
                if isinstance(v, cached_property):
                    getattr(self, v)

    def check_key_order(self) -> None:
        inv = {k: i for i, k in enumerate(self.all)}
        for fingering in self.fingerings.values():
            previous = -1
            for key in fingering:
                last = previous
                previous = inv[key]
                if last >= previous:
                    self.err('Key out of order', key.short_name)
                    break

    @cached_property
    def _all_fingerings(self) -> tuple[Sequence[Key], dict[Note, Sequence[Key]]]:
        all_: Sequence[Key] = ()
        fingerings: dict[Note, Sequence[Key]] = {}

        for k, fingering in self.fingerings_.items():
            pressed = fingering.split()
            self.err.test_dupes('Duplicate keys in fingering', pressed, k)
            if bad_notes := [i for i in pressed if i not in self.to_key]:
                self.err('Unknown note', k, bad_notes)
                continue
            keys_pressed = [self.to_key[n] for n in pressed]
            if k == 'all':
                all_ = keys_pressed
                continue
            try:
                note = Note(k)
            except Exception as e:
                self.err('Invalid note', k, e)
            else:
                fingerings[note] = keys_pressed
        return all_, fingerings


def make(filename: str, check_key_order: bool = True) -> FingeringSystem:
    with ErrorMaker() as err:
        with open(filename) as fp:
            doc: dict[str, Any] = tomlkit.load(fp)

        fix_input_variables(doc, FingeringSystem)
        names = {f.name for f in dc.fields(FingeringSystem)}
        if bad := [k for k in doc if k == 'document' or k not in names]:
            raise ValueError(f'Do not understand field{"s" * (len(bad) != 1)} {bad}')

        assert isinstance(doc, dict)
        fs = FingeringSystem(err=err, document=doc, **doc)  # ty: ignore[invalid-argument-type]
        fs.check(check_key_order)
        return fs


REPLACEMENTS = {'_': '', '-': '', ' ': '', '♭': 'b', '♯': '#'}
NOTE_TO_OFFSET = {
    'C': 0,
    'C#': 1,
    'Db': 1,
    'D': 2,
    'D#': 3,
    'Eb': 3,
    'E': 4,
    'F': 5,
    'F#': 6,
    'Gb': 6,
    'G': 7,
    'G#': 8,
    'Ab': 8,
    'A': 9,
    'A#': 10,
    'Bb': 10,
    'B': 11,
}
