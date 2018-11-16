# coding: utf-8
"""
Units
=====

Utility functions to convert values from one unit to another.
"""

#: Usual units Lengths in meter
UNITS = {
    'mm': 0.001, 'dm': 0.1, 'cm': 0.01, 'm': 1.0,
    'in': 0.001 * 25.4,
    'ft': 0.3048,
    'px': 0.001 * 25.4 / 72,
    'pt': 0.001 * 25.4 / 72,
    'pc': 0.001 * 25.4 / 12,
}


def convert_value(value, unit_in, unit_out):
    """
    Convert a value from one unit to another.

    To convert '1pt' to 'mm', you can do:

    .. doctest:: units_demo

        >>> from benker.units import convert_value

        >>> convert_value(1, 'pt', 'mm')
        0.353

    :type  value: int or float
    :param value: Value to convert

    :param unit_in: Current unit of the value.

    :param unit_out: Expected unit of the value.

    :rtype:  float
    :return: The converted value
    """
    return round(value * UNITS[unit_in] / UNITS[unit_out], 3)
