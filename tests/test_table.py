# coding: utf-8

import textwrap

from benker.table import Table


def test_colspan():
    # fmt: off
    table = Table()
    table.cols[1].insert_cell("one")
    table.cols[1].insert_cell("spanned", width=2)
    table.cols[2].insert_cell("two")
    text = str(table)
    assert text == textwrap.dedent("""\
    +-----------+-----------+
    |    one    |    two    |
    +-----------------------+
    |  spanned              |
    +-----------------------+""")
    # fmt: on


def test_rowspan():
    # fmt: off
    table = Table()
    table.rows[1].insert_cell("one")
    table.rows[1].insert_cell("spanned", height=2)
    table.rows[2].insert_cell("two")
    text = str(table)
    assert text == textwrap.dedent("""\
    +-----------+-----------+
    |    one    |  spanned  |
    +-----------|           |
    |    two    |           |
    +-----------+-----------+""")
    # fmt: on


def test_fill_missing_cells():
    # fmt: off
    table = Table()
    table.rows[1].insert_cell("one")
    table.rows[1].insert_cell("two")
    table.rows[1].insert_cell("three")
    table.rows[1].insert_cell("four", height=2)
    table.rows[2].insert_cell("un-deux", width=2)

    table.fill_missing(table.bounding_box, "???")
    text = str(table)
    assert text == textwrap.dedent("""\
    +-----------+-----------+-----------+-----------+
    |    one    |    two    |   three   |   four    |
    +-----------------------+-----------|           |
    |  un-deux              |    ???    |           |
    +-----------------------+-----------+-----------+""")
    # fmt: on
