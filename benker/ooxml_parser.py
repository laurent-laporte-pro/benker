# coding: utf-8
"""
Office Open XML to CALS tables parser
=====================================
"""
import functools

from lxml import etree

from benker import units

#: Namespace map used for xpath evaluation in Office Open XML documents
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


class OoxmlParser(object):
    """
    Office Open XML to CALS tables parser.
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

    def __init__(self, table_cls, w_styles=None, width_unit='mm', **options):
        """
        Construct a converter

        :type  table_cls:
        :param table_cls:
            Class to use to create a new instance of :class:`benker.table.Table`.
            This can be a factory function.

        :type  w_styles: etree._Element
        :param w_styles:
            ``<w:styles>`` element containing the document styles.
            If missing, this element will be searched from the root element ``<pkg:package>``.

        :param str width_unit:
            Unit to use for column widths.
            Possible values are: 'cm', 'dm', 'ft', 'in', 'm', 'mm', 'pc', 'pt', 'px'.

        :param str options: Extra conversion options.
        """
        self.create_table = table_cls
        self._state = self._State()
        self.w_styles = w_styles
        self.width_unit = width_unit
        self.options = options

    def parse(self, w_tbl):
        """
        Convert a Office Open XML ``<w:tbl>`` into CALS ``<table>``

        :type  w_tbl: etree._Element
        :param w_tbl: Office Open XML element.

        :rtype: etree.Element
        :return: CALS element.
        """
        self._state.reset()

        elements = {w(name) for name in {'tbl', 'tblGrid', 'gridCol', 'tr', 'tc'}}
        context = etree.iterwalk(w_tbl, events=('start',), tag=elements)

        for action, elem in context:
            elem_tag = elem.tag
            if elem_tag == w('tbl'):
                if elem is w_tbl:
                    self.parse_tbl(elem)
                else:
                    # This <tbl> element is inside the table.
                    # It will be handled separately in another call to convert_tbl()
                    context.skip_subtree()

            elif elem_tag == w('tblGrid'):
                # this element has no specific data
                pass

            elif elem_tag == w('gridCol'):
                self._state.next_col()
                self.parse_grid_col(elem)

            elif elem_tag == w('tr'):
                self._state.next_row()
                self.parse_tr(elem)

            elif elem_tag == w('tc'):
                self._state.next_col()
                self.parse_tc(elem)

            else:
                raise NotImplementedError(elem_tag)

        return self._state.table

    def parse_tbl(self, w_tbl):
        """
        Parse a ``<w:tbl>`` element.

        See: `Table Properties <http://officeopenxml.com/WPtableProperties.php>`_.

        :type  w_tbl: etree._Element
        :param w_tbl: Table element.
        """
        attrs = {}

        # - tabstyle: The identifier for a table style defined for the application

        style_id = value_of(w_tbl, "w:tblPr/w:tblStyle/@w:val")
        if style_id:
            attrs['tabstyle'] = style_id

        # -- frame: Describes position of outer rulings.
        # -- colsep: display the internal column rulings to the right of each <entry>
        # -- rowsep: display the internal horizontal row ruling below each <entry>

        tbl_borders = get_table_borders(self.w_styles, style_id)
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

        self._state.table = self.create_table(styles=attrs)

    def parse_grid_col(self, w_grid_col):
        """
        Parse a ``<w:gridCol>`` element.

        See: `Table Grid/Column Definition <http://officeopenxml.com/WPtableGrid.php>`_.

        :type  w_grid_col: etree._Element
        :param w_grid_col: Table element.
        """
        # w:w => width of the column in twentieths of a point.
        width = float(w_grid_col.attrib[w('w')]) / 20  # pt
        width = units.convert_value(width, 'pt', self.width_unit)
        state = self._state
        styles = {
            u"colname": "c{0}".format(state.col_pos),
            u"colwidth": "{width:0.2f}{unit}".format(width=width, unit=self.width_unit)}
        state.col = state.table.cols[state.col_pos]
        state.col.styles.update(styles)

    def parse_tr(self, w_tr):
        """
        Parse a ``<w:tr>`` element.

        See: `Table Row Properties <http://officeopenxml.com/WPtableRowProperties.php>`_.

        :type  w_tr: etree._Element
        :param w_tr: Table element.
        """
        # w:tblHeader => the current row should be repeated at the top
        # of each new page on which the table is displayed.
        # This is a simple boolean property, so you can specify a val attribute of true or false.
        tbl_header = value_of(w_tr, "w:trPr/w:tblHeader")
        if tbl_header is not None:
            tbl_header = value_of(w_tr, "w:trPr/w:tblHeader/@w:val", default=u"true")
        nature = {u"true": "head", u"false": "body", None: "body"}[tbl_header]
        state = self._state
        state.row = state.table.rows[state.row_pos]
        state.row.nature = nature

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
            content = w_tc.xpath('w:p | w:tbl', namespaces=NS)
            state.row.insert_cell(content, width=width, height=height)
