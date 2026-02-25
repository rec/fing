from __future__ import annotations

import dataclasses as dc
from typing import Any


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

    def check(self) -> None:
        if self.errors:
            m = '\n' + '\n'.join(f'{k}: {", ".join(v)}' for k, v in self.errors.items())
            raise self.exception_type(m)

    def fail(self, label: str, *args: Any) -> None:
        self(label, *args)
        self.check()

    def __enter__(self) -> ErrorMaker:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if exc_value:
            if self.reraise or exc_type is self.exception_type:
                return
            self('Unexpected exception', f'{exc_value}\n\n{traceback}')
        self.check()
