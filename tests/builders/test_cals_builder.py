# coding: utf-8
from __future__ import print_function

import sys
import unittest

import pytest
import xmldiff.main
from lxml import etree

from benker.builders.cals import CalsBuilder
from benker.cell import Cell
from benker.table import Table

# noinspection PyProtectedMember
ElementType = etree._Element


class TestCalsBuilder(unittest.TestCase):
    def test_init(self):
        builder = CalsBuilder()
        assert builder.cals_ns.uri is None
        assert builder.cals_ns.prefix is None
        assert builder.ns_map == {}
        assert builder.width_unit == "mm"
        assert builder.table_in_tgroup is False
        assert builder.tgroup_sorting == {"header": 0, "footer": 1, "body": 2}

    def test_option_cals_ns(self):
        builder = CalsBuilder(cals_ns="http://cals")
        assert builder.cals_ns.uri == "http://cals"
        assert builder.ns_map == {None: "http://cals"}

    def test_option_cals_prefix(self):
        builder = CalsBuilder(cals_ns="http://cals", cals_prefix="cals")
        assert builder.cals_ns.prefix == "cals"
        assert builder.ns_map == {"cals": "http://cals"}

    def test_option_cals_prefix__without_ns(self):
        with self.assertRaises(ValueError):
            CalsBuilder(cals_prefix="cals")

    def test_option_width_unit(self):
        builder = CalsBuilder(width_unit="pt")
        assert builder.width_unit == "pt"

    def test_option_table_in_tgroup(self):
        builder = CalsBuilder(table_in_tgroup=True)
        assert builder.table_in_tgroup is True

    def test_option_tgroup_sorting(self):
        builder = CalsBuilder(tgroup_sorting=["header", "body", "footer"])
        assert builder.tgroup_sorting == {"header": 0, "body": 1, "footer": 2}

    def test_option_tgroup_sorting__missing(self):
        with pytest.raises(ValueError):
            CalsBuilder(tgroup_sorting=["header", "body"])


def test_setup_table():
    builder = CalsBuilder()
    table = Table()
    result = builder.setup_table(table)
    assert result == table


TEST_DATA__WITH_SEP = [
    # fmt: off
    pytest.param(
        {},
        {},
        id="no_style"),

    pytest.param(
        {'border-top': 'double 1.0pt #FFFFFF',
         'border-right': 'dotted 2.0pt #FF0000',
         'border-bottom': 'dashed 3.0pt #00FF00',
         'border-left': 'outset 4.0pt #0000FF'},
        {'colsep': '1', 'rowsep': '1'},
        id="style_border-all"),

    pytest.param(
        {'border-top': 'double 1.0pt #FFFFFF'},
        {},
        id="style_border-top"),

    pytest.param(
        {'border-right': 'double 1.0pt #FFFFFF'},
        {'colsep': '1'},
        id="style_border-right"),

    pytest.param(
        {'border-bottom': 'double 1.0pt #FFFFFF'},
        {'rowsep': '1'},
        id="style_border-bottom"),

    pytest.param(
        {'border-left': 'double 1.0pt #FFFFFF'},
        {},
        id="style_border-left"),
    # fmt: on
]


@pytest.mark.parametrize("cell_styles, expected", TEST_DATA__WITH_SEP)
def test_build_cell__with_sep(cell_styles, expected):
    # .. note::
    #
    #   CALS default value for @colsep and @rowsep is "1".

    builder = CalsBuilder()

    # -- create a minimal <row> element
    row_elem = etree.XML("<row/>")

    # -- setup a minimal cell
    p_elem = etree.XML("<p>text</p>")
    cell_x1_y1 = Cell([p_elem], x=1, y=1, styles=cell_styles)
    cell_x2_y1 = Cell([p_elem], x=2, y=1, styles=cell_styles)
    cell_x1_y2 = Cell([p_elem], x=1, y=2, styles=cell_styles)
    cell_x2_y2 = Cell([p_elem], x=2, y=2, styles=cell_styles)
    builder.setup_table(Table([cell_x1_y1, cell_x2_y1, cell_x1_y2, cell_x2_y2]))

    # -- build the cell
    builder.build_cell(row_elem, cell_x1_y1)

    # -- check the '<entry>' attributes
    entry_elem = row_elem[0]  # type: ElementType
    assert entry_elem.tag == u"entry"
    assert entry_elem.attrib == expected
    assert entry_elem[0] == p_elem


TEST_DATA__WITHOUT_SEP = [
    # fmt: off
    pytest.param(
        {},
        {},
        id="no_style"),

    pytest.param(
        {'border-top': 'double 1.0pt #FFFFFF',
            'border-right': 'dotted 2.0pt #FF0000',
            'border-bottom': 'dashed 3.0pt #00FF00',
         'border-left': 'outset 4.0pt #0000FF'},
        {'colsep': '1', 'rowsep': '1'},
        id="style_border-all"),

    pytest.param(
        {'border-top': 'double 1.0pt #FFFFFF'},
        {},
        id="style_border-top"),

    pytest.param(
        {'border-right': 'double 1.0pt #FFFFFF'},
        {'colsep': '1'},
        id="style_border-right"),

    pytest.param(
        {'border-bottom': 'double 1.0pt #FFFFFF'},
        {'rowsep': '1'},
        id="style_border-bottom"),

    pytest.param(
        {'border-left': 'double 1.0pt #FFFFFF'},
        {},
        id="style_border-left"),
    # fmt: on
]


@pytest.mark.parametrize("cell_styles, expected", TEST_DATA__WITHOUT_SEP)
def test_build_cell__without_sep(cell_styles, expected):
    # .. note::
    #
    #   CALS default value for @colsep and @rowsep is "1"
    #   For testing, we set it to "0" by default.

    # -- create a minimal <row> element
    row_elem = etree.XML("<row/>")

    # -- setup a minimal cell
    p_elem = etree.XML("<p>text</p>")
    cell_x1_y1 = Cell([p_elem], x=1, y=1, styles=cell_styles)
    cell_x2_y1 = Cell([p_elem], x=2, y=1, styles=cell_styles)
    cell_x1_y2 = Cell([p_elem], x=1, y=2, styles=cell_styles)
    cell_x2_y2 = Cell([p_elem], x=2, y=2, styles=cell_styles)

    # -- build the cell
    builder = CalsBuilder()
    builder.setup_table(Table([cell_x1_y1, cell_x2_y1, cell_x1_y2, cell_x2_y2]))
    builder.build_cell(row_elem, cell_x1_y1)

    # -- check the '<entry>' attributes
    entry_elem = row_elem[0]  # type: ElementType
    assert entry_elem.tag == u"entry"
    assert entry_elem.attrib == expected
    assert entry_elem[0] == p_elem


TEST_DATA__ALIGN = [
    pytest.param(
        {"vertical-align": "top", "align": "left"},
        {"valign": "top", "align": "left"},
        id="style_vertical-align_top_align_left",
    ),
    pytest.param(
        {"vertical-align": "bottom", "align": "right"},
        {"valign": "bottom", "align": "right"},
        id="style_vertical-align_bottom_align_right",
    ),
    pytest.param(
        {"vertical-align": "middle", "align": "center"},
        {"valign": "middle", "align": "center"},
        id="style_vertical-align_middle_align_center",
    ),
    pytest.param(
        {"vertical-align": "w-both", "align": "justify"},
        {"valign": "bottom", "align": "justify"},
        id="style_vertical-align_both_align_justify",
    ),
]


@pytest.mark.parametrize("cell_styles, expected", TEST_DATA__ALIGN)
def test_build_cell__align(cell_styles, expected):
    builder = CalsBuilder()

    # -- create a minimal <row> element
    row_elem = etree.XML("<row/>")

    # -- setup a minimal cell
    p_elem = etree.XML("<p>text</p>")
    cell = Cell([p_elem], x=1, y=1, styles=cell_styles)
    builder.setup_table(Table([cell]))

    # -- build the cell
    builder.build_cell(row_elem, cell)

    # -- check the '<entry>' attributes
    entry_elem = row_elem[0]  # type: ElementType
    assert entry_elem.tag == u"entry"

    # we don't want to check @colsep/@rowsep here
    actual = dict(entry_elem.attrib)
    actual.pop("colsep", None)
    actual.pop("rowsep", None)

    assert actual == expected
    assert entry_elem[0] == p_elem


@pytest.mark.parametrize(
    "tgroup_sorting, expected_tags",
    [
        (None, ["colspec", "thead", "tfoot", "tbody"]),
        (["header", "body", "footer"], ["colspec", "thead", "tbody", "tfoot"]),
        (["header", "footer", "body"], ["colspec", "thead", "tfoot", "tbody"]),
        (["footer", "body", "header"], ["colspec", "tfoot", "tbody", "thead"]),
    ],
)
def test_build_tgroup__tgroup_sorting(tgroup_sorting, expected_tags):
    # -- create a table with different natures
    table = Table()
    row1 = table.rows[1]
    row2 = table.rows[2]
    row3 = table.rows[3]
    row1.nature = "header"
    row2.nature = "body"
    row3.nature = "footer"
    row1.insert_cell("a")
    row2.insert_cell("b")
    row3.insert_cell("c")

    # -- create a builder
    table_elem = etree.Element("table")
    builder = CalsBuilder(tgroup_sorting=tgroup_sorting)
    builder.setup_table(table)
    builder.build_tgroup(table_elem, table)

    # -- check the tgroup children name and order
    actual_tags = [elem.tag for elem in table_elem.xpath("tgroup/*")]
    assert actual_tags == expected_tags


def test_build_table():
    # see: formex-4/samples/jo-compl-2002C_061/C_2002061EN.01000403.xml

    table = Table(
        styles={
            "border-top": "solid",
            "border-bottom": "solid",
            "x-sect-orient": "landscape",
            "x-sect-cols": "1",
            "background-color": "yellow",
            "width": "247",
        }
    )
    table.rows[1].nature = "header"
    table.rows[1].insert_cell(u"Expert group")
    table.rows[1].insert_cell(u"First name and surname of the expert")
    table.rows[2].insert_cell(u"Control of infectious diseases")
    table.rows[2].insert_cell(u"Michael Angelo BORG")
    table.rows[3].insert_cell(u"Information society", height=3)
    table.rows[3].insert_cell(u"Tony HEY")
    table.rows[4].insert_cell(u"José L. ENCARNAÇÃO")
    table.rows[5].insert_cell(u"Berit SVENDSEN")
    table.rows[6].insert_cell(u"Controlled thermonuclear fusion")
    table.rows[6].insert_cell(u"Pekka PIRILÄ")

    builder = CalsBuilder()
    table_elem = builder.build_table(table)

    xml_parser = etree.XMLParser(remove_blank_text=True)

    # fmt: off
    expected = etree.XML(u"""\
    <table frame="topbot" colsep="0" rowsep="0" orient="land" pgwide="1" bgcolor="yellow" width="247.00mm">
      <tgroup cols="2">
        <colspec colnum="1" colname="c1"/>
        <colspec colnum="2" colname="c2"/>
        <thead>
          <row>
            <entry>Expert group</entry>
            <entry>First name and surname of the expert</entry>
          </row>
        </thead>
        <tbody>
          <row>
            <entry>Control of infectious diseases</entry>
            <entry>Michael Angelo BORG</entry>
          </row>
          <row>
            <entry morerows="2">Information society</entry>
            <entry>Tony HEY</entry>
          </row>
          <row>
            <entry>José L. ENCARNAÇÃO</entry>
          </row>
          <row>
            <entry>Berit SVENDSEN</entry>
          </row>
          <row>
            <entry>Controlled thermonuclear fusion</entry>
            <entry>Pekka PIRILÄ</entry>
          </row>
        </tbody>
      </tgroup>
    </table>""", parser=xml_parser)
    # fmt: on

    for elem in table_elem.xpath("//*"):
        elem.text = elem.text or None
    for elem in expected.xpath("//*"):
        elem.text = elem.text or None

    diff_list = xmldiff.main.diff_trees(table_elem, expected)
    if diff_list:
        print(etree.tounicode(table_elem, pretty_print=True, with_tail=False), file=sys.stderr)
        assert diff_list == []
