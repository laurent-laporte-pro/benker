# coding: utf-8
import pytest
from lxml import etree

from benker.builders.cals import CalsBuilder
from benker.cell import Cell
from benker.table import Table

TEST_DATA__WITH_SEP = [

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
]


@pytest.mark.parametrize('cell_styles, expected', TEST_DATA__WITH_SEP)
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
    builder._table = Table([cell_x1_y1, cell_x2_y1, cell_x1_y2, cell_x2_y2])

    # -- build the cell
    builder.build_cell(row_elem, cell_x1_y1)

    # -- check the '<entry>' attributes
    entry_elem = row_elem[0]  # type: etree._Element
    assert entry_elem.tag == u"entry"
    assert entry_elem.attrib == expected
    assert entry_elem[0] == p_elem


TEST_DATA__WITHOUT_SEP = [

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
]


@pytest.mark.parametrize('cell_styles, expected', TEST_DATA__WITHOUT_SEP)
def test_build_cell__without_sep(cell_styles, expected):
    # .. note::
    #
    #   CALS default value for @colsep and @rowsep is "1"
    #   For testing, we set it to "0" by default.

    builder = CalsBuilder()
    builder._table_colsep = u"0"
    builder._table_rowsep = u"0"

    # -- create a minimal <row> element
    row_elem = etree.XML("<row/>")

    # -- setup a minimal cell
    p_elem = etree.XML("<p>text</p>")
    cell_x1_y1 = Cell([p_elem], x=1, y=1, styles=cell_styles)
    cell_x2_y1 = Cell([p_elem], x=2, y=1, styles=cell_styles)
    cell_x1_y2 = Cell([p_elem], x=1, y=2, styles=cell_styles)
    cell_x2_y2 = Cell([p_elem], x=2, y=2, styles=cell_styles)
    builder._table = Table([cell_x1_y1, cell_x2_y1, cell_x1_y2, cell_x2_y2])

    # -- build the cell
    builder.build_cell(row_elem, cell_x1_y1)

    # -- check the '<entry>' attributes
    entry_elem = row_elem[0]  # type: etree._Element
    assert entry_elem.tag == u"entry"
    assert entry_elem.attrib == expected
    assert entry_elem[0] == p_elem


TEST_DATA__ALIGN = [

    pytest.param(
        {'vertical-align': 'top', 'align': 'left'},
        {'valign': 'top', 'align': 'left'},
        id="style_vertical-align_top_align_left"),

    pytest.param(
        {'vertical-align': 'bottom', 'align': 'right'},
        {'valign': 'bottom', 'align': 'right'},
        id="style_vertical-align_bottom_align_right"),

    pytest.param(
        {'vertical-align': 'middle', 'align': 'center'},
        {'valign': 'middle', 'align': 'center'},
        id="style_vertical-align_middle_align_center"),

    pytest.param(
        {'vertical-align': 'w-both', 'align': 'justify'},
        {'valign': 'bottom', 'align': 'justify'},
        id="style_vertical-align_both_align_justify"),
]


@pytest.mark.parametrize('cell_styles, expected', TEST_DATA__ALIGN)
def test_build_cell__align(cell_styles, expected):
    builder = CalsBuilder()

    # -- create a minimal <row> element
    row_elem = etree.XML("<row/>")

    # -- setup a minimal cell
    p_elem = etree.XML("<p>text</p>")
    cell = Cell([p_elem], x=1, y=1, styles=cell_styles)
    builder._table = Table([cell])

    # -- build the cell
    builder.build_cell(row_elem, cell)

    # -- check the '<entry>' attributes
    entry_elem = row_elem[0]  # type: etree._Element
    assert entry_elem.tag == u"entry"

    # we don't want to check @colsep/@rowsep here
    actual = dict(entry_elem.attrib)
    actual.pop("colsep", None)
    actual.pop("rowsep", None)

    assert actual == expected
    assert entry_elem[0] == p_elem
