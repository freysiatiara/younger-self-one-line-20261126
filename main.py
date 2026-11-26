"""One line to your younger self.

Writes a single line to /output/entry.txt (or the path the environment
selects) for make.fun's "One Line to Your Younger Self" bounty.

The line is a fixed, original sentence written for this entry. The
program takes no input, reads no file, and makes no network call: it
only writes the line, then reads it back and validates it.
"""

import os
import sys

LINE = "Stop saving the good shoes for someday, kid \u2014 someday is a Tuesday and your feet will already hurt."

MAX_CHARS = 200


def resolve_output_path() -> str:
    """Pick the output path: ENTRY_OUTPUT wins, then a directory env var."""
    direct = os.environ.get("ENTRY_OUTPUT")
    if direct:
        return direct
    for var in ("OUTPUT_DIR", "MAKEFUN_OUTPUT_DIR"):
        directory = os.environ.get(var)
        if directory:
            return os.path.join(directory, "entry.txt")
    return "/output/entry.txt"


def main() -> int:
    text = LINE
    if not (1 <= len(text) <= MAX_CHARS):
        print(f"gate failed: line is {len(text)} chars, must be 1-200",
              file=sys.stderr)
        return 1
    if not text.strip():
        print("gate failed: line is whitespace only", file=sys.stderr)
        return 1
    if "\n" in text or "\r" in text:
        print("gate failed: line must be a single line", file=sys.stderr)
        return 1
    if any(ord(ch) < 0x20 and ch not in ("\t",) for ch in text):
        print("gate failed: control characters in line", file=sys.stderr)
        return 1

    path = resolve_output_path()
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    data = text.encode("utf-8")
    with open(path, "wb") as handle:
        handle.write(data)
    os.chmod(path, 0o644)

    with open(path, "rb") as handle:
        written = handle.read()
    if written != data:
        print("validation failed: file bytes differ from the line",
              file=sys.stderr)
        return 1
    decoded = written.decode("utf-8")
    if decoded != text or "\n" in decoded or "\r" in decoded:
        print("validation failed: file text differs from the line",
              file=sys.stderr)
        return 1
    print(f"wrote {len(text)} chars ({len(data)} bytes) to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
