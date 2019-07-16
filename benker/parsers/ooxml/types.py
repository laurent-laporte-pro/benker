# coding: utf-8


class StValue(object):
    """
    Base class of ``ST_*`` types.
    """

    def __init__(self, value, default=None):
        if value == default:
            value = None
        self.value = value

    def __repr__(self):
        cls = self.__class__.__name__
        return "<{cls}({value})>".format(cls=cls, value=self.value)

    def __str__(self):
        return "" if self.value is None else self.value

    @property
    def style(self):
        return self.value


class StTwipsMeasure(StValue):
    """
    Measurement in Twentieths of a Point
    """

    @property
    def style(self):
        return None if self.value is None else float(self.value) / 20


class StPageOrientation(StValue):
    """
    Page Orientation

    http://www.datypic.com/sc/ooxml/t-w_ST_PageOrientation.html
    """


class StHexColor(StValue):
    """
    Color Value
    """

    def __init__(self, value):
        super(StHexColor, self).__init__(value, default="auto")

    @property
    def style(self):
        return None if self.value is None else "#{}".format(self.value)
