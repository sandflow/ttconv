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
from fractions import Fraction
from numbers import Number
from typing import List, Union, Type, Optional

from ttconv import model
from ttconv.isd import ISD
from ttconv.model import Br, P, ContentElement, CellResolutionType, Span
from ttconv.scc.codes.attribute_codes import SccAttributeCode
from ttconv.scc.reader import to_model, to_disassembly
from ttconv.style_properties import StyleProperties, CoordinateType, LengthType, FontStyleType, NamedColors, TextDecorationType, \
  StyleProperty, ExtentType, ColorType, DisplayAlignType, ShowBackgroundType
from ttconv.time_code import FPS_29_97, SmpteTimeCode

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
    self.check_element_timecode(paragraph.get_begin(), begin)

    if end is not None:
      self.check_element_timecode(paragraph.get_end(), end)

    p_children = list(paragraph)
    self.assertEqual(len(children), len(p_children))

    for (index, child) in enumerate(p_children):
      expected_child = children[index]
      if isinstance(expected_child, str):
        texts = list(child)
        self.assertEqual(expected_child, texts[0].get_text())
      else:
        self.assertEqual(expected_child, Br)

  @staticmethod
  def get_rows(paragraph: P) -> List[str]:
    """Returns the text of the rows of a paragraph, an empty row being an empty
    string"""
    rows = [""]
    for child in paragraph:
      if isinstance(child, Br):
        rows.append("")
      else:
        rows[-1] += list(child)[0].get_text()
    return rows

  def check_captions(self, doc: model.ContentDocument, expected_captions: list):
    """Checks the paragraphs of a document against a list of (id, begin, end,
    rows, region id) tuples"""
    p_list = list(list(doc.get_body())[0])

    self.assertEqual([rows for (_, _, _, rows, _) in expected_captions], [self.get_rows(p) for p in p_list])

    for (p, (caption_id, begin, end, _, region_id)) in zip(p_list, expected_captions):
      self.assertEqual(caption_id, p.get_id())
      self.check_element_timecode(p.get_begin(), begin)
      if end is None:
        self.assertIsNone(p.get_end())
      else:
        self.check_element_timecode(p.get_end(), end)
      self.assertEqual(region_id, p.get_region().get_id())

  def check_element_timecode(self, timecode: Fraction, expected_timecode: str):
    self.assertEqual(SmpteTimeCode.parse(expected_timecode, FPS_29_97).to_temporal_offset(), timecode)

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

01:02:53:14	94ae 94ae 9420 9420 9476 9476 97a2 97a2 a820 68ef f26e 2068 ef6e 6be9 6e67 2029 942c 942c 8080 8080 942f 942f

01:02:55:14	942c 942c

01:03:27:29	94ae 94ae 9420 9420 94f2 94f2 c845 d92c 2054 c845 91b0 45ae 942c 942c 8080 8080 942f 942f

01:11:31:01	9420 9420 9452 9452 97a1 97a1 54e5 73f4 2080 9132 2043 6170 f4e9 ef6e 2080 94f2 94f2 97a1 97a1 54e5 73f4 2080 91ae 91ae f4e5 73f4 9120 9120 2043 6170 f4e9 ef6e 7380 942c 942c 942f 942f

01:11:33:14	942c 942c

01:16:17:15	9420 9420 9570 9570 91ae 91ae 4c6f 7265 6d20 6970 7375 6d20 96c8 96c8 646f 6c6f 7220 7369 7420 616d 6574 2c80 9670 9670 91ae 91ae 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e 942c 942c 942f 942f

01:16:19:23	942c 942c

01:20:56:00	9420 9420 9370 9370 d0e5 ecec e56e f4e5 73f1 75e5 20e9 6ef4 e5f2 6475 6d20 ec61 e375 73ae 942c 942c 942f 942f

01:22:19:23	942c 942c
"""

    scc_disassembly = """\
01:02:53:14	{ENM}{ENM}{RCL}{RCL}{1512}{1512}{TO2}{TO2}( horn honking ){EDM}{EDM}{}{}{EOC}{EOC}
01:02:55:14	{EDM}{EDM}
01:03:27:29	{ENM}{ENM}{RCL}{RCL}{1504}{1504}HEY, THE®E.{EDM}{EDM}{}{}{EOC}{EOC}
01:11:31:01	{RCL}{RCL}{1404}{1404}{TO1}{TO1}Test ½ Caption {1504}{1504}{TO1}{TO1}Test {I}{I}test{Wh}{Wh} Captions{EDM}{EDM}{EOC}{EOC}
01:11:33:14	{EDM}{EDM}
01:16:17:15	{RCL}{RCL}{0600}{0600}{I}{I}Lorem ipsum {07R}{07R}dolor sit amet,{0800}{0800}{I}{I}consectetur adipiscing elit.{EDM}{EDM}{EOC}{EOC}
01:16:19:23	{EDM}{EDM}
01:20:56:00	{RCL}{RCL}{1300}{1300}Pellentesque interdum lacus.{EDM}{EDM}{EOC}{EOC}
01:22:19:23	{EDM}{EDM}
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    region_1 = doc.get_region("pop1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 18, 16, doc.get_cell_resolution())
    self.check_region_extent(region_1, 16, 1, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_2 = doc.get_region("pop2")
    self.assertIsNotNone(region_2)
    self.check_region_origin(region_2, 8, 16, doc.get_cell_resolution())
    self.check_region_extent(region_2, 11, 1, doc.get_cell_resolution())
    self.check_element_style(region_2, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_2, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_3 = doc.get_region("pop3")
    self.assertIsNotNone(region_3)
    self.check_region_origin(region_3, 9, 15, doc.get_cell_resolution())
    self.check_region_extent(region_3, 20, 2, doc.get_cell_resolution())
    self.check_element_style(region_3, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_3, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_4 = doc.get_region("pop4")
    self.assertIsNotNone(region_4)
    self.check_region_origin(region_4, 4, 7, doc.get_cell_resolution())
    self.check_region_extent(region_4, 29, 10, doc.get_cell_resolution())
    self.check_element_style(region_4, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_4, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_5 = doc.get_region("pop5")
    self.assertIsNotNone(region_5)
    self.check_region_origin(region_5, 4, 14, doc.get_cell_resolution())
    self.check_region_extent(region_5, 28, 3, doc.get_cell_resolution())
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

    self.check_caption(p_list[0], "caption1", "01:02:54:04", "01:02:55:14", "( horn honking )")
    self.assertEqual(region_1, p_list[0].get_region())

    self.check_caption(p_list[1], "caption2", "01:03:28:15", "01:11:32:04", "HEY, THE®E.")
    self.assertEqual(region_2, p_list[1].get_region())

    self.check_caption(p_list[2], "caption3", "01:11:32:06", "01:11:33:14", "Test ½ Caption ", Br, "Test ", " test", "  Captions")
    self.assertEqual(region_3, p_list[2].get_region())

    self.check_caption(p_list[3], "caption4", "01:16:18:27", "01:16:19:23", " Lorem ipsum ", Br, "dolor sit amet,", Br,
                       " consectetur adipiscing elit.")
    self.assertEqual(region_4, p_list[3].get_region())

    self.check_caption(p_list[4], "caption5", "01:20:56:20", "01:22:19:23", "Pellentesque interdum lacus.")
    self.assertEqual(region_5, p_list[4].get_region())

    self.check_element_style(list(p_list[2])[3], StyleProperties.FontStyle, FontStyleType.italic)
    self.check_element_style(list(p_list[2])[4], StyleProperties.FontStyle, None)
    self.check_element_style(list(p_list[2])[4], StyleProperties.Color, NamedColors.white.value)

    self.check_element_style(list(p_list[3])[0], StyleProperties.FontStyle, FontStyleType.italic)
    self.check_element_style(list(p_list[3])[2], StyleProperties.Color, NamedColors.red.value)
    self.check_element_style(list(p_list[3])[4], StyleProperties.FontStyle, FontStyleType.italic)

    for p in p_list:
      for span in [elem for elem in list(p) if isinstance(elem, Span)]:
        self.check_element_style(span, StyleProperties.BackgroundColor, NamedColors.black.value)

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
    self.check_region_origin(region_1, 4, 14, doc.get_cell_resolution())
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

    self.check_caption(p_list[0], "caption1", "00:00:04:06", None, "Lorem ipsum ", Br, "dolor sit amet,", Br,
                       "consectetur adipiscing elit.")
    self.assertEqual(region_1, p_list[0].get_region())

  def test_scc_pop_on_content_without_preamble_address_code(self):
    scc_content = """\
Scenarist_SCC V1.0

00:00:02:16	942c

00:00:03:01	9420 91ae 9421 4c6f 7265 6d20 6970 7375 6d20 9220 942c 942f

00:00:07:29	9420 94D0 646f 6c6f 7220 7369 7420 616d 6574 2c80 9470 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e 942c 942f

00:00:09:07	9420 d0e5 ecec e56e f4e5 73f1 75e5 20e9 6ef4 e5f2 6475 6d20 ec61 e375 73ae 942c 942f

00:00:11:27	9420
"""

    scc_disassembly = """\
00:00:02:16	{EDM}
00:00:03:01	{RCL}{I}{BS}Lorem ipsum Á{EDM}{EOC}
00:00:07:29	{RCL}{1400}dolor sit amet,{1500}consectetur adipiscing elit.{EDM}{EOC}
00:00:09:07	{RCL}Pellentesque interdum lacus.{EDM}{EOC}
00:00:11:27	{RCL}
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    # without a PAC, the text is written at the cursor, which starts on row 15
    region_1 = doc.get_region("pop1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 4, 16, doc.get_cell_resolution())
    self.check_region_extent(region_1, 12, 1, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_2 = doc.get_region("pop2")
    self.check_region_origin(region_2, 4, 15, doc.get_cell_resolution())
    self.check_region_extent(region_2, 28, 2, doc.get_cell_resolution())

    region_3 = doc.get_region("pop3")
    self.check_region_origin(region_3, 32, 16, doc.get_cell_resolution())
    self.check_region_extent(region_3, 4, 1, doc.get_cell_resolution())

    body = doc.get_body()
    self.assertIsNotNone(body)

    div_list = list(body)
    self.assertEqual(1, len(div_list))
    div = div_list[0]
    self.assertIsNotNone(div)

    p_list = list(div)
    self.assertEqual(3, len(p_list))

    # the mid-row code writes a space that BS erases, and the extended character replaces the last space
    self.check_caption(p_list[0], "caption1", "00:00:03:12", "00:00:08:24", "Lorem ipsumÁ")
    self.assertEqual(region_1, p_list[0].get_region())

    self.check_caption(p_list[1], "caption2", "00:00:08:25", "00:00:09:22", "dolor sit amet,", Br,
                       "consectetur adipiscing elit.")
    self.assertEqual(region_2, p_list[1].get_region())

    # without a PAC, the text continues at the cursor, on row 15 after "consectetur adipiscing elit.", and the
    # characters past column 32 overwrite the last column
    self.check_caption(p_list[2], "caption3", "00:00:09:23", None, "Pel.")
    self.assertEqual(region_3, p_list[2].get_region())

  def test_scc_double_word_in_content(self):
    scc_content = """"Scenarist_SCC V1.0
01:02:53:14	9420 9420 94AE 94AE 9452 9452 97A1 97A1 20F2 E56D E56D 62E5 F220 9137 9137 9137 9137 942F 942F
01:02:55:14 942c 942c
"""
    scc_disassembly = """\
01:02:53:14	{RCL}{RCL}{ENM}{ENM}{1404}{1404}{TO1}{TO1} remember ♪♪♪♪{EOC}{EOC}
"""
    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)
    body = doc.get_body()
    self.assertIsNotNone(body)

    div_list = list(body)
    self.assertEqual(1, len(div_list))
    div = div_list[0]
    self.assertIsNotNone(div)

    p_list = list(div)
    self.assertEqual(1, len(p_list))

    first_span = p_list[0][0]
    first_text = first_span[0].get_text()

    self.assertEqual(" remember ♪♪", first_text)

  def test_2_rows_roll_up_content(self):
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:22	9425 9425 94ad 94ad 9470 9470 4c6f 7265 6d20 6970 7375 6d20 646f 6c6f 7220 7369 7420 616d 6574 2c80

00:00:02:23	9425 9425 94ad 94ad 9673 9673 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e

00:00:04:17	9425 9425 94ad 94ad 9473 9473 d0e5 ecec e56e f4e5 73f1 75e5 20e9 6ef4 e5f2 6475 6d20 ec61 e375 73ae

00:00:06:04	9425 9425 94ad 94ad 9470 9470 496e f4e5 67e5 f220 ec75 e3f4 7573 20e5 f420 ece9 6775 ec61 ae80

"""

    scc_disassembly = """\
00:00:00:22	{RU2}{RU2}{CR}{CR}{1500}{1500}Lorem ipsum dolor sit amet,
00:00:02:23	{RU2}{RU2}{CR}{CR}{0804}{0804}consectetur adipiscing elit.
00:00:04:17	{RU2}{RU2}{CR}{CR}{1504}{1504}Pellentesque interdum lacus.
00:00:06:04	{RU2}{RU2}{CR}{CR}{1500}{1500}Integer luctus et ligula.
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)

    self.check_region_origin(doc.get_region("rollup1"), 4, 2, doc.get_cell_resolution())
    self.check_region_extent(doc.get_region("rollup1"), 28, 15, doc.get_cell_resolution())
    self.check_element_style(doc.get_region("rollup1"), StyleProperties.DisplayAlign, DisplayAlignType.after)
    self.check_element_style(doc.get_region("rollup1"), StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    # captions whose rows all start at column 4 are in another region
    self.check_region_origin(doc.get_region("rollup2"), 8, 2, doc.get_cell_resolution())
    self.check_region_extent(doc.get_region("rollup2"), 28, 15, doc.get_cell_resolution())

    # a caption ends at each CR
    self.check_captions(doc, [
      ('caption1', '00:00:00:28', '00:00:02:25', ['Lorem ipsum dolor sit amet,'], 'rollup1'),
      ('caption2', '00:00:02:25', '00:00:04:19', ['Lorem ipsum dolor sit amet,', 'consectetur adipiscing elit.'], 'rollup1'),
      ('caption3', '00:00:04:19', '00:00:06:06', ['consectetur adipiscing elit.', 'Pellentesque interdum lacus.'], 'rollup2'),
      ('caption4', '00:00:06:06', None, ['Pellentesque interdum lacus.', 'Integer luctus et ligula.'], 'rollup1'),
    ])

    p_list = list(list(doc.get_body())[0])

    # the words of the base row appear when they are received
    self.assertEqual(["Lorem ", "ipsum ", "dolor ", "sit ", "amet,"], [list(span)[0].get_text() for span in p_list[0]])
    self.assertIsNone(list(p_list[0])[0].get_begin())
    self.assertEqual([3, 6, 9, 11], [round(span.get_begin() * 30000 / 1001) for span in list(p_list[0])[1:]])

    # PACs 0804 and 1504 underline the text
    for span in [child for child in p_list[2] if isinstance(child, Span)]:
      self.check_element_style(span, StyleProperties.TextDecoration, TextDecorationType(underline=True))

    for p in p_list:
      for span in [elem for elem in list(p) if isinstance(elem, Span)]:
        self.check_element_style(span, StyleProperties.BackgroundColor, NamedColors.black.value)

  def test_3_rows_roll_up_content(self):
    scc_content = """\
Scenarist_SCC V1.0

00:00:17;01	9426 9426 94ad 94ad 9470 9470 4c6f 7265 6d20 6970 7375 6d20 646f 6c6f 7220 7369 7420 616d 6574 2c80

00:00:18;19	9426 9426 94ad 94ad 9470 9470 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e

00:00:20;06	9426 9426 94ad 94ad 9470 9470 d0e5 ecec e56e f4e5 73f1 75e5 20e9 6ef4 e5f2 6475 6d20 ec61 e375 73ae

00:00:21;24	9426 9426 94ad 94ad 9470 9470 496e f4e5 67e5 f220 ec75 e3f4 7573 20e5 f420 ece9 6775 ec61 ae80
"""

    scc_disassembly = """\
00:00:17;01	{RU3}{RU3}{CR}{CR}{1500}{1500}Lorem ipsum dolor sit amet,
00:00:18;19	{RU3}{RU3}{CR}{CR}{1500}{1500}consectetur adipiscing elit.
00:00:20;06	{RU3}{RU3}{CR}{CR}{1500}{1500}Pellentesque interdum lacus.
00:00:21;24	{RU3}{RU3}{CR}{CR}{1500}{1500}Integer luctus et ligula.
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)

    region_1 = doc.get_region("rollup1")
    self.check_region_origin(region_1, 4, 2, doc.get_cell_resolution())
    self.check_region_extent(region_1, 28, 15, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.after)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    # a caption ends at each CR
    self.check_captions(doc, [
      ('caption1', '00:00:17:07', '00:00:18:21', ['Lorem ipsum dolor sit amet,'], 'rollup1'),
      ('caption2', '00:00:18:21', '00:00:20:08', ['Lorem ipsum dolor sit amet,', 'consectetur adipiscing elit.'], 'rollup1'),
      ('caption3', '00:00:20:08', '00:00:21:26', ['Lorem ipsum dolor sit amet,', 'consectetur adipiscing elit.', 'Pellentesque interdum lacus.'], 'rollup1'),
      ('caption4', '00:00:21:26', None, ['consectetur adipiscing elit.', 'Pellentesque interdum lacus.', 'Integer luctus et ligula.'], 'rollup1'),
    ])

    p_list = list(list(doc.get_body())[0])

    for p in p_list:
      for span in [elem for elem in list(p) if isinstance(elem, Span)]:
        self.check_element_style(span, StyleProperties.BackgroundColor, NamedColors.black.value)

  def test_4_rows_roll_up_content(self):
    scc_content = """\
Scenarist_SCC V1.0

00:00:34;27	94a7 94ad 9470 4c6f 7265 6d20 6970 7375 6d20 646f 6c6f 7220 7369 7420 616d 6574 2c80

00:00:36;12	94a7 94ad 9470 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e

00:00:44;08	94a7 94ad 9470 d0e5 ecec e56e f4e5 73f1 75e5 20e9 6ef4 e5f2 6475 6d20 ec61 e375 73ae

00:00:47;12	94a7 94ad 9470 496e f4e5 67e5 f220 ec75 e3f4 7573 20e5 f420 ece9 6775 ec61 ae80

00:00:49;03	94a7 94ad 9470 d5f4 2061 f420 64e9 616d 2073 e9f4 2061 6de5 f420 6e75 ecec 61ae

00:00:50;23	94a7 94ad 9470 7665 7374 6962 756c 756d 206e 6563 2076 6974 6165 206e 6973 692e
"""

    scc_disassembly = """\
00:00:34;27	{RU4}{CR}{1500}Lorem ipsum dolor sit amet,
00:00:36;12	{RU4}{CR}{1500}consectetur adipiscing elit.
00:00:44;08	{RU4}{CR}{1500}Pellentesque interdum lacus.
00:00:47;12	{RU4}{CR}{1500}Integer luctus et ligula.
00:00:49;03	{RU4}{CR}{1500}Ut at diam sit amet nulla.
00:00:50;23	{RU4}{CR}{1500}vestibulum nec vitae nisi.
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)

    region_1 = doc.get_region("rollup1")
    self.check_region_origin(region_1, 4, 2, doc.get_cell_resolution())
    self.check_region_extent(region_1, 28, 15, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.after)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    # a caption ends at each CR
    self.check_captions(doc, [
      ('caption1', '00:00:35:00', '00:00:36:13', ['Lorem ipsum dolor sit amet,'], 'rollup1'),
      ('caption2', '00:00:36:13', '00:00:44:09', ['Lorem ipsum dolor sit amet,', 'consectetur adipiscing elit.'], 'rollup1'),
      ('caption3', '00:00:44:09', '00:00:47:13', ['Lorem ipsum dolor sit amet,', 'consectetur adipiscing elit.', 'Pellentesque interdum lacus.'], 'rollup1'),
      ('caption4', '00:00:47:13', '00:00:49:04', ['Lorem ipsum dolor sit amet,', 'consectetur adipiscing elit.', 'Pellentesque interdum lacus.', 'Integer luctus et ligula.'], 'rollup1'),
      ('caption5', '00:00:49:04', '00:00:50:24', ['consectetur adipiscing elit.', 'Pellentesque interdum lacus.', 'Integer luctus et ligula.', 'Ut at diam sit amet nulla.'], 'rollup1'),
      ('caption6', '00:00:50:24', None, ['Pellentesque interdum lacus.', 'Integer luctus et ligula.', 'Ut at diam sit amet nulla.', 'vestibulum nec vitae nisi.'], 'rollup1'),
    ])

    p_list = list(list(doc.get_body())[0])

    for p in p_list:
      for span in [elem for elem in list(p) if isinstance(elem, Span)]:
        self.check_element_style(span, StyleProperties.BackgroundColor, NamedColors.black.value)

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

00:00:13;07	9425 9425 94ad 94ad 9470 9470 c1c2 43c4 4580 91bf

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

    region_1 = doc.get_region("rollup1")
    self.check_region_origin(region_1, 4, 2, doc.get_cell_resolution())
    self.check_region_extent(region_1, 32, 15, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.after)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    # characters appear as they are received, and a caption ends at each CR. When the number of rows increases,
    # the rows that are still in memory above the window are displayed again. Special and extended characters
    # are sent twice, and an extended character replaces the preceding character.
    self.check_captions(doc, [
      ('caption1', '00:00:00:28', '00:00:02:25', ['>>> HI.'], 'rollup1'),
      ('caption2', '00:00:02:25', '00:00:04:19', ['>>> HI.', "I'M KEVIN CUNNING AND AT"], 'rollup1'),
      ('caption3', '00:00:04:19', '00:00:06:06', ["I'M KEVIN CUNNING AND AT", "INVESTOR'S BANK WE BELIEVE IN"], 'rollup1'),
      ('caption4', '00:00:06:06', '00:00:09:23', ["INVESTOR'S BANK WE BELIEVE IN", 'HELPING THE LOCAL NEIGHBORHOODS'], 'rollup1'),
      ('caption5', '00:00:09:23', '00:00:11:09', ['HELPING THE LOCAL NEIGHBORHOODS', 'AND  IMPROVING  THE LIVES OF ALL'], 'rollup1'),
      ('caption6', '00:00:11:09', '00:00:12:09', ['AND  IMPROVING  THE LIVES OF ALL', 'WE SERVE.'], 'rollup1'),
      ('caption7', '00:00:12:09', '00:00:13:09', ['WE SERVE.', '®°½'], 'rollup1'),
      ('caption8', '00:00:13:09', '00:00:14:09', ['®°½', 'ABCDEû'], 'rollup1'),
      ('caption9', '00:00:14:09', '00:00:17:03', ['ABCDEû', 'ÁÉÓ¡'], 'rollup1'),
      ('caption10', '00:00:17:03', '00:00:18:21', ['ABCDEû', 'ÁÉÓ¡', "WHERE YOU'RE STANDING NOW,"], 'rollup1'),
      ('caption11', '00:00:18:21', '00:00:20:08', ['ÁÉÓ¡', "WHERE YOU'RE STANDING NOW,", "LOOKING OUT THERE, THAT'S ALL"], 'rollup1'),
      ('caption12', '00:00:20:08', '00:00:21:26', ["WHERE YOU'RE STANDING NOW,", "LOOKING OUT THERE, THAT'S ALL", 'THE CROWD.'], 'rollup1'),
      ('caption13', '00:00:21:26', '00:00:34:28', ["LOOKING OUT THERE, THAT'S ALL", 'THE CROWD.', '>> IT WAS GOOD TO BE IN THE'], 'rollup1'),
      ('caption14', '00:00:34:28', '00:00:36:13', ["LOOKING OUT THERE, THAT'S ALL", 'THE CROWD.', '>> IT WAS GOOD TO BE IN THE', "And restore Iowa's land, water"], 'rollup1'),
      ('caption15', '00:00:36:13', '00:00:44:09', ['THE CROWD.', '>> IT WAS GOOD TO BE IN THE', "And restore Iowa's land, water", 'And wildlife.'], 'rollup1'),
      ('caption16', '00:00:44:09', None, ['>> IT WAS GOOD TO BE IN THE', "And restore Iowa's land, water", 'And wildlife.', '>> Bike Iowa, your source for'], 'rollup1'),
    ])

    p_list = list(list(doc.get_body())[0])

    def spans(p: P, text: str) -> List[Span]:
      return [child for child in p if isinstance(child, Span) and list(child)[0].get_text() == text]

    # the {I} mid-row code italicizes "IMPROVING", until the {Wh} mid-row code
    self.check_element_style(spans(p_list[4], "IMPROVING ")[0], StyleProperties.FontStyle, FontStyleType.italic)
    self.check_element_style(spans(p_list[4], "THE ")[0], StyleProperties.FontStyle, None)
    self.check_element_style(spans(p_list[5], " IMPROVING ")[0], StyleProperties.FontStyle, FontStyleType.italic)

    # the {BMaS} attribute code sets a semi-transparent magenta background, until the {BBk} attribute code
    semi_transparent_magenta = ColorType((255, 0, 255, 136))
    for p in p_list[12:16]:
      self.check_element_style(spans(p, "GOOD")[0], StyleProperties.BackgroundColor, semi_transparent_magenta)
      self.check_element_style(spans(p, " TO BE IN THE" if p is not p_list[12] else " TO ")[0],
                               StyleProperties.BackgroundColor, NamedColors.black.value)

  def test_scc_roll_up_content_without_preamble_address_code(self):
    scc_content = """\
Scenarist_SCC V1.0

00:00:34:27	9425 94ad 4c6f 7265 6d20 6970 7375 6d20 646f 6c6f 7220 7369 7420 616d 6574 2c80

00:00:36:12	9425 94ad 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e

00:00:44:08	9425 94ad d0e5 ecec e56e f4e5 73f1 75e5 20e9 6ef4 e5f2 6475 6d20 ec61 e375 73ae

"""

    scc_disassembly = """\
00:00:34:27	{RU2}{CR}Lorem ipsum dolor sit amet,
00:00:36:12	{RU2}{CR}consectetur adipiscing elit.
00:00:44:08	{RU2}{CR}Pellentesque interdum lacus.
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)

    region_1 = doc.get_region("rollup1")
    self.check_region_origin(region_1, 4, 2, doc.get_cell_resolution())
    self.check_region_extent(region_1, 28, 15, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.after)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    # a caption ends at each CR
    self.check_captions(doc, [
      ('caption1', '00:00:34:29', '00:00:36:13', ['Lorem ipsum dolor sit amet,'], 'rollup1'),
      ('caption2', '00:00:36:13', '00:00:44:09', ['Lorem ipsum dolor sit amet,', 'consectetur adipiscing elit.'], 'rollup1'),
      ('caption3', '00:00:44:09', None, ['consectetur adipiscing elit.', 'Pellentesque interdum lacus.'], 'rollup1'),
    ])

    p_list = list(list(doc.get_body())[0])

    for p in p_list:
      for span in [elem for elem in list(p) if isinstance(elem, Span)]:
        self.check_element_style(span, StyleProperties.BackgroundColor, NamedColors.black.value)

  def test_scc_paint_on_content(self):
    scc_content = """\
Scenarist_SCC V1.0

00:02:53:14	9429 9429 94d2 94d2 4c6f 7265 6d20 6970 7375 6d20 646f 6c6f 7220 7369 7420 616d 6574 2c80 94f2 94f2 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e

00:02:56:00	9429 9429 94d2 94d2 d0e5 ecec e56e f4e5 73f1 75e5 20e9 6ef4 e5f2 6475 6d20 ec61 e375 73ae

00:02:56:25	9429 9429 94f2 94f2 496e f4e5 67e5 f220 ec75 e3f4 7573 20e5 f420 ece9 6775 ec61 ae80

"""

    scc_disassembly = """\
00:02:53:14	{RDC}{RDC}{1404}{1404}Lorem ipsum dolor sit amet,{1504}{1504}consectetur adipiscing elit.
00:02:56:00	{RDC}{RDC}{1404}{1404}Pellentesque interdum lacus.
00:02:56:25	{RDC}{RDC}{1504}{1504}Integer luctus et ligula.
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    region_1 = doc.get_region("paint1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 8, 15, doc.get_cell_resolution())
    self.check_region_extent(region_1, 28, 2, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    # characters appear as they are received. A PAC only moves the cursor: the following characters overwrite the
    # displayed ones one by one, and each overwrite ends the caption.
    self.check_captions(doc, [
      ('caption1', '00:02:53:18', '00:02:56:04', ['Lorem ipsum dolor sit amet,', 'consectetur adipiscing elit.'], 'paint1'),
      ('caption2', '00:02:56:04', '00:02:56:05', ['Perem ipsum dolor sit amet,', 'consectetur adipiscing elit.'], 'paint1'),
      ('caption3', '00:02:56:05', '00:02:56:06', ['Pellm ipsum dolor sit amet,', 'consectetur adipiscing elit.'], 'paint1'),
      ('caption4', '00:02:56:06', '00:02:56:07', ['Pellenipsum dolor sit amet,', 'consectetur adipiscing elit.'], 'paint1'),
      ('caption5', '00:02:56:07', '00:02:56:08', ['Pellentesum dolor sit amet,', 'consectetur adipiscing elit.'], 'paint1'),
      ('caption6', '00:02:56:08', '00:02:56:09', ['Pellentesqm dolor sit amet,', 'consectetur adipiscing elit.'], 'paint1'),
      ('caption7', '00:02:56:09', '00:02:56:10', ['Pellentesquedolor sit amet,', 'consectetur adipiscing elit.'], 'paint1'),
      ('caption8', '00:02:56:10', '00:02:56:11', ['Pellentesque ilor sit amet,', 'consectetur adipiscing elit.'], 'paint1'),
      ('caption9', '00:02:56:11', '00:02:56:12', ['Pellentesque intr sit amet,', 'consectetur adipiscing elit.'], 'paint1'),
      ('caption10', '00:02:56:12', '00:02:56:13', ['Pellentesque intersit amet,', 'consectetur adipiscing elit.'], 'paint1'),
      ('caption11', '00:02:56:13', '00:02:56:14', ['Pellentesque interdut amet,', 'consectetur adipiscing elit.'], 'paint1'),
      ('caption12', '00:02:56:14', '00:02:56:15', ['Pellentesque interdum amet,', 'consectetur adipiscing elit.'], 'paint1'),
      ('caption13', '00:02:56:15', '00:02:56:16', ['Pellentesque interdum laet,', 'consectetur adipiscing elit.'], 'paint1'),
      ('caption14', '00:02:56:16', '00:02:56:17', ['Pellentesque interdum lacu,', 'consectetur adipiscing elit.'], 'paint1'),
      ('caption15', '00:02:56:17', '00:02:56:29', ['Pellentesque interdum lacus.', 'consectetur adipiscing elit.'], 'paint1'),
      ('caption16', '00:02:56:29', '00:02:57:00', ['Pellentesque interdum lacus.', 'Innsectetur adipiscing elit.'], 'paint1'),
      ('caption17', '00:02:57:00', '00:02:57:01', ['Pellentesque interdum lacus.', 'Inteectetur adipiscing elit.'], 'paint1'),
      ('caption18', '00:02:57:01', '00:02:57:02', ['Pellentesque interdum lacus.', 'Integetetur adipiscing elit.'], 'paint1'),
      ('caption19', '00:02:57:02', '00:02:57:03', ['Pellentesque interdum lacus.', 'Integer tur adipiscing elit.'], 'paint1'),
      ('caption20', '00:02:57:03', '00:02:57:04', ['Pellentesque interdum lacus.', 'Integer lur adipiscing elit.'], 'paint1'),
      ('caption21', '00:02:57:04', '00:02:57:05', ['Pellentesque interdum lacus.', 'Integer luctadipiscing elit.'], 'paint1'),
      ('caption22', '00:02:57:05', '00:02:57:06', ['Pellentesque interdum lacus.', 'Integer luctusipiscing elit.'], 'paint1'),
      ('caption23', '00:02:57:06', '00:02:57:07', ['Pellentesque interdum lacus.', 'Integer luctus eiscing elit.'], 'paint1'),
      ('caption24', '00:02:57:07', '00:02:57:08', ['Pellentesque interdum lacus.', 'Integer luctus et cing elit.'], 'paint1'),
      ('caption25', '00:02:57:08', '00:02:57:09', ['Pellentesque interdum lacus.', 'Integer luctus et ling elit.'], 'paint1'),
      ('caption26', '00:02:57:09', '00:02:57:10', ['Pellentesque interdum lacus.', 'Integer luctus et ligu elit.'], 'paint1'),
      ('caption27', '00:02:57:10', '00:02:57:11', ['Pellentesque interdum lacus.', 'Integer luctus et ligulalit.'], 'paint1'),
      ('caption28', '00:02:57:11', None, ['Pellentesque interdum lacus.', 'Integer luctus et ligula.it.'], 'paint1'),
    ])

    p_list = list(list(doc.get_body())[0])

    # the words of the first caption appear when they are received
    paragraph = p_list[0]
    self.check_caption(paragraph, "caption1", "00:02:53:18", "00:02:56:04", "Lorem ", "ipsum ", "dolor ", "sit ", "amet,",
                       Br, "consectetur ", "adipiscing ", "elit.")
    spans = [child for child in paragraph if isinstance(child, Span)]
    self.assertIsNone(spans[0].get_begin())
    self.assertEqual([3, 6, 9, 11, 16, 22, 27], [round(span.get_begin() * 30000 / 1001) for span in spans[1:]])

    # the content that is displayed when a caption begins appears with it
    for span in [child for child in p_list[1] if isinstance(child, Span)]:
      self.assertIsNone(span.get_begin())

    for p in p_list:
      for span in [elem for elem in list(p) if isinstance(elem, Span)]:
        self.check_element_style(span, StyleProperties.BackgroundColor, NamedColors.black.value)

  def test_scc_paint_on_content_without_preamble_address_codes(self):
    scc_content = """\
Scenarist_SCC V1.0

00:02:53:14	9429 4cef f2e5 6d20 e970 7375 6d20

00:02:56:00	9429 64ef ecef f220 73e9 f420 616d e5f4 2c80

00:02:56:25	9429 e5ec e9f4 ae80 95d0 ec61 e3e9 6ee9 6120 73ef ecec e9e3 e9f4 7564 e96e ae80

"""

    scc_disassembly = """\
00:02:53:14	{RDC}Lorem ipsum 
00:02:56:00	{RDC}dolor sit amet,
00:02:56:25	{RDC}elit.{0500}lacinia sollicitudin.
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    # without a PAC, the text is written at the cursor, which starts on row 15, and continues on the same row
    # until the last PAC moves the cursor to row 5
    region_1 = doc.get_region("paint1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 4, 6, doc.get_cell_resolution())
    self.check_region_extent(region_1, 32, 11, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    # no character is overwritten: the caption does not end
    self.check_captions(doc, [
      ('caption1', '00:02:53:15', None,
       ['lacinia sollicitudin.', '', '', '', '', '', '', '', '', '', 'Lorem ipsum dolor sit amet,elit.'], 'paint1'),
    ])

    p_list = list(list(doc.get_body())[0])

    # the words appear when they are received
    spans = [child for child in p_list[0] if isinstance(child, Span)]
    self.assertEqual(["lacinia ", "sollicitudin.", "Lorem ", "ipsum ", "dolor ", "sit ", "amet,elit."],
                     [list(span)[0].get_text() for span in spans])
    self.assertEqual([105, 109, None, 3, 76, 79, 81],
                     [None if span.get_begin() is None else round(span.get_begin() * 30000 / 1001) for span in spans])

    for p in p_list:
      for span in [elem for elem in list(p) if isinstance(elem, Span)]:
        self.check_element_style(span, StyleProperties.BackgroundColor, NamedColors.black.value)

  def test_scc_mid_row_erase_displayed_memory_control_code(self):
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9420 9150 4c6f 7265 6d20 6970 7375 6d20 646f 6c6f 7220 7369 7420 616d 6574 2c80 942c 8080 8080 942f

00:00:01:14	9426 942c 94ad 9050 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e

00:00:02:00	9426 94ad 942c 9350 d0e5 ecec e56e f4e5 73f1 75e5 20e9 6ef4 e5f2 6475 6d20 ec61 e375 73ae

00:00:03:00	9429 942c 9370 496e 7465 6765 7220 6c75 6374 7573 2065 7420 942c 7361 6769 7474 6973 2e80

"""

    scc_disassembly = """\
00:00:00:00	{RCL}{0100}Lorem ipsum dolor sit amet,{EDM}{}{}{EOC}
00:00:01:14	{RU3}{EDM}{CR}{1100}consectetur adipiscing elit.
00:00:02:00	{RU3}{CR}{EDM}{1200}Pellentesque interdum lacus.
00:00:03:00	{RDC}{EDM}{1300}Integer luctus et {EDM}sagittis.
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    region_1 = doc.get_region("pop1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 4, 2, doc.get_cell_resolution())
    self.check_region_extent(region_1, 27, 15, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_2 = doc.get_region("rollup2")
    self.assertIsNotNone(region_2)
    self.check_region_origin(region_2, 4, 2, doc.get_cell_resolution())
    self.check_region_extent(region_2, 28, 15, doc.get_cell_resolution())
    self.check_element_style(region_2, StyleProperties.DisplayAlign, DisplayAlignType.after)
    self.check_element_style(region_2, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_3 = doc.get_region("paint3")
    self.assertIsNotNone(region_3)
    self.check_region_origin(region_3, 4, 14, doc.get_cell_resolution())
    self.check_region_extent(region_3, 18, 3, doc.get_cell_resolution())
    self.check_element_style(region_3, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_3, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_4 = doc.get_region("paint4")
    self.assertIsNotNone(region_4)
    self.check_region_origin(region_4, 22, 14, doc.get_cell_resolution())
    self.check_region_extent(region_4, 9, 3, doc.get_cell_resolution())
    self.check_element_style(region_4, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_4, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    # Roll-Up text appears as it is received. The CR followed by an EDM displays the rolled-up row for one frame.
    # An EDM does not move the cursor: "sagittis." continues at column 18.
    self.check_captions(doc, [
      ('caption1', '00:00:00:19', '00:00:01:14', ['Lorem ipsum dolor sit amet,'], 'pop1'),
      ('caption2', '00:00:01:18', '00:00:02:01', ['consectetur adipiscing elit.'], 'rollup2'),
      ('caption3', '00:00:02:01', '00:00:02:02', ['consectetur adipiscing elit.'], 'rollup2'),
      ('caption4', '00:00:02:04', '00:00:03:01', ['Pellentesque interdum lacus.'], 'rollup2'),
      ('caption5', '00:00:03:03', '00:00:03:12', ['Integer luctus et '], 'paint3'),
      ('caption6', '00:00:03:13', None, ['sagittis.'], 'paint4'),
    ])

  def test_scc_content_starting_with_text(self):
    scc_content = """\
Scenarist_SCC V1.0

00:00:03:01	6970 7375 6d00 942c 942f

00:00:07:29	9420 94D0 646f 6c6f 7220 7369 7420 616d 6574 2c80 9470 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e 942c 942f

00:00:09:07	942c
"""

    scc_disassembly = """\
00:00:03:01	ipsum{EDM}{EOC}
00:00:07:29	{RCL}{1400}dolor sit amet,{1500}consectetur adipiscing elit.{EDM}{EOC}
00:00:09:07	{EDM}
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    region_1 = doc.get_region("pop1")
    self.assertIsNotNone(region_1)
    # without a PAC, the text is written at the cursor, which starts on row 15
    self.check_region_origin(region_1, 4, 16, doc.get_cell_resolution())
    self.check_region_extent(region_1, 5, 1, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_2 = doc.get_region("pop2")
    self.assertIsNotNone(region_2)
    self.check_region_origin(region_2, 4, 15, doc.get_cell_resolution())
    self.check_region_extent(region_2, 28, 2, doc.get_cell_resolution())
    self.check_element_style(region_2, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_2, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    body = doc.get_body()
    self.assertIsNotNone(body)

    div_list = list(body)
    self.assertEqual(1, len(div_list))
    div = div_list[0]
    self.assertIsNotNone(div)

    p_list = list(div)
    self.assertEqual(2, len(p_list))

    self.check_caption(p_list[0], "caption1", "00:00:03:05", "00:00:08:24", "ipsum")
    self.assertEqual(region_1, p_list[0].get_region())

    self.check_caption(p_list[1], "caption2", "00:00:08:25", "00:00:09:07", "dolor sit amet,", Br,
                       "consectetur adipiscing elit.")
    self.assertEqual(region_2, p_list[1].get_region())

  def test_scc_content_starting_with_mid_row_code(self):
    scc_content = """\
Scenarist_SCC V1.0

00:00:03:01	91ae 6970 7375 6d00 942c 942f

00:00:07:29	9420 94D0 646f 6c6f 7220 7369 7420 616d 6574 2c80 9470 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e 942c 942f

00:00:09:07	942c
"""

    scc_disassembly = """\
00:00:03:01	{I}ipsum{EDM}{EOC}
00:00:07:29	{RCL}{1400}dolor sit amet,{1500}consectetur adipiscing elit.{EDM}{EOC}
00:00:09:07	{EDM}
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    region_1 = doc.get_region("pop1")
    self.assertIsNotNone(region_1)
    # without a PAC, the text is written at the cursor, which starts on row 15
    self.check_region_origin(region_1, 4, 16, doc.get_cell_resolution())
    self.check_region_extent(region_1, 6, 1, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_2 = doc.get_region("pop2")
    self.assertIsNotNone(region_2)
    self.check_region_origin(region_2, 4, 15, doc.get_cell_resolution())
    self.check_region_extent(region_2, 28, 2, doc.get_cell_resolution())
    self.check_element_style(region_2, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_2, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    body = doc.get_body()
    self.assertIsNotNone(body)

    div_list = list(body)
    self.assertEqual(1, len(div_list))
    div = div_list[0]
    self.assertIsNotNone(div)

    p_list = list(div)
    self.assertEqual(2, len(p_list))

    self.check_caption(p_list[0], "caption1", "00:00:03:06", "00:00:08:24", " ipsum")
    self.assertEqual(region_1, p_list[0].get_region())

    self.check_caption(p_list[1], "caption2", "00:00:08:25", "00:00:09:07", "dolor sit amet,", Br,
                       "consectetur adipiscing elit.")
    self.assertEqual(region_2, p_list[1].get_region())

  def test_scc_content_starting_with_control_code(self):
    scc_content = """\
Scenarist_SCC V1.0

00:00:03:01	942c 6970 7375 6d00 942c 942f

00:00:07:29	9420 94D0 646f 6c6f 7220 7369 7420 616d 6574 2c80 9470 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e 942c 942f

00:00:09:07	942c
"""

    scc_disassembly = """\
00:00:03:01	{EDM}ipsum{EDM}{EOC}
00:00:07:29	{RCL}{1400}dolor sit amet,{1500}consectetur adipiscing elit.{EDM}{EOC}
00:00:09:07	{EDM}
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    region_1 = doc.get_region("pop1")
    self.assertIsNotNone(region_1)
    # without a PAC, the text is written at the cursor, which starts on row 15
    self.check_region_origin(region_1, 4, 16, doc.get_cell_resolution())
    self.check_region_extent(region_1, 5, 1, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_2 = doc.get_region("pop2")
    self.assertIsNotNone(region_2)
    self.check_region_origin(region_2, 4, 15, doc.get_cell_resolution())
    self.check_region_extent(region_2, 28, 2, doc.get_cell_resolution())
    self.check_element_style(region_2, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_2, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    body = doc.get_body()
    self.assertIsNotNone(body)

    div_list = list(body)
    self.assertEqual(1, len(div_list))
    div = div_list[0]
    self.assertIsNotNone(div)

    p_list = list(div)
    self.assertEqual(2, len(p_list))

    self.check_caption(p_list[0], "caption1", "00:00:03:06", "00:00:08:24", "ipsum")
    self.assertEqual(region_1, p_list[0].get_region())

    self.check_caption(p_list[1], "caption2", "00:00:08:25", "00:00:09:07", "dolor sit amet,", Br,
                       "consectetur adipiscing elit.")
    self.assertEqual(region_2, p_list[1].get_region())

  def test_scc_content_starting_with_preamble_address_code(self):
    scc_content = """\
Scenarist_SCC V1.0

00:00:03:01	9370 6970 7375 6d00 942c 942f

00:00:07:29	9420 94D0 646f 6c6f 7220 7369 7420 616d 6574 2c80 9470 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e 942c 942f

00:00:09:07	942c
"""

    scc_disassembly = """\
00:00:03:01	{1300}ipsum{EDM}{EOC}
00:00:07:29	{RCL}{1400}dolor sit amet,{1500}consectetur adipiscing elit.{EDM}{EOC}
00:00:09:07	{EDM}
"""

    self.assertEqual(scc_disassembly, to_disassembly(scc_content))

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    region_1 = doc.get_region("pop1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 4, 14, doc.get_cell_resolution())
    self.check_region_extent(region_1, 5, 3, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_2 = doc.get_region("pop2")
    self.assertIsNotNone(region_2)
    self.check_region_origin(region_2, 4, 15, doc.get_cell_resolution())
    self.check_region_extent(region_2, 28, 2, doc.get_cell_resolution())
    self.check_element_style(region_2, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_2, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    body = doc.get_body()
    self.assertIsNotNone(body)

    div_list = list(body)
    self.assertEqual(1, len(div_list))
    div = div_list[0]
    self.assertIsNotNone(div)

    p_list = list(div)
    self.assertEqual(2, len(p_list))

    self.check_caption(p_list[0], "caption1", "00:00:03:06", "00:00:08:24", "ipsum")
    self.assertEqual(region_1, p_list[0].get_region())

    self.check_caption(p_list[1], "caption2", "00:00:08:25", "00:00:09:07", "dolor sit amet,", Br,
                       "consectetur adipiscing elit.")
    self.assertEqual(region_2, p_list[1].get_region())

  def test_scc_with_negative_cursor(self):
    scc_content = """Scenarist_SCC V1.0
00:00:01:00	94AE 94AE 9420 9420 94F8 94F8 45E5 E5E3 68A1 94F4 94F4 D3E3 61F2 79A1 942C 942C 942F 942F
00:00:02:00	942F 942F
"""
    scc_disassembly_expected = """\
00:00:01:00	{ENM}{ENM}{RCL}{RCL}{1516}{1516}Eeech!{1508}{1508}Scary!{EDM}{EDM}{EOC}{EOC}
00:00:02:00	{EOC}{EOC}
"""
    scc_disassembly = to_disassembly(scc_content)
    self.assertEqual(scc_disassembly_expected, scc_disassembly)

    doc = to_model(scc_content)

    self.assertIsNotNone(doc)

    region_1 = doc.get_region("pop1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 12, 16, doc.get_cell_resolution())
    self.check_region_extent(region_1, 14, 1, doc.get_cell_resolution())
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

    # "Scary!" is at column 8 and "Eeech!" at column 16 of the same row: the empty cells between them are a
    # transparent gap
    self.check_caption(p_list[0], "caption1", "00:00:01:16", "00:00:02:00", "Scary!", "  ", "Eeech!")
    self.assertEqual(region_1, p_list[0].get_region())
    self.check_element_style(list(p_list[0])[1], StyleProperties.BackgroundColor, NamedColors.transparent.value)
    self.check_element_style(list(p_list[0])[2], StyleProperties.BackgroundColor, NamedColors.black.value)

  def test_scc_content_starting_with_tab(self):
    scc_content = """Scenarist_SCC V1.0
00:42:41;20	942C 9429 97A2 5BF7
"""
    print(to_disassembly(scc_content))
    self.assertIsNotNone(to_model(scc_content))

  def test_scc_content_starting_with_bs(self):
    scc_content = """Scenarist_SCC V1.0
00:42:41;20	942C 9429 94A1 5BF7
"""
    self.assertIsNotNone(to_model(scc_content))

  def test_scc_content_starting_with_backspace(self):
    scc_content = """Scenarist_SCC V1.0
10:01:44;17	94AE 9420 9470 9723 946E 94A1 92B0 20ec 6120 e6e9 6e20 64e5 7320 616e 6edc e573 2031 38b0 b02c 942C 8080 8080 942F
"""

    expected_scc_disassembly = """\
10:01:44;17	{ENM}{RCL}{1500}{TO3}{15WhI}{BS}À la fin des années 1800,{EDM}{}{}{EOC}
"""

    scc_disassembly = to_disassembly(scc_content)
    self.assertEqual(expected_scc_disassembly, scc_disassembly)

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    region_1 = doc.get_region("pop1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 4, 16, doc.get_cell_resolution())
    self.check_region_extent(region_1, 25, 1, doc.get_cell_resolution())
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

    self.check_caption(p_list[0], "caption1", "10:01:45;09", None, "À la fin des années 1800,")
    self.assertEqual(region_1, p_list[0].get_region())

  def test_scc_content_roll_up_empty_caption(self):
    scc_content = """Scenarist_SCC V1.0
10:03:20:16	94ad 94ad 9426 9426 92d0 92d0 a880 9138 9138 2064 942c 942c e575 f820 76ef e9f8 2c20 e56e 2061 6e67 ec61 e973 29ba
"""
    expected_scc_disassembly = """\
10:03:20:16	{CR}{CR}{RU3}{RU3}{0300}{0300}(àà d{EDM}{EDM}eux voix, en anglais):
"""

    scc_disassembly = to_disassembly(scc_content)
    self.assertEqual(expected_scc_disassembly, scc_disassembly)

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    region_1 = doc.get_region("rollup1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 4, 2, doc.get_cell_resolution())
    self.check_region_extent(region_1, 4, 15, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.after)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    # the EDM does not move the cursor: the text that follows it, without a PAC, continues at column 4
    region_2 = doc.get_region("rollup2")
    self.assertIsNotNone(region_2)
    self.check_region_origin(region_2, 8, 2, doc.get_cell_resolution())
    self.check_region_extent(region_2, 22, 15, doc.get_cell_resolution())

    # the CRs received before RU3, in Pop-On style, are ignored, and the special character à is sent twice
    self.check_captions(doc, [
      ('caption1', '10:03:20:22', '10:03:20:26', ['(à d'], 'rollup1'),
      ('caption2', '10:03:20:28', None, ['eux voix, en anglais):'], 'rollup2'),
    ])

  def test_scc_text_without_style_nor_position(self):
    scc_content = """Scenarist_SCC V1.0
10:55:31:29	2080 3280 2046 3180
"""
    expected_scc_disassembly = """\
10:55:31:29	 2 F1
"""

    scc_disassembly = to_disassembly(scc_content)
    self.assertEqual(expected_scc_disassembly, scc_disassembly)

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    body = doc.get_body()
    self.assertIsNotNone(body)

    div_list = list(body)
    self.assertEqual(1, len(div_list))
    div = div_list[0]
    self.assertIsNotNone(div)
    self.assertEqual(0, len(list(div)))

  def test_scc_content_with_paragraph_of_spaces(self):
    scc_content = """\
Scenarist_SCC V1.0

00:00:03:01	9370 6970 7375 6d00 942c 942f

09:59:59:18	9420 9476 9723 2080 9420 942c 942f 9420 97f4 a8e3 616d e5f2 6120 7368 75f4 f4e5 f229 9452 9723 91ae bce3 6861 eff4 e9e3 20e3 61e3 ef70 68ef 6e79 9470 9723 91ae e5f8 e973 f473 20f4 68f2 ef75 6768 ef75 f420 70f2 ef67 f261 6d3e 9420 942c 942f 9420 94f4 a870 ec61 79e6 75ec 206d 7573 e9e3 2980

11:00:09:07	942c
"""

    expected_disassembly = """\
00:00:03:01	{1300}ipsum{EDM}{EOC}
09:59:59:18	{RCL}{1512}{TO3} {RCL}{EDM}{EOC}{RCL}{1008}(camera shutter){1404}{TO3}{I}<chaotic cacophony{1500}{TO3}{I}exists throughout program>{RCL}{EDM}{EOC}{RCL}{1508}(playful music)
11:00:09:07	{EDM}
"""

    disassembly = to_disassembly(scc_content)
    self.assertEqual(expected_disassembly, disassembly)

    doc = to_model(scc_content)

    self.assertIsNotNone(doc)

    region_1 = doc.get_region("pop1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 4, 14, doc.get_cell_resolution())
    self.check_region_extent(region_1, 5, 3, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_2 = doc.get_region("pop2")
    self.assertIsNotNone(region_2)
    self.check_region_origin(region_2, 19, 16, doc.get_cell_resolution())
    self.check_region_extent(region_2, 1, 1, doc.get_cell_resolution())
    self.check_element_style(region_2, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_2, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_3 = doc.get_region("pop3")
    self.assertIsNotNone(region_3)
    self.check_region_origin(region_3, 7, 11, doc.get_cell_resolution())
    self.check_region_extent(region_3, 27, 6, doc.get_cell_resolution())
    self.check_element_style(region_3, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_3, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    body = doc.get_body()
    self.assertIsNotNone(body)

    div_list = list(body)
    self.assertEqual(1, len(div_list))
    div = div_list[0]
    self.assertIsNotNone(div)

    p_list = list(div)
    self.assertEqual(3, len(p_list))

    self.check_caption(p_list[0], "caption1", "00:00:03:06", "09:59:59:23", "ipsum")
    self.assertEqual(region_1, p_list[0].get_region())

    self.check_caption(p_list[1], "caption2", "09:59:59:24", "10:00:01:04", " ")
    self.assertEqual(region_2, p_list[1].get_region())

    self.check_caption(p_list[2], "caption3", "10:00:01:05", "11:00:09:07", "(camera shutter)", Br, Br, Br, Br,
                       " <chaotic cacophony", Br, " exists throughout program>")
    self.assertEqual(region_3, p_list[2].get_region())

  def test_scc_content_trying_to_roll_up_pop_on_paragraph(self):
    scc_content = """\
Scenarist_SCC V1.0

11:19:24:05	9420 946E A861 7070 EC61 7564 E973 73E5 6DE5 6EF4 7329 9420 942C 942F

11:19:30:17	9426 94AD 946E 3E3E 3E20 CE61 F2F2 61F4 E575 F2BA 2043 E5F4 F4E5
"""
    expected_disassembly = """\
11:19:24:05	{RCL}{15WhI}(applaudissements){RCL}{EDM}{EOC}
11:19:30:17	{RU3}{CR}{15WhI}>>> Narrateur: Cette
"""

    disassembly = to_disassembly(scc_content)
    self.assertEqual(expected_disassembly, disassembly)

    doc = to_model(scc_content)

    self.assertIsNotNone(doc)

    region_1 = doc.get_region("pop1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 4, 16, doc.get_cell_resolution())
    self.check_region_extent(region_1, 18, 1, doc.get_cell_resolution())
    self.check_element_style(region_1, StyleProperties.DisplayAlign, DisplayAlignType.before)
    self.check_element_style(region_1, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    region_2 = doc.get_region("rollup2")
    self.assertIsNotNone(region_2)
    self.check_region_origin(region_2, 4, 2, doc.get_cell_resolution())
    self.check_region_extent(region_2, 20, 15, doc.get_cell_resolution())
    self.check_element_style(region_2, StyleProperties.DisplayAlign, DisplayAlignType.after)
    self.check_element_style(region_2, StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    body = doc.get_body()
    self.assertIsNotNone(body)

    div_list = list(body)
    self.assertEqual(1, len(div_list))
    div = div_list[0]
    self.assertIsNotNone(div)

    p_list = list(div)
    self.assertEqual(2, len(p_list))

    self.check_caption(p_list[0], "caption1", "11:19:24:18", "11:19:30:17", "(applaudissements)")
    self.assertEqual(region_1, p_list[0].get_region())

    # the Roll-Up caption begins when its first character is received
    self.check_caption(p_list[1], "caption2", "11:19:30:20", None, ">>> ", "Narrateur: ", "Cette")
    self.assertEqual(region_2, p_list[1].get_region())

  def test_skipping_channel_2_content(self):
    scc_content = """\
01:03:27:29	1c20 1cd0 a843 4332 2920 1c2c 94ae 94ae 9420 9420 94f2 94f2 c845 d92c 2054 c845 5245 ae80 942c 942c 8080 8080 942f 942f
"""
    expected_disassembly = """\
01:03:27:29	{CC2|RCL}{CC2|1400}(CC2) {CC2|EDM}{CC1|ENM}{CC1|ENM}{CC1|RCL}{CC1|RCL}{CC1|1504}{CC1|1504}HEY, THERE.{CC1|EDM}{CC1|EDM}{}{}{CC1|EOC}{CC1|EOC}
"""

    disassembly = to_disassembly(scc_content, show_channels=True)
    self.assertEqual(expected_disassembly, disassembly)

    doc = to_model(scc_content)

    self.assertIsNotNone(doc)

    region_1 = doc.get_region("pop1")
    self.assertIsNotNone(region_1)
    self.check_region_origin(region_1, 8, 16, doc.get_cell_resolution())
    self.check_region_extent(region_1, 11, 1, doc.get_cell_resolution())
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

    self.check_caption(p_list[0], "caption1", "01:03:28:21", None, "HEY, THERE.")
    self.assertEqual(region_1, p_list[0].get_region())

  def test_scc_fg_black_attribute_preserves_bg(self):
    # a background attribute code followed by a foreground attribute code: the text is black on white
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9420 9420 94ae 94ae 1540 1540 2080 1020 1020 2080 97ae 97ae c2ec 61e3 6b20 f4e5 f8f4 942f 942f
"""

    doc = to_model(scc_content)

    p_list = list(list(doc.get_body())[0])
    self.assertEqual(1, len(p_list))
    spans = [child for child in p_list[0] if isinstance(child, Span)]
    text_span = spans[-1]
    self.assertEqual("Black text", list(text_span)[0].get_text())
    self.assertEqual(NamedColors.black.value, text_span.get_style(StyleProperties.Color))
    self.assertEqual(NamedColors.white.value, text_span.get_style(StyleProperties.BackgroundColor))

  def test_scc_bg_attribute_persists_across_mid_row_code(self):
    # a background attribute code remains in effect after a mid-row code on the same row
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9420 9420 94ae 94ae 1540 1540 1020 1020 2080 c162 91a8 91a8 e364 942f 942f
"""

    doc = to_model(scc_content)

    p_list = list(list(doc.get_body())[0])
    self.assertEqual(1, len(p_list))
    spans = [child for child in p_list[0] if isinstance(child, Span)]
    self.assertEqual(2, len(spans))

    self.assertEqual(" Ab", list(spans[0])[0].get_text())
    self.assertEqual(NamedColors.white.value, spans[0].get_style(StyleProperties.Color))
    self.assertEqual(NamedColors.white.value, spans[0].get_style(StyleProperties.BackgroundColor))

    self.assertEqual(" cd", list(spans[1])[0].get_text())
    self.assertEqual(NamedColors.red.value, spans[1].get_style(StyleProperties.Color))
    self.assertEqual(NamedColors.white.value, spans[1].get_style(StyleProperties.BackgroundColor))

  def test_scc_roll_up_blank_row_rolls_up_the_rows_above(self):
    # CTA-608-E D.2: of three consecutive CR, the second is redundant, so two rows roll up and one
    # blank row is left between A and B
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	942c 942c 94a7 94a7 94ad 94ad 94e0 94e0 c180

00:00:01:15	94ad 94ad 94ad 94e0 94e0 c280
"""

    doc = to_model(scc_content)

    last = list(list(doc.get_body())[0])[-1]
    content = ["/" if isinstance(child, Br) else list(child)[0].get_text() for child in last]
    self.assertEqual(["A", "/", "/", "B"], content)

  def test_scc_pop_on_repeated_eoc_unique_ids(self):
    # swapping memories back and forth with EOC re-displays captions: each one must get a new id
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9420 9420 9470 9470 c162 942f 942f

00:00:01:00	9420 9420 9470 9470 e364 942f 942f

00:00:02:00	942f 942f

00:00:03:00	942f 942f

00:00:04:00	942c 942c
"""

    doc = to_model(scc_content)

    p_list = list(list(doc.get_body())[0])
    self.assertEqual(4, len(p_list))
    self.assertEqual(["caption1", "caption2", "caption3", "caption4"], [p.get_id() for p in p_list])
    self.assertEqual(["Ab", "cd", "Ab", "cd"], [list(list(p)[0])[0].get_text() for p in p_list])

  def test_scc_roll_up_erases_the_non_displayed_memory(self):
    # CTA-608-E C.10: Roll-Up erases Pop-On data in both memories
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9420 9420 94ae 94ae 13e0 13e0 d0ef 70ad ef6e 20c1 ba20 e5f2 6173 e564 2062 7920 52d5 3280 942f 942f

00:00:01:00	9420 9420 94ae 94ae 1340 1340 c8e9 6464 e56e 20c2 ba20 6d75 73f4 206e e576 e5f2 2073 68ef f780

00:00:04:00	9425 9425 94ad 94ad 94e0 94e0 52ef ecec ad75 70ba 20c1 2061 6e64 20c2 20e5 f261 73e5 6480

00:00:08:00	942f 942f

00:00:11:00	942f 942f
"""

    doc = to_model(scc_content)

    texts = ["".join(list(span)[0].get_text() for span in p if isinstance(span, Span)) for p in list(list(doc.get_body())[0])]
    self.assertFalse([text for text in texts if "Hidden B" in text], texts)
    self.assertEqual(["Pop-on A: erased by RU2", "Roll-up: A and B erased", "Roll-up: A and B erased"], texts)

  def test_scc_repeated_backspace_is_redundant_only_in_the_next_frame(self):
    # CTA-608-E D.2: a control code that is sent twice in two consecutive frames is acted on once,
    # a null in between makes the second one a new command
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	942c 942c 9429 9429 97e0 97e0 c1c2 43c4 4546

00:00:01:00	94a1 94a1

00:00:02:00	c780

00:00:03:00	94a1 8080 94a1

00:00:04:00	c880
"""

    doc = to_model(scc_content)

    texts = ["".join(list(span)[0].get_text() for span in p if isinstance(span, Span)) for p in list(list(doc.get_body())[0])]
    # ABCDEF, BS pair: ABCDE, G: ABCDEG, BS null BS: ABCD, H: ABCDH
    self.assertEqual("ABCDH", texts[-1])

  def test_cr_default_styles(self):
    # CTA-608-E C.14: a row that is created by a CR and has no PAC is white and not underlined
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	942c 942c 9425 9425 94ad 94ad 946b 946b 52ef f720 31ba 2079 e5ec ecef f720 756e 64e5 f2ec e96e e564

00:00:02:00	94ad 94ad 52ef f720 32ba 2043 522c 206e ef20 d0c1 43ba 20f7 68e9 f4e5
"""

    doc = to_model(scc_content)

    p_list = list(list(doc.get_body())[0])
    last = p_list[-1]
    self.assertEqual(["Row 1: yellow underlined", "Row 2: CR, no PAC: white"], self.get_rows(last))

    children = list(last)
    br_index = next(i for (i, child) in enumerate(children) if isinstance(child, Br))

    for span in children[:br_index]:
      self.assertEqual(NamedColors.yellow.value, span.get_style(StyleProperties.Color))
      self.assertEqual(TextDecorationType(underline=True), span.get_style(StyleProperties.TextDecoration))

    for span in children[br_index + 1:]:
      self.assertIn(span.get_style(StyleProperties.Color), (None, NamedColors.white.value))
      self.assertIn(span.get_style(StyleProperties.TextDecoration), (None, TextDecorationType(underline=False)))

  def test_scc_repeated_control_code_on_a_later_line_is_not_redundant(self):
    # CTA-608-E D.2: a control code is redundant only if it repeats the one in the immediately
    # preceding frame, so an EOC sent once and sent again one second later is acted on twice
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9420 9470 c1c2 942f

00:00:01:00	9420 9470 c3c4

00:00:02:00	942f

00:00:03:00	942f

00:00:04:00	942c
"""

    doc = to_model(scc_content)

    p_list = list(list(doc.get_body())[0])
    self.assertEqual(["AB", "CD", "AB"], [list(list(p)[0])[0].get_text() for p in p_list])
    self.assertEqual([SmpteTimeCode.parse(tc, FPS_29_97).to_temporal_offset() for tc in ("00:00:02:00", "00:00:03:00")],
                     [p_list[1].get_begin(), p_list[2].get_begin()])
    self.assertEqual(SmpteTimeCode.parse("00:00:04:00", FPS_29_97).to_temporal_offset(), p_list[2].get_end())

  def test_scc_roll_up_text_after_edm_without_pac(self):
    # after an EDM, roll-up text that is not preceded by a PAC is written on the base row, and rolls up
    # on the next CR
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9425 9425 94ad 94ad 9470 9470 c1c2

00:00:01:00	942c 942c

00:00:02:00	94ad 94ad 43c4

00:00:03:00	94ad 94ad 4546
"""

    doc = to_model(scc_content)

    p_list = list(list(doc.get_body())[0])
    self.assertEqual([["AB"], ["CD"], ["CD", "EF"]], [self.get_rows(p) for p in p_list])

    # all the roll-up paragraphs share the same region, at the bottom of the safe area
    self.assertEqual(1, len({p.get_region().get_id() for p in p_list}))

  def test_scc_roll_up_mid_row_code_after_edm_without_pac(self):
    # same as above, but the text after the EDM starts with a mid-row code
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9425 9425 94ad 94ad 9470 9470 c1c2

00:00:01:00	942c 942c

00:00:02:00	94ad 94ad 91ae 91ae 43c4

00:00:03:00	94ad 94ad 4546
"""

    doc = to_model(scc_content)

    p_list = list(list(doc.get_body())[0])
    self.assertEqual([["AB"], [" CD"], [" CD", "EF"]], [self.get_rows(p) for p in p_list])
    self.assertEqual(1, len({p.get_region().get_id() for p in p_list}))

  def test_scc_paint_on_after_edm_continues_at_the_cursor(self):
    # an EDM does not move the cursor: the Paint-On text that follows continues on the same row,
    # whether it starts with a character or with a mid-row code
    for mid_row_code in ("", "91ae 91ae "):
      with self.subTest(mid_row_code=mid_row_code):
        scc_content = f"""\
Scenarist_SCC V1.0

00:00:00:00	9429 9429 9470 9470 c1c2

00:00:01:00	942c 942c

00:00:02:00	{mid_row_code}43c4

00:00:03:00	942c 942c
"""

        doc = to_model(scc_content)

        p_list = list(list(doc.get_body())[0])
        self.assertEqual(2, len(p_list))
        self.assertEqual(p_list[0].get_region().get_style(StyleProperties.Origin).y,
                         p_list[1].get_region().get_style(StyleProperties.Origin).y)

  def test_scc_pop_on_pac_on_the_same_row(self):
    # a second PAC on the same row moves the cursor without changing the text that is already written: the
    # empty cells between the two are a gap, and a mid-row code changes only the color of the following text
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9420 9470 c8e5 ecec ef80 94f8 91a8 57ef f2ec 6480 942f

00:00:01:00	942c
"""

    doc = to_model(scc_content)

    self.check_captions(doc, [
      ("caption1", "00:00:00:10", "00:00:01:00", ["Hello" + " " * 11 + " World"], "pop1"),
    ])

    spans = list(list(list(doc.get_body())[0])[0])
    self.assertEqual(["Hello", " " * 11, " World"], [list(span)[0].get_text() for span in spans])
    # indent PACs set the default color, white
    self.check_element_style(spans[0], StyleProperties.Color, None)
    self.check_element_style(spans[1], StyleProperties.BackgroundColor, NamedColors.transparent.value)
    self.check_element_style(spans[2], StyleProperties.Color, NamedColors.red.value)

  def test_scc_backspace_across_a_mid_row_code(self):
    # BS erases the space of the mid-row code, then the preceding character, and the following characters are
    # written in their place with the attributes of the mid-row code
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9420 9470 c1c2 91a8 9421 8080 9421 43c4 942f

00:00:01:00	942c
"""

    doc = to_model(scc_content)

    self.check_captions(doc, [
      ("caption1", "00:00:00:08", "00:00:01:00", ["ACD"], "pop1"),
    ])

    spans = list(list(list(doc.get_body())[0])[0])
    self.assertEqual(["A", "CD"], [list(span)[0].get_text() for span in spans])
    # indent PACs set the default color, white
    self.check_element_style(spans[0], StyleProperties.Color, None)
    self.check_element_style(spans[1], StyleProperties.Color, NamedColors.red.value)

  def test_scc_backspace_in_the_first_column(self):
    # BS does nothing when the cursor is in the first column
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9420 9470 9421 58d9 942f

00:00:01:00	942c
"""

    self.check_captions(to_model(scc_content), [
      ("caption1", "00:00:00:04", "00:00:01:00", ["XY"], "pop1"),
    ])

  def test_scc_tab_offsets(self):
    # tab offsets move the cursor to the right
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9420 9470 9723 c1c2 97a1 43c4 942f

00:00:01:00	942c
"""

    doc = to_model(scc_content)

    self.check_captions(doc, [
      ("caption1", "00:00:00:06", "00:00:01:00", ["AB CD"], "pop1"),
    ])
    self.check_region_origin(doc.get_region("pop1"), 4 + 3, 16, doc.get_cell_resolution())

  def test_scc_paint_on_delete_to_end_of_row(self):
    # DER erases the characters from the cursor to the end of the row, which ends the displayed caption
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9429 9470 c1c2 43c4 4546 9470 97a2 9424

00:00:01:00	942c
"""

    self.check_captions(to_model(scc_content), [
      ("caption1", "00:00:00:02", "00:00:00:07", ["ABCDEF"], "paint1"),
      ("caption2", "00:00:00:07", "00:00:01:00", ["AB"], "paint1"),
    ])

  def test_scc_roll_up_fewer_rows(self):
    # when the number of rows of the Roll-Up window decreases, the rows above the window are erased
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9427 94ad 52ef f731 94ad 52ef f732 94ad 52ef f7b3 94ad 52ef f734

00:00:01:00	9425

00:00:02:00	942c
"""

    self.check_captions(to_model(scc_content), [
      ("caption1", "00:00:00:02", "00:00:00:04", ["Row1"], "rollup1"),
      ("caption2", "00:00:00:04", "00:00:00:07", ["Row1", "Row2"], "rollup1"),
      ("caption3", "00:00:00:07", "00:00:00:10", ["Row1", "Row2", "Row3"], "rollup1"),
      ("caption4", "00:00:00:10", "00:00:01:00", ["Row1", "Row2", "Row3", "Row4"], "rollup1"),
      ("caption5", "00:00:01:00", "00:00:02:00", ["Row3", "Row4"], "rollup1"),
    ])

  def test_scc_roll_up_pac_moves_the_window(self):
    # a PAC on another row moves the Roll-Up window and the rows it displays, which does not end the caption
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9425 94ad 9470 c1c2 94ad 13d0 43c4

00:00:01:00	942c
"""

    self.check_captions(to_model(scc_content), [
      ("caption1", "00:00:00:03", "00:00:00:04", ["AB"], "rollup1"),
      ("caption2", "00:00:00:04", "00:00:01:00", ["AB", "CD"], "rollup1"),
    ])

  def test_scc_carriage_return_outside_roll_up(self):
    # CR is ignored in Pop-On and Paint-On styles
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9420 9470 c1c2 942f

00:00:00:10	94ad

00:00:00:20	9429 43c4 94ad

00:00:01:00	942c
"""

    self.check_captions(to_model(scc_content), [
      ("caption1", "00:00:00:03", "00:00:00:21", ["AB"], "pop1"),
      ("caption2", "00:00:00:21", "00:00:01:00", ["ABCD"], "paint2"),
    ])

  def test_scc_roll_up_extended_character(self):
    # an extended character replaces the preceding character in place, which does not end the caption
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9425 94ad 9470 c180 9230 c280

00:00:01:00	942c
"""

    doc = to_model(scc_content)

    self.check_captions(doc, [
      ("caption1", "00:00:00:03", "00:00:01:00", ["ÀB"], "rollup1"),
    ])

    spans = list(list(list(doc.get_body())[0])[0])
    self.assertEqual(["ÀB"], [list(span)[0].get_text() for span in spans])
    self.assertIsNone(spans[0].get_begin())

  def test_scc_right_margin_limit(self):
    # Encoder error: text that goes past the 32nd column. CTA-608-E C.13: the cursor can not move past the
    # last column, a character that is written there replaces the one in the column, a tab offset stops
    # at the last column, and a BS that follows a character in the last column moves the cursor to column 31
    scc_content = """\
Scenarist_SCC V1.0

00:02:32:03	9420 9420 94ae 94ae 15e0 15e0 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 d5d6 5758 d9da b031 32b3 34b5 58d9 16fe 16fe 97a1 97a1 9723 9723 da80 97e0 97e0 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 d5d6 5758 d9da b031 32b3 34b5 94a1 94a1 f880 1340 1340 94a1 94a1 5180 942f 942f
"""

    with self.assertLogs("ttconv.scc.context", level="WARNING") as logs:
      doc = to_model(scc_content)

    self.assertEqual(1, len([log for log in logs.output if "overflows" in log]))

    last = list(list(doc.get_body())[0])[-1]
    rows = [list(child)[0].get_text() for child in last if isinstance(child, Span)]

    # 32 columns: the characters after the 32nd replace the 32nd one, here ...0123 4 5 X Y become ...01234 Y
    # on the first row, and the BS of the third row erases the column 31 before the x is written there
    self.assertEqual(["ABCDEFGHIJKLMNOPQRSTUVWXYZ01234Y", "Z", "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123x5", "Q"], rows)


  def test_scc_flash_on_occupies_a_cell(self):
    # CTA-608-E C.19: the FON code occupies a cell, shown as a space, so "Ab" FON "Cd" has two characters
    # between the b and the C
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9420 9420 94ae 94ae 1540 1540 c162 2080 1428 1428 4364 942f 942f
"""

    doc = to_model(scc_content)

    p_list = list(list(doc.get_body())[0])
    self.assertEqual(1, len(p_list))
    text = "".join(list(span)[0].get_text() for span in p_list[0] if isinstance(span, Span))
    self.assertEqual("Ab  Cd", text)

  def test_scc_paint_on_backspace_shows_the_erased_character_until_the_code(self):
    # CTA-608-E B.12: BS erases the character to the left; the character is on screen until then
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9429 9429 1540 1540 c162 a180

00:00:02:00	94a1 94a1

00:00:04:00	942c 942c
"""

    doc = to_model(scc_content)

    p_list = list(list(doc.get_body())[0])
    texts = ["".join(list(span)[0].get_text() for span in p if isinstance(span, Span)) for p in p_list]
    self.assertEqual(["Ab!", "Ab"], texts)
    self.assertEqual(p_list[0].get_end(), p_list[1].get_begin())


  def test_scc_paint_on_extended_character_does_not_end_the_paragraph(self):
    # an extended character replaces the character before it, it is not a BS that ends the paragraph
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9429 9429 1540 1540 c180 9220 c280

00:00:04:00	942c 942c
"""

    doc = to_model(scc_content)

    p_list = list(list(doc.get_body())[0])
    self.assertEqual(1, len(p_list))
    self.assertEqual("\u00c1B", "".join(list(span)[0].get_text() for span in p_list[0] if isinstance(span, Span)))

  def test_scc_fifth_row_replaces_the_oldest_row(self):
    # CTA-608-E C.5: a caption memory has four rows at most, a fifth row replaces the oldest one
    scc_content = """\
Scenarist_SCC V1.0

00:00:00:00	9420 9420 94ae 94ae 9140 9140 c180 9240 9240 c280 1540 1540 4380 1640 1640 c480 9740 9740 4580 942f 942f
"""

    doc = to_model(scc_content)

    p_list = list(list(doc.get_body())[0])
    self.assertEqual(1, len(p_list))
    texts = [list(span)[0].get_text() for span in p_list[0] if isinstance(span, Span)]
    self.assertEqual(["B", "C", "D", "E"], texts)

if __name__ == '__main__':
  unittest.main()
