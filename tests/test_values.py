from sqlalchemy import MetaData, Table
from sqlalchemy.sql import select

metadata = MetaData()


def test_2010_southerly(connection):
    era2010_journals = Table("era2010_journal", metadata, autoload_with=connection)
    query = select(era2010_journals.columns.title).where(era2010_journals.columns.eraid == 11637)
    result = connection.execute(query).first()[0]
    assert result == "Southerly: a review of Australian literature"

    era2010_journal_issn = Table("era2010_journal_issn", metadata, autoload_with=connection)
    query = select(era2010_journal_issn.columns.issn).where(era2010_journal_issn.columns.eraid == 11637)
    result = connection.execute(query).fetchall()
    assert result == [("0038-3732",)]

    era2010_journal_for = Table("era2010_journal_for", metadata, autoload_with=connection)
    query = (
        select(era2010_journal_for.columns.discipline)
        .where(era2010_journal_for.columns.eraid == 11637)
        .order_by(era2010_journal_for.columns.discipline)
    )
    result = connection.execute(query).fetchall()
    assert result == [("190000",), ("200000",), ("210000",)]


def test_2012_southerly(connection):
    era2012_journals = Table("era2012_journal", metadata, autoload_with=connection)
    query = select(era2012_journals.columns.title).where(era2012_journals.columns.eraid == 11637)
    result = connection.execute(query).first()[0]
    assert result == "Southerly: a review of Australian literature"

    era2012_journal_issn = Table("era2012_journal_issn", metadata, autoload_with=connection)
    query = select(era2012_journal_issn.columns.issn).where(era2012_journal_issn.columns.eraid == 11637)
    result = connection.execute(query).fetchall()
    assert result == [("0038-3732",)]

    era2012_journal_for = Table("era2012_journal_for", metadata, autoload_with=connection)
    query = (
        select(era2012_journal_for.columns.discipline)
        .where(era2012_journal_for.columns.eraid == 11637)
        .order_by(era2012_journal_for.columns.discipline)
    )
    result = connection.execute(query).fetchall()
    assert result == [("190000",), ("200000",), ("210000",)]


def test_2015_southerly(connection):
    era2015_journals = Table("era2015_journal", metadata, autoload_with=connection)
    query = select(era2015_journals.columns.title).where(era2015_journals.columns.eraid == 11637)
    result = connection.execute(query).first()[0]
    assert result == "Southerly: a review of Australian literature"

    era2015_journal_issn = Table("era2015_journal_issn", metadata, autoload_with=connection)
    query = select(era2015_journal_issn.columns.issn).where(era2015_journal_issn.columns.eraid == 11637)
    result = connection.execute(query).fetchall()
    assert result == [("0038-3732",)]

    era2015_journal_for = Table("era2015_journal_for", metadata, autoload_with=connection)
    query = (
        select(era2015_journal_for.columns.discipline)
        .where(era2015_journal_for.columns.eraid == 11637)
        .order_by(era2015_journal_for.columns.discipline)
    )
    result = connection.execute(query).fetchall()
    assert result == [("190000",), ("200000",), ("210000",)]


def test_2015_consultation_southerly(connection):
    era2015_journals = Table("era2015c_journal", metadata, autoload_with=connection)
    query = select(era2015_journals.columns.title).where(era2015_journals.columns.eraid == 11637)
    result = connection.execute(query).first()[0]
    assert result == "Southerly: a review of Australian literature"

    era2015_journal_issn = Table("era2015c_journal_issn", metadata, autoload_with=connection)
    query = select(era2015_journal_issn.columns.issn).where(era2015_journal_issn.columns.eraid == 11637)
    result = connection.execute(query).fetchall()
    assert result == [("0038-3732",)]

    era2015_journal_for = Table("era2015c_journal_for", metadata, autoload_with=connection)
    query = (
        select(era2015_journal_for.columns.discipline)
        .where(era2015_journal_for.columns.eraid == 11637)
        .order_by(era2015_journal_for.columns.discipline)
    )
    result = connection.execute(query).fetchall()
    assert result == [("190000",), ("200000",), ("210000",)]


def test_2015_submitted_southerly(connection):
    era2015_journals = Table("era2015s_journal", metadata, autoload_with=connection)
    query = select(era2015_journals.columns.title).where(era2015_journals.columns.eraid == 11637)
    result = connection.execute(query).first()[0]
    assert result == "Southerly: a review of Australian literature"

    era2015_journal_issn = Table("era2015s_journal_issn", metadata, autoload_with=connection)
    query = select(era2015_journal_issn.columns.issn).where(era2015_journal_issn.columns.eraid == 11637)
    result = connection.execute(query).fetchall()
    assert result == [("0038-3732",)]

    era2015_journal_for = Table("era2015s_journal_for", metadata, autoload_with=connection)
    query = (
        select(era2015_journal_for.columns.discipline)
        .where(era2015_journal_for.columns.eraid == 11637)
        .order_by(era2015_journal_for.columns.discipline)
    )
    result = connection.execute(query).fetchall()
    assert result == [("190000",), ("200000",), ("210000",)]


def test_2018_southerly(connection):
    era2018_journals = Table("era2018_journal", metadata, autoload_with=connection)
    query = select(era2018_journals.columns.title).where(era2018_journals.columns.eraid == 11637)
    result = connection.execute(query).first()[0]
    assert result == "Southerly: a review of Australian literature"

    era2018_journal_issn = Table("era2018_journal_issn", metadata, autoload_with=connection)
    query = select(era2018_journal_issn.columns.issn).where(era2018_journal_issn.columns.eraid == 11637)
    result = connection.execute(query).fetchall()
    assert result == [("0038-3732",)]

    era2018_journal_for = Table("era2018_journal_for", metadata, autoload_with=connection)
    query = (
        select(era2018_journal_for.columns.discipline)
        .where(era2018_journal_for.columns.eraid == 11637)
        .order_by(era2018_journal_for.columns.discipline)
    )
    result = connection.execute(query).fetchall()
    assert result == [("190000",), ("200000",), ("210000",)]


def test_2012_unicode(connection):
    era2012_journals = Table("era2012_journal", metadata, autoload_with=connection)
    query = select(era2012_journals.columns.foreign_title).where(era2012_journals.columns.eraid == 6859)
    result = connection.execute(query).first()[0]
    assert result == "Arkiv f\u00f6r nordisk filologi"


def test_conference_3dim(connection):
    """3-D Digital Imaging and Modelling is on both conference lists, with the same field of research."""
    for prefix, rank in (("era2010", "C"), ("era2015", None)):
        conferences = Table(f"{prefix}_conference", metadata, autoload_with=connection)
        columns = conferences.columns
        query = select(columns.title, columns.acronym, columns.rank).where(columns.eraid == 42269)
        assert tuple(connection.execute(query).first()) == ("3-D Digital Imaging and Modelling", "3DIM", rank)
        conference_for = Table(f"{prefix}_conference_for", metadata, autoload_with=connection)
        query = select(conference_for.columns.discipline).where(conference_for.columns.eraid == 42269)
        assert connection.execute(query).fetchall() == [("080100",)]


def test_conference_unicode(connection):
    """The spreadsheets keep the characters the ERA 2010 conference list's XML lost."""
    for prefix in ("era2010", "era2015"):
        conferences = Table(f"{prefix}_conference", metadata, autoload_with=connection)
        query = select(conferences.columns.title).where(conferences.columns.eraid == 44078)
        assert connection.execute(query).scalar() == (
            "Symposium on \u2018Building Simulation in the Southwest of England\u2019"
        )
