from __future__ import annotations

import constants

from fing.renderer import Renderer
from fing.sizes import SizedRegion, Sizes


def test_size():
    sizes = Renderer(constants.LAYOUT, constants.FS.fingerings).sizes
    it = ((k, getattr(sizes, k)) for k in dir(Sizes) if not k.startswith('_'))
    actual = {k: [v.width, v.height] for k, v in it if k != 'inset'}

    if not constants.REWRITE_TEST_DATA:
        assert actual == SIZES
        return

    with open(__file__) as fp:
        lines = list(fp)

    with open(__file__, 'w') as fp:
        for line in lines:
            fp.write(line)
            if line.startswith('SIZES = {'):
                for k in SizedRegion:
                    fp.write(f"    '{k}': {actual[k]},\n")
                fp.write('}\n')
                break


SIZES = {
    'document': [2448, 3360],
    'body': [2388, 3300],
    'chart': [2328, 1420],
    'note_fingering': [162, 1360],
    'fingering': [102, 1200],
}
