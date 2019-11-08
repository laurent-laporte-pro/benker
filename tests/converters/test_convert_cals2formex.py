# coding: utf-8
from __future__ import print_function

import shutil

import py.path  # type hints
import pytest
import xmldiff.main
from lxml import etree

from benker.converters.cals2formex import convert_cals2formex

from tests.resources import RESOURCES_DIR


@pytest.mark.parametrize(
    "input_name, expected_name, cals_prefix, cals_ns",
    # fmt: off
    [
        (
            "cals/tbl_small_table.xml",
            "cals2formex/tbl_small_table.xml",
            "cals",
            "https://lib.benker.com/schemas/cals.xsd",
        ),
        (
            "cals/tbl_sample.xml",
            "cals2formex/tbl_sample.xml",
            "cals",
            "https://lib.benker.com/schemas/cals.xsd",
        ),
        (
            "cals/tbl_sample_formex.xml",
            "cals2formex/tbl_sample_formex.xml",
            "cals",
            "https://lib.benker.com/schemas/cals.xsd",
        ),
        (
            "cals/tbl_sample_cals2.xml",
            "cals2formex/tbl_sample_cals2.xml",
            None,
            None,
        ),
        (
            "cals/fix_9_lost_text_in_entries.xml",
            "cals2formex/fix_9_lost_text_in_entries.xml",
            None,
            None,
        ),
        (
            "cals/fix_11_corpus_width_missing.xml",
            "cals2formex/fix_11_corpus_width_missing.xml",
            None,
            None,
        ),
        (
            "cals/fix_12_missing_colspec_attributes.xml",
            "cals2formex/fix_12_missing_colspec_attributes.xml",
            None,
            None,
        ),
        (
            "cals/fix_10_embed_gr_notes1.xml",
            "cals2formex/fix_10_embed_gr_notes1.xml",
            None,
            None,
        ),
        (
            "cals/fix_10_embed_gr_notes2.xml",
            "cals2formex/fix_10_embed_gr_notes2.xml",
            None,
            None,
        ),
    ],
    # fmt: on
)
def test_convert_cals2formex(input_name, expected_name, cals_prefix, cals_ns, tmpdir):
    # type: (str, str, str, str, py.path.local) -> None
    src_xml = RESOURCES_DIR.join(input_name)  # type: py.path.local
    dst_xml = tmpdir.join(src_xml.basename)
    convert_cals2formex(
        str(src_xml), str(dst_xml), width_unit="mm", use_cals=True, cals_prefix=cals_prefix, cals_ns=cals_ns
    )

    # - Compare with expected
    xml_parser = etree.XMLParser(remove_blank_text=True)
    expected_xml = RESOURCES_DIR.join(expected_name)  # type: py.path.local
    if expected_xml.exists():
        expected_tree = etree.parse(str(expected_xml), parser=xml_parser)
        expected_elements = expected_tree.xpath("//TBL")
        dst_tree = etree.parse(str(dst_xml), parser=xml_parser)
        dst_elements = dst_tree.xpath("//TBL")
        assert len(expected_elements) == len(dst_elements)

        for dst_elem, expected_elem in zip(dst_elements, expected_elements):
            diff_list = xmldiff.main.diff_trees(dst_elem, expected_elem)
            assert not diff_list
    else:
        # missing resource: create it
        shutil.copy(str(dst_xml), str(expected_xml))
        print("You should check and commit the file: '{}'".format(expected_xml))
