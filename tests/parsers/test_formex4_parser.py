# coding: utf-8
from __future__ import print_function

import textwrap

import pytest
from lxml import etree
from lxml.builder import ElementMaker

from benker.builders.base_builder import BaseBuilder
from benker.parsers.formex4 import BORDER_NONE
from benker.parsers.formex4 import BORDER_SOLID
from benker.parsers.formex4 import Formex4Parser
from benker.parsers.formex4 import get_frame_styles
from benker.schemas import CALS_NS
from benker.schemas import CALS_PREFIX
from benker.schemas import FORMEX_NS
from benker.schemas import FORMEX_PREFIX


def test_ns_map__default():
    builder = BaseBuilder()
    parser = Formex4Parser(builder)
    assert parser.ns_map == {FORMEX_PREFIX: FORMEX_NS, CALS_PREFIX: CALS_NS}


@pytest.mark.parametrize("formex_prefix", [None, "formex"])
@pytest.mark.parametrize("formex_ns", [None, "http://server.com/formex"])
@pytest.mark.parametrize("cals_prefix", [None, "cals"])
@pytest.mark.parametrize("cals_ns", [None, "http://server.com/cals"])
def test_ns_map(formex_prefix, formex_ns, cals_prefix, cals_ns):
    expected = {}
    if formex_prefix and formex_ns:
        expected[formex_prefix] = formex_ns
    if cals_prefix and cals_ns:
        expected[cals_prefix] = cals_ns
    builder = BaseBuilder()
    parser = Formex4Parser(
        builder, formex_ns=formex_ns, formex_prefix=formex_prefix, cals_ns=cals_ns, cals_prefix=cals_prefix
    )
    assert expected == parser.ns_map


@pytest.mark.parametrize("formex_prefix", [None, "formex"])
@pytest.mark.parametrize("formex_ns", [None, "http://server.com/formex"])
def test_get_formex_qname(formex_prefix, formex_ns):
    name = "dummy"
    prefix = "{" + formex_ns + "}" if formex_prefix and formex_ns else ""
    expected = prefix + name
    builder = BaseBuilder()
    parser = Formex4Parser(builder, formex_ns=formex_ns, formex_prefix=formex_prefix)
    assert expected == parser.get_formex_qname(name)


@pytest.mark.parametrize("cals_prefix", [None, "cals"])
@pytest.mark.parametrize("cals_ns", [None, "http://server.com/cals"])
def test_get_cals_qname(cals_prefix, cals_ns):
    name = "dummy"
    prefix = "{" + cals_ns + "}" if cals_prefix and cals_ns else ""
    expected = prefix + name
    builder = BaseBuilder()
    parser = Formex4Parser(builder, cals_ns=cals_ns, cals_prefix=cals_prefix)
    assert expected == parser.get_cals_qname(name)


@pytest.mark.parametrize("formex_prefix", [None, "formex"])
@pytest.mark.parametrize("formex_ns", [None, "http://server.com/formex"])
def test_get_formex_name(formex_prefix, formex_ns):
    name = "dummy"
    prefix = formex_prefix + ":" if formex_prefix and formex_ns else ""
    expected = prefix + name
    builder = BaseBuilder()
    parser = Formex4Parser(builder, formex_ns=formex_ns, formex_prefix=formex_prefix)
    assert expected == parser.get_formex_name(name)


@pytest.mark.parametrize("cals_prefix", [None, "cals"])
@pytest.mark.parametrize("cals_ns", [None, "http://server.com/cals"])
def test_get_cals_name(cals_prefix, cals_ns):
    name = "dummy"
    prefix = cals_prefix + ":" if cals_prefix and cals_ns else ""
    expected = prefix + name
    builder = BaseBuilder()
    parser = Formex4Parser(builder, cals_ns=cals_ns, cals_prefix=cals_prefix)
    assert expected == parser.get_cals_name(name)


class StrBuilder(BaseBuilder):
    """
    Create a ``table`` element with the string representation of the table object.
    """

    def generate_table_tree(self, table):
        element = etree.Element("table")
        element.text = str(table)
        return element


def test_transform_tables():
    E = ElementMaker(namespace=FORMEX_NS, nsmap={FORMEX_PREFIX: FORMEX_NS})
    tbl_elem = E.TBL(E.CORPUS(
        E.ROW(E.CELL("A1"), E.CELL("B1")),
        E.ROW(E.CELL("A2", COLSPAN="2"))  # fixme: fmx namespace missing
    ))
    tree = E.FORMEX(tbl_elem)
    builder = StrBuilder()
    parser = Formex4Parser(builder)
    parser.transform_tables(tree)
    str_table = tree.xpath("table")[0].text
    print("str_table:")
    print(str_table)
    assert str_table == textwrap.dedent("""\
    +-----------+-----------+
    |    A1     |    B1     |
    +-----------+-----------+
    |    A2                 |
    +-----------+-----------+""")


def test_transform_tables__no_namespace():
    E = ElementMaker()
    tbl_elem = E.TBL(E.CORPUS(
        E.ROW(E.CELL("A1"), E.CELL("B1", ROWSPAN="2")),
        E.ROW(E.CELL("A2"))
    ))
    tree = E.FORMEX(tbl_elem)
    builder = StrBuilder()
    parser = Formex4Parser(builder, formex_ns="")
    parser.transform_tables(tree)
    str_table = tree.xpath("table")[0].text
    print("str_table:")
    print(str_table)
    assert str_table == textwrap.dedent("""\
    +-----------+-----------+
    |    A1     |    B1     |
    +-----------+           +
    |    A2     |           |
    +-----------+-----------+""")


@pytest.mark.parametrize(
    "frame, expected",
    [
        (None, {}),
        (
            "all",
            {
                "border-bottom": BORDER_SOLID,
                "border-left": BORDER_SOLID,
                "border-right": BORDER_SOLID,
                "border-top": BORDER_SOLID,
            },
        ),
        (
            "topbot",
            {
                "border-bottom": BORDER_SOLID,
                "border-left": BORDER_NONE,
                "border-right": BORDER_NONE,
                "border-top": BORDER_SOLID,
            },
        ),
        (
            "sides",
            {
                "border-bottom": BORDER_NONE,
                "border-left": BORDER_SOLID,
                "border-right": BORDER_SOLID,
                "border-top": BORDER_NONE,
            },
        ),
        (
            "top",
            {
                "border-bottom": BORDER_NONE,
                "border-left": BORDER_NONE,
                "border-right": BORDER_NONE,
                "border-top": BORDER_SOLID,
            },
        ),
        (
            "bottom",
            {
                "border-bottom": BORDER_SOLID,
                "border-left": BORDER_NONE,
                "border-right": BORDER_NONE,
                "border-top": BORDER_NONE,
            },
        ),
    ],
)
def test_get_frame_styles(frame, expected):
    actual = get_frame_styles(frame)
    assert actual == expected


@pytest.mark.parametrize(
    "attrib, styles",
    [
        ({"COLS": "1"}, {}),
        ({"NO.SEQ": "0001", "COLS": "1", "PAGE.SIZE": "DOUBLE.LANDSCAPE"}, {"x-sect-orient": "landscape"}),
        (
            {"NO.SEQ": "0001", "CLASS": "GEN", "COLS": "1", "PAGE.SIZE": "SINGLE.PORTRAIT"},
            {"tabstyle": "GEN", "x-sect-orient": "portrait"},
        ),
        (
            {"NO.SEQ": "0001", "CLASS": "SCHEDULE", "COLS": "1", "PAGE.SIZE": "SINGLE.LANDSCAPE"},
            {"tabstyle": "SCHEDULE", "x-sect-orient": "landscape"},
        ),
        (
            {"NO.SEQ": "0001", "CLASS": "RECAP", "COLS": "1", "PAGE.SIZE": "DOUBLE.PORTRAIT"},
            {"tabstyle": "RECAP", "x-sect-orient": "portrait"},
        ),
        (
            {"frame": "all"},
            {
                "border-bottom": BORDER_SOLID,
                "border-left": BORDER_SOLID,
                "border-right": BORDER_SOLID,
                "border-top": BORDER_SOLID,
            },
        ),
        (
            {"colsep": "0"},
            {"x-cell-border-right": BORDER_NONE},
        ),
        (
            {"colsep": "1"},
            {"x-cell-border-right": BORDER_SOLID},
        ),
        (
            {"rowsep": "0"},
            {"x-cell-border-bottom": BORDER_NONE},
        ),
        (
            {"rowsep": "1"},
            {"x-cell-border-bottom": BORDER_SOLID},
        ),
        (
            {"orient": "land"},
            {"x-sect-orient": "landscape"},
        ),
        (
            {"orient": "port"},
            {"x-sect-orient": "portrait"},
        ),
        (
            {"pgwide": "1"},
            {"x-sect-cols": "1"},
        ),
        (
            {"pgwide": "0"},
            {"x-sect-cols": "2"},
        ),
        (
            {"bgcolor": "#FF8000"},
            {"background-color": "#FF8000"},
        ),
    ],
)
def test_parse_tbl(attrib, styles):
    E = ElementMaker()
    tbl_elem = etree.Element("TBL", attrib=attrib)
    parser = Formex4Parser(BaseBuilder(), formex_ns="", cals_ns="")
    state = parser.parse_tbl(tbl_elem)
    table = state.table
    assert table.styles == styles


def test_parse_title():
    assert 0


def test_parse_gr_seq():
    assert 0


def test_parse_gr_notes():
    assert 0


def test_parse_ti_blk():
    assert 0


def test_parse_sti_blk():
    assert 0


def test_parse_row():
    assert 0


@pytest.mark.parametrize(
    "attrib, styles, nature, size",
    [
        ({}, {}, None, (1, 1)),
        ({"COLSPAN": "1"}, {}, None, (1, 1)),
        ({"COLSPAN": "2"}, {}, None, (2, 1)),
        ({"ROWSPAN": "1"}, {}, None, (1, 1)),
        ({"ROWSPAN": "2"}, {}, None, (1, 2)),
        ({"TYPE": "ALIAS"}, {}, "header", (1, 1)),
        ({"TYPE": "HEADER"}, {}, "header", (1, 1)),
        ({"TYPE": "NORMAL"}, {}, "body", (1, 1)),
        ({"TYPE": "NOTCOL"}, {}, "body", (1, 1)),
        ({"TYPE": "TOTAL"}, {}, "footer", (1, 1)),
    ])
def test_parse_cell(attrib, styles, nature, size):
    E = ElementMaker()
    cell_elem = etree.Element("CELL", attrib=attrib)
    row_elem = E.ROW(cell_elem)
    tbl_elem = E.TBL(row_elem)
    parser = Formex4Parser(BaseBuilder(), formex_ns="", cals_ns="")
    state = parser.parse_tbl(tbl_elem)
    state.next_row()
    state.row = state.table.rows[state.row_pos]
    state.next_col()
    state = parser.parse_cell(cell_elem)
    table = state.table
    cell = table[(1, 1)]
    assert cell.styles == styles
    assert cell.nature == nature
    assert cell.size == size


def test_parse_colspec():
    assert 0
