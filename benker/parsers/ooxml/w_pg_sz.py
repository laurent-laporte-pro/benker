# coding: utf-8

from benker.parsers.ooxml.namespaces import value_of
from benker.parsers.ooxml.types import StPageOrientation
from benker.parsers.ooxml.types import StTwipsMeasure


class PgSz(object):
    """
    Page Size. --
    This element specifies the properties (size and orientation)
    for all pages in the current section.

    Example: ``<w:pgSz w:w="11907" w:h="16839" />``, for A4 portrait.
    """

    def __init__(self, w_pg_sz):
        #: Page Width
        self.w_w = value_of(w_pg_sz, "@w:w")

        #: Page Height
        self.w_h = value_of(w_pg_sz, "@w:h")

        #: Page Orientation (Possible values are "landscape" and "portrait").
        self.w_orient = value_of(w_pg_sz, "@w:orient")

        #: Printer Paper Code
        self.w_code = value_of(w_pg_sz, "@w:code")

    @property
    def styles(self):
        w = StTwipsMeasure(self.w_w).style
        h = StTwipsMeasure(self.w_h).style
        size = (w, h) if w is not None and h is not None else None
        orient = StPageOrientation(self.w_orient).style
        styles = {
            "x-sect-size": size,
            "x-sect-orient": orient,
        }
        return {k: v for k, v in styles.items() if v is not None}
