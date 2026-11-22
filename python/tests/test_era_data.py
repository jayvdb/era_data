"""Tests of the era_data package, against the file named by ERA_DATA_NT: a local build of the release's file."""

import gzip
import os
from pathlib import Path

import era_data
import pytest
import rdflib

LOCAL = os.environ.get(era_data.LOCAL, "")
pytestmark = pytest.mark.skipif(not LOCAL, reason="ERA_DATA_NT names no local build of era_data.nt.gz")

SKOS = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
VOCAB = rdflib.Namespace("https://jayvdb.github.io/era_data/vocab#")
SOUTHERLY = rdflib.URIRef("https://jayvdb.github.io/era_data/era2010/journal/11637")


@pytest.fixture(scope="module")
def graph():
    return era_data.graph()


def test_pinned_checksum():
    """The package pins the checksum of the file the pipeline builds; `mise run pin` updates it."""
    assert era_data.sha256(LOCAL) == era_data.SHA256


def test_triple_count(graph):
    assert len(graph) == 912738


def test_journal(graph):
    title = graph.value(SOUTHERLY, rdflib.URIRef("http://purl.org/dc/terms/title"))
    assert str(title) == "Southerly: a review of Australian literature"
    assert str(graph.value(SOUTHERLY, VOCAB.rank)) == "B"
    fields = sorted(str(o) for o in graph.objects(SOUTHERLY, VOCAB.fieldOfResearch))
    assert fields == [f"http://purl.org/au-research/vocabulary/anzsrc-for/2008/{code}" for code in ("19", "20", "21")]


def test_concepts(graph):
    for2008 = rdflib.Namespace("http://purl.org/au-research/vocabulary/anzsrc-for/2008/")
    group = for2008["0801"]
    assert str(graph.value(group, SKOS.prefLabel)) == "Artificial Intelligence and Image Processing"
    assert graph.value(group, SKOS.broader) == for2008["08"]
    # Non-ASCII names survive the file's \u escapes.
    field = rdflib.URIRef("http://purl.org/au-research/vocabulary/anzsrc-for/2008/050208")
    assert str(graph.value(field, SKOS.prefLabel)) == "M\u0101ori Environmental Knowledge"
    division = rdflib.URIRef("https://linked.data.gov.au/def/anzsrc-for/2020/46")
    assert str(graph.value(division, SKOS.prefLabel)) == "INFORMATION AND COMPUTING SCIENCES"


def test_ntriples_is_ascii():
    text = era_data.ntriples()
    assert text.isascii()
    assert text.count("\n") == 912738


def test_fetch_downloads_and_caches(tmp_path):
    """fetch() downloads, checks and keeps the file, and reuses the kept copy; a file:// URL stands in for GitHub."""
    url = Path(LOCAL).resolve().as_uri()
    dest = tmp_path / "cache" / era_data.FILE
    assert era_data.fetch(url, era_data.SHA256, dest) == dest
    assert era_data.sha256(dest) == era_data.SHA256
    mtime = dest.stat().st_mtime_ns
    assert era_data.fetch("file:///nonexistent", era_data.SHA256, dest) == dest
    assert dest.stat().st_mtime_ns == mtime


def test_fetch_replaces_a_damaged_copy(tmp_path):
    """A kept copy that is not gzip is downloaded again, rather than failing every call until it is removed."""
    dest = tmp_path / "cache" / era_data.FILE
    dest.parent.mkdir()
    dest.write_bytes(b"not gzip")
    assert era_data.fetch(Path(LOCAL).resolve().as_uri(), era_data.SHA256, dest) == dest
    assert era_data.sha256(dest) == era_data.SHA256


def test_fetch_rejects_a_wrong_file(tmp_path):
    wrong = tmp_path / "wrong.nt.gz"
    wrong.write_bytes(gzip.compress(b"<urn:a> <urn:b> <urn:c> .\n"))
    dest = tmp_path / "cache" / era_data.FILE
    with pytest.raises(era_data.ChecksumError):
        era_data.fetch(wrong.as_uri(), era_data.SHA256, dest)
    # Neither the file nor the temporary directory it was downloaded to is left.
    assert list(dest.parent.iterdir()) == []


def test_cache_dir(monkeypatch, tmp_path):
    monkeypatch.setenv(era_data.CACHE, str(tmp_path))
    assert era_data.cache_dir() == tmp_path / era_data.RELEASE
    monkeypatch.delenv(era_data.CACHE)
    default = era_data.cache_dir()
    assert default.parts[-2:] == ("era_data", era_data.RELEASE)
    assert "Cache" not in default.parts[-3:-1]
