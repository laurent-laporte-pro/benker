# coding: utf-8
import zipfile

import py.path  # type hints
import pytest
import xmldiff.main
from lxml import etree

from benker.converters.ooxml2formex import convert_ooxml2formex

from tests.resources import RESOURCES_DIR


def _check_expected(dst_xml, expected_name):
    # - Compare with expected
    xml_parser = etree.XMLParser(remove_blank_text=True)
    expected_xml = RESOURCES_DIR.join(expected_name)  # type: py.path.local
    expected_tree = etree.parse(str(expected_xml), parser=xml_parser)
    expected_elements = expected_tree.xpath("//TBL")
    dst_tree = etree.parse(str(dst_xml), parser=xml_parser)
    dst_elements = dst_tree.xpath("//TBL")
    assert len(expected_elements) == len(dst_elements)
    for dst_elem, expected_elem in zip(dst_elements, expected_elements):
        diff_list = xmldiff.main.diff_trees(dst_elem, expected_elem)
        assert not diff_list


def test_convert_ooxml2formex__demo(tmpdir):
    # type: (py.path.local) -> None

    # - Unzip the ``.docx``
    src_zip = RESOURCES_DIR.join("ooxml/demo.docx")  # type: py.path.local
    with zipfile.ZipFile(str(src_zip)) as zf:
        zf.extractall(str(tmpdir))

    # - Source and destination paths
    src_xml = tmpdir.join("word/document.xml")  # type: py.path.local
    styles_xml = tmpdir.join("word/styles.xml")  # type: py.path.local
    dst_xml = tmpdir.join(src_zip.basename).new(ext=".formex.xml")  # type: py.path.local

    # - Create some options and convert tables
    options = {"encoding": "utf-8", "styles_path": str(styles_xml)}
    convert_ooxml2formex(str(src_xml), str(dst_xml), **options)
    expected_name = "ooxml2formex/demo.xml"
    _check_expected(dst_xml, expected_name)


@pytest.mark.parametrize(
    "input_name, expected_name",
    [
        # ("ooxml/misc_tables.xml", "ooxml2formex/misc_tables.xml"),
        ("ooxml/simple_merge.xml", "ooxml2formex/simple_merge.xml"),
        # ("ooxml/table_in_table.xml", "ooxml2formex/table_in_table.xml"),
        # ("ooxml/Revision marks.xml", "ooxml2formex/Revision marks.xml"),
        # ("ooxml/empty_cells.xml", "ooxml2formex/empty_cells.xml"),
        # ("ooxml/demo_images.xml", "ooxml2formex/demo_images.xml"),
    ],
)
def test_convert_ooxml2formex(input_name, expected_name, tmpdir):
    # type: (str, str, py.path.local) -> None
    src_xml = RESOURCES_DIR.join(input_name)  # type: py.path.local
    dst_xml = tmpdir.join(src_xml.basename)
    convert_ooxml2formex(str(src_xml), str(dst_xml), width_unit="pt")
    _check_expected(dst_xml, expected_name)


@pytest.mark.parametrize(
    "input_name, expected_name", [("ooxml/empty_cells.xml", "ooxml2formex_detect_titles/empty_cells.xml")]
)
def test_convert_ooxml2formex4__detect_titles(input_name, expected_name, tmpdir):
    # type: (str, str, py.path.local) -> None
    src_xml = RESOURCES_DIR.join(input_name)  # type: py.path.local
    dst_xml = tmpdir.join(src_xml.basename)
    convert_ooxml2formex(str(src_xml), str(dst_xml), width_unit="pt", detect_titles=True)
    _check_expected(dst_xml, expected_name)
