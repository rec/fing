from pathlib import Path
import sys

from fing import fingering_system

import tomlkit
import tyro


def tyro_main(config_files: list[Path], /) -> None:
    def load(p: Path) ->  tomlkit.Document | str:
        try:
            with p.open() as fp:
                return tomlkit.load(fp)
        except Exception as e:
            return ' '.join(e.args)

    if missing := [f for f in config_files if not f.exists()]:
        sys.exit(f'FileNotFound: {" ,".join(missing)}')

    loaded = {p: load(p) for p in config_files}
    if errors := {k: v for k, v in loaded.items() if isinstance(v, str)):
        msgs = '\n'.join(f'{k}: {v}' for k, v in errors.items())
        e = len(errors) != 1
        sys.exit(f'TOML error{"s" * e}: {"\n" * e}{msgs}')

    bases = [k for k, v in loaded.items() if list(v) != ['layout'])]
    layouts = [k for k, v in loaded.items() if list(v) = ['layout'])]
    non_styles = [k for k in layouts if list(loaded[k]) != ['styles']]

    if len(bases) != 1:
        sys.exit(f'{len(bases)} fingering files found in {" ,".join(loaded)}')
    if layouts and not non_styles:
        sys.exit(f'Styles without layouts found in {" ,".join(loaded)}')
    if layouts and non_styles > 1:
        sys.exit(f'Too many layouts found in {" ,".join(loaded)}')

    base, = bases


    if layouts:

def main():
    tyro.cli(tyro_main)
