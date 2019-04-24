# coding: utf-8
"""
Office Open XML parser
======================

This module can parse Office Open XML (OOXML) tables.

Specifications:

- The documentation about OOXML Table is available online at
  `Word Processing - Table Grid/Column Definition <http://officeopenxml.com/WPtableGrid.php>`_.
"""
import collections
import functools

from lxml import etree

from benker.parsers.base_parser import BaseParser
from benker.parsers.base_parser import value_of as base_value_of
from benker.parsers.lxml_iterwalk import iterwalk
from benker.table import Table

#: Namespace map used for xpath evaluation in Office Open XML documents
NS = {'w': "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def ns_name(ns, name):
    return '{' + ns + '}' + name


w = functools.partial(ns_name, NS['w'])
value_of = functools.partial(base_value_of, namespaces=NS)

#: See w:ST_Border: http://www.datypic.com/sc/ooxml/t-w_ST_Border.html
#: See CSS styles: https://www.w3.org/wiki/CSS/Properties/border-top-style
_BORDER_STYLE_MAPPING = {
    # No Border
    'nil': 'none',

    # No Border
    'none': 'none',

    # Single Line Border
    'single': 'solid',

    # Single Line Border
    'thick': 'w-thick',

    # Double Line Border
    'double': 'double',

    # Dotted Line Border
    'dotted': 'dotted',

    # Dashed Line Border
    'dashed': 'dashed',

    # Dot Dash Line Border
    'dotDash': 'w-dot-dash',

    # Dot Dot Dash Line Border
    'dotDotDash': 'w-dot-dot-dash',

    # Triple Line Border
    'triple': 'w-triple',

    # Thin, Thick Line Border
    'thinThickSmallGap': 'w-thin-thick-small-gap',

    # Thick, Thin Line Border
    'thickThinSmallGap': 'w-thick-thin-small-gap',

    # Thin, Thick, Thin Line Border
    'thinThickThinSmallGap': 'w-thin-thick-thin-small-gap',

    # Thin, Thick Line Border
    'thinThickMediumGap': 'w-thin-thick-medium-gap',

    # Thick, Thin Line Border
    'thickThinMediumGap': 'w-thick-thin-medium-gap',

    # Thin, Thick, Thin Line Border
    'thinThickThinMediumGap': 'w-thin-thick-thin-medium-gap',

    # Thin, Thick Line Border
    'thinThickLargeGap': 'w-thin-thick-large-gap',

    # Thick, Thin Line Border
    'thickThinLargeGap': 'w-thick-thin-large-gap',

    # Thin, Thick, Thin Line Border
    'thinThickThinLargeGap': 'w-thin-thick-thin-large-gap',

    # Wavy Line Border
    'wave': 'w-wave',

    # Double Wave Line Border
    'doubleWave': 'w-double-wave',

    # Dashed Line Border
    'dashSmallGap': 'w-dash-small-gap',

    # Dash Dot Strokes Line Border
    'dashDotStroked': 'w-dash-dot-stroked',

    # 3D Embossed Line Border
    'threeDEmboss': 'w-three-d-emboss',

    # 3D Engraved Line Border
    'threeDEngrave': 'w-three-d-engrave',

    # Outset Line Border
    'outset': 'outset',

    # Inset Line Border
    'inset': 'inset',

    # Apples Art Border
    'apples': 'w-apples',

    # Arched Scallops Art Border
    'archedScallops': 'w-arched-scallops',

    # Baby Pacifier Art Border
    'babyPacifier': 'w-baby-pacifier',

    # Baby Rattle Art Border
    'babyRattle': 'w-baby-rattle',

    # Three Color Balloons Art Border
    'balloons3Colors': 'w-balloons3-colors',

    # Hot Air Balloons Art Border
    'balloonsHotAir': 'w-balloons-hot-air',

    # Black Dash Art Border
    'basicBlackDashes': 'w-basic-black-dashes',

    # Black Dot Art Border
    'basicBlackDots': 'w-basic-black-dots',

    # Black Square Art Border
    'basicBlackSquares': 'w-basic-black-squares',

    # Thin Line Art Border
    'basicThinLines': 'w-basic-thin-lines',

    # White Dash Art Border
    'basicWhiteDashes': 'w-basic-white-dashes',

    # White Dot Art Border
    'basicWhiteDots': 'w-basic-white-dots',

    # White Square Art Border
    'basicWhiteSquares': 'w-basic-white-squares',

    # Wide Inline Art Border
    'basicWideInline': 'w-basic-wide-inline',

    # Wide Midline Art Border
    'basicWideMidline': 'w-basic-wide-midline',

    # Wide Outline Art Border
    'basicWideOutline': 'w-basic-wide-outline',

    # Bats Art Border
    'bats': 'w-bats',

    # Birds Art Border
    'birds': 'w-birds',

    # Birds Flying Art Border
    'birdsFlight': 'w-birds-flight',

    # Cabin Art Border
    'cabins': 'w-cabins',

    # Cake Art Border
    'cakeSlice': 'w-cake-slice',

    # Candy Corn Art Border
    'candyCorn': 'w-candy-corn',

    # Knot Work Art Border
    'celticKnotwork': 'w-celtic-knotwork',

    # Certificate Banner Art Border
    'certificateBanner': 'w-certificate-banner',

    # Chain Link Art Border
    'chainLink': 'w-chain-link',

    # Champagne Bottle Art Border
    'champagneBottle': 'w-champagne-bottle',

    # Black and White Bar Art Border
    'checkedBarBlack': 'w-checked-bar-black',

    # Color Checked Bar Art Border
    'checkedBarColor': 'w-checked-bar-color',

    # Checkerboard Art Border
    'checkered': 'w-checkered',

    # Christmas Tree Art Border
    'christmasTree': 'w-christmas-tree',

    # Circles And Lines Art Border
    'circlesLines': 'w-circles-lines',

    # Circles and Rectangles Art Border
    'circlesRectangles': 'w-circles-rectangles',

    # Wave Art Border
    'classicalWave': 'w-classical-wave',

    # Clocks Art Border
    'clocks': 'w-clocks',

    # Compass Art Border
    'compass': 'w-compass',

    # Confetti Art Border
    'confetti': 'w-confetti',

    # Confetti Art Border
    'confettiGrays': 'w-confetti-grays',

    # Confetti Art Border
    'confettiOutline': 'w-confetti-outline',

    # Confetti Streamers Art Border
    'confettiStreamers': 'w-confetti-streamers',

    # Confetti Art Border
    'confettiWhite': 'w-confetti-white',

    # Corner Triangle Art Border
    'cornerTriangles': 'w-corner-triangles',

    # Dashed Line Art Border
    'couponCutoutDashes': 'w-coupon-cutout-dashes',

    # Dotted Line Art Border
    'couponCutoutDots': 'w-coupon-cutout-dots',

    # Maze Art Border
    'crazyMaze': 'w-crazy-maze',

    # Butterfly Art Border
    'creaturesButterfly': 'w-creatures-butterfly',

    # Fish Art Border
    'creaturesFish': 'w-creatures-fish',

    # Insects Art Border
    'creaturesInsects': 'w-creatures-insects',

    # Ladybug Art Border
    'creaturesLadyBug': 'w-creatures-lady-bug',

    # Cross-stitch Art Border
    'crossStitch': 'w-cross-stitch',

    # Cupid Art Border
    'cup': 'w-cup',

    # Archway Art Border
    'decoArch': 'w-deco-arch',

    # Color Archway Art Border
    'decoArchColor': 'w-deco-arch-color',

    # Blocks Art Border
    'decoBlocks': 'w-deco-blocks',

    # Gray Diamond Art Border
    'diamondsGray': 'w-diamonds-gray',

    # Double D Art Border
    'doubleD': 'w-double-d',

    # Diamond Art Border
    'doubleDiamonds': 'w-double-diamonds',

    # Earth Art Border
    'earth1': 'w-earth1',

    # Earth Art Border
    'earth2': 'w-earth2',

    # Shadowed Square Art Border
    'eclipsingSquares1': 'w-eclipsing-squares1',

    # Shadowed Square Art Border
    'eclipsingSquares2': 'w-eclipsing-squares2',

    # Painted Egg Art Border
    'eggsBlack': 'w-eggs-black',

    # Fans Art Border
    'fans': 'w-fans',

    # Film Reel Art Border
    'film': 'w-film',

    # Firecracker Art Border
    'firecrackers': 'w-firecrackers',

    # Flowers Art Border
    'flowersBlockPrint': 'w-flowers-block-print',

    # Daisy Art Border
    'flowersDaisies': 'w-flowers-daisies',

    # Flowers Art Border
    'flowersModern1': 'w-flowers-modern1',

    # Flowers Art Border
    'flowersModern2': 'w-flowers-modern2',

    # Pansy Art Border
    'flowersPansy': 'w-flowers-pansy',

    # Red Rose Art Border
    'flowersRedRose': 'w-flowers-red-rose',

    # Roses Art Border
    'flowersRoses': 'w-flowers-roses',

    # Flowers in a Teacup Art Border
    'flowersTeacup': 'w-flowers-teacup',

    # Small Flower Art Border
    'flowersTiny': 'w-flowers-tiny',

    # Gems Art Border
    'gems': 'w-gems',

    # Gingerbread Man Art Border
    'gingerbreadMan': 'w-gingerbread-man',

    # Triangle Gradient Art Border
    'gradient': 'w-gradient',

    # Handmade Art Border
    'handmade1': 'w-handmade1',

    # Handmade Art Border
    'handmade2': 'w-handmade2',

    # Heart-Shaped Balloon Art Border
    'heartBalloon': 'w-heart-balloon',

    # Gray Heart Art Border
    'heartGray': 'w-heart-gray',

    # Hearts Art Border
    'hearts': 'w-hearts',

    # Pattern Art Border
    'heebieJeebies': 'w-heebie-jeebies',

    # Holly Art Border
    'holly': 'w-holly',

    # House Art Border
    'houseFunky': 'w-house-funky',

    # Circular Art Border
    'hypnotic': 'w-hypnotic',

    # Ice Cream Cone Art Border
    'iceCreamCones': 'w-ice-cream-cones',

    # Light Bulb Art Border
    'lightBulb': 'w-light-bulb',

    # Lightning Art Border
    'lightning1': 'w-lightning1',

    # Lightning Art Border
    'lightning2': 'w-lightning2',

    # Map Pins Art Border
    'mapPins': 'w-map-pins',

    # Maple Leaf Art Border
    'mapleLeaf': 'w-maple-leaf',

    # Muffin Art Border
    'mapleMuffins': 'w-maple-muffins',

    # Marquee Art Border
    'marquee': 'w-marquee',

    # Marquee Art Border
    'marqueeToothed': 'w-marquee-toothed',

    # Moon Art Border
    'moons': 'w-moons',

    # Mosaic Art Border
    'mosaic': 'w-mosaic',

    # Musical Note Art Border
    'musicNotes': 'w-music-notes',

    # Patterned Art Border
    'northwest': 'w-northwest',

    # Oval Art Border
    'ovals': 'w-ovals',

    # Package Art Border
    'packages': 'w-packages',

    # Black Palm Tree Art Border
    'palmsBlack': 'w-palms-black',

    # Color Palm Tree Art Border
    'palmsColor': 'w-palms-color',

    # Paper Clip Art Border
    'paperClips': 'w-paper-clips',

    # Papyrus Art Border
    'papyrus': 'w-papyrus',

    # Party Favor Art Border
    'partyFavor': 'w-party-favor',

    # Party Glass Art Border
    'partyGlass': 'w-party-glass',

    # Pencils Art Border
    'pencils': 'w-pencils',

    # Character Art Border
    'people': 'w-people',

    # Waving Character Border
    'peopleWaving': 'w-people-waving',

    # Character With Hat Art Border
    'peopleHats': 'w-people-hats',

    # Poinsettia Art Border
    'poinsettias': 'w-poinsettias',

    # Postage Stamp Art Border
    'postageStamp': 'w-postage-stamp',

    # Pumpkin Art Border
    'pumpkin1': 'w-pumpkin1',

    # Push Pin Art Border
    'pushPinNote2': 'w-push-pin-note2',

    # Push Pin Art Border
    'pushPinNote1': 'w-push-pin-note1',

    # Pyramid Art Border
    'pyramids': 'w-pyramids',

    # Pyramid Art Border
    'pyramidsAbove': 'w-pyramids-above',

    # Quadrants Art Border
    'quadrants': 'w-quadrants',

    # Rings Art Border
    'rings': 'w-rings',

    # Safari Art Border
    'safari': 'w-safari',

    # Saw tooth Art Border
    'sawtooth': 'w-sawtooth',

    # Gray Saw tooth Art Border
    'sawtoothGray': 'w-sawtooth-gray',

    # Scared Cat Art Border
    'scaredCat': 'w-scared-cat',

    # Umbrella Art Border
    'seattle': 'w-seattle',

    # Shadowed Squares Art Border
    'shadowedSquares': 'w-shadowed-squares',

    # Shark Tooth Art Border
    'sharksTeeth': 'w-sharks-teeth',

    # Bird Tracks Art Border
    'shorebirdTracks': 'w-shorebird-tracks',

    # Rocket Art Border
    'skyrocket': 'w-skyrocket',

    # Snowflake Art Border
    'snowflakeFancy': 'w-snowflake-fancy',

    # Snowflake Art Border
    'snowflakes': 'w-snowflakes',

    # Sombrero Art Border
    'sombrero': 'w-sombrero',

    # Southwest-themed Art Border
    'southwest': 'w-southwest',

    # Stars Art Border
    'stars': 'w-stars',

    # Stars On Top Art Border
    'starsTop': 'w-stars-top',

    # 3-D Stars Art Border
    'stars3d': 'w-stars3d',

    # Stars Art Border
    'starsBlack': 'w-stars-black',

    # Stars With Shadows Art Border
    'starsShadowed': 'w-stars-shadowed',

    # Sun Art Border
    'sun': 'w-sun',

    # Whirligig Art Border
    'swirligig': 'w-swirligig',

    # Torn Paper Art Border
    'tornPaper': 'w-torn-paper',

    # Black Torn Paper Art Border
    'tornPaperBlack': 'w-torn-paper-black',

    # Tree Art Border
    'trees': 'w-trees',

    # Triangle Art Border
    'triangleParty': 'w-triangle-party',

    # Triangles Art Border
    'triangles': 'w-triangles',

    # Tribal Art Border One
    'tribal1': 'w-tribal1',

    # Tribal Art Border Two
    'tribal2': 'w-tribal2',

    # Tribal Art Border Three
    'tribal3': 'w-tribal3',

    # Tribal Art Border Four
    'tribal4': 'w-tribal4',

    # Tribal Art Border Five
    'tribal5': 'w-tribal5',

    # Tribal Art Border Six
    'tribal6': 'w-tribal6',

    # Twisted Lines Art Border
    'twistedLines1': 'w-twisted-lines1',

    # Twisted Lines Art Border
    'twistedLines2': 'w-twisted-lines2',

    # Vine Art Border
    'vine': 'w-vine',

    # Wavy Line Art Border
    'waveline': 'w-waveline',

    # Weaving Angles Art Border
    'weavingAngles': 'w-weaving-angles',

    # Weaving Braid Art Border
    'weavingBraid': 'w-weaving-braid',

    # Weaving Ribbon Art Border
    'weavingRibbon': 'w-weaving-ribbon',

    # Weaving Strips Art Border
    'weavingStrips': 'w-weaving-strips',

    # White Flowers Art Border
    'whiteFlowers': 'w-white-flowers',

    # Woodwork Art Border
    'woodwork': 'w-woodwork',

    # Crisscross Art Border
    'xIllusions': 'w-x-illusions',

    # Triangle Art Border
    'zanyTriangles': 'w-zany-triangles',

    # Zigzag Art Border
    'zigZag': 'w-zig-zag',

    # Zigzag stitch
    'zigZagStitch': 'w-zig-zag-stitch',
}


def _get_border_properties(w_tbl_borders, style_xpath_mapping):
    # - Get the cell properties for each direction: 'top', 'right'...
    #   Values are converted to HTML values, size are in 'pt'
    properties = []
    for style, xpath in style_xpath_mapping:
        prop = {}
        color = value_of(w_tbl_borders, xpath.format(attr='color'))
        if color and color != "auto":
            prop['color'] = "#" + color
        shadow = value_of(w_tbl_borders, xpath.format(attr='shadow'))
        if shadow:
            prop['shadow'] = {"true": True, "false": False}[shadow]
        space = value_of(w_tbl_borders, xpath.format(attr='space'))
        if space:
            # unit is 'pt'
            prop['space'] = float(space)
        sz = value_of(w_tbl_borders, xpath.format(attr='sz'))
        if sz:
            # convert eighths of a point to 'pt'
            prop['sz'] = float(sz) / 8
        val = value_of(w_tbl_borders, xpath.format(attr='val'))
        if val:
            val = "none" if val == "nil" else val  # "nil" is "none" -- no border
            prop['val'] = _BORDER_STYLE_MAPPING.get(val, 'w-' + val)
        properties.append((style, prop))
    return properties


def _border_properties_to_styles(properties):
    """
    Convert the properties to border styles.

    :param properties: Ordered list of OOXML properties

    :return: dictionary of border styles
    """
    styles = {}

    # - 'border-top', 'border-right', 'border-bottom', 'border-left'
    for style, prop in properties:
        # formats -- order is important
        formats = ('val', "{val}"), ('sz', "{sz}pt"), ('color', "{color}")
        values = [fmt.format(**prop) for key, fmt in formats if key in prop]
        if values:
            styles[style] = " ".join(values)

    if any('space' in prop for style, prop in properties):
        # - 'border-collapse' property selects a table's border model(separated or collapsing).
        #   Value is "collapse" if all spaces == 0
        spaces = [prop.get('space', 0) for style, prop in properties]
        all_spaces_are_nul = all(space == 0 for space in spaces)
        styles['border-collapse'] = "collapse" if all_spaces_are_nul else "separate"

        # - 'border-spacing' property specifies the distance between the borders of adjacent cells.
        if not all_spaces_are_nul:
            spacing = ["{0}pt".format(prop.get('space', 0)) for style, prop in properties]
            styles['border-spacing'] = " ".join(spacing)

    # - The box-shadow property attaches one or more shadows to an element.
    #   Use the border size, the default color, without effect (blur...)
    has_shadow = any(prop.get('shadow') for style, prop in properties)
    if has_shadow:
        shadow = ["{0}pt".format(prop['sz'] if prop.get('shadow') else "0pt")
                  for style, prop in properties]
        styles['box-shadow'] = " ".join(shadow)

    return styles


def _get_table_borders(w_tbl_borders):
    """
    Construct a border dictionary from the ``w:tblPr/w:tblBorders`` properties.

    See `Table Properties <http://officeopenxml.com/WPtableProperties.php>`_
    and `Table Borders <http://officeopenxml.com/WPtableBorders.php>`_.

    :param w_tbl_borders:
        Properties of the OOXML table.

    :rtype: benker.parsers.ooxml.OoxmlBorder
    :return: New instance.
    """
    # Table Cell Top Right to Bottom Left Diagonal Border
    #  http://www.datypic.com/sc/ooxml/e-w_tr2bl-1.html
    #  xpath='w:tcPr/w:tcBorders/w:tr2bl'
    #  ex.: <w:tr2bl w:val="single" w:sz="4" w:space="0" w:color="auto"/>

    # Table Cell Top Left to Bottom Right Diagonal Border
    #  http://www.datypic.com/sc/ooxml/e-w_tl2br-1.html
    #  xpath='w:tcPr/w:tcBorders/w:tl2br'
    #  ex.: <w:tl2br w:val="single" w:sz="4" w:space="0" w:color="auto"/>

    if w_tbl_borders is None:
        return {}
    # style_xpath_mapping -- order is important
    style_xpath_mapping = [
        ('border-top', "w:top/@w:{attr}"),
        ('border-right', "w:end/@w:{attr} | w:right/@w:{attr}"),
        ('border-bottom', "w:bottom/@w:{attr}"),
        ('border-left', "w:start/@w:{attr} | w:left/@w:{attr}"),
        ('x-border-tr2bl', "w:tr2bl/@w:{attr}"),
        ('x-border-tl2br', "w:tl2br/@w:{attr}"),
    ]
    properties = _get_border_properties(w_tbl_borders, style_xpath_mapping)
    styles = _border_properties_to_styles(properties)
    return styles


def _get_cell_borders(w_tbl_borders):
    """
    Construct a border dictionary from the ``w:tblPr/w:tblBorders`` properties.

    See `Table Properties <http://officeopenxml.com/WPtableProperties.php>`_
    and `Table Borders <http://officeopenxml.com/WPtableBorders.php>`_.

    :param w_tbl_borders:
        Properties of the OOXML table.

    :rtype: benker.parsers.ooxml.OoxmlBorder
    :return: New instance.
    """
    if w_tbl_borders is None:
        return {}
    # style_xpath_mapping -- order is important
    style_xpath_mapping = [
        ('border-top', "w:insideH/@w:{attr}"),
        ('border-right', "w:insideV/@w:{attr}"),
        ('border-bottom', "w:insideH/@w:{attr}"),
        ('border-left', "w:insideV/@w:{attr}"),
    ]
    properties = _get_border_properties(w_tbl_borders, style_xpath_mapping)
    styles = _border_properties_to_styles(properties)
    return styles


def _get_style_borders(w_styles, style_id):
    if w_styles is None or style_id is None:
        return {}
    w_style = value_of(w_styles, 'w:style[@w:styleId = "{0}"]'.format(style_id))
    if w_style is None:
        return {}

    # - get parent styles (if it exist)
    based_on_id = value_of(w_style, 'w:basedOn/@w:val')
    parent_styles = _get_style_borders(w_styles, based_on_id)

    # - get child styles
    w_tbl_borders = value_of(w_style, 'w:tblPr/w:tblBorders')
    table_borders = _get_table_borders(w_tbl_borders)
    cell_borders = _get_cell_borders(w_tbl_borders)
    child_styles = table_borders.copy()
    child_styles.update({'x-cell-' + key: value for key, value in cell_borders.items()})

    # - *child_styles* override *parent_styles*
    real_styles = parent_styles.copy()
    real_styles.update({key: value for key, value in child_styles.items() if value is not None})
    return real_styles


class OoxmlParser(BaseParser):
    """
    Office Open XML to CALS tables parsers.
    """

    class _State(object):
        """
        Parsing state for the converter (internal usage).
        """

        def __init__(self):
            self.col_pos = 0
            self.col = None
            self.row_pos = 0
            self.row = None
            self.table = None

        reset = __init__

        def next_col(self):
            self.col_pos += 1
            self.col = None

        def next_row(self):
            self.col_pos = 0
            self.col = None
            self.row_pos += 1
            self.row = None

    def __init__(self, builder, styles_path=None, **options):
        """
        Construct a parser

        :type  builder: benker.builders.base_builder.BaseBuilder
        :param builder:
            Builder used by this parser to instantiate :class:`~benker.table.Table` objects.

        :param str styles_path:
            Path to the stylesheet to use to resole table styles.
            In an uncompressed ``.docx`` tree structure, the stylesheet path
            is ``word/styles.xml``.

        :param str options: Extra conversion options.
            See :meth:`~benker.converters.base_converter.BaseConverter.convert_file`
            to have a list of all possible options.
        """
        self._state = self._State()
        self._w_styles = None
        self.styles_path = styles_path
        super(OoxmlParser, self).__init__(builder, **options)

    def transform_tables(self, tree):
        self._w_styles = etree.parse(self.styles_path) if self.styles_path else None
        self._w_styles = self._w_styles or value_of(tree, ".//w:styles")

        for w_tbl in tree.xpath("//w:tbl", namespaces=NS):
            table = self.parse_table(w_tbl)
            table_elem = self.builder.generate_table_tree(table)
            parent = w_tbl.getparent()
            index = parent.index(w_tbl)
            parent.insert(index, table_elem)
            table_elem.tail = w_tbl.tail
            parent.remove(w_tbl)

    def parse_table(self, w_tbl):
        """
        Convert a Office Open XML ``<w:tbl>`` into CALS ``<table>``

        :type  w_tbl: etree._Element
        :param w_tbl: Office Open XML element.

        :rtype: etree.Element
        :return: CALS element.
        """
        state = self._state
        state.reset()

        elements = {w(name) for name in {'tbl', 'tblGrid', 'gridCol', 'tr', 'tc'}}
        context = iterwalk(w_tbl, events=('start', 'end'), tag=elements)

        depth = 0
        for action, elem in context:
            elem_tag = elem.tag
            if elem_tag == w('tbl'):
                if action == 'start':
                    depth += 1
                else:
                    depth -= 1
            if depth > 1:
                # .. note:: context.skip_subtree() is not available for all version of lxml
                # This <tbl> element is inside the table.
                # It will be handled separately in another call to convert_tbl()
                continue
            if action == 'start':
                if elem_tag == w('tbl'):
                    self.parse_tbl(elem)

                elif elem_tag == w('tblGrid'):
                    # this element has no specific data
                    pass

                elif elem_tag == w('gridCol'):
                    state.next_col()
                    self.parse_grid_col(elem)

                elif elem_tag == w('tr'):
                    state.next_row()
                    self.parse_tr(elem)

                elif elem_tag == w('tc'):
                    state.next_col()
                    self.parse_tc(elem)

                else:
                    raise NotImplementedError(elem_tag)
            else:
                if elem_tag == w('tr'):
                    # add missing entries
                    for _ in range(state.col_pos, len(state.table.cols)):
                        state.row.insert_cell(None)

        return state.table

    def parse_tbl(self, w_tbl):
        """
        Parse a ``<w:tbl>`` element.

        See: `Table Properties <http://officeopenxml.com/WPtableProperties.php>`_.

        :type  w_tbl: etree._Element
        :param w_tbl: Table element.

        .. versionchanged:: 0.4.0
           The section width and height are now stored in the 'x-sect-size' table style (units in 'pt').
        """
        style_id = value_of(w_tbl, "w:tblPr/w:tblStyle/@w:val")

        # - Table and borders are extracted from the style (if possible)
        #   and then from the ``w:tblPr/w:tblBorders`` properties.

        style_borders = _get_style_borders(self._w_styles, style_id)
        w_tbl_borders = value_of(w_tbl, 'w:tblPr/w:tblBorders')

        # - Table borders (frame) and Cell borders (colsep/rowsep) use the "x-cell-" prefix

        table_borders = _get_table_borders(w_tbl_borders)
        real_table_borders = style_borders.copy()
        real_table_borders.update({key: value for key, value in table_borders.items() if value is not None})

        attrs = real_table_borders.copy()

        # -- Sections: http://officeopenxml.com/WPsection.php

        # A section's properties are stored in a sectPr element.
        # For all sections except the last section, the sectPr element is stored as
        # a child element of the last paragraph in the section. For the last section,
        # the sectPr is stored as a child element of the body element.

        w_sect_pr = value_of(w_tbl, 'following::w:p/w:pPr/w:sectPr | following::w:sectPr')

        # - ``x-sect-orient``: Section orientation
        #   Possible values are "landscape" and "portrait".
        sect_orient = value_of(w_sect_pr, 'w:pgSz/@w:orient')
        if sect_orient:
            attrs['x-sect-orient'] = sect_orient

        # - ``x-sect-size``: Section size (width and height)
        sect_w = value_of(w_sect_pr, 'w:pgSz/@w:w')
        sect_h = value_of(w_sect_pr, 'w:pgSz/@w:h')
        if sect_w and sect_h:
            # convert twentieths of a point to 'pt'
            attrs['x-sect-size'] = float(sect_w) / 20, float(sect_h) / 20

        # - w:cols -- Specifies the set of columns for the section.
        # - ``x-sect-cols``: Section column number
        #   Default value is "1" -- useful for @pgwide
        sect_cols = value_of(w_sect_pr, 'w:cols/@w:num')
        if sect_cols is None:
            if w_sect_pr is None:
                sect_cols = "1"  # type: str
            else:
                sect_cols = w_sect_pr.xpath('count(w:cols/w:col)', namespaces=NS)  # type: float
                sect_cols = str(int(sect_cols)) if sect_cols else "1"  # type: str
        attrs['x-sect-cols'] = sect_cols

        # - The HTML ``class`` attribute is not a regular style.
        #   We use the table ``nature``instead.

        self._state.table = Table(styles=attrs, nature=style_id)

    def parse_grid_col(self, w_grid_col):
        """
        Parse a ``<w:gridCol>`` element.

        See: `Table Grid/Column Definition <http://officeopenxml.com/WPtableGrid.php>`_.

        :type  w_grid_col: etree._Element
        :param w_grid_col: Table element.
        """
        # w:w => width of the column in twentieths of a point.
        width = float(w_grid_col.attrib[w('w')]) / 20  # pt
        state = self._state
        styles = {u"width": u"{0:0.2f}pt".format(width)}
        state.col = state.table.cols[state.col_pos]
        state.col.styles.update(styles)

    def parse_tr(self, w_tr):
        """
        Parse a ``<w:tr>`` element.

        See: `Table Row Properties <http://officeopenxml.com/WPtableRowProperties.php>`_.

        :type  w_tr: etree._Element
        :param w_tr: Table element.
        """

        # - w:tblHeader => the current row should be repeated at the top
        #   of each new page on which the table is displayed.
        #   This is a simple boolean property, so you can specify a val attribute of true or false.
        #
        #   <w:trPr>
        #     <w:tblHeader/>
        #   </w:trPr>
        #
        w_tbl_header = value_of(w_tr, "w:trPr/w:tblHeader")
        if w_tbl_header is not None:
            w_tbl_header = value_of(w_tr, "w:trPr/w:tblHeader/@w:val", default=u"true")
        nature = {"true": u"head", "false": u"body", None: u"body"}[w_tbl_header]
        state = self._state
        state.row = state.table.rows[state.row_pos]
        state.row.nature = nature

        # - w:trHeight => height of the row
        #
        #   <w:trPr>
        #     <w:trHeight w:val="567"/>
        #   </w:trPr>
        #
        w_tr_height = value_of(w_tr, "w:trPr/w:trHeight")
        if w_tr_height is not None:
            h_rule = value_of(w_tr, "w:trPr/w:tblHeader/@w:hRule", default="auto")
            # Possible values are:
            # - atLeast (height should be at least the value specified),
            # - exact (height should be exactly the value specified), or
            # - auto (height is determined based on the height of the contents, so the value is ignored).
            style = {'atLeast': u'min-height', 'exact': u'height', 'auto': None}[h_rule]
            if style:
                val = value_of(w_tr, "w:trPr/w:tblHeader/@w:val", default="0")
                # Specifies the row's height, in twentieths of a point.
                height = float(val) / 20  # pt
                state.row.styles[style] = "{0:0.2f}pt".format(height)

        # - w:ins => revision marks: A row can be marked as "inserted".
        #
        #   <w:trPr>
        #     <w:ins w:id="0" w:author="Laurent Laporte" w:date="2018-11-21T18:08:00Z"/>
        #   </w:trPr>
        #
        w_ins = value_of(w_tr, "w:trPr/w:ins")
        if w_ins is not None:
            state.row.styles['x-ins'] = True
            style_xpath_mapping = [
                ('x-ins-id', "w:trPr/w:ins/@w:id"),
                ('x-ins-author', "w:trPr/w:ins/@w:author"),
                ('x-ins-date', "w:trPr/w:ins/@w:date"),
            ]
            for style, xpath in style_xpath_mapping:
                value = value_of(w_tr, xpath)
                if value:
                    state.row.styles[style] = value

        # note: ``vertical-align`` attribute is not available for a row => see w:tcPr instead

    def parse_tc(self, w_tc):
        """
        Parse a ``<w:tc>`` element.

        See: `Table Cell Properties <http://officeopenxml.com/WPtableCellProperties.php>`_.

        :type  w_tc: etree._Element
        :param w_tc: Table element.
        """
        state = self._state

        # w:gridSpan => number of logical columns across which the cell spans
        width = int(value_of(w_tc, "w:tcPr/w:gridSpan/@w:val", default=u"1"))

        # take the colspan into account:
        state.col_pos += width - 1

        # w:vMerge => specifies that the cell is part of a vertically merged set of cells.
        w_v_merge = value_of(w_tc, "w:tcPr/w:vMerge")
        if w_v_merge is not None:
            w_v_merge = value_of(w_tc, "w:tcPr/w:vMerge/@w:val", default=u"continue")
        if w_v_merge is None:
            # no merge
            height = 1
        elif w_v_merge == u"continue":
            # the current cell continues a previously existing merge group
            state.table.expand((state.col_pos, state.row.row_pos - 1), height=1)
            height = None
        elif w_v_merge == u"restart":
            # the current cell starts a new merge group
            height = 1
        else:
            raise NotImplementedError(w_v_merge)

        if height:
            styles = {}

            # -- Vertical alignment
            #
            # w:vAlign => Specifies the vertical alignment for text between the top and bottom margins of the cell.
            #
            # Possible values are:
            # - bottom - Specifies that the text should be vertically aligned to the bottom margin.
            # - center - Specifies that the text should be vertically aligned to the center of the cell.
            # - top - Specifies that the text should be vertically aligned to the top margin.
            w_v_align = value_of(w_tc, "w:tcPr/w:vAlign")
            if w_v_align is not None:
                w_v_align = value_of(w_tc, "w:tcPr/w:vAlign/@w:val", default=u"top")
                # CSS/Properties/vertical-align
                # valid values: http://www.datypic.com/sc/ooxml/t-w_ST_VerticalJc.html
                v_align = {"top": u"top",
                           "center": u"middle",
                           "bottom": u"bottom",
                           "both": u"w-both"}[w_v_align]
                styles["vertical-align"] = v_align

            # -- Horizontal alignment
            #
            # Horizontal alignment is done at paragraph level, inside the cell.
            # We can calculate the cell alignment base on the paragraph properties,
            # for instance ``<w:p><w:pPr><w:jc w:val="right"/>``,
            # see: http://officeopenxml.com/WPalignment.php
            #
            # We use the most common alignment for cell alignment.
            w_p_list = w_tc.xpath("w:p", namespaces=NS)
            w_jc_counter = collections.Counter(value_of(w_p, "w:pPr/w:jc/@w:val") for w_p in w_p_list)
            w_jc = w_jc_counter.most_common(1)[0][0]  # type: str or None
            if w_jc is not None:
                # CSS/Properties/text-align
                # valid values: http://www.datypic.com/sc/ooxml/t-w_ST_Jc.html
                align = {"start": u"left",
                         "end": u"right",
                         "left": u"left",
                         "right": u"right",
                         "center": u"center",
                         "both": u"justify",
                         "distribute": u"justify",
                         # "mediumKashida": None,
                         # "numTab": None,
                         # "lowKashida": None,
                         # "thaiDistribute": None
                         }[w_jc]
                styles["align"] = align

            # -- Borders
            w_tc_borders = value_of(w_tc, 'w:tcPr/w:tcBorders')
            cell_borders = _get_table_borders(w_tc_borders)
            styles.update(cell_borders)

            # todo: calculate the ``@rotate`` attribute.

            content = w_tc.xpath('w:p | w:tbl', namespaces=NS)
            state.row.insert_cell(content, width=width, height=height, styles=styles)
