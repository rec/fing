from __future__ import annotations

import os
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from fing import fingering_system, render
from fing.layout import Layout

TEST_ALL_FINGERINGS = Path(__file__).parent / 'all-recorder-fingerings.svg'
TEST_ONE_FINGERING = Path(__file__).parent / 'one-recorder-fingering.svg'
REWRITE_TEST_DATA = os.environ.get('REWRITE_TEST_DATA')


def _xml_to_str(e: ET.element) -> str:
    ET.indent(e)

    f = StringIO()
    ET.ElementTree(e).write(f, encoding='unicode', xml_declaration=True)
    return f.getvalue() + '\n'


def render_one(fs, layout):
    return render.render(layout, [], 'D')


@pytest.mark.parametrize(
    'expected_file, renderer',
    ((TEST_ONE_FINGERING, render_one), (TEST_ALL_FINGERINGS, render.render_all)),
)
def test_fingering(renderer, expected_file):
    fs = fingering_system.make('fingerings/recorder-fingering.toml')
    layout = Layout.make('fingerings/recorder-fingering.layout.toml', fs.to_key)

    actual = _xml_to_str(renderer(fs, layout))

    if REWRITE_TEST_DATA or not expected_file.exists():
        expected_file.write_text(actual)
    else:
        expected = expected_file.read_text()
        assert actual == expected
