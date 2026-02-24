import sys

from tomlkit import exceptions, load


def check(files: list[str]) -> int | None:
    def check(f: str) -> str | None:
        try:
            keys = load(open(f))['key']
        except exceptions.TOMLKitError as e:
            return str(e)

        count = {}
        assert isinstance(keys, dict)
        for v in keys.values():
            assert isinstance(v, dict)
            s = v['short_name']  # ty: ignore[invalid-argument-type]  WHY
            count[s] = 1 + count.get(s, 0)

        if dupes := [k for k, v in count.items() if v > 1]:
            return f'Duplicate keys {dupes}'

    errors = [f'ERROR: {f}: {v}' for f in files if (v := check(f))]
    print(*(errors or ['ok']), sep='\n', file=sys.stderr)
    return bool(errors)


def main():
    sys.exit(check(sys.argv[1:]))


if __name__ == '__main__':
    main()
