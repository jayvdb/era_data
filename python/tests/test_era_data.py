"""Tests of the era_data package, against the file named by ERA_DATA_NT: a local build of the release's file."""

import gzip
import importlib.util
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
    assert len(graph) == 1562967


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


def test_journal_history_example(graph):
    """The example's default journal, which changes in every way the lists record."""
    path = Path(__file__).parent.parent / "examples" / "journal_history.py"
    spec = importlib.util.spec_from_file_location("journal_history", path)
    assert spec and spec.loader
    example = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(example)
    entries = dict(example.history(graph, example.DEFAULT))
    assert list(entries) == [
        "ERA 2010 journal list",
        "ERA 2012 journal list",
        "ERA 2015 consultation journal list",
        "ERA 2015 journal list",
        "ERA 2015 submitted journal list",
        "ERA 2018 journal list",
        "ERA 2023 original journal list",
        "ERA 2023 revised journal list",
    ]
    first, last = entries["ERA 2010 journal list"], entries["ERA 2018 journal list"]
    # ERA 2023 assigns ANZSRC 2020 groups.
    assert entries["ERA 2023 revised journal list"]["fields"] == [
        ("4602", "Artificial intelligence"),
        ("4603", "Computer vision and multimedia computation"),
        ("4611", "Machine learning"),
    ]
    assert first["title"] == "IEEE Transactions on Systems, Man and Cybernetics, Part B: Cybernetics"
    assert first["rank"] == "A"
    assert [code for code, _ in first["fields"]] == ["08", "09", "17"]
    assert entries["ERA 2012 journal list"]["multidisciplinary"]
    assert entries["ERA 2012 journal list"]["fields"] == []
    assert last["title"] == "IEEE Transactions on Cybernetics"
    assert last["rank"] is None
    assert last["fields"] == [
        ("0102", "Applied Mathematics"),
        ("0801", "Artificial Intelligence and Image Processing"),
        ("0906", "Electrical and Electronic Engineering"),
    ]
    assert last["issns"] == ["1083-4419", "1941-0492", "2168-2267", "2168-2275"]


def test_ntriples_is_ascii():
    text = era_data.ntriples()
    assert text.isascii()
    assert text.count("\n") == 1562967


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
