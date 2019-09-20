# coding: utf-8
"""
Formex 4 Parser
===============

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
   see :class:`~benker.builders.formex.FormexBuilder`.

.. versionadded:: 0.5.0
"""
import re

from lxml import etree

from benker.box import Box
from benker.common.lxml_iterwalk import iterwalk
from benker.common.namespace import Namespace
from benker.parsers.base_parser import BaseParser
from benker.table import Table

# noinspection PyProtectedMember
#: Element Type
ElementType = etree._Element

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


class FormexParser(BaseParser):
    """
    Formex 4 tables parser
    """

    def __init__(self, builder, formex_prefix=None, formex_ns=None, cals_prefix=None, cals_ns=None, **options):
        """
        Construct a parser

        :type  builder: benker.builders.base_builder.BaseBuilder
        :param builder:
            Builder used by this parser to instantiate :class:`~benker.table.Table` objects.

        :param str formex_ns:
            Namespace to use for Formex elements and attributes.
            Set ``None`` (or "") if you don't use namespace.

        :param str formex_prefix:
            Namespace prefix to use for Formex elements and attributes.
            If a prefix is defined, a namespace must also be defined.

        :param str cals_ns:
            Namespace to use for CALS-like elements and attributes.
            Set ``None`` (or "") if you don't use namespace.

        :param str cals_prefix:
            Namespace prefix to use for CALS-like elements and attributes.
            If a prefix is defined, a namespace must also be defined.

        :keyword str options: Extra conversion options.
            See :meth:`~benker.converters.base_converter.BaseConverter.convert_file`
            to have a list of all possible options.
        """
        self._ns_map = {}
        self.formex_ns = self._register_namespace(formex_prefix, formex_ns)
        self.cals_ns = self._register_namespace(cals_prefix, cals_ns)
        super(FormexParser, self).__init__(builder, **options)

    def _register_namespace(self, prefix, ns):
        ns = ns or None
        prefix = prefix or None
        if prefix and not ns:
            raise ValueError("prefix '{prefix}' defined without namespace".format(prefix=prefix))
        if prefix in self._ns_map and self._ns_map[prefix] != ns:
            if prefix:
                fmt = "prefix '{prefix}' is already mapped to '{ns}'"
            else:
                fmt = "default prefix is already mapped to '{ns}'"
            raise ValueError(fmt.format(prefix=prefix, ns=self._ns_map[prefix]))
        if ns:
            self._ns_map[prefix] = ns
        return Namespace(prefix, ns)

    @property
    def ns_map(self):
        return self._ns_map

    def transform_tables(self, tree):
        if self.formex_ns.uri:
            nodes = tree.xpath("//fmx:CORPUS", namespaces={"fmx": self.formex_ns.uri})
        else:
            nodes = tree.xpath("//CORPUS")
        for node in nodes:
            table = self.parse_table(node)
            table_elem = self.builder.generate_table_tree(table)
            parent = node.getparent()
            index = parent.index(node)
            parent.insert(index, table_elem)
            table_elem.tail = node.tail
            parent.remove(node)

    # noinspection PyPep8Naming
    def parse_table(self, fmx_corpus):
        """
        Convert a ``<CORPUS>`` Formex element into table object.

        :type  fmx_corpus: ElementType
        :param fmx_corpus: Formex element.

        :rtype: ElementType
        :return: Table.
        """
        state = self._state
        state.reset()

        # -- Formex elements
        fmx = self.formex_ns.get_qname

        CORPUS = fmx("CORPUS").text
        ROW = fmx("ROW").text
        CELL = fmx("CELL").text
        MARGIN = fmx("MARGIN").text
        BLK = fmx("BLK").text
        TI_BLK = fmx("TI.BLK").text
        STI_BLK = fmx("STI.BLK").text

        # -- CLAS-like elements
        cals = self.cals_ns.get_qname

        colspec = cals("colspec").text

        elements = {CORPUS, ROW, CELL, MARGIN, BLK, TI_BLK, STI_BLK, colspec}
        context = iterwalk(fmx_corpus, events=("start", "end"), tag=elements)

        depth = 0
        for action, elem in context:
            elem_tag = elem.tag
            if elem_tag == CORPUS:
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
                if elem_tag == CELL:
                    state.next_col()
                    self.parse_fmx_cell(elem)

                elif elem_tag == ROW:
                    state.next_row()
                    self.parse_fmx_row(elem)

                elif elem_tag == BLK:
                    # only a container
                    pass

                elif elem_tag == TI_BLK:
                    state.next_row()
                    self.parse_fmx_ti_blk(elem)

                elif elem_tag == STI_BLK:
                    state.next_row()
                    self.parse_fmx_sti_blk(elem)

                elif elem_tag == colspec:
                    state.next_col()
                    self.parse_fmx_colspec(elem)

                elif elem_tag == CORPUS:
                    self.parse_fmx_corpus(elem)

                elif elem_tag == MARGIN:
                    raise NotImplementedError("MARGIN is not supported yet")

                else:
                    raise NotImplementedError(elem_tag)
            else:
                if elem_tag in {ROW, TI_BLK, STI_BLK}:
                    bounding_box = Box(1, state.row_pos, len(state.table.cols), state.row_pos)
                    state.table.fill_missing(bounding_box, None, nature=state.row.nature)
                elif elem_tag == CORPUS:
                    # if there is a GR.NOTES, we create a row for it with the nature "footer"
                    if self.formex_ns.uri:
                        nodes = elem.xpath("preceding-sibling::fmx:GR.NOTES", namespaces={"fmx": self.formex_ns.uri})
                    else:
                        nodes = elem.xpath("preceding-sibling::GR.NOTES")
                    for fmx_gr_notes in nodes:
                        # Convert the GR.NOTES and remove it
                        state.next_row()
                        self.parse_gr_notes(fmx_gr_notes)
                        fmx_tbl = fmx_gr_notes.getparent()
                        fmx_tbl.remove(fmx_gr_notes)
                    state.table.fill_missing(state.table.bounding_box, None)

        return state.table

    def setup_table(self, styles=None, nature=None):
        table = Table(styles=styles, nature=nature)
        self._state.table = table
        return self._state

    def parse_fmx_corpus(self, fmx_corpus):
        fmx_tbl = fmx_corpus.getparent()
        styles, nature = self.parse_tbl_styles(fmx_tbl)

        # support for CALS-like elements and attributes
        cals = self.cals_ns.get_qname

        # -- attribute @cals:frame
        frame = fmx_corpus.attrib.get(cals("frame"))
        styles.update(get_frame_styles(frame))

        # -- attribute @cals:colsep
        colsep = fmx_corpus.attrib.get(cals("colsep"))
        colsep_map = {"0": BORDER_NONE, "1": BORDER_SOLID}
        if colsep in colsep_map:
            styles["x-cell-border-right"] = colsep_map[colsep]

        # -- attribute @cals:rowsep
        rowsep = fmx_corpus.attrib.get(cals("rowsep"))
        rowsep_map = {"0": BORDER_NONE, "1": BORDER_SOLID}
        if rowsep in rowsep_map:
            styles["x-cell-border-bottom"] = rowsep_map[rowsep]

        # -- attribute @cals:orient
        orient = fmx_corpus.attrib.get(cals("orient"))
        orient_map = {"land": "landscape", "port": "portrait"}
        if orient in orient_map:
            styles["x-sect-orient"] = orient_map[orient]

        # -- attribute @cals:pgwide
        pgwide = fmx_corpus.attrib.get(cals("pgwide"))
        pgwide_map = {"0": "2", "1": "1"}
        if pgwide in pgwide_map:
            styles["x-sect-cols"] = pgwide_map[pgwide]

        # -- attribute @cals:bgcolor
        bgcolor = fmx_corpus.attrib.get(cals("bgcolor"))
        if bgcolor:
            styles["background-color"] = bgcolor

        # -- attribute @cals:tabstyle
        tabstyle = fmx_corpus.attrib.get(cals("tabstyle"))
        if tabstyle:
            # overrides the calculated tabstyle (see @fmx:CLASS)
            nature = nature + "-" + tabstyle if nature else tabstyle

        return self.setup_table(styles, nature)

    def parse_tbl_styles(self, fmx_tbl):
        """
        Parse a ``TBL`` element and extract the styles

        :type  fmx_tbl: ElementType
        :param fmx_tbl: table

        :return: dictionary of styles and nature
        """
        if fmx_tbl is None:
            # mainly for unit tests
            return {}, None

        fmx = self.formex_ns.get_qname
        styles = {}

        # -- attribute @fmx:NO.SEQ => ignored (computed)

        # -- attribute @fmx:CLASS => @cals:tabstyle or @cals:tgroupstyle
        nature = fmx_tbl.attrib.get(fmx("CLASS"))

        # -- attribute @fmx:COLS => ignored (*table.cols*)

        # -- attribute @fmx:PAGE.SIZE
        page_size = fmx_tbl.attrib.get(fmx("PAGE.SIZE"))
        page_size_map = {
            "DOUBLE.LANDSCAPE": "landscape",
            "DOUBLE.PORTRAIT": "portrait",
            "SINGLE.LANDSCAPE": "landscape",
            "SINGLE.PORTRAIT": "portrait",
        }
        if page_size in page_size_map:
            styles["x-sect-orient"] = page_size_map[page_size]

        return styles, nature

    def parse_fmx_row(self, fmx_row):
        """
        Parse a ``ROW`` element which contains ``CELL`` elements.

        This element may be in a ``BLK```

        :type  fmx_row: ElementType
        :param fmx_row: table row
        """
        fmx = self.formex_ns.get_qname
        styles = {}

        # -- attribute @fmx:TYPE => *nature*
        type_map = {"ALIAS": "header", "HEADER": "header", "NORMAL": "body", "NOTCOL": "body", "TOTAL": "body"}
        row_type = fmx_row.attrib.get(fmx("TYPE"))
        nature = type_map.get(row_type, "body")

        # the @fmx:TYPE is preserved in a @cals:rowstyle
        # the BLK level is also stored in this attribute
        blk_count = self._count_blk(fmx_row)
        blk_level = "level{count}".format(count=blk_count) if blk_count else None
        row_styles = list(filter(None, [row_type, blk_level]))
        if row_styles:
            styles["rowstyle"] = "-".join(["ROW"] + row_styles)

        # support for CALS-like elements and attributes
        cals = self.cals_ns.get_qname

        # -- attribute @cals:rowstyle (extension)
        rowstyle = fmx_row.attrib.get(cals("rowstyle"))
        if rowstyle:
            # overrides the previously calculated @cals:rowstyle attribute
            styles["rowstyle"] = rowstyle

        # -- attribute @cals:valign (extension)
        valign = fmx_row.attrib.get(cals("valign"))
        valign_map = {'top': 'top', 'middle': 'middle', 'bottom': 'bottom'}
        if valign in valign_map:
            styles["valign"] = valign_map[valign]

        # -- attribute @cals:rowsep
        rowsep = fmx_row.attrib.get(cals("rowsep"))
        rowsep_map = {"0": BORDER_NONE, "1": BORDER_SOLID}
        if rowsep in rowsep_map:
            styles["border-bottom"] = rowsep_map[rowsep]

        # -- Create a ROW
        state = self._state
        state.row = state.table.rows[state.row_pos]
        state.row.nature = nature
        state.row.styles = styles

        return state  # mainly for unit test

    def parse_fmx_ti_blk(self, fmx_ti_blk):
        """
        Parse a ``TI.BLK`` element, considering it like a row of a single cell.

        For instance:

        .. code-block:: xml

           <TI.BLK COL.START="1" COL.END="2">
             <P><HT TYPE="BOLD">TI.BLK title</HT></P>
           </TI.BLK>

        :type  fmx_ti_blk: ElementType
        :param fmx_ti_blk: title of the ``BLK``.
        """
        styles = {}

        # the @fmx:TYPE is preserved in a @cals:rowstyle
        # the BLK level is also stored in this attribute
        blk_count = self._count_blk(fmx_ti_blk)
        blk_level = "TI.BLK-level{count}".format(count=blk_count)
        styles["rowstyle"] = blk_level

        return self._insert_blk_title_row(fmx_ti_blk, styles)

    def parse_fmx_sti_blk(self, fmx_sti_blk):
        """
        Parse a ``STI.BLK`` element, considering it like a row of a single cell.

        For instance:

        .. code-block:: xml

           <STI.BLK COL.START="1" COL.END="1">
             <P>STI.BLK title</P>
           </STI.BLK>

        :type  fmx_sti_blk: ElementType
        :param fmx_sti_blk: subtitle of the ``BLK``.
        """
        styles = {}

        # the @fmx:TYPE is preserved in a @cals:rowstyle
        # the BLK level is also stored in this attribute
        blk_count = self._count_blk(fmx_sti_blk)
        blk_level = "STI.BLK-level{count}".format(count=blk_count)
        styles["rowstyle"] = blk_level

        return self._insert_blk_title_row(fmx_sti_blk, styles)

    def parse_gr_notes(self, fmx_gr_notes):
        """
        Parse a ``GR.NOTES`` element, considering it like a row of a single cell.

        For instance:

        .. code-block:: xml

           <GR.NOTES>
             <TITLE>
               <TI>
                 <P>GR.NOTES Title</P>
               </TI>
             </TITLE>
             <NOTE NOTE.ID="N0001">
               <P>Table note</P>
             </NOTE>
           </GR.NOTES>

        :type  fmx_gr_notes: ElementType
        :param fmx_gr_notes: group of notes called in the table (``GR.NOTES``)
        """
        # -- Create a ROW
        state = self._state
        state.row = state.table.rows[state.row_pos]
        state.row.nature = "footer"

        # -- Create a CELL
        if self._contains_ie(fmx_gr_notes):
            content = ""
        else:
            text = [fmx_gr_notes.text] if fmx_gr_notes.text else []
            content = text + fmx_gr_notes.getchildren()
        state.row.insert_cell(content, width=state.table.bounding_box.width, height=1, nature=state.row.nature)

        return state

    def _count_blk(self, fmx_node):
        if self.formex_ns.uri:
            blk_count = len(fmx_node.xpath("ancestor::fmx:BLK", namespaces={"fmx": self.formex_ns.uri}))
        else:
            blk_count = len(fmx_node.xpath("ancestor::BLK"))
        return blk_count

    def _insert_blk_title_row(self, fmx_blk_title, styles):
        # -- Create a ROW
        state = self._state
        state.row = state.table.rows[state.row_pos]
        state.row.nature = "body"
        state.row.styles = styles

        fmx = self.formex_ns.get_qname
        col_start = int(fmx_blk_title.attrib.get(fmx("COL.START"), "1"))
        col_end = int(fmx_blk_title.attrib.get(fmx("COL.END"), "1"))
        width = col_end - col_start + 1

        # -- Insert empty cells if necessary
        for x in range(1, col_start):
            state.row.insert_cell(None, nature=state.row.nature)

        # -- Create a CELL
        if self._contains_ie(fmx_blk_title):
            content = ""
        else:
            text = [fmx_blk_title.text] if fmx_blk_title.text else []
            content = text + fmx_blk_title.getchildren()
        state.row.insert_cell(content, width=width, height=1, nature=state.row.nature)

        return state

    def _contains_ie(self, fmx_node):
        return (self.formex_ns.uri and fmx_node.xpath("//fmx:IE", namespaces={"fmx": self.formex_ns.uri})) or (
            not self.formex_ns.uri and fmx_node.xpath("//IE")
        )

    def parse_fmx_cell(self, fmx_cell):
        """
        Parse a ``CELL`` element.

        :type  fmx_cell: ElementType
        :param fmx_cell: table cell
        """
        fmx = self.formex_ns.get_qname
        styles = {}

        # -- attribute @fmx:COL => not used

        # -- attribute @fmx:COLSPAN
        width = int(fmx_cell.attrib.get(fmx("COLSPAN"), "1"))

        # -- attribute @fmx:ROWSPAN
        height = int(fmx_cell.attrib.get(fmx("ROWSPAN"), "1"))

        # -- attribute @fmx:TYPE
        row_nature = self._state.row.nature
        type_map = {"ALIAS": "header", "HEADER": "header", "NORMAL": "body", "NOTCOL": "body", "TOTAL": "footer"}
        cell_type = fmx_cell.attrib.get(fmx("TYPE"))
        cell_nature = type_map.get(cell_type)
        nature = cell_nature or row_nature

        # support for CALS-like elements and attributes
        cals = self.cals_ns.get_qname

        # -- attribute @cals:colsep
        colsep = fmx_cell.attrib.get(cals("colsep"))
        colsep_map = {"0": BORDER_NONE, "1": BORDER_SOLID}
        if colsep in colsep_map:
            styles["x-cell-border-right"] = colsep_map[colsep]

        # -- attribute @cals:rowsep
        rowsep = fmx_cell.attrib.get(cals("rowsep"))
        rowsep_map = {"0": BORDER_NONE, "1": BORDER_SOLID}
        if rowsep in rowsep_map:
            styles["x-cell-border-bottom"] = rowsep_map[rowsep]

        # -- attribute @cals:bgcolor
        bgcolor = fmx_cell.attrib.get(cals("bgcolor"))
        if bgcolor:
            styles["background-color"] = bgcolor

        # -- attributes @cals:namest and @cals:nameend
        name_start = fmx_cell.attrib.get(cals("namest"))
        name_end = fmx_cell.attrib.get(cals("nameend"))
        if name_start and name_end:
            col_start = int(re.findall(r"\d+", name_start)[0])
            col_end = int(re.findall(r"\d+", name_end)[0])
            width = col_end - col_start + 1

        # -- attribute @cals:morerows
        morerows = fmx_cell.attrib.get(cals("morerows"))
        if morerows:
            height = int(morerows) + 1

        # -- Create a CELL
        if self._contains_ie(fmx_cell):
            content = ""
        else:
            text = [fmx_cell.text] if fmx_cell.text else []
            content = text + fmx_cell.getchildren()
        self._state.row.insert_cell(content, width=width, height=height, styles=styles, nature=nature)

        return self._state  # mainly for unit test

    def parse_fmx_colspec(self, cals_colspec):
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
        cals = self.cals_ns.get_qname
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
