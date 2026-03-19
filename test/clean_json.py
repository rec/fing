import json
from collections.abc import Iterator
from functools import wraps
from typing import Any


@wraps(json.dumps)
def dumps(
    obj: Any, *, indent: int | None = None, width: int = 88, **kwargs: Any
) -> Iterator[str]:
    """Multi-line JSON which fits lists and dicts of scalars onto one line"""
    delta = ' ' * (indent or 0)

    def dumps(x: Any, total_indent: str = '', offset: int = 0) -> Iterator[str]:
        i, w = 0, width - offset
        split = isinstance(x, (dict, list)) and any((i := i + s) > w for s in sizes(x))
        if not (split and indent):
            yield json.dumps(x, **kwargs)
            return

        if isinstance(x, dict):
            delimiters = '{}'
            items = iter(x.items())
            key_format = lambda key: f'{json.dumps(key, **kwargs)}: '  # noqa: E731

        elif isinstance(x, list):
            delimiters = '[]'
            items = enumerate(x)
            key_format = ''.format

        yield delimiters[0]
        yield '\n'

        next_indent = total_indent + delta
        for i, (k, v) in enumerate(items):
            k = str(k) if isinstance(k, int) else k

            yield next_indent
            yield (key := key_format(key=k))

            yield from dumps(v, next_indent, offset + len(key))
            if i != len(x) - 1:
                yield ','
            yield '\n'

        yield total_indent
        yield delimiters[1]
        if not total_indent:
            yield '\n'

    def sizes(x: Any) -> Iterator[int]:
        if isinstance(x, (dict, list)):
            it = (j for i in x.items() for j in i) if isinstance(x, dict) else iter(x)
            for i, v in enumerate(it):
                yield (i != 0) * 2  # The separator
                yield from sizes(v)
        elif isinstance(x, str):
            yield len(json.dumps(x))
        else:
            yield len(str(x))

    yield from dumps(obj)
