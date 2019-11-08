# coding: utf-8
from __future__ import print_function

import shutil

import py.path  # type hints
import pytest
import xmldiff.main
from lxml import etree

from benker.converters.formex2cals import convert_formex2cals

from tests.resources import RESOURCES_DIR


@pytest.mark.parametrize(
    'input_name, expected_name, embed_gr_notes',
    [
        ("formex/tbl_small_table.xml", "formex2cals/tbl_small_table.xml", False),
        ("formex/tbl_sample.xml", "formex2cals/tbl_sample.xml", False),
        ("formex/tbl_sample_cals.xml", "formex2cals/tbl_sample_cals.xml", False),
        ("formex/tbl_sample.xml", "formex2cals/tbl_sample.embedded.xml", True),
        ("formex/tbl_sample_cals.xml", "formex2cals/tbl_sample_cals.embedded.xml", True),
    ],
)
def test_convert_formex2cals(input_name, expected_name, embed_gr_notes, tmpdir):
    # type: (str, str, bool, py.path.local) -> None
    src_xml = RESOURCES_DIR.join(input_name)  # type: py.path.local
    dst_xml = tmpdir.join(src_xml.basename)
    convert_formex2cals(
        str(src_xml),
        str(dst_xml),
        width_unit='mm',
        cals_prefix="cals",
        cals_ns="https://lib.benker.com/schemas/cals.xsd",
        embed_gr_notes=embed_gr_notes,
    )

    # - Compare with expected
    xml_parser = etree.XMLParser(remove_blank_text=True)
    expected_xml = RESOURCES_DIR.join(expected_name)  # type: py.path.local
    if expected_xml.exists():
        expected_tree = etree.parse(str(expected_xml), parser=xml_parser)
        NS = {"cals": "https://lib.benker.com/schemas/cals.xsd"}
        expected_elements = expected_tree.xpath("//cals:table", namespaces=NS)
        dst_tree = etree.parse(str(dst_xml), parser=xml_parser)
        dst_elements = dst_tree.xpath("//cals:table", namespaces=NS)
        assert len(expected_elements) == len(dst_elements)

        for dst_elem, expected_elem in zip(dst_elements, expected_elements):
            diff_list = xmldiff.main.diff_trees(dst_elem, expected_elem)
            assert not diff_list
    else:
        # missing resource: create it
        shutil.copy(str(dst_xml), str(expected_xml))
        print("You should check and commit the file: '{}'".format(expected_xml))
