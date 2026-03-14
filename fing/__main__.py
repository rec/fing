import sys
from pathlib import Path
from typing import Any

from typing_extensions import Never

import tomlkit
import tyro


def tyro_main(config_files: list[Path], /) -> None:
    def exit(*msgs: Any) -> Never:
        sys.exit(' '.join(str(i) for i in ('ERROR:', *msgs)))

    def load(p: Path) -> tomlkit.TOMLDocument | str:
        try:
            with p.open() as fp:
                return tomlkit.load(fp)
        except Exception as e:
            return ' '.join(e.args)

    if not config_files:
        exit('No files')

    if missing := [f for f in config_files if not f.exists()]:
        exit(f'FileNotFound: {", ".join(str(i) for i in missing)}')

    loaded = {p: load(p) for p in config_files}
    if len(loaded) != len(config_files):
        print('WARNING: duplicate input files', file=sys.stderr)
    if errors := {k: v for k, v in loaded.items() if isinstance(v, str)}:
        msgs = '\n'.join(f'{k}: {v}' for k, v in errors.items())
        e = len(errors) != 1
        s, n = 's' * e, '\n' * e
        exit(f'TOML error{s}: {n}{msgs}')

    bases = [k for k, v in loaded.items() if list(v) != ['layout']]
    layouts = [k for k, v in loaded.items() if list(v) == ['layout']]
    non_styles = [k for k in layouts if list(loaded[k]) != ['styles']]

    fnames = ' ,'.join(str(i) for i in loaded)
    if len(bases) != 1:
        exit(f'{len(bases)} fingering files found')
    if layouts and not non_styles:
        exit('Styles without layouts found')
    if layouts and len(non_styles) > 1:
        exit('Too many layouts found')

    (base,) = bases


def main():
    tyro.cli(tyro_main)
