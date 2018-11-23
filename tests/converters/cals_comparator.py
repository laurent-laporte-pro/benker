# coding: utf-8
from lxml import etree

# noinspection PyProtectedMember
ElementTreeType = etree._ElementTree

# noinspection PyProtectedMember
ElementType = etree._Element


class CalsComparator(object):
    def compare_files(self, src_path, dst_file):
        src_tree = etree.parse(src_path)  # type: ElementTreeType
        dst_tree = etree.parse(dst_file)
        # The number of <table> must be the same
        src_tables = src_tree.xpath("//table")
        dst_tables = dst_tree.xpath("//table")
        self._compare_children(src_tables, dst_tables)

    def _compare_children(self, dst_children, src_children):
        assert len(src_children) == len(dst_children)
        for src_table, dst_table in zip(src_children, dst_children):
            method_name = "compare_{tag}".format(tag=src_table.tag)
            if hasattr(self, method_name):
                compare_method = getattr(self, method_name)
                compare_method(src_table, dst_table)

    def _compare_elements(self, src_tree, dst_tree):
        # type: (ElementType, ElementType) -> None
        assert src_tree.tag == dst_tree.tag
        assert src_tree.attrib == dst_tree.attrib, str((src_tree.attrib, dst_tree.attrib))
        src_children = list(src_tree)
        dst_children = list(dst_tree)
        self._compare_children(dst_children, src_children)

    compare_table = _compare_elements
    compare_tgroup = _compare_elements
    compare_colspec = _compare_elements
    compare_tbody = _compare_elements
    compare_thead = _compare_elements
    compare_tfoot = _compare_elements
    compare_row = _compare_elements
    compare_entry = _compare_elements
