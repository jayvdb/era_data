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
Instead it provides tools to fetch and transform the datasets into other formats,
and will do analysis on the dataset in the cloud.

All files stored in this repository are available under the MIT license.

## Data sources

The `download` task in `mise.toml` fetches the following from the [Internet Archive](https://web.archive.org/):

* ERA 2010 tech pack, which contains the ERA 2010 journal list
* ERA 2012 tech pack, which has no journal list in it
* ERA 2012 journal list
* ERA 2015 journal list
* ERA 2015 consultation journal list
* ERA 2015 submitted journal list

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
in the tables `era2010_journal`, `era2012_journal`, `era2015_journal`, `era2015c_journal` (consultation)
and `era2015s_journal` (submitted), each with its `_issn` and `_for` (field of research) tables.
It is the data this pipeline produces, tested, not the original files, and `era_data.sqlite.gz.sha256`
holds its checksum.

`mise run release` builds the same file into `build/release/`. Pushing a tag such as `v2026.11.0` runs the
release workflow, which builds it afresh and attaches it to that tag's release.

## Contributing

Feel free to submit pull requests for additional transforms or analysis.
Dont worry if you have only tested the changes against the databases that you have access to.
i.e. Open door policy. The more the merrier. Submit pull requests early.
It is my job to figure out how to incorporate any new code into the repository.
