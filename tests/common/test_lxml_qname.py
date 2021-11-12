# coding: utf-8
from lxml import etree

from benker.common.lxml_qname import QName

LXML_VERSION = tuple(map(int, etree.__version__.split('.')))


def test_qname__tag():
    qname = etree.QName("tag")
    assert qname.localname == "tag"
    assert qname.namespace is None
    assert qname.text == "tag"


def test_qname__qname():
    qname = etree.QName("{http://somewhere}tag")
    assert qname.localname == "tag"
    assert qname.namespace == "http://somewhere"
    assert qname.text == "{http://somewhere}tag"


def test_qname__element():
    qname = etree.QName(etree.XML('<tag xmlns="http://somewhere"/>'))
    assert qname.localname == "tag"
    assert qname.namespace == "http://somewhere"
    assert qname.text == "{http://somewhere}tag"


def test_qname__uri_tag():
    qname = etree.QName("http://somewhere", "tag")
    assert qname.localname == "tag"
    assert qname.namespace == "http://somewhere"
    assert qname.text == "{http://somewhere}tag"


def test_qname__none_tag():
    qname = etree.QName(None, "tag")
    if LXML_VERSION >= (4, 2):
        assert qname.localname == "tag"
        assert qname.namespace is None
        assert qname.text == "tag"
    else:
        assert qname.localname == "tag"
        assert qname.namespace == "None"
        assert qname.text == "{None}tag"


def test_my_qname__none_tag():
    qname = QName(None, "tag")
    assert qname.localname == "tag"
    assert qname.namespace is None
    assert qname.text == "tag"
