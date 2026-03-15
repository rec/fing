import sys

import tyro

from .read_fingerings import Exit, process_files


def main():
    try:
        tyro.cli(process_files)
    except Exit as e:
        print(*e.args, file=sys.stderr)
