# coding: utf-8
import py.path  # type hints
import pytest

from benker.converters.ooxml2cals import convert_ooxml2cals
from tests.converters.cals_comparator import CalsComparator
from tests.resources import RESOURCES_DIR


@pytest.mark.parametrize('input_name, expected_name',
                         [
                             ("cals/alignements.xml", "cals/alignements.expected.xml"),
                             ("cals/simple_merge.xml", "cals/simple_merge.expected.xml"),
                             ("cals/table_in_table.xml", "cals/table_in_table.expected.xml"),
                             ("cals/Lorem Ipsum.xml", "cals/Lorem Ipsum.expected.xml"),
                             ('cals/Revision marks.xml', 'cals/Revision marks.expected.xml')
                         ])
def test_convert_to_cals(input_name, expected_name, tmpdir):
    # type: (str, str, py.path.local) -> None
    src_xml = RESOURCES_DIR.join(input_name)  # type: py.path.local
    dst_xml = tmpdir.join(src_xml.basename)
    convert_ooxml2cals(str(src_xml), str(dst_xml), width_unit='pt')
    expected_xml = RESOURCES_DIR.join(expected_name)  # type: py.path.local
    CalsComparator().compare_files(str(dst_xml), str(expected_xml))
