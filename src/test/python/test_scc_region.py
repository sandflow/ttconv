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

"""Unit tests for the SCC paragraph region"""

# pylint: disable=R0201,C0115,C0116,W0212

import unittest
from fractions import Fraction
from typing import Dict, Tuple

from ttconv.model import ContentDocument, CellResolutionType
from ttconv.scc.display_memory_snapshot import SccDisplayMemorySnapshot
from ttconv.scc.caption_style import SccCaptionStyle
from ttconv.scc.display_memory import SccCellEvent, SccDisplayMemory, SccPen
from ttconv.style_properties import StyleProperties, ShowBackgroundType


def make_memory(lines: Dict[int, Tuple[int, str]]) -> SccDisplayMemory:
  """Returns a memory with the specified text, as {row: (column, text)}"""
  memory = SccDisplayMemory()
  for (row, (column, text)) in lines.items():
    for (i, char) in enumerate(text):
      memory.set_cell(row, column + i, SccCellEvent(char, SccPen.DEFAULT, Fraction(0)))
  return memory


class SccParagraphRegionTest(unittest.TestCase):

  def test_region_prefix(self):
    for (caption_style, prefix) in ((SccCaptionStyle.PaintOn, "paint"), (SccCaptionStyle.PopOn, "pop"),
                                    (SccCaptionStyle.RollUp, "rollup")):
      caption = SccDisplayMemorySnapshot(SccDisplayMemory(), caption_style, None, None)
      self.assertEqual(prefix, caption._get_region_prefix())

  def test_matching_region(self):
    doc = ContentDocument()
    doc.set_cell_resolution(CellResolutionType(rows=19, columns=40))

    safe_area_x_offset = 4
    safe_area_y_offset = 2

    caption = SccDisplayMemorySnapshot(make_memory({4: (7, "A 20-char long line.")}), SccCaptionStyle.PopOn, None, None,
                                  safe_area_x_offset=safe_area_x_offset, safe_area_y_offset=safe_area_y_offset)

    origin = caption.get_origin()
    self.assertEqual(11, origin.x.value)
    self.assertEqual(5, origin.y.value)

    extent = caption.get_extent()
    self.assertEqual(20, extent.width.value)
    self.assertEqual(1, extent.height.value)


    self.assertIsNone(caption._find_matching_region(doc))
    region = caption._create_matching_region(doc)

    self.assertEqual("pop1", region.get_id())
    self.assertTrue(caption._has_same_origin_as_region(region, doc))
    self.assertEqual(region, caption._find_matching_region(doc))

    self.assertEqual(ShowBackgroundType.whenActive, region.get_style(StyleProperties.ShowBackground))

    region_extent = region.get_style(StyleProperties.Extent)

    self.assertEqual(50, region_extent.width.value)
    self.assertEqual(63, region_extent.height.value)

    # a wider caption at the same origin extends the region, up to the right of the safe area
    caption = SccDisplayMemorySnapshot(make_memory({4: (7, "A 20-char long line."), 5: (7, "A 25-character long line.")}),
                                  SccCaptionStyle.PopOn, None, None,
                                  safe_area_x_offset=safe_area_x_offset, safe_area_y_offset=safe_area_y_offset)

    origin = caption.get_origin()
    self.assertEqual(11, origin.x.value)
    self.assertEqual(5, origin.y.value)

    extent = caption.get_extent()
    self.assertEqual(25, extent.width.value)
    self.assertEqual(2, extent.height.value)


    self.assertEqual(region, caption._find_matching_region(doc))
    caption._extend_region_to_paragraph(region, doc)
    self.assertTrue(caption._has_same_origin_as_region(region, doc))

    region_extent = region.get_style(StyleProperties.Extent)

    self.assertEqual(62, region_extent.width.value)
    self.assertEqual(63, region_extent.height.value)


if __name__ == '__main__':
  unittest.main()
