# coding: utf-8
from lxml import etree


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
    assert qname.localname == "tag"
    assert qname.namespace is None
    assert qname.text == "tag"
