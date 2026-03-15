import tyro

from .read_fingerings import process_files


def main():
    tyro.cli(process_files)
