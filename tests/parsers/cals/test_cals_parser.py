# coding: utf-8
import textwrap
import unittest

import pytest
from lxml import etree
from lxml.builder import ElementMaker

from benker.builders.base_builder import BaseBuilder
from benker.common.lxml_qname import QName
from benker.parsers.cals import CalsParser
from benker.parsers.cals.frame_styles import BORDER_NONE
from benker.parsers.cals.frame_styles import BORDER_SOLID
from benker.schemas import CALS_NS
from benker.schemas import CALS_PREFIX


def cals(name):
    return QName(CALS_NS, name)


class TestCalsParser(unittest.TestCase):
    def setUp(self):
        self.builder = BaseBuilder()

    def test_builder_attached(self):
        parser = CalsParser(self.builder)
        assert parser.builder is self.builder

    def test_ns(self):
        parser = CalsParser(self.builder)
        assert parser.cals_ns is None
        parser = CalsParser(self.builder, cals_ns=CALS_NS)
        assert parser.cals_ns == CALS_NS


class StrBuilder(BaseBuilder):
    """
    Create a ``table`` element with the string representation of the table object.
    """

    def generate_table_tree(self, table):
        element = etree.Element("table")
        element.text = str(table)
        return element


def test_transform_tables():
    # fmt: off
    E = ElementMaker()
    root = E.root(
        E.table(
            E.titles("titles"),
            E.tgroup(
                E.colspec(),
                E.colspec(),
                E.thead(E.row(E.entry("Col A"), E.entry("Col B"))),
                E.tfoot(E.row(E.entry("Foot notes", namest="c1", nameend="c2"))),
                E.tbody(E.row(E.entry("A1"), E.entry("B1")),
                        E.row(E.entry("A2"), E.entry("B2"))),
            ),
        )
    )
    parser = CalsParser(StrBuilder())
    parser.transform_tables(root)
    table = root.xpath("//table")[0]
    assert table.text == textwrap.dedent("""\
    +-----------+-----------+
    |   Col A   |   Col B   |
    +-----------------------+
    | Foot note             |
    +-----------+-----------+
    |    A1     |    B1     |
    +-----------+-----------+
    |    A2     |    B2     |
    +-----------+-----------+""")
    # fmt: on


def test_parse_table():
    # fmt: off
    E = ElementMaker()
    cals_table = E.table(
        E.titles("titles"),
        E.tgroup(
            E.colspec(),
            E.colspec(),
            E.thead(E.row(E.entry("Col A"), E.entry("Col B"))),
            E.tfoot(E.row(E.entry("Foot notes", namest="c1", nameend="c2"))),
            E.tbody(E.row(E.entry("A1"), E.entry("B1")),
                    E.row(E.entry("A2"), E.entry("B2"))),
        ),
    )
    parser = CalsParser(BaseBuilder())
    table = parser.parse_table(cals_table)
    assert len(table.cols) == 2
    assert len(table.rows) == 4
    assert str(table) == textwrap.dedent("""\
    +-----------+-----------+
    |   Col A   |   Col B   |
    +-----------------------+
    | Foot note             |
    +-----------+-----------+
    |    A1     |    B1     |
    +-----------+-----------+
    |    A2     |    B2     |
    +-----------+-----------+""")
    # fmt: on


def test_setup_table():
    parser = CalsParser(BaseBuilder())
    state = parser.setup_table({"key": "value"}, nature="something")
    assert state.table is not None
    assert state.table.styles == {"key": "value"}
    assert state.table.nature == "something"


@pytest.mark.parametrize(
    "attrib, styles, nature",
    [
        (
            {"frame": "all"},
            {
                "border-bottom": BORDER_SOLID,
                "border-left": BORDER_SOLID,
                "border-right": BORDER_SOLID,
                "border-top": BORDER_SOLID,
            },
            None,
        ),
        ({"colsep": "0"}, {"x-entry-border-right": BORDER_NONE}, None),
        ({"colsep": "1"}, {"x-entry-border-right": BORDER_SOLID}, None),
        ({"rowsep": "0"}, {"x-entry-border-bottom": BORDER_NONE}, None),
        ({"rowsep": "1"}, {"x-entry-border-bottom": BORDER_SOLID}, None),
        ({"orient": "land"}, {"x-sect-orient": "landscape"}, None),
        ({"orient": "port"}, {"x-sect-orient": "portrait"}, None),
        ({"pgwide": "0"}, {"x-sect-cols": "2"}, None),
        ({"pgwide": "1"}, {"x-sect-cols": "1"}, None),
        ({"bgcolor": "#00ff00"}, {"background-color": "#00ff00"}, None),
        ({"tabstyle": "BeautifulTable"}, {}, "BeautifulTable"),
    ],
)
def test_parse_cals_table(attrib, styles, nature):
    # --without namespaces
    cals_table = etree.Element("table", attrib=attrib)
    parser = CalsParser(BaseBuilder())
    state = parser.parse_cals_table(cals_table)
    table = state.table
    assert table.styles == styles
    assert table.nature == nature

    # --with default namespaces
    cals_table_attrib = {cals(k): v for k, v in attrib.items()}
    cals_table = etree.Element(cals("table"), attrib=cals_table_attrib, nsmap={None: CALS_NS})
    parser = CalsParser(BaseBuilder(), cals_ns=CALS_NS)
    state = parser.parse_cals_table(cals_table)
    table = state.table
    assert table.styles == styles
    assert table.nature == nature

    # --with namespaces prefix
    cals_table_attrib = {cals(k): v for k, v in attrib.items()}
    cals_table = etree.Element(cals("table"), attrib=cals_table_attrib, nsmap={CALS_PREFIX: CALS_NS})
    parser = CalsParser(BaseBuilder(), cals_ns=CALS_NS)
    state = parser.parse_cals_table(cals_table)
    table = state.table
    assert table.styles == styles
    assert table.nature == nature


@pytest.mark.parametrize(
    "attrib, styles, nature",
    [
        ({"colsep": "0"}, {"x-entry-border-right": BORDER_NONE}, None),
        ({"colsep": "1"}, {"x-entry-border-right": BORDER_SOLID}, None),
        ({"rowsep": "0"}, {"x-entry-border-bottom": BORDER_NONE}, None),
        ({"rowsep": "1"}, {"x-entry-border-bottom": BORDER_SOLID}, None),
        ({"tgroupstyle": "BeautifulTable"}, {}, "BeautifulTable"),
    ],
)
def test_parse_cals_tgroup(attrib, styles, nature):
    # --without namespaces
    cals_tgroup = etree.Element("tgroup", attrib=attrib)
    parser = CalsParser(BaseBuilder())
    parser.setup_table()
    state = parser.parse_cals_tgroup(cals_tgroup)
    table = state.table
    assert table.styles == styles
    assert table.nature == nature

    # --with default namespaces
    cals_tgroup_attrib = {cals(k): v for k, v in attrib.items()}
    cals_tgroup = etree.Element(cals("tgroup"), attrib=cals_tgroup_attrib, nsmap={None: CALS_NS})
    parser = CalsParser(BaseBuilder(), cals_ns=CALS_NS)
    parser.setup_table()
    state = parser.parse_cals_tgroup(cals_tgroup)
    table = state.table
    assert table.styles == styles
    assert table.nature == nature


def test_parse_cals_tgroup__overrides_table():
    # --without namespaces
    parser = CalsParser(BaseBuilder())
    parser.setup_table(
        {
            "x-entry-border-right": BORDER_NONE,
            "x-entry-border-bottom": BORDER_NONE,
            "x-sect-orient": "landscape",
            "x-sect-cols": "1",
            "background-color": "velvet",
        },
        "TableOld",
    )
    cals_tgroup_attrib = {"colsep": "1", "rowsep": "1", "tgroupstyle": "TableNew"}
    cals_tgroup = etree.Element("tgroup", attrib=cals_tgroup_attrib)
    state = parser.parse_cals_tgroup(cals_tgroup)
    table = state.table
    assert table.styles == {
        "x-entry-border-right": BORDER_SOLID,
        "x-entry-border-bottom": BORDER_SOLID,
        "x-sect-orient": "landscape",  # preserved
        "x-sect-cols": "1",  # preserved
        "background-color": "velvet",  # preserved
    }
    assert table.nature == "TableNew"


@pytest.mark.parametrize(
    "attrib, styles, nature",
    [
        ({"valign": "top"}, {"valign": "top"}, None),
        ({"valign": "middle"}, {"valign": "middle"}, None),
        ({"valign": "bottom"}, {"valign": "bottom"}, None),
        ({"rowsep": "0"}, {"border-bottom": BORDER_NONE}, None),
        ({"rowsep": "1"}, {"border-bottom": BORDER_SOLID}, None),
        ({"rowstyle": "RowStyle"}, {"rowstyle": "RowStyle"}, None),
    ],
)
def test_parse_cals_row(attrib, styles, nature):
    # --without namespaces
    cals_row = etree.Element("row", attrib=attrib)
    parser = CalsParser(BaseBuilder())
    parser.setup_table()
    parser._state.next_row()
    state = parser.parse_cals_row(cals_row)
    row = state.table.rows[1]
    assert row.styles == styles
    assert row.nature == nature

    # --with default namespaces
    cals_row_attrib = {cals(k): v for k, v in attrib.items()}
    cals_row = etree.Element(cals("row"), attrib=cals_row_attrib, nsmap={None: CALS_NS})
    parser = CalsParser(BaseBuilder(), cals_ns=CALS_NS)
    parser.setup_table()
    parser._state.next_row()
    state = parser.parse_cals_row(cals_row)
    row = state.table.rows[1]
    assert row.styles == styles
    assert row.nature == nature


@pytest.mark.parametrize("tag, nature", [("thead", "header"), ("tfoot", "footer"), ("tbody", "body")])
def test_parse_cals_row__nature_from_parent(tag, nature):
    # --without namespaces
    cals_parent = etree.Element(tag)
    cals_row = etree.SubElement(cals_parent, "row")
    parser = CalsParser(BaseBuilder())
    parser.setup_table()
    parser._state.next_row()
    state = parser.parse_cals_row(cals_row)
    row = state.table.rows[1]
    assert row.nature == nature


def test_parse_cals_row__overrides_parent_valign():
    # --without namespaces
    cals_tbody = etree.Element("tbody", valign="top")
    cals_row = etree.SubElement(cals_tbody, "row", valign="middle")
    parser = CalsParser(BaseBuilder())
    parser.setup_table()
    parser._state.next_row()
    state = parser.parse_cals_row(cals_row)
    row = state.table.rows[1]
    assert row.styles["valign"] == "middle"


@pytest.mark.parametrize(
    "attrib, styles, nature",
    [
        ({"colsep": "0"}, {"border-right": BORDER_NONE}, None),
        ({"colsep": "1"}, {"border-right": BORDER_SOLID}, None),
        ({"rowsep": "0"}, {"border-bottom": BORDER_NONE}, None),
        ({"rowsep": "1"}, {"border-bottom": BORDER_SOLID}, None),
        ({"bgcolor": "purple"}, {"background-color": "purple"}, None),
        ({"namest": "1"}, {}, None),
        ({"nameend": "2"}, {}, None),
        ({"namest": "1", "nameend": "2"}, {}, None),
        ({"morerows": "2"}, {}, None),
        ({"valign": "top"}, {"valign": "top"}, None),
        ({"valign": "middle"}, {"valign": "middle"}, None),
        ({"valign": "bottom"}, {"valign": "bottom"}, None),
        ({"align": "left"}, {"align": "left"}, None),
        ({"align": "right"}, {"align": "right"}, None),
        ({"align": "center"}, {"align": "center"}, None),
        ({"align": "justify"}, {"align": "justify"}, None),
        ({"align": "char"}, {"align": "left"}, None),
    ],
)
def test_parse_cals_entry(attrib, styles, nature):
    # --without namespaces
    cals_entry = etree.Element("entry", attrib=attrib)
    parser = CalsParser(BaseBuilder())
    parser.setup_table()
    state = parser._state
    state.next_row()
    state.row = state.table.rows[state.row_pos]
    state.next_col()
    state = parser.parse_cals_entry(cals_entry)
    cell = state.table[(1, 1)]
    assert cell.styles == styles
    assert cell.nature == nature

    # --with default namespaces
    cals_entry_attrib = {cals(k): v for k, v in attrib.items()}
    cals_entry = etree.Element(cals("entry"), attrib=cals_entry_attrib, nsmap={None: CALS_NS})
    parser = CalsParser(BaseBuilder(), cals_ns=CALS_NS)
    parser.setup_table()
    state = parser._state
    state.next_row()
    state.row = state.table.rows[state.row_pos]
    state.next_col()
    state = parser.parse_cals_entry(cals_entry)
    cell = state.table[(1, 1)]
    assert cell.styles == styles
    assert cell.nature == nature


@pytest.mark.parametrize(
    "attrib, size",
    [
        ({"namest": "1"}, (1, 1)),
        ({"nameend": "2"}, (2, 1)),
        ({"namest": "1", "nameend": "3"}, (3, 1)),
        ({"morerows": "2"}, (1, 3)),
        ({"namest": "3", "nameend": "5", "morerows": "1"}, (3, 2)),
    ],
)
def test_parse_cals_entry__spanning(attrib, size):
    # --without namespaces
    cals_entry = etree.Element("entry", attrib=attrib)
    parser = CalsParser(BaseBuilder())
    parser.setup_table()
    state = parser._state
    state.next_row()
    state.row = state.table.rows[state.row_pos]
    state.next_col()
    state = parser.parse_cals_entry(cals_entry)
    cell = state.table[(1, 1)]
    assert cell.size == size


@pytest.mark.parametrize(
    "attrib, styles, nature",
    [
        ({"colnum": "2"}, {}, None),
        ({"colsep": "0"}, {"border-right": BORDER_NONE}, None),
        ({"colsep": "1"}, {"border-right": BORDER_SOLID}, None),
        ({"rowsep": "0"}, {"border-bottom": BORDER_NONE}, None),
        ({"rowsep": "1"}, {"border-bottom": BORDER_SOLID}, None),
        ({"colwidth": "5mm"}, {"width": "5mm"}, None),
        ({"align": "left"}, {"align": "left"}, None),
        ({"align": "right"}, {"align": "right"}, None),
        ({"align": "center"}, {"align": "center"}, None),
        ({"align": "justify"}, {"align": "justify"}, None),
        ({"align": "char"}, {"align": "left"}, None),
    ],
)
def test_parse_cals_colspec(attrib, styles, nature):
    # --without namespaces
    cals_colspec = etree.Element("colspec", attrib=attrib)
    parser = CalsParser(BaseBuilder())
    parser.setup_table()
    state = parser._state
    state.next_col()
    state = parser.parse_cals_colspec(cals_colspec)
    col_pos = int(attrib.get("colnum", 1))
    col = state.table.cols[col_pos]
    assert col.styles == styles
    assert col.nature == nature

    # --with default namespaces
    cals_colspec_attrib = {cals(k): v for k, v in attrib.items()}
    cals_colspec = etree.Element(cals("colspec"), attrib=cals_colspec_attrib, nsmap={None: CALS_NS})
    parser = CalsParser(BaseBuilder(), cals_ns=CALS_NS)
    parser.setup_table()
    state = parser._state
    state.next_col()
    state = parser.parse_cals_colspec(cals_colspec)
    col_pos = int(attrib.get("colnum", 1))
    col = state.table.cols[col_pos]
    assert col.styles == styles
    assert col.nature == nature
