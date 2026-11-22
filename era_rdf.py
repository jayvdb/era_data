"""Write the whole database as gzipped N-Triples, the triple store published on each release.

Usage: python era_rdf.py <SQLite database> <output .nt.gz>

The database is the one the pipeline loads and tests, build/sqlite3/era_data.sqlite.
The output is the same bytes whenever the database is: its lines are sorted, it is ASCII-only, with any other
character written as an N-Triples Unicode escape, and the gzip header has no name or time in it.

The ANZSRC codes are SKOS concepts under the IRIs their publishers use: linked.data.gov.au's for ANZSRC 2020,
which the ABS and ARDC publish, and ARDC's purl.org vocabularies for ANZSRC 2008.
The journal lists and journals are under NAMESPACE, with the terms of this repository's own vocabulary in VOCAB.
"""

import gzip
import sqlite3
import sys

NAMESPACE = "https://jayvdb.github.io/era_data/"
VOCAB = NAMESPACE + "vocab#"

RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
SKOS = "http://www.w3.org/2004/02/skos/core#"
DCTERMS_TITLE = "http://purl.org/dc/terms/title"
BIBO_ISSN = "http://purl.org/ontology/bibo/issn"
XSD = "http://www.w3.org/2001/XMLSchema#"

# Each ANZSRC table, with the IRI its codes go under and the title of its concept scheme.
SCHEMES = {
    "anzsrc2008_for": ("http://purl.org/au-research/vocabulary/anzsrc-for/2008/", "ANZSRC 2008 Fields of Research"),
    "anzsrc2008_seo": (
        "http://purl.org/au-research/vocabulary/anzsrc-seo/2008/",
        "ANZSRC 2008 Socio-Economic Objectives",
    ),
    "anzsrc2020_for": ("https://linked.data.gov.au/def/anzsrc-for/2020/", "ANZSRC 2020 Fields of Research"),
    "anzsrc2020_seo": ("https://linked.data.gov.au/def/anzsrc-seo/2020/", "ANZSRC 2020 Socio-Economic Objectives"),
}

# Each journal list, by the prefix of its tables, with its title. They all assign ANZSRC 2008 codes.
LISTS = {
    "era2010": "ERA 2010 journal list",
    "era2012": "ERA 2012 journal list",
    "era2015": "ERA 2015 journal list",
    "era2015c": "ERA 2015 consultation journal list",
    "era2015s": "ERA 2015 submitted journal list",
}
LIST_FOR = "anzsrc2008_for"


def iri(value):
    """Return an IRI as an N-Triples term."""
    return f"<{value}>"


def literal(value, datatype=None, language=None):
    """Return a string as an N-Triples literal, ASCII-only, with an optional datatype or language tag."""
    out: list[str] = []
    for char in str(value):
        code = ord(char)
        if char in {"\\", '"'}:
            out.append("\\" + char)
        elif char == "\n":
            out.append("\\n")
        elif char == "\r":
            out.append("\\r")
        elif code < 0x20 or code > 0x7E:
            out.append(f"\\u{code:04X}" if code <= 0xFFFF else f"\\U{code:08X}")
        else:
            out.append(char)
    text = '"' + "".join(out) + '"'
    if language:
        return f"{text}@{language}"
    if datatype:
        return f"{text}^^<{XSD}{datatype}>"
    return text


def code(padded):
    """Return a code as ANZSRC writes it, from the six-digit form the tables hold: 080000 is 08, 080100 is 0801."""
    if padded.endswith("0000"):
        return padded[:2]
    if padded.endswith("00"):
        return padded[:4]
    return padded


def concept(table, padded):
    """Return the IRI of the code padded in an ANZSRC table."""
    return SCHEMES[table][0] + code(padded)


def anzsrc(db, table):
    """Yield the triples of one ANZSRC classification, as a SKOS concept scheme."""
    base, title = SCHEMES[table]
    scheme = iri(base.rstrip("/"))
    yield scheme, iri(RDF_TYPE), iri(SKOS + "ConceptScheme")
    yield scheme, iri(DCTERMS_TITLE), literal(title, language="en")
    for padded, name, parent in db.execute(f"select code, name, parent from {table}"):
        subject = iri(concept(table, padded))
        yield subject, iri(RDF_TYPE), iri(SKOS + "Concept")
        yield subject, iri(SKOS + "inScheme"), scheme
        yield subject, iri(SKOS + "notation"), literal(code(padded))
        yield subject, iri(SKOS + "prefLabel"), literal(name, language="en")
        if parent:
            yield subject, iri(SKOS + "broader"), iri(concept(table, parent))
        else:
            yield subject, iri(SKOS + "topConceptOf"), scheme


def journals(db, prefix):
    """Yield the triples of one journal list and its journals."""
    journal_list = iri(NAMESPACE + prefix)
    yield journal_list, iri(RDF_TYPE), iri(VOCAB + "JournalList")
    yield journal_list, iri(DCTERMS_TITLE), literal(LISTS[prefix], language="en")

    def journal(eraid):
        return iri(f"{NAMESPACE}{prefix}/journal/{eraid}")

    rows = db.execute(f"select eraid, title, foreign_title, rank, multidisciplinary_ind from {prefix}_journal")
    for eraid, title, foreign_title, rank, multidisciplinary in rows:
        subject = journal(eraid)
        yield subject, iri(RDF_TYPE), iri(VOCAB + "Journal")
        yield subject, iri(VOCAB + "journalList"), journal_list
        yield subject, iri(VOCAB + "eraId"), literal(eraid, "integer")
        yield subject, iri(DCTERMS_TITLE), literal(title)
        yield subject, iri(VOCAB + "multidisciplinary"), literal(str(multidisciplinary == "Y").lower(), "boolean")
        if foreign_title:
            yield subject, iri(VOCAB + "foreignTitle"), literal(foreign_title)
        if rank:
            yield subject, iri(VOCAB + "rank"), literal(rank.strip())
    for eraid, issn in db.execute(f"select eraid, issn from {prefix}_journal_issn"):
        yield journal(eraid), iri(BIBO_ISSN), literal(issn)
    for eraid, discipline in db.execute(f"select eraid, discipline from {prefix}_journal_for"):
        yield journal(eraid), iri(VOCAB + "fieldOfResearch"), iri(concept(LIST_FOR, discipline))


def lines(db):
    """Return every triple in the database as a sorted list of N-Triples lines."""
    triples = [triple for table in SCHEMES for triple in anzsrc(db, table)]
    triples += [triple for prefix in LISTS for triple in journals(db, prefix)]
    return sorted({" ".join(triple) + " .\n" for triple in triples})


def main(database, out):
    """Write the database at the path database as gzipped N-Triples to the path out."""
    db = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        text = "".join(lines(db)).encode("ascii")
    finally:
        db.close()
    # An empty name and a zero time leave nothing in the gzip header that differs from one build to the next.
    with open(out, "wb") as f, gzip.GzipFile(filename="", mode="wb", fileobj=f, mtime=0, compresslevel=9) as gz:
        gz.write(text)


if __name__ == "__main__":
    main(*sys.argv[1:])
