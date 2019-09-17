# coding: utf-8
from lxml import etree

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
    if LXML_VERSION >= (4, 0):
        assert qname.localname == "tag"
        assert qname.namespace is None
        assert qname.text == "tag"
    else:
        assert qname.localname == "tag"
        assert qname.namespace == "None"
        assert qname.text == "{None}tag"


class MyQName(etree.QName):
    def __init__(self, text_or_uri_or_element, tag=None):
        if text_or_uri_or_element is None:
            super(MyQName, self).__init__(tag)
        else:
            super(MyQName, self).__init__(text_or_uri_or_element, tag=tag)


def test_my_qname__none_tag():
    qname = MyQName(None, "tag")
    assert qname.localname == "tag"
    assert qname.namespace is None
    assert qname.text == "tag"
