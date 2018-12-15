# coding: utf-8
"""
lxml Iterators
==============

Python alternative to :class:`lxml.etree.iterwalk` for lxml < 4.2.1
"""
from lxml import etree

if etree.LXML_VERSION >= (4, 2, 1, 0):
    iterwalk = etree.iterwalk

else:
    class _MultiTagMatcher(object):
        def __init__(self, tag):
            self.tags = {tag} if isinstance(tag, str) else set(tag)

        def __call__(self, element_or_tree):
            # type: (etree._ElementTree or etree._Element) -> bool
            return element_or_tree.tag in self.tags

    def _iterwalk_impl(tree, events, matcher):
        if 'start' in events and (matcher is None or matcher(tree)):
            yield ('start', tree)
        for child in tree:
            for event, node in _iterwalk_impl(child, events, matcher):
                yield (event, node)
        if 'end' in events and (matcher is None or matcher(tree)):
            yield ('end', tree)

    def iterwalk(element_or_tree, events=(u"end",), tag=None):
        matcher = None if tag is None or tag == "*" else _MultiTagMatcher(tag)
        for event, node in _iterwalk_impl(element_or_tree, events, matcher):
            yield (event, node)
