from __future__ import annotations

from constants import FS

from fing import fingering_system


def test_fingerings():
    assert FS.fingerings, FS.fingerings
    a, *_ = FS.fingerings
    assert isinstance(a, fingering_system.Note), type(a)
    FS.fingerings[a]
    b = fingering_system.Note('C1')
    assert str(a) == str(b)
    assert a == b, (a, type(a), b, type(b))
    FS.fingerings[fingering_system.Note('C1')]
