from __future__ import annotations

import os
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree as ET

from fing import fingering_system
from fing.layout import Layout
from fing.render import Renderer

ROOT = Path(__file__).parents[1] / 'charts'
TEST_FINGERINGS = ROOT / 'recorder-fingerings.svg'

REWRITE_TEST_DATA = os.environ.get('REWRITE_TEST_DATA')

FS = fingering_system.make('fingerings/recorder-fingering.toml')
LAYOUT = Layout.make('fingerings/recorder-fingering.layout.toml', FS.to_button)


def _xml_to_str(e: ET.element) -> str:
    ET.indent(e)

    f = StringIO()
    ET.ElementTree(e).write(f, encoding='unicode', xml_declaration=True)
    return f.getvalue() + '\n'


def test_fingerings():
    assert FS.fingerings, FS.fingerings
    a, *_ = FS.fingerings
    assert isinstance(a, fingering_system.Note), type(a)
    FS.fingerings[a]
    b = fingering_system.Note('C1')
    assert str(a) == str(b)
    assert a == b, (a, type(a), b, type(b))
    FS.fingerings[fingering_system.Note('C1')]


def test_rendering():
    actual = _xml_to_str(Renderer(LAYOUT, FS.fingerings)())

    if REWRITE_TEST_DATA or not TEST_FINGERINGS.exists():
        TEST_FINGERINGS.write_text(actual)
    else:
        expected = TEST_FINGERINGS.read_text()
        assert actual == expected
