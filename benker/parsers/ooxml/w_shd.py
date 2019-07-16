# coding: utf-8
from lxml import etree

from benker.parsers.ooxml.namespaces import value_of
from benker.parsers.ooxml.types import StHexColor


class Shd(object):
    """
    Table/Cell shading and Table Shading Exception

    Example: ``<w:shd w:val="clear" w:color="auto" w:fill="E6E6E6"/>``

    See: http://www.datypic.com/sc/ooxml/e-w_shd-3.html
    See: http://www.datypic.com/sc/ooxml/e-w_shd-4.html
    See: http://www.datypic.com/sc/ooxml/e-w_shd-5.html
    """

    def __init__(self, w_shd):
        # type: (etree._Element) -> None

        #: Shading Pattern
        self.w_val = value_of(w_shd, "@w:val")  # required

        #: Shading Pattern Color
        self.w_color = value_of(w_shd, "@w:color")

        #: Shading Background Color
        self.w_fill = value_of(w_shd, "@w:fill")

        #: Shading Pattern Theme Color
        self.w_themeColor = value_of(w_shd, "@w:themeColor")

        #: Shading Pattern Theme Color Tint
        self.w_themeTint = value_of(w_shd, "@w:themeTint")

        #: Shading Pattern Theme Color Shade
        self.w_themeShade = value_of(w_shd, "@w:themeShade")

        #: Shading Background Theme Color
        self.w_themeFill = value_of(w_shd, "@w:themeFill")

        #: Shading Background Theme Color Tint
        self.w_themeFillTint = value_of(w_shd, "@w:themeFillTint")

        #: Shading Background Theme Color Shade
        self.w_themeFillShade = value_of(w_shd, "@w:themeFillShade")

    @property
    def styles(self):
        styles = {
            "background-color": StHexColor(self.w_fill).style,
        }
        return {k: v for k, v in styles.items() if v is not None}
