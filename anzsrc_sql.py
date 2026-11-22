"""Convert the ABS spreadsheets of one ANZSRC edition to SQL insert statements.

Usage: python anzsrc_sql.py <edition> <downloads directory> [<sql flavour>]

The edition is 2008 or 2020, and the statements are written to stdout for the tables anzsrc<edition>_for (Fields of
Research) and anzsrc<edition>_seo (Socio-Economic Objectives), each made from anzsrc_schema.sql.
The flavour is the database the SQL is for: `oracle` adds the sqlplus settings it needs, and `mysql` doubles
backslashes, which it reads as escapes in string literals.

The ABS publishes ANZSRC 2020 as one spreadsheet per classification, with every division, group and field.
ANZSRC 2008 has no such spreadsheet, so it is put together from three that the ABS published with it:
- its correspondence tables with the 1998 classification, which list every six-digit field and objective;
- its correspondence tables with FOS 2007 and NABS 2007, which list every two- and four-digit code with its name.
Those hold the same codes as the ANZSRC 2008 publication, cat. no. 1297.0, and CORRECTIONS_2008 gives the
publication's names where theirs are wrong.
"""

import re
import sys
from pathlib import Path

import pyexcel

from era_journal_list_sql import Writer

# A cell holding a two- or four-digit code and its name, as the FOS and NABS correspondences have them.
# "(P)" after the name marks a partial correspondence, which is not part of the name.
CODE_AND_NAME = re.compile(r"(\d{2}|\d{4}) (.+?)(?: \(P\))?")
# A column heading in the FOS and NABS correspondences naming the ANZSRC 2008 level of the codes beneath it.
LEVEL_HEADING = re.compile(r"Matching (?:FOR|SEO) 2008 .*\(([24])-digit level\)")
# Names the 2008 spreadsheets give wrongly, each with the name the ANZSRC 2008 publication gives that code in its
# chapters on the classification. The FOS and NABS correspondences have misspellings, names shortened or from a
# draft, and spell 21 and 84 two ways each; the 1998 correspondence swaps 830205 and 830206.
# Differences only of macrons, dashes or capitals are left as the spreadsheets have them.
# FoR and SEO codes never coincide, so one table holds both.
CORRECTIONS_2008 = {
    "0701": "Agriculture, Land and Farm Management",
    "1005": "Communications Technologies",
    "21": "History and Archaeology",
    "2101": "Archaeology",
    "2199": "Other History and Archaeology",
    "180202": "Te Maori Whakahaere Rauemi (Maori Resource Law)",
    "830205": "Wild Caught Prawns",
    "830206": "Wild Caught Rock Lobster",
    "84": "Mineral Resources (excl. Energy Resources)",
    "8402": "Primary Mining and Extraction of Mineral Resources",
    "8506": "Energy Storage, Distribution and Supply",
    "8507": "Energy Conservation and Efficiency",
    "8601": "Processed Food Products and Beverages (excl. Dairy Products)",
    "8603": "Processed Non-Food Agriculture Products (excl. Wood, Paper and Fibre)",
    "8606": "Industrial Chemicals and Related Products",
    "9002": "Property, Business Support Services and Trade",
    "9606": "Environmental and Natural Resource Evaluation",
    "97": "Expanding Knowledge",
    "9701": "Expanding Knowledge",
}

# The files the download task fetches for each edition.
FILES = {
    "2008": {
        "fields": "1297.0_correspondence_tables.xls",
        "for": "12970_2008_FOS_2007_Correspondence_Table.xls",
        "seo": "12970_2008_NABS_2007_Correspondence_Table.xls",
    },
    "2020": {
        "for": "anzsrc2020_for.xlsx",
        "seo": "anzsrc2020_seo.xlsx",
    },
}


def text(cell):
    """Return a spreadsheet cell as text, a number read as a float losing its `.0`.

    Each run of whitespace becomes one space, as a few names in the 2020 spreadsheets have non-breaking spaces.
    """
    if isinstance(cell, float) and cell.is_integer():
        cell = int(cell)
    return " ".join(str(cell).split())


def pad(code):
    """Return a two-, four- or six-digit code padded with zeros to six, as the tables hold it."""
    return code.ljust(6, "0")


def add(codes, code, name):
    """Add a code and its name to codes, failing if the code already has another name."""
    if codes.setdefault(code, name) != name:
        raise ValueError(f"code {code} is named both {codes[code]!r} and {name!r}")


def upper_levels_2008(path):
    """Return {code: name} for the two- and four-digit codes in a FOS or NABS correspondence."""
    codes: dict[str, str] = {}
    levels: dict[int, int] = {}
    for row in pyexcel.get_sheet(file_name=str(path), sheet_name="Table 1").to_array():
        cells = [text(cell) for cell in row]
        if not levels:
            # Skip down to the heading row, and note which columns hold which level.
            levels = {i: int(m[1]) for i, cell in enumerate(cells) if (m := LEVEL_HEADING.fullmatch(cell))}
            continue
        # The table ends at the copyright notices, for Australia and for New Zealand.
        if any("Commonwealth of Australia" in cell for cell in cells):
            break
        for i, digits in levels.items():
            cell = cells[i] if i < len(cells) else ""
            if cell in {"", "N/A"}:
                continue
            match = CODE_AND_NAME.fullmatch(cell)
            if not match or len(match[1]) != digits:
                raise ValueError(f"{path.name}: {cell!r} is not a {digits}-digit code and name")
            code = match[1]
            add(codes, code, CORRECTIONS_2008.get(code, match[2]))
    if not levels:
        raise ValueError(f"{path.name}: no ANZSRC 2008 columns found")
    return codes


def fields_2008(path, sheet):
    """Return {code: name} for the six-digit codes in the first two columns of a 1998 correspondence table."""
    codes: dict[str, str] = {}
    for row in pyexcel.get_sheet(file_name=str(path), sheet_name=sheet).to_array():
        code, name = text(row[0]), text(row[1])
        # Codes of the 2008 classification are text, so a leading zero is kept; skip the headings and notes.
        if re.fullmatch(r"\d{6}", code):
            add(codes, code, CORRECTIONS_2008.get(code, name))
    return codes


def classification_2020(path):
    """Return {code: name} for every division, group and field or objective in an ANZSRC 2020 spreadsheet."""
    codes: dict[str, str] = {}
    # Table 3 has all three levels, each code in the column before its name.
    for row in pyexcel.get_sheet(file_name=str(path), sheet_name="Table 3").to_array():
        cells = [text(cell) for cell in row if text(cell)]
        if len(cells) >= 2 and re.fullmatch(r"\d{2}|\d{4}|\d{6}", cells[0]):
            add(codes, cells[0], cells[1])
    return codes


def read(edition, downloads):
    """Return {"for": {code: name}, "seo": {code: name}} for an edition, from the files in downloads."""
    files = {key: downloads / name for key, name in FILES[edition].items()}
    if edition == "2020":
        return {key: classification_2020(files[key]) for key in ("for", "seo")}
    return {
        "for": upper_levels_2008(files["for"]) | fields_2008(files["fields"], "Table 2"),
        "seo": upper_levels_2008(files["seo"]) | fields_2008(files["fields"], "Table 4"),
    }


def parent(code):
    """Return the code a code sits under: a field's group or a group's division; None for a division."""
    return code[:-2] if len(code) > 2 else None


def check(codes, name):
    """Fail unless every group and field of the classification sits under a code it also has."""
    if orphans := sorted(code for code in codes if (up := parent(code)) and up not in codes):
        raise ValueError(f"{name}: {len(orphans)} codes are under no code in the classification, such as {orphans[0]}")


def quote(name, flavour):
    """Return a name as the body of a SQL string literal for the given SQL flavour."""
    if flavour == "mysql":
        name = name.replace("\\", "\\\\")
    return name.replace("'", "''")


def convert(classifications, edition, writer):
    """Write the SQL inserting each classification of an edition into its table."""
    writer.set_verbose("off")
    for key, codes in classifications.items():
        table = f"anzsrc{edition}_{key}"
        check(codes, table)
        # Sorted by their padded form, every code comes after the one it sits under, which the foreign key needs.
        for code in sorted(codes, key=pad):
            up = parent(code)
            values = f"'{pad(code)}', '{quote(codes[code], writer.flavour)}', " + (f"'{pad(up)}'" if up else "null")
            writer.write(f"insert into {table} (code, name, parent) values ({values});")
        writer.set_verbose("on")
        writer.write(f"select count(*) from {table};")
        writer.set_verbose("off")
    writer.set_verbose("on")
    if writer.flavour == "oracle":
        writer.write("commit;")
        writer.write("exit")


def main(edition, downloads, flavour=""):
    """Write the SQL for one ANZSRC edition, read from the downloads directory, to stdout."""
    classifications = read(edition, Path(downloads))
    # stdout is reopened, rather than used as it is, so it writes UTF-8 and LF line endings on Windows too.
    with open(sys.stdout.fileno(), "w", encoding="utf-8", newline="\n", closefd=False) as out:
        convert(classifications, edition, Writer(out, "", flavour))


if __name__ == "__main__":
    main(*sys.argv[1:])
