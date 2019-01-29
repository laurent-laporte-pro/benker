# coding: utf-8
"""
Office Open XML parser
======================

This module can parse Office Open XML (OOXML) tables.

Specifications:

- The documentation about OOXML Table is available online at
  `Word Processing - Table Grid/Column Definition <http://officeopenxml.com/WPtableGrid.php>`_.
"""
import collections
import functools

from lxml import etree

from benker.parsers.base_parser import BaseParser
from benker.parsers.base_parser import value_of as base_value_of
from benker.parsers.lxml_iterwalk import iterwalk
from benker.table import Table

#: Namespace map used for xpath evaluation in Office Open XML documents
NS = {'w': "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def ns_name(ns, name):
    return '{' + ns + '}' + name


w = functools.partial(ns_name, NS['w'])
value_of = functools.partial(base_value_of, namespaces=NS)

_BORDER_STYLE_MAPPING = {

    # a single line
    'single': 'solid',

    # a line with a series of alternating thin and thick strokes
    'dashDotStroked': 'w-dash-dot-stroked',

    # a dashed line
    'dashed': 'dashed',

    # a dashed line with small gaps
    'dashSmallGap': 'w-dash-small-gap',

    # a line with alternating dots and dashes
    'dotDash': 'w-dot-dash',

    # a line with a repeating dot - dot - dash sequence
    'dotDotDash': 'w-dot-dot-dash',

    # a dotted line
    'dotted': 'dotted',

    # a double line
    'double': 'double',

    # a double wavy line
    'doubleWave': 'w-double-Wave',

    # an inset set of lines
    'inset': 'inset',

    # no border
    'nil': 'none',

    # no border
    'none': 'none',

    # an outset set of lines
    'outset': 'outset',

    # a single line
    'thick': 'w-thick',

    # a thick line contained within a thin line with a large-sized intermediate gap
    'thickThinLargeGap': 'w-thick-thin-large-gap',

    # a thick line contained within a thin line with a medium-sized intermediate gap
    'thickThinMediumGap': 'w-thick-thin-medium-gap',

    # a thick line contained within a thin line with a small intermediate gap
    'thickThinSmallGap': 'w-thick-thin-small-gap',

    # a thin line contained within a thick line with a large-sized intermediate gap
    'thinThickLargeGap': 'w-thin-thick-large-gap',

    # a thick line contained within a thin line with a medium-sized intermediate gap
    'thinThickMediumGap': 'w-thin-thick-medium-gap',

    # a thick line contained within a thin line with a small intermediate gap
    'thinThickSmallGap': 'w-thin-thick-small-gap',

    # a thin-thick-thin line with a large gap
    'thinThickThinLargeGap': 'w-thin-thick-thin-large-gap',

    # a thin-thick-thin line with a medium gap
    'thinThickThinMediumGap': 'w-thin-thick-thin-medium-gap',

    # a thin-thick-thin line with a small gap
    'thinThickThinSmallGap': 'w-thin-thick-thin-small-gap',

    # a three-staged gradient line, getting darker towards the paragraph
    'threeDEmboss': 'w-three-d-emboss',

    # a three-staged gradient like, getting darker away from the paragraph
    'threeDEngrave': 'w-three-d-engrave',

    # a triple line
    'triple': 'w-triple',

    # a wavy line
    'wave': 'w-wave',
}


def _get_border_properties(w_tbl_borders, style_xpath_mapping):
    # - Get the cell properties for each direction: 'top', 'right'...
    #   Values are converted to HTML values, size are in 'pt'
    properties = []
    for style, xpath in style_xpath_mapping:
        prop = {}
        color = value_of(w_tbl_borders, xpath.format(attr='color'))
        if color and color != "auto":
            prop['color'] = "#" + color
        shadow = value_of(w_tbl_borders, xpath.format(attr='shadow'))
        if shadow:
            prop['shadow'] = {"true": True, "false": False}[shadow]
        space = value_of(w_tbl_borders, xpath.format(attr='space'))
        if space:
            # unit is 'pt'
            prop['space'] = float(space)
        sz = value_of(w_tbl_borders, xpath.format(attr='sz'))
        if sz:
            # convert eighths of a point to 'pt'
            prop['sz'] = float(sz) / 8
        val = value_of(w_tbl_borders, xpath.format(attr='val'))
        if val:
            val = "none" if val == "nil" else val  # "nil" is "none" -- no border
            prop['val'] = _BORDER_STYLE_MAPPING.get(val, 'w-' + val)
        properties.append((style, prop))
    return properties


def _border_properties_to_styles(properties):
    """
    Convert the properties to border styles.

    :param properties: Ordered list of OOXML properties

    :return: dictionary of border styles
    """
    styles = {}

    # - 'border-top', 'border-right', 'border-bottom', 'border-left'
    for style, prop in properties:
        # formats -- order is important
        formats = ('val', "{val}"), ('sz', "{sz}pt"), ('color', "{color}")
        values = [fmt.format(**prop) for key, fmt in formats if key in prop]
        if values:
            styles[style] = " ".join(values)

    if any('space' in prop for style, prop in properties):
        # - 'border-collapse' property selects a table's border model(separated or collapsing).
        #   Value is "collapse" if all spaces == 0
        spaces = [prop.get('space', 0) for style, prop in properties]
        all_spaces_are_nul = all(space == 0 for space in spaces)
        styles['border-collapse'] = "collapse" if all_spaces_are_nul else "separate"

        # - 'border-spacing' property specifies the distance between the borders of adjacent cells.
        if not all_spaces_are_nul:
            spacing = ["{0}pt".format(prop.get('space', 0)) for style, prop in properties]
            styles['border-spacing'] = " ".join(spacing)

    # - The box-shadow property attaches one or more shadows to an element.
    #   Use the border size, the default color, without effect (blur...)
    has_shadow = any(prop.get('shadow') for style, prop in properties)
    if has_shadow:
        shadow = ["{0}pt".format(prop['sz'] if prop.get('shadow') else "0pt")
                  for style, prop in properties]
        styles['box-shadow'] = " ".join(shadow)

    return styles


def _get_table_borders(w_tbl_borders):
    """
    Construct a border dictionary from the ``w:tblPr/w:tblBorders`` properties.

    See `Table Properties <http://officeopenxml.com/WPtableProperties.php>`_
    and `Table Borders <http://officeopenxml.com/WPtableBorders.php>`_.

    :param w_tbl_borders:
        Properties of the OOXML table.

    :rtype: benker.parsers.ooxml.OoxmlBorder
    :return: New instance.
    """
    if w_tbl_borders is None:
        return {}
    # style_xpath_mapping -- order is important
    style_xpath_mapping = [
        ('border-top', "w:top/@w:{attr}"),
        ('border-right', "w:end/@w:{attr} | w:right/@w:{attr}"),
        ('border-bottom', "w:bottom/@w:{attr}"),
        ('border-left', "w:start/@w:{attr} | w:left/@w:{attr}"),
    ]
    properties = _get_border_properties(w_tbl_borders, style_xpath_mapping)
    styles = _border_properties_to_styles(properties)
    return styles


def _get_cell_borders(w_tbl_borders):
    """
    Construct a border dictionary from the ``w:tblPr/w:tblBorders`` properties.

    See `Table Properties <http://officeopenxml.com/WPtableProperties.php>`_
    and `Table Borders <http://officeopenxml.com/WPtableBorders.php>`_.

    :param w_tbl_borders:
        Properties of the OOXML table.

    :rtype: benker.parsers.ooxml.OoxmlBorder
    :return: New instance.
    """
    if w_tbl_borders is None:
        return {}
    # style_xpath_mapping -- order is important
    style_xpath_mapping = [
        ('border-top', "w:insideH/@w:{attr}"),
        ('border-right', "w:insideV/@w:{attr}"),
        ('border-bottom', "w:insideH/@w:{attr}"),
        ('border-left', "w:insideV/@w:{attr}"),
    ]
    properties = _get_border_properties(w_tbl_borders, style_xpath_mapping)
    styles = _border_properties_to_styles(properties)
    return styles


def _get_style_borders(w_styles, style_id):
    if w_styles is None or style_id is None:
        return {}
    w_style = value_of(w_styles, 'w:style[@w:styleId = "{0}"]'.format(style_id))
    if w_style is None:
        return {}

    # - get parent styles (if it exist)
    based_on_id = value_of(w_style, 'w:basedOn/@w:val')
    parent_styles = _get_style_borders(w_styles, based_on_id)

    # - get child styles
    w_tbl_borders = value_of(w_style, 'w:tblPr/w:tblBorders')
    table_borders = _get_table_borders(w_tbl_borders)
    cell_borders = _get_cell_borders(w_tbl_borders)
    child_styles = table_borders.copy()
    child_styles.update({'x-cell-' + key: value for key, value in cell_borders.items()})

    # - *child_styles* override *parent_styles*
    real_styles = parent_styles.copy()
    real_styles.update({key: value for key, value in child_styles.items() if value is not None})
    return real_styles


class OoxmlParser(BaseParser):
    """
    Office Open XML to CALS tables parsers.
    """

    class _State(object):
        """
        Parsing state for the converter (internal usage).
        """

        def __init__(self):
            self.col_pos = 0
            self.col = None
            self.row_pos = 0
            self.row = None
            self.table = None

        reset = __init__

        def next_col(self):
            self.col_pos += 1
            self.col = None

        def next_row(self):
            self.col_pos = 0
            self.col = None
            self.row_pos += 1
            self.row = None

    def __init__(self, builder, styles_path=None, **options):
        """
        Construct a parser

        :type  builder: benker.builders.base_builder.BaseBuilder
        :param builder:
            Builder used by this parser to instantiate :class:`~benker.table.Table` objects.

        :param str styles_path:
            Path to the stylesheet to use to resole table styles.
            In an uncompressed ``.docx`` tree structure, the stylesheet path
            is ``word/styles.xml``.

        :param str options: Extra conversion options.
            See :meth:`~benker.converters.base_converter.BaseConverter.convert_file`
            to have a list of all possible options.
        """
        self._state = self._State()
        self._w_styles = None
        self.styles_path = styles_path
        super(OoxmlParser, self).__init__(builder, **options)

    def transform_tables(self, tree):
        self._w_styles = etree.parse(self.styles_path) if self.styles_path else None
        self._w_styles = self._w_styles or value_of(tree, ".//w:styles")

        for w_tbl in tree.xpath("//w:tbl", namespaces=NS):
            table = self.parse_table(w_tbl)
            table_elem = self.builder.generate_table_tree(table)
            parent = w_tbl.getparent()
            index = parent.index(w_tbl)
            parent.insert(index, table_elem)
            table_elem.tail = w_tbl.tail
            parent.remove(w_tbl)

    def parse_table(self, w_tbl):
        """
        Convert a Office Open XML ``<w:tbl>`` into CALS ``<table>``

        :type  w_tbl: etree._Element
        :param w_tbl: Office Open XML element.

        :rtype: etree.Element
        :return: CALS element.
        """
        state = self._state
        state.reset()

        elements = {w(name) for name in {'tbl', 'tblGrid', 'gridCol', 'tr', 'tc'}}
        context = iterwalk(w_tbl, events=('start', 'end'), tag=elements)

        depth = 0
        for action, elem in context:
            elem_tag = elem.tag
            if elem_tag == w('tbl'):
                if action == 'start':
                    depth += 1
                else:
                    depth -= 1
            if depth > 1:
                # .. note:: context.skip_subtree() is not available for all version of lxml
                # This <tbl> element is inside the table.
                # It will be handled separately in another call to convert_tbl()
                continue
            if action == 'start':
                if elem_tag == w('tbl'):
                    self.parse_tbl(elem)

                elif elem_tag == w('tblGrid'):
                    # this element has no specific data
                    pass

                elif elem_tag == w('gridCol'):
                    state.next_col()
                    self.parse_grid_col(elem)

                elif elem_tag == w('tr'):
                    state.next_row()
                    self.parse_tr(elem)

                elif elem_tag == w('tc'):
                    state.next_col()
                    self.parse_tc(elem)

                else:
                    raise NotImplementedError(elem_tag)
            else:
                if elem_tag == w('tr'):
                    # add missing entries
                    for _ in range(state.col_pos, len(state.table.cols)):
                        state.row.insert_cell(None)

        return state.table

    def parse_tbl(self, w_tbl):
        """
        Parse a ``<w:tbl>`` element.

        See: `Table Properties <http://officeopenxml.com/WPtableProperties.php>`_.

        :type  w_tbl: etree._Element
        :param w_tbl: Table element.
        """
        style_id = value_of(w_tbl, "w:tblPr/w:tblStyle/@w:val")

        # - Table and borders are extracted from the style (if possible)
        #   and then from the ``w:tblPr/w:tblBorders`` properties.

        style_borders = _get_style_borders(self._w_styles, style_id)
        w_tbl_borders = value_of(w_tbl, 'w:tblPr/w:tblBorders')

        # - Table borders (frame) and Cell borders (colsep/rowsep) use the "x-cell-" prefix

        table_borders = _get_table_borders(w_tbl_borders)
        real_table_borders = style_borders.copy()
        real_table_borders.update({key: value for key, value in table_borders.items() if value is not None})

        attrs = real_table_borders.copy()

        # -- Sections: http://officeopenxml.com/WPsection.php

        # A section's properties are stored in a sectPr element.
        # For all sections except the last section, the sectPr element is stored as
        # a child element of the last paragraph in the section. For the last section,
        # the sectPr is stored as a child element of the body element.

        w_sect_pr = value_of(w_tbl, 'following::w:p/w:pPr/w:sectPr | following::w:sectPr')

        # - ``x-sect-orient``: Section orientation
        #   Possible values are "landscape" and "portrait".
        sect_orient = value_of(w_sect_pr, 'w:pgSz/@w:orient')
        if sect_orient:
            attrs['x-sect-orient'] = sect_orient

        # - w:cols -- Specifies the set of columns for the section.
        # - ``x-sect-cols``: Section column number
        #   Default value is "1" -- useful for @pgwide
        sect_cols = value_of(w_sect_pr, 'w:cols/@w:num')
        if sect_cols is None:
            sect_cols = w_sect_pr.xpath('count(w:cols/w:col)', namespaces=NS)  # type: float
            sect_cols = str(int(sect_cols)) if sect_cols else "1"
        attrs['x-sect-cols'] = sect_cols

        # - The HTML ``class`` attribute is not a regular style.
        #   We use the table ``nature``instead.

        self._state.table = Table(styles=attrs, nature=style_id)

    def parse_grid_col(self, w_grid_col):
        """
        Parse a ``<w:gridCol>`` element.

        See: `Table Grid/Column Definition <http://officeopenxml.com/WPtableGrid.php>`_.

        :type  w_grid_col: etree._Element
        :param w_grid_col: Table element.
        """
        # w:w => width of the column in twentieths of a point.
        width = float(w_grid_col.attrib[w('w')]) / 20  # pt
        state = self._state
        styles = {u"width": "{0:0.2f}pt".format(width)}
        state.col = state.table.cols[state.col_pos]
        state.col.styles.update(styles)

    def parse_tr(self, w_tr):
        """
        Parse a ``<w:tr>`` element.

        See: `Table Row Properties <http://officeopenxml.com/WPtableRowProperties.php>`_.

        :type  w_tr: etree._Element
        :param w_tr: Table element.
        """

        # - w:tblHeader => the current row should be repeated at the top
        #   of each new page on which the table is displayed.
        #   This is a simple boolean property, so you can specify a val attribute of true or false.
        #
        #   <w:trPr>
        #     <w:tblHeader/>
        #   </w:trPr>
        #
        w_tbl_header = value_of(w_tr, "w:trPr/w:tblHeader")
        if w_tbl_header is not None:
            w_tbl_header = value_of(w_tr, "w:trPr/w:tblHeader/@w:val", default=u"true")
        nature = {u"true": "head", u"false": "body", None: "body"}[w_tbl_header]
        state = self._state
        state.row = state.table.rows[state.row_pos]
        state.row.nature = nature

        # - w:trHeight => height of the row
        #
        #   <w:trPr>
        #     <w:trHeight w:val="567"/>
        #   </w:trPr>
        #
        w_tr_height = value_of(w_tr, "w:trPr/w:trHeight")
        if w_tr_height is not None:
            h_rule = value_of(w_tr, "w:trPr/w:tblHeader/@w:hRule", default="auto")
            # Possible values are:
            # - atLeast (height should be at least the value specified),
            # - exact (height should be exactly the value specified), or
            # - auto (height is determined based on the height of the contents, so the value is ignored).
            style = {'atLeast': 'min-height', 'exact': 'height', 'auto': None}[h_rule]
            if style:
                val = value_of(w_tr, "w:trPr/w:tblHeader/@w:val", default="0")
                # Specifies the row's height, in twentieths of a point.
                height = float(val) / 20  # pt
                state.row.styles[style] = "{0:0.2f}pt".format(height)

        # - w:ins => revision marks: A row can be marked as "inserted".
        #
        #   <w:trPr>
        #     <w:ins w:id="0" w:author="Laurent Laporte" w:date="2018-11-21T18:08:00Z"/>
        #   </w:trPr>
        #
        w_ins = value_of(w_tr, "w:trPr/w:ins")
        if w_ins is not None:
            state.row.styles['x-ins'] = True
            style_xpath_mapping = [
                ('x-ins-id', "w:trPr/w:ins/@w:id"),
                ('x-ins-author', "w:trPr/w:ins/@w:author"),
                ('x-ins-date', "w:trPr/w:ins/@w:date"),
            ]
            for style, xpath in style_xpath_mapping:
                value = value_of(w_tr, xpath)
                if value:
                    state.row.styles[style] = value

        # note: ``valign`` attribute is not available for a row => see w:tcPr instead

    def parse_tc(self, w_tc):
        """
        Parse a ``<w:tc>`` element.

        See: `Table Cell Properties <http://officeopenxml.com/WPtableCellProperties.php>`_.

        :type  w_tc: etree._Element
        :param w_tc: Table element.
        """
        state = self._state

        # w:gridSpan => number of logical columns across which the cell spans
        width = int(value_of(w_tc, "w:tcPr/w:gridSpan/@w:val", default=u"1"))

        # take the colspan into account:
        state.col_pos += width - 1

        # w:vMerge => specifies that the cell is part of a vertically merged set of cells.
        w_v_merge = value_of(w_tc, "w:tcPr/w:vMerge")
        if w_v_merge is not None:
            w_v_merge = value_of(w_tc, "w:tcPr/w:vMerge/@w:val", default=u"continue")
        if w_v_merge is None:
            # no merge
            height = 1
        elif w_v_merge == u"continue":
            # the current cell continues a previously existing merge group
            state.table.expand((state.col_pos, state.row.row_pos - 1), height=1)
            height = None
        elif w_v_merge == u"restart":
            # the current cell starts a new merge group
            height = 1
        else:
            raise NotImplementedError(w_v_merge)

        if height:
            styles = {}

            # -- Vertical alignment
            #
            # w:vAlign => Specifies the vertical alignment for text between the top and bottom margins of the cell.
            #
            # Possible values are:
            # - bottom - Specifies that the text should be vertically aligned to the bottom margin.
            # - center - Specifies that the text should be vertically aligned to the center of the cell.
            # - top - Specifies that the text should be vertically aligned to the top margin.
            w_v_align = value_of(w_tc, "w:tcPr/w:vAlign")
            if w_v_align is not None:
                w_v_align = value_of(w_tc, "w:tcPr/w:vAlign/@w:val", default=u"top")
                # CSS/Properties/vertical-align
                v_align = {"top": "top", "center": "middle", "bottom": "bottom"}[w_v_align]
                styles["valign"] = v_align

            # -- Horizontal alignment
            #
            # Horizontal alignment is done at paragraph level, inside the cell.
            # We can calculate the cell alignment base on the paragraph properties,
            # for instance ``<w:p><w:pPr><w:jc w:val="right"/>``,
            # see: http://officeopenxml.com/WPalignment.php
            #
            # We use the most common alignment for cell alignment.
            w_p_list = w_tc.xpath("w:p", namespaces=NS)
            w_jc_counter = collections.Counter(value_of(w_p, "w:pPr/w:jc/@w:val") for w_p in w_p_list)
            w_jc = w_jc_counter.most_common(1)[0][0]  # type: str or None
            if w_jc is not None:
                # CSS/Properties/text-align
                align = {"start": "left",
                         "end": "right",
                         "left": "left",
                         "right": "right",
                         "center": "center",
                         "both": "justify",
                         "distribute": "justify"}[w_jc]
                styles["align"] = align

            # -- Borders
            w_tc_borders = value_of(w_tc, 'w:tcPr/w:tcBorders')
            cell_borders = _get_table_borders(w_tc_borders)
            styles.update(cell_borders)

            # todo: calculate the ``@rotate`` attribute.

            content = w_tc.xpath('w:p | w:tbl', namespaces=NS)
            state.row.insert_cell(content, width=width, height=height, styles=styles)
