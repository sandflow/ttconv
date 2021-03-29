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

"""Unit tests for the SCC paragraph"""

# pylint: disable=R0201,C0115,C0116,W0212

import unittest
from fractions import Fraction

from ttconv.model import ContentDocument, Span, Br
from ttconv.scc.content import SccCaptionLine
from ttconv.scc.paragraph import SccCaptionParagraph
from ttconv.scc.style import SccCaptionStyle
from ttconv.time_code import SmpteTimeCode, FPS_30


class SccCaptionParagraphTest(unittest.TestCase):

  def test_content(self):
    caption_paragraph = SccCaptionParagraph()
    self.assertEqual(0, caption_paragraph._safe_area_x_offset)
    self.assertEqual(0, caption_paragraph._safe_area_y_offset)

    caption_paragraph = SccCaptionParagraph(4, 2)
    self.assertEqual(4, caption_paragraph._safe_area_x_offset)
    self.assertEqual(2, caption_paragraph._safe_area_y_offset)

    self.assertIsNone(caption_paragraph.get_current_text())
    self.assertEqual(0, len(caption_paragraph._caption_lines))

    caption_paragraph.new_caption_text()
    self.assertEqual(caption_paragraph.get_current_line(), caption_paragraph.get_lines()[0])
    self.assertIsNotNone(caption_paragraph.get_current_text())
    self.assertEqual(1, len(caption_paragraph._caption_lines))

    caption_paragraph.set_cursor_at(4, 4)
    caption_paragraph.new_caption_text()
    self.assertEqual((4, 4), caption_paragraph.get_cursor())
    self.assertEqual(caption_paragraph.get_current_line(), caption_paragraph.get_lines()[4])
    self.assertEqual(4, caption_paragraph.get_current_line().get_row())
    self.assertEqual(4, caption_paragraph.get_current_line().get_indent())
    self.assertEqual(0, caption_paragraph.get_current_line().get_cursor())
    self.assertEqual(0, caption_paragraph.get_current_text().get_cursor())

    caption_paragraph.indent_cursor(3)
    self.assertEqual((4, 7), caption_paragraph.get_cursor())
    self.assertEqual(4, caption_paragraph.get_current_line().get_row())
    self.assertEqual(7, caption_paragraph.get_current_line().get_indent())
    self.assertEqual(0, caption_paragraph.get_current_line().get_cursor())
    self.assertEqual(0, caption_paragraph.get_current_text().get_cursor())

    caption_paragraph.append_text("Hello")
    self.assertEqual(5, caption_paragraph.get_current_line().get_cursor())
    self.assertEqual(5, caption_paragraph.get_current_text().get_cursor())

    caption_paragraph.set_cursor_at(4, 10)
    self.assertEqual((4, 10), caption_paragraph.get_cursor())
    self.assertEqual(4, caption_paragraph.get_current_line().get_row())
    self.assertEqual(7, caption_paragraph.get_current_line().get_indent())

    self.assertEqual(3, caption_paragraph.get_current_line().get_cursor())
    self.assertEqual(3, caption_paragraph.get_current_text().get_cursor())

    caption_paragraph.indent_cursor(2)
    self.assertEqual((4, 12), caption_paragraph.get_cursor())
    self.assertEqual(4, caption_paragraph.get_current_line().get_row())
    self.assertEqual(7, caption_paragraph.get_current_line().get_indent())

    self.assertEqual(5, caption_paragraph.get_current_line().get_cursor())
    self.assertEqual(5, caption_paragraph.get_current_text().get_cursor())

    self.assertListEqual([], caption_paragraph.get_last_caption_lines(0))
    self.assertListEqual([caption_paragraph.get_current_line()], caption_paragraph.get_last_caption_lines(1))

    caption_paragraph.set_cursor_at(2, 4)
    caption_paragraph.new_caption_text()
    caption_paragraph.append_text("World")
    self.assertEqual(5, caption_paragraph.get_current_line().get_cursor())
    self.assertEqual(5, caption_paragraph.get_current_text().get_cursor())

    self.assertRaisesRegex(RuntimeError, "Cannot roll-Up Unknown-styled caption.",
                           caption_paragraph.roll_up)

    caption_paragraph._caption_style = SccCaptionStyle.PopOn
    self.assertRaisesRegex(RuntimeError, "Cannot roll-Up PopOn-styled caption.",
                           caption_paragraph.roll_up)

    caption_paragraph._caption_style = SccCaptionStyle.RollUp
    caption_paragraph.roll_up()
    self.assertEqual(2, len(caption_paragraph.get_lines()))
    self.assertEqual(caption_paragraph.get_current_line(), caption_paragraph.get_lines().get(1))
    self.assertEqual(1, caption_paragraph.get_lines().get(1).get_row())
    self.assertEqual("World", caption_paragraph.get_lines().get(1).get_current_text().get_text())

    self.assertTrue(isinstance(caption_paragraph.get_lines().get(3), SccCaptionLine))
    self.assertEqual(3, caption_paragraph.get_lines().get(3).get_row())
    self.assertEqual("Hello", caption_paragraph.get_lines().get(3).get_current_text().get_text())

    self.assertListEqual([], caption_paragraph.get_last_caption_lines(0))
    self.assertListEqual([caption_paragraph.get_lines().get(3)], caption_paragraph.get_last_caption_lines(1))
    self.assertListEqual([caption_paragraph.get_lines().get(1), caption_paragraph.get_lines().get(3)],
                         caption_paragraph.get_last_caption_lines(2))

    caption_paragraph.set_cursor_at(15, 0)
    caption_paragraph.new_caption_text()
    caption_paragraph.append_text("!!!")
    self.assertEqual(3, caption_paragraph.get_current_line().get_cursor())
    self.assertEqual(3, caption_paragraph.get_current_text().get_cursor())

    caption_paragraph.roll_up()
    self.assertEqual(3, len(caption_paragraph.get_lines()))
    self.assertTrue(isinstance(caption_paragraph.get_lines().get(0), SccCaptionLine))
    self.assertEqual(0, caption_paragraph.get_lines().get(0).get_row())
    self.assertEqual("World", caption_paragraph.get_lines().get(0).get_current_text().get_text())

    self.assertTrue(isinstance(caption_paragraph.get_lines().get(2), SccCaptionLine))
    self.assertEqual(2, caption_paragraph.get_lines().get(2).get_row())
    self.assertEqual("Hello", caption_paragraph.get_lines().get(2).get_current_text().get_text())

    self.assertEqual(caption_paragraph.get_current_line(), caption_paragraph.get_lines().get(14))
    self.assertEqual(14, caption_paragraph.get_lines().get(14).get_row())
    self.assertEqual("!!!", caption_paragraph.get_lines().get(14).get_current_text().get_text())

    self.assertListEqual([], caption_paragraph.get_last_caption_lines(0))
    self.assertListEqual([caption_paragraph.get_lines().get(14)], caption_paragraph.get_last_caption_lines(1))
    self.assertListEqual(
      [caption_paragraph.get_lines().get(2), caption_paragraph.get_lines().get(14)],
      caption_paragraph.get_last_caption_lines(2))
    self.assertListEqual(
      [caption_paragraph.get_lines().get(0), caption_paragraph.get_lines().get(2), caption_paragraph.get_lines().get(14)],
      caption_paragraph.get_last_caption_lines(3))

  def test_to_paragraph(self):
    caption_paragraph = SccCaptionParagraph()
    doc = ContentDocument()

    self.assertRaisesRegex(TypeError, "Element id must be a valid xml:id string", caption_paragraph.to_paragraph, doc)

    caption_paragraph.set_id("test-id")

    origin = caption_paragraph.get_origin()
    self.assertEqual(0, origin.x.value)
    self.assertEqual(0, origin.y.value)

    extent = caption_paragraph.get_extent()
    self.assertEqual(0, extent.width.value)
    self.assertEqual(0, extent.height.value)

    paragraph = caption_paragraph.to_paragraph(doc)

    self.assertEqual("test-id", paragraph.get_id())
    self.assertEqual(doc, paragraph.get_doc())
    self.assertIsNone(paragraph.get_begin())
    self.assertIsNone(paragraph.get_end())

    children = list(paragraph)
    self.assertEqual(0, len(children))

    caption_paragraph.set_begin(SmpteTimeCode.parse("00:01:02:03", FPS_30))
    caption_paragraph.set_end(SmpteTimeCode.parse("00:02:03:04", FPS_30))

    caption_paragraph.set_cursor_at(0)
    caption_paragraph.new_caption_text()
    caption_paragraph.append_text("Hello")
    caption_paragraph.set_cursor_at(1)
    caption_paragraph.new_caption_text()
    caption_paragraph.append_text("World")

    paragraph = caption_paragraph.to_paragraph(doc)

    self.assertEqual("test-id", paragraph.get_id())
    self.assertEqual(doc, paragraph.get_doc())
    self.assertEqual(Fraction(1863, 30), paragraph.get_begin())
    self.assertEqual(Fraction(3694, 30), paragraph.get_end())

    children = list(paragraph)
    self.assertEqual(3, len(children))

    self.assertIsInstance(children[0], Span)
    self.assertEqual("Hello", list(children[0])[0].get_text())

    self.assertIsInstance(children[1], Br)

    self.assertIsInstance(children[2], Span)
    self.assertEqual("World", list(children[2])[0].get_text())


if __name__ == '__main__':
  unittest.main()
