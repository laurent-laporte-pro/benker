# coding: utf-8
import zipfile

import py.path  # type hints
import pytest

from benker.converters.ooxml2cals import convert_ooxml2cals
from tests.converters.cals_comparator import CalsComparator
from tests.resources import RESOURCES_DIR


def test_convert_ooxml2cals__demo(tmpdir):
    # type: (py.path.local) -> None

    # - Unzip the ``.docx``
    src_zip = RESOURCES_DIR.join("cals/demo.docx")  # type: py.path.local
    with zipfile.ZipFile(str(src_zip)) as zf:
        zf.extractall(str(tmpdir))

    # - Source and destination paths
    src_xml = tmpdir.join("word/document.xml")  # type: py.path.local
    styles_xml = tmpdir.join("word/styles.xml")  # type: py.path.local
    dst_xml = tmpdir.join(src_zip.basename).new(ext='.cals.xml')  # type: py.path.local

    # - Create some options and convert tables
    options = {
        'encoding': 'utf-8',
        'styles_path': str(styles_xml),
        'width_unit': "mm",
        'table_in_tgroup': True,
    }
    convert_ooxml2cals(str(src_xml), str(dst_xml), **options)

    # - Compare with expected
    expected_xml = RESOURCES_DIR.join("cals/demo.expected.xml")  # type: py.path.local
    CalsComparator().compare_files(str(dst_xml), str(expected_xml))


@pytest.mark.parametrize('input_name, expected_name',
                         [
                             ("cals/alignements.xml", "cals/alignements.expected.xml"),
                             ("cals/alignements2.xml", "cals/alignements2.expected.xml"),
                             ("cals/simple_merge.xml", "cals/simple_merge.expected.xml"),
                             ("cals/table_in_table.xml", "cals/table_in_table.expected.xml"),
                             ("cals/Lorem Ipsum.xml", "cals/Lorem Ipsum.expected.xml"),
                             ('cals/Revision marks.xml', 'cals/Revision marks.expected.xml'),
                         ])
def test_convert_ooxml2cals(input_name, expected_name, tmpdir):
    # type: (str, str, py.path.local) -> None
    src_xml = RESOURCES_DIR.join(input_name)  # type: py.path.local
    dst_xml = tmpdir.join(src_xml.basename)
    convert_ooxml2cals(str(src_xml), str(dst_xml), width_unit='pt')
    expected_xml = RESOURCES_DIR.join(expected_name)  # type: py.path.local
    # shutil.copy(str(dst_xml), str(expected_xml))
    CalsComparator().compare_files(str(dst_xml), str(expected_xml))
