# coding: utf-8
"""
Miscellaneous Functions
=======================

Miscellaneous functions used in color parsing and conversion.
"""


def parse_num_value(value, rgb_scale):
    # type: (str, int or float) -> float
    if value.endswith("%"):
        return float(value[:-1]) * rgb_scale / 100
    else:
        return float(value)
