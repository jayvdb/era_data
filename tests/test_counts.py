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


def test_2010_rank_counts(connection):
    """ERA 2010 is the only list with ranks; its 279 "Not ranked" journals have none."""
    era2010_journals = Table("era2010_journal", metadata, autoload_with=connection)
    rank = era2010_journals.columns.rank
    query = select(rank, func.count()).group_by(rank)
    result = {(value or "").strip(): count for value, count in connection.execute(query)}
    assert result == {"A*": 1030, "A": 3054, "B": 5667, "C": 10682, "": 279}


def test_later_lists_have_no_ranks(connection):
    for prefix in ("era2012", "era2015", "era2015c", "era2015s"):
        journals = Table(f"{prefix}_journal", metadata, autoload_with=connection)
        query = select(func.count()).select_from(journals).where(journals.columns.rank.is_not(None))
        assert connection.execute(query).scalar() == 0, prefix
