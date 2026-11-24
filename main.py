#!/usr/bin/env python3
"""Deliver the finished front page to the scorer's output directory.

The page itself (entry.png, drawn by frontpage24.py) sits beside this
file. Running this program:

1. walks the PNG chunk by chunk to confirm it is a well-formed
   1024x1024 image under the 1 MiB cap,
2. copies it into $MAKEFUN_OUTPUT_DIR (or /output) under a temporary
   name and renames it into place, so a scorer never sees a
   half-written file,
3. re-reads the delivered copy and compares SHA-256 digests.

If entry.png is missing it is first rebuilt by running
frontpage24.py, which renders deterministically from its story data.
Standard library only; no network.
"""

import hashlib
import os
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE = HERE / "entry.png"
BUILDER = HERE / "frontpage24.py"
SIDE = 1024
CAP = 1_048_576
SIGNATURE = b"\x89PNG\r\n\x1a\n"


def die(reason):
    sys.exit(f"entry delivery failed: {reason}")


def png_dimensions(blob):
    """Return (width, height) by walking chunks to the IHDR payload."""
    if not blob.startswith(SIGNATURE):
        die("entry.png does not start with the PNG signature")
    pos = len(SIGNATURE)
    while pos + 8 <= len(blob):
        (length,) = struct.unpack(">I", blob[pos : pos + 4])
        kind = blob[pos + 4 : pos + 8]
        if kind == b"IHDR":
            return struct.unpack(">II", blob[pos + 8 : pos + 16])
        pos += 12 + length  # length + type + payload + CRC
    die("entry.png has no IHDR chunk")


def ensure_page():
    if PAGE.exists():
        return PAGE.read_bytes()
    subprocess.run([sys.executable, str(BUILDER)], check=True)
    if not PAGE.exists():
        die("frontpage24.py ran but entry.png is still missing")
    return PAGE.read_bytes()


def deliver(blob):
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    staging = out_dir / ".entry.png.partial"
    staging.write_bytes(blob)
    os.replace(staging, target)
    return target


def inspect(blob):
    """Validate the page against the gate; return its digest."""
    width, height = png_dimensions(blob)
    if (width, height) != (SIDE, SIDE):
        die(f"page is {width}x{height}, the gate wants {SIDE}x{SIDE}")
    if len(blob) > CAP:
        die(f"page is {len(blob)} bytes, over the {CAP}-byte cap")
    return hashlib.sha256(blob).hexdigest()


def run():
    blob = ensure_page()
    digest = inspect(blob)
    if "--check" in sys.argv:
        print(f"entry.png passes the gate - {len(blob)} bytes, sha256 {digest}")
        return
    target = deliver(blob)
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        die("delivered copy's SHA-256 does not match the source page")
    print(f"delivered {target} - {len(blob)} bytes, sha256 {digest}")


if __name__ == "__main__":
    run()
