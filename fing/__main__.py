import sys
from pathlib import Path

import tomlkit
import tyro


def tyro_main(config_files: list[Path], /) -> None:
    def load(p: Path) -> tomlkit.TOMLDocument | str:
        try:
            with p.open() as fp:
                return tomlkit.load(fp)
        except Exception as e:
            return ' '.join(e.args)

    if missing := [f for f in config_files if not f.exists()]:
        sys.exit(f'FileNotFound: {" ,".join(str(i) for i in missing)}')

    loaded = {p: load(p) for p in config_files}
    if errors := {k: v for k, v in loaded.items() if isinstance(v, str)}:
        msgs = '\n'.join(f'{k}: {v}' for k, v in errors.items())
        e = len(errors) != 1
        s, n = 's' * e, '\n' * e
        sys.exit(f'TOML error{s}: {n}{msgs}')

    bases = [k for k, v in loaded.items() if list(v) != ['layout']]
    layouts = [k for k, v in loaded.items() if list(v) == ['layout']]
    non_styles = [k for k in layouts if list(loaded[k]) != ['styles']]

    fnames = ' ,'.join(str(i) for i in loaded)
    if len(bases) != 1:
        sys.exit(f'{len(bases)} fingering files found in {fnames}')
    if layouts and not non_styles:
        sys.exit(f'Styles without layouts found in {fnames}')
    if layouts and len(non_styles) > 1:
        sys.exit(f'Too many layouts found in {fnames}')

    (base,) = bases


def main():
    tyro.cli(tyro_main)
