"""The ERA journal and conference lists and the ANZSRC classifications, as an RDF graph.

The data is the triple store published with the era_data release RELEASE: era_data.nt.gz, gzipped N-Triples.
This package has none of it. On first use, `path()` downloads the file from GitHub, checks it against SHA256 and
keeps it in `cache_dir()`. Set ERA_DATA_NT to the path of a local copy to use that instead, without a download.

    import era_data

    graph = era_data.graph()  # an rdflib.Graph of every triple
"""

import gzip
import hashlib
import os
import shutil
import tempfile
import urllib.request
import zlib
from pathlib import Path

import platformdirs
import rdflib

__version__ = "0.1.0"

# The release the data comes from, and the checksum of the N-Triples text in its file; `mise run pin` writes both.
RELEASE = "data-v4"
SHA256 = "bc68654497e876d01b82efea1fbf30cc8f75320d98ecc742cc9b87d764bcf5d6"
FILE = "era_data.nt.gz"
URL = f"https://github.com/jayvdb/era_data/releases/download/{RELEASE}/{FILE}"

# The environment variable naming a local copy of the file, which is used as it is.
LOCAL = "ERA_DATA_NT"
# The environment variable naming the directory to keep downloads in.
CACHE = "ERA_DATA_CACHE"


class ChecksumError(ValueError):
    """A downloaded file is not the one the release published."""


def cache_dir():
    """Return the directory the file is kept in once downloaded.

    It is ERA_DATA_CACHE when that is set, and otherwise era_data in the user's cache directory, as platformdirs
    finds it: %LOCALAPPDATA% on Windows, ~/Library/Caches on macOS and $XDG_CACHE_HOME, or ~/.cache, elsewhere.
    Each release has its own directory in it.
    """
    if base := os.environ.get(CACHE):
        return Path(base) / RELEASE
    # No author or "Cache" subdirectory, which platformdirs adds on Windows by default, so the directory is the same
    # as the Rust crate's.
    return platformdirs.user_cache_path("era_data", appauthor=False, opinion=False) / RELEASE


def sha256(file):
    """Return the SHA-256, in hex, of the N-Triples text in the gzipped file at a path.

    The text is what is checked, not the gzip bytes around it, which differ with the zlib that compressed them.
    """
    with gzip.open(file, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def cached(file):
    """Return the checksum of a kept copy of the file, or None when it is not gzip, so that it is downloaded again.

    Any other error, such as being unable to read it, is raised.
    """
    try:
        return sha256(file)
    except gzip.BadGzipFile, EOFError, zlib.error:
        return None


def fetch(url=URL, checksum=SHA256, dest=None):
    """Return the path of the file at url, downloading it to dest unless a copy with that checksum is there already.

    dest defaults to FILE in `cache_dir()`. The download goes to a temporary directory beside it, and the file replaces
    dest, in one rename, only once its checksum matches, so dest is never a partial or wrong file. ChecksumError is
    raised when it does not, and the temporary directory is removed whatever happens. A copy at dest that is damaged,
    and is not gzip, is downloaded again.
    """
    dest = Path(dest) if dest else cache_dir() / FILE
    if dest.is_file() and cached(dest) == checksum:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    # A directory rather than a file, as Windows will not rename a file that is still open.
    with tempfile.TemporaryDirectory(dir=dest.parent) as tmp:
        part = Path(tmp) / FILE
        with urllib.request.urlopen(url) as response, open(part, "wb") as f:
            shutil.copyfileobj(response, f)
        if (actual := sha256(part)) != checksum:
            raise ChecksumError(f"{url} has SHA-256 {actual}, not {checksum}")
        part.replace(dest)
    return dest


def path():
    """Return the path of the file: ERA_DATA_NT when that is set, or else the release's file, downloaded if need be."""
    if local := os.environ.get(LOCAL):
        return Path(local)
    return fetch()


def ntriples(source=None):
    """Return the whole triple store as N-Triples text, from source or, by default, `path()`."""
    with gzip.open(source or path(), "rt", encoding="ascii") as f:
        return f.read()


def graph(source=None):
    """Return the whole triple store as an rdflib.Graph, from source or, by default, `path()`."""
    result = rdflib.Graph()
    with gzip.open(source or path(), "rb") as f:
        result.parse(f, format="nt")
    return result
