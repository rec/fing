from __future__ import annotations

import os
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from fing import fingering_system
from fing.layout import Layout
from fing.render import Renderer

ROOT = Path(__file__).parents[1] / 'charts'
TEST_FINGERINGS = ROOT / 'recorder-fingerings.svg'
TEST_FINGERINGS_BELOW = ROOT / 'recorder-fingerings-below.svg'

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


@pytest.mark.parametrize(
    'above, output_file',
    (
        (False, TEST_FINGERINGS_BELOW),
        (True, TEST_FINGERINGS),
    ),
)
def test_rendering(above, output_file):
    LAYOUT.caption.__dict__['above'] = above
    actual = _xml_to_str(Renderer(LAYOUT, FS.fingerings)())

    if REWRITE_TEST_DATA or not output_file.exists():
        output_file.write_text(actual)
    else:
        expected = output_file.read_text()
        assert actual == expected
