# coding: utf-8
"""
lxml - QName
============

Python alternative to :class:`lxml.etree.QName` for lxml < 4

.. versionadded:: 0.5.0
"""
from lxml import etree

if etree.LXML_VERSION >= (4,):
    QName = etree.QName

else:
    class _QName(etree.QName):
        __doc__ = etree.QName.__doc__

        def __init__(self, text_or_uri_or_element, tag=None):
            if text_or_uri_or_element is None:
                super(_QName, self).__init__(tag)
            else:
                super(_QName, self).__init__(text_or_uri_or_element, tag=tag)

    QName = _QName
