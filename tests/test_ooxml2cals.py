# coding: utf-8

# noinspection PyUnresolvedReferences
import py.path  # type hints

from benker.ooxml2cals import convert_to_cals
from tests.resources import RESOURCES_DIR


def test_convert_to_cals(tmpdir):
    # type: (py.path.local) -> None
    src_xml = RESOURCES_DIR.join("cals/simple_merge.xml")  # type: py.path.local
    dst_xml = tmpdir.join(src_xml.basename)
    convert_to_cals(str(src_xml), str(dst_xml))
