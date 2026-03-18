from __future__ import annotations

import os
from pathlib import Path

import tomlkit

from fing import fingering_system
from fing.layout import Layout


def load(f):
    with open(f) as fp:
        return tomlkit.load(fp)


TEST_FINGERINGS = Path('charts/recorder-fingerings.svg')
REWRITE_TEST_DATA = os.environ.get('REWRITE_TEST_DATA')
SIZES_FILE = Path('test/sizes.json')

ROOT = Path('fingerings/recorder')

FS_FILE = ROOT / 'recorder-fingering.toml'
FS = fingering_system.make(load(FS_FILE))
LAYOUT_FILE = ROOT / 'recorder-fingering.layout.toml'
LAYOUT = Layout.make(load(LAYOUT_FILE), FS.to_button)
