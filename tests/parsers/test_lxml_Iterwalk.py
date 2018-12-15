# coding: utf-8
import pytest
from lxml import etree

from benker.parsers.lxml_iterwalk import iterwalk


@pytest.mark.parametrize(
    'events, tag, expected',
    [
        ((), None, []),

        (('start',), None, [('start', 'root'), ('start', 'a')]),
        (('start',), '*', [('start', 'root'), ('start', 'a')]),
        (('start',), 'root', [('start', 'root')]),
        (('start',), 'other', []),

        (('end',), None, [('end', 'a'), ('end', 'root')]),
        (('end',), '*', [('end', 'a'), ('end', 'root')]),
        (('end',), 'root', [('end', 'root')]),
        (('end',), 'other', []),

        (('start', 'end'), None, [('start', 'root'), ('start', 'a'), ('end', 'a'), ('end', 'root')]),
        (('start', 'end'), '*', [('start', 'root'), ('start', 'a'), ('end', 'a'), ('end', 'root')]),
        (('start', 'end'), 'root', [('start', 'root'), ('end', 'root')]),
        (('start', 'end'), 'other', []),
    ]
)
def test_iterwalk_root(events, tag, expected):
    root = etree.XML("<root><a/></root>")
    context = iterwalk(root, events=events, tag=tag)
    actual = [(event, node.tag) for event, node in context]
    assert expected == actual
