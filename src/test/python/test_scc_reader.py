#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2020, Sandflow Consulting LLC
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Unit tests for the SCC reader"""

# pylint: disable=R0201,C0115,C0116,W0212
import unittest
from numbers import Number
from typing import Union, Type, Optional

from ttconv.model import Br, P, ContentElement, CellResolutionType
from ttconv.scc.reader import to_model, to_disassembly
from ttconv.style_properties import StyleProperties, CoordinateType, LengthType, FontStyleType, NamedColors, TextDecorationType, \
  StyleProperty, ExtentType, ColorType, DisplayAlignType, ShowBackgroundType
from ttconv.time_code import SmpteTimeCode, FPS_30

LOREM_IPSUM = """Lorem ipsum dolor sit amet,
consectetur adipiscing elit.
Pellentesque interdum lacinia sollicitudin.
Integer luctus et ligula ac sagittis.
Ut at diam sit amet nulla fringilla
vestibulum nec vitae nisi.
"""


class SccReaderTest(unittest.TestCase):

  def check_caption(self, paragraph: P, caption_id: str, begin: str, end: Optional[str], *children):
    self.assertEqual(caption_id, paragraph.get_id())
    self.assertEqual(SmpteTimeCode.parse(begin, FPS_30).to_temporal_offset(), paragraph.get_begin())

    if end is not None:
      self.assertEqual(SmpteTimeCode.parse(end, FPS_30).to_temporal_offset(), paragraph.get_end())

    p_children = list(paragraph)
    self.assertEqual(len(children), len(p_children))

    for (index, child) in enumerate(p_children):
      expected_child = children[index]
      if isinstance(expected_child, str):
        texts = list(child)
        self.assertEqual(expected_child, texts[0].get_text())
      else:
        self.assertEqual(expected_child, Br)

  def check_element_style(self, elem: ContentElement, style_property: Type[StyleProperty], expected_value):
    self.assertEqual(expected_value, elem.get_style(style_property))

  def check_element_origin(self, elem: ContentElement, expected_x_origin: Union[int, float, Number],
                           expected_y_origin: Union[int, float, Number], unit=LengthType.Units.c):
    expected_origin = CoordinateType(x=LengthType(value=expected_x_origin, units=unit),
                                     y=LengthType(value=expected_y_origin, units=unit))
    self.check_element_style(elem, StyleProperties.Origin, expected_origin)

  def check_element_extent(self, elem: ContentElement, width: Union[int, float, Number], height: Union[int, float, Number],
                           unit=LengthType.Units.c):
    expected_extent = ExtentType(width=LengthType(value=width, units=unit),
                                 height=LengthType(value=height, units=unit))
    self.check_element_style(elem, StyleProperties.Extent, expected_extent)

  def check_region_origin(self, elem: ContentElement, expected_x_cell_origin: int, expected_y_cell_origin: int,
                          cell_resolution: CellResolutionType):
    expected_x_origin = round(expected_x_cell_origin * 100 / cell_resolution.columns)
    expected_y_origin = round(expected_y_cell_origin * 100 / cell_resolution.rows)
    self.check_element_origin(elem, expected_x_origin, expected_y_origin, unit=LengthType.Units.pct)

  def check_region_extent(self, elem: ContentElement, expected_cell_width: int, expected_cell_height: int,
                          cell_resolution: CellResolutionType):
    width = round(expected_cell_width * 100 / cell_resolution.columns)
    height = round(expected_cell_height * 100 / cell_resolution.rows)
    self.check_element_extent(elem, width, height, unit=LengthType.Units.pct)

  def test_scc_pop_on_content(self):
    scc_content = """Scenarist_SCC V1.0

01:02:53:14	94ae 94ae 9420 9420 947a 947a 97a2 97a2 a820 68ef f26e 2068 ef6e 6be9 6e67 2029 942c 942c 8080 8080 942f 942f

01:02:55:14	942c 942c

01:03:27:29	94ae 94ae 9420 9420 94f2 94f2 c845 d92c 2054 c845 91b0 45ae 942c 942c 8080 8080 942f 942f

01:11:31:01	9420 9420 9452 9452 97a1 97a1 54e5 73f4 2080 9132 2043 6170 f4e9 ef6e 2080 94f2 94f2 97a1 97a1 54e5 73f4 2080 91ae 91ae f4e5 73f4 9120 9120 2043 6170 f4e9 ef6e 7380 942c 942c 942f 942f

01:11:33:14	942c 942c

01:16:17:15	9420 9420 9570 9570 91ae 91ae 4c6f 7265 6d20 6970 7375 6d20 96c8 96c8 646f 6c6f 7220 7369 7420 616d 6574 2c80 9670 9670 91ae 91ae 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e 942c 942c 942f 942f

01:16:19:23	942c 942c

01:20:56:00	9420 9420 9370 9370 656e 7465 7371 7565 2069 6e74 6572 6475 6d20 6c61 6369 6e69 6120 736f 6c6c 6963 6974 7564 696e 2e80 942c 942c 942f 942f

01:22:19:23	942c 942c
"""

    scc_disassembly = """\
01:02:53:14	{ENM}{ENM}{RCL}{RCL}{1520}{1520}{TO2}{TO2}( horn honking ){EDM}{EDM}{}{}{EOC}{EOC}
01:02:55:14	{EDM}{EDM}
01:03:27:29	{ENM}{ENM}{RCL}{RCL}{1504}{1504}HEY, THE®E.{EDM}{EDM}{}{}{EOC}{EOC}
01:11:31:01	{RCL}{RCL}{1404}{1404}{TO1}{TO1}Test ½ Caption {1504}{1504}{TO1}{TO1}Test {I}{I}test{Wh}{Wh} Captions{EDM}{EDM}{EOC}{EOC}
01:11:33:14	{EDM}{EDM}
01:16:17:15	{RCL}{RCL}{0600}{0600}{I}{I}Lorem ipsum {07R}{07R}dolor sit amet,{0800}{0800}{I}{I}consectetur adipiscing elit.{EDM}{EDM}{EOC}{EOC}
01:16:19:23	{EDM}{EDM}
01:20:56:00	{RCL}{RCL}{1300}{1300}entesque interdum lacinia sollicitudin.{EDM}{EDM}{EOC}{EOC}
01:22:19:23	{EDM}{EDM}
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    region_1 = doc.get_region("pop1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 26, 17, doc.get_cell_resolution())
    self.check_region_extent(region_1, 10, 1, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_2 = doc.get_region("pop2")
    self.assertIsNotNone(region_2)
    self.check_region_origin(region_2, 8, 17, doc.get_cell_resolution())
    self.check_region_extent(region_2, 11, 1, doc.get_cell_resolution())
    self.check_element_style(region_2, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_2, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_3 = doc.get_region("pop3")
    self.assertIsNotNone(region_3)
    self.check_region_origin(region_3, 9, 16, doc.get_cell_resolution())
    self.check_region_extent(region_3, 20, 2, doc.get_cell_resolution())
    self.check_element_style(region_3, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_3, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_4 = doc.get_region("pop4")
    self.assertIsNotNone(region_4)
    self.check_region_origin(region_4, 4, 8, doc.get_cell_resolution())
    self.check_region_extent(region_4, 29, 10, doc.get_cell_resolution())
    self.check_element_style(region_4, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_4, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_5 = doc.get_region("pop5")
    self.assertIsNotNone(region_5)
    self.check_region_origin(region_5, 4, 15, doc.get_cell_resolution())
    self.check_region_extent(region_5, 32, 3, doc.get_cell_resolution())
    self.check_element_style(region_5, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_5, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    body = doc.get_body()
    self.assertIsNotNone(body)

    div_list = list(body)
    self.assertEqual(1, len(div_list))
    div = div_list[0]
    self.assertIsNotNone(div)

    p_list = list(div)
    self.assertEqual(5, len(p_list))

    self.check_caption(p_list[0], "caption1", "01:02:54:00", "01:02:55:15", "( horn honking )")
    self.assertEqual(region_1, p_list[0].get_region())

    self.check_caption(p_list[1], "caption2", "01:03:28:12", "01:11:31:28", "HEY, THE®E.")
    self.assertEqual(region_2, p_list[1].get_region())

    self.check_caption(p_list[2], "caption3", "01:11:31:29", "01:11:33:15", "Test ½ Caption ", Br, "Test ", " test", "  Captions")
    self.assertEqual(region_3, p_list[2].get_region())

    self.check_caption(p_list[3], "caption4", "01:16:18:21", "01:16:19:24", " Lorem ipsum ", Br, "dolor sit amet,", Br,
                       " consectetur adipiscing elit.")
    self.assertEqual(region_4, p_list[3].get_region())

    self.check_caption(p_list[4], "caption5", "01:20:56:24", "01:22:19:24", "entesque interdum lacinia sollicitudin.")
    self.assertEqual(region_5, p_list[4].get_region())

    self.check_element_style(list(p_list[2])[3], StyleProperties.FontStyle, FontStyleType.italic)
    self.check_element_style(list(p_list[2])[4], StyleProperties.FontStyle, None)
    self.check_element_style(list(p_list[2])[4], StyleProperties.Color, NamedColors.white.value)

    self.check_element_style(list(p_list[3])[0], StyleProperties.FontStyle, FontStyleType.italic)
    self.check_element_style(list(p_list[3])[2], StyleProperties.Color, NamedColors.red.value)
    self.check_element_style(list(p_list[3])[4], StyleProperties.FontStyle, FontStyleType.italic)

    self.check_element_style(p_list[0][0], StyleProperties.BackgroundColor, NamedColors.black.value)

  def test_scc_pop_on_content_unexpectedly_ended(self):
    scc_content = """\
Scenarist_SCC V1.0

00:00:02:16	942c

00:00:03:01	9420 93F0 91ae 9421 4c6f 7265 6d20 6970 7375 6d20 94D0 646f 6c6f 7220 7369 7420 616d 6574 2c80 9470 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e 942c 942f

00:00:11:27	9420
"""

    scc_disassembly = """\
00:00:02:16	{EDM}
00:00:03:01	{RCL}{1300}{I}{BS}Lorem ipsum {1400}dolor sit amet,{1500}consectetur adipiscing elit.{EDM}{EOC}
00:00:11:27	{RCL}
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    region_1 = doc.get_region("pop1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 4, 15, doc.get_cell_resolution())
    self.check_region_extent(region_1, 28, 3, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    body = doc.get_body()
    self.assertIsNotNone(body)

    div_list = list(body)
    self.assertEqual(1, len(div_list))
    div = div_list[0]
    self.assertIsNotNone(div)

    p_list = list(div)
    self.assertEqual(1, len(p_list))

    self.check_caption(p_list[0], "caption1", "00:00:04:07", None, "Lorem ipsum ", Br, "dolor sit amet,", Br,
                       "consectetur adipiscing elit.")
    self.assertEqual(region_1, p_list[0].get_region())

  def test_2_rows_roll_up_content(self):
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:22	9425 9425 94ad 94ad 9470 9470 4c6f 7265 6d20 6970 7375 6d20 646f 6c6f 7220 7369 7420 616d 6574 2c80

00:00:02:23	9425 9425 94ad 94ad 9673 9673 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e

00:00:04:17	9425 9425 94ad 94ad 9473 9473 5065 6c6c 656e 7465 7371 7565 2069 6e74 6572 6475 6d20 6c61 6369 6e69 6120 736f 6c6c 6963 6974 7564 696e 2e80

00:00:06:04	9425 9425 94ad 94ad 9470 9470 496e 7465 6765 7220 6c75 6374 7573 2065 7420 6c69 6775 6c61 2061 6320 7361 6769 7474 6973 2e80

"""

    scc_disassembly = """\
00:00:00:22	{RU2}{RU2}{CR}{CR}{1500}{1500}Lorem ipsum dolor sit amet,
00:00:02:23	{RU2}{RU2}{CR}{CR}{0804}{0804}consectetur adipiscing elit.
00:00:04:17	{RU2}{RU2}{CR}{CR}{1504}{1504}Pellentesque interdum lacinia sollicitudin.
00:00:06:04	{RU2}{RU2}{CR}{CR}{1500}{1500}Integer luctus et ligula ac sagittis.
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    region_1 = doc.get_region("rollup1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 4, 2, doc.get_cell_resolution())
    self.check_region_extent(region_1, 32, 15, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.after)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    body = doc.get_body()
    self.assertIsNotNone(body)

    div_list = list(body)
    self.assertEqual(1, len(div_list))
    div = div_list[0]
    self.assertIsNotNone(div)

    p_list = list(div)
    self.assertEqual(4, len(p_list))

    expected_text = LOREM_IPSUM.splitlines()

    self.check_caption(p_list[0], "caption1", "00:00:00:23", "00:00:02:24", expected_text[0])
    self.assertEqual(region_1, p_list[0].get_region())

    self.check_caption(p_list[1], "caption2", "00:00:02:24", "00:00:04:18", expected_text[0], Br, expected_text[1])
    self.assertEqual(region_1, p_list[1].get_region())

    self.check_caption(p_list[2], "caption3", "00:00:04:18", "00:00:06:05", expected_text[1], Br, expected_text[2])
    self.assertEqual(region_1, p_list[2].get_region())

    self.check_element_style(list(p_list[2])[2], StyleProperties.TextDecoration,
                             TextDecorationType(underline=True))

    self.check_caption(p_list[3], "caption4", "00:00:06:05", None, expected_text[2], Br, expected_text[3])
    self.assertEqual(region_1, p_list[3].get_region())

    self.check_element_style(list(p_list[3])[0], StyleProperties.TextDecoration,
                             TextDecorationType(underline=True))

    self.check_element_style(p_list[0][0], StyleProperties.BackgroundColor, NamedColors.black.value)

  def test_3_rows_roll_up_content(self):
    scc_content = """\
Scenarist_SCC V1.0

00:00:17;01	9426 9426 94ad 94ad 9470 9470 4c6f 7265 6d20 6970 7375 6d20 646f 6c6f 7220 7369 7420 616d 6574 2c80

00:00:18;19	9426 9426 94ad 94ad 9470 9470 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e

00:00:20;06	9426 9426 94ad 94ad 9470 9470 5065 6c6c 656e 7465 7371 7565 2069 6e74 6572 6475 6d20 6c61 6369 6e69 6120 736f 6c6c 6963 6974 7564 696e 2e80

00:00:21;24	9426 9426 94ad 94ad 9470 9470 496e 7465 6765 7220 6c75 6374 7573 2065 7420 6c69 6775 6c61 2061 6320 7361 6769 7474 6973 2e80
"""

    scc_disassembly = """\
00:00:17;01	{RU3}{RU3}{CR}{CR}{1500}{1500}Lorem ipsum dolor sit amet,
00:00:18;19	{RU3}{RU3}{CR}{CR}{1500}{1500}consectetur adipiscing elit.
00:00:20;06	{RU3}{RU3}{CR}{CR}{1500}{1500}Pellentesque interdum lacinia sollicitudin.
00:00:21;24	{RU3}{RU3}{CR}{CR}{1500}{1500}Integer luctus et ligula ac sagittis.
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    region_1 = doc.get_region("rollup1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 4, 2, doc.get_cell_resolution())
    self.check_region_extent(region_1, 32, 15, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.after)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    body = doc.get_body()
    self.assertIsNotNone(body)

    div_list = list(body)
    self.assertEqual(1, len(div_list))
    div = div_list[0]
    self.assertIsNotNone(div)

    p_list = list(div)
    self.assertEqual(4, len(p_list))

    expected_text = LOREM_IPSUM.splitlines()

    self.check_caption(p_list[0], "caption1", "00:00:17;02", "00:00:18;20", expected_text[0])
    self.assertEqual(region_1, p_list[0].get_region())

    self.check_caption(p_list[1], "caption2", "00:00:18;20", "00:00:20;07", expected_text[0], Br, expected_text[1])
    self.assertEqual(region_1, p_list[1].get_region())

    self.check_caption(p_list[2], "caption3", "00:00:20;07", "00:00:21;25", expected_text[0], Br, expected_text[1], Br,
                       expected_text[2])
    self.assertEqual(region_1, p_list[2].get_region())

    self.check_caption(p_list[3], "caption4", "00:00:21;25", None, expected_text[1], Br, expected_text[2], Br,
                       expected_text[3])
    self.assertEqual(region_1, p_list[3].get_region())

    self.check_element_style(p_list[0][0], StyleProperties.BackgroundColor, NamedColors.black.value)


  def test_4_rows_roll_up_content(self):
    scc_content = """\
Scenarist_SCC V1.0

00:00:34;27	94a7 94ad 9470 4c6f 7265 6d20 6970 7375 6d20 646f 6c6f 7220 7369 7420 616d 6574 2c80

00:00:36;12	94a7 94ad 9470 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e

00:00:44;08	94a7 94ad 9470 5065 6c6c 656e 7465 7371 7565 2069 6e74 6572 6475 6d20 6c61 6369 6e69 6120 736f 6c6c 6963 6974 7564 696e 2e80

00:00:47;12	94a7 94ad 9470 496e 7465 6765 7220 6c75 6374 7573 2065 7420 6c69 6775 6c61 2061 6320 7361 6769 7474 6973 2e80

00:00:49;03	94a7 94ad 9470 5574 2061 7420 6469 616d 2073 6974 2061 6d65 7420 6e75 6c6c 6120 6672 696e 6769 6c6c 6180

00:00:50;23	94a7 94ad 9470 7665 7374 6962 756c 756d 206e 6563 2076 6974 6165 206e 6973 692e
"""

    scc_disassembly = """\
00:00:34;27	{RU4}{CR}{1500}Lorem ipsum dolor sit amet,
00:00:36;12	{RU4}{CR}{1500}consectetur adipiscing elit.
00:00:44;08	{RU4}{CR}{1500}Pellentesque interdum lacinia sollicitudin.
00:00:47;12	{RU4}{CR}{1500}Integer luctus et ligula ac sagittis.
00:00:49;03	{RU4}{CR}{1500}Ut at diam sit amet nulla fringilla
00:00:50;23	{RU4}{CR}{1500}vestibulum nec vitae nisi.
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    region_1 = doc.get_region("rollup1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 4, 2, doc.get_cell_resolution())
    self.check_region_extent(region_1, 32, 15, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.after)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    body = doc.get_body()
    self.assertIsNotNone(body)

    div_list = list(body)
    self.assertEqual(1, len(div_list))
    div = div_list[0]
    self.assertIsNotNone(div)

    p_list = list(div)
    self.assertEqual(6, len(p_list))

    expected_text = LOREM_IPSUM.splitlines()

    self.check_caption(p_list[0], "caption1", "00:00:34;28", "00:00:36;13", expected_text[0])
    self.assertEqual(region_1, p_list[0].get_region())

    self.check_caption(p_list[1], "caption2", "00:00:36;13", "00:00:44;09", expected_text[0], Br, expected_text[1])
    self.assertEqual(region_1, p_list[1].get_region())

    self.check_caption(p_list[2], "caption3", "00:00:44;09", "00:00:47;13", expected_text[0], Br, expected_text[1], Br,
                       expected_text[2])
    self.assertEqual(region_1, p_list[2].get_region())

    self.check_caption(p_list[3], "caption4", "00:00:47;13", "00:00:49;04", expected_text[0], Br, expected_text[1], Br,
                       expected_text[2], Br, expected_text[3])
    self.assertEqual(region_1, p_list[3].get_region())

    self.check_caption(p_list[4], "caption5", "00:00:49;04", "00:00:50;24", expected_text[1], Br, expected_text[2], Br,
                       expected_text[3], Br, expected_text[4])
    self.assertEqual(region_1, p_list[4].get_region())

    self.check_caption(p_list[5], "caption6", "00:00:50;24", None, expected_text[2], Br, expected_text[3], Br,
                       expected_text[4], Br, expected_text[5])
    self.assertEqual(region_1, p_list[5].get_region())

    self.check_element_style(p_list[0][0], StyleProperties.BackgroundColor, NamedColors.black.value)


  def test_mix_rows_roll_up_content(self):
    scc_content = """\
Scenarist_SCC V1.0

00:00:00;22	9425 9425 94ad 94ad 9470 9470 3e3e 3e20 c849 ae80

00:00:02;23	9425 9425 94ad 94ad 9470 9470 49a7 cd20 cb45 d649 ce20 43d5 cece 49ce c720 c1ce c420 c154

00:00:04;17	9425 9425 94ad 94ad 9470 9470 49ce d645 d354 4f52 a7d3 20c2 c1ce cb20 5745 20c2 454c 4945 d645 2049 ce80

00:00:06;04	9425 9425 94ad 94ad 9470 9470 c845 4cd0 49ce c720 54c8 4520 4c4f 43c1 4c20 ce45 49c7 c8c2 4f52 c84f 4fc4 d380

00:00:09;21	9425 9425 94ad 94ad 9470 9470 c1ce c420 91ae 91ae 49cd d052 4fd6 49ce c720 9120 9120 54c8 4520 4c49 d645 d320 4f46 20c1 4c4c

00:00:11;07	9425 9425 94ad 94ad 9470 9470 5745 20d3 4552 d645 ae80

00:00:12;07	9425 9425 94ad 94ad 9470 9470 91b0 9131 9132 9132

00:00:13;07	9425 9425 94ad 94ad 9470 9470 c1c2 c3c4 c580 91bf

00:00:14;07	9425 9425 94ad 94ad 9470 9470 c180 9220 c580 92a1 4f80 92a2 2080 92a7

00:00:17;01	9426 9426 94ad 94ad 9470 9470 57c8 4552 4520 d94f d5a7 5245 20d3 54c1 cec4 49ce c720 ce4f 572c

00:00:18;19	9426 9426 94ad 94ad 9470 9470 4c4f 4fcb 49ce c720 4fd5 5420 54c8 4552 452c 2054 c8c1 54a7 d320 c14c 4c80

00:00:20;06	9426 9426 94ad 94ad 9470 9470 54c8 4520 4352 4f57 c4ae

00:00:21;24	9426 9426 94ad 94ad 9470 9470 3e3e 2049 5420 57c1 d320 902d 902d c74f 4fc4 902e 902e 2054 4f20 c245 2049 ce20 54c8 4580

00:00:34;27	94a7 94ad 9470 c16e 6420 f2e5 73f4 eff2 e520 49ef f761 a773 20ec 616e 642c 20f7 61f4 e5f2

00:00:36;12	94a7 94ad 9470 c16e 6420 f7e9 ec64 ece9 e6e5 ae80

00:00:44;08	94a7 94ad 9470 3e3e 20c2 e96b e520 49ef f761 2c20 79ef 75f2 2073 ef75 f2e3 e520 e6ef f280

"""

    scc_disassembly = """\
00:00:00;22	{RU2}{RU2}{CR}{CR}{1500}{1500}>>> HI.
00:00:02;23	{RU2}{RU2}{CR}{CR}{1500}{1500}I'M KEVIN CUNNING AND AT
00:00:04;17	{RU2}{RU2}{CR}{CR}{1500}{1500}INVESTOR'S BANK WE BELIEVE IN
00:00:06;04	{RU2}{RU2}{CR}{CR}{1500}{1500}HELPING THE LOCAL NEIGHBORHOODS
00:00:09;21	{RU2}{RU2}{CR}{CR}{1500}{1500}AND {I}{I}IMPROVING {Wh}{Wh}THE LIVES OF ALL
00:00:11;07	{RU2}{RU2}{CR}{CR}{1500}{1500}WE SERVE.
00:00:12;07	{RU2}{RU2}{CR}{CR}{1500}{1500}®°½½
00:00:13;07	{RU2}{RU2}{CR}{CR}{1500}{1500}ABCDEû
00:00:14;07	{RU2}{RU2}{CR}{CR}{1500}{1500}AÁEÉOÓ ¡
00:00:17;01	{RU3}{RU3}{CR}{CR}{1500}{1500}WHERE YOU'RE STANDING NOW,
00:00:18;19	{RU3}{RU3}{CR}{CR}{1500}{1500}LOOKING OUT THERE, THAT'S ALL
00:00:20;06	{RU3}{RU3}{CR}{CR}{1500}{1500}THE CROWD.
00:00:21;24	{RU3}{RU3}{CR}{CR}{1500}{1500}>> IT WAS {BMaS}{BMaS}GOOD{BBk}{BBk} TO BE IN THE
00:00:34;27	{RU4}{CR}{1500}And restore Iowa's land, water
00:00:36;12	{RU4}{CR}{1500}And wildlife.
00:00:44;08	{RU4}{CR}{1500}>> Bike Iowa, your source for
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    region_1 = doc.get_region("rollup1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 4, 2, doc.get_cell_resolution())
    self.check_region_extent(region_1, 32, 15, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.after)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    body = doc.get_body()
    self.assertIsNotNone(body)

    div_list = list(body)
    self.assertEqual(1, len(div_list))
    div = div_list[0]
    self.assertIsNotNone(div)

    p_list = list(div)
    self.assertEqual(16, len(p_list))

    self.check_caption(p_list[0], "caption1", "00:00:00;23", "00:00:02;24", ">>> HI.")
    self.assertEqual(region_1, p_list[0].get_region())

    self.check_caption(p_list[1], "caption2", "00:00:02;24", "00:00:04;18", ">>> HI.", Br, "I'M KEVIN CUNNING AND AT")
    self.assertEqual(region_1, p_list[1].get_region())

    self.check_caption(p_list[2], "caption3", "00:00:04;18", "00:00:06;05", "I'M KEVIN CUNNING AND AT", Br,
                       "INVESTOR'S BANK WE BELIEVE IN")
    self.assertEqual(region_1, p_list[2].get_region())

    self.check_caption(p_list[3], "caption4", "00:00:06;05", "00:00:09;22", "INVESTOR'S BANK WE BELIEVE IN", Br,
                       "HELPING THE LOCAL NEIGHBORHOODS")
    self.assertEqual(region_1, p_list[3].get_region())

    self.check_caption(p_list[4], "caption5", "00:00:09;22", "00:00:11;08", "HELPING THE LOCAL NEIGHBORHOODS", Br, "AND ",
                       " IMPROVING ", " THE LIVES OF ALL")
    self.assertEqual(region_1, p_list[4].get_region())

    self.check_caption(p_list[5], "caption6", "00:00:11;08", "00:00:12;08", "AND ", " IMPROVING ", " THE LIVES OF ALL", Br,
                       "WE SERVE.")
    self.assertEqual(region_1, p_list[5].get_region())

    self.check_caption(p_list[6], "caption7", "00:00:12;08", "00:00:13;08", "WE SERVE.", Br, "®°½")
    self.assertEqual(region_1, p_list[6].get_region())

    self.check_caption(p_list[7], "caption8", "00:00:13;08", "00:00:14;08", "®°½", Br, "ABCDEû")
    self.assertEqual(region_1, p_list[7].get_region())

    self.check_caption(p_list[8], "caption9", "00:00:14;08", "00:00:17;02", "ABCDEû", Br, "ÁÉÓ¡")
    self.assertEqual(region_1, p_list[8].get_region())

    self.check_caption(p_list[9], "caption10", "00:00:17;02", "00:00:18;20", "ABCDEû", Br, "ÁÉÓ¡", Br, "WHERE YOU'RE STANDING NOW,")
    self.assertEqual(region_1, p_list[9].get_region())

    self.check_caption(p_list[10], "caption11", "00:00:18;20", "00:00:20;07", "ÁÉÓ¡", Br, "WHERE YOU'RE STANDING NOW,", Br,
                       "LOOKING OUT THERE, THAT'S ALL")
    self.assertEqual(region_1, p_list[10].get_region())

    self.check_caption(p_list[11], "caption12", "00:00:20;07", "00:00:21;25", "WHERE YOU'RE STANDING NOW,", Br,
                       "LOOKING OUT THERE, THAT'S ALL", Br, "THE CROWD.")
    self.assertEqual(region_1, p_list[11].get_region())

    self.check_caption(p_list[12], "caption13", "00:00:21;25", "00:00:34;28", "LOOKING OUT THERE, THAT'S ALL", Br, "THE CROWD.", Br,
                       ">> IT WAS ", "GOOD", " TO BE IN THE")
    self.assertEqual(region_1, p_list[12].get_region())

    self.check_caption(p_list[13], "caption14", "00:00:34;28", "00:00:36;13", "LOOKING OUT THERE, THAT'S ALL", Br, "THE CROWD.", Br,
                       ">> IT WAS ", "GOOD", " TO BE IN THE", Br, "And restore Iowa's land, water")
    self.assertEqual(region_1, p_list[13].get_region())

    self.check_caption(p_list[14], "caption15", "00:00:36;13", "00:00:44;09", "THE CROWD.", Br, ">> IT WAS ", "GOOD",
                       " TO BE IN THE", Br,
                       "And restore Iowa's land, water", Br, "And wildlife.")
    self.assertEqual(region_1, p_list[14].get_region())

    self.check_caption(p_list[15], "caption16", "00:00:44;09", None, ">> IT WAS ", "GOOD", " TO BE IN THE", Br,
                       "And restore Iowa's land, water", Br, "And wildlife.", Br, ">> Bike Iowa, your source for")
    self.assertEqual(region_1, p_list[15].get_region())

    self.check_element_style(list(p_list[4])[3], StyleProperties.FontStyle, FontStyleType.italic)
    self.check_element_style(list(p_list[5])[1], StyleProperties.FontStyle, FontStyleType.italic)

    semi_transparent_magenta = ColorType((255, 0, 255, 136))
    self.check_element_style(list(p_list[12])[5], StyleProperties.BackgroundColor, semi_transparent_magenta)
    self.check_element_style(list(p_list[13])[5], StyleProperties.BackgroundColor, semi_transparent_magenta)
    self.check_element_style(list(p_list[14])[3], StyleProperties.BackgroundColor, semi_transparent_magenta)
    self.check_element_style(list(p_list[15])[1], StyleProperties.BackgroundColor, semi_transparent_magenta)

    self.check_element_style(p_list[0][0], StyleProperties.BackgroundColor, NamedColors.black.value)

  def test_scc_paint_on_content(self):
    scc_content = """\
Scenarist_SCC V1.0

00:02:53:14	9429 9429 94d2 94d2 4c6f 7265 6d20 6970 7375 6d20 646f 6c6f 7220 7369 7420 616d 6574 2c80 94f2 94f2 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e

00:02:56:00	9429 9429 94d2 94d2 5065 6c6c 656e 7465 7371 7565 2069 6e74 6572 6475 6d20 6c61 6369 6e69 6120 736f 6c6c 6963 6974 7564 696e 2e80

00:02:56:25	9429 9429 94f2 94f2 496e 7465 6765 7220 6c75 6374 7573 2065 7420 6c69 6775 6c61 2061 6320 7361 6769 7474 6973 2e80

"""

    scc_disassembly = """\
00:02:53:14	{RDC}{RDC}{1404}{1404}Lorem ipsum dolor sit amet,{1504}{1504}consectetur adipiscing elit.
00:02:56:00	{RDC}{RDC}{1404}{1404}Pellentesque interdum lacinia sollicitudin.
00:02:56:25	{RDC}{RDC}{1504}{1504}Integer luctus et ligula ac sagittis.
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    region_1 = doc.get_region("paint1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 8, 16, doc.get_cell_resolution())
    self.check_region_extent(region_1, 28, 2, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    body = doc.get_body()
    self.assertIsNotNone(body)

    div_list = list(body)
    self.assertEqual(1, len(div_list))

    div = div_list[0]
    self.assertIsNotNone(div)

    p_list = list(div)
    self.assertEqual(4, len(p_list))

    self.check_caption(p_list[0], "caption1", "00:02:53:15", "00:02:56:01", "Lorem ", "ipsum ", "dolor ", "sit ", "amet,")
    self.assertEqual(region_1, p_list[0].get_region())

    self.assertIsNone(list(p_list[0])[0].get_begin())
    self.assertAlmostEqual(0.1333, float(list(p_list[0])[1].get_begin()), delta=0.0001)
    self.assertAlmostEqual(0.2333, float(list(p_list[0])[2].get_begin()), delta=0.0001)
    self.assertAlmostEqual(0.3333, float(list(p_list[0])[3].get_begin()), delta=0.0001)
    self.assertAlmostEqual(0.4, float(list(p_list[0])[4].get_begin()), delta=0.0001)

    self.check_caption(p_list[1], "caption2", "00:02:54:01", "00:02:56:26", "consectetur ", "adipiscing", " elit.")
    self.assertEqual(region_1, p_list[1].get_region())

    self.assertIsNone(list(p_list[1])[0].get_begin())
    self.assertAlmostEqual(0.2, float(list(p_list[1])[1].get_begin()), delta=0.0001)
    self.assertAlmostEqual(0.4, float(list(p_list[1])[2].get_begin()), delta=0.0001)

    self.check_caption(p_list[2], "caption3", "00:02:56:01", None, "Pellentesque", " interdum ", "lacinia ",
                       "sollicitudin.")
    self.assertEqual(region_1, p_list[2].get_region())

    self.assertIsNone(list(p_list[2])[0].get_begin())
    self.assertAlmostEqual(0.2666, float(list(p_list[2])[1].get_begin()), delta=0.0001)
    self.assertAlmostEqual(0.4, float(list(p_list[2])[2].get_begin()), delta=0.0001)
    self.assertAlmostEqual(0.5333, float(list(p_list[2])[3].get_begin()), delta=0.0001)

    self.check_caption(p_list[3], "caption4", "00:02:56:26", None, "Integer ", "luctus", " et ", "ligula", " ac ",
                       "sagittis.")
    self.assertEqual(region_1, p_list[3].get_region())

    self.assertIsNone(list(p_list[3])[0].get_begin())
    self.assertAlmostEqual(0.1666, float(list(p_list[3])[1].get_begin()), delta=0.0001)
    self.assertAlmostEqual(0.3, float(list(p_list[3])[2].get_begin()), delta=0.0001)
    self.assertAlmostEqual(0.3333, float(list(p_list[3])[3].get_begin()), delta=0.0001)
    self.assertAlmostEqual(0.4666, float(list(p_list[3])[4].get_begin()), delta=0.0001)
    self.assertAlmostEqual(0.5, float(list(p_list[3])[5].get_begin()), delta=0.0001)

    self.check_element_style(p_list[0][0], StyleProperties.BackgroundColor, NamedColors.black.value)


if __name__ == '__main__':
  unittest.main()
