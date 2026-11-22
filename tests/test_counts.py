import pytest
from sqlalchemy import MetaData, Table, func
from sqlalchemy.sql import select

metadata = MetaData()


def test_2010_journal_count(connection):
    era2010_journals = Table("era2010_journal", metadata, autoload_with=connection)
    query = select(func.count(era2010_journals.columns.eraid))
    result = connection.execute(query).scalar()
    assert result == 20712


def test_2010_journal_issn_count(connection):
    era2010_journal_issn = Table("era2010_journal_issn", metadata, autoload_with=connection)
    query = select(func.count(era2010_journal_issn.columns.issn))
    result = connection.execute(query).scalar()
    assert result == 33848


def test_2010_journal_for_count(connection):
    era2010_journal_for = Table("era2010_journal_for", metadata, autoload_with=connection)
    query = select(func.count(era2010_journal_for.columns.eraid))
    result = connection.execute(query).scalar()
    assert result == 26822


def test_2012_journal_count(connection):
    era2012_journals = Table("era2012_journal", metadata, autoload_with=connection)
    query = select(func.count(era2012_journals.columns.eraid))
    result = connection.execute(query).scalar()
    assert result == 22413


def test_2012_journal_issn_count(connection):
    era2012_journal_issn = Table("era2012_journal_issn", metadata, autoload_with=connection)
    query = select(func.count(era2012_journal_issn.columns.issn))
    result = connection.execute(query).scalar()
    assert result == 36661


def test_2012_journal_for_count(connection):
    era2012_journal_for = Table("era2012_journal_for", metadata, autoload_with=connection)
    query = select(func.count(era2012_journal_for.columns.eraid))
    result = connection.execute(query).scalar()
    assert result == 32864


def test_2015_journal_count(connection):
    era2015_journals = Table("era2015_journal", metadata, autoload_with=connection)
    query = select(func.count(era2015_journals.columns.eraid))
    result = connection.execute(query).scalar()
    assert result == 24028


def test_2015_journal_issn_count(connection):
    era2015_journal_issn = Table("era2015_journal_issn", metadata, autoload_with=connection)
    query = select(func.count(era2015_journal_issn.columns.issn))
    result = connection.execute(query).scalar()
    assert result == 39451


def test_2015_journal_for_count(connection):
    era2015_journal_for = Table("era2015_journal_for", metadata, autoload_with=connection)
    query = select(func.count(era2015_journal_for.columns.eraid))
    result = connection.execute(query).scalar()
    assert result == 37522


def test_2015_consultation_journal_count(connection):
    era2015_journals = Table("era2015c_journal", metadata, autoload_with=connection)
    query = select(func.count(era2015_journals.columns.eraid))
    result = connection.execute(query).scalar()
    assert result == 22497


def test_2015_consultation_journal_issn_count(connection):
    era2015_journal_issn = Table("era2015c_journal_issn", metadata, autoload_with=connection)
    query = select(func.count(era2015_journal_issn.columns.issn))
    result = connection.execute(query).scalar()
    assert result == 36848


def test_2015_consultation_journal_for_count(connection):
    era2015_journal_for = Table("era2015c_journal_for", metadata, autoload_with=connection)
    query = select(func.count(era2015_journal_for.columns.eraid))
    result = connection.execute(query).scalar()
    assert result == 33005


def test_2015_submission_journal_count(connection):
    era2015_journals = Table("era2015s_journal", metadata, autoload_with=connection)
    query = select(func.count(era2015_journals.columns.eraid))
    result = connection.execute(query).scalar()
    assert result == 16229


def test_2015_submission_journal_issn_count(connection):
    era2015_journal_issn = Table("era2015s_journal_issn", metadata, autoload_with=connection)
    query = select(func.count(era2015_journal_issn.columns.issn))
    result = connection.execute(query).scalar()
    assert result == 28947


def test_2015_submission_journal_for_count(connection):
    era2015_journal_for = Table("era2015s_journal_for", metadata, autoload_with=connection)
    query = select(func.count(era2015_journal_for.columns.eraid))
    result = connection.execute(query).scalar()
    assert result == 27820


# The ERA 2018 counts are the spreadsheet's own: 40,976 FoR cells, of which 798 are MD rather than a code.
def test_2018_journal_count(connection):
    era2018_journals = Table("era2018_journal", metadata, autoload_with=connection)
    query = select(func.count(era2018_journals.columns.eraid))
    result = connection.execute(query).scalar()
    assert result == 25017


def test_2018_journal_issn_count(connection):
    era2018_journal_issn = Table("era2018_journal_issn", metadata, autoload_with=connection)
    query = select(func.count(era2018_journal_issn.columns.issn))
    result = connection.execute(query).scalar()
    assert result == 41495


def test_2018_journal_for_count(connection):
    era2018_journal_for = Table("era2018_journal_for", metadata, autoload_with=connection)
    query = select(func.count(era2018_journal_for.columns.eraid))
    result = connection.execute(query).scalar()
    assert result == 40178


def test_2018_multidisciplinary_count(connection):
    era2018_journals = Table("era2018_journal", metadata, autoload_with=connection)
    query = select(func.count()).where(era2018_journals.columns.multidisciplinary_ind == "Y")
    result = connection.execute(query).scalar()
    assert result == 798


# The ERA 2023 counts are the spreadsheets' own: each has 911 MD cells, and one journal given the same code twice.
@pytest.mark.parametrize(
    ("prefix", "journals", "issns", "fields"),
    [("era2023", 26246, 47657, 42096), ("era2023o", 26241, 47661, 42092)],
)
def test_2023_counts(connection, prefix, journals, issns, fields):
    counts: list[int] = []
    for suffix in ("", "_issn", "_for"):
        table = Table(f"{prefix}_journal{suffix}", metadata, autoload_with=connection)
        counts.append(connection.execute(select(func.count()).select_from(table)).scalar())
    assert counts == [journals, issns, fields]
    table = Table(f"{prefix}_journal", metadata, autoload_with=connection)
    query = select(func.count()).where(table.columns.multidisciplinary_ind == "Y")
    assert connection.execute(query).scalar() == 911


def test_2010_rank_counts(connection):
    """ERA 2010 is the only list with ranks; its 279 "Not ranked" journals have none."""
    era2010_journals = Table("era2010_journal", metadata, autoload_with=connection)
    rank = era2010_journals.columns.rank
    query = select(rank, func.count()).group_by(rank)
    result = {(value or "").strip(): count for value, count in connection.execute(query)}
    assert result == {"A*": 1030, "A": 3054, "B": 5667, "C": 10682, "": 279}


def test_later_lists_have_no_ranks(connection):
    for prefix in ("era2012", "era2015", "era2015c", "era2015s", "era2018", "era2023", "era2023o"):
        journals = Table(f"{prefix}_journal", metadata, autoload_with=connection)
        query = select(func.count()).select_from(journals).where(journals.columns.rank.is_not(None))
        assert connection.execute(query).scalar() == 0, prefix


# The conference lists' counts are the spreadsheets' own. ERA 2015's has 6,302 FoR cells: 3 are MD, and 5 repeat a
# code the conference already has.
@pytest.mark.parametrize(
    ("prefix", "conferences", "fields", "multidisciplinary"),
    [("era2010", 1952, 2135, 0), ("era2015", 3735, 6294, 3)],
)
def test_conference_counts(connection, prefix, conferences, fields, multidisciplinary):
    table = Table(f"{prefix}_conference", metadata, autoload_with=connection)
    for_table = Table(f"{prefix}_conference_for", metadata, autoload_with=connection)
    assert connection.execute(select(func.count()).select_from(table)).scalar() == conferences
    assert connection.execute(select(func.count()).select_from(for_table)).scalar() == fields
    query = select(func.count()).where(table.columns.multidisciplinary_ind == "Y")
    assert connection.execute(query).scalar() == multidisciplinary


def test_conference_rank_counts(connection):
    """ERA 2010 is the only conference list with ranks; its 5 "Not ranked" conferences have none."""
    for prefix, expected in (("era2010", {"A": 414, "B": 527, "C": 1006, "": 5}), ("era2015", {"": 3735})):
        table = Table(f"{prefix}_conference", metadata, autoload_with=connection)
        query = select(table.columns.rank, func.count()).group_by(table.columns.rank)
        assert {(value or "").strip(): count for value, count in connection.execute(query)} == expected, prefix
