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

"""Unit tests for the SCC caption paragraph"""

# pylint: disable=R0201,C0115,C0116,W0212

import unittest
from fractions import Fraction
from typing import Dict, Tuple

from ttconv.model import ContentDocument, Span, Br
from ttconv.scc.display_memory_snapshot import SccDisplayMemorySnapshot
from ttconv.scc.caption_style import SccCaptionStyle
from ttconv.scc.config import TextAlignment
from ttconv.scc.display_memory import SccCellEvent, SccDisplayMemory, SccPen
from ttconv.style_properties import TextAlignType, StyleProperties, NamedColors, FontStyleType, TextDecorationType


def make_memory(lines: Dict[int, Tuple[int, str]], pen: SccPen = SccPen.DEFAULT,
              time: Fraction = Fraction(0)) -> SccDisplayMemory:
  """Returns a memory with the specified text, as {row: (column, text)}"""
  memory = SccDisplayMemory()
  for (row, (column, text)) in lines.items():
    for (i, char) in enumerate(text):
      memory.set_cell(row, column + i, SccCellEvent(char, pen, time))
  return memory


def row_text(memory: SccDisplayMemory, row: int) -> str:
  """Returns the text of a row, from its first to its last character, empty
  cells being spaces"""
  return "".join(" " if cell is None else cell.char for cell in memory.get_row_cells(row))


class SccDisplayMemorySnapshotTest(unittest.TestCase):

  def test_content(self):
    caption = SccDisplayMemorySnapshot(make_memory({4: (7, "Hello"), 2: (4, " World ")}), SccCaptionStyle.PopOn, None, None,
                                  safe_area_x_offset=4, safe_area_y_offset=2)

    self.assertFalse(caption.is_empty())

    # origin: first column and row - 1, in the root area
    origin = caption.get_origin()
    self.assertEqual(4 + 4, origin.x.value)
    self.assertEqual(1 + 2, origin.y.value)

    extent = caption.get_extent()
    self.assertEqual(7, extent.width.value)
    self.assertEqual(3, extent.height.value)

  def test_empty(self):
    caption = SccDisplayMemorySnapshot(SccDisplayMemory(), SccCaptionStyle.PopOn, None, None,
                                  safe_area_x_offset=4, safe_area_y_offset=2)

    self.assertTrue(caption.is_empty())
    self.assertEqual(4, caption.get_origin().x.value)
    self.assertEqual(2, caption.get_origin().y.value)
    self.assertEqual(0, caption.get_extent().width.value)
    self.assertEqual(0, caption.get_extent().height.value)

  def test_gap(self):
    memory = make_memory({15: (2, "Hello")})
    for (i, char) in enumerate("World"):
      memory.set_cell(15, 10 + i, SccCellEvent(char, SccPen.DEFAULT, Fraction(0)))
    caption = SccDisplayMemorySnapshot(memory, SccCaptionStyle.PopOn, None, None)

    self.assertEqual("Hello   World", row_text(memory, 15))

    p = caption.to_paragraph(ContentDocument(), "caption1")
    spans = list(p)
    self.assertEqual(["Hello", "   ", "World"], [list(span)[0].get_text() for span in spans])
    self.assertEqual(NamedColors.black.value, spans[0].get_style(StyleProperties.BackgroundColor))
    self.assertEqual(NamedColors.transparent.value, spans[1].get_style(StyleProperties.BackgroundColor))
    self.assertEqual(NamedColors.black.value, spans[2].get_style(StyleProperties.BackgroundColor))

  def test_paragraph_alignment_detection_left(self):
    caption = SccDisplayMemorySnapshot(make_memory({1: (0, "0123456789"), 2: (0, "012345"), 3: (0, "0123")}),
                                  SccCaptionStyle.PopOn, None, None)
    self.assertEqual(TextAlignType.start, caption._guess_text_alignment())

  def test_paragraph_alignment_detection_center(self):
    caption = SccDisplayMemorySnapshot(make_memory({1: (0, "0123456789"), 2: (2, "012345"), 3: (3, "0123")}),
                                  SccCaptionStyle.PopOn, None, None)
    self.assertEqual(TextAlignType.center, caption._guess_text_alignment())

  def test_paragraph_alignment_detection_right(self):
    caption = SccDisplayMemorySnapshot(make_memory({1: (0, "0123456789"), 2: (4, "012345"), 3: (6, "0123")}),
                                  SccCaptionStyle.PopOn, None, None)
    self.assertEqual(TextAlignType.end, caption._guess_text_alignment())

  def test_paragraph_content_alignment_detection_left(self):
    caption = SccDisplayMemorySnapshot(make_memory({1: (0, "  0123456789"), 2: (0, "  012345"), 3: (0, "  0123")}),
                                  SccCaptionStyle.PopOn, None, None)
    self.assertEqual(TextAlignType.start, caption._guess_text_alignment())

  def test_paragraph_content_alignment_detection_center(self):
    caption = SccDisplayMemorySnapshot(make_memory({1: (2, "0123456789"), 2: (2, "  012345"), 3: (2, "   0123")}),
                                  SccCaptionStyle.PopOn, None, None)
    self.assertEqual(TextAlignType.center, caption._guess_text_alignment())

    caption = SccDisplayMemorySnapshot(make_memory({1: (0, "  0123456789"), 2: (2, "  012345"), 3: (5, "0123")}),
                                  SccCaptionStyle.PopOn, None, None)
    self.assertEqual(TextAlignType.center, caption._guess_text_alignment())

  def test_paragraph_content_alignment_detection_right(self):
    caption = SccDisplayMemorySnapshot(make_memory({10: (0, "0123456789"), 11: (0, "    012345"), 12: (0, "      0123")}),
                                  SccCaptionStyle.PopOn, None, None)
    self.assertEqual(TextAlignType.end, caption._guess_text_alignment())

    caption = SccDisplayMemorySnapshot(make_memory({10: (0, "0123456789"), 11: (0, "    012345"), 12: (4, "  0123")}),
                                  SccCaptionStyle.PopOn, None, None)
    self.assertEqual(TextAlignType.end, caption._guess_text_alignment())

  def test_text_alignment(self):
    memory = make_memory({1: (0, "0123456789"), 2: (2, "012345"), 3: (3, "0123")})

    # Pop-On captions get the guessed alignment, or the configured one
    p = SccDisplayMemorySnapshot(memory, SccCaptionStyle.PopOn, None, None).to_paragraph(ContentDocument(), "caption1")
    self.assertEqual(TextAlignType.center, p.get_style(StyleProperties.TextAlign))

    p = SccDisplayMemorySnapshot(memory, SccCaptionStyle.PopOn, None, None, text_alignment=TextAlignment.RIGHT) \
      .to_paragraph(ContentDocument(), "caption1")
    self.assertEqual(TextAlignType.end, p.get_style(StyleProperties.TextAlign))

    # other captions do not
    p = SccDisplayMemorySnapshot(memory, SccCaptionStyle.PaintOn, None, None).to_paragraph(ContentDocument(), "caption1")
    self.assertIsNone(p.get_style(StyleProperties.TextAlign))

  def test_to_paragraph(self):
    doc = ContentDocument()

    caption = SccDisplayMemorySnapshot(make_memory({1: (0, "Hello"), 2: (0, "World")}), SccCaptionStyle.PopOn,
                                  Fraction(1863, 30), Fraction(3694, 30))

    self.assertRaisesRegex(TypeError, "Element id must be a valid xml:id string", caption.to_paragraph, doc, "")

    paragraph = caption.to_paragraph(doc, "test-id")

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

  def test_to_paragraph_empty_rows(self):
    caption = SccDisplayMemorySnapshot(make_memory({1: (0, "Hello"), 4: (0, "World")}), SccCaptionStyle.PopOn, None, None)
    children = list(caption.to_paragraph(ContentDocument(), "caption1"))
    self.assertEqual([Span, Br, Br, Br, Span], [type(child) for child in children])

  def test_to_paragraph_styles(self):
    pen = SccPen(color=NamedColors.yellow.value, font_style=FontStyleType.italic,
                 text_decoration=TextDecorationType(underline=True), background=NamedColors.blue.value)
    memory = make_memory({1: (0, "AB")}, pen)
    for (i, char) in enumerate("CD"):
      memory.set_cell(1, 2 + i, SccCellEvent(char, SccPen.DEFAULT, Fraction(0)))

    spans = list(SccDisplayMemorySnapshot(memory, SccCaptionStyle.PopOn, None, None).to_paragraph(ContentDocument(), "caption1"))
    self.assertEqual(["AB", "CD"], [list(span)[0].get_text() for span in spans])

    self.assertEqual(NamedColors.yellow.value, spans[0].get_style(StyleProperties.Color))
    self.assertEqual(FontStyleType.italic, spans[0].get_style(StyleProperties.FontStyle))
    self.assertEqual(TextDecorationType(underline=True), spans[0].get_style(StyleProperties.TextDecoration))
    self.assertEqual(NamedColors.blue.value, spans[0].get_style(StyleProperties.BackgroundColor))

    # default attributes: no color, font style or text decoration, and a black background
    self.assertIsNone(spans[1].get_style(StyleProperties.Color))
    self.assertIsNone(spans[1].get_style(StyleProperties.FontStyle))
    self.assertIsNone(spans[1].get_style(StyleProperties.TextDecoration))
    self.assertEqual(NamedColors.black.value, spans[1].get_style(StyleProperties.BackgroundColor))

  def test_to_paragraph_appearance(self):
    # "Hello " was displayed when the caption began, "my" and "friend" were written later
    memory = make_memory({15: (0, "Hello ")}, time=Fraction(1))
    for (column, char, time) in ((6, "m", 3), (7, "y", 3), (8, " ", 4), (9, "f", 5), (10, "r", 5), (11, "i", 6),
                                 (12, "e", 6), (13, "n", 7), (14, "d", 7)):
      memory.set_cell(15, column, SccCellEvent(char, SccPen.DEFAULT, Fraction(time)))

    caption = SccDisplayMemorySnapshot(memory, SccCaptionStyle.RollUp, Fraction(2), Fraction(10))
    spans = list(caption.to_paragraph(ContentDocument(), "caption1"))

    # a span starts at each word that appears after the begin of the caption, and begins when its first
    # character was written, relative to the begin of the caption
    self.assertEqual(["Hello ", "my ", "friend"], [list(span)[0].get_text() for span in spans])
    self.assertEqual([None, Fraction(1), Fraction(3)], [span.get_begin() for span in spans])


if __name__ == '__main__':
  unittest.main()
