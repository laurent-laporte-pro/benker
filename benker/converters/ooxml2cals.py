# coding: utf-8
"""
benker - ooxml2cals
=========================

:Created on: 2018-11-22
:Author: Laurent LAPORTE <llaporte@jouve.com>
"""
from benker.builders.cals import CalsBuilder
from benker.converters.base_converter import BaseConverter
from benker.parsers.ooxml import OoxmlParser


class Ooxml2CalsConverter(BaseConverter):
    parser_cls = OoxmlParser
    builder_cls = CalsBuilder


def convert_ooxml2cals(src_xml, dst_xml, **options):
    converter = Ooxml2CalsConverter()
    converter.convert_file(src_xml, dst_xml, **options)
