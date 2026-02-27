from __future__ import annotations

import dataclasses as dc
from collections.abc import Iterable
from typing import Any

from typing_extensions import Never


class ErrorMakerException(ValueError):
    pass


@dc.dataclass(frozen=True)
class ErrorMaker:
    errors: dict[str, list[str]] = dc.field(default_factory=dict)
    exception_type: type = ErrorMakerException
    joiner: str = ': '
    reraise: bool = True

    def __call__(self, label: str, *args: Any) -> None:
        msg = self.joiner.join(str(a) for a in args)
        self.errors.setdefault(label, []).append(msg)

    @property
    def exception(self) -> Exception:
        m = '\n' + '\n'.join(f'{k}: {", ".join(v)}' for k, v in self.errors.items())
        return self.exception_type(m)

    def check(self) -> None:
        if self.errors:
            raise self.exception

    def test_dupes(self, message: str, items: Iterable[str], *args: Any) -> bool:
        dupes = {}
        for i in items:
            dupes[i] = 1 + dupes.get(i, 0)
        if d := [k for k, v in dupes.items() if v > 1]:
            self(message, *d, *args)
            return False
        return True

    def fail(self, label: str, *args: Any) -> Never:
        self(label, *args)
        raise self.exception

    def __enter__(self) -> ErrorMaker:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if exc_value:
            if self.reraise or exc_type is self.exception_type:
                return
            self('Unexpected exception', f'{exc_value}\n\n{traceback}')
        self.check()
