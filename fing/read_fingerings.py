import dataclasses as dc
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

    loaded: dict[Path, Any] = {Path(p): load(p) for p in config_files}
    if len(loaded) != len(config_files):
        print('WARNING: duplicate input files', file=sys.stderr)
    if errors := {k: v for k, v in loaded.items() if isinstance(v, str)}:
        msgs = '\n'.join(f'{k}: {v}' for k, v in errors.items())
        e = len(errors) != 1
        s, n = 's' * e, '\n' * e
        exit(f'TOML error{s}: {n}{msgs}')

    bases = [k for k, v in loaded.items() if list(v) != ['layout']]
    layouts = [k for k, v in loaded.items() if list(v) == ['layout']]
    styles = [k for k in layouts if list(loaded[k]) == ['styles']]
    non_styles = [k for k in layouts if list(loaded[k]) != ['styles']]

    if len(bases) != 1:
        exit(f'{len(bases)} fingering files found')
    if layouts and not non_styles:
        exit('Styles without layouts found')
    if layouts and len(non_styles) > 1:
        exit('Too many layouts found')

    fs = fingering_system.make(loaded[bases[0]])
    msg = f'Found {len(fs.buttons)} buttons and {len(fs.fingerings)} fingerings'
    print(msg, file=sys.stderr)
    if not layouts:
        return

    layout = Layout.make(loaded[non_styles[0]], fs.to_button)
    if styles:
        # We need to be able to override existing styles
        sd = {}
        for i in (non_styles[0], *styles):
            for line in loaded[i].styles.split('\n'):
                if line := line.strip():
                    name, _, value = line.partition(' ')
                    sd[name] = value
        layout = dc.replace(layout, styles='\n'.join('{k} {v}' for k, v in sd.items()))
    r = Renderer(layout, fs.fingerings)
    print(_xml_to_str(r()))


def _xml_to_str(e: ET.Element) -> str:
    ET.indent(e)

    f = StringIO()
    ET.ElementTree(e).write(f, encoding='unicode', xml_declaration=True)
    return f.getvalue() + '\n'
