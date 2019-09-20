# coding: utf-8
"""
CALS - Frame Styles
===================

.. versionadded:: 0.5.0
"""

#: Default value for a solid border (for @cals:frame/@cals:colsep/@cals:rowsep, ...)
BORDER_SOLID = "solid 1pt black"

#: Default value for no border (for @cals:frame/@cals:colsep/@cals:rowsep, ...)
BORDER_NONE = "none"


def get_frame_styles(frame):
    styles = {}
    if not frame:
        return styles
    top, bottom, left, right = {
        "none": (False, False, False, False),
        "all": (True, True, True, True),
        "topbot": (True, True, False, False),
        "sides": (False, False, True, True),
        "top": (True, False, False, False),
        "bottom": (False, True, False, False),
    }[frame]
    styles["border-top"] = BORDER_SOLID if top else BORDER_NONE
    styles["border-bottom"] = BORDER_SOLID if bottom else BORDER_NONE
    styles["border-left"] = BORDER_SOLID if left else BORDER_NONE
    styles["border-right"] = BORDER_SOLID if right else BORDER_NONE
    return styles
