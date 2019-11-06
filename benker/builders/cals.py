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
import collections
import itertools

from lxml import etree

from benker.builders.base_builder import BaseBuilder
from benker.builders.namespace import Namespace
from benker.units import convert_value
from benker.units import parse_width

# noinspection PyProtectedMember
#: Element Type
ElementType = etree._Element


def _get_border_style(styles, style):
    parts = styles.get(style, "")
    parts = parts.split(" ") if parts else []
    value = None
    for part in parts:
        if not part.endswith("pt") and part != "auto" and not part.startswith("#"):
            value = part
    return value


def get_frame_attr(styles):
    frame_styles = {"border-top": False, "border-right": False, "border-bottom": False, "border-left": False}
    for style in frame_styles:
        value = _get_border_style(styles, style) or u"none"
        frame_styles[style] = value != u"none"
    top = frame_styles["border-top"]
    bottom = frame_styles["border-bottom"]
    left = frame_styles["border-left"]
    right = frame_styles["border-right"]
    return {
        (True, True, True, True): u"all",
        (True, True, False, False): u"topbot",
        (False, False, True, True): u"sides",
        (True, False, False, False): u"top",
        (False, True, False, False): u"bottom",
    }.get((top, bottom, left, right), u"none")


def get_colsep_attr(styles, style="x-cell-border-right"):
    value = _get_border_style(styles, style)
    return None if value is None else "0" if value == "none" else "1"


def get_rowsep_attr(styles, style="x-cell-border-bottom"):
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

    def __init__(
        self,
        cals_ns=None,
        cals_prefix=None,
        width_unit="mm",
        table_in_tgroup=False,
        tgroup_sorting=None,
        **options
    ):
        """
        Initialize the builder.

        :param str cals_ns:
            Namespace to use for CALS-like elements and attributes to generate.
            Set "" ``None`` (empty) if you don't want to use namespace.

        :param str cals_prefix:
            Namespace prefix to use for CALS-like elements and attributes to generate.

        :param str width_unit:
            Unit to use for table/column widths.
            Possible values are: 'cm', 'dm', 'ft', 'in', 'm', 'mm', 'pc', 'pt', 'px'.

        :param bool table_in_tgroup:
            Where should we put the table properties:
            - ``False`` to put the properties in the ``<table>`` element,
            - ``True`` to put the properties in the ``<tgroup>`` element.

        :type  tgroup_sorting: typing.List[str]
        :param tgroup_sorting:
            List used to sort (and group) the rows in a ``tgroup``.
            The sorting is done according to the row natures
            which is by default: ``["header", "footer", "body"]``
            (this order match the CALS DTD defaults,
            where the footer is between the header and the body.
            To move the footer to the end, you can use ``["header", "body", "footer"]``.

        :keyword options: Extra conversion options.
            See :meth:`~benker.converters.base_converter.BaseConverter.convert_file`
            to have a list of all possible options.

        .. versionchanged:: 0.5.0
           Add the options *cals_ns*, *cals_prefix*, *tgroup_sorting*.
        """
        # Internal state of the table used during building
        self._table = None
        self._table_colsep = u"0"
        self._table_rowsep = u"0"
        # options
        self._ns_map = {}
        self.cals_ns = self._register_namespace(cals_prefix, cals_ns)
        self.width_unit = width_unit
        self.table_in_tgroup = table_in_tgroup
        tgroup_sorting_default = ["header", "footer", "body"]
        tgroup_sorting = tgroup_sorting or tgroup_sorting_default
        self.tgroup_sorting = {nature: index for index, nature in enumerate(tgroup_sorting)}
        missing = set(tgroup_sorting_default) - set(self.tgroup_sorting)
        if missing:
            raise ValueError("sort order not defined for {}".format(missing))
        super(CalsBuilder, self).__init__(**options)

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

    def generate_table_tree(self, table):
        """
        Build the XML table from the Table instance.

        :type  table: benker.table.Table
        :param table: Table

        :return: Table tree
        """
        table_elem = self.build_table(table)
        return table_elem

    def setup_table(self, table):
        self._table = table
        self._table_colsep = u"0"
        self._table_rowsep = u"0"
        return self._table  # mainly for unit tests

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

        -   ``@bgcolor`` is built from the "background-color" style (HTML color).

        -   ``@width`` is built from the "width" style (percentage or width with unit).
            This attribute in an extension.

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

        .. versionchanged:: 0.5.0
           Add support for the ``bgcolor`` attribute (background color).

        .. versionchanged:: 0.5.1
           Add support for the ``@width`` attribute (table width).
        """
        self.setup_table(table)

        # support for CALS namespace
        cals = self.cals_ns.get_qname
        table_styles = table.styles
        attrs = {cals('frame'): get_frame_attr(table_styles)}
        if not self.table_in_tgroup:
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
        if "width" in table_styles:
            width, unit = parse_width(table_styles["width"])
            value = convert_value(width, unit, self.width_unit)
            attrs[cals("width")] = u"{value:0.2f}{unit}".format(value=value, unit=self.width_unit)

        table_elem = etree.Element(cals(u"table"), attrib=attrs, nsmap=self.ns_map)
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

        :type  table_elem: ElementType
        :param table_elem: Parent element: ``<table>``.

        :type  table: benker.table.Table
        :param table: Table

        :return: The newly-created ``<tgroup>`` element.
        """
        # support for CALS namespace
        cals = self.cals_ns.get_qname
        table_styles = table.styles
        attrs = {cals(u"cols"): str(len(table.cols))}
        if self.table_in_tgroup:
            self._table_colsep = attrs[cals("colsep")] = get_colsep_attr(table_styles) or "0"
            self._table_rowsep = attrs[cals("rowsep")] = get_rowsep_attr(table_styles) or "0"
            if table.nature is not None:
                attrs[cals("tgroupstyle")] = table.nature
        group_elem = etree.SubElement(table_elem, cals(u"tgroup"), attrib=attrs, nsmap=self.ns_map)
        for col in table.cols:
            self.build_colspec(group_elem, col)
        # -- group rows by header/body/footer
        groups = [(k, list(g)) for k, g in itertools.groupby(table.rows, key=lambda r: r.nature)]
        # -- sort the groups in the order: header => footer => body
        groups = sorted(groups, key=lambda item: self.tgroup_sorting.get(item[0], self.tgroup_sorting["body"]))
        group_tags = {"header": u"thead", "body": u"tbody", "footer": u"tfoot"}
        for nature, row_list in groups:
            nature_tag = group_tags.get(nature, group_tags["body"])
            self.build_tbody(group_elem, row_list, nature_tag)

    # noinspection PyMethodMayBeStatic
    def build_colspec(self, group_elem, col):
        """
        Build the CALS ``<colspec>`` element.

        CALS attributes:

        -   ``@colnum`` is the column number.

        -   ``@colname`` is the column name. Its format is "c{col_pos}".

        -   ``@colwidth`` width of the column (with its unit).
            The unit is defined by the *width_unit* options.

        -   ``@align`` horizontal alignment of table entry content.
            Possible values are: "left", "right", "center", "justify" ("char" is not supported).

        -   ``@colsep`` column separators (vertical ruling).
            Possible values are "0" or "1".

        -   ``@colsep`` row separators (horizontal ruling).
            Possible values are "0" or "1".

        :type  group_elem: ElementType
        :param group_elem: Parent element: ``<tgroup>``.

        :type  col: benker.table.ColView
        :param col: Columns

        .. versionchanged:: 0.5.0
           The ``@colnum`` and ``@align`` attributes are generated.

        .. versionchanged:: 0.5.1
           The ``@colsep`` and ``@rowsep`` attributes are generated.
        """
        # support for CALS namespace
        cals = self.cals_ns.get_qname
        col_styles = col.styles

        # -- @cals:colnum
        # -- @cals:colname
        attrs = {cals(u"colnum"): u"{0}".format(col.col_pos), cals(u"colname"): u"c{0}".format(col.col_pos)}

        # -- @cals:colwidth
        if "width" in col_styles:
            width, unit = parse_width(col_styles["width"])
            value = convert_value(width, unit, self.width_unit)
            attrs[cals("colwidth")] = u"{value:0.2f}{unit}".format(value=value, unit=self.width_unit)

        # -- @cals:align
        align = col_styles.get("align")
        align_map = {"left": "left", "right": "right", "center": "center", "justify": "justify"}
        if align in align_map:
            attrs[cals("align")] = align_map[align]

        cell_colsep = get_colsep_attr(col_styles, "border-right")
        if cell_colsep and cell_colsep != self._table_colsep:
            attrs[cals("colsep")] = cell_colsep

        cell_rowsep = get_rowsep_attr(col_styles, "border-bottom")
        if cell_rowsep and cell_rowsep != self._table_rowsep:
            attrs[cals("rowsep")] = cell_rowsep

        etree.SubElement(group_elem, cals(u"colspec"), attrib=attrs, nsmap=self.ns_map)

    def build_tbody(self, group_elem, row_list, nature_tag):
        """
        Build the CALS ``<tbody>``, `<thead>``, or `<tfoot>`` element.

        :type  group_elem: ElementType
        :param group_elem: Parent element: ``<tgroup>``.

        :param row_list: List of rows

        :param nature_tag: name of the tag: 'tbody', 'thead' or 'tfoot'.
        """
        # support for CALS namespace
        cals = self.cals_ns.get_qname
        nature_elem = etree.SubElement(group_elem, cals(nature_tag), nsmap=self.ns_map)
        for row in row_list:
            self.build_row(nature_elem, row)

    def build_row(self, tbody_elem, row):
        """
        Build the CALS ``<row>`` element.

        CALS attributes:

        -   ``@valign`` is built from the "vertical-align" style.
            Values can be "top", "middle", "bottom" (note: "baseline" is not supported).
            Default value is "bottom".

        .. note::

           A row can be marked as inserted if "x-ins" is defined in the row styles.
           Revision marks are inserted before and after a ``<row>``
           using a couple of processing-instructions.
           We use the ``<?change-start?>`` PI to mark the start of the inserted row,
           and the ``<?change-end?>`` PI to mark the end.

        :type  tbody_elem: ElementType
        :param tbody_elem: Parent element: ``<tbody>``, `<thead>``, or `<tfoot>``.

        :type  row: benker.table.RowView
        :param row: The row.

        .. versionadded:: 0.5.0
           Add support for the ``@cals:rowstyle`` attribute (extension).

        .. versionchanged:: 0.5.1
           The ``@cals:valign`` attribute is built from the "vertical-align" style.
        """
        # Possible attrs:
        # - Row height: min-height' or 'height'
        # - Insertion revision mark: 'x-ins', 'x-ins-id', 'x-ins-author', 'x-ins-date'
        # - Vertical align: 'valign'
        #
        # support for CALS namespace
        cals = self.cals_ns.get_qname
        row_styles = row.styles
        attrs = {}
        if "vertical-align" in row_styles:
            # same values as CSS/Properties/vertical-align
            # fmt: off
            attrs[cals('valign')] = {
                'top': 'top',
                'middle': 'middle',
                'bottom': 'bottom',
                'baseline': 'bottom',
            }[row_styles['vertical-align']]
            # fmt: on

        row_rowsep = get_rowsep_attr(row_styles, "border-bottom")
        if row_rowsep and row_rowsep != self._table_rowsep:
            attrs[cals("rowsep")] = row_rowsep

        # -- attribute @cals:rowstyle (extension)
        if "rowstyle" in row_styles:
            attrs[cals("rowstyle")] = row_styles["rowstyle"]

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
            tbody_elem.append(rev_pi)

        row_elem = etree.SubElement(tbody_elem, cals(u"row"), attrib=attrs, nsmap=self.ns_map)

        if "x-ins" in row_styles:
            # <?change-end change-id="ct139821811327752" type="row:insertion"?>
            rev_attrs = collections.OrderedDict({'type': 'row:insertion'})
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

        -   ``@valign`` is built from the "vertical-align" style.
            Values can be "top", "middle", "bottom" (note: "baseline" is not supported).
            Default value is "bottom".

        -   ``@align`` is built from the "align" style.
            Values can be "left", "center", "right", or "justify".
            Default value is "left".
            note: paragraphs alignment should be preferred to cells alignment.

        -   ``@namest``/``@nameend`` are set when the cell is spanned horizontally.

        -   ``@morerows`` is set when the cell is spanned vertically.

        -   ``@bgcolor`` is built from the "background-color" style (HTML color).

        :type  row_elem: ElementType
        :param row_elem: Parent element: ``<row>``.

        :type  cell: benker.cell.Cell
        :param cell: The cell.

        .. versionchanged:: 0.5.0
           Add support for ``bgcolor``.

        .. versionchanged:: 0.5.1
           Preserve processing instruction in cell content.
        """
        # support for CALS namespace
        cals = self.cals_ns.get_qname
        cell_styles = cell.styles
        attrs = {}
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
            # fmt: off
            attrs[cals('align')] = {
                'left': u'left',
                'center': u'center',
                'right': u'right',
                'justify': u'justify',
            }[cell_styles['align']]
            # fmt: on
        if cell.width > 1:
            attrs[cals(u"namest")] = u"c{0}".format(cell.box.min.x)
            attrs[cals(u"nameend")] = u"c{0}".format(cell.box.max.x)
        if cell.height > 1:
            attrs[cals(u"morerows")] = str(cell.height - 1)
        if "background-color" in cell_styles:
            attrs[cals("bgcolor")] = cell_styles["background-color"]

        entry_elem = etree.SubElement(row_elem, cals(u"entry"), attrib=attrs, nsmap=self.ns_map)
        self.append_cell_elements(entry_elem, cell.content)
