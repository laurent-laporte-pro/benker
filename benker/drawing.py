# coding: utf-8
"""
Drawing
=======

Utility functions used to draw a :class:`~benker.grid.Grid`.
"""
from benker.box import Box

#: Default tiles used to draw a :class:`~benker.grid.Grid`.
#:
#: Keys are tuples (*left*, *top*, *right*, *bottom*) : which represent the
#: presence (if ``True``) or absence (if ``False``) : of the border.
#: Values are the string representation of the tiles,
#: "XXXXXXXXX" will be replaced by the cell content.
TILES = {
    (True, True, True, True): """\
+-----------+
| XXXXXXXXX |
+-----------+
""",
    (True, True, True, False): """\
+-----------+
| XXXXXXXXX |
""",
    (True, True, False, True): """\
+-----------
| XXXXXXXXX 
+-----------
""",
    (True, True, False, False): """\
+-----------
| XXXXXXXXX 
""",

    (True, False, True, True): """\
|           |
| XXXXXXXXX |
+-----------+
""",
    (True, False, True, False): """\
|           |
| XXXXXXXXX |
""",
    (True, False, False, True): """\
|           
| XXXXXXXXX 
+-----------
""",
    (True, False, False, False): """\
|           
| XXXXXXXXX 
""",

    (False, True, True, True): """\
------------+
  XXXXXXXXX |
------------+
""",
    (False, True, True, False): """\
------------+
  XXXXXXXXX |
""",
    (False, True, False, True): """\
------------
  XXXXXXXXX 
------------
""",
    (False, True, False, False): """\
------------
  XXXXXXXXX 
""",

    (False, False, True, True): """\
            |
  XXXXXXXXX |
------------+
""",
    (False, False, True, False): """\
            |
  XXXXXXXXX |
""",
    (False, False, False, True): """\
            
  XXXXXXXXX 
------------
""",
    (False, False, False, False): """\
            
  XXXXXXXXX 
""",
}


def iter_tiles(grid, tiles=None):
    tiles = tiles or TILES
    bb = grid.bounding_box
    for row_idx in range(bb.min.y, bb.max.y + 1):
        row = []
        for col_idx in range(bb.min.x, bb.max.x + 1):
            coord = col_idx, row_idx
            if coord in grid:
                cell = grid[coord]
                box = cell.box
                text = str(cell)
            else:
                box = Box(col_idx, row_idx)
                text = ""
            left = box.min.x == col_idx
            top = box.min.y == row_idx
            right = bb.max.x == col_idx
            bottom = bb.max.y == row_idx
            tile = tiles[(left, top, right, bottom)]
            if (box.min.x + box.max.x) // 2 == col_idx and (box.min.y + box.max.y) // 2 == row_idx:
                title = "{0:^9}".format(str(text))[:9]
                tile = tile.replace('XXXXXXXXX', title)
            else:
                tile = tile.replace('XXXXXXXXX', ' ' * 9)
            row.append(tile)
        yield row


def iter_lines(grid, tiles=None):
    for row in iter_tiles(grid, tiles):
        tiles = [list(filter(None, tile.splitlines())) for tile in row]
        size = len(tiles[0])
        for index in range(size):
            yield "".join(tile[index] for tile in tiles)


def draw(grid, tiles=None):
    """
    Draw a grid using a collection of tiles.

    :type  grid: benker.grid.Grid
    :param grid: Grid to draw.

    :param tiles:
        Collection of tiles, use :data:`~benker.drawing.TILES` if not provided.

    :return: String representation of the grid.
    """
    if grid:
        return "\n".join(iter_lines(grid, tiles))
    return ""
