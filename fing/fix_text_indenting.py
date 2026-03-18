def fix_text_indenting(s: str) -> str:
    # Simple hack, won't work in the general case

    def it():
        indent = ''
        delta = 2 * ' '

        for line in s.splitlines(keepends=True):
            before, _, after = line.partition('<text ')
            if after:
                if '</text>' not in line:
                    indent = before
                yield line
            elif not indent:
                yield line
            elif '</text>' in line:
                yield indent + line.lstrip()
                indent = ''
            else:
                yield indent + delta + line.lstrip()

    return ''.join(it())
