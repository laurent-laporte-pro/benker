# coding: utf-8
"""
CALS Builder
============

This module can construct a CALS table from
an instance of type :class:`~benker.table.Table`.

Specifications and examples:

- The CALS DTD is available online in the OASIS web site:
  `CALS Table Model Document Type Definition <https://www.oasis-open.org/specs/a502.htm>`_.

- An example of CALS table is available in Wikipedia:
  `CALS Table Model <https://en.wikipedia.org/wiki/CALS_Table_Model>`_

"""
import itertools
import re

from lxml import etree

from benker.builders.base_builder import BaseBuilder
from benker.units import convert_value


def _get_border_style(styles, style):
    parts = styles.get(style, "")
    parts = parts.split(" ") if parts else []
    value = None
    for part in parts:
        if not part.endswith("pt") and part != "auto" and not part.startswith("#"):
            value = part
    return value


def _get_frame_attr(styles):
    frame_styles = {'border-top': False, 'border-right': False, 'border-bottom': False, 'border-left': False}
    for style in frame_styles:
        value = _get_border_style(styles, style) or u"none"
        frame_styles[style] = value != u"none"
    top = frame_styles['border-top']
    bottom = frame_styles['border-bottom']
    left = frame_styles['border-left']
    right = frame_styles['border-right']
    return {
        (True, True, True, True): u"all",
        (True, True, False, False): u"topbot",
        (False, False, True, True): u"sides",
        (True, False, False, False): u"top",
        (False, True, False, False): u"bottom",
    }.get((top, bottom, left, right), u"none")


def _get_colsep_attr(styles, style="x-cell-border-right"):
    value = _get_border_style(styles, style)
    return None if value is None else "0" if value == "none" else "1"


def _get_rowsep_attr(styles, style="x-cell-border-bottom"):
    value = _get_border_style(styles, style)
    return None if value is None else "0" if value == "none" else "1"


def revision_mark(name, attrs):
    target = etree.tounicode(etree.Element(name, attrib=attrs))
    target = target.replace("<{0} ".format(name), "").replace("/>", "")
    rev_pi = etree.ProcessingInstruction(name, target)
    return rev_pi


class CalsBuilder(BaseBuilder):
    """
    CALS table builder.
    """

    def __init__(self, width_unit="mm", table_in_tgroup=False, **options):
        """
        Initialize the builder.

        :param str width_unit:
            Unit to use for column widths.
            Possible values are: 'cm', 'dm', 'ft', 'in', 'm', 'mm', 'pc', 'pt', 'px'.

        :param bool table_in_tgroup:
            Where should we put the table properties:
            - ``False`` to put the properties in the ``<table>`` element,
            - ``True`` to put the properties in the ``<tgroup>`` element.

        :param str options: Extra conversion options.
            See :meth:`~benker.converters.base_converter.BaseConverter.convert_file`
            to have a list of all possible options.
        """
        # Internal state of the table used during building
        self._table = None
        self._table_colsep = u"0"
        self._table_rowsep = u"0"
        # options
        self.width_unit = width_unit
        self.table_in_tgroup = table_in_tgroup
        super(CalsBuilder, self).__init__(**options)

    def generate_table_tree(self, table):
        """
        Build the XML table from the Table instance.

        :type  table: benker.table.Table
        :param table: Table

        :return: Table tree
        """
        table_elem = self.build_table(table)
        return table_elem

    def build_table(self, table):
        """
        Build the CALS ``<table>`` element.

        CALS attributes:

        -   ``@colsep`` is built from the "x-cell-border-right" style.
            Default value is "0" (not displayed).

        -   ``@rowsep`` is built from the "x-cell-border-bottom" style.
            Default value is "0" (not displayed).

        -   ``@tabstyle`` is built from the table nature.

        -   ``@orient`` is built from the "x-sect-orient" style (orientation of the current section).
            Possible values are "port" (portrait, the default) or "land" (landscape).

        -   ``@pgwide`` is built from the "x-sect-cols" style (column number of the current section).
            Default value is "0" (width of the current column).

        .. note::

           ``@colsep``, ``@rowsep`` and ``@tabstyle`` attributes are generated only
           if the *table_in_tgroup* options is ``False``.

        .. attention::

           According to the `CALS specification <https://www.oasis-open.org/specs/tm9502.html#c37ab3>`_,
           the default value for ``@colsep`` and ``@rowsep`` should be "1".
           But, having this value as a default is really problematic for conversions:
           most of nowadays formats, like Office Open XML and CSS, consider that the default
           value is "no border" (a.k.a: ``border: none``).
           So, setting "0" as a default value is a better choice.

        :type  table: benker.table.Table
        :param table: Table

        :return: The newly-created ``<table>`` element.
        """
        self._table = table
        self._table_colsep = u"0"
        self._table_rowsep = u"0"
        table_styles = table.styles
        attrs = {'frame': _get_frame_attr(table_styles), }
        if not self.table_in_tgroup:
            self._table_colsep = attrs['colsep'] = _get_colsep_attr(table_styles) or "0"
            self._table_rowsep = attrs['rowsep'] = _get_rowsep_attr(table_styles) or "0"
            if table.nature is not None:
                attrs['tabstyle'] = table.nature
        if 'x-sect-orient' in table_styles:
            attrs['orient'] = {"landscape": "land", "portrait": "port"}[table_styles['x-sect-orient']]
        if 'x-sect-cols' in table_styles:
            attrs['pgwide'] = "1" if table_styles['x-sect-cols'] == "1" else "0"
        table_elem = etree.Element(u"table", attrib=attrs)
        self.build_tgroup(table_elem, table)
        return table_elem

    def build_tgroup(self, table_elem, table):
        """
        Build the CALS ``<tgroup>`` element.

        CALS attributes:

        -   ``@cols`` is the total number of columns.

        -   ``@colsep`` is built from the "x-cell-border-right" style.
            Default value is "0" (not displayed).

        -   ``@rowsep`` is built from the "x-cell-border-bottom" style.
            Default value is "0" (not displayed).

        -   ``@tgroupstyle`` is built from the table nature.

        .. note::

           ``@colsep``, ``@rowsep`` and ``@tgroupstyle`` attributes are generated only
           if the *table_in_tgroup* options is ``True``.

        :type  table_elem: etree.Element
        :param table_elem: Parent element: ``<table>``.

        :type  table: benker.table.Table
        :param table: Table

        :return: The newly-created ``<tgroup>`` element.
        """
        table_styles = table.styles
        attrs = {u'cols': str(len(table.cols))}
        if self.table_in_tgroup:
            self._table_colsep = attrs['colsep'] = _get_colsep_attr(table_styles) or "0"
            self._table_rowsep = attrs['rowsep'] = _get_rowsep_attr(table_styles) or "0"
            if table.nature is not None:
                attrs['tgroupstyle'] = table.nature
        group_elem = etree.SubElement(table_elem, u"tgroup", attrib=attrs)
        for col in table.cols:
            self.build_colspec(group_elem, col)
        # -- group rows by head/body/foot
        groups = [(k, list(g)) for k, g in itertools.groupby(table.rows, key=lambda r: r.nature)]
        # -- sort the groups in the order: head => foot => body
        groups = sorted(groups, key=lambda item: {"head": 0, "foot": 1, "body": 2}[item[0]])
        group_tags = {"head": u"thead", "body": u"tbody", "foot": u"tfoot"}
        for nature, row_list in groups:
            nature_tag = group_tags[nature]
            self.build_tbody(group_elem, row_list, nature_tag)

    # noinspection PyMethodMayBeStatic
    def build_colspec(self, group_elem, col):
        """
        Build the CALS ``<colspec>`` element.

        CALS attributes:

        -   ``@colname`` is the column name. Its format is "c{col_pos}".

        -   ``@colwidth`` width of the column (with its unit).
            The unit is defined by the *width_unit* options.

        .. note::

           The ``@colnum`` attribute (number of column) is not generated
           because this value is usually implied, and can be deduce
           from the ``@colname`` attribute.

        :type  group_elem: etree.Element
        :param group_elem: Parent element: ``<tgroup>``.

        :type  col: benker.table.ColView
        :param col: Columns
        """
        col_styles = col.styles
        attrs = {u'colname': u"c{0}".format(col.col_pos)}
        if 'width' in col_styles:
            width = col_styles['width']
            width, unit = re.findall(r"([+-]?(?:[0-9]*[.])?[0-9]+)(\w+)", width)[0]
            value = convert_value(float(width), unit, self.width_unit)
            attrs['colwidth'] = u"{value:0.2f}{unit}".format(value=value, unit=self.width_unit)
        etree.SubElement(group_elem, u"colspec", attrib=attrs)

    def build_tbody(self, group_elem, row_list, nature_tag):
        """
        Build the CALS ``<tbody>``, `<thead>``, or `<tfoot>`` element.

        :type  group_elem: etree.Element
        :param group_elem: Parent element: ``<tgroup>``.

        :param row_list: List of rows

        :param nature_tag: name of the tag: 'tbody', 'thead' or 'tfoot'.
        """
        nature_elem = etree.SubElement(group_elem, nature_tag)
        for row in row_list:
            self.build_row(nature_elem, row)

    def build_row(self, tbody_elem, row):
        """
        Build the CALS ``<row>`` element.

        CALS attributes:

        -   ``@valign`` is built from the "valign" style.
            Values can be "top", "middle", "bottom" (note: "baseline" is not supported).
            Default value is "bottom".

        .. note::

           A row can be marked as inserted if "x-ins" is defined in the row styles.
           Revision marks are inserted before and after a ``<row>``
           using a couple of processing-instructions.
           We use the ``<?change-start?>`` PI to mark the start of the inserted row,
           and the ``<?change-end?>`` PI to mark the end.

        :type  tbody_elem: etree.Element
        :param tbody_elem: Parent element: ``<tbody>``, `<thead>``, or `<tfoot>``.

        :type  row: benker.table.RowView
        :param row: The row.
        """
        # Possible attrs:
        # - Row height: min-height' or 'height'
        # - Insertion revision mark: 'x-ins', 'x-ins-id', 'x-ins-author', 'x-ins-date'
        # - Vertical align: 'valign'
        #
        row_styles = row.styles
        attrs = {}
        if 'valign' in row_styles:
            # same values as CSS/Properties/vertical-align
            attrs['valign'] = {'top': 'top',
                               'middle': 'middle',
                               'bottom': 'bottom',
                               'baseline': 'bottom'}[row_styles['valign']]

        if 'x-ins' in row_styles:
            # <?change-start change-id="ct140446841083680" type="row:insertion"
            #   creator="Anita BARREL" date="2017-11-15T11:46:00"?>
            rev_attrs = {'type': 'row:insertion'}
            if 'x-ins-id' in row_styles:
                rev_attrs['change-id'] = "ct{0}".format(row_styles['x-ins-id'])
            if 'x-ins-author' in row_styles:
                rev_attrs['creator'] = row_styles['x-ins-author']
            if 'x-ins-date' in row_styles:
                rev_attrs['date'] = row_styles['x-ins-date']
            rev_pi = revision_mark("change-start", rev_attrs)
            tbody_elem.append(rev_pi)

        row_elem = etree.SubElement(tbody_elem, u"row", attrib=attrs)

        if 'x-ins' in row_styles:
            # <?change-end change-id="ct139821811327752" type="row:insertion"?>
            rev_attrs = {'type': 'row:insertion'}
            if 'x-ins-id' in row_styles:
                rev_attrs['change-id'] = "ct{0}".format(row_styles['x-ins-id'])
            rev_pi = revision_mark('change-end', rev_attrs)
            tbody_elem.append(rev_pi)

        for cell in row.owned_cells:
            self.build_cell(row_elem, cell)

    # noinspection PyMethodMayBeStatic
    def build_cell(self, row_elem, cell):
        """
        Build the CALS ``<entry>`` element.

        CALS attributes:

        -   ``@colsep`` is built from the "border-right" style.
            Default value is "1" (displayed), so, it is better to always define it.
            This value is only set if different from the table ``@colsep`` value.

        -   ``@rowsep`` is built from the "border-bottom" style.
            Default value is "1" (displayed), so, it is better to always define it.
            This value is only set if different from the table ``@rowsep`` value.

        -   ``@valign`` is built from the "valign" style.
            Values can be "top", "middle", "bottom" (note: "baseline" is not supported).
            Default value is "bottom".

        -   ``@align`` is built from the "align" style.
            Values can be "left", "center", "right", or "justify".
            Default value is "left".
            note: paragraphs alignment should be preferred to cells alignment.

        -   ``@namest``/``@nameend`` are set when the cell is spanned horizontally.

        -   ``@morerows`` is set when the cell is spanned vertically.

        :type  row_elem: etree.Element
        :param row_elem: Parent element: ``<row>``.

        :type  cell: benker.cell.Cell
        :param cell: The cell.
        """
        cell_styles = cell.styles
        attrs = {}
        if cell.box.max.x != self._table.bounding_box.max.x:
            # generate @colsep if the cell isn't in the last column
            cell_colsep = _get_colsep_attr(cell_styles, "border-right")
            if cell_colsep and cell_colsep != self._table_colsep:
                attrs['colsep'] = cell_colsep
        if cell.box.max.y != self._table.bounding_box.max.y:
            # generate @rowsep if the cell isn't in the last row
            cell_rowsep = _get_rowsep_attr(cell_styles, "border-bottom")
            if cell_rowsep and cell_rowsep != self._table_rowsep:
                attrs['rowsep'] = cell_rowsep
        if 'vertical-align' in cell_styles:
            # same values as CSS/Properties/vertical-align
            # 'w-both' is an extension of OoxmlParser
            attrs['valign'] = {'top': u'top',
                               'middle': u'middle',
                               'bottom': u'bottom',
                               'baseline': u'bottom',
                               'w-both': u'bottom'}[cell_styles['vertical-align']]
        if 'align' in cell_styles:
            # same values as CSS/Properties/text-align
            attrs['align'] = {'left': u'left',
                              'center': u'center',
                              'right': u'right',
                              'justify': u'justify'}[cell_styles['align']]
        if cell.width > 1:
            attrs[u"namest"] = u"c{0}".format(cell.box.min.x)
            attrs[u"nameend"] = u"c{0}".format(cell.box.max.x)
        if cell.height > 1:
            attrs[u"morerows"] = str(cell.height - 1)

        entry_elem = etree.SubElement(row_elem, u"entry", attrib=attrs)
        if cell.content is not None:
            entry_elem.extend(cell.content)
