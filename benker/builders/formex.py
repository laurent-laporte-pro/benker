# coding: utf-8
"""
Formex 4 Builder
================

This module can construct a Formex 4 table from
an instance of type :class:`~benker.table.Table`.

:abbr:`Formex (Formalized Exchange of Electronic Publications)` describes the format for the exchange
of data between the Publication Office and its contractors. In particular, it defines the logical
markup for documents which are published in the different series of the Official Journal
of the European Union.

This builder allow you to convert Word document tables
into Formex 4 tables using the Formex 4 schema (formex-05.59-20170418.xd).

Specifications and examples:

- The Formex 4 documentation and schema is available online in the Publication Office:
  `Formex Version 4 <https://publications.europa.eu/en/web/eu-vocabularies/formex>`_.

- An example of Formex 4 table is available in the Schema documentation:
  `TBL <https://publications.europa.eu/documents/3938058/5910419/formex_manual_on_screen_version.html/#TBL>`_

.. versionchanged:: 0.5.0
   Refactoring (rename "Formex4" to "Formex"):

   - the class ``Formex4Builder`` is renamed ``FormexBuilder``,
"""
import collections
import re

from lxml import etree

from benker.builders.base_builder import BaseBuilder
from benker.builders.cals import get_colsep_attr
from benker.builders.cals import get_frame_attr
from benker.builders.cals import get_rowsep_attr
from benker.common.lxml_iterwalk import iterwalk
from benker.common.lxml_qname import QName
from benker.schemas import CALS_NS
from benker.schemas import CALS_PREFIX
from benker.units import convert_value

# noinspection PyProtectedMember
#: ElementTree Type
ElementTreeType = etree._ElementTree

# noinspection PyProtectedMember
#: Element Type
ElementType = etree._Element

# noinspection PyProtectedMember
#: ProcessingInstructionType is an alias for type hints
ProcessingInstructionType = etree._ProcessingInstruction  # pylint: disable=C0103,W0212

text_type = type(u"")


def revision_mark(name, attrs):
    target = etree.tounicode(etree.Element(name, attrib=attrs))
    target = target.replace("<{0} ".format(name), "").replace("/>", "")
    rev_pi = etree.ProcessingInstruction(name, target)
    return rev_pi


RowInfo = collections.namedtuple("RowInfo", "tag, type, level")


def guess_row_info(rowstyle):
    if rowstyle is None:
        return RowInfo("ROW", None, 0)
    mo = re.match(
        r"""^
        (ROW | TI\.BLK | STI\.BLK)
        (?: - (ALIAS|HEADER|NORMAL|NOTCOL|TOTAL) )?
        (?: - level(\d+) )?
        $""",
        rowstyle,
        flags=re.VERBOSE,
    )
    if mo:
        info_tag = mo.group(1)
        info_type = mo.group(2)
        info_level = int(mo.group(3) or "0")
        return RowInfo(info_tag, info_type, info_level)
    return RowInfo("ROW", None, 0)


class FormexBuilder(BaseBuilder):
    """
    Formex 4 builder used to convert tables into ``TBL`` elements according to the
    `TBL Schema <https://publications.europa.eu/documents/3938058/5910419/formex_manual_on_screen_version.html/#TBL>`_
    """

    # fmt: off
    def __init__(
        self,
        detect_titles=False,
        use_cals=False,
        cals_ns=CALS_NS,
        cals_prefix=CALS_PREFIX,
        width_unit="mm",
        **options
    ):
        # fmt: on
        """
        Initialize the builder.

        :param detect_titles:
            If this option is enable, a title will be generated if the first row
            contains an unique cell with centered text.

        :param bool use_cals:
            Generate additional CALS-like elements and attributes
            to simplify the layout of Formex document in typesetting systems.

        :param str or None cals_ns:
            Namespace to use for CALS-like elements and attributes (requires: ``use_cals``).
            Set ``None`` (or "") if you don't want to use namespace.

        :param str or None cals_prefix:
            Namespace prefix to use for CALS-like elements and attributes (requires: ``use_cals``).

        :param str width_unit:
            Unit to use for column widths (requires: ``use_cals``).
            Possible values are: 'cm', 'dm', 'ft', 'in', 'm', 'mm', 'pc', 'pt', 'px'.

        :keyword options: Extra conversion options.
            See :meth:`~benker.converters.base_converter.BaseConverter.convert_file`
            to have a list of all possible options.

        .. versionchanged:: 0.5.1
           Add the *detect_titles* option.
        """
        # Internal state of the table used during building
        self._table = None
        self._table_colsep = u"0"  # for cals
        self._table_rowsep = u"0"  # for cals

        # NO.SEQ counter
        self._no_seq = 0

        # options
        self.detect_titles = detect_titles
        self.use_cals = use_cals
        self.cals_ns = cals_ns or None
        self.cals_prefix = cals_prefix or None
        self.width_unit = width_unit

        super(FormexBuilder, self).__init__(**options)

    @property
    def ns_map(self):
        if self.use_cals and self.cals_ns:
            return {self.cals_prefix: self.cals_ns}
        return {}

    def get_cals_qname(self, name):
        return QName(self.cals_ns, name)

    def generate_table_tree(self, table):
        """
        Build the XML table from the Table instance.

        :type  table: benker.table.Table
        :param table: Table

        :return: Table tree
        """
        table_elem = self.build_tbl(table)
        return table_elem

    def setup_table(self, table):
        self._table = table
        self._table_colsep = u"0"
        self._table_rowsep = u"0"
        return self._table  # mainly for unit tests

    def build_tbl(self, table):
        """
        Build the Formex 4 ``<TBL>`` element.

        Formex 4 attributes:

        -   ``@NO.SEQ`` This mandatory attribute provides a sequence number to the table.
            This number represents the order in which the table appears in the document.

        -   ``@CLASS`` The CLASS attribute is mandatory and is used to specify the type of data
            contained in the table. The allowed values are:

            *   GEN: if the table contains general data (default value),
            *   SCHEDULE: if it is a schedule,
            *   RECAP: if it is a synoptic table.

            These two last values are only used for documents related to the general budget.

        -   ``@COLS`` This mandatory attribute provides the actual number of columns of the table.

        -   ``@PAGE.SIZE`` The PAGE.SIZE attribute takes one of these values:

            *   DOUBLE.LANDSCAPE: table on two A4 pages forming an A3 landscape page,
            *   DOUBLE.PORTRAIT: table on two A4 pages forming an A3 portrait page,
            *   SINGLE.LANDSCAPE: table on a single A4 page in landscape,
            *   SINGLE.PORTRAIT: table on a single A4 page in portrait (default).

        :type  table: benker.table.Table
        :param table: Table

        :return: The newly-created ``<TBL>`` element.

        .. versionchanged:: 0.5.0
           Add support for CALS-like elements and attributes.
           Add support for ``bgcolor`` (Table background color).
        """
        self.setup_table(table)
        table_styles = table.styles
        self._no_seq += 1
        attrs = {
            "NO.SEQ": u"{:04d}".format(self._no_seq),
            # 'CLASS': u"GEN",  # default value
            "COLS": str(len(table.cols)),
            # 'PAGE.SIZE': u"SINGLE.PORTRAIT",  # default value
        }
        if "x-sect-orient" in table_styles:
            # size = (width x height) in 'pt'
            size = table_styles.get("x-sect-size", (595, 842))
            # C4 format 22.9cm x 32.4cm is a little bigger than A4
            if (size[0] <= 649 and size[1] <= 918) or (size[0] <= 918 and size[1] <= 649):
                orient_page_sizes = {"landscape": "SINGLE.LANDSCAPE"}
            else:
                orient_page_sizes = {"landscape": "DOUBLE.LANDSCAPE", "portrait": "DOUBLE.PORTRAIT"}
            orient = table_styles["x-sect-orient"]
            if orient in orient_page_sizes:
                attrs["PAGE.SIZE"] = orient_page_sizes[orient]

        table_elem = etree.Element(u"TBL", attrib=attrs, nsmap=self.ns_map)

        self.build_corpus(table_elem, table)
        return table_elem

    def build_corpus(self, tbl_elem, table):
        """
        Build the Formex 4 ``<CORPUS>`` element.

        :type  tbl_elem: ElementType
        :param tbl_elem: Parent element: ``<TBL>``.

        :type  table: benker.table.Table
        :param table: Table

        .. versionchanged:: 0.5.1
            If this option *detect_titles* is enable, a title will be generated
            if the first row contains an unique cell with centered text.
        """
        table_styles = table.styles
        attrs = {}  # no attribute
        rows = list(table.rows)

        if self.detect_titles:
            # Does the first row/cell contains a centered title?
            first_cell = table[(1, 1)]
            align = first_cell.styles.get("align")
            if first_cell.width == table.bounding_box.width and align == "center":
                # yes, we can generate the title
                self.build_title(tbl_elem, rows.pop(0))

        # support for CALS-like elements and attributes
        if self.use_cals:
            cals = self.get_cals_qname
            attrs[cals("frame")] = get_frame_attr(table_styles)
            self._table_colsep = attrs[cals("colsep")] = get_colsep_attr(table_styles) or "0"
            self._table_rowsep = attrs[cals("rowsep")] = get_rowsep_attr(table_styles) or "0"
            if table.nature is not None:
                attrs[cals("tabstyle")] = table.nature
            if "x-sect-orient" in table_styles:
                attrs[cals("orient")] = {"landscape": "land", "portrait": "port"}[table_styles["x-sect-orient"]]
            if "x-sect-cols" in table_styles:
                attrs[cals("pgwide")] = "1" if table_styles["x-sect-cols"] == "1" else "0"
            if "background-color" in table_styles:
                attrs[cals("bgcolor")] = table_styles["background-color"]

        corpus_elem = etree.SubElement(tbl_elem, u"CORPUS", attrib=attrs)

        # support for CALS-like elements and attributes
        if self.use_cals:
            for col in table.cols:
                self.build_colspec(corpus_elem, col)

        for row in rows:
            self.build_row(corpus_elem, row)

    def build_title(self, tbl_elem, row):
        """
        Build the table title using the ``<TITLE>`` element.

        For instance:

        .. code-block:: xml

           <TITLE>
             <TI>
               <P>Table IV</P>
             </TI>
           </TITLE>

        :type  tbl_elem: ElementType
        :param tbl_elem: Parent element: ``<TBL>``.

        :type  row: benker.table.RowView
        :param row: The row which contains the title.
        """
        title_elem = etree.SubElement(tbl_elem, u"TITLE")
        for cell in row.owned_cells:
            text = text_type(cell)
            if text:
                if isinstance(cell.content, type(u"")):
                    # mainly useful for unit test
                    ti_elem = etree.SubElement(title_elem, u"TI")
                    p_elem = etree.SubElement(ti_elem, u"P")
                    p_elem.text = cell.content
                else:
                    paragraphs = list(cell.content)
                    ti_elem = etree.SubElement(title_elem, u"TI")
                    ti_elem.append(paragraphs[0])
                    sti_elem = etree.SubElement(title_elem, u"STI")
                    sti_elem.extend(paragraphs[1:])
            else:
                # assert cell.content in {None, "", []}
                ti_elem = etree.SubElement(title_elem, u"TI")
                etree.SubElement(ti_elem, u"IE")

    def build_colspec(self, group_elem, col):
        """
        Build the CALS ``<colspec>`` element (only is *use_cals* is ``True``).

        CALS attributes:

        -   ``@colname`` is the column name. Its format is "c{col_pos}".

        -   ``@colwidth`` width of the column (with its unit).
            The unit is defined by the *width_unit* options.

        .. note::

           The ``@colnum`` attribute (number of column) is not generated
           because this value is usually implied, and can be deduce
           from the ``@colname`` attribute.

        :type  group_elem: ElementType
        :param group_elem: Parent element: ``<tgroup>``.

        :type  col: benker.table.ColView
        :param col: Columns

        .. versionchanged:: 0.5.0
           Add support for CALS-like elements and attributes.
        """
        col_styles = col.styles
        cals = self.get_cals_qname
        attrs = {cals("colname"): u"c{0}".format(col.col_pos)}
        if "width" in col_styles:
            width = col_styles["width"]
            width, unit = re.findall(r"([+-]?(?:[0-9]*[.])?[0-9]+)(\w+)", width)[0]
            value = convert_value(float(width), unit, self.width_unit)
            attrs[cals("colwidth")] = u"{value:0.2f}{unit}".format(value=value, unit=self.width_unit)
        etree.SubElement(group_elem, cals("colspec"), attrib=attrs)

    def build_row(self, corpus_elem, row):
        """
        Build the Formex 4 ``<ROW>`` element.

        Formex 4 attributes:

        -   ``@TYPE`` The TYPE attribute indicates the specific role of the row in the table.
            The allowed values are:

            *   ALIAS: if the row contains aliases. Such references may be used when the table
                is included on several pages of a publication. The references are associated
                to column headers on the first page and are repeated on subsequent pages.
            *   HEADER: if the row contains cells which may be considered as a column header.
                This generally occurs for the first row of a table.
            *   NORMAL: if most of the cells of the row contain 'simple' or 'normal' data.
                This is the default value.
            *   NOTCOL: if the cells of the row contain units of measure relating to subsequent rows.
            *   TOTAL: if the row contains data which could be considered as 'totals'.

            Note that this TYPE attribute is also provided for the cells (CELL), which could
            be used to override the value defined for the row. On the other hand, 'NORMAL'
            is the default value, so it is necessary to specify the TYPE attribute value
            in each cell of a row which has a specific type in order to avoid the default
            overriding (see the first row of the example below).

        :type  corpus_elem: ElementType
        :param corpus_elem: Parent element: ``<CORPUS>``.

        :type  row: benker.table.RowView
        :param row: The row.

        .. versionchanged:: 0.5.0
           Add support for CALS-like elements and attributes.
        """
        row_styles = row.styles
        attrs = {}
        nature_types = {"header": u"HEADER", "footer": u"__GR.NOTES__"}
        if row.nature in nature_types:
            attrs["TYPE"] = nature_types[row.nature]

        # support for CALS-like elements and attributes
        if self.use_cals:
            cals = self.get_cals_qname
            if "valign" in row_styles:
                # same values as CSS/Properties/vertical-align
                # fmt: off
                attrs[cals('valign')] = {
                    'top': 'top',
                    'middle': 'middle',
                    'bottom': 'bottom',
                    'baseline': 'bottom',
                }[row_styles['valign']]
                # fmt: on
            row_rowsep = get_rowsep_attr(row_styles, "border-bottom")
            if row_rowsep and row_rowsep != self._table_rowsep:
                attrs[cals("rowsep")] = row_rowsep
            if "rowstyle" in row_styles:
                attrs[cals("rowstyle")] = row_styles["rowstyle"]
            if "background-color" in row_styles:
                attrs[cals("bgcolor")] = row_styles["background-color"]

        if "x-ins" in row_styles:
            # <?change-start change-id="ct140446841083680" type="row:insertion"
            #   creator="Anita BARREL" date="2017-11-15T11:46:00"?>
            rev_attrs = collections.OrderedDict({'type': 'row:insertion'})
            if 'x-ins-id' in row_styles:
                rev_attrs['change-id'] = "ct{0}".format(row_styles['x-ins-id'])
            if 'x-ins-author' in row_styles:
                rev_attrs['creator'] = row_styles['x-ins-author']
            if 'x-ins-date' in row_styles:
                rev_attrs['date'] = row_styles['x-ins-date']
            rev_pi = revision_mark("change-start", rev_attrs)
            corpus_elem.append(rev_pi)

        row_elem = etree.SubElement(corpus_elem, u"ROW", attrib=attrs)

        if "x-ins" in row_styles:
            # <?change-end change-id="ct139821811327752" type="row:insertion"?>
            rev_attrs = collections.OrderedDict({'type': 'row:insertion'})
            if 'x-ins-id' in row_styles:
                rev_attrs['change-id'] = "ct{0}".format(row_styles['x-ins-id'])
            rev_pi = revision_mark('change-end', rev_attrs)
            corpus_elem.append(rev_pi)

        for cell in row.owned_cells:
            self.build_cell(row_elem, cell, row)

    # noinspection PyMethodMayBeStatic
    def build_cell(self, row_elem, cell, row):
        """
        Build the Formex 4 ``<CELL>`` element.

        Formex 4 attributes:

        -   ``@COL`` The mandatory COL attribute is used to specify in which column the cell is located.

        -   ``@COLSPAN`` When a cell in a row 'A' must be linked to a group of cells in the same row,
            the first CELL element of this group has to provide the COLSPAN attribute. The value of
            the COLSPAN attribute is the number of cells in the group. The COL attribute of the first
            cell indicates the number of the first column in the group.

            The use of the COLSPAN attribute is only allowed to relate the value of a cell in several
            columns within the same row. Its value must be at least equal to '2'.

        -   ``@ROWSPAN`` When a cell in column 'A' is linked to a cell in row 'B' located just below
            row 'A', the CELL element of this single cell must provide the ROWSPAN attribute.
            The value of the ROWSPAN attribute is equal to the number of cells in the group.
            The CELL element relating to the single cell must be placed within the first ROW element
            in the group. The ROW elements corresponding to the other rows in the group may not
            contain any CELL elements for the column containing the single cell 'A'.

            The use of the ROWSPAN attribute is only authorised to relate the value of a cell in several
            rows. Its value must be at least equal to '2'.

        -   ``@ACCH`` If the group of related cells is physically delimited by a horizontal brace,
            this symbol must be marked up using the ACCH attribute.

        -   ``@ACCV`` If the group of related cells is physically delimited by a vertical brace,
            this symbol must be marked up using the ACCV attribute.

        -   ``@TYPE`` The TYPE attribute of the CELL element is used to indicate locally the type
            of contents of the cells. It overrides the value of the TYPE attribute defined for
            the row (ROW) which contains the cell.

        :type  row_elem: ElementType
        :param row_elem: Parent element: ``<ROW>``.

        :type  cell: benker.cell.Cell
        :param cell: The cell.

        :type  row: benker.table.RowView
        :param row: The parent row.

        .. versionchanged:: 0.5.0
           Add support for CALS-like elements and attributes.
           Add support for ``bgcolor`` (Table background color).
        """
        cell_styles = cell.styles
        attrs = {"COL": str(cell.box.min.x)}
        if cell.nature and cell.nature != row.nature:
            nature_types = {"header": u"HEADER", "body": u"NORMAL", "footer": u"__GR.NOTES__"}
            attrs["TYPE"] = nature_types[cell.nature]
        if cell.width > 1:
            attrs[u"COLSPAN"] = str(cell.width)
        if cell.height > 1:
            attrs[u"ROWSPAN"] = str(cell.height)

        # support for CALS-like elements and attributes
        if self.use_cals:
            cals = self.get_cals_qname
            if cell.box.max.x != self._table.bounding_box.max.x:
                # generate @colsep if the cell isn't in the last column
                cell_colsep = get_colsep_attr(cell_styles, "border-right")
                if cell_colsep and cell_colsep != self._table_colsep:
                    attrs[cals("colsep")] = cell_colsep
            if cell.box.max.y != self._table.bounding_box.max.y:
                # generate @rowsep if the cell isn't in the last row
                cell_rowsep = get_rowsep_attr(cell_styles, "border-bottom")
                if cell_rowsep and cell_rowsep != self._table_rowsep:
                    attrs[cals("rowsep")] = cell_rowsep
            if "vertical-align" in cell_styles:
                # same values as CSS/Properties/vertical-align
                # 'w-both' is an extension of OoxmlParser
                attrs[cals('valign')] = {
                    'top': u'top',
                    'middle': u'middle',
                    'bottom': u'bottom',
                    'baseline': u'bottom',
                    'w-both': u'bottom',
                }[cell_styles['vertical-align']]
            if 'align' in cell_styles:
                # same values as CSS/Properties/text-align
                attrs[cals('align')] = {
                    'left': u'left',
                    'center': u'center',
                    'right': u'right',
                    'justify': u'justify',
                }[cell_styles['align']]
            if cell.width > 1:
                attrs[cals("namest")] = u"c{0}".format(cell.box.min.x)
                attrs[cals("nameend")] = u"c{0}".format(cell.box.max.x)
            if cell.height > 1:
                attrs[cals("morerows")] = str(cell.height - 1)
            if "background-color" in cell_styles:
                attrs[cals("bgcolor")] = cell_styles["background-color"]

        cell_elem = etree.SubElement(row_elem, u"CELL", attrib=attrs)
        text = text_type(cell)
        if text:
            if cell.content is not None:
                for node in cell.content:
                    # noinspection PyProtectedMember
                    if isinstance(node, ElementType):
                        cell_elem.append(node)
                    else:
                        text = cell_elem.text or ""
                        cell_elem.text = text + node
        else:
            # The IE element is used to explicitly indicate
            # that specific structures have an empty content.
            etree.SubElement(cell_elem, u"IE")

    def finalize_tree(self, tree):
        """
        Finalize the resulting tree structure:

        - Calculate the ``@NO.SEQ`` values: sequence number of each table;
        - Cleanup the ``TBL`` elements when they are direct children of another ``TBL``;
        - Extract ``GR.NOTES`` from the table footers;
        - Group ``ROW`` elements by ``BLK`` based on the ``@cals:rowstyle`` attribute (CALS extension).

        :type  tree: ElementTreeType
        :param tree: The resulting tree.
        """
        fmx_root = tree.getroot()
        self.update_no_seq(fmx_root)
        self.cleanup_tbl_in_tbl(fmx_root)
        self.extract_gr_notes(fmx_root)
        self.insert_blk(fmx_root)

    # noinspection PyMethodMayBeStatic
    def update_no_seq(self, fmx_root):
        """
        Calculate the ``@NO.SEQ`` values: sequence number of each table.

        :type  fmx_root: ElementType
        :param fmx_root: The result tree which contains the ``TBL`` elements to update.
        """
        context = iterwalk(fmx_root, events=("start",), tag=("TBL",))
        stack = []
        for action, elem in context:  # type: str, ElementType
            elem_level = int(elem.xpath("count(ancestor-or-self::TBL)"))
            curr_level = len(stack)
            if curr_level < elem_level:
                stack.extend([0] * (elem_level - curr_level))
            else:
                stack[:] = stack[:elem_level]
            stack[elem_level - 1] += 1
            no_seq = u".".join(u"{:04d}".format(value) for value in stack)
            elem.attrib["NO.SEQ"] = no_seq

    # noinspection PyMethodMayBeStatic
    def cleanup_tbl_in_tbl(self, fmx_root):
        """
        Cleanup the ``TBL`` elements when they are direct children of another ``TBL``

        :type  fmx_root: ElementType
        :param fmx_root: The result tree which contains the ``TBL`` elements to remove.
        """
        for fmx_tbl in fmx_root.xpath("//TBL"):  # type: ElementType
            fmx_parent = fmx_tbl.getparent()
            if fmx_parent is not None and fmx_parent.tag == "TBL":
                # note that we cannot use etree.strip_tags() because a TBL may contains another TBL.
                index = fmx_parent.index(fmx_tbl)
                fmx_parent[index:index + 1] = fmx_tbl.getchildren()

    # noinspection PyMethodMayBeStatic
    def extract_gr_notes(self, fmx_root):
        """
        Extract ``GR.NOTES`` from the table footers.

        :type  fmx_root: ElementType
        :param fmx_root: The result tree with ``GR.NOTES``.
        """
        for fmx_row in fmx_root.xpath("//ROW[@TYPE = '__GR.NOTES__']"):  # type: ElementType
            fmx_corpus = fmx_row.xpath("ancestor::CORPUS[1]")[0]  # type: ElementType
            fmx_tbl = fmx_corpus.getparent()
            attrib = {k: v for k, v in fmx_row.attrib.items() if k != "TYPE"}
            fmx_gr_notes = etree.Element("GR.NOTES", attrib=attrib)
            fmx_cell = fmx_row.xpath("CELL")[0]
            fmx_gr_notes.text = fmx_cell.text
            fmx_gr_notes.extend(fmx_cell.getchildren())
            index = fmx_tbl.index(fmx_corpus)
            fmx_tbl.insert(index, fmx_gr_notes)
            fmx_row.getparent().remove(fmx_row)

    def insert_blk(self, fmx_root):
        """
        Group ``ROW`` elements by ``BLK`` based on the ``@cals:rowstyle`` attribute (CALS extension).

        :type  fmx_root: ElementType
        :param fmx_root: The result tree which contains the ``CORPUS/ROW`` elements.
        """
        cals = self.get_cals_qname
        for fmx_corpus in fmx_root.xpath("//CORPUS"):  # type: ElementType
            stack = [fmx_corpus]
            for fmx_row in fmx_corpus.getchildren():  # type: ElementType
                if isinstance(fmx_row, ProcessingInstructionType):
                    # handle PIs (e.g.: revision marks)
                    fmx_top = stack[-1]
                    fmx_top.append(fmx_row)
                    continue
                rowstyle = fmx_row.get(cals("rowstyle"))
                row_info = guess_row_info(rowstyle)
                while len(stack) < row_info.level + 1:
                    fmx_top = stack[-1]
                    fmx_blk = etree.SubElement(fmx_top, "BLK")
                    stack.append(fmx_blk)
                while len(stack) > row_info.level + 1:
                    stack.pop()
                fmx_top = stack[-1]
                if row_info.tag == "ROW":
                    if row_info.type is not None:
                        fmx_row.set("TYPE", row_info.type)
                        for fmx_cell in fmx_row.xpath("CELL"):
                            fmx_cell.set("TYPE", row_info.type)
                    fmx_top.append(fmx_row)
                elif row_info.tag in {"TI.BLK", "STI.BLK"}:
                    # get the COL.START/COL.END integer values (**required**)
                    # find the first non-empty cell (usually this is the first one).
                    for col_pos, fmx_cell in enumerate(fmx_row.xpath("CELL"), 1):
                        if fmx_cell.xpath("self::CELL[string() != '' or count(IE) != 0]"):
                            name_start = fmx_cell.attrib.get(cals("namest"))
                            name_end = fmx_cell.attrib.get(cals("nameend"))
                            if name_start and name_end:
                                col_start = int(re.findall(r"\d+", name_start)[0])
                                col_end = int(re.findall(r"\d+", name_end)[0])
                            else:
                                col_start = col_end = col_pos
                            attrib = {"COL.START": text_type(col_start), "COL.END": text_type(col_end)}
                            break
                    else:
                        # unlikely to go here
                        fmx_cell = fmx_row.xpath("CELL")[0]
                        attrib = {"COL.START": u"1", "COL.END": u"1"}
                    attrib.update({k: v for k, v in fmx_row.attrib.items() if k != "TYPE"})
                    fmx_title = etree.SubElement(fmx_top, row_info.tag, attrib=attrib)
                    fmx_title.text = fmx_cell.text
                    fmx_title.extend(fmx_cell.getchildren())
                    fmx_corpus.remove(fmx_row)
                else:
                    raise NotImplementedError(row_info.tag)
