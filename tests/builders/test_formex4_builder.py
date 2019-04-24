# coding: utf-8
from __future__ import print_function

import sys

import pytest
import xmldiff.main
from lxml import etree
from lxml.builder import E

from benker.builders.formex4 import Formex4Builder
from benker.cell import Cell
from benker.table import Table

TBL = E.TBL
ROW = E.ROW
P = E.P


@pytest.mark.parametrize('kwargs, expected', [
    ({}, {'COL': u"1"}),
    ({'width': 2}, {'COL': u"1", 'COLSPAN': u"2"}),
    ({'height': 2}, {'COL': u"1", 'ROWSPAN': u"2"}),
    ({'nature': 'body'}, {'COL': u"1"}),
    ({'nature': 'head'}, {'COL': u"1", 'TYPE': 'HEADER'}),
    ({'nature': 'foot'}, {'COL': u"1", 'TYPE': 'TOTAL'}),
])
def test_build_cell__body(kwargs, expected):
    builder = Formex4Builder()

    p_elem = P(u"text")
    cell_x1_y1 = Cell([p_elem], x=1, y=1, **kwargs)
    table = Table([cell_x1_y1])
    builder._table = table

    # -- build the cell
    row_elem = ROW()
    row_y1 = next(iter(table.rows))
    builder.build_cell(row_elem, cell_x1_y1, row_y1)

    # -- check the '<CELL>' attributes
    entry_elem = row_elem[0]  # type: etree._Element
    assert entry_elem.tag == u"CELL"
    assert entry_elem.attrib == expected
    assert entry_elem[0] == p_elem


@pytest.mark.parametrize('kwargs, expected', [
    ({'nature': 'body'}, {'COL': u"1", 'TYPE': 'NORMAL'}),
    ({'nature': 'head'}, {'COL': u"1"}),
    ({'nature': 'foot'}, {'COL': u"1", 'TYPE': 'TOTAL'}),
])
def test_build_cell__head(kwargs, expected):
    builder = Formex4Builder()

    p_elem = P(u"text")
    cell_x1_y1 = Cell([p_elem], x=1, y=1, **kwargs)
    table = Table([cell_x1_y1])
    builder._table = table

    # -- build the cell
    row_elem = ROW()
    row_y1 = next(iter(table.rows))
    row_y1.nature = "head"
    builder.build_cell(row_elem, cell_x1_y1, row_y1)

    # -- check the '<CELL>' attributes
    entry_elem = row_elem[0]  # type: etree._Element
    assert entry_elem.tag == u"CELL"
    assert entry_elem.attrib == expected
    assert entry_elem[0] == p_elem


def test_build_title():
    table = Table()
    table.rows[1].insert_cell(u"Title", styles={"align": "center"})

    builder = Formex4Builder()
    tbl_elem = TBL()
    builder.build_title(tbl_elem, table.rows[0])

    # -- check the '<TITLE>' attributes
    title_elem = tbl_elem[0]  # type: etree._Element
    xml_parser = etree.XMLParser(remove_blank_text=True)
    expected = etree.XML(u"""\
    <TITLE>
      <TI>
        <P>Title</P>
      </TI>
    </TITLE>""", parser=xml_parser)

    diff_list = xmldiff.main.diff_trees(title_elem, expected)
    if diff_list:
        print(etree.tounicode(title_elem, pretty_print=True, with_tail=False), file=sys.stderr)
        assert diff_list == []


def test_build_title__empty():
    table = Table()
    table.rows[1].insert_cell(None, styles={"align": "center"})

    builder = Formex4Builder()
    tbl_elem = TBL()
    builder.build_title(tbl_elem, table.rows[0])

    # -- check the '<TITLE>' attributes
    title_elem = tbl_elem[0]  # type: etree._Element
    xml_parser = etree.XMLParser(remove_blank_text=True)
    expected = etree.XML(u"""\
    <TITLE>
      <TI>
        <IE/>
      </TI>
    </TITLE>""", parser=xml_parser)

    diff_list = xmldiff.main.diff_trees(title_elem, expected)
    if diff_list:
        print(etree.tounicode(title_elem, pretty_print=True, with_tail=False), file=sys.stderr)
        assert diff_list == []


def test_build_title__subtitle():
    table = Table()
    content = [P(u"TITLE"),
               P(u"Subtitle 1"),
               P(u"Subtitle 2")]
    table.rows[1].insert_cell(content, styles={"align": "center"})

    builder = Formex4Builder()
    tbl_elem = TBL()
    builder.build_title(tbl_elem, table.rows[0])

    # -- check the '<TITLE>' attributes
    title_elem = tbl_elem[0]  # type: etree._Element
    xml_parser = etree.XMLParser(remove_blank_text=True)
    expected = etree.XML(u"""\
    <TITLE>
      <TI>
        <P>TITLE</P>
      </TI>
      <STI>
        <P>Subtitle 1</P>
        <P>Subtitle 2</P>
      </STI>
    </TITLE>""", parser=xml_parser)

    diff_list = xmldiff.main.diff_trees(title_elem, expected)
    if diff_list:
        print(etree.tounicode(title_elem, pretty_print=True, with_tail=False), file=sys.stderr)
        assert diff_list == []


def test_build_tbl():
    # see: formex-4/samples/jo-compl-2002C_061/C_2002061EN.01000403.xml

    table = Table()
    table.rows[1].nature = "head"
    table.rows[1].insert_cell([P(u"Expert group")], nature="head")
    table.rows[1].insert_cell([P(u"First name and surname of the expert")], nature="head")
    table.rows[2].insert_cell([P(u"Control of infectious diseases")])
    table.rows[2].insert_cell([P(u"Michael Angelo BORG")])
    table.rows[3].insert_cell([P(u"Information society")], height=3)
    table.rows[3].insert_cell([P(u"Tony HEY")])
    table.rows[4].insert_cell([P(u"José L. ENCARNAÇÃO")])
    table.rows[5].insert_cell([P(u"Berit SVENDSEN")])
    table.rows[6].insert_cell([P(u"Controlled thermonuclear fusion")])
    table.rows[6].insert_cell([P(u"Pekka PIRILÄ")])

    builder = Formex4Builder()
    table_elem = builder.build_tbl(table)

    xml_parser = etree.XMLParser(remove_blank_text=True)

    expected = etree.XML(u"""\
    <TBL COLS="2" NO.SEQ="0001">
      <CORPUS>
        <ROW TYPE="HEADER">
          <CELL COL="1">
            <P>Expert group</P>
          </CELL>
          <CELL COL="2">
            <P>First name and surname of the expert</P>
          </CELL>
        </ROW>
        <ROW>
          <CELL COL="1">
            <P>Control of infectious diseases</P>
          </CELL>
          <CELL COL="2">
            <P>Michael Angelo BORG</P>
          </CELL>
        </ROW>
        <ROW>
          <CELL COL="1" ROWSPAN="3">
            <P>Information society</P>
          </CELL>
          <CELL COL="2">
            <P>Tony HEY</P>
          </CELL>
        </ROW>
        <ROW>
          <CELL COL="2">
            <P>José L. ENCARNAÇÃO</P>
          </CELL>
        </ROW>
        <ROW>
          <CELL COL="2">
            <P>Berit SVENDSEN</P>
          </CELL>
        </ROW>
        <ROW>
          <CELL COL="1">
            <P>Controlled thermonuclear fusion</P>
          </CELL>
          <CELL COL="2">
            <P>Pekka PIRILÄ</P>
          </CELL>
        </ROW>
      </CORPUS>
    </TBL>""", parser=xml_parser)

    for elem in table_elem.xpath("//*"):
        elem.text = elem.text or None
    for elem in expected.xpath("//*"):
        elem.text = elem.text or None

    diff_list = xmldiff.main.diff_trees(table_elem, expected)
    if diff_list:
        print(etree.tounicode(table_elem, pretty_print=True, with_tail=False), file=sys.stderr)
        assert diff_list == []


def test_build_tbl__with_title():
    # see: formex-4/samples/jo-compl-2002C_280/C_2002280EN.01000101.xml

    table = Table()
    table.rows[1].insert_cell([P(u"1 euro =")], width=3, styles={"align": "center"})
    table.rows[2].nature = "head"
    table.rows[2].insert_cell([P()], nature="head")
    table.rows[2].insert_cell([P(u"Currency")], nature="head")
    table.rows[2].insert_cell([P(u"Exchange rate")], nature="head")
    table.rows[3].insert_cell([P(u"USD")])
    table.rows[3].insert_cell([P(u"US dollar")])
    table.rows[3].insert_cell([P(u"1,0029")])
    table.rows[4].insert_cell([P(u"JPY")])
    table.rows[4].insert_cell([P(u"Japanese yen")])
    table.rows[4].insert_cell([P(u"121,05")])

    builder = Formex4Builder()
    table_elem = builder.build_tbl(table)

    xml_parser = etree.XMLParser(remove_blank_text=True)

    expected = etree.XML(u"""\
    <TBL COLS="3" NO.SEQ="0001">
      <TITLE>
        <TI>
          <P>1 euro =</P>
        </TI>
        <STI/>
      </TITLE>
      <CORPUS>
        <ROW TYPE="HEADER">
          <CELL COL="1">
            <IE/>
          </CELL>
          <CELL COL="2">
            <P>Currency</P>
          </CELL>
          <CELL COL="3">
            <P>Exchange rate</P>
          </CELL>
        </ROW>
        <ROW>
          <CELL COL="1">
            <P>USD</P>
          </CELL>
          <CELL COL="2">
            <P>US dollar</P>
          </CELL>
          <CELL COL="3">
            <P>1,0029</P>
          </CELL>
        </ROW>
        <ROW>
          <CELL COL="1">
            <P>JPY</P>
          </CELL>
          <CELL COL="2">
            <P>Japanese yen</P>
          </CELL>
          <CELL COL="3">
            <P>121,05</P>
          </CELL>
        </ROW>
      </CORPUS>
    </TBL>""", parser=xml_parser)

    for elem in table_elem.xpath("//*"):
        elem.text = elem.text or None
    for elem in expected.xpath("//*"):
        elem.text = elem.text or None

    diff_list = xmldiff.main.diff_trees(table_elem, expected)
    if diff_list:
        print(etree.tounicode(table_elem, pretty_print=True, with_tail=False), file=sys.stderr)
        assert diff_list == []


@pytest.mark.parametrize('orient, size, expected', [
    ('portrait', (595, 841), {'NO.SEQ': '0001', 'COLS': '1'}),
    ('landscape', (595, 841), {'NO.SEQ': '0001', 'COLS': '1', 'PAGE.SIZE': 'SINGLE.LANDSCAPE'}),
    ('portrait', (841, 595), {'NO.SEQ': '0001', 'COLS': '1'}),
    ('landscape', (841, 595), {'NO.SEQ': '0001', 'COLS': '1', 'PAGE.SIZE': 'SINGLE.LANDSCAPE'}),
    ('portrait', (1190, 841), {'NO.SEQ': '0001', 'COLS': '1', 'PAGE.SIZE': 'DOUBLE.PORTRAIT'}),
    ('landscape', (1190, 841), {'NO.SEQ': '0001', 'COLS': '1', 'PAGE.SIZE': 'DOUBLE.LANDSCAPE'}),
    ('portrait', (841, 1190), {'NO.SEQ': '0001', 'COLS': '1', 'PAGE.SIZE': 'DOUBLE.PORTRAIT'}),
    ('landscape', (841, 1190), {'NO.SEQ': '0001', 'COLS': '1', 'PAGE.SIZE': 'DOUBLE.LANDSCAPE'}),
])
def test_build_tbl__orient(orient, size, expected):
    builder = Formex4Builder()
    table = Table(styles={'x-sect-orient': orient, 'x-sect-size': size})
    table.rows[1].insert_cell(u"text")
    table_elem = builder.build_tbl(table)
    assert table_elem.attrib == expected


def test_build_tbl__no_seq():
    builder = Formex4Builder()
    table1 = Table()
    table1.rows[1].insert_cell(u"text1")
    table1_elem = builder.build_tbl(table1)
    table2 = Table()
    table2.rows[1].insert_cell(u"text2")
    table2_elem = builder.build_tbl(table2)
    assert table1_elem.attrib['NO.SEQ'] == u"0001"
    assert table2_elem.attrib['NO.SEQ'] == u"0002"


def test_build_tbl__empty_cell():
    builder = Formex4Builder()
    table1 = Table()
    table1.rows[1].insert_cell(u"")
    table1_elem = builder.build_tbl(table1)
    cell_elem = table1_elem.xpath('//CELL')[0]
    assert len(cell_elem) == 1
    assert cell_elem[0].tag == 'IE'
