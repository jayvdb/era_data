"""Convert an ERA journal list spreadsheet to generic XML.

Usage: python era_journal_list_xml.py <spreadsheet> <output stem>

The spreadsheet (xlsx or csv, with a header row) is written to <output stem>.json with pyexcel, and that to
<output stem>.messy-xml with dicttoxml. era_journal_list_tidy.xsl then turns the messy XML into the ERA 2010
journal list layout.
"""

import json
import sys

import dicttoxml
import pyexcel


def main(src, out):
    """Convert the spreadsheet at src to <out>.json and <out>.messy-xml."""
    pyexcel.save_as(file_name=src, dest_file_name=out + ".json", name_columns_by_row=0)
    with open(out + ".json") as f:
        data = json.load(f)
    with open(out + ".messy-xml", "wb") as f:
        f.write(dicttoxml.dicttoxml(data, attr_type=False, custom_root="JournalList"))


if __name__ == "__main__":
    main(*sys.argv[1:])
