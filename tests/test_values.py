from sqlalchemy import Table, MetaData
from sqlalchemy.sql import select

metadata = MetaData()


def test_2010_southerly(connection):
    era2010_journals = Table('era2010_journal', metadata, autoload=True, autoload_with=connection)
    query = select([era2010_journals.columns.title]).where(era2010_journals.columns.eraid == 11637)
    result = connection.execute(query).first()[0]
    assert result == 'Southerly: a review of Australian literature'

def test_2010_southerly(connection):
    era2010_journals = Table('era2012_journal', metadata, autoload=True, autoload_with=connection)
    query = select([era2012_journals.columns.title]).where(era2012_journals.columns.eraid == 11637)
    result = connection.execute(query).first()[0]
    assert result == 'Southerly: a review of Australian literature'
