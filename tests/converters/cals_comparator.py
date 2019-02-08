# coding: utf-8
from __future__ import print_function

import sys

from lxml import etree

# noinspection PyProtectedMember
ElementTreeType = etree._ElementTree

# noinspection PyProtectedMember
ElementType = etree._Element


class CalsComparator(object):
    def compare_files(self, src_path, exp_file):
        src_tree = etree.parse(src_path)  # type: ElementTreeType
        exp_tree = etree.parse(exp_file)
        # The number of <table> must be the same
        src_tables = src_tree.xpath("//table")
        exp_tables = exp_tree.xpath("//table")
        self._compare_children(src_tables, exp_tables)

    def _compare_children(self, src_children, exp_children):
        assert len(src_children) == len(exp_children)
        for src_table, exp_table in zip(src_children, exp_children):
            method_name = "compare_{tag}".format(tag=src_table.tag)
            if hasattr(self, method_name):
                compare_method = getattr(self, method_name)
                compare_method(src_table, exp_table)

    def _compare_elements(self, src_tree, exp_tree):
        # type: (ElementType, ElementType) -> None
        try:
            assert src_tree.tag == exp_tree.tag
            src_keys = sorted(src_tree.attrib.keys())
            exp_keys = sorted(exp_tree.attrib.keys())
            assert src_keys == exp_keys, "src: {0!r}, exp: {1!r}".format(src_keys, exp_keys)
            src_attrs = sorted(src_tree.attrib.items())
            exp_attrs = sorted(exp_tree.attrib.items())
            assert src_attrs == exp_attrs, "src: {0!r}, exp: {1!r}".format(src_attrs, exp_attrs)
        except AssertionError:
            tree = exp_tree.getroottree()
            src_proto = etree.Element(src_tree.tag, attrib=src_tree.attrib)
            exp_proto = etree.Element(exp_tree.tag, attrib=exp_tree.attrib)
            print("FAIL: invalid xpath: {0}".format(tree.getpath(exp_tree)), file=sys.stderr)
            print("source:   " + etree.tounicode(src_proto, with_tail=False), file=sys.stderr)
            print("expected: " + etree.tounicode(exp_proto, with_tail=False), file=sys.stderr)
            raise
        else:
            src_children = list(src_tree.iterchildren('*'))
            exp_children = list(exp_tree.iterchildren('*'))
            self._compare_children(exp_children, src_children)

    compare_table = _compare_elements
    compare_tgroup = _compare_elements
    compare_colspec = _compare_elements
    compare_tbody = _compare_elements
    compare_thead = _compare_elements
    compare_tfoot = _compare_elements
    compare_row = _compare_elements
    compare_entry = _compare_elements
