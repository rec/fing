import sys
from pathlib import Path
from typing import Any

import tomlkit

from fing import fingering_system
from fing.layout import Layout
from fing.renderer import Renderer
from fing.xml_to_str import xml_to_str


class Exit(Exception):
    pass


def render_chart(config_files: list[Path], /) -> None:
    fingering, *layouts = _get_configs(config_files)

    fs = fingering_system.make(fingering)
    msg = f'Found {len(fs.buttons)} buttons and {len(fs.fingerings)} fingerings'
    print(msg, file=sys.stderr)
    if not layouts:
        return

    lo = layouts[0]
    styles = lo['layout'].setdefault('styles', {})
    for s in layouts[1:]:
        styles.update(s['layout'].get('styles', {}))

    layout = Layout.make(lo, fs.to_button)
    svg = Renderer(layout, fs.fingerings)()
    print(xml_to_str(svg))


def _get_configs(config_files: list[Path]) -> list[Any]:
    if not config_files:
        raise Exit('No files')

    if missing := [f for f in config_files if not f.exists()]:
        raise Exit(f'FileNotFound: {", ".join(str(i) for i in missing)}')

    loaded: dict[Path, Any] = {Path(p): load(p) for p in config_files}
    if len(loaded) != len(config_files):
        print('WARNING: duplicate input files', file=sys.stderr)
    if errors := {k: v for k, v in loaded.items() if isinstance(v, str)}:
        msgs = '\n'.join(f'{k}: {v}' for k, v in errors.items())
        e = len(errors) != 1
        s, n = 's' * e, '\n' * e
        raise Exit(f'TOML error{s}: {n}{msgs}')

    bases = [v for v in loaded.values() if list(v) != ['layout']]
    layouts = [v for v in loaded.values() if list(v) == ['layout']]
    non_styles = [v for v in layouts if list(v['layout']) != ['styles']]
    styles = [v for v in layouts if list(v['layout']) == ['styles']]

    if len(bases) != 1:
        raise Exit(f'{len(bases)} fingering files found')
    if layouts and not non_styles:
        raise Exit('Styles without layouts found')
    if layouts and len(non_styles) > 1:
        raise Exit(f'Too many layouts found: {len(non_styles)=} {non_styles=}')

    return bases + non_styles + styles


def load(p: Path) -> tomlkit.TOMLDocument | str:
    try:
        with p.open() as fp:
            return tomlkit.load(fp)
    except Exception as e:
        return ' '.join(e.args)
