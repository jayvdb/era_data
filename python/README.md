# era-data

The Excellence in Research for Australia (ERA) journal lists of 2010, 2012, 2015, 2018 and 2023, its conference lists
of 2010 and 2015, and the ANZSRC 2008 and 2020 Fields of Research and Socio-Economic Objectives, as one RDF graph.

```python
import era_data

graph = era_data.graph()  # an rdflib.Graph of every triple
```

The package holds no data. On first use it downloads `era_data.nt.gz`, gzipped N-Triples, from the
[era_data](https://github.com/jayvdb/era_data) release `data-v4`, checks its SHA-256 and keeps it in the user's cache
directory. Set `ERA_DATA_NT` to the path of a local copy to use that instead, and `ERA_DATA_CACHE` to keep the
download somewhere else.

- `era_data.graph()` returns the triples as an `rdflib.Graph`.
- `era_data.ntriples()` returns them as N-Triples text.
- `era_data.path()` returns the path of the file.

`era_data.graph()` is slow: rdflib parses the 1.6 million triples into memory, which takes about two minutes and
2 GB of memory on a 2019 laptop. Where that matters, load the graph once and keep it, or give `era_data.path()` or
`era_data.ntriples()` to a faster RDF library or a triple store.

`examples/journal_history.py` prints how one journal changed from list to list: its titles, fields of research,
ISSNs and, in ERA 2010, its rank. It defaults to ERA ID 4465, IEEE Transactions on Cybernetics:

```bash
python examples/journal_history.py 4465
```

The repository's README describes the data, and its
[VOCAB.md](https://github.com/jayvdb/era_data/blob/master/VOCAB.md) the vocabulary.

## Copyright

The data comes from the Australian Research Council and the Australian Bureau of Statistics. The
[Copyright section](https://github.com/jayvdb/era_data#copyright) of the repository's README describes the terms
each was published under.
