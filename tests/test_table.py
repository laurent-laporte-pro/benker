# coding: utf-8

import textwrap

from benker.table import Table


def test_fill_missing_cells():
    table = Table()
    table.rows[1].insert_cell("one")
    table.rows[1].insert_cell("two")
    table.rows[1].insert_cell("three")
    table.rows[1].insert_cell("four", height=2)
    table.rows[2].insert_cell("un-deux", width=2)

    table.fill_missing("???")
    text = str(table)
    assert text == textwrap.dedent("""\
    +-----------+-----------+-----------+-----------+
    |    one    |    two    |   three   |   four    |
    +-----------------------+-----------|           |
    |  un-deux              |    ???    |           |
    +-----------------------+-----------+-----------+""")
