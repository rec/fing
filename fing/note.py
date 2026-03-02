from __future__ import annotations

from functools import total_ordering
from typing import Any


@total_ordering
class Note:
    def __init__(self, s: str) -> None:
        for k, v in REPLACEMENTS.items():
            s = s.replace(k, v)
        self.name = s
        self.note = s[: 1 if s[1].isnumeric() else 2]
        self.octave = int(s[len(self.note) :])
        self.note_number = 12 * self.octave + NOTE_TO_OFFSET[self.note]

    @property
    def full_name(self) -> str:
        return self.name

    def __eq__(self, other: Any) -> bool:
        return self.note_number == other.note_number

    def __lt__(self, other: Any) -> bool:
        return self.note_number < other.note_number

    def __hash__(self) -> int:
        return hash((Note, self.note_number))

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Note('{self.name}')"


REPLACEMENTS = {'_': '', '-': '', ' ': '', 'b': '♭', '#': '♯'}
NOTE_TO_OFFSET = {
    'C': 0,
    'C♯': 1,
    'D♭': 1,
    'D': 2,
    'D♯': 3,
    'E♭': 3,
    'E': 4,
    'F': 5,
    'F♯': 6,
    'G♭': 6,
    'G': 7,
    'G♯': 8,
    'A♭': 8,
    'A': 9,
    'A♯': 10,
    'B♭': 10,
    'B': 11,
}
