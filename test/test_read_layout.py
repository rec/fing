from __future__ import annotations

from fing import fingering_system as fs
from fing import layout


def test_read_layout():
    fingering = fs.make('fingerings/recorder-fingering.toml')
    lay = layout.make('fingerings/recorder-fingering.layout.toml', fingering.to_key)
    assert lay
