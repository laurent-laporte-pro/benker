.. _benker__styled:

Styled
======

Description
-----------

A :class:`benker.styled.Styled` object contains a dictionary of styles.

It is mainly used for :class:`~benker.table.Table`, :class:`~benker.row.Row`,
:class:`~benker.col.Col`, and :class:`~benker.cell.Cell`.


.. doctest:: styled

    >>> from benker.styled import Styled

    >>> styled = Styled({'text-align': 'justify'})

The representation of a styled is the representation of its dictionary of styles:

.. doctest:: styled

    >>> print(styled)
    {'text-align': 'justify'}


Attributes
----------

A :class:`benker.styled.Styled` object has the following attribute:

-   *styles* is the user-defined styles: a dictionary of key-value pairs.
    This values are useful to store some HTML-like styles (border-style,
    border-width, border-color, vertical-align, text-align, etc.).
    Of course, we are not tied to the HTML-like styles, you can use your own
    styles list.

    .. note::

        The style dictionary is always copied: in other words, key-value pairs
        are copied but a shallow copy is done for the values (in general, it
        is not a problem if you use non-mutable values like :class:`str`).

Example of *styles* initialisation and shallow copy:

.. doctest:: styled

    >>> css =  { 'border-style': 'solid', 'border-width': '5px'}

    >>> one = Styled(css)
    >>> one.styles['border-width'] = '2px 10px 4px 20px'
    >>> two = Styled(one.styles)
    >>> two.styles['border-width'] = 'medium'

    >>> css
    {'border-style': 'solid', 'border-width': '5px'}

    >>> one.styles
    {'border-style': 'solid', 'border-width': '2px 10px 4px 20px'}

    >>> two.styles
    {'border-style': 'solid', 'border-width': 'medium'}
