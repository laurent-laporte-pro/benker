# coding: utf-8
import unittest

import pytest
from lxml import etree

from benker.builders.base_builder import BaseBuilder


class TestBaseBuilder(unittest.TestCase):
    def test_init(self):
        builder = BaseBuilder()
        assert builder.options == {}

    def test_init__options(self):
        builder = BaseBuilder(key="value")
        assert builder.options == {"key": "value"}


def pi(target, text=None, tail=None):
    node = etree.ProcessingInstruction(target, text=text)
    node.tail = tail
    return node


@pytest.mark.parametrize(
    u"elements, expected",
    # fmt: off
    [
        (
            None,
            u"<cell/>",
        ),
        (
            u"text",
            u"<cell>text</cell>",
        ),
        (
            b"text",
            u"<cell>text</cell>",
        ),
        (
            3.14,
            u"<cell>3.14</cell>",
        ),
        (
            etree.Element(u"P"),
            u"<cell><P/></cell>",
        ),
        (
            [etree.Element(u"P")],
            u"<cell><P/></cell>",
        ),
        (
            [u"text"],
            u"<cell>text</cell>",
        ),
        (
            [u"text", pi(u"instr", text=u"no='1'")],
            u"<cell>text<?instr no='1'?></cell>",
        ),
        (
            [pi(u"instr", text=u"no='1'")],
            u"<cell><?instr no='1'?></cell>",
        ),
        (
            [pi(u"instr", text=u"no='1'", tail=u" following")],
            u"<cell><?instr no='1'?> following</cell>",
        ),
        (
            [u"one", pi(u"instr", text=u"no='1'", tail=u"two")],
            u"<cell>one<?instr no='1'?>two</cell>",
        ),
        (
            [u"one", pi(u"instr", text=u"no='1'", tail=u"two"), u" three", pi(u"instr", text=u"no='2'", tail=u"four")],
            u"<cell>one<?instr no='1'?>two three<?instr no='2'?>four</cell>",
        ),
        (
            [u"one", etree.XML(u"<b>bold</b>"), u"two"],
            u"<cell>one<b>bold</b>two</cell>",
        ),
    ],
    # fmt: on
)
def test_append_content(elements, expected):
    builder = BaseBuilder()
    cell_elem = etree.Element(u"cell")
    builder.append_cell_elements(cell_elem, elements)
    assert etree.tounicode(cell_elem) == expected
