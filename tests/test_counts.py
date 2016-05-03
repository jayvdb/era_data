from sqlalchemy import Table, MetaData, func
from sqlalchemy.sql import select

metadata = MetaData()


def test_2010_count(connection):
    era2010_journals = Table('era2010_journal', metadata, autoload=True, autoload_with=connection)
    print(era2010_journals)
    query = select([func.count(era2010_journals.columns.eraid)])
    result = connection.execute(query).scalar()
    print(result)
    assert False


def test_2012_count(connection):
    era2012_journals = Table('era2012_journal', metadata, autoload=True, autoload_with=connection)
    print(era2012_journals)
    query = select([func.count(era2012_journals.columns.eraid)])
    result = connection.execute(query).scalar()
    print(result)
    assert False
