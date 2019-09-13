# coding: utf-8
"""
Formex4 Parser
==============

This module can parse the tables (``TBL`` elements) of a Formex 4 file.

The ``TBL`` element is used to mark up a Formex table, which actually contains text structured
in columns with related data.

A table usually contains the following information:

- an optional title (``TITLE``),
- one or more structured text blocks (``GR.SEQ``) in order to mark up optional explanatory
  information about the table content, located between the title of the table and the table itself,
- optionally a group of notes called in the table (``GR.NOTES``),
- the corpus of the table (``CORPUS``).

When building the internal table object, this builder will:

- interpret the title (``TITLE``) and structured text blocks (``GR.SEQ``) like rows.
  The *nature* attribute of each row will be "title" and "text-block" respectively.
- interpret the group of notes (``GR.NOTES``) like a row of *nature* "footer"
- interpret the corpus of the table (``CORPUS``) like the body of the table.
  The *nature* attribute of each row will be "body".

.. note::

   Since the Formex table structure is not suitable for typesetting/page layout, this parser is
   also able to parse CALS-like attributes (for instance ``frame``, ``cols``, ``colsep``,
   ``rowsep``, ...) and CALS-like elements (for instance ``colspec``). This attributes and
   elements may be added with the Formex 4 builder,
   see :class:`~benker.builders.formex4.Formex4Builder`.
"""

from lxml import etree

from benker.parsers.base_parser import BaseParser
from benker.parsers.lxml_iterwalk import iterwalk
from benker.schemas import CALS_NS
from benker.schemas import CALS_PREFIX
from benker.schemas import FORMEX_NS
from benker.schemas import FORMEX_PREFIX
from benker.table import Table

#: Default value for a solid border (for @cals:frame/@cals:colsep/@cals:rowsep, ...)
BORDER_SOLID = "solid 1pt black"

#: Default value for no border (for @cals:frame/@cals:colsep/@cals:rowsep, ...)
BORDER_NONE = "none"


def get_frame_styles(frame):
    styles = {}
    if not frame:
        return styles
    top, bottom, left, right = {
        "all": (True, True, True, True),
        "topbot": (True, True, False, False),
        "sides": (False, False, True, True),
        "top": (True, False, False, False),
        "bottom": (False, True, False, False),
    }[frame]
    styles["border-top"] = BORDER_SOLID if top else BORDER_NONE
    styles["border-bottom"] = BORDER_SOLID if bottom else BORDER_NONE
    styles["border-left"] = BORDER_SOLID if left else BORDER_NONE
    styles["border-right"] = BORDER_SOLID if right else BORDER_NONE
    return styles


class Formex4Parser(BaseParser):
    """
    Formex 4 tables parser
    """

    def __init__(
        self,
        builder,
        formex_ns=FORMEX_NS,
        formex_prefix=FORMEX_PREFIX,
        cals_ns=CALS_NS,
        cals_prefix=CALS_PREFIX,
        **options,
    ):
        """
        Construct a parser

        :type  builder: benker.builders.base_builder.BaseBuilder
        :param builder:
            Builder used by this parser to instantiate :class:`~benker.table.Table` objects.

        :param str formex_ns:
            Namespace to use for Formex elements and attributes.
            Set "" (empty) if you don't use namespace.

        :param str formex_prefix:
            Namespace prefix to use for Formex elements and attributes.

        :param str cals_ns:
            Namespace to use for CALS-like elements and attributes.
            Set "" (empty) if you don't use namespace.

        :param str cals_prefix:
            Namespace prefix to use for CALS-like elements and attributes.

        :keyword str options: Extra conversion options.
            See :meth:`~benker.converters.base_converter.BaseConverter.convert_file`
            to have a list of all possible options.
        """
        self.formex_ns = formex_ns
        self.formex_prefix = formex_prefix
        self.cals_ns = cals_ns
        self.cals_prefix = cals_prefix
        super(Formex4Parser, self).__init__(builder, **options)

    @property
    def ns_map(self):
        map = {}
        if self.formex_prefix and self.formex_ns:
            map[self.formex_prefix] = self.formex_ns
        if self.cals_prefix and self.cals_ns:
            map[self.cals_prefix] = self.cals_ns
        return map

    def get_formex_qname(self, name):
        if self.formex_prefix and self.formex_ns:
            return etree.QName(self.formex_ns, name)
        return name

    def get_cals_qname(self, name):
        if self.cals_prefix and self.cals_ns:
            return etree.QName(self.cals_ns, name)
        return name

    def get_formex_name(self, name):
        if self.formex_prefix and self.formex_ns:
            return "{prefix}:{name}".format(prefix=self.formex_prefix, name=name)
        return name

    def get_cals_name(self, name):
        if self.cals_prefix and self.cals_ns:
            return "{prefix}:{name}".format(prefix=self.cals_prefix, name=name)
        return name

    def transform_tables(self, tree):
        name = self.get_formex_name
        for node in tree.xpath("//{TBL}".format(TBL=name("TBL")), namespaces=self.ns_map):
            table = self.parse_table(node)
            table_elem = self.builder.generate_table_tree(table)
            parent = node.getparent()
            index = parent.index(node)
            parent.insert(index, table_elem)
            table_elem.tail = node.tail
            parent.remove(node)

    def parse_table(self, w_tbl):
        """
        Convert a Office Open XML ``<w:tbl>`` into CALS ``<table>``

        :type  w_tbl: etree._Element
        :param w_tbl: Office Open XML element.

        :rtype: etree._Element
        :return: CALS element.
        """
        state = self._state
        state.reset()

        # -- Formex elements
        fmx = self.get_formex_qname

        TBL = fmx("TBL")
        TITLE = fmx("TITLE")
        GR_SEQ = fmx("GR.SEQ")
        GR_NOTES = fmx("GR.NOTES")

        # CORPUS := (ROW | BLK]+
        CORPUS = fmx("CORPUS")
        ROW = fmx("ROW")
        CELL = fmx("CELL")

        # BLK := (TI.BLK, STI.BLK*)*, (ROW | BLK]*
        BLK = fmx("BLK")
        TI_BLK = fmx("TI.BLK")  # spanned cell
        STI_BLK = fmx("STI.BLK")  # spanned cell

        # -- CLAS-like elements
        cals = self.get_cals_qname

        colspec = cals("colspec")

        elements = {TBL, TITLE, GR_SEQ, GR_NOTES, CORPUS, ROW, CELL, BLK, TI_BLK, STI_BLK, colspec}
        context = iterwalk(w_tbl, events=("start", "end"), tag=elements)

        depth = 0
        for action, elem in context:
            elem_tag = elem.tag
            if elem_tag == TBL:
                if action == "start":
                    depth += 1
                else:
                    depth -= 1
            if depth > 1:
                # .. note:: context.skip_subtree() is not available for all version of lxml
                # This <TBL> element is inside the table.
                # It will be handled separately in another call to convert_tbl()
                continue
            if action == "start":
                if elem_tag == TBL:
                    self.parse_tbl(elem)

                elif elem_tag == TITLE:
                    state.next_row()
                    self.parse_title(elem)

                elif elem_tag == GR_SEQ:
                    state.next_row()
                    self.parse_gr_seq(elem)

                elif elem_tag == GR_NOTES:
                    state.next_row()
                    self.parse_gr_notes(elem)

                elif elem_tag == CORPUS:
                    # only a container
                    pass

                elif elem_tag == BLK:
                    # only a container
                    pass

                elif elem_tag == TI_BLK:
                    state.next_row()
                    self.parse_ti_blk(elem)

                elif elem_tag == STI_BLK:
                    state.next_row()
                    self.parse_sti_blk(elem)

                elif elem_tag == ROW:
                    state.next_row()
                    self.parse_row(elem)

                elif elem_tag == CELL:
                    state.next_col()
                    self.parse_cell(elem)

                elif elem_tag == colspec:
                    state.next_col()
                    self.parse_colspec(elem)

                else:
                    raise NotImplementedError(elem_tag)
            else:
                if elem_tag in {TITLE, GR_SEQ, GR_NOTES, TI_BLK, STI_BLK, ROW}:
                    # add missing entries
                    state.table.fill_missing("???")

        return state.table

    def parse_tbl(self, tbl_elem):
        """
        Parse a ``TBL`` element

        :type  tbl_elem: etree._Element
        :param tbl_elem: table
        """
        fmx = self.get_formex_qname
        cals = self.get_cals_qname

        styles = {}

        # -- attribute @fmx:NO.SEQ => ignored (computed)

        # -- attribute @fmx:CLASS
        cls = tbl_elem.attrib.get(fmx("CLASS"))
        if cls:
            styles["tabstyle"] = cls

        # -- attribute @fmx:COLS => ignored (*table.cols*)

        # -- attribute @fmx:PAGE.SIZE
        page_size = tbl_elem.attrib.get(fmx("PAGE.SIZE"))
        page_size_map = {
            "DOUBLE.LANDSCAPE": "landscape",
            "DOUBLE.PORTRAIT": "portrait",
            "SINGLE.LANDSCAPE": "landscape",
            "SINGLE.PORTRAIT": "portrait",
        }
        if page_size in page_size_map:
            styles["x-sect-orient"] = page_size_map[page_size]

        # support for CALS-like elements and attributes

        # -- attribute @cals:frame
        frame = tbl_elem.attrib.get(cals("frame"))
        styles.update(get_frame_styles(frame))

        # -- attribute @cals:colsep
        colsep = tbl_elem.attrib.get(cals("colsep"))
        colsep_map = {"0": BORDER_NONE, "1": BORDER_SOLID}
        if colsep in colsep_map:
            styles["x-cell-border-right"] = colsep_map[colsep]

        # -- attribute @cals:rowsep
        rowsep = tbl_elem.attrib.get(cals("rowsep"))
        rowsep_map = {"0": BORDER_NONE, "1": BORDER_SOLID}
        if rowsep in rowsep_map:
            styles["x-cell-border-bottom"] = rowsep_map[rowsep]

        # -- attribute @cals:orient
        orient = tbl_elem.attrib.get(cals("orient"))
        orient_map = {"land": "landscape", "port": "portrait"}
        if orient in orient_map:
            styles["x-sect-orient"] = orient_map[orient]

        # -- attribute @cals:pgwide
        pgwide = tbl_elem.attrib.get(cals("pgwide"))
        pgwide_map = {"0": "2", "1": "1"}
        if pgwide in pgwide_map:
            styles["x-sect-cols"] = pgwide_map[pgwide]

        # -- attribute @cals:bgcolor
        bgcolor = tbl_elem.attrib.get(cals("bgcolor"))
        if bgcolor:
            styles["background-color"] = bgcolor

        table = Table(styles=styles)
        self._state.table = table
        return self._state  # mainly for unit test

    def parse_title(self, title_elem, nature="title"):
        """
        Parse a ``TABLE``  element, considering it like a row of a single cell.

        :type  title_elem: etree._Element
        :param title_elem: table title

        :type  nature: str
        :param nature: nature of the row
        """
        fmx = self.get_formex_qname
        fmx_name = self.get_formex_name

        # -- find the TBL ancestor to get tht @fmx:COLS attribute
        xpath = "ancestor::{TBL}[1]".format(TBL=fmx_name("TBL"))
        tbl_elem = title_elem.xpath(xpath, namespaces=self.ns_map)[0]
        cols = int(tbl_elem.attrib.get(fmx("COLS"), "0"))

        # -- Create a ROW
        state = self._state
        state.row = state.table.rows[state.row_pos]
        state.row.nature = nature

        # -- Insert a single CELL
        content = title_elem.getchildren()
        state.row.insert_cell(content, width=cols)

        return state  # mainly for unit test

    def parse_gr_seq(self, gr_seq_elem):
        """
        Parse a ``GR.SEQ`` element, considering it like a row of a single cell.

        :type  gr_seq_elem: etree._Element
        :param gr_seq_elem: structured text blocks (``GR.SEQ``)
        """
        return self.parse_title(gr_seq_elem, nature="text-block")

    def parse_gr_notes(self, gr_notes_elem):
        """
        Parse a ``GR.NOTES`` element, considering it like a row of a single cell.

        :type  gr_notes_elem: etree._Element
        :param gr_notes_elem: group of notes called in the table (``GR.NOTES``)
        """
        return self.parse_title(gr_notes_elem, nature="footer")

    def parse_ti_blk(self, ti_blk_elem):
        """
        Parse a ``TI.BLK`` element, considering it like a row of a single cell.

        :type  ti_blk_elem: etree._Element
        :param ti_blk_elem: title of the ``BLK``.
        """
        return self.parse_title(ti_blk_elem, nature="title")

    def parse_sti_blk(self, sti_blk_elem):
        """
        Parse a ``STI.BLK`` element, considering it like a row of a single cell.

        :type  sti_blk_elem: etree._Element
        :param sti_blk_elem: subtitle of the ``BLK``.
        """
        return self.parse_title(sti_blk_elem, nature="subtitle")

    def parse_row(self, row_elem):
        """
        Parse a ``ROW`` element which contains ``CELL`` elements.

        This element may be in a ``BLK```

        :type  row_elem: etree._Element
        :param row_elem: table row

        :type  nature: str
        :param nature: nature of the row
        """
        fmx = self.get_formex_qname
        cals = self.get_cals_qname

        # -- attribute @fmx:MARGIN => Not implemented

        # -- attribute @fmx:TYPE => *nature*
        type_map = {"ALIAS": "header", "HEADER": "header", "NORMAL": "body", "NOTCOL": "body", "TOTAL": "footer"}
        row_type = row_elem.attrib.get(fmx("TYPE"))
        nature = type_map.get(row_type, "body")

        # -- Create a ROW
        state = self._state
        state.row = state.table.rows[state.row_pos]
        state.row.nature = nature

        return state  # mainly for unit test

    def parse_cell(self, cell_elem):
        """
        Parse a ``CELL`` element.

        :type  cell_elem: etree._Element
        :param cell_elem: table cell
        """
        fmx = self.get_formex_qname
        cals = self.get_cals_qname

        # -- attribute @fmx:COL => not used

        # -- attribute @fmx:COLSPAN
        width = int(cell_elem.attrib.get(fmx("COLSPAN"), "1"))

        # -- attribute @fmx:ROWSPAN
        height = int(cell_elem.attrib.get(fmx("ROWSPAN"), "1"))

        # -- attribute @fmx:TYPE
        row_nature = self._state.row.nature
        type_map = {"ALIAS": "header", "HEADER": "header", "NORMAL": "body", "NOTCOL": "body", "TOTAL": "footer"}
        cell_type = cell_elem.attrib.get(fmx("TYPE"))
        cell_nature = type_map.get(cell_type)
        nature = cell_nature or row_nature

        styles = {}

        # -- Create a CELL
        if cell_elem.xpath("IE"):
            content = ""
        else:
            text = [cell_elem.text] if cell_elem.text else []
            content = text + cell_elem.getchildren()
        self._state.row.insert_cell(content, width=width, height=height, styles=styles, nature=nature)

        return self._state  # mainly for unit test

    def parse_colspec(self, colspec_elem):
        """
        Parse a CALS-like ``colspec`` element.

        :type  colspec_elem: etree._Element
        :param colspec_elem: CALS-like ``colspec`` element.
        """
