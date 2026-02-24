from __future__ import annotations

import dataclasses as dc
from collections.abc import (
    Sequence,
)

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


@dc.dataclass(frozen=True)
class Key:
    short_name: str
    press: str
    description: str = ''


class Note:
    def __init__(self, s: str) -> None:
        self.name = s.replace('_', '').replace('-', '')
        self.note = self.name[: 1 if self.name[1].isnumeric() else 2]
        self.octave = int(self.name[len(self.note) :])
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


@dc.dataclass(frozen=True)
class FingeringSpec:
    fingerings: dict[str, str]
    keys: dict[str, dict[str, str]]
    lowest_c: dict[str, str]
    metadata: dict[str, str]


def make_fingering_system(spec: FingeringSpec, reraise: bool = True) -> FingeringSystem:
    all_: Sequence[Key] = ()
    fingerings: dict[Note, Sequence[Key]] = {}
    keys: dict[str, Key] = {}
    lowest_c: dict[str, Note] = {}
    to_key: dict[str, Key] = {}

    bad: dict[str, list[str]] = {}
    dupes: dict[str, int] = {}
    for k, v in spec.keys.items():
        try:
            key = Key(**v)
        except Exception:
            if reraise:
                raise
            bad.setdefault('Invalid keys', []).append(str(v))
            continue
        to_key[k] = keys[k] = key
        if s := key.short_name:
            to_key[s] = key
            dupes[s] = 1 + dupes.get(s, 0)

    if dupe_names := [k for k, v in dupes.items() if v > 1]:
        bad['Duplicate short_name'] = dupe_names

    for k, v in spec.fingerings.items():
        try:
            note = None if k == 'all' else Note(k)
        except Exception:
            if reraise:
                raise
            bad.setdefault('Invalid note', []).append(k)
            continue
        if bad_keys := [i for i in v.split() if i not in to_key]:
            bad.setdefault('Unknown key', []).extend(bad_keys)
            continue
        f = [to_key[i] for i in v.split()]
        if isinstance(note, Note):
            fingerings[note] = f
        else:
            all_ = f

    for k, v in spec.lowest_c.items():
        try:
            note = Note(v)
        except Exception:
            if reraise:
                raise
            bad.setdefault('Invalid note', []).append(k)
            continue
        lowest_c[k] = note

    if bad:
        import pprint

        pprint.pprint(bad)
        err = '\n'.join(
            f'{k}{"s" * (len(v) != 1)}: {", ".join(v)}' for k, v in bad.items()
        )
        raise ValueError(err)

    return FingeringSystem(
        all=all_,
        fingerings=fingerings,
        keys=keys,
        lowest_c=lowest_c,
        metadata=spec.metadata,
        to_key=to_key,
    )
