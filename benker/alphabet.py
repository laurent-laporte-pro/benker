# coding: utf-8
"""
Alphabet
========

Utility functions to convert integer into a base-26 "number", and vis versa.
"""

try:
    from string import uppercase as ascii_uppercase
except ImportError:
    from string import ascii_uppercase


def int_to_alphabet(value, alphabet=ascii_uppercase):
    """
    Convert a non-nul integer into a base-26 "number" using uppercase ASCII letters.

    Usage:

    .. doctest:: alphabet_demo

        >>> from benker.alphabet import int_to_alphabet

        >>> int_to_alphabet(1)
        'A'
        >>> int_to_alphabet(2)
        'B'
        >>> int_to_alphabet(26)
        'Z'
        >>> int_to_alphabet(27)
        'AA'
        >>> int_to_alphabet(28)
        'AB'
        >>> int_to_alphabet(52)
        'AZ'
        >>> int_to_alphabet(53)
        'BA'
        >>> int_to_alphabet(18278)
        'ZZZ'
        >>> int_to_alphabet(-5)
        Traceback (most recent call last):
            ...
        ValueError: -5

    :param int value: value to convert
    :param alphabet: alphabet to use for the conversion.
    :return: string representing this "number" in the base-26.
    """
    if value == 0:
        return ""
    elif value < 0:
        raise ValueError(value)
    size = len(alphabet)
    q, r = divmod(value - 1, size)
    letters = [alphabet[r]]
    while q:
        q, r = divmod(q - 1, size)
        letters.insert(0, alphabet[r])
    return "".join(letters)


def alphabet_to_int(letters, alphabet=ascii_uppercase):
    """
    Convert a base-26 "number" using uppercase ASCII letters into an integer.

    .. doctest:: alphabet_demo

        >>> from benker.alphabet import alphabet_to_int

        >>> alphabet_to_int("A")
        1
        >>> alphabet_to_int("B")
        2
        >>> alphabet_to_int("AA")
        27
        >>> alphabet_to_int("AB")
        28
        >>> alphabet_to_int("ZZZ")
        18278
        >>> alphabet_to_int("")
        0
        >>> alphabet_to_int("AA@")
        Traceback (most recent call last):
            ...
        ValueError: AA@

    :param letters: string representing a "number" in the base-26.
    :param alphabet: alphabet to use for the conversion.
    :return: Integer value of the "number".
    """
    value = 0
    size = len(alphabet)
    try:
        for letter in letters:
            value *= size
            value += alphabet.index(letter) + 1
        return value
    except ValueError:
        raise ValueError(letters)
