"""Convert an ERA journal list spreadsheet to generic XML.

Usage: python era_journal_list_xml.py <spreadsheet> <output stem> [<sheet name>]

The named sheet of the spreadsheet (xlsx or csv, with a header row), or else its first, is read with pyexcel and
written to <output stem>.json as `{sheet name: [one object per row]}`, and that to <output stem>.messy-xml with
dicttoxml.
era_journal_list_tidy.xsl then turns the messy XML into the ERA 2010 journal list layout.
"""

import json
import sys

import dicttoxml
import pyexcel


def main(src, out, sheet_name=None):
    """Convert the named sheet, or else the first, of the spreadsheet at src to <out>.json and <out>.messy-xml."""
    sheet = pyexcel.get_sheet(file_name=src, sheet_name=sheet_name, name_columns_by_row=0)
    # Each row's columns are sorted by name: dicttoxml writes the elements in that order, and the stylesheet and the
    # SQL converter after it are built against it.
    data = json.loads(json.dumps({sheet.name: list(sheet.to_records())}, sort_keys=True))
    with open(out + ".json", "w") as f:
        json.dump(data, f)
    with open(out + ".messy-xml", "wb") as f:
        f.write(dicttoxml.dicttoxml(data, attr_type=False, custom_root="JournalList"))


if __name__ == "__main__":
    main(*sys.argv[1:])
