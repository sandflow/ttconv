#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2023, Sandflow Consulting LLC
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

'''Unit tests for lcd document filter'''

# pylint: disable=R0201,C0115,C0116

import unittest
from ttconv.filters.doc.lcd import LCDFilter, LCDFilterConfig
import ttconv.model as model
import ttconv.style_properties as styles

class LCDFilterTests(unittest.TestCase):

  '''
  <region xml:id="r1"/>
  <region xml:id="r2"/>
  <region xml:id="r2" begin="2s" end="9s">
    <set tts:color="red"/>
  </region>

  <body>
    <div>

    </div>
  </body>
  '''

  def test_region_merging(self):
    doc = model.ContentDocument()

    # r1
    r1 = model.Region("r1", doc)
    doc.put_region(r1)

    # r2: tts:extent="100% 100%"
    r2 = model.Region("r2", doc)
    r2.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        height=styles.LengthType(value=100),
        width=styles.LengthType(value=100)
      )
    )
    doc.put_region(r2)

    # r3: tts:displayAlign="after"
    r3 = model.Region("r3", doc)
    r3.set_style(
      styles.StyleProperties.DisplayAlign,
      styles.DisplayAlignType.after
    )
    doc.put_region(r3)

    # r4: set: tts:displayAlign="after"
    r4 = model.Region("r4", doc)
    r4.add_animation_step(
      model.DiscreteAnimationStep(
        style_property=styles.StyleProperties.DisplayAlign,
        begin=None,
        end=None,
        value=styles.DisplayAlignType.after
      )
    )
    doc.put_region(r4)

    # r5: begin="1s"
    r5 = model.Region("r5", doc)
    r5.set_begin(1)
    doc.put_region(r5)

    # body
    body = model.Body(doc)
    doc.set_body(body)

    # div
    div = model.Div(doc)
    body.push_child(div)

    # p1: r1
    p1 = model.P(doc)
    p1.set_id("p1")
    p1.set_region(r1)
    div.push_child(p1)

    # p2: r2
    p2 = model.P(doc)
    p2.set_id("p2")
    p2.set_region(r2)
    div.push_child(p2)

    # p3: r3
    p3 = model.P(doc)
    p3.set_id("p3")
    p3.set_region(r3)
    div.push_child(p3)

    # p4: r4
    p4 = model.P(doc)
    p4.set_id("p4")
    p4.set_region(r4)
    div.push_child(p4)

    # p5: r5
    p5 = model.P(doc)
    p5.set_id("p5")
    p5.set_region(r5)
    div.push_child(p5)

    filter = LCDFilter(LCDFilterConfig())

    filter.process(doc)

    self.assertSetEqual(
      set(["r1", "r3", "r5"]),
      set([r.get_id() for r in doc.iter_regions()])
    )

  def test_region_resizing(self):
    doc = model.ContentDocument()

    # r1: origin=10,10 extent=80,20
    r1 = model.Region("r1", doc)
    r1.set_style(
      styles.StyleProperties.Origin,
      styles.CoordinateType(
        x=styles.LengthType(value=10),
        y=styles.LengthType(value=10)
      )
    )
    r1.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        height=styles.LengthType(value=20),
        width=styles.LengthType(value=80)
      )
    )
    doc.put_region(r1)

    # r2: origin=10,70 extent=80,20
    r2 = model.Region("r2", doc)
    r2.set_style(
      styles.StyleProperties.Origin,
      styles.CoordinateType(
        x=styles.LengthType(value=10),
        y=styles.LengthType(value=70)
      )
    )
    r2.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        height=styles.LengthType(value=20),
        width=styles.LengthType(value=80)
      )
    )
    doc.put_region(r2)

    # r3: origin=10,10 extent=80,20 displayAlign=after
    r3 = model.Region("r3", doc)
    r3.set_style(
      styles.StyleProperties.Origin,
      styles.CoordinateType(
        x=styles.LengthType(value=10),
        y=styles.LengthType(value=10)
      )
    )
    r3.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        height=styles.LengthType(value=20),
        width=styles.LengthType(value=80)
      )
    )
    r3.set_style(
      styles.StyleProperties.DisplayAlign,
      styles.DisplayAlignType.after
    )
    doc.put_region(r3)

    # r4: origin=10,70 extent=80,20 displayAlign=after
    r4 = model.Region("r4", doc)
    r4.set_style(
      styles.StyleProperties.Origin,
      styles.CoordinateType(
        x=styles.LengthType(value=10),
        y=styles.LengthType(value=70)
      )
    )
    r4.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        height=styles.LengthType(value=20),
        width=styles.LengthType(value=80)
      )
    )
    r4.set_style(
      styles.StyleProperties.DisplayAlign,
      styles.DisplayAlignType.after
    )
    doc.put_region(r4)

    # body
    body = model.Body(doc)
    doc.set_body(body)

    # div
    div = model.Div(doc)
    body.push_child(div)

    # p1: r1
    p1 = model.P(doc)
    p1.set_id("p1")
    p1.set_region(r1)
    div.push_child(p1)

    # p2: r2
    p2 = model.P(doc)
    p2.set_id("p2")
    p2.set_region(r2)
    div.push_child(p2)

    # p3: r3
    p3 = model.P(doc)
    p3.set_id("p3")
    p3.set_region(r3)
    div.push_child(p3)

    # p4: r4
    p4 = model.P(doc)
    p4.set_id("p4")
    p4.set_region(r4)
    div.push_child(p4)

    # apply filter
    filter = LCDFilter(LCDFilterConfig())

    filter.process(doc)

    self.assertSetEqual(
      set(["r1", "r2"]),
      set([r.get_id() for r in doc.iter_regions()])
    )

    self.assertLessEqual(
      doc.get_region("r1").get_style(styles.StyleProperties.Origin).y.value,
      50
    )

    self.assertGreaterEqual(
      doc.get_region("r1").get_style(styles.StyleProperties.Extent).height.value,
      50
    )

    self.assertEqual(
      doc.get_region("r1").get_style(styles.StyleProperties.DisplayAlign),
      styles.DisplayAlignType.before
    )

    self.assertLessEqual(
      doc.get_region("r2").get_style(styles.StyleProperties.Origin).y.value,
      50
    )

    self.assertGreaterEqual(
      doc.get_region("r2").get_style(styles.StyleProperties.Extent).height.value,
      50
    )

    self.assertEqual(
      doc.get_region("r2").get_style(styles.StyleProperties.DisplayAlign),
      styles.DisplayAlignType.after
    )


if __name__ == '__main__':
  unittest.main()
