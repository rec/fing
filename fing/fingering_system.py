from __future__ import annotations

import dataclasses as dc
from collections.abc import Sequence
from typing import Any

import tomlkit

from .error_maker import ErrorMaker


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
    # All the keys in order
    all: Sequence[Key]
    fingerings: dict[Note, Sequence[Key]]
    keys: dict[str, Key]
    lowest_c: dict[str, Note]
    to_key: dict[str, Key]
    metadata: dict[str, str]
    document: tomlkit.TOMLDocument | None = None


@dc.dataclass(frozen=True)
class FingeringSpec:
    fingerings: dict[str, str]
    keys: dict[str, dict[str, str]]
    lowest_c: dict[str, str]
    metadata: dict[str, str]
    document: tomlkit.TOMLDocument | None = None

    @staticmethod
    def make(filename: str) -> FingeringSpec:
        with open(filename) as fp:
            doc: dict[str, Any] = tomlkit.load(fp)

        names = {f.name for f in dc.fields(FingeringSpec)}
        if bad := [k for k in doc if k == 'document' or k not in names]:
            raise ValueError(f'Do not understand field{"s" * (len(bad) != 1)} {bad}')

        assert isinstance(doc, dict) and all(isinstance(i, str) for i in doc), doc
        return FingeringSpec(document=doc, **doc)  # ty: ignore[invalid-argument-type]


def make(filename: str, check_key_order: bool = True) -> FingeringSystem:
    with ErrorMaker() as err:
        spec = FingeringSpec.make(filename)

        keys: dict[str, Key] = {}
        for k, v in spec.keys.items():
            try:
                keys[k] = Key(**v)
            except Exception as e:
                err('Invalid key', v, e)
        err.test_dupes('Duplicate short_name', (k.short_name for k in keys.values()))

        all_: Sequence[Key] = ()
        to_key = {v.short_name: v for v in keys.values()} | keys

        fingerings: dict[Note, Sequence[Key]] = {}
        for k, fingering in spec.fingerings.items():
            pressed = fingering.split()
            err.test_dupes('Duplicate keys in fingering', pressed, k)
            if bad_notes := [i for i in pressed if i not in to_key]:
                err('Unknown note', k, bad_notes)
                continue
            keys_pressed = [to_key[n] for n in pressed]
            if k == 'all':
                all_ = keys_pressed
                continue
            try:
                note = Note(k)
            except Exception as e:
                err('Invalid note', k, e)
            else:
                fingerings[note] = keys_pressed

        if check_key_order:
            inv = {k: i for i, k in enumerate(all_)}
            for fingering in fingerings.values():
                previous = -1
                for ii, key in enumerate(fingering):
                    last = previous
                    previous = inv[key]
                    if last >= previous:
                        err('Key out of order', key.short_name)
                        break
                    previous_key = key

        lowest_c: dict[str, Note] = {}
        for k, v in spec.lowest_c.items():
            try:
                note = Note(v)
            except Exception:
                err('Invalid note', k)
                continue
            lowest_c[k] = note

    return FingeringSystem(
        all=all_,
        document=spec.document,
        fingerings=fingerings,
        keys=keys,
        lowest_c=lowest_c,
        metadata=spec.metadata,
        to_key=to_key,
    )


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
