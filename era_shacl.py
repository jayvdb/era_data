"""Validate the triple store against the SHACL shapes in vocab/shapes.ttl.

Usage: python era_shacl.py <.nt.gz>

It prints the validation report, and exits non-zero when the triple store has a violation. Warnings, such as the one
for the code 4709 of the revised ERA 2023 list, are printed but pass.
"""

import gzip
import sys
from pathlib import Path

import pyshacl
import rdflib

SHAPES = Path(__file__).parent / "vocab" / "shapes.ttl"


def main(path):
    """Validate the gzipped N-Triples at path, and exit non-zero if it does not conform."""
    data = rdflib.Graph()
    with gzip.open(path, "rb") as f:
        data.parse(f, format="nt")
    shapes = rdflib.Graph().parse(SHAPES, format="turtle")
    conforms, _, report = pyshacl.validate(data, shacl_graph=shapes, allow_warnings=True)
    print(report)
    if not conforms:
        sys.exit(1)


if __name__ == "__main__":
    main(*sys.argv[1:])
