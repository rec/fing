from __future__ import annotations

import os
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree as ET

from fing import fingering_system as fs
from fing import layout

TEST_FILE = Path(__file__).parent / 'test.svg'
REWRITE_TEST_DATA = os.environ.get('REWRITE_TEST_DATA')


def test_read_layout():
    fingering = fs.make('fingerings/recorder-fingering.toml')
    lay = layout.make('fingerings/recorder-fingering.layout.toml', fingering.to_key)
    assert lay

    tree = lay.render([])
    ET.indent(tree.getroot())
    # print(ET.tostring(root, encoding='unicode', method='xml'))

    f = StringIO()
    tree.write(f, encoding='unicode', xml_declaration=True)
    actual = f.getvalue()

    if REWRITE_TEST_DATA or not TEST_FILE.exists():
        TEST_FILE.write_text(actual)
    else:
        expected = TEST_FILE.read_text()
        assert actual == expected
