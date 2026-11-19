"""Saved-byte checker for the frozen GNU sed/diff recipes; never runs C."""


PROFILES = ('blank_and_leading', 'blank_only', 'blank_and_both')


def line_records(raw):
    if not raw:
        return []
    parts = raw.split(b'\n')
    final_newline = parts[-1] == b''
    if final_newline:
        parts.pop()
    return [(line, index < len(parts) - 1 or final_newline) for index, line in enumerate(parts)]


def normalize_bytes(raw, profile):
    if profile not in PROFILES:
        raise ValueError('unknown_output_normalizer')
    output = []
    for line, terminated in line_records(raw):
        if line == b'':
            continue  # The first sed command deletes exactly empty input lines.
        if profile in ('blank_and_leading', 'blank_and_both'):
            line = line.lstrip(b' \t')
        if profile == 'blank_and_both':
            line = line.rstrip(b' \t')
        # An unterminated line reduced to zero bytes emits no phantom newline.
        output.append(line + (b'\n' if terminated else b''))
    return b''.join(output)


def portable_equal(raw, expected, profile):
    normalized = normalize_bytes(raw, profile)
    # GNU diff's default binary detection checks an initial block. Its -q path
    # does not apply text whitespace equivalence to binary output.
    if b'\x00' in normalized[:8192] or b'\x00' in expected[:8192]:
        return normalized == expected
    whitespace = b' \t\r\v\f'
    left = [line.rstrip(whitespace) for line, _ in line_records(normalized)]
    right = [line.rstrip(whitespace) for line, _ in line_records(expected)]
    return left == right
