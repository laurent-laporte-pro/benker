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
    value = 'none'
    for part in parts:
        if not part.endswith("pt") and part != "auto" and not part.startswith("#"):
            value = part
    return value


def _get_frame_attr(styles):
    frame_styles = {'border-top': False, 'border-right': False, 'border-bottom': False, 'border-left': False}
    for style in frame_styles:
        value = _get_border_style(styles, style)
        frame_styles[style] = value != "none"
    top = frame_styles['border-top']
    bottom = frame_styles['border-top']
    left = frame_styles['border-top']
    right = frame_styles['border-top']
    return {
        (True, True, True, True): u"all",
        (True, True, False, False): u"topbot",
        (False, False, True, True): u"sides",
        (True, False, False, False): u"top",
        (False, True, False, False): u"bottom",
    }.get((top, bottom, left, right), u"none")


def _get_colsep_attr(styles):
    value = _get_border_style(styles, "x-cell-border-right")
    return "0" if value is "none" else "1"


def _get_rowsep_attr(styles):
    value = _get_border_style(styles, "x-cell-border-bottom")
    return "0" if value is "none" else "1"


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
        table_styles = table.styles
        attrs = {'frame': _get_frame_attr(table_styles),}
        if not self.table_in_tgroup:
            attrs['colsep'] = _get_colsep_attr(table_styles)
            attrs['rowsep'] = _get_rowsep_attr(table_styles)
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
        table_styles = table.styles
        attrs = {u'cols': str(len(table.cols))}
        if self.table_in_tgroup:
            attrs['colsep'] = _get_colsep_attr(table_styles)
            attrs['rowsep'] = _get_rowsep_attr(table_styles)
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
        
        :param group_elem: 
        
        :type  col: benker.table.ColView
        :param col: 
        :return: 
        """
        col_styles = col.styles
        attrs = {u'colname': u"c{0}".format(col.col_pos),}
        if 'width' in col_styles:
            width = col_styles['width']
            width, unit = re.findall(r"([+-]?(?:[0-9]*[.])?[0-9]+)(\w+)", width)[0]
            value = convert_value(float(width), unit, self.width_unit)
            attrs['colwidth'] = u"{value:0.2f}{unit}".format(value=value, unit=self.width_unit)
        etree.SubElement(group_elem, u"colspec", attrib=attrs)

    def build_tbody(self, group_elem, row_list, nature_tag):
        nature_elem = etree.SubElement(group_elem, nature_tag)
        for row in row_list:
            self.build_row(nature_elem, row)

    def build_row(self, tbody_elem, row):
        # Possible attrs:
        # - Row height: min-height' or 'height'
        # - Insertion revision mark: 'x-ins', 'x-ins-id', 'x-ins-author', 'x-ins-date'
        # - Vertical align: 'valign'
        #
        row_styles = row.styles
        attrs = {}
        if 'valign' in row_styles:
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
            rev_name = "change-start"
            rev_pi = revision_mark(rev_name, rev_attrs)
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
        cell_styles = cell.styles
        if cell.width > 1:
            cell_styles[u"namest"] = "c{0}".format(cell.box.min.x)
            cell_styles[u"nameend"] = "c{0}".format(cell.box.max.x)
        if cell.height > 1:
            cell_styles[u"morerows"] = str(cell.height - 1)
        entry_elem = etree.SubElement(row_elem, u"entry", attrib=cell_styles)
        if cell.content is not None:
            entry_elem.extend(cell.content)
