import sys

import tyro

from .render_chart import Exit, render_chart


def main():
    try:
        tyro.cli(render_chart)
    except Exit as e:
        print('ERROR:', *e.args, file=sys.stderr)
