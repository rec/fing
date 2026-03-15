from __future__ import annotations

import os
from pathlib import Path

import tomlkit

from fing import fingering_system
from fing.layout import Layout


def load(f):
    with open(f) as fp:
        return tomlkit.load(fp)


ROOT = Path(__file__).parents[1] / 'charts'
TEST_FINGERINGS = ROOT / 'recorder-fingerings.svg'
TEST_FINGERINGS_BELOW = ROOT / 'recorder-fingerings-below.svg'
REWRITE_TEST_DATA = os.environ.get('REWRITE_TEST_DATA')
SIZES_FILE = Path(__file__).parent / 'sizes.json'
FS_FILE = Path('fingerings/recorder-fingering.toml')
FS = fingering_system.make(load(FS_FILE))
LAYOUT_FILE = Path('fingerings/recorder-fingering.layout.toml')
LAYOUT = Layout.make(load(LAYOUT_FILE), FS.to_button)
