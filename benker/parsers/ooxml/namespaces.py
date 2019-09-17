# coding: utf-8
"""
OOXML namespaces
================
"""
import functools

from benker.parsers.base_parser import value_of as base_value_of

#: Namespace map used for xpath evaluation in Office Open XML documents
NS = {'w': "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def ns_name(ns, name):
    return '{' + ns + '}' + name


w = functools.partial(ns_name, NS['w'])
value_of = functools.partial(base_value_of, namespaces=NS)
