"""One line to your younger self.

Writes a single line to /output/entry.txt (or the path the environment
selects) for make.fun's "One Line to Your Younger Self" bounty.

The line is a fixed, original sentence written for this entry. The
program takes no input, reads no file, and makes no network call: it
only writes the line, then reads it back and validates it.

If the first output location cannot be written or fails read-back
validation, the program falls through to the next candidate location
instead of failing outright, and only exits non-zero when no candidate
location produces a verified file.
"""

import os
import sys

LINE = "Stop saving the good shoes for someday, kid \u2014 someday is a Tuesday and your feet will already hurt."

MAX_CHARS = 200


def candidate_paths() -> list:
    """Output locations in priority order.

    ENTRY_OUTPUT wins; then a directory env var; then the default.
    """
    paths = []
    direct = os.environ.get("ENTRY_OUTPUT")
    if direct:
        paths.append(direct)
    for var in ("OUTPUT_DIR", "MAKEFUN_OUTPUT_DIR"):
        directory = os.environ.get(var)
        if directory:
            paths.append(os.path.join(directory, "entry.txt"))
    paths.append("/output/entry.txt")
    return paths


def check_line(text: str) -> str | None:
    """Return an error message if the line breaks a gate, else None."""
    if not (1 <= len(text) <= MAX_CHARS):
        return f"line is {len(text)} chars, must be 1-200"
    if not text.strip():
        return "line is whitespace only"
    if "\n" in text or "\r" in text:
        return "line must be a single line"
    if any(ord(ch) < 0x20 and ch != "\t" for ch in text):
        return "control characters in line"
    return None


def write_and_verify(path: str, text: str, data: bytes) -> None:
    """Write the line to path, then prove the file holds exactly it.

    Raises OSError / ValueError on any failure so the caller can try
    the next candidate location.
    """
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.chmod(path, 0o644)
    if os.stat(path).st_mode & 0o777 != 0o644:
        raise ValueError("file mode is not 0644 after chmod")

    with open(path, "rb") as handle:
        written = handle.read()
    if written != data:
        raise ValueError("file bytes differ from the line")
    decoded = written.decode("utf-8")
    if decoded != text:
        raise ValueError("file text differs from the line")
    if "\n" in decoded or "\r" in decoded:
        raise ValueError("written file is not a single line")
    if any(ord(ch) < 0x20 and ch != "\t" for ch in decoded):
        raise ValueError("control characters in written file")


def main() -> int:
    text = LINE
    problem = check_line(text)
    if problem is not None:
        print(f"gate failed: {problem}", file=sys.stderr)
        return 1

    data = text.encode("utf-8")
    errors = []
    for path in candidate_paths():
        try:
            write_and_verify(path, text, data)
        except (OSError, ValueError) as exc:
            errors.append(f"{path}: {exc}")
            continue
        print(f"wrote {len(text)} chars ({len(data)} bytes) to {path}")
        return 0

    for error in errors:
        print(f"write failed: {error}", file=sys.stderr)
    print("validation failed: no output location produced a verified file",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
