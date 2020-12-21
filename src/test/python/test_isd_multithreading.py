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

'''Unit tests for white space handling during ISD generation'''

# pylint: disable=R0201,C0115,C0116

import unittest
from ttconv.isd import ISD
import ttconv.model as model
import ttconv.style_properties as styles

class MultithreadingTests(unittest.TestCase):

  def test_large_document(self):
    doc = model.ContentDocument()

    regions = []

    # size of the document in number of p elements
    doc_size = 101

    for i in range(doc_size):
      r = model.Region(f"{i}", doc)
      r.set_style(styles.StyleProperties.ShowBackground, styles.ShowBackgroundType.whenActive)
      doc.put_region(r)
      regions.append(r)

    body = model.Body(doc)
    doc.set_body(body)

    div = model.Div(doc)
    body.push_child(div)

    for i in range(doc_size):
      p = model.P(doc)
      p.set_begin(i)
      p.set_end(i + 1)
      p.set_region(regions[i])
      span = model.Span(doc)
      span.push_child(model.Text(doc, f"Span {i}"))
      p.push_child(span)
      div.push_child(p)

    isds_multi = ISD.generate_isd_sequence(doc)
    isds = ISD.generate_isd_sequence(doc, is_multithreaded=False)

    self.assertEqual(len(isds_multi), len(isds))

    for offset, isd, offset_multi, isd_multi in [(*x, *y) for x, y in zip(isds, isds_multi)]:
      self.assertEqual(offset, offset_multi)
      self.assertEqual(len(isd), len(isd_multi))

      for region1, region2 in zip(isd.iter_regions(), isd_multi.iter_regions()):
        self.assertEqual(region1.get_id(), region2.get_id())

        self.assertEqual(len(region1), len(region2))

        self.assertEqual(region1[0][0][0][0][0].get_text(), region2[0][0][0][0][0].get_text())

if __name__ == '__main__':
  unittest.main()
