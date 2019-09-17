# coding: utf-8
import zipfile

import py.path  # type hints
import pytest
import xmldiff.main
from lxml import etree

from benker.converters.ooxml2cals import convert_ooxml2cals

from tests.converters.cals_comparator import CalsComparator
from tests.resources import RESOURCES_DIR


def test_convert_ooxml2cals__demo(tmpdir):
    # type: (py.path.local) -> None

    # - Unzip the ``.docx``
    src_zip = RESOURCES_DIR.join("ooxml/demo.docx")  # type: py.path.local
    with zipfile.ZipFile(str(src_zip)) as zf:
        zf.extractall(str(tmpdir))

    # - Source and destination paths
    src_xml = tmpdir.join("word/document.xml")  # type: py.path.local
    styles_xml = tmpdir.join("word/styles.xml")  # type: py.path.local
    dst_xml = tmpdir.join(src_zip.basename).new(ext='.cals.xml')  # type: py.path.local

    # - Create some options and convert tables
    options = {'encoding': 'utf-8', 'styles_path': str(styles_xml), 'width_unit': "mm", 'table_in_tgroup': True}
    convert_ooxml2cals(str(src_xml), str(dst_xml), **options)

    # - Compare with expected
    expected_xml = RESOURCES_DIR.join("ooxml2cals/demo.xml")  # type: py.path.local
    CalsComparator().compare_files(str(dst_xml), str(expected_xml))


@pytest.mark.parametrize(
    'input_name, expected_name',
    [
        ("ooxml/misc_tables.xml", "ooxml2cals/misc_tables.xml"),
        ("ooxml/alignements.xml", "ooxml2cals/alignements.xml"),
        ("ooxml/alignements2.xml", "ooxml2cals/alignements2.xml"),
        ("ooxml/simple_merge.xml", "ooxml2cals/simple_merge.xml"),
        ("ooxml/table_in_table.xml", "ooxml2cals/table_in_table.xml"),
        ("ooxml/Lorem Ipsum.xml", "ooxml2cals/Lorem Ipsum.xml"),
        ("ooxml/Revision marks.xml", "ooxml2cals/Revision marks.xml"),
    ],
)
def test_convert_ooxml2cals(input_name, expected_name, tmpdir):
    # type: (str, str, py.path.local) -> None
    src_xml = RESOURCES_DIR.join(input_name)  # type: py.path.local
    dst_xml = tmpdir.join(src_xml.basename)
    convert_ooxml2cals(str(src_xml), str(dst_xml), width_unit='pt')

    # - Compare with expected
    xml_parser = etree.XMLParser(remove_blank_text=True)
    expected_xml = RESOURCES_DIR.join(expected_name)  # type: py.path.local
    expected_tree = etree.parse(str(expected_xml), parser=xml_parser)
    expected_elements = expected_tree.xpath("//table")
    dst_tree = etree.parse(str(dst_xml), parser=xml_parser)
    dst_elements = dst_tree.xpath("//table")
    assert len(expected_elements) == len(dst_elements)

    for dst_elem, expected_elem in zip(dst_elements, expected_elements):
        diff_list = xmldiff.main.diff_trees(dst_elem, expected_elem)
        assert not diff_list
