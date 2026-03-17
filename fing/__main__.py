import sys
from pathlib import Path

import tyro

from .render_chart import Exit, render_chart

USE_TYRO = True


def main():
    try:
        if USE_TYRO:
            tyro.cli(render_chart)
        else:
            render_chart([Path(i) for i in sys.argv[1:]])
    except Exit as e:
        print('ERROR:', *e.args, file=sys.stderr)
