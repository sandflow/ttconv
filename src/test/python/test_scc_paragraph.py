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

from ttconv.model import Document, Span, Br
from ttconv.scc.content import SccCaptionLineBreak
from ttconv.scc.paragraph import SccCaptionParagraph
from ttconv.scc.style import SccCaptionStyle
from ttconv.scc.time_codes import SccTimeCode


class SccCaptionParagraphTest(unittest.TestCase):

  def test_content(self):
    caption_paragraph = SccCaptionParagraph()
    self.assertEqual(0, caption_paragraph._safe_area_x_offset)
    self.assertEqual(0, caption_paragraph._safe_area_y_offset)

    caption_paragraph = SccCaptionParagraph(4, 2)
    self.assertEqual(4, caption_paragraph._safe_area_x_offset)
    self.assertEqual(2, caption_paragraph._safe_area_y_offset)

    self.assertIsNone(caption_paragraph.get_current_text())
    self.assertEqual(0, len(caption_paragraph._caption_contents))

    caption_paragraph.new_caption_text()
    self.assertIsNotNone(caption_paragraph.get_current_text())
    self.assertEqual(1, len(caption_paragraph._caption_contents))

    caption_paragraph.set_row_offset(None)
    self.assertEqual(2, caption_paragraph.get_row_offset())
    caption_paragraph.set_row_offset(4)
    self.assertEqual(6, caption_paragraph.get_row_offset())

    caption_paragraph.set_column_offset(None)
    self.assertEqual(4, caption_paragraph.get_column_offset())
    caption_paragraph.set_column_offset(4)
    self.assertEqual(8, caption_paragraph.get_column_offset())

    caption_paragraph.apply_current_text_offsets()
    self.assertEqual(6, caption_paragraph.get_current_text().get_y_offset())
    self.assertEqual(8, caption_paragraph.get_current_text().get_x_offset())

    caption_paragraph.indent(3)
    self.assertEqual(6, caption_paragraph.get_row_offset())
    self.assertEqual(11, caption_paragraph.get_column_offset())
    self.assertEqual(6, caption_paragraph.get_current_text().get_y_offset())
    self.assertEqual(11, caption_paragraph.get_current_text().get_x_offset())

    self.assertListEqual([], caption_paragraph.get_last_caption_lines(0))
    self.assertListEqual([caption_paragraph.get_current_text()], caption_paragraph.get_last_caption_lines(1))

    self.assertRaisesRegex(RuntimeError, "Cannot set Roll-Up row offset for SccCaptionStyle.Unknown-styled caption.",
                           caption_paragraph.apply_roll_up_row_offsets)

    caption_paragraph._style = SccCaptionStyle.PopOn
    self.assertRaisesRegex(RuntimeError, "Cannot set Roll-Up row offset for SccCaptionStyle.PopOn-styled caption.",
                           caption_paragraph.apply_roll_up_row_offsets)

    caption_paragraph._style = SccCaptionStyle.RollUp
    caption_paragraph.apply_roll_up_row_offsets()
    self.assertEqual(17, caption_paragraph.get_current_text().get_y_offset())
    self.assertEqual(11, caption_paragraph.get_current_text().get_x_offset())

    self.assertListEqual([], caption_paragraph.get_last_caption_lines(0))
    self.assertListEqual([caption_paragraph.get_current_text()], caption_paragraph.get_last_caption_lines(1))
    self.assertListEqual([caption_paragraph.get_current_text()], caption_paragraph.get_last_caption_lines(2))

    caption_paragraph._caption_contents.append(SccCaptionLineBreak())
    caption_paragraph.new_caption_text()
    caption_paragraph.apply_current_text_offsets()

    caption_paragraph.apply_roll_up_row_offsets()
    self.assertEqual(17, caption_paragraph.get_current_text().get_y_offset())
    self.assertEqual(11, caption_paragraph.get_current_text().get_x_offset())

    self.assertListEqual([], caption_paragraph.get_last_caption_lines(0))
    self.assertListEqual([caption_paragraph.get_current_text()], caption_paragraph.get_last_caption_lines(1))
    self.assertListEqual(
      [caption_paragraph._caption_contents[-3], caption_paragraph._caption_contents[-2], caption_paragraph.get_current_text()],
      caption_paragraph.get_last_caption_lines(2))
    self.assertListEqual(
      [caption_paragraph._caption_contents[-3], caption_paragraph._caption_contents[-2], caption_paragraph.get_current_text()],
      caption_paragraph.get_last_caption_lines(3))

  def test_to_paragraph(self):
    caption_paragraph = SccCaptionParagraph()
    doc = Document()

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

    caption_paragraph.set_begin(SccTimeCode.parse("00:01:02:03"))
    caption_paragraph.set_end(SccTimeCode.parse("00:02:03:04"))

    caption_paragraph.new_caption_text()
    caption_paragraph.get_current_text().append("Hello")
    caption_paragraph._caption_contents.append(SccCaptionLineBreak())
    caption_paragraph.new_caption_text()
    caption_paragraph.get_current_text().append("World")

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
