# coding: utf-8
"""
Office Open XML to CALS tables converter
========================================

This module can convert the Office Open XML (OOXML) tables into CALS tables,
by keeping the other XML elements unchanged in order to allow further XSLT transformations.

Specifications and examples:

- The documentation about OOXML Table is available online at
  `Word Processing - Table Grid/Column Definition <http://officeopenxml.com/WPtableGrid.php>`_.

- The CALS DTD is available online in the OASIS web site:
  `CALS Table Model Document Type Definition <https://www.oasis-open.org/specs/a502.htm>`_.

- An example of CALS table is available in Wikipedia:
  `CALS Table Model <https://en.wikipedia.org/wiki/CALS_Table_Model>`_

Office Open XML format
----------------------

In Office Open XML document, tables are represented by ``w:tbl`` elements:

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

===============  ===================  ===============
  **Element**    **Office Open XML**       **CALS**
===============  ===================  ===============
Table             | <w:tbl>            | <table>
Table Grid        | <w:gridCol>        | <colspec>
Row               | <w:tr>             | <row>
Column            | <w:tc>             | <entry>
===============  ===================  ===============

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
import itertools

from lxml import etree

from benker.ooxml_parser import NS
from benker.ooxml_parser import OoxmlParser
from benker.ooxml_parser import value_of
from benker.table import Table


class CalsTable(Table):
    """
    Cals table object
    """

    def to_xml(self):
        # -- group rows by head/body/foot
        groups = [(k, list(g)) for k, g in itertools.groupby(self.rows, key=lambda r: r.nature)]

        # -- sort the groups in the order: head => foot => body
        groups = sorted(groups, key=lambda item: {"head": 0, "foot": 1, "body": 2}[item[0]])

        # -- convert to cals
        table_elem = etree.Element(u"table", attrib=self.styles)
        group_elem = etree.SubElement(table_elem, u"tgroup", attrib={u'cols': str(len(self.cols))})
        for col in self.cols:
            etree.SubElement(group_elem, u"colspec", attrib=col.styles)

        group_tags = {"head": u"thead", "body": u"tbody", "foot": u"tfoot"}
        for nature, row_list in groups:
            nature_tag = group_tags[nature]
            nature_elem = etree.SubElement(group_elem, nature_tag)
            for row in row_list:
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
    Parse a XML file and convert Office Open XML tables into CALS tables

    :param str src_path: source path of the XML file to read.
    :param str dst_path: destination path of the XML file.
    :param str styles_path: path of the Office Open XML styles (root element should be ``w:styles>``).
    :param str encoding: target encoding to use for XML writing.
    """
    tree = etree.parse(src_path)

    w_styles = etree.parse(styles_path) if styles_path else None
    w_styles = w_styles or value_of(tree, ".//w:styles")

    converter = OoxmlParser(CalsTable, w_styles)

    for w_tbl in tree.xpath("//w:tbl", namespaces=NS):
        table = converter.parse(w_tbl)
        table_elem = table.to_xml()
        parent = w_tbl.getparent()
        index = parent.index(w_tbl)
        parent.insert(index, table_elem)
        table_elem.tail = w_tbl.tail
        parent.remove(w_tbl)

    tree.write(dst_path, encoding=encoding, pretty_print=False)
