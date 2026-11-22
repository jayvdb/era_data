# era_data

The Excellence in Research for Australia (ERA) journal lists of 2010, 2012 and 2015, and the ANZSRC 2008 and 2020
Fields of Research and Socio-Economic Objectives, as one RDF graph.

```rust,no_run
let graph = era_data::graph()?; // an oxrdf::Graph of every triple
# Ok::<(), era_data::Error>(())
```

The crate holds no data. On first use it downloads `era_data.nt.gz`, gzipped N-Triples, from the
[era_data](https://github.com/jayvdb/era_data) release `data-v3`, checks its SHA-256 and keeps it in the user's cache
directory. Set `ERA_DATA_NT` to the path of a local copy to use that instead, and `ERA_DATA_CACHE` to keep the
download somewhere else.

- `era_data::graph()` returns the triples as an `oxrdf::Graph`.
- `era_data::ntriples()` returns them as N-Triples text.
- `era_data::path()` returns the path of the file.

The repository's README describes the data and its vocabulary.
