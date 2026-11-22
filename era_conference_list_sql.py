"""Convert an ERA conference list spreadsheet to SQL insert statements.

Usage: python era_conference_list_sql.py <conference list spreadsheet> [<table prefix> [<sql flavour>]]

The statements are written to stdout, for the tables in conference_schema.sql named <table prefix>_conference and
<table prefix>_conference_for. The flavour is as for era_journal_list_sql.py.

The list is the spreadsheet's first sheet: a header row, then a row per conference. The columns are found by their
headers, which differ between the lists: its ERA ID, title, acronym, a rank in ERA 2010 alone, and up to three fields
of research, each a code beside its name. Each cell's whitespace, non-breaking spaces included, is made single
spaces. A rank of "Not ranked" is left empty, a field of research of MD marks the conference multidisciplinary, and
a code the row repeats is kept once.
"""

import re
import sys

import pyexcel

from era_journal_list_sql import Writer

# The header of each column, as each list writes it, made lower case and without spaces.
ERAID = {"eraid"}
TITLE = {"title"}
ACRONYM = {"acronym"}
RANK = {"rank"}
FIELD = re.compile(r"for[0-9]$")


def text(cell):
    """Return a cell as text, with its runs of whitespace made single spaces and none at either end."""
    return " ".join(str(cell).split())


def columns(header):
    """Return the indexes of a list's columns, from its header row.

    They are the ERA ID's, title's, acronym's and rank's, the rank's None where the list has none, and a list of
    those of the fields of research.
    """
    names = ["".join(text(cell).lower().split()) for cell in header]

    def index(name, required=True):
        found = [n for n, cell in enumerate(names) if cell in name]
        if not found and required:
            sys.exit(f"no {min(name)} column in {header}")
        return found[0] if found else None

    fields = [n for n, cell in enumerate(names) if FIELD.match(cell)]
    if not fields:
        sys.exit(f"no field of research columns in {header}")
    return index(ERAID), index(TITLE), index(ACRONYM), index(RANK, required=False), fields


class ConferenceWriter(Writer):
    """Writes the SQL for a conference list, in the dialect of one database."""

    def quote(self, text):
        """Return text as the body of a string literal in this writer's SQL flavour."""
        if self.flavour == "mysql":
            text = text.replace("\\", "\\\\")
        return text.replace("'", "''")

    def conference(self, eraid, title, acronym, rank, codes):
        """Write the statements that insert one conference and its disciplines."""
        p = self.prefix
        names = ["eraid", "title"]
        values = [eraid, f"'{self.quote(title)}'"]
        if acronym:
            names.append("acronym")
            values.append(f"'{self.quote(acronym)}'")
        if rank:
            names.append(self.rank)
            values.append(f"'{self.quote(rank)}'")
        if "MD" in codes:
            names.append("multidisciplinary_ind")
            values.append("'Y'")
        self.write(f"insert into {p}conference ({', '.join(names)}) values ({', '.join(values)});")
        # Disciplines are two or four digits, padded to six as era_journal_list_sql.py pads a journal's.
        disciplines = [code for code in dict.fromkeys(codes) if code != "MD"]
        for column_id, code in enumerate(disciplines, 1):
            self.write(
                f"insert into {p}conference_for (eraid, discipline, column_id)"
                f" values ({eraid}, '{code.ljust(6, '0')}', {column_id});"
            )


def main(path, prefix="", flavour=""):
    """Write the SQL for the conference list spreadsheet at path to stdout."""
    header, *rows = pyexcel.get_array(file_name=path)
    eraid, title, acronym, rank, fields = columns(header)
    # stdout is reopened, rather than used as it is, so it writes UTF-8 and LF line endings on Windows too.
    with open(sys.stdout.fileno(), "w", encoding="utf-8", newline="\n", closefd=False) as out:
        writer = ConferenceWriter(out, prefix, flavour)
        writer.set_verbose("off")
        for row in rows:
            if not text(row[eraid]):
                continue
            ranked = text(row[rank]) if rank is not None else ""
            writer.conference(
                text(row[eraid]),
                text(row[title]),
                text(row[acronym]),
                "" if ranked == "Not ranked" else ranked,
                [text(row[n]) for n in fields if text(row[n])],
            )
        writer.set_verbose("on")
        writer.write(f"select count(*) from {writer.prefix}conference;")
        if flavour == "oracle":
            writer.write("commit;")
            writer.write("exit")


if __name__ == "__main__":
    main(*sys.argv[1:])
