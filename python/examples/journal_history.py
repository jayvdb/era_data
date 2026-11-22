"""Print how one journal changed across the ERA journal lists: its titles, fields of research, ISSNs and rank.

Usage: python journal_history.py [<ERA journal ID>]

The ERA ID defaults to DEFAULT, a journal whose fields of research and ISSNs change from list to list. A journal
has a rank only in ERA 2010, the one list that ranked journals. The journal lists assign fields of research but no
socio-economic objectives, so there are none to print.
"""

import sys

import era_data
import rdflib
from rdflib.namespace import DCTERMS, SKOS, XSD

VOCAB = rdflib.Namespace("https://jayvdb.github.io/era_data/vocab#")
BIBO_ISSN = rdflib.URIRef("http://purl.org/ontology/bibo/issn")

# IEEE Transactions on Cybernetics: renamed, and given divisions, MD, then 2008 and 2020 groups, and more ISSNs.
DEFAULT = 4465


def history(graph, eraid):
    """Return, for each journal list that has the journal, its title and that list's details of the journal.

    The details are a dict of its title, its rank or None, its fields of research as (code, name) pairs and its
    ISSNs. The lists come in the order of their titles, which is the order they were published in.
    """
    entries: list[tuple[str, dict]] = []
    for journal in graph.subjects(VOCAB.eraId, rdflib.Literal(eraid, datatype=XSD.integer)):
        journal_list = graph.value(journal, VOCAB.journalList)
        fields = sorted(
            (str(graph.value(field, SKOS.notation)), str(graph.value(field, SKOS.prefLabel)))
            for field in graph.objects(journal, VOCAB.fieldOfResearch)
        )
        rank = graph.value(journal, VOCAB.rank)
        details = {
            "title": str(graph.value(journal, DCTERMS.title)),
            "rank": str(rank) if rank is not None else None,
            "multidisciplinary": graph.value(journal, VOCAB.multidisciplinary) == rdflib.Literal(True),
            "fields": fields,
            "issns": sorted(str(issn) for issn in graph.objects(journal, BIBO_ISSN)),
        }
        entries.append((str(graph.value(journal_list, DCTERMS.title)), details))
    return sorted(entries)


def main(eraid=None):
    """Print the history of the journal with the ERA ID eraid, or DEFAULT."""
    eraid = int(eraid) if eraid else DEFAULT
    entries = history(era_data.graph(), eraid)
    if not entries:
        sys.exit(f"No journal has the ERA ID {eraid}")
    for list_title, details in entries:
        print(list_title)
        print(f"  Title: {details['title']}")
        if details["rank"]:
            print(f"  Rank: {details['rank']}")
        fields = [f"{code} {name}" for code, name in details["fields"]]
        if details["multidisciplinary"]:
            fields.append("MD Multidisciplinary")
        print(f"  Fields of research: {'; '.join(fields) or 'none'}")
        print(f"  ISSNs: {', '.join(details['issns']) or 'none'}")


if __name__ == "__main__":
    main(*sys.argv[1:])
