from __future__ import annotations

import dataclasses as dc
from typing import Any


def fix_input_variables(dv: dict[str, Any], dc_type: type) -> None:
    assert isinstance(dv, dict), dv
    for f in dc.fields(dc_type):
        if f.name.endswith('_'):
            if (v := dv.pop(f.name[:-1], dv)) is not dv:
                dv[f.name] = v
