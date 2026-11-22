# era_data

The Excellence in Research for Australia (ERA) journal lists of 2010, 2012, 2015 and 2018, and the ANZSRC 2008 and 2020
Fields of Research and Socio-Economic Objectives, as one RDF graph.

```rust,no_run
let graph = era_data::graph()?; // an oxrdf::Graph of every triple
# Ok::<(), era_data::Error>(())
```

The crate holds no data. On first use it downloads `era_data.nt.gz`, gzipped N-Triples, from the
[era_data](https://github.com/jayvdb/era_data) release `data-v4`, checks its SHA-256 and keeps it in the user's cache
directory. Set `ERA_DATA_NT` to the path of a local copy to use that instead, and `ERA_DATA_CACHE` to keep the
download somewhere else.

- `era_data::graph()` returns the triples as an `oxrdf::Graph`.
- `era_data::ntriples()` returns them as N-Triples text.
- `era_data::path()` returns the path of the file.

`examples/journal_history.rs` prints how one journal changed from list to list: its titles, fields of research,
ISSNs and, in ERA 2010, its rank. It defaults to ERA ID 4465, IEEE Transactions on Cybernetics:

```bash
cargo run --release --example journal_history -- 4465
```

The repository's README describes the data and its vocabulary.
