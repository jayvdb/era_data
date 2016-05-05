# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sqlalchemy import Table, MetaData
from sqlalchemy.sql import select

metadata = MetaData()


def test_2010_southerly(connection):
    era2010_journals = Table('era2010_journal', metadata, autoload=True, autoload_with=connection)
    query = select([era2010_journals.columns.title]).where(era2010_journals.columns.eraid == 11637)
    result = connection.execute(query).first()[0]
    assert result == 'Southerly: a review of Australian literature'

    era2010_journal_issn = Table('era2010_journal_issn', metadata, autoload=True, autoload_with=connection)
    query = select([era2010_journal_issn.columns.issn]).where(era2010_journal_issn.columns.eraid == 11637)
    result = connection.execute(query).fetchall()
    assert result == [('0038-3732', )]

    era2010_journal_for = Table('era2010_journal_for', metadata, autoload=True, autoload_with=connection)
    query = select([era2010_journal_for.columns.discipline]).where(era2010_journal_for.columns.eraid == 11637)
    result = connection.execute(query).fetchall()
    assert sorted(result) == [('190000', ), ('200000', ), ('210000', )]


def test_2012_southerly(connection):
    era2012_journals = Table('era2012_journal', metadata, autoload=True, autoload_with=connection)
    query = select([era2012_journals.columns.title]).where(era2012_journals.columns.eraid == 11637)
    result = connection.execute(query).first()[0]
    assert result == 'Southerly: a review of Australian literature'

    era2012_journal_issn = Table('era2012_journal_issn', metadata, autoload=True, autoload_with=connection)
    query = select([era2012_journal_issn.columns.issn]).where(era2012_journal_issn.columns.eraid == 11637)
    result = connection.execute(query).fetchall()
    assert result == [('0038-3732', )]

    era2012_journal_for = Table('era2012_journal_for', metadata, autoload=True, autoload_with=connection)
    query = select([era2012_journal_for.columns.discipline]).where(era2012_journal_for.columns.eraid == 11637)
    result = connection.execute(query).fetchall()
    assert sorted(result) == [('190000', ), ('200000', ), ('210000', )]


def test_2015_southerly(connection):
    era2015_journals = Table('era2015_journal', metadata, autoload=True, autoload_with=connection)
    query = select([era2015_journals.columns.title]).where(era2015_journals.columns.eraid == 11637)
    result = connection.execute(query).first()[0]
    assert result == 'Southerly: a review of Australian literature'

    era2015_journal_issn = Table('era2015_journal_issn', metadata, autoload=True, autoload_with=connection)
    query = select([era2015_journal_issn.columns.issn]).where(era2015_journal_issn.columns.eraid == 11637)
    result = connection.execute(query).fetchall()
    assert result == [('0038-3732', )]

    era2015_journal_for = Table('era2015_journal_for', metadata, autoload=True, autoload_with=connection)
    query = select([era2015_journal_for.columns.discipline]).where(era2015_journal_for.columns.eraid == 11637)
    result = connection.execute(query).fetchall()
    assert sorted(result) == [('190000', ), ('200000', ), ('210000', )]


def test_2012_unicode(connection):
    era2012_journals = Table('era2012_journal', metadata, autoload=True, autoload_with=connection)
    query = select([era2012_journals.columns.foreign_title]).where(era2012_journals.columns.eraid == 6859)
    result = connection.execute(query).first()[0]
    assert result == 'Arkiv för nordisk filologi'
