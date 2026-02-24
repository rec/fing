from __future__ import annotations

from fing import fingering_system as fs


def test_read_recorder():
    fingering = fs.make('fingerings/recorder-fingering.toml')
    assert fingering
