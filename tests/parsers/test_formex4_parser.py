# coding: utf-8
from __future__ import print_function

import textwrap
import unittest

import pytest
from lxml import etree
from lxml.builder import ElementMaker

from benker.builders.base_builder import BaseBuilder
from benker.parsers.formex4 import BORDER_NONE
from benker.parsers.formex4 import BORDER_SOLID
from benker.parsers.formex4 import Formex4Parser
from benker.parsers.formex4 import get_frame_styles
from benker.schemas import FORMEX_NS, CALS_NS, CALS_PREFIX
from benker.schemas import FORMEX_PREFIX


class TestFormex4Parser(unittest.TestCase):
    def setUp(self):
        self.builder = BaseBuilder()

    def test_builder_attached(self):
        parser = Formex4Parser(self.builder)
        assert parser.builder is self.builder

    def test_ns_map(self):
        parser = Formex4Parser(self.builder)
        assert parser.ns_map == {}
        parser = Formex4Parser(self.builder, formex_ns="http://opoce", cals_prefix=CALS_PREFIX, cals_ns=CALS_NS)
        assert parser.ns_map == {None: "http://opoce", CALS_PREFIX: CALS_NS}
        parser = Formex4Parser(self.builder, formex_prefix="fmx", formex_ns="http://opoce")
        assert parser.ns_map == {"fmx": "http://opoce"}

    def test_invalid_ns_map(self):
        with self.assertRaises(ValueError):
            Formex4Parser(self.builder, formex_prefix="fmx")
        with self.assertRaises(ValueError):
            Formex4Parser(self.builder, cals_prefix="fmx")


class StrBuilder(BaseBuilder):
    """
    Create a ``table`` element with the string representation of the table object.
    """

    def generate_table_tree(self, table):
        element = etree.Element("table")
        element.text = str(table)
        return element


def test_transform_tables__no_namespace():
    E = ElementMaker()
    fmx_tbl = E.TBL(E.CORPUS(E.ROW(E.CELL("A1"), E.CELL("B1", ROWSPAN="2")), E.ROW(E.CELL("A2"))))
    tree = E.FORMEX(fmx_tbl)
    builder = StrBuilder()
    parser = Formex4Parser(builder, formex_ns="")
    parser.transform_tables(tree)
    str_table = tree.xpath("//table")[0].text
    print("str_table:")
    print(str_table)
    # fmt: off
    assert str_table == textwrap.dedent("""\
    +-----------+-----------+
    |    A1     |    B1     |
    +-----------|           |
    |    A2     |           |
    +-----------+-----------+""")


def test_transform_tables__with_namespace():
    E = ElementMaker(namespace=FORMEX_NS, nsmap={FORMEX_PREFIX: FORMEX_NS})
    colspan = etree.QName(FORMEX_NS, "COLSPAN")
    # fmt: off
    tree = E.FORMEX(E.TBL(E.CORPUS(
        E.ROW(E.CELL("A1"), E.CELL("B1")),
        E.ROW(E.CELL("A2", **{colspan.text: "2"}))
    )))
    # fmt: on
    builder = StrBuilder()
    parser = Formex4Parser(builder, formex_prefix=FORMEX_PREFIX, formex_ns=FORMEX_NS)
    parser.transform_tables(tree)
    str_table = tree.xpath("//table")[0].text
    print("str_table:")
    print(str_table)
    # fmt: off
    assert str_table == textwrap.dedent("""\
    +-----------+-----------+
    |    A1     |    B1     |
    +-----------------------+
    |    A2                 |
    +-----------------------+""")


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
    # fmt: off
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
    # fmt: on
)
def test_parse_tbl_corpus(attrib, styles):
    fmx_tbl = etree.Element("TBL", attrib=attrib)
    fmx_corpus = etree.SubElement(fmx_tbl, "CORPUS")
    parser = Formex4Parser(BaseBuilder())
    state = parser.parse_corpus(fmx_corpus)
    table = state.table
    assert table.styles == styles


@pytest.mark.parametrize(
    "attrib, styles, nature",
    [
        ({}, {}, "body"),
        ({"TYPE": "ALIAS"}, {"rowstyle": "ALIAS"}, "header"),
        ({"TYPE": "HEADER"}, {"rowstyle": "HEADER"}, "header"),
        ({"TYPE": "NORMAL"}, {"rowstyle": "NORMAL"}, "body"),
        ({"TYPE": "NOTCOL"}, {"rowstyle": "NOTCOL"}, "body"),
        ({"TYPE": "TOTAL"}, {"rowstyle": "TOTAL"}, "footer"),
    ],
)
def test_parse_row(attrib, styles, nature):
    E = ElementMaker()
    fmx_row = E.ROW(**attrib)
    parser = Formex4Parser(BaseBuilder())
    state = parser.setup_table()
    state.next_row()
    state.row = state.table.rows[state.row_pos]
    state = parser.parse_row(fmx_row)
    row = state.row
    assert row.styles == styles
    assert row.nature == nature


@pytest.mark.parametrize(
    "attrib, styles, nature",
    [
        ({}, {"rowstyle": "level2"}, "body"),
        ({"TYPE": "ALIAS"}, {"rowstyle": "ALIAS-level2"}, "header"),
        ({"TYPE": "HEADER"}, {"rowstyle": "HEADER-level2"}, "header"),
        ({"TYPE": "NORMAL"}, {"rowstyle": "NORMAL-level2"}, "body"),
        ({"TYPE": "NOTCOL"}, {"rowstyle": "NOTCOL-level2"}, "body"),
        ({"TYPE": "TOTAL"}, {"rowstyle": "TOTAL-level2"}, "footer"),
    ],
)
def test_parse_row__in_blk_level2(attrib, styles, nature):
    E = ElementMaker()
    fmx_row = E.ROW(**attrib)
    fmx_blk = E.BLK(E.BLK(fmx_row))
    parser = Formex4Parser(BaseBuilder())
    state = parser.setup_table()
    state.next_row()
    state.row = state.table.rows[state.row_pos]
    state = parser.parse_row(fmx_row)
    row = state.row
    assert row.styles == styles
    assert row.nature == nature


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
    ],
)
def test_parse_cell(attrib, styles, nature, size):
    E = ElementMaker()
    fmx_cell = E.CELL(**attrib)
    parser = Formex4Parser(BaseBuilder())
    state = parser.setup_table()
    state.next_row()
    state.row = state.table.rows[state.row_pos]
    parser.parse_cell(fmx_cell)
    table = state.table
    cell = table[(1, 1)]
    assert cell.styles == styles
    assert cell.nature == nature
    assert cell.size == size


def test_parse_cell__with_cals():
    E = ElementMaker()
    fmx_cell = E.CELL(colsep="1", rowsep="1", namest="c1", nameend="c3", bgcolor="#00007f", morerows="1")
    parser = Formex4Parser(BaseBuilder())
    state = parser.setup_table()
    state.next_row()
    state.row = state.table.rows[state.row_pos]
    parser.parse_cell(fmx_cell)
    table = state.table
    cell = table[(1, 1)]
    assert cell.styles == {
        'background-color': '#00007f',
        'x-cell-border-bottom': 'solid 1pt black',
        'x-cell-border-right': 'solid 1pt black',
    }
    assert cell.nature is None
    assert cell.size == (3, 2)
