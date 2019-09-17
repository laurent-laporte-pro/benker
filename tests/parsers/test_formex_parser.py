# coding: utf-8
import textwrap
import unittest

import pytest
from lxml import etree
from lxml.builder import ElementMaker

from benker.builders.base_builder import BaseBuilder
from benker.parsers.formex import BORDER_NONE
from benker.parsers.formex import BORDER_SOLID
from benker.parsers.formex import FormexParser
from benker.parsers.formex import get_frame_styles
from benker.schemas import CALS_NS
from benker.schemas import CALS_PREFIX
from benker.schemas import FORMEX_NS
from benker.schemas import FORMEX_PREFIX


class TestFormexParser(unittest.TestCase):
    def setUp(self):
        self.builder = BaseBuilder()

    def test_builder_attached(self):
        parser = FormexParser(self.builder)
        assert parser.builder is self.builder

    def test_ns_map(self):
        parser = FormexParser(self.builder)
        assert parser.ns_map == {}
        parser = FormexParser(self.builder, formex_ns="http://opoce", cals_prefix=CALS_PREFIX, cals_ns=CALS_NS)
        assert parser.ns_map == {None: "http://opoce", CALS_PREFIX: CALS_NS}
        parser = FormexParser(self.builder, formex_prefix="fmx", formex_ns="http://opoce")
        assert parser.ns_map == {"fmx": "http://opoce"}

    def test_invalid_ns_map(self):
        with self.assertRaises(ValueError):
            FormexParser(self.builder, formex_prefix="fmx")
        with self.assertRaises(ValueError):
            FormexParser(self.builder, cals_prefix="fmx")


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
    parser = FormexParser(builder, formex_ns="")
    parser.transform_tables(tree)
    str_table = tree.xpath("//table")[0].text
    # print("str_table:")
    # print(str_table)
    # fmt: off
    assert str_table == textwrap.dedent("""\
    +-----------+-----------+
    |    A1     |    B1     |
    +-----------|           |
    |    A2     |           |
    +-----------+-----------+""")
    # fmt: on


def test_transform_tables__with_header():
    E = ElementMaker()
    fmx_tbl = E.TBL(E.CORPUS(
        E.ROW(E.CELL("Header 1", TYPE="HEADER"), E.CELL("Header 2", TYPE="HEADER"), TYPE="HEADER"),
        E.ROW(E.CELL("A1"), E.CELL("B1")),
        E.ROW(E.CELL("A2"), E.CELL("B2")),
        E.ROW(E.CELL("A3"), E.CELL("B3")),
    ))
    tree = E.FORMEX(fmx_tbl)
    builder = StrBuilder()
    parser = FormexParser(builder, formex_ns="")
    parser.transform_tables(tree)
    str_table = tree.xpath("//table")[0].text
    # print("str_table:")
    # print(str_table)
    # fmt: off
    assert str_table == textwrap.dedent("""\
    +-----------+-----------+
    | Header 1  | Header 2  |
    +-----------+-----------+
    |    A1     |    B1     |
    +-----------+-----------+
    |    A2     |    B2     |
    +-----------+-----------+
    |    A3     |    B3     |
    +-----------+-----------+""")
    # fmt: on


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
    parser = FormexParser(builder, formex_prefix=FORMEX_PREFIX, formex_ns=FORMEX_NS)
    parser.transform_tables(tree)
    str_table = tree.xpath("//table")[0].text
    # print("str_table:")
    # print(str_table)
    # fmt: off
    assert str_table == textwrap.dedent("""\
    +-----------+-----------+
    |    A1     |    B1     |
    +-----------------------+
    |    A2                 |
    +-----------------------+""")
    # fmt: on


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
    parser = FormexParser(BaseBuilder())
    state = parser.parse_corpus(fmx_corpus)
    table = state.table
    assert table.styles == styles


@pytest.mark.parametrize(
    "attrib, styles, nature",
    [
        ({}, {}, "body"),
        ({"TYPE": "ALIAS"}, {"rowstyle": "ROW-ALIAS"}, "header"),
        ({"TYPE": "HEADER"}, {"rowstyle": "ROW-HEADER"}, "header"),
        ({"TYPE": "NORMAL"}, {"rowstyle": "ROW-NORMAL"}, "body"),
        ({"TYPE": "NOTCOL"}, {"rowstyle": "ROW-NOTCOL"}, "body"),
        ({"TYPE": "TOTAL"}, {"rowstyle": "ROW-TOTAL"}, "body"),
        ({"TYPE": "NORMAL", "rowstyle": "ROW-TOTAL"}, {"rowstyle": "ROW-TOTAL"}, "body"),
        ({"valign": "top"}, {"valign": "top"}, "body"),
        ({"valign": "middle"}, {"valign": "middle"}, "body"),
        ({"valign": "bottom"}, {"valign": "bottom"}, "body"),
        ({"rowsep": "0"}, {"border-bottom": BORDER_NONE}, "body"),
        ({"rowsep": "1"}, {"border-bottom": BORDER_SOLID}, "body"),
    ],
)
def test_parse_row(attrib, styles, nature):
    E = ElementMaker()
    fmx_row = E.ROW(**attrib)
    parser = FormexParser(BaseBuilder())
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
        ({}, {"rowstyle": "ROW-level2"}, "body"),
        ({"TYPE": "ALIAS"}, {"rowstyle": "ROW-ALIAS-level2"}, "header"),
        ({"TYPE": "HEADER"}, {"rowstyle": "ROW-HEADER-level2"}, "header"),
        ({"TYPE": "NORMAL"}, {"rowstyle": "ROW-NORMAL-level2"}, "body"),
        ({"TYPE": "NOTCOL"}, {"rowstyle": "ROW-NOTCOL-level2"}, "body"),
        ({"TYPE": "TOTAL"}, {"rowstyle": "ROW-TOTAL-level2"}, "body"),
    ],
)
def test_parse_row__in_blk_level2(attrib, styles, nature):
    E = ElementMaker()
    fmx_row = E.ROW(**attrib)
    E.BLK(E.BLK(fmx_row))
    parser = FormexParser(BaseBuilder())
    state = parser.setup_table()
    state.next_row()
    state.row = state.table.rows[state.row_pos]
    state = parser.parse_row(fmx_row)
    row = state.row
    assert row.styles == styles
    assert row.nature == nature


def test_parse_row__ti_blk_level1():
    fmx_blk = etree.Element("BLK")
    fmx_ti_blk = etree.XML("""<TI.BLK COL.START="1" COL.END="2"><P>paragraph</P></TI.BLK>""")
    fmx_blk.append(fmx_ti_blk)
    parser = FormexParser(BaseBuilder())
    state = parser.setup_table()
    state.next_row()
    state = parser.parse_ti_blk(fmx_ti_blk)
    row = state.row
    assert row.styles == {"rowstyle": "TI.BLK-level1"}
    assert row.nature == "body"
    table = state.table
    cell = table[(1, 1)]
    assert cell.styles == {}
    assert cell.nature == "body"
    assert cell.width == 2
    assert cell.height == 1
    assert etree.tounicode(cell.content[0]) == "<P>paragraph</P>"


def test_parse_row__ti_blk_level2():
    fmx_blk = etree.Element("BLK")
    fmx_blk = etree.SubElement(fmx_blk, "BLK")
    fmx_ti_blk = etree.XML("""<TI.BLK><IE/></TI.BLK>""")
    fmx_blk.append(fmx_ti_blk)
    parser = FormexParser(BaseBuilder())
    state = parser.setup_table()
    state.next_row()
    state = parser.parse_ti_blk(fmx_ti_blk)
    row = state.row
    assert row.styles == {"rowstyle": "TI.BLK-level2"}
    assert row.nature == "body"
    table = state.table
    cell = table[(1, 1)]
    assert cell.styles == {}
    assert cell.nature == "body"
    assert cell.width == 1
    assert cell.height == 1
    assert cell.content == ""


def test_parse_row__ti_blk_level2__with_namespace():
    def fmx(name):
        return etree.QName(FORMEX_NS, name).text

    BLK = fmx("BLK")
    TI_BLK = fmx("TI.BLK")
    IE = fmx("IE")

    fmx_blk1 = etree.Element(BLK, nsmap={None: FORMEX_NS})
    fmx_blk2 = etree.SubElement(fmx_blk1, BLK, nsmap={None: FORMEX_NS})
    fmx_ti_blk = etree.SubElement(fmx_blk2, TI_BLK, nsmap={None: FORMEX_NS})
    etree.SubElement(fmx_ti_blk, IE, nsmap={None: FORMEX_NS})

    parser = FormexParser(BaseBuilder(), formex_ns=FORMEX_NS, cals_prefix=CALS_PREFIX, cals_ns=CALS_NS)
    state = parser.setup_table()
    state.next_row()
    state = parser.parse_ti_blk(fmx_ti_blk)

    row = state.row
    assert row.styles == {"rowstyle": "TI.BLK-level2"}
    assert row.nature == "body"
    table = state.table
    cell = table[(1, 1)]
    assert cell.styles == {}
    assert cell.nature == "body"
    assert cell.width == 1
    assert cell.height == 1
    assert cell.content == ""


def test_parse_row__sti_blk_level1():
    fmx_blk = etree.Element("BLK")
    fmx_sti_blk = etree.XML("""<STI.BLK COL.START="2" COL.END="2">text</STI.BLK>""")
    fmx_blk.append(fmx_sti_blk)
    parser = FormexParser(BaseBuilder())
    state = parser.setup_table()
    state.next_row()
    state = parser.parse_sti_blk(fmx_sti_blk)
    row = state.row
    assert row.styles == {"rowstyle": "STI.BLK-level1"}
    assert row.nature == "body"
    table = state.table
    cell1 = table[(1, 1)]
    assert cell1.content is None
    cell2 = table[(2, 1)]
    assert cell2.styles == {}
    assert cell2.nature == "body"
    assert cell2.width == 1
    assert cell2.height == 1
    assert cell2.content[0] == "text"


def test_parse_gr_notes():
    fmx_gr_notes = etree.XML(
        """<GR.NOTES>
      <TITLE><TI><P>GR.NOTES Title</P></TI></TITLE>
      <NOTE NOTE.ID="N0001"><P>Table note</P></NOTE>
    </GR.NOTES>"""
    )
    parser = FormexParser(BaseBuilder())
    state = parser.setup_table()
    # -- insert at least one ROW for testing
    state.next_row()
    state.row = state.table.rows[state.row_pos]
    state.row.insert_cell("text1")
    state.row.insert_cell("text2")
    state.row.insert_cell("text3")
    # -- then add the footer
    state.next_row()
    state = parser.parse_gr_notes(fmx_gr_notes)
    row = state.row
    assert row.styles == {}
    assert row.nature == "footer"
    # -- the cell is in the row 2
    cell = state.table[(1, 2)]
    assert cell.styles == {}
    assert cell.nature == "footer"
    assert cell.width == 3
    assert cell.height == 1
    content = [node for node in cell.content if isinstance(node, etree._Element)]
    assert etree.tounicode(content[0], with_tail=False) == "<TITLE><TI><P>GR.NOTES Title</P></TI></TITLE>"
    assert etree.tounicode(content[1], with_tail=False) == '<NOTE NOTE.ID="N0001"><P>Table note</P></NOTE>'


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
    parser = FormexParser(BaseBuilder())
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
    parser = FormexParser(BaseBuilder())
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


def test_parse_colspec():
    E = ElementMaker()
    cals_colspec = E.colspec(
        colnum="1", colname="c1", colwidth="70mm", colsep="0", rowsep="1", align="char", char=",", charoff="50"
    )
    parser = FormexParser(BaseBuilder())
    state = parser.setup_table()
    parser.parse_colspec(cals_colspec)
    table = state.table
    col = table.cols[1]
    assert col.styles == {'align': 'left', 'width': '70mm', 'border-bottom': 'solid 1pt black', 'border-right': 'none'}
