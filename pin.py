"""Pin the packages and the website to a release and the checksum of its triple store, or check that they are.

Usage: python pin.py [--check] <release tag> <era_data.nt.gz>

The python/ and rust/ packages and the website's build, web/build.mjs, each name the release they download
era_data.nt.gz from, and the SHA-256 of the N-Triples text in it, which they check the download against. This
writes both into each. With --check it changes nothing, and fails unless each already names that release and that
checksum, as the release workflow requires before it publishes.
"""

import gzip
import hashlib
import re
import sys
from pathlib import Path

# Each file that pins the release, with the patterns of the lines naming its release and its checksum; the second
# group of each is the value.
PACKAGES = {
    Path("python/src/era_data/__init__.py"): (r'^(RELEASE = ")([^"]*)(")$', r'^(SHA256 = ")([^"]*)(")$'),
    Path("rust/src/lib.rs"): (
        r'^(pub const RELEASE: &str = ")([^"]*)(";)$',
        r'^(pub const SHA256: &str = ")([^"]*)(";)$',
    ),
    Path("web/build.mjs"): (r'^(const RELEASE = ")([^"]*)(";)$', r'^(const SHA256 = ")([^"]*)(";)$'),
}


def sha256(path):
    """Return the SHA-256, in hex, of the N-Triples text in the gzipped file at path, as the packages check it."""
    with gzip.open(path, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def pinned(text, pattern):
    """Return the value the line matching pattern holds, failing unless exactly one line matches."""
    matches = re.findall(pattern, text, flags=re.MULTILINE)
    if len(matches) != 1:
        raise ValueError(f"{len(matches)} lines match {pattern}")
    return matches[0][1]


def main(*args):
    """Pin, or with --check verify, each file in PACKAGES; return the process exit status."""
    check = args[:1] == ("--check",)
    tag, file = args[1:] if check else args
    values = (tag, sha256(file))
    status = 0
    for path, patterns in PACKAGES.items():
        text = path.read_text(encoding="utf-8")
        for pattern, value in zip(patterns, values, strict=True):
            current = pinned(text, pattern)
            if check:
                if current != value:
                    print(f"{path} pins {current}, not {value}", file=sys.stderr)
                    status = 1
            else:
                text = re.sub(pattern, lambda m, v=value: m[1] + v + m[3], text, flags=re.MULTILINE)
        if not check:
            path.write_text(text, encoding="utf-8", newline="\n")
    return status


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
