from __future__ import annotations

import os
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from fing import fingering_system, render
from fing.layout import Layout

ROOT = Path(__file__).parents[1] / 'charts'
TEST_ALL_FINGERINGS = ROOT / 'all-recorder-fingerings.svg'
TEST_ONE_FINGERING = ROOT / 'one-recorder-fingering.svg'

REWRITE_TEST_DATA = os.environ.get('REWRITE_TEST_DATA')

FS = fingering_system.make('fingerings/recorder-fingering.toml')
LAYOUT = Layout.make('fingerings/recorder-fingering.layout.toml', FS.to_button)


def _xml_to_str(e: ET.element) -> str:
    ET.indent(e)

    f = StringIO()
    ET.ElementTree(e).write(f, encoding='unicode', xml_declaration=True)
    return f.getvalue() + '\n'


def render_one(fs, layout):
    assert fs.fingerings, fs.fingerings
    a, *_ = fs.fingerings
    assert isinstance(a, fingering_system.Note), type(a)
    fs.fingerings[a]
    b = fingering_system.Note('C1')
    assert str(a) == str(b)
    assert a == b, (a, type(a), b, type(b))
    fs.fingerings[fingering_system.Note('C1')]
    return render.render(layout, fs.fingerings[fingering_system.Note('C1')], 'C1')


@pytest.mark.parametrize(
    'expected_file, renderer',
    ((TEST_ONE_FINGERING, render_one), (TEST_ALL_FINGERINGS, render.render_all)),
)
def test_fingering(renderer, expected_file):
    actual = _xml_to_str(renderer(FS, LAYOUT))

    if REWRITE_TEST_DATA or not expected_file.exists():
        expected_file.write_text(actual)
    else:
        expected = expected_file.read_text()
        assert actual == expected
