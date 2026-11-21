"""Convert an ERA journal list in the ERA 2010 XML layout to SQL insert statements.

Usage: python era_journal_list_sql.py <journal list xml> [<table prefix> [<sql flavour>]]

The statements are written to stdout, for the tables in schema.sql named <table prefix>_journal etc.
The flavour is the database the SQL is for. `oracle` adds the sqlplus settings it needs, and `mysql` quotes the
rank column, as MySQL 8 reserves RANK.
"""

import re
import sys
from dataclasses import dataclass, field

ERAID = re.compile(r"eraIdentifier>(\d+)<")
TITLE = re.compile(r"title>([^<]+)<")
FOREIGN_TITLE = re.compile(r"<foreignTitle>([^<]+)<")
RANK = re.compile(r"<journalRank>([^<]+)<")  # 2010 only
ISSN = re.compile(r'<issn issnCode="(.+)"/>')
DISCIPLINE = re.compile(r'<fieldOfResearch forCode="([0-9]+)" ')
MULTIDISCIPLINARY = re.compile(r'<fieldOfResearch forCode="MD" ')
# The references XML text and attribute values can hold: the five predefined entities and character references.
ENTITY = re.compile(r"&(?:#x([0-9a-fA-F]+)|#([0-9]+)|(amp|lt|gt|quot|apos));")
NAMED_ENTITIES = {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'"}


def unescape(text):
    """Return XML text with its entity and character references decoded."""

    def decode(match):
        hexadecimal, decimal, name = match.groups()
        if hexadecimal:
            return chr(int(hexadecimal, 16))
        if decimal:
            return chr(int(decimal))
        return NAMED_ENTITIES[name]

    return ENTITY.sub(decode, text)


def quote(text, flavour=""):
    """Return XML text as the body of a SQL string literal for the given SQL flavour.

    The references are decoded first, so an apostrophe one produces is doubled along with the rest.
    MySQL also reads a backslash in a string literal as an escape, so for it each backslash is doubled too.
    """
    text = unescape(text)
    if flavour == "mysql":
        text = text.replace("\\", "\\\\")
    return text.replace("'", "''")


@dataclass
class Journal:
    """One journal in the list, as read from the XML."""

    eraid: str
    title: str = ""
    foreign_title: str = ""  # 2012 only
    rank: str = ""  # 2010 only
    issns: list[str] = field(default_factory=list)
    disciplines: list[str] = field(default_factory=list)
    multidisciplinary: bool = False


class Writer:
    """Writes the SQL for one journal list, in the dialect of one database."""

    def __init__(self, out, prefix, flavour):
        """Write to out, for the tables named <prefix>_journal etc., in the SQL flavour given."""
        self.out = out
        self.prefix = prefix + "_" if prefix else ""
        self.flavour = flavour
        self.rank = "`rank`" if flavour == "mysql" else "rank"

    def quote(self, text):
        """Return XML text as the body of a string literal in this writer's SQL flavour."""
        return quote(text, self.flavour)

    def write(self, line):
        """Write one line of SQL."""
        self.out.write(line + "\n")

    def set_verbose(self, flag):
        """Turn sqlplus's echoing of statements and their results on or off; a no-op for other databases."""
        # sqlplus echoes every statement unless told not to, and `scan off` stops it reading `&` as a variable.
        if self.flavour == "oracle":
            for setting in ("scan", "echo", "termout", "feedback"):
                self.write(f"set {setting} {flag}")

    def count(self):
        """Write a query reporting how many journals are loaded so far."""
        self.set_verbose("on")
        self.write(f"select count(*) from {self.prefix}journal;")
        self.set_verbose("off")

    def journal(self, journal: Journal):
        """Write the statements that insert one journal, its ISSNs and its disciplines."""
        p = self.prefix
        eraid = journal.eraid
        title = self.quote(journal.title)
        rank = self.quote(journal.rank)
        if rank == "Not ranked":
            rank = ""

        if rank:
            self.write(f"insert into {p}journal (eraid, title, {self.rank}) values ({eraid}, '{title}', '{rank}');")
        else:
            self.write(f"insert into {p}journal (eraid, title) values ({eraid}, '{title}');")

        for column_id, issn in enumerate(journal.issns, 1):
            self.write(
                f"insert into {p}journal_issn (eraid, issn, column_id)"
                f" values ({eraid}, '{self.quote(issn)}', {column_id});"
            )

        # Disciplines are two or four digits, padded to the six of the ERA classification codes.
        for column_id, code in enumerate(journal.disciplines, 1):
            discipline = code + "00"
            if len(discipline) == 4:
                discipline += "00"
            self.write(
                f"insert into {p}journal_for (eraid, discipline, column_id)"
                f" values ({eraid}, '{discipline}', {column_id});"
            )

        if journal.multidisciplinary:
            self.write(f"update {p}journal set multidisciplinary_ind = 'Y' where eraid = {eraid};")
        if journal.foreign_title:
            foreign_title = self.quote(journal.foreign_title)
            self.write(f"update {p}journal set foreign_title = '{foreign_title}' where eraid = {eraid};")


def convert(lines, writer):
    """Write the SQL for the journal list XML read line by line from lines."""
    writer.set_verbose("off")
    journal: Journal | None = None
    count = 0
    for line in lines:
        if match := ERAID.search(line):
            if journal:
                writer.journal(journal)
                count += 1
                if count % 5000 == 0:
                    writer.count()
            journal = Journal(match[1])
        elif journal is None:
            continue
        elif match := TITLE.search(line):
            journal.title = match[1]
        elif match := FOREIGN_TITLE.search(line):
            journal.foreign_title = match[1]
        elif match := RANK.search(line):
            journal.rank = match[1]
        elif match := ISSN.search(line):
            journal.issns.append(match[1])
        elif match := DISCIPLINE.search(line):
            journal.disciplines.append(match[1])
        elif MULTIDISCIPLINARY.search(line):
            journal.multidisciplinary = True
    if journal:
        writer.journal(journal)

    writer.set_verbose("on")
    writer.write(f"select count(*) from {writer.prefix}journal;")
    if writer.flavour == "oracle":
        writer.write("commit;")
        writer.write("exit")


def main(path, prefix="", flavour=""):
    """Write the SQL for the journal list XML at path to stdout."""
    # surrogateescape passes any byte through unchanged, whatever the file's encoding.
    # stdout is reopened, rather than used as it is, so it writes UTF-8 and LF line endings on Windows too.
    with (
        open(path, encoding="utf-8", errors="surrogateescape") as f,
        open(sys.stdout.fileno(), "w", encoding="utf-8", errors="surrogateescape", newline="\n", closefd=False) as out,
    ):
        convert(f, Writer(out, prefix, flavour))


if __name__ == "__main__":
    main(*sys.argv[1:])
