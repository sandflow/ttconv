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

from ttconv.model import Document
from ttconv.scc.content import SccCaptionLineBreak
from ttconv.scc.paragraph import SccCaptionParagraph, _SccParagraphRegion
from ttconv.scc.style import SccCaptionStyle
from ttconv.style_properties import StyleProperties


class SccParagraphRegionTest(unittest.TestCase):

  def test_region_prefix(self):
    caption_paragraph = SccCaptionParagraph()
    paragraph_region = _SccParagraphRegion(caption_paragraph)
    self.assertEqual("region", paragraph_region._get_region_prefix())

    caption_paragraph = SccCaptionParagraph(caption_style=SccCaptionStyle.PaintOn)
    paragraph_region = _SccParagraphRegion(caption_paragraph)
    self.assertEqual("paint", paragraph_region._get_region_prefix())

    caption_paragraph = SccCaptionParagraph(caption_style=SccCaptionStyle.PopOn)
    paragraph_region = _SccParagraphRegion(caption_paragraph)
    self.assertEqual("pop", paragraph_region._get_region_prefix())

    caption_paragraph = SccCaptionParagraph(caption_style=SccCaptionStyle.RollUp)
    paragraph_region = _SccParagraphRegion(caption_paragraph)
    self.assertEqual("rollup", paragraph_region._get_region_prefix())

  def test_matching_region(self):
    doc = Document()

    caption_paragraph = SccCaptionParagraph(4, 2)
    caption_paragraph.new_caption_text()

    caption_paragraph.set_row_offset(4)
    caption_paragraph.set_column_offset(4)
    caption_paragraph.apply_current_text_offsets()
    caption_paragraph.indent(3)

    self.assertEqual(6, caption_paragraph.get_current_text().get_y_offset())
    self.assertEqual(11, caption_paragraph.get_current_text().get_x_offset())

    caption_paragraph.get_current_text().append("This is a 28-char long line.")

    origin = caption_paragraph.get_origin()
    self.assertEqual(11, origin.x.value)
    self.assertEqual(6, origin.y.value)

    extent = caption_paragraph.get_extent()
    self.assertEqual(28, extent.width.value)
    self.assertEqual(1, extent.height.value)

    paragraph_region = _SccParagraphRegion(caption_paragraph)

    self.assertIsNone(paragraph_region._find_matching_region(doc))
    region = paragraph_region._create_matching_region(doc)

    self.assertEqual("region1", region.get_id())
    self.assertTrue(paragraph_region._has_same_origin_as_region(region))
    self.assertEqual(region, paragraph_region._find_matching_region(doc))

    region_extent = region.get_style(StyleProperties.Extent)
    self.assertEqual(extent.width.value, region_extent.width.value)
    self.assertEqual(extent.height.value, region_extent.height.value)

    caption_paragraph._caption_contents.append(SccCaptionLineBreak())

    caption_paragraph.new_caption_text()
    caption_paragraph.apply_current_text_offsets()
    caption_paragraph.get_current_text().append("This is another 34-char long line.")

    origin = caption_paragraph.get_origin()
    self.assertEqual(11, origin.x.value)
    self.assertEqual(6, origin.y.value)

    extent = caption_paragraph.get_extent()
    self.assertEqual(34, extent.width.value)
    self.assertEqual(2, extent.height.value)

    paragraph_region = _SccParagraphRegion(caption_paragraph)

    self.assertEqual(region, paragraph_region._find_matching_region(doc))
    paragraph_region._extend_region_to_paragraph(region)
    self.assertTrue(paragraph_region._has_same_origin_as_region(region))

    region_extent = region.get_style(StyleProperties.Extent)
    self.assertEqual(extent.width.value, region_extent.width.value)
    self.assertEqual(extent.height.value, region_extent.height.value)
