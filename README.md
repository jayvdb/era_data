# ERA data

This repository contains tools to fetch and load data from the
[Excellence in Research for Australia](https://en.wikipedia.org/wiki/Excellence_in_Research_for_Australia)
program (ERA) into a database.

The motivation is the reference data for 2010 and 2012 ERA came in slightly different formats,
and the data had unusual copyright protections when it was released from the Australian Research Council (ARC),
in part due to [the Australian Crown copyright](https://en.wikipedia.org/wiki/Crown_copyright#Australia).

## Copyright

The [ARC website copyright notice](http://www.arc.gov.au/copyright.htm) mentions
[Creative Commons (CC) BY 3.0](http://creativecommons.org/licenses/by/3.0/legalcode)
however it also has an other "Other Copyright" section referring to restrictive
Crown copyright, and no statement regarding when CC or Crown applies.

In addition, the datasets for ERA 2010 and ERA 2012 can no longer be found on
their website, and the copyright notice did not mention CC licenses when these
datasets were available from their website.

To avoid this copyright problem, this repository does not contain any ERA data.
Instead it provides tools to fetch the datasets and extract the facts in them: each journal's titles, ISSNs,
fields of research and rank. Those facts, and none of the original files, are published as a SQLite database and
an RDF triple store on this repository's GitHub releases, described under Releases below.

All files stored in this repository are available under the MIT license.

## Data sources

The `download` task in `mise.toml` fetches the following from the [Internet Archive](https://web.archive.org/):

* ERA 2010 tech pack, which contains the ERA 2010 journal list
* ERA 2012 tech pack, which has no journal list in it
* ERA 2012 journal list
* ERA 2015 journal list
* ERA 2015 consultation journal list
* ERA 2015 submitted journal list
* ERA 2018 journal list
* ANZSRC 2008 and ANZSRC 2020 Fields of Research and Socio-Economic Objectives,
  from the Australian Bureau of Statistics (ABS)

## Research classifications

The ABS publishes the Australian and New Zealand Standard Research Classification (ANZSRC), cat. no. 1297.0,
with Stats NZ. It has three classifications: Type of Activity (ToA), Fields of Research (FoR) and
Socio-Economic Objectives (SEO). Each FoR and SEO code has two, four or six digits: a division, a group in
it and a field (an objective, for SEO) in that.

ERA assesses research by two- and four-digit FoR. Its journal lists assign each journal up to three of those codes,
or `MD` for multidisciplinary. The editions each round used:

| Round                               | Classification                                            |
| ----------------------------------- | --------------------------------------------------------- |
| ERA 2009 trial                      | ANZSRC 2008 FoR, for two of the eight discipline clusters |
| ERA 2010, 2012, 2015 and 2018       | ANZSRC 2008 FoR                                           |
| Engagement and Impact (EI) 2018     | ANZSRC 2008 FoR, and SEO for its impact studies           |
| ERA 2023, stopped before assessment | ANZSRC 2020 FoR                                           |

The tests check this for the lists here: every code that the 2010, 2012, 2015 and 2018 lists assign is an ANZSRC
2008 division or group, and some of them are not ANZSRC 2020 codes.

ANZSRC 2008 was released on 31 March 2008. It replaced the Australian Standard Research Classification (ASRC) 1998,
whose Research Fields, Courses and Disciplines (RFCD) classification FoR replaced, and whose SEO it revised.
Universities recoded their research records to it that year, for two collections:
the ABS's survey of research and experimental development in higher education (cat. no. 8111.0), which collected
its 2008 figures by ANZSRC for the first time, and ERA, which was built on it.

ERA takes its research income from Higher Education Research Data Collection (HERDC)'s categories, and has each
institution apportion that income, and its outputs, to FoR codes in its submission.

ANZSRC 2020 replaced the 2008 edition on 30 June 2020, with new codes throughout: FoR divisions are 30 to 52
and SEO divisions 10 to 28. It drops the SEO sectors. The ABS publishes correspondence tables between the two
editions.

The pipeline loads both editions into the tables `anzsrc2008_for`, `anzsrc2008_seo`, `anzsrc2020_for` and
`anzsrc2020_seo`. Each code is padded with zeros to six digits, as the journal lists' disciplines are, so the two
join directly. `parent` is the code each one is under. The ABS publishes ANZSRC 2020 as one spreadsheet per
classification. ANZSRC 2008 has none, so `anzsrc_sql.py` puts it together from the spreadsheets the ABS published
with it, and corrects the names where they differ from the 2008 publication.

## Usage

The tools and tasks are defined in `mise.toml` for [mise](https://mise.jdx.dev/).
Everything downloaded goes into `build/downloads/`, and everything generated into `build/`.

```bash
mise install
```

```bash
mise run test
```

`mise run test` downloads the data, converts it to XML and SQL, loads it into `build/sqlite3/era_data.sqlite`
and runs the tests.

The same pipeline runs against each of the four supported databases:

| Task                    | Database                                                                    |
| ----------------------- | --------------------------------------------------------------------------- |
| `mise run test:sqlite3` | SQLite, the same as `mise run test`                                         |
| `mise run test:pgsql`   | PostgreSQL, a local server in `build/pgsql/` on 127.0.0.1:55432             |
| `mise run test:mysql`   | MySQL, a local server in `build/mysql/` on 127.0.0.1:53306                  |
| `mise run test:oracle`  | Oracle Database Free, in the `gvenzl/oracle-free` container; needs Docker   |
| `mise run test:all`     | All four, one after another                                                 |

mise installs PostgreSQL and MySQL along with the other tools, on Linux, macOS and Windows; set `PGPORT` or
`MYSQL_TCP_PORT` to use other ports. The tasks run in bash, which on Windows is Git Bash's.
The servers keep running after the tests, for looking at the data; `mise run db:stop` stops them all.

`mise tasks` lists every step, and `mise run check` runs the linters.

## Releases

Each release has `era_data.sqlite.gz`, a single SQLite database holding every journal list above,
in the tables `era2010_journal`, `era2012_journal`, `era2015_journal`, `era2015c_journal` (consultation),
`era2015s_journal` (submitted) and `era2018_journal`, each with its `_issn` and `_for` (field of research) tables,
and the ANZSRC tables described above.
It is the data this pipeline produces, tested, not the original files, and `era_data.sqlite.gz.sha256`
holds its checksum.

Each release also has `era_data.nt.gz`, the journals and ANZSRC codes as an RDF triple store: gzipped N-Triples, one
triple per line, sorted, and ASCII-only, with any other character as an N-Triples `\u` escape. `era_data.nt.gz.sha256`
holds its checksum. `era_rdf.py` writes it from the SQLite database, leaving out the order of each journal's ISSNs
and fields of research, which the SQLite tables keep in `column_id`; use the database where that order matters.

* Each ANZSRC classification is a SKOS concept scheme, and each code a `skos:Concept` with its `skos:notation`,
  `skos:prefLabel` and `skos:broader` code. ANZSRC 2020 codes have the IRIs the ABS and ARDC publish them under, such
  as `https://linked.data.gov.au/def/anzsrc-for/2020/4601`, and ANZSRC 2008 codes those of ARDC's vocabularies,
  such as `http://purl.org/au-research/vocabulary/anzsrc-for/2008/0801`.
* Each journal list is under `https://jayvdb.github.io/era_data/`, as `<era2010>` and so on, and each journal in it
  as `<era2010/journal/11637>`. A journal has its `dcterms:title`, `bibo:issn`s and the terms of
  `https://jayvdb.github.io/era_data/vocab#`: `eraId`, `journalList`, `multidisciplinary`, `foreignTitle`, `rank`
  (ERA 2010 only) and `fieldOfResearch`, which is the ANZSRC 2008 concept.

`mise run release` builds the same files into `build/release/`. Pushing a tag such as `data-v4` runs the release
workflow, which builds them afresh and attaches them to that tag's release.

## Packages

`python/` is the Python package `era-data`, and `rust/` the Rust crate `era_data`. Each loads the triple store of
one release, which it names along with the file's checksum, and returns the whole of it as a graph:

```python
import era_data

graph = era_data.graph()  # an rdflib.Graph
```

```rust
let graph = era_data::graph()?; // an oxrdf::Graph
```

Neither holds any data. On first use each downloads `era_data.nt.gz` from its release, checks the checksum and keeps
the file in the user's cache directory. `ERA_DATA_NT` names a local copy to use instead.

`mise run test:packages` tests both against a fresh `build/era_data.nt.gz`. Before pushing a `data-v*` tag, run
`TAG=data-v4 mise run pin` to pin both packages to that release and the file's checksum, and commit the result.
The release workflow checks the pins, and publishes nothing when they do not match the file it builds.

## Contributing

Feel free to submit pull requests for additional transforms or analysis.
Dont worry if you have only tested the changes against the databases that you have access to.
i.e. Open door policy. The more the merrier. Submit pull requests early.
It is my job to figure out how to incorporate any new code into the repository.
