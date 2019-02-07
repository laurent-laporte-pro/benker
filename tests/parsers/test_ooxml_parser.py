# coding: utf-8
from lxml import etree

from benker.builders.base_builder import BaseBuilder
from benker.parsers.ooxml import OoxmlParser
from benker.table import Table


def test_parse_tc():
    builder = BaseBuilder()
    parser = OoxmlParser(builder)

    # -- setup a minimal table
    state = parser._state
    state.table = Table()
    state.row = state.table.rows[1]
    state.next_col()

    # -- parse a <w:tc/>
    w_tc_content = u"""<w:tc xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
        <w:tcPr>
            <w:tcW w:w="1298" w:type="dxa"/>
            <w:gridSpan w:val="3"/>
            <w:tcBorders>
                <w:bottom w:val="nil"/>
                <w:right w:val="single" w:sz="12" w:space="0" w:color="4472C4" w:themeColor="accent1"/>
            </w:tcBorders>
            <w:shd w:val="clear" w:color="auto" w:fill="FBE4D5" w:themeFill="accent2" w:themeFillTint="33"/>
        </w:tcPr>
        <w:p w:rsidR="00EF2ECA" w:rsidRDefault="00EF2ECA"><w:r><w:t>1</w:t></w:r></w:p>
    </w:tc>"""
    w_tc = etree.XML(w_tc_content)
    parser.parse_tc(w_tc)

    # -- check the styles
    table = state.table
    cell = table[(1, 1)]
    expected = {'border-collapse': 'collapse', 'border-right': 'solid 1.5pt #4472C4', 'border-bottom': 'none'}
    assert expected == cell.styles
