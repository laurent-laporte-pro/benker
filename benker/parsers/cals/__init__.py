# coding: utf-8
"""
CALS Parser Implementation
==========================

This module can parse the tables (``table`` elements) of a CALS file.

Specifications and examples:

- The CALS DTD is available online in the OASIS web site:
  `CALS Table Model Document Type Definition <https://www.oasis-open.org/specs/a502.htm>`_.

- An example of CALS table is available in Wikipedia:
  `CALS Table Model <https://en.wikipedia.org/wiki/CALS_Table_Model>`_

The main elements of a CALS table are:

*   ``table``: a table can contains one or several ``tgroup``.

    *   ``titles``: table titles (*not supported by the CALS parser*)

    *   ``tgroup``: a portion of table

        *   ``colspec``: column specifications

        *   ``spanspec``: spanning specifications (*not supported by the CALS parser*)

        *   ``thead``: table header

            *   ``colspec``: header column specifications (*not supported by the CALS parser*)

            *   ``row``: table row (see ``tbody``)

        *   ``tfoot``: table footer

            *   ``colspec``: footer column specifications (*not supported by the CALS parser*)

            *   ``row``: table row (see ``tbody``)

        *   ``tbody``: table body

            *   ``row``: table row

                *   ``entry``: table entry which contains paragraphs

                *   ``entrytbl``: table entry which contains a table (*not supported by the CALS parser*)

An example of CALS table is available in Wikipedia:
`CALS Table Model <https://en.wikipedia.org/wiki/CALS_Table_Model>`_

.. versionadded:: 0.5.0
"""
import re

from lxml import etree

from benker.box import Box
from benker.common.lxml_iterwalk import iterwalk
from benker.common.lxml_qname import QName
from benker.parsers.base_parser import BaseParser
from benker.parsers.cals.frame_styles import BORDER_NONE
from benker.parsers.cals.frame_styles import BORDER_SOLID
from benker.parsers.cals.frame_styles import get_frame_styles
from benker.table import Table
from benker.units import convert_value
from benker.units import parse_width

# noinspection PyProtectedMember
#: Element Type
ElementType = etree._Element


class CalsParser(BaseParser):
    """
    CALS tables parser
    """

    def __init__(self, builder, cals_ns=None, width_unit="mm", **options):
        """
        Construct a parser

        :type  builder: benker.builders.base_builder.BaseBuilder
        :param builder:
            Builder used by this parser to instantiate :class:`~benker.table.Table` objects.

        :param str cals_ns:
            Namespace to use for CALS elements and attributes.
            Set ``None`` (or "") if you don't use namespace in your XML.

        :param str width_unit:
            Unit to use for table/column widths.
            Possible values are: 'cm', 'dm', 'ft', 'in', 'm', 'mm', 'pc', 'pt', 'px'.

        :keyword str options: Extra conversion options.
            See :meth:`~benker.converters.base_converter.BaseConverter.convert_file`
            to have a list of all possible options.

        .. versionchanged:: 0.5.1
           Add the options *width_unit*.
        """
        self.cals_ns = cals_ns
        self.width_unit = width_unit
        super(CalsParser, self).__init__(builder, **options)

    def get_cals_qname(self, name):
        return QName(self.cals_ns, name)

    def transform_tables(self, tree):
        if self.cals_ns:
            nodes = tree.xpath("//cals:table", namespaces={"cals": self.cals_ns})
        else:
            nodes = tree.xpath("//table")
        for node in nodes:
            table = self.parse_table(node)
            table_elem = self.builder.generate_table_tree(table)
            parent = node.getparent()
            index = parent.index(node)
            parent.insert(index, table_elem)
            table_elem.tail = node.tail
            parent.remove(node)

    # noinspection PyPep8Naming
    def parse_table(self, cals_table):
        """
        Convert a ``<table>`` CALS element into table object.

        :type  cals_table: ElementType
        :param cals_table: CALS element.

        :rtype: benker.table.Table
        :return: Table.
        """
        state = self._state
        state.reset()

        # -- CALS elements
        cals = self.get_cals_qname

        table = cals("table").text
        # titles = cals("titles").text  # not supported
        tgroup = cals("tgroup").text
        colspec = cals("colspec").text
        thead = cals("thead").text
        tfoot = cals("tfoot").text
        tbody = cals("tbody").text
        row = cals("row").text
        # entrytbl = cals("entrytbl").text  # not supported
        entry = cals("entry").text

        elements = {table, tgroup, colspec, thead, tfoot, tbody, row, entry}
        context = iterwalk(cals_table, events=("start", "end"), tag=elements)

        depth = 0
        for action, elem in context:
            elem_tag = elem.tag
            if elem_tag == table:
                if action == "start":
                    depth += 1
                else:
                    depth -= 1
            if depth > 1:
                # .. note:: context.skip_subtree() is not available for all version of lxml
                # This <TBL> element is inside the table.
                # It will be handled separately in another call to transform_tables()
                continue
            if action == "start":
                # tags sorted by frequency:
                if elem_tag == entry:
                    state.next_col()
                    self.parse_cals_entry(elem)

                elif elem_tag == row:
                    state.next_row()
                    self.parse_cals_row(elem)

                elif elem_tag in {tbody, tfoot, thead}:
                    # everything is done in parse_fmx_row()
                    pass

                elif elem_tag == colspec:
                    state.next_col()
                    self.parse_cals_colspec(elem)

                elif elem_tag == tgroup:
                    self.parse_cals_tgroup(elem)

                elif elem_tag == table:
                    self.parse_cals_table(elem)

                else:
                    raise NotImplementedError(elem_tag)
            else:
                if elem_tag in {row}:
                    bounding_box = Box(1, state.row_pos, len(state.table.cols), state.row_pos)
                    state.table.fill_missing(bounding_box, None, nature=state.row.nature)
                elif elem_tag == table:
                    state.table.fill_missing(state.table.bounding_box, None)

        return state.table

    def setup_table(self, styles=None, nature=None):
        table = Table(styles=styles, nature=nature)
        self._state.table = table
        return self._state

    def parse_cals_table(self, cals_table):
        """
        Parse a CALS ``table`` element.

        :type  cals_table: ElementType
        :param cals_table: CALS table Element.

        :return: State of the parser (for debug purpose).

        .. versionchanged:: 0.5.1
           Add support for the ``@cals:width`` attribute (table width).
        """
        cals = self.get_cals_qname
        styles = {}
        nature = None

        # -- attribute @cals:frame
        frame = cals_table.attrib.get(cals("frame"))
        styles.update(get_frame_styles(frame))

        # -- attribute @cals:colsep
        colsep = cals_table.attrib.get(cals("colsep"))
        colsep_map = {"0": BORDER_NONE, "1": BORDER_SOLID}
        if colsep in colsep_map:
            styles["x-cell-border-right"] = colsep_map[colsep]

        # -- attribute @cals:rowsep
        rowsep = cals_table.attrib.get(cals("rowsep"))
        rowsep_map = {"0": BORDER_NONE, "1": BORDER_SOLID}
        if rowsep in rowsep_map:
            styles["x-cell-border-bottom"] = rowsep_map[rowsep]

        # -- attribute @cals:orient
        orient = cals_table.attrib.get(cals("orient"))
        orient_map = {"land": "landscape", "port": "portrait"}
        if orient in orient_map:
            styles["x-sect-orient"] = orient_map[orient]

        # -- attribute @cals:pgwide
        pgwide = cals_table.attrib.get(cals("pgwide"))
        pgwide_map = {"0": "2", "1": "1"}
        if pgwide in pgwide_map:
            styles["x-sect-cols"] = pgwide_map[pgwide]

        # -- attribute @cals:bgcolor
        bgcolor = cals_table.attrib.get(cals("bgcolor"))
        if bgcolor:
            styles["background-color"] = bgcolor

        # -- attribute @cals:tabstyle
        tabstyle = cals_table.attrib.get(cals("tabstyle"))
        if tabstyle:
            nature = tabstyle

        # -- attribute @cals:tabstyle
        width = cals_table.attrib.get(cals("width"))
        if width:
            width, unit = parse_width(width)
            value = convert_value(width, unit, self.width_unit)
            styles["width"] = u"{value:0.2f}{unit}".format(value=value, unit=self.width_unit)

        return self.setup_table(styles, nature)

    def parse_cals_tgroup(self, cals_tgroup):
        cals = self.get_cals_qname
        styles = {}
        nature = self._state.table.nature

        # -- attribute @cals:cols => ignored (*table.cols*)

        # -- attribute @cals:colsep
        colsep = cals_tgroup.attrib.get(cals("colsep"))
        colsep_map = {"0": BORDER_NONE, "1": BORDER_SOLID}
        if colsep in colsep_map:
            styles["x-cell-border-right"] = colsep_map[colsep]

        # -- attribute @cals:rowsep
        rowsep = cals_tgroup.attrib.get(cals("rowsep"))
        rowsep_map = {"0": BORDER_NONE, "1": BORDER_SOLID}
        if rowsep in rowsep_map:
            styles["x-cell-border-bottom"] = rowsep_map[rowsep]

        # -- attribute @cals:tgroupstyle
        tgroupstyle = cals_tgroup.attrib.get(cals("tgroupstyle"))
        if tgroupstyle:
            nature = self._state.table.nature
            if nature:
                parts = nature.split(" ")
                nature = " ".join(parts[:-1] + [tgroupstyle])
            else:
                nature = tgroupstyle

        # -- Override the table defaults
        state = self._state
        table = state.table
        table.styles.update(styles)
        table.nature = nature

        return state  # mainly for unit test

    def parse_cals_row(self, cals_row):
        """
        Parse a ``row`` element which contains ``entry`` elements.

        This element may be in a ``BLK```

        :type  cals_row: ElementType
        :param cals_row: table row

        .. versionchanged:: 0.5.1
           The "vertical-align" style is built from the ``@cals:valign`` attribute.
        """
        cals = self.get_cals_qname
        styles = {}
        nature = None  # overridden below if parent's element exists

        cals_parent = cals_row.getparent()  # type:  ElementType
        if cals_parent is not None:
            # -- nature of the row
            tag_map = {"thead": "header", "tfoot": "footer", "tbody": "body"}
            localname = QName(cals_parent.tag).localname
            nature = tag_map[localname]

            # -- attribute @cals:valign
            valign = cals_parent.attrib.get(cals("valign"))
            valign_map = {'top': 'top', 'middle': 'middle', 'bottom': 'bottom'}
            if valign in valign_map:
                styles["vertical-align"] = valign_map[valign]

        # -- attribute @cals:valign
        valign = cals_row.attrib.get(cals("valign"))
        valign_map = {'top': 'top', 'middle': 'middle', 'bottom': 'bottom'}
        if valign in valign_map:
            # overrides parent's value
            styles["vertical-align"] = valign_map[valign]

        # -- attribute @cals:rowsep
        rowsep = cals_row.attrib.get(cals("rowsep"))
        rowsep_map = {"0": BORDER_NONE, "1": BORDER_SOLID}
        if rowsep in rowsep_map:
            styles["border-bottom"] = rowsep_map[rowsep]

        # -- attribute @cals:bgcolor
        bgcolor = cals_row.attrib.get(cals("bgcolor"))
        if bgcolor:
            styles["background-color"] = bgcolor

        # -- attribute @cals:rowstyle (extension)
        rowstyle = cals_row.attrib.get(cals("rowstyle"))
        if rowstyle:
            # overrides the previously calculated @cals:rowstyle attribute
            styles["rowstyle"] = rowstyle

        # -- Create a row
        state = self._state
        state.row = state.table.rows[state.row_pos]
        state.row.nature = nature
        state.row.styles = styles

        return state  # mainly for unit test

    def parse_cals_entry(self, cals_entry):
        """
        Parse a ``entry`` element.

        :type  cals_entry: ElementType
        :param cals_entry: table entry

        .. versionchanged:: 0.5.1
           The "vertical-align" style is built from the ``@cals:valign`` attribute.
        """
        cals = self.get_cals_qname
        styles = {}
        nature = self._state.row.nature

        # -- attribute @cals:colsep
        colsep = cals_entry.attrib.get(cals("colsep"))
        colsep_map = {"0": BORDER_NONE, "1": BORDER_SOLID}
        if colsep in colsep_map:
            styles["border-right"] = colsep_map[colsep]

        # -- attribute @cals:rowsep
        rowsep = cals_entry.attrib.get(cals("rowsep"))
        rowsep_map = {"0": BORDER_NONE, "1": BORDER_SOLID}
        if rowsep in rowsep_map:
            styles["border-bottom"] = rowsep_map[rowsep]

        # -- attribute @cals:bgcolor
        bgcolor = cals_entry.attrib.get(cals("bgcolor"))
        if bgcolor:
            styles["background-color"] = bgcolor

        # -- attributes @cals:namest and @cals:nameend
        name_start = cals_entry.attrib.get(cals("namest"), str(self._state.col_pos))
        name_end = cals_entry.attrib.get(cals("nameend"), str(self._state.col_pos))
        col_start = int(re.findall(r"\d+", name_start)[0])
        col_end = int(re.findall(r"\d+", name_end)[0])
        width = col_end - col_start + 1

        # -- attribute @cals:morerows
        morerows = cals_entry.attrib.get(cals("morerows"), "0")
        height = int(morerows) + 1

        # -- attribute @cals:valign
        valign = cals_entry.attrib.get(cals("valign"))
        valign_map = {'top': 'top', 'middle': 'middle', 'bottom': 'bottom'}
        if valign in valign_map:
            # overrides parent's value
            styles["vertical-align"] = valign_map[valign]

        # -- attribute @cals:rowsep
        align = cals_entry.attrib.get(cals("align"))
        align_map = {"left": "left", "right": "right", "center": "center", "justify": "justify", "char": "left"}
        if align in align_map:
            styles["align"] = align_map[align]

        # todo: calculate the ``@rotate`` attribute.

        # -- Create a entry
        text = [cals_entry.text] if cals_entry.text else []
        content = text + cals_entry.getchildren()
        self._state.row.insert_cell(content, width=width, height=height, styles=styles, nature=nature)

        return self._state  # mainly for unit test

    def parse_cals_colspec(self, cals_colspec):
        """
        Parse a CALS-like ``colspec`` element.

        For instance:

        .. code-block:: xml

           <colspec
             colname="c1"
             colnum="1"
             colsep="1"
             rowsep="1"
             colwidth="30mm"
             align="center"/>

        :type  cals_colspec: ElementType
        :param cals_colspec: CALS-like ``colspec`` element.
        """
        cals_parent = cals_colspec.getparent()
        if cals_parent is not None:  # pragma: no cover
            localname = QName(cals_parent).localname
            if localname not in {"table", "tgroup"}:
                raise NotImplementedError("colspec in {} not supported".format(localname))

        cals = self.get_cals_qname
        styles = {}

        # -- attribute @cals:colname is ignored
        # -- attribute @cals:char is ignored
        # -- attribute @cals:charoff is ignored

        # -- attribute @cals:colnum
        colnum = cals_colspec.attrib.get(cals("colnum"))
        colnum = int(colnum) if colnum else self._state.col_pos

        # -- attribute @cals:colsep
        colsep = cals_colspec.attrib.get(cals("colsep"))
        colsep_map = {"0": BORDER_NONE, "1": BORDER_SOLID}
        if colsep in colsep_map:
            styles["border-right"] = colsep_map[colsep]

        # -- attribute @cals:rowsep
        rowsep = cals_colspec.attrib.get(cals("rowsep"))
        rowsep_map = {"0": BORDER_NONE, "1": BORDER_SOLID}
        if rowsep in rowsep_map:
            styles["border-bottom"] = rowsep_map[rowsep]

        # -- attribute @cals:rowsep
        colwidth = cals_colspec.attrib.get(cals("colwidth"))
        if colwidth:
            styles["width"] = colwidth

        # -- attribute @cals:rowsep
        align = cals_colspec.attrib.get(cals("align"))
        align_map = {"left": "left", "right": "right", "center": "center", "justify": "justify", "char": "left"}
        if align in align_map:
            styles["align"] = align_map[align]

        state = self._state
        state.col = state.table.cols[colnum]
        state.col.styles.update(styles)

        return state
