# coding: utf-8
"""
Units
=====

Utility functions to convert values from one unit to another.
"""

#: Usual units Lengths in meter
import re

UNITS = {
    'mm': 0.001, 'dm': 0.1, 'cm': 0.01, 'm': 1.0,
    'in': 0.001 * 25.4,
    'ft': 0.3048,
    'px': 0.001 * 25.4 / 72,
    'pt': 0.001 * 25.4 / 72,
    'pc': 0.001 * 25.4 / 12,
    'em': 12 * 0.001 * 25.4 / 72,  # 1em = 12pt
}


def convert_unit(value, unit_in, unit_out):
    """
    Convert a value from one unit to another.

    To convert '1pt' to 'mm', you can do:

    .. doctest:: units_demo

        >>> from benker.units import convert_unit

        >>> convert_unit(1, 'pt', 'mm')
        0.353

    :type  value: int or float
    :param value: Value to convert

    :param unit_in: Current unit of the value.

    :param unit_out: Expected unit of the value.

    :rtype:  float
    :return: The converted value
    """
    return round(value * UNITS[unit_in] / UNITS[unit_out], 3)


def convert_value(value, unit_out='pt'):
    """
    Convert a value with unit into another one.

    Examples:

    .. doctest:: units_demo

        >>> from benker.units import convert_value

        >>> convert_value('1cm')
        28.346

        >>> convert_value('1cm', unit_out='mm')
        10.0

        >>> convert_value('0')
        0.0

        >>> convert_value('thin')
        0.5


    :param value: String value with unit, for instance: '0.5em'.

    :param unit_out: Expected unit of the value.

    :rtype:  float
    :return: The converted value
    """
    value = {"thin": ".5pt", "medium": "1pt", "thick": "2pt"}.get(value, value)
    value, unit = re.findall(r"([+-]?(?:[0-9]*[.])?[0-9]+)(\w*)", value)[0]
    if unit:
        return convert_unit(float(value), unit, unit_out)
    return float(value)
