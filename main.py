#!/usr/bin/env python3
"""main.py -- entrypoint for the news-image-20261124 entry.

Copies the finished front page (entry.png, in this repository) to
/output/entry.png, or to $MAKEFUN_OUTPUT_DIR/entry.png when that
variable is set. Standard library only, no network, deterministic:
every run writes the same bytes.

Before copying, the image is checked against the bounty gate:
PNG signature, IHDR 1024x1024, at most 1 MiB. After the copy, the
written file is verified by SHA-256 digest against the source.
"""

import hashlib
import os
import struct
import sys

SRC_NAME = "entry.png"
MAX_BYTES = 1048576


def fail(message):
    print("main.py: " + message, file=sys.stderr)
    raise SystemExit(1)


def check_png(data):
    if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n":
        fail("not a PNG file (bad signature)")
    if data[12:16] != b"IHDR":
        fail("PNG has no IHDR chunk where expected")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (1024, 1024):
        fail("image is %dx%d, must be 1024x1024" % (width, height))
    if len(data) > MAX_BYTES:
        fail("image is %d bytes, over the 1 MiB cap" % len(data))


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, SRC_NAME)
    with open(src, "rb") as fh:
        data = fh.read()
    check_png(data)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, SRC_NAME)
    with open(dst, "wb") as fh:
        fh.write(data)
    with open(dst, "rb") as fh:
        written = fh.read()
    if hashlib.sha256(written).hexdigest() != hashlib.sha256(data).hexdigest():
        fail("SHA-256 mismatch after copy")
    print("wrote %s (%d bytes, sha256 %s)"
          % (dst, len(written), hashlib.sha256(written).hexdigest()))


if __name__ == "__main__":
    main()
