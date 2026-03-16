from __future__ import annotations

from fing.render_chart import render_chart
from test import constants


def test_rendering(capsys):
    render_chart([constants.FS_FILE, constants.LAYOUT_FILE])
    actual = capsys.readouterr().out
    output_file = constants.TEST_FINGERINGS
    if constants.REWRITE_TEST_DATA or not output_file.exists():
        output_file.write_text(actual)
    else:
        expected = output_file.read_text()
        assert actual == expected
