"""Write VOCAB.md, the documentation of the era_data vocabulary, from vocab/vocab.ttl and vocab/shapes.ttl.

Usage: python vocab_md.py [--check]

vocab.ttl gives the ontology's description and each of its own terms' rdfs:comment, and shapes.ttl what properties
each class has, how many of each and of what type, with a sh:description of each where it has one. With --check it
writes nothing, and exits non-zero when VOCAB.md is not what it would write.
"""

import sys
import textwrap
from pathlib import Path

import rdflib
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SH

ROOT = Path(__file__).parent
VOCAB = ROOT / "vocab" / "vocab.ttl"
SHAPES = ROOT / "vocab" / "shapes.ttl"
OUT = ROOT / "VOCAB.md"
WIDTH = 120

# The prefixes VOCAB.md writes terms with.
PREFIXES = {
    "era": "https://jayvdb.github.io/era_data/vocab#",
    "bibo": "http://purl.org/ontology/bibo/",
    "dcterms": "http://purl.org/dc/terms/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}


def curie(term):
    """Return a term as `prefix:name` in backticks, or its whole IRI where no prefix covers it."""
    for prefix, namespace in PREFIXES.items():
        if str(term).startswith(namespace):
            return f"`{prefix}:{str(term)[len(namespace) :]}`"
    return f"<{term}>"


def text(value):
    """Return a literal's text with its line breaks and runs of spaces made single spaces."""
    return " ".join(str(value).split())


def paragraph(value, indent=""):
    """Return text wrapped to WIDTH, with indent before each line after the first."""
    return textwrap.fill(value, WIDTH, subsequent_indent=indent, break_long_words=False, break_on_hyphens=False)


def count(shape, shapes):
    """Return how many values a property shape allows, in words."""
    low = shapes.value(shape, SH.minCount)
    high = shapes.value(shape, SH.maxCount)
    low = int(low) if low is not None else 0
    high = int(high) if high is not None else None
    if high == 1:
        return "exactly one" if low == 1 else "at most one"
    return "one or more" if low else "any number of"


def values(shape, shapes):
    """Return the type a property shape allows its values, and any constraint on them, in words."""
    kind = shapes.value(shape, SH.datatype) or shapes.value(shape, SH["class"])
    words = curie(kind) if kind is not None else "values"
    allowed = shapes.value(shape, SH["in"])
    if allowed is not None:
        words += ": one of " + ", ".join(f"`{value}`" for value in Collection(shapes, allowed))
    pattern = shapes.value(shape, SH.pattern)
    if pattern is not None:
        words += f" matching `{pattern}`"
    return words


def describe(term, *graphs):
    """Return the descriptions of a term in the graphs: its rdfs:comment and sh:description, in that order."""
    parts = [text(graph.value(term, RDFS.comment)) for graph in graphs if graph.value(term, RDFS.comment)]
    parts += [text(graph.value(term, SH.description)) for graph in graphs if graph.value(term, SH.description)]
    return " ".join(parts)


def section(cls, vocab, shapes):
    """Return the lines of VOCAB.md for one class: what it is, and the properties its shapes allow it."""
    lines = [f"### {curie(cls)}", ""]
    node_shapes = sorted(shapes.subjects(SH.targetClass, cls))
    closed = [shape for shape in node_shapes if shapes.value(shape, SH.property)]
    intro = describe(cls, vocab) or " ".join(describe(shape, shapes) for shape in closed)
    lines += [paragraph(intro), ""]
    properties = [prop for shape in closed for prop in shapes.objects(shape, SH.property)]
    for prop in sorted(properties, key=lambda prop: curie(shapes.value(prop, SH.path))):
        path = shapes.value(prop, SH.path)
        details = describe(path, vocab) + " " + describe(prop, shapes)
        bullet = f"- {curie(path)}: {count(prop, shapes)} {values(prop, shapes)}. {details.strip()}"
        lines.append(paragraph(bullet.strip(), "  "))
    for shape in node_shapes:
        if shape not in closed:
            lines.append(paragraph(f"- {describe(shape, shapes)}", "  "))
    if any(shapes.value(shape, SH.closed) for shape in closed):
        lines.append("- No other property but `rdf:type`.")
    return [*lines, ""]


def markdown():
    """Return the text of VOCAB.md."""
    vocab = rdflib.Graph().parse(VOCAB, format="turtle")
    shapes = rdflib.Graph().parse(SHAPES, format="turtle")
    ontology = vocab.value(predicate=RDF.type, object=OWL.Ontology)
    lines = [
        f"# {text(vocab.value(ontology, DCTERMS.title))}",
        "",
        "<!-- vocab_md.py writes this file from vocab/vocab.ttl and vocab/shapes.ttl: edit those, and run",
        "     `mise run vocab`. -->",
        "",
        paragraph(text(vocab.value(ontology, DCTERMS.description))),
        "",
        paragraph(
            "vocab/vocab.ttl defines the vocabulary in OWL, and vocab/shapes.ttl gives the shape of the triple store "
            "in SHACL, which `mise run shacl` validates it against. The terms below use these prefixes:"
        ),
        "",
    ]
    lines += [f"- `{prefix}:` {namespace}" for prefix, namespace in PREFIXES.items()]
    lines += ["", "## Classes", ""]
    for cls in sorted(set(shapes.objects(predicate=SH.targetClass)), key=curie):
        lines += section(cls, vocab, shapes)
    return "\n".join(lines).rstrip("\n") + "\n"


def main(*args):
    """Write VOCAB.md, or with --check, exit non-zero when it is out of date."""
    out = markdown()
    if args == ("--check",):
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != out:
            sys.exit("VOCAB.md is out of date: run `mise run vocab`")
    elif args:
        sys.exit(__doc__)
    else:
        OUT.write_text(out, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main(*sys.argv[1:])
