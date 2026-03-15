from __future__ import annotations

from fing import read_fingerings
from test import constants


def test_rendering(capsys):
    read_fingerings.process_files([constants.FS_FILE, constants.LAYOUT_FILE])
    actual = capsys.readouterr().out
    output_file = constants.TEST_FINGERINGS
    if constants.REWRITE_TEST_DATA or not output_file.exists():
        output_file.write_text(actual)
    else:
        expected = output_file.read_text()
        assert actual == expected
