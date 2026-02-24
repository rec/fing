from __future__ import annotations

import tomlkit

from fing.fingering_system import FingeringSpec, make_fingering_system


def test_read_fingering():
    rspec = tomlkit.load(open('recorder-fingering.toml'))
    fs = make_fingering_system(FingeringSpec(**rspec))
    assert fs
