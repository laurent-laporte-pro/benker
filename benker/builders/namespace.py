# coding: utf-8
"""
Namespace
=========
"""
import collections

from benker.common.lxml_qname import QName


class Namespace(collections.namedtuple("Namespace", "prefix, uri")):
    """
    A namespace is defined by a *prefix* and an *uri*.

    .. versionadded:: 0.5.0
    """

    def get_qname(self, name):
        """ get the qualified name """
        return QName(self.uri, name)

    def get_name(self, name):
        """ get the prefixed name """
        fmt = "{prefix}:{name}" if self.prefix else "{name}"
        return fmt.format(prefix=self.prefix, name=name)
