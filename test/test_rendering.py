from __future__ import annotations

import pytest

from fing.render_chart import render_chart
from test import constants


@pytest.mark.parametrize('use_colors', (False, True))
def test_rendering(capsys, use_colors):
    files = constants.FS_FILE, constants.LAYOUT_FILE
    if use_colors:
        files = *files, constants.COLOR_FILE
        output_file = constants.TEST_FINGERINGS_COLOR
    else:
        output_file = constants.TEST_FINGERINGS

    render_chart(files)
    actual = capsys.readouterr().out
    if constants.REWRITE_TEST_DATA or not output_file.exists():
        output_file.write_text(actual)
    else:
        expected = output_file.read_text()
        assert actual == expected
