from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
)


def fix_text_indenting(lines: Iterable[str]) -> Iterator[str]:
    # Simple hack, won't work in the general case
    indent = ''
    delta = 2 * ' '

    for line in lines:
        before, _, after = line.partition('<text ')
        if after:
            indent = before
            yield line
        elif not indent:
            yield line
        elif '</text>' in line:
            yield indent + line.lstrip()
            indent = ''
        else:
            yield indent + delta + line.lstrip()
