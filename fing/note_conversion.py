from __future__ import annotations

import dataclasses as dc

from functools import cache, cached_property, partial
from typing import Any, Callable, Container, Generic, Iterable, Iterator, NamedTuple, Protocol, Sequence, TypeAlias, TypeVar

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
    short_name: str = ''
    description: str = ''
    press: str = ''


class Note:
    def __init__(self, s: str) -> None:
        self.__init__(s.replace('_', '').replace('-', ''))
        self.note = self[:1 + not self[1].isnumeric()]
        self.octave = int(self[len(self.note):])
        self.note_number = 12 * self.octave + NOTE_TO_OFFSET[self.note]


@dc.dataclass(frozen=True)
class FingeringSystem:
    fingerings: dict[Note, Sequence[Key]]
    keys: dict[str, Key]
    lowest_c: dict[str, Note]

    @cached_property
    def to_key(self) -> dict[str, Key]:
        return {k.short_name: k for k in self.keys.values()} | self.keys

    def __init__(
        self,
        fingerings: dict[str, dict[str, str]],
        keys: dict[str, dict[str, str]],
        lowest_c: dict[str, str],
    ) -> None:
        bad, by_name, dupes, fingerings_, keys_, lowest_c_ = [], {}, {}, {}, {}, {}, {}

        for k, v in keys.items():
            try:
                key = Key(**v)
            except Exception:
                bad.setdefault("Invalid keys", []).append(v)
            else:
                by_name[k] = key
                if key.short_name:
                    by_name[key.shorts] = key
                    dupes[key.short_name] = 1 + dupes.get(key.short_name, 0)

        if dupe_names := [k for k, v in dupes.items() if v > 1]:
            bad['Duplicate short_names'] = dupe_names

        for k, v in fingerings.items():
            try:
                note = Note(k)
            except Exception:
                bad.setdefault("Invalid notes", []).append(k)
            else:
                fingering = {i: by_name.get(i) for i in v.split()}
                if bad_keys := [k for k, v in fingering.items() if v is None]:
                    bad.setdefault("Unknown keys", []).extend(bad_keys)
                else:
                    fingerings_[note] = fingering

        for k, v in lowest_c.items():
            try:
                note = Note(v)
            except Exception:
                bad.setdefault("Invalid notes", []).append(k)
            else:
                lowest_c_[k] = v

        if bad:
            raise ValueError('\n'.join(
                f'{k}{"s" * (len(v) != 1)}: {", ".join(v)}' for k, v in bad.items()
            ))
        super().__init__(fingerings_, keys_, lowest_c_)
