from sqlalchemy import Table, MetaData, func
from sqlalchemy.sql import select

metadata = MetaData()


def test_2010_journal_count(connection):
    era2010_journals = Table('era2010_journal', metadata, autoload=True, autoload_with=connection)
    query = select([func.count(era2010_journals.columns.eraid)])
    result = connection.execute(query).scalar()
    assert result == 20712


def test_2010_journal_issn_count(connection):
    era2010_journal_issn = Table('era2010_journal_issn', metadata, autoload=True, autoload_with=connection)
    query = select([func.count(era2010_journal_issn.columns.issn)])
    result = connection.execute(query).scalar()
    assert result == 33848


def test_2010_journal_for_count(connection):
    era2010_journal_for = Table('era2010_journal_for', metadata, autoload=True, autoload_with=connection)
    query = select([func.count(era2010_journal_for.columns.eraid)])
    result = connection.execute(query).scalar()
    assert result == 26822


def test_2012_journal_count(connection):
    era2012_journals = Table('era2012_journal', metadata, autoload=True, autoload_with=connection)
    query = select([func.count(era2012_journals.columns.eraid)])
    result = connection.execute(query).scalar()
    assert result == 22413


def test_2012_journal_issn_count(connection):
    era2012_journal_issn = Table('era2012_journal_issn', metadata, autoload=True, autoload_with=connection)
    query = select([func.count(era2012_journal_issn.columns.issn)])
    result = connection.execute(query).scalar()
    assert result == 36661


def test_2012_journal_for_count(connection):
    era2012_journal_for = Table('era2012_journal_for', metadata, autoload=True, autoload_with=connection)
    query = select([func.count(era2012_journal_for.columns.eraid)])
    result = connection.execute(query).scalar()
    assert result == 32864


def test_2015_journal_count(connection):
    era2015_journals = Table('era2015_journal', metadata, autoload=True, autoload_with=connection)
    query = select([func.count(era2015_journals.columns.eraid)])
    result = connection.execute(query).scalar()
    assert result == 22497


def test_2015_journal_issn_count(connection):
    era2015_journal_issn = Table('era2015_journal_issn', metadata, autoload=True, autoload_with=connection)
    query = select([func.count(era2015_journal_issn.columns.issn)])
    result = connection.execute(query).scalar()
    assert result == 36848


def test_2015_journal_for_count(connection):
    era2015_journal_for = Table('era2015_journal_for', metadata, autoload=True, autoload_with=connection)
    query = select([func.count(era2015_journal_for.columns.eraid)])
    result = connection.execute(query).scalar()
    assert result == 33005


def test_2015_consultation_journal_count(connection):
    era2015_journals = Table('era2015c_journal', metadata, autoload=True, autoload_with=connection)
    query = select([func.count(era2015_journals.columns.eraid)])
    result = connection.execute(query).scalar()
    assert result == 22497


def test_2015_consultation_journal_issn_count(connection):
    era2015_journal_issn = Table('era2015c_journal_issn', metadata, autoload=True, autoload_with=connection)
    query = select([func.count(era2015_journal_issn.columns.issn)])
    result = connection.execute(query).scalar()
    assert result == 36848


def test_2015_consultation_journal_for_count(connection):
    era2015_journal_for = Table('era2015c_journal_for', metadata, autoload=True, autoload_with=connection)
    query = select([func.count(era2015_journal_for.columns.eraid)])
    result = connection.execute(query).scalar()
    assert result == 33005


def test_2015_submission_journal_count(connection):
    era2015_journals = Table('era2015s_journal', metadata, autoload=True, autoload_with=connection)
    query = select([func.count(era2015_journals.columns.eraid)])
    result = connection.execute(query).scalar()
    assert result == 16229


def test_2015_submission_journal_issn_count(connection):
    era2015_journal_issn = Table('era2015s_journal_issn', metadata, autoload=True, autoload_with=connection)
    query = select([func.count(era2015_journal_issn.columns.issn)])
    result = connection.execute(query).scalar()
    assert result == 28947


def test_2015_submission_journal_for_count(connection):
    era2015_journal_for = Table('era2015s_journal_for', metadata, autoload=True, autoload_with=connection)
    query = select([func.count(era2015_journal_for.columns.eraid)])
    result = connection.execute(query).scalar()
    assert result == 27820
