import re
import subprocess
import sys
from pathlib import Path

import rdflib
from rdflib.namespace import OWL, RDF, SH

ROOT = Path(__file__).parent.parent
ERA = rdflib.Namespace("https://jayvdb.github.io/era_data/vocab#")


def terms(graph, *types):
    """Return the names of the era: terms the graph gives one of the types."""
    return {
        str(term).removeprefix(str(ERA))
        for kind in types
        for term in graph.subjects(RDF.type, kind)
        if str(term).startswith(str(ERA))
    }


def test_vocab_md_is_up_to_date():
    subprocess.run([sys.executable, str(ROOT / "vocab_md.py"), "--check"], check=True)


def test_vocab_defines_the_terms_era_rdf_writes():
    """vocab.ttl defines each term era_rdf.py writes, and only those."""
    used = set(re.findall(r'VOCAB \+ "(\w+)"', (ROOT / "era_rdf.py").read_text(encoding="utf-8")))
    vocab = rdflib.Graph().parse(ROOT / "vocab" / "vocab.ttl", format="turtle")
    assert terms(vocab, OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty) == used


def test_shapes_cover_the_vocab():
    """shapes.ttl has a shape for each class of vocab.ttl, and a property shape for each of its properties."""
    vocab = rdflib.Graph().parse(ROOT / "vocab" / "vocab.ttl", format="turtle")
    shapes = rdflib.Graph().parse(ROOT / "vocab" / "shapes.ttl", format="turtle")
    targets = {str(cls).removeprefix(str(ERA)) for cls in shapes.objects(predicate=SH.targetClass)}
    paths = {str(path).removeprefix(str(ERA)) for path in shapes.objects(predicate=SH.path)}
    assert terms(vocab, OWL.Class) <= targets
    assert terms(vocab, OWL.ObjectProperty, OWL.DatatypeProperty) <= paths
