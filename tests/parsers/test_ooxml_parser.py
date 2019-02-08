# coding: utf-8
import pytest
from lxml import etree

from benker.builders.base_builder import BaseBuilder
from benker.parsers.ooxml import OoxmlParser
from benker.table import Table

TEST_DATA = [

    # without style
    # -------------

    pytest.param(
        u"""<w:tc xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:p w:rsidR="00EF2ECA" w:rsidRDefault="00EF2ECA"><w:r><w:t>empty</w:t></w:r></w:p>
        </w:tc>""",
        {},
        id="no_style"),

    pytest.param(
        u"""<w:tc xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:tcPr>
                <w:tcW w:w="736" w:type="dxa"/>
                <w:gridSpan w:val="2"/>
            </w:tcPr>
            <w:p w:rsidR="00EF2ECA" w:rsidRDefault="00EF2ECA"><w:r><w:t>B</w:t></w:r></w:p>
        </w:tc>""",
        {},
        id="style_is_empty"),

    # Borders
    # -------

    pytest.param(
        u"""<w:tc xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
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
        </w:tc>""",
        {'border-collapse': 'collapse',
         'border-right': 'solid 1.5pt #4472C4',
         'border-bottom': 'none'},
        id="style_border-right_solid_border-bottom_none"),

    pytest.param(
        u"""<w:tc xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:tcPr>
                <w:tcW w:w="562" w:type="dxa"/>
                <w:tcBorders>
                    <w:top    w:val="double" w:sz="8"  w:color="FFFFFF"/>
                    <w:right  w:val="dotted" w:sz="16" w:color="FF0000"/>
                    <w:bottom w:val="dashed" w:sz="24" w:color="00FF00"/>
                    <w:left   w:val="outset" w:sz="32" w:color="0000FF"/>
                </w:tcBorders>
            </w:tcPr>
            <w:p w:rsidR="00EF2ECA" w:rsidRDefault="00EF2ECA"/>
        </w:tc>""",
        {'border-top': 'double 1.0pt #FFFFFF',
         'border-right': 'dotted 2.0pt #FF0000',
         'border-bottom': 'dashed 3.0pt #00FF00',
         'border-left': 'outset 4.0pt #0000FF'},
        id="style_border-all"),

    pytest.param(
        u"""<w:tc xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:tcPr>
                <w:tcW w:w="562" w:type="dxa"/>
                <w:tcBorders>
                    <w:tr2bl w:val="single" w:sz="4" w:space="0" w:color="auto"/>
                    <w:tl2br w:val="single" w:sz="4" w:space="0" w:color="auto"/>
                </w:tcBorders>
            </w:tcPr>
            <w:p w:rsidR="00EF2ECA" w:rsidRDefault="00EF2ECA"/>
        </w:tc>""",
        {'border-collapse': 'collapse',
         'x-border-tl2br': 'solid 0.5pt',
         'x-border-tr2bl': 'solid 0.5pt'},
        id="style_border-tl2br-tr2bl"),

    # align and vertical-align
    # ------------------------

    pytest.param(
        u"""<w:tc xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:tcPr><w:vAlign w:val="top"/></w:tcPr>
            <w:p>
                <w:pPr><w:jc w:val="left"/></w:pPr>
                <w:r><w:t>text</w:t></w:r>
            </w:p>
        </w:tc>""",
        {'vertical-align': 'top', 'align': 'left'},
        id="style_vertical-align_top_align_left"),

    pytest.param(
        u"""<w:tc xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:tcPr><w:vAlign w:val="bottom"/></w:tcPr>
            <w:p>
                <w:pPr><w:jc w:val="right"/></w:pPr>
                <w:r><w:t>text</w:t></w:r>
            </w:p>
        </w:tc>""",
        {'vertical-align': 'bottom', 'align': 'right'},
        id="style_vertical-align_bottom_align_right"),

    pytest.param(
        u"""<w:tc xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:tcPr><w:vAlign w:val="center"/></w:tcPr>
            <w:p>
                <w:pPr><w:jc w:val="center"/></w:pPr>
                <w:r><w:t>text</w:t></w:r>
            </w:p>
        </w:tc>""",
        {'vertical-align': 'middle', 'align': 'center'},
        id="style_vertical-align_middle_align_center"),

    pytest.param(
        u"""<w:tc xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:tcPr><w:vAlign w:val="both"/></w:tcPr>
            <w:p>
                <w:pPr><w:jc w:val="both"/></w:pPr>
                <w:r><w:t>text</w:t></w:r>
            </w:p>
        </w:tc>""",
        {'vertical-align': 'w-both', 'align': 'justify'},
        id="style_vertical-align_both_align_justify"),

]


@pytest.mark.parametrize('w_tc_content, expected', TEST_DATA)
def test_parse_tc(w_tc_content, expected):
    builder = BaseBuilder()
    parser = OoxmlParser(builder)

    # -- setup a minimal table
    state = parser._state
    state.table = Table()
    state.row = state.table.rows[1]
    state.next_col()

    # -- parse a <w:tc/>
    w_tc = etree.XML(w_tc_content)
    parser.parse_tc(w_tc)

    # -- check the styles
    table = state.table
    cell = table[(1, 1)]
    assert expected == cell.styles
