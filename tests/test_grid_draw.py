# coding: utf-8
import textwrap

from benker.cell import Cell
from benker.drawing import draw
from benker.grid import Grid


def test_g1():
    g1 = Grid([
        Cell("aaa", x=1, y=1, width=2), Cell("bb", x=3, y=1),
        Cell("cc", x=1, y=2), Cell("dddddddddd", x=2, y=2, width=2)
    ])
    actual = draw(g1)
    expected = textwrap.dedent("""\
    +-----------------------+-----------+
    |    aaa                |    bb     |
    +-----------+-----------------------+
    |    cc     | ddddddddd             |
    +-----------+-----------------------+""")
    assert expected == actual


def test_g2():
    g2 = Grid([
        Cell("aaaaaa", x=1, y=1, width=2), Cell("bb", x=3, y=1),
        Cell("cc", x=1, y=2), Cell("dddddd", x=2, y=2, width=2)
    ])
    actual = draw(g2)
    expected = textwrap.dedent("""\
    +-----------------------+-----------+
    |  aaaaaa               |    bb     |
    +-----------+-----------------------+
    |    cc     |  dddddd               |
    +-----------+-----------------------+""")
    assert expected == actual


def test_g3():
    g3 = Grid([
        Cell("aaa", x=1, y=1, width=2), Cell("b", x=3, y=1),
        Cell("cc", x=1, y=2), Cell("ddddd", x=2, y=2, width=2)
    ])
    actual = draw(g3)
    expected = textwrap.dedent("""\
    +-----------------------+-----------+
    |    aaa                |     b     |
    +-----------+-----------------------+
    |    cc     |   ddddd               |
    +-----------+-----------------------+""")
    assert expected == actual


def test_g4():
    g4 = Grid([
        Cell("aa", x=1, y=1, height=2), Cell("bbb", x=2, y=1, width=2),
        Cell("ccc", x=2, y=2, height=2), Cell("dd", x=3, y=2),
        Cell("eeee", x=1, y=3), Cell("ffffff", x=3, y=3),
    ])
    actual = draw(g4)
    expected = textwrap.dedent("""\
    +-----------+-----------------------+
    |    aa     |    bbb                |
    |           +-----------+-----------+
    |           |    ccc    |    dd     |
    +-----------|           +-----------+
    |   eeee    |           |  ffffff   |
    +-----------+-----------+-----------+""")
    assert expected == actual


def test_g5():
    g5 = Grid([
        Cell("aa", x=1, y=1, height=2), Cell("bb", x=2, y=1), Cell("cccc", x=3, y=1),
        Cell("ddd", x=2, y=2), Cell("eeeee", x=3, y=2),
        Cell("ff", x=1, y=3, width=2), Cell("gggggg", x=3, y=3),
    ])
    actual = draw(g5)
    expected = textwrap.dedent("""\
    +-----------+-----------+-----------+
    |    aa     |    bb     |   cccc    |
    |           +-----------+-----------+
    |           |    ddd    |   eeeee   |
    +-----------------------+-----------+
    |    ff                 |  gggggg   |
    +-----------------------+-----------+""")
    assert expected == actual


def test_g6():
    g6 = Grid([
        Cell("a", x=1, y=1), Cell("bb", x=2, y=1),
        Cell("cc", x=1, y=2), Cell("d", x=2, y=2)
    ])
    actual = draw(g6)
    expected = textwrap.dedent("""\
    +-----------+-----------+
    |     a     |    bb     |
    +-----------+-----------+
    |    cc     |     d     |
    +-----------+-----------+""")
    assert expected == actual


def test_g7():
    g7 = Grid([
        Cell("aa", x=1, y=1, height=2), Cell("bb", x=2, y=1), Cell("cccc", x=3, y=1),
        Cell("ddd", x=2, y=2), Cell("eeeee", x=3, y=2),
        Cell("ffffff", x=1, y=3, width=2), Cell("gggggg", x=3, y=3),
    ])
    actual = draw(g7)
    expected = textwrap.dedent("""\
    +-----------+-----------+-----------+
    |    aa     |    bb     |   cccc    |
    |           +-----------+-----------+
    |           |    ddd    |   eeeee   |
    +-----------------------+-----------+
    |  ffffff               |  gggggg   |
    +-----------------------+-----------+""")
    assert expected == actual
