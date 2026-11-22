import pytest
from sqlalchemy import MetaData, Table, and_, func, not_
from sqlalchemy.sql import select

metadata = MetaData()

# The number of divisions, groups, and fields or objectives in each classification, as the ABS publishes them.
LEVELS = {
    "anzsrc2008_for": (22, 157, 1238),
    "anzsrc2008_seo": (17, 119, 847),
    "anzsrc2020_for": (23, 213, 1967),
    "anzsrc2020_seo": (19, 128, 840),
}

# The journal lists, each of which assigns its journals ANZSRC 2008 divisions and groups.
JOURNAL_LISTS = ["era2010", "era2012", "era2015", "era2015c", "era2015s", "era2018"]


@pytest.mark.parametrize("name", LEVELS)
def test_level_counts(connection, name):
    table = Table(name, metadata, autoload_with=connection)
    code = table.columns.code
    divisions = code.like("__0000")
    groups = and_(code.like("____00"), not_(divisions))
    fields = not_(code.like("____00"))
    counts = tuple(
        connection.execute(select(func.count()).select_from(table).where(level)).scalar()
        for level in (divisions, groups, fields)
    )
    assert counts == LEVELS[name]


@pytest.mark.parametrize("name", LEVELS)
def test_parents(connection, name):
    """Each code sits under the code it starts with: a field under its group, a group under its division."""
    table = Table(name, metadata, autoload_with=connection)
    for code, parent in connection.execute(select(table.columns.code, table.columns.parent)):
        if code.endswith("0000"):
            assert parent is None
        elif code.endswith("00"):
            assert parent == code[:2] + "0000"
        else:
            assert parent == code[:4] + "00"


@pytest.mark.parametrize(
    ("name", "code", "expected"),
    [
        ("anzsrc2008_for", "080000", "Information and Computing Sciences"),
        ("anzsrc2008_for", "080100", "Artificial Intelligence and Image Processing"),
        ("anzsrc2008_for", "010103", "Category Theory, K Theory, Homological Algebra"),
        # Names that anzsrc_sql.py corrects from the spreadsheets to the ANZSRC 2008 publication's.
        ("anzsrc2008_for", "210000", "History and Archaeology"),
        ("anzsrc2008_for", "210100", "Archaeology"),
        ("anzsrc2008_seo", "830205", "Wild Caught Prawns"),
        ("anzsrc2008_seo", "830206", "Wild Caught Rock Lobster"),
        ("anzsrc2008_seo", "840000", "Mineral Resources (excl. Energy Resources)"),
        ("anzsrc2008_seo", "970000", "Expanding Knowledge"),
        ("anzsrc2008_seo", "970101", "Expanding Knowledge in the Mathematical Sciences"),
        ("anzsrc2020_for", "460000", "INFORMATION AND COMPUTING SCIENCES"),
        ("anzsrc2020_for", "490401", "Algebra and number theory"),
        ("anzsrc2020_seo", "140101", "Air"),
    ],
)
def test_names(connection, name, code, expected):
    table = Table(name, metadata, autoload_with=connection)
    result = connection.execute(select(table.columns.name).where(table.columns.code == code)).scalar()
    assert result == expected


@pytest.mark.parametrize("prefix", JOURNAL_LISTS)
def test_journal_disciplines_are_anzsrc2008(connection, prefix):
    """Every discipline a journal list assigns is a division or group of ANZSRC 2008, and some are not of 2020."""
    journal_for = Table(f"{prefix}_journal_for", metadata, autoload_with=connection)
    disciplines = select(journal_for.columns.discipline).distinct()
    for edition, missing in (("2008", False), ("2020", True)):
        anzsrc = Table(f"anzsrc{edition}_for", metadata, autoload_with=connection)
        unknown = disciplines.where(journal_for.columns.discipline.not_in(select(anzsrc.columns.code)))
        result = connection.execute(unknown).fetchall()
        assert bool(result) == missing, result[:5]
