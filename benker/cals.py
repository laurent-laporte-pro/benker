# coding: ascii
"""
CALS Tables converter
=====================

This module can convert the Open XML tables into CALS tables,
by keeping the other XML elements unchanged in order to allow further XLST transformations.

The CALS DTD is available online in the OASIS web site:
`CALS Table Model Document Type Definition <https://www.oasis-open.org/specs/a502.htm>`_.

An example of CALS table is available in Wikipedia:
`CALS Table Model <https://en.wikipedia.org/wiki/CALS_Table_Model>`_

Open XML format
---------------

In Open XML document, tables are represented by ``w:tbl`` elements:

- The ``w:tbl`` element specifies a Table object.
  The details of the object consists of rows and cells and is structured much like an HTML table.
- ``w:tblPr`` specifies the table-wide properties for the table.
- ``w:tblGrid`` specifies the columns for the table.
- ``w:tr`` specifies a table row.
- ``w:tc`` specifies a table column.
- The ``w:gridSpan`` indicates a cell horizontally spanning multiple cells.
- Cells can also span vertically using the ``w:vMerge`` element in a ``w:tcPr`` element.

Conversion
----------

The CALS converter must convert according to the following table:

===============  =================  ===============
   **Element**       **Open XML**       **CALS**
===============  =================  ===============
Table             | <w:tbl>          | <table>
Table Grid        | <w:gridCol>      | <colspec>
Row               | <w:tr>           | <row>
Column            | <w:tc>           | <entry>
===============  =================  ===============

-  **frame** attribute values are ``top``, ``bottom``, ``topbot``, ``sides``, ``all`` and ``none``.
   To get this attribute value, *<w:tblBorders>* holds the sides of the frames. When the elements
   value are ``single`` then it will consider as a frame side.

      +-----------------------------+-----------------+
      |      Open xml               | Frame Attribute |
      +=============================+=================+
      | | <w:top w:val="single">    |       top       |
      +-----------------------------+-----------------+
      | | <w:bottom w:val="single"> |      bottom     |
      +-----------------------------+-----------------+
      | | <w:top w:val="single">    |                 |
      |                             |                 |
      | | <w:bottom w:val="single"> |      topbot     |
      +-----------------------------+-----------------+
      | | <w:left w:val="single">   |                 |
      |                             |                 |
      | | <w:right w:val="single">  |      sides      |
      +-----------------------------+-----------------+
      | | <w:top w:val="single">    |                 |
      |                             |                 |
      | | <w:bottom w:val="single"> |       all       |
      |                             |                 |
      | | <w:right w:val="single">  |                 |
      |                             |                 |
      | | <w:left w:val="single">   |                 |
      +-----------------------------+-----------------+


   **Notice**

   -  There is also another case to find the frame value with the *<w:tblBorders>* elements are ``none``.

      +-----------------------------+-----------------+
      |      Open xml               | Frame Attribute |
      +=============================+=================+
      | | <w:bottom w:val="none">   |                 |
      | |                           |                 |
      | | <w:left w:val="none">     |      top        |
      | |                           |                 |
      | | <w:right w:val="none">    |                 |
      +-----------------------------+-----------------+
      | | <w:top w:val="none">      |                 |
      | |                           |                 |
      | | <w:left w:val="none">     |     bottom      |
      | |                           |                 |
      | | <w:right w:val="none">    |                 |
      +-----------------------------+-----------------+
      | | <w:left w:val="none">     |                 |
      | |                           |     topbot      |
      | | <w:right w:val="none">    |                 |
      +-----------------------------+-----------------+
      | | <w:top w:val="none">      |                 |
      | |                           |                 |
      | | <w:bottom w:val="none">   |      sides      |
      +-----------------------------+-----------------+
      | | <w:top w:val="none">      |                 |
      | |                           |                 |
      | | <w:bottom w:val="none">   |      none       |
      | |                           |                 |
      | | <w:right w:val="none">    |                 |
      | |                           |                 |
      | | <w:left w:val="none">     |                 |
      +-----------------------------+-----------------+
      | | If there's no             |                 |
      | | <w:tblBorders> element    |       all       |
      +-----------------------------+-----------------+

- **orient** attribute values are either port or land. To get this value,
  ``@w:orient`` attribute from the element of <w:sectPr> holds the value. Default value is ``port``.

- **pgwide** attribute values are either 0 or 1. If the table width is larger than the page width,
  then the pgwide value is 1, if not the value is 0. Table width value can be determined from
  the ``<w:tblPr>`` element and page width can be calculated from the ``<w:pgSz>``
  within the ``<w:sectPr>`` tag.

- **cols** attribute values will be calculated by the number of ``<w:gridCol>`` elements within
  the ``<w:tblGrid>``.

- **colnum** attribute value are autogenerated unique number for each column starting from 1.

- **colname**  values are as same as **colnum** in addition with *col* as prefix.

- **colwidth** Get w:w attribute from the ``<w:gridCol>`` element and divide it by *1440*
  to convert it into inches, then multiply it by *25.4* with the converted value of inches
  into millimeter and it is suffixed with the following condition.

      +------------+-------------------+
      |  Omnibook  |  colwidth suffix  |
      +============+===================+
      |  pgwide=0  |     ``in``        |
      +------------+-------------------+
      |  pgwide=1  |     ``*``         |
      +------------+-------------------+

- **colsep** attribute will be either 0 or 1 decided by the ``<w:tc>`` element.
  If the current ``<w:tc>`` node has following siblings of ``<w:tc>`` element
  then the colsep value is *1*, if not the colsep value as *0*.

- **tbody** element will be generated when ``<w:tblHeader>`` element isn't within the ``<w:trPr>`` tag.

- **rowsep** attribute will be either 0 or 1 decided by the ``<w:tr>``.
  If the current ``<w:tr>`` node has following siblings of ``<w:tr>`` then the rowsep value is *1*,
  if not the rowsep value as *0*.

- **align** attribute value will be derived from the element ``<w:jc>`` within the ``<w:pPr>`` element.
  Default value is *left*.

- **thead** element will be generated when ``<w:tblHeader>`` element within the ``<w:trPr>`` tag.

- **valign** attribute values are either top or bottom or middle.
  This can be calculated from the ``<w:vAlign>`` element within the ``<w:tcPr>`` tag.
  If the value is *center* then it will be assumed as *middle*.

- **morerows** attribute value will be calculated by the number of ``<w:vMerge>``
  elements present in a vertical straddle of each ``<w:tr>``.

- **namest** attribute value will be derived by the current ``<w:tc>`` element column name.

- **nameend** attribute value will be derived by the column name of the count of ``<w:gridSpan>`` value.
"""
import functools
import itertools

from lxml import etree

from benker.table import RowView
from benker.table import Table

#: Namespace map used for xpath evaluation in Open XML documents
NS = {'w': "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def ns_name(ns, name):
    return '{' + ns + '}' + name


w = functools.partial(ns_name, NS['w'])


def value_of(element, xpath, default=None):
    """
    Take the first value of a xpath evaluation.

    :type  element: etree._Element
    :param element: Root element used to evaluate the xpath expression.

    :param str xpath: xpath expression.
        This expression will be evaluated using the :data:`NS` namespace.

    :param default: default value used if the xpath evaluation returns no result.

    :return: the first result or the *default* value.
    """
    nodes = element.xpath(xpath, namespaces=NS)
    return nodes[0] if nodes else default


class TblBorders(object):
    """
    Tables borders `<http://officeopenxml.com/WPtableBorders.php>`_
    """
    _none_values = ["nil", "none", "", None]
    _top = None
    _bottom = None
    _start = None
    _end = None
    _inside_h = None
    _inside_v = None

    def __init__(self, w_tbl_borders=None):
        if w_tbl_borders is None:
            return
        # only @w:val attribute is useful for CALS
        self._top = value_of(w_tbl_borders, "w:top/@w:val")
        self._bottom = value_of(w_tbl_borders, "w:bottom/@w:val")
        self._start = value_of(w_tbl_borders, "w:start/@w:val | w:left/@w:val")
        self._end = value_of(w_tbl_borders, "w:end/@w:val | w:right/@w:val")
        self._inside_h = value_of(w_tbl_borders, "w:insideH/@w:val")
        self._inside_v = value_of(w_tbl_borders, "w:insideV/@w:val")

    def update(self, other):
        """
        Update from another instance of table border.

        :type  other: TblBorders
        :param other: table borders.
        """

        def merge(x, y):
            return x if y is None else y

        self._top = merge(self._top, other._top)
        self._bottom = merge(self._bottom, other._bottom)
        self._start = merge(self._start, other._start)
        self._end = merge(self._end, other._end)
        self._inside_h = merge(self._inside_h, other._inside_h)
        self._inside_v = merge(self._inside_v, other._inside_v)

    @property
    def frame(self):
        top = self._top not in self._none_values
        bottom = self._bottom not in self._none_values
        left = self._start not in self._none_values
        right = self._end not in self._none_values
        return {
            (True, True, True, True): u"all",
            (True, True, False, False): u"topbot",
            (False, False, True, True): u"sides",
            (True, False, False, False): u"top",
            (False, True, False, False): u"bottom",
        }.get((top, bottom, left, right), u"none")

    @property
    def colsep(self):
        return u"0" if self._inside_h in self._none_values else u"1"

    @property
    def rowsep(self):
        return u"0" if self._inside_v in self._none_values else u"1"


def get_table_borders(w_styles, style_id):
    if w_styles is None or style_id is None:
        return TblBorders()
    w_style = value_of(w_styles, 'w:style[@w:styleId = "{0}"]'.format(style_id))
    if w_style is None:
        return TblBorders()
    based_on = value_of(w_style, 'w:basedOn/@w:val')
    tbl_borders = get_table_borders(w_styles, based_on)
    w_tbl_borders = value_of(w_style, 'w:tblPr/w:tblBorders')
    tbl_borders.update(TblBorders(w_tbl_borders))
    return tbl_borders


def convert_tbl(w_tbl, w_styles=None):
    """
    Convert a Open XML ``<w:tbl>`` into ``<table>``

    :type  w_tbl: etree._Element
    :param w_tbl: Open XML element.

    :type  w_styles: etree._Element
    :param w_styles:
        ``<w:styles>`` element containing the document styles.
        If missing, this element will be searched from the root element ``<pkg:package>``.

    :rtype: etree.Element
    :return: CALS element.
    """

    root_tree = w_tbl.getroottree()  # type: etree._Element
    w_styles = w_styles or value_of(root_tree, ".//w:styles")

    # Calculate the CALS table attributes
    # -----------------------------------

    attrs = {}

    # - tabstyle: The identifier for a table style defined for the application

    style_id = value_of(w_tbl, "w:tblPr/w:tblStyle/@w:val")
    if style_id:
        attrs['tabstyle'] = style_id

    # -- frame: Describes position of outer rulings.
    # -- colsep: display the internal column rulings to the right of each <entry>
    # -- rowsep: display the internal horizontal row ruling below each <entry>

    tbl_borders = get_table_borders(w_styles, style_id)
    w_tbl_borders = value_of(w_tbl, 'w:tblPr/w:tblBorders')
    tbl_borders.update(TblBorders(w_tbl_borders))
    attrs['frame'] = tbl_borders.frame
    attrs['colsep'] = tbl_borders.colsep
    attrs['rowsep'] = tbl_borders.rowsep

    # -- orient: Orientation of the entire <table>: "port" (default) or "land"
    # todo: 'orient' attribute

    # -- pgwide: Table width = 100% (if orient="port").
    # todo: 'pgwide' attribute
    # see: http://officeopenxml.com/WPtableLayout.php
    # see: http://officeopenxml.com/WPtableWidth.php

    table = Table(styles=attrs)

    elements = {name: w(name) for name in {'tbl', 'tblGrid', 'gridCol', 'tr', 'tc'}}

    events = ('start',)
    context = etree.iterwalk(w_tbl, events=events, tag=list(elements.values()))
    col_pos = 0
    row_num = 0
    curr_row = None
    for action, elem in context:
        elem_tag = elem.tag
        if action == 'start':
            if elem_tag == w('tblGrid'):
                col_pos = 0

            elif elem_tag == w('gridCol'):
                col_pos += 1

                # w:w => width of the column in twentieths of a point.
                width = float(elem.attrib[w('w')]) / 20  # pt
                styles = {
                    u"colname": "c{0}".format(col_pos),
                    u"colwidth": "{0:0.2f}pt".format(width)}
                col = table.cols[col_pos]
                col.styles.update(styles)

            elif elem_tag == w('tr'):
                col_pos = 0
                row_num += 1

                # w:tblHeader => the current row should be repeated at the top
                # of each new page on which the table is displayed.
                # This is a simple boolean property, so you can specify a val attribute of true or false.
                tbl_header = value_of(elem, "w:trPr/w:tblHeader")
                if tbl_header is not None:
                    tbl_header = value_of(elem, "w:trPr/w:tblHeader/@w:val", default=u"true")
                nature = {u"true": "head", u"false": "body", None: "body"}[tbl_header]
                curr_row = table.rows[row_num]
                curr_row.nature = nature = nature

            elif elem_tag == w('tc'):
                col_pos += 1

                # w:gridSpan => number of logical columns across which the cell spans
                width = int(value_of(elem, "w:tcPr/w:gridSpan/@w:val", default=u"1"))

                # w:vMerge => specifies that the cell is part of a vertically merged set of cells.
                w_v_merge = value_of(elem, "w:tcPr/w:vMerge")
                if w_v_merge is not None:
                    w_v_merge = value_of(elem, "w:tcPr/w:vMerge/@w:val", default=u"continue")
                if w_v_merge is None:
                    # no merge
                    height = 1
                elif w_v_merge == u"continue":
                    # the current cell continues a previously existing merge group
                    table.expand((col_pos, curr_row.row_pos - 1), height=1)
                    height = None
                elif w_v_merge == u"restart":
                    # the current cell starts a new merge group
                    height = 1
                else:
                    raise NotImplementedError(w_v_merge)

                if height:
                    content = elem.xpath('w:p | w:tbl', namespaces=NS)
                    curr_row.insert_cell(content, width=width, height=height)

        else:
            raise NotImplementedError(action)

    table_elem = export_table_to_cals(table)

    return table_elem


_GROUP_TAGS = {"head": u"thead", "body": u"tbody", "foot": u"tfoot"}


def _head_foot_body(item):
    key = item[0]
    value = {"head": 0, "foot": 1, "body": 2}[key]
    return value


def export_table_to_cals(table):
    # -- group rows by head/body/foot
    groups = [(k, list(g)) for k, g in itertools.groupby(table.rows, key=lambda r: r.nature)]

    # -- sort the groups in the order: head => foot => body
    groups = sorted(groups, key=_head_foot_body)

    # -- convert to cals
    table_elem = etree.Element(u"table", attrib=table.styles)
    group_elem = etree.SubElement(table_elem, u"tgroup", attrib={u'cols': str(len(table.cols))})
    for col in table.cols:
        etree.SubElement(group_elem, u"colspec", attrib=col.styles)
    for nature, row_list in groups:
        nature_tag = _GROUP_TAGS[nature]
        nature_elem = etree.SubElement(group_elem, nature_tag)
        for row in row_list:  # type: RowView
            row_elem = etree.SubElement(nature_elem, u"row", attrib=row.styles)
            for cell in row.owned_cells:
                cell_styles = cell.styles
                if cell.width > 1:
                    cell_styles[u"namest"] = "c{0}".format(cell.box.min.x)
                    cell_styles[u"nameend"] = "c{0}".format(cell.box.max.x)
                if cell.height > 1:
                    cell_styles[u"morerows"] = str(cell.height - 1)
                entry_elem = etree.SubElement(row_elem, u"entry", attrib=cell_styles)
                entry_elem.extend(cell.content)
    return table_elem


def convert_to_cals(src_path, dst_path, styles_path=None, encoding='utf-8'):
    """
    Parse a XML file and convert Open XML tables into CALS tables

    :param str src_path: source path of the XML file to read.
    :param str dst_path: destination path of the XML file.
    :param str styles_path: path of the Open XML styles (root element should be ``w:styles>``).
    :param str encoding: target encoding to use for XML writing.
    """
    tree = etree.parse(src_path)
    w_styles = etree.parse(styles_path) if styles_path else None
    for w_tbl in tree.xpath("//w:tbl", namespaces=NS):
        table = convert_tbl(w_tbl, w_styles=w_styles)
        parent = w_tbl.getparent()
        index = parent.index(w_tbl)
        parent.insert(index, table)
        table.tail = w_tbl.tail
        parent.remove(w_tbl)
    tree.write(dst_path, encoding=encoding, pretty_print=False)
