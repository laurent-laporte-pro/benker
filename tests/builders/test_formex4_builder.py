# coding: utf-8
from __future__ import print_function

import sys

import pytest
import xmldiff.main
from lxml import etree

from benker.builders.formex4 import Formex4Builder
from benker.cell import Cell
from benker.table import Table


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

    p_elem = etree.XML("<P>text</P>")
    cell_x1_y1 = Cell([p_elem], x=1, y=1, **kwargs)
    table = Table([cell_x1_y1])
    builder._table = table

    # -- build the cell
    row_elem = etree.XML("<ROW/>")
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

    p_elem = etree.XML("<P>text</P>")
    cell_x1_y1 = Cell([p_elem], x=1, y=1, **kwargs)
    table = Table([cell_x1_y1])
    builder._table = table

    # -- build the cell
    row_elem = etree.XML("<ROW/>")
    row_y1 = next(iter(table.rows))
    row_y1.nature = "head"
    builder.build_cell(row_elem, cell_x1_y1, row_y1)

    # -- check the '<CELL>' attributes
    entry_elem = row_elem[0]  # type: etree._Element
    assert entry_elem.tag == u"CELL"
    assert entry_elem.attrib == expected
    assert entry_elem[0] == p_elem


def test_build_tbl():
    # see: formex-4/samples/jo-compl-2002C_061/C_2002061EN.01000403.xml

    table = Table()
    table.rows[1].nature = "head"
    table.rows[1].insert_cell(u"Expert group", nature="head")
    table.rows[1].insert_cell(u"First name and surname of the expert", nature="head")
    table.rows[2].insert_cell(u"Control of infectious diseases")
    table.rows[2].insert_cell(u"Michael Angelo BORG")
    table.rows[3].insert_cell(u"Information society", height=3)
    table.rows[3].insert_cell(u"Tony HEY")
    table.rows[4].insert_cell(u"José L. ENCARNAÇÃO")
    table.rows[5].insert_cell(u"Berit SVENDSEN")
    table.rows[6].insert_cell(u"Controlled thermonuclear fusion")
    table.rows[6].insert_cell(u"Pekka PIRILÄ")

    builder = Formex4Builder()
    table_elem = builder.build_tbl(table)

    xml_parser = etree.XMLParser(remove_blank_text=True)

    expected = etree.XML(u"""\
    <TBL COLS="2" NO.SEQ="0001">
        <CORPUS>
            <ROW TYPE="HEADER">
                <CELL COL="1">Expert group</CELL>
                <CELL COL="2">First name and surname of the expert</CELL>
            </ROW>
            <ROW>
                <CELL COL="1">Control of infectious diseases</CELL>
                <CELL COL="2">Michael Angelo BORG</CELL>
            </ROW>
            <ROW>
                <CELL COL="1" ROWSPAN="3">Information society</CELL>
                <CELL COL="2">Tony HEY</CELL>
            </ROW>
            <ROW>
                <CELL COL="2">José L. ENCARNAÇÃO</CELL>
            </ROW>
            <ROW>
                <CELL COL="2">Berit SVENDSEN</CELL>
            </ROW>
            <ROW>
                <CELL COL="1">Controlled thermonuclear fusion</CELL>
                <CELL COL="2">Pekka PIRILÄ</CELL>
            </ROW>
        </CORPUS>
    </TBL>""", parser=xml_parser)

    diff_list = xmldiff.main.diff_trees(table_elem, expected)
    if diff_list:
        print(etree.tounicode(table_elem, pretty_print=True, with_tail=False), file=sys.stderr)
        assert 0


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
