from __future__ import annotations

import dataclasses as dc
from typing import Any


def fix_input_variables(d: dict[str, Any], dc_type: type) -> None:
    for f in dc.fields(dc_type):
        if f.name.endswith('_'):
            if (v := d.pop(f.name[:-1], d)) is not d:
                d[f.name] = v
