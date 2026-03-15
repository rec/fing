import sys
from io import StringIO
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import tomlkit
from typing_extensions import Never

from fing import fingering_system
from fing.layout import Layout
from fing.render import Renderer


def process_files(config_files: list[Path], /) -> None:
    fingering, *layouts = _get_configs(config_files)

    fs = fingering_system.make(fingering)
    msg = f'Found {len(fs.buttons)} buttons and {len(fs.fingerings)} fingerings'
    print(msg, file=sys.stderr)
    if not layouts:
        return

    sd = {}
    for la in layouts:
        for line in la['layout'].get('styles', '').split('\n'):
            if line := line.strip():
                name, _, value = line.partition(' ')
                sd[name] = value

    lay = layouts[0]
    lay['layout']['styles'] = '\n'.join(f'{k} {v}' for k, v in sd.items())

    layout = Layout.make(lay, fs.to_button)
    r = Renderer(layout, fs.fingerings)
    print(_xml_to_str(r()))


def _get_configs(config_files: list[Path]) -> list[Any]:
    if not config_files:
        exit('No files')

    if missing := [f for f in config_files if not f.exists()]:
        exit(f'FileNotFound: {", ".join(str(i) for i in missing)}')

    loaded: dict[Path, Any] = {Path(p): load(p) for p in config_files}
    if len(loaded) != len(config_files):
        print('WARNING: duplicate input files', file=sys.stderr)
    if errors := {k: v for k, v in loaded.items() if isinstance(v, str)}:
        msgs = '\n'.join(f'{k}: {v}' for k, v in errors.items())
        e = len(errors) != 1
        s, n = 's' * e, '\n' * e
        exit(f'TOML error{s}: {n}{msgs}')

    bases = [v for v in loaded.values() if list(v) != ['layout']]
    layouts = [v for v in loaded.values() if list(v) == ['layout']]
    non_styles = [v for v in layouts if list(v) != ['styles']]
    styles = [v for v in layouts if list(v) == ['styles']]

    if len(bases) != 1:
        exit(f'{len(bases)} fingering files found')
    if layouts and not non_styles:
        exit('Styles without layouts found')
    if layouts and len(non_styles) > 1:
        exit('Too many layouts found')

    return bases + non_styles + styles


def load(p: Path) -> tomlkit.TOMLDocument | str:
    try:
        with p.open() as fp:
            return tomlkit.load(fp)
    except Exception as e:
        return ' '.join(e.args)


class Exit(Exception):
    pass


def exit(*msgs: Any) -> Never:
    raise Exit(' '.join(str(i) for i in ('ERROR:', *msgs)))


def _xml_to_str(e: ET.Element) -> str:
    ET.indent(e)

    f = StringIO()
    ET.ElementTree(e).write(f, encoding='unicode', xml_declaration=True)
    return f.getvalue()
