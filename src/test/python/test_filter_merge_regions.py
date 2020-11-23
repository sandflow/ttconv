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

from unittest import TestCase

from ttconv.filters.merge_regions import RegionsMergingFilter
from ttconv.isd import ISD
from ttconv.model import P, Body, Div, Span, Text, ContentElement


class RegionsMergingFilterTest(TestCase):

  @staticmethod
  def _get_filled_body(isd: ISD, text: str) -> Body:
    body = Body(isd)
    text = Text(isd, text)
    span = Span(isd)
    span.push_child(text)

    p = P(isd)
    p.push_child(span)

    div = Div(isd)
    div.push_child(p)

    body.push_child(div)

    return body

  @staticmethod
  def _get_text_from_children(element: ContentElement) -> str:
    if isinstance(element, Text):
      return element.get_text()

    for child in element:
      return RegionsMergingFilterTest._get_text_from_children(child)

  def test_merging_regions(self):
    regions_merging_filter = RegionsMergingFilter()

    isd = ISD(None)

    r1 = ISD.Region("r1", isd)
    b1 = self._get_filled_body(isd, "Hello world")
    r1.push_child(b1)

    r2 = ISD.Region("r2", isd)
    b2 = self._get_filled_body(isd, "Is there anyone here?")
    r2.push_child(b2)

    isd.put_region(r1)
    isd.put_region(r2)

    self.assertEqual(2, len(list(isd.iter_regions())))

    regions_merging_filter.process(isd)

    self.assertEqual(1, len(list(isd.iter_regions())))

    merged_region = isd.get_region("r1_r2")
    self.assertIsNotNone(merged_region)

    body = list(merged_region)
    self.assertEqual(1, len(body))

    divs = list(body[0])
    self.assertEqual(2, len(divs))

    text = self._get_text_from_children(divs[0])
    self.assertEqual("Hello world", text)

    text = self._get_text_from_children(divs[1])
    self.assertEqual("Is there anyone here?", text)
