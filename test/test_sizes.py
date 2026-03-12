from test_read_layout import LAYOUT

from fing.layout import Inset
from fing.sizes import Sizes


def test_sizes():
    inset = Inset(
        document=(150, 120),
        page=(100, 80),
        body=(60, 40),
        note_fingering=(10, 5),
    )
    sizes = Sizes(
        inset=inset,
        columns=14,
        rows=2,
        width=LAYOUT.width,
        height=LAYOUT.height,
    )
    actual = {k: getattr(sizes, k) for k in dir(Sizes) if not k.startswith('_')}
    expected = {
        'document': (960, 18820),
        'page': (660, 18580),
        'body': (460, 18420),
        'note_fingering': (170, 1310),
    }
    assert actual == expected
