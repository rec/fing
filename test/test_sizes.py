from __future__ import annotations

import json

from fing.render import Renderer
from fing.sizes import Sizes
from test import constants


def test_size():
    sizes = Renderer(constants.LAYOUT, constants.FS.fingerings).sizes
    it = ((k, getattr(sizes, k)) for k in dir(Sizes) if not k.startswith('_'))
    actual = {k: [v.x, v.y, v.width, v.height] for k, v in it if k != 'inset'}

    if constants.REWRITE_TEST_DATA or not constants.SIZES_FILE.exists():
        with constants.SIZES_FILE.open('w') as fp:
            print(json.dumps(actual, indent=2), file=fp)
    else:
        with constants.SIZES_FILE.open() as fp:
            expected = json.load(fp)
        assert actual == expected
