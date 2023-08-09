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

from ttconv.model import ContentDocument, CellResolutionType
from ttconv.scc.caption_paragraph import SccCaptionParagraph, _SccParagraphRegion
from ttconv.scc.style import SccCaptionStyle
from ttconv.style_properties import StyleProperties, ShowBackgroundType


class SccParagraphRegionTest(unittest.TestCase):

  def test_region_prefix(self):
    doc = ContentDocument()

    caption_paragraph = SccCaptionParagraph()
    paragraph_region = _SccParagraphRegion(caption_paragraph, doc)
    self.assertEqual("region", paragraph_region._get_region_prefix())

    caption_paragraph = SccCaptionParagraph(caption_style=SccCaptionStyle.PaintOn)
    paragraph_region = _SccParagraphRegion(caption_paragraph, doc)
    self.assertEqual("paint", paragraph_region._get_region_prefix())

    caption_paragraph = SccCaptionParagraph(caption_style=SccCaptionStyle.PopOn)
    paragraph_region = _SccParagraphRegion(caption_paragraph, doc)
    self.assertEqual("pop", paragraph_region._get_region_prefix())

    caption_paragraph = SccCaptionParagraph(caption_style=SccCaptionStyle.RollUp)
    paragraph_region = _SccParagraphRegion(caption_paragraph, doc)
    self.assertEqual("rollup", paragraph_region._get_region_prefix())

  def test_matching_region(self):
    doc = ContentDocument()
    doc_columns = 40
    doc_rows = 19
    doc.set_cell_resolution(CellResolutionType(rows=doc_rows, columns=doc_columns))

    safe_area_x_offset = 4
    safe_area_y_offset = 2

    caption_paragraph = SccCaptionParagraph(safe_area_x_offset, safe_area_y_offset)
    caption_paragraph.set_cursor_at(4, 7)
    caption_paragraph.new_caption_text()

    caption_paragraph.get_current_text().append("A 20-char long line.")

    origin = caption_paragraph.get_origin()
    self.assertEqual(11, origin.x.value)
    self.assertEqual(5, origin.y.value)

    extent = caption_paragraph.get_extent()
    self.assertEqual(20, extent.width.value)
    self.assertEqual(1, extent.height.value)

    paragraph_region = _SccParagraphRegion(caption_paragraph, doc)

    self.assertIsNone(paragraph_region._find_matching_region())
    region = paragraph_region._create_matching_region()

    self.assertEqual("region1", region.get_id())
    self.assertTrue(paragraph_region._has_same_origin_as_region(region))
    self.assertEqual(region, paragraph_region._find_matching_region())

    self.assertEqual(ShowBackgroundType.whenActive, region.get_style(StyleProperties.ShowBackground))

    region_extent = region.get_style(StyleProperties.Extent)

    self.assertEqual(50, region_extent.width.value)
    self.assertEqual(63, region_extent.height.value)

    caption_paragraph.set_cursor_at(5, 7)
    caption_paragraph.new_caption_text()
    caption_paragraph.get_current_text().append("This is another 34-char long line.")

    origin = caption_paragraph.get_origin()
    self.assertEqual(11, origin.x.value)
    self.assertEqual(5, origin.y.value)

    extent = caption_paragraph.get_extent()
    self.assertEqual(34, extent.width.value)
    self.assertEqual(2, extent.height.value)

    paragraph_region = _SccParagraphRegion(caption_paragraph, doc)

    self.assertEqual(region, paragraph_region._find_matching_region())
    paragraph_region._extend_region_to_paragraph(region)
    self.assertTrue(paragraph_region._has_same_origin_as_region(region))

    region_extent = region.get_style(StyleProperties.Extent)

    self.assertEqual(62, region_extent.width.value)
    self.assertEqual(63, region_extent.height.value)


if __name__ == '__main__':
  unittest.main()
