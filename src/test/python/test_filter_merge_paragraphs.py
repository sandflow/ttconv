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

"""Unit tests for the regions merging filter"""

# pylint: disable=R0201,C0115,C0116,W0212

from typing import List
from unittest import TestCase

from ttconv.filters.merge_paragraphs import ParagraphsMergingFilter
from ttconv.isd import ISD
from ttconv.model import P, Body, Div, Span, Text, ContentElement, Br


class ParagraphsMergingFilterTest(TestCase):

  @staticmethod
  def _get_filled_body(isd: ISD, *text_contents: List[str]) -> Body:
    body = Body(isd)

    for text_content in text_contents:
      div = Div(isd)
      body.push_child(div)

      for content in text_content:
        text = Text(isd, content)
        span = Span(isd)
        span.push_child(text)

        p = P(isd)
        p.push_child(span)

        div.push_child(p)

    return body

  @staticmethod
  def _get_text_from_children(element: ContentElement) -> str:
    if isinstance(element, Text):
      return element.get_text()

    for child in element:
      return ParagraphsMergingFilterTest._get_text_from_children(child)

  def test_merging_regions(self):
    paragraphs_merging_filter = ParagraphsMergingFilter()

    isd = ISD(None)

    r1 = ISD.Region("r1", isd)
    b1 = self._get_filled_body(isd, ["Hello", "world"], ["Is there", "anyone here?"])
    r1.push_child(b1)

    isd.put_region(r1)

    regions = list(isd.iter_regions())
    self.assertEqual(1, len(regions))

    body = list(regions[0])
    self.assertEqual(1, len(body))

    divs = list(body[0])
    self.assertEqual(2, len(divs))

    paragraphs_1 = list(divs[0])
    self.assertEqual(2, len(paragraphs_1))

    paragraphs_2 = list(divs[1])
    self.assertEqual(2, len(paragraphs_2))

    paragraphs_merging_filter.process(isd)

    regions = list(isd.iter_regions())
    self.assertEqual(1, len(regions))

    body = list(regions[0])
    self.assertEqual(1, len(body))

    divs = list(body[0])
    self.assertEqual(1, len(divs))

    paragraphs = list(divs[0])
    self.assertEqual(1, len(paragraphs))

    spans_and_brs = list(paragraphs[0])

    text = self._get_text_from_children(spans_and_brs[0])
    self.assertEqual("Hello", text)

    self.assertIsInstance(spans_and_brs[1], Br)

    text = self._get_text_from_children(spans_and_brs[2])
    self.assertEqual("world", text)

    self.assertIsInstance(spans_and_brs[3], Br)

    text = self._get_text_from_children(spans_and_brs[4])
    self.assertEqual("Is there", text)

    self.assertIsInstance(spans_and_brs[5], Br)

    text = self._get_text_from_children(spans_and_brs[6])
    self.assertEqual("anyone here?", text)
