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

'''Unit tests for the data model'''

# pylint: disable=R0201,C0115,C0116

import unittest
import os
import logging
import xml.etree.ElementTree as et
from fractions import Fraction
import ttconv.imsc.reader as imsc_reader
import ttconv.model as model
import ttconv.style_properties as styles
from ttconv.isd import ISD

def _print_isd_node(element, level):
  if isinstance(element, model.Text):
    print('"', element.get_text(), '"')
  else:
    print(" " * 2 * level, element.__class__.__name__)

  for child in element:
    _print_isd_node(child, level + 1)

class ContentDocument0Test(unittest.TestCase):

  '''
  <region xml:id="r1"/>
  <region xml:id="r2" begin="2s" end="9s">
    <set tts:color="red"/>
  </region>

  <body begin="1s" end="10s">
    <div begin="3s" region="r1">
      <set begin="1s" tts:color="green"/>
    </div>
    <div end="12s" region="r2">
      <p>
        <span>
        hello
        </span>
      </p>
    </div>
  </body>
  '''

  def setUp(self):
    self.doc = model.ContentDocument()

    a1 = model.DiscreteAnimationStep(
      style_property=styles.StyleProperties.Color,
      begin=None,
      end=None,
      value=styles.NamedColors.red.value
    )

    a2 = model.DiscreteAnimationStep(
      style_property=styles.StyleProperties.Color,
      begin=Fraction(1),
      end=None,
      value=styles.NamedColors.green.value
    )

    a3 = model.DiscreteAnimationStep(
      style_property=styles.StyleProperties.Color,
      begin=Fraction(2),
      end=None,
      value=styles.NamedColors.blue.value
    )

    r1 = model.Region("r1", self.doc)
    self.doc.put_region(r1)

    # r2: sig times = {2, 9}

    r2 = model.Region("r2", self.doc)
    r2.set_begin(Fraction(2))
    r2.set_end(Fraction(9))
    r2.add_animation_step(a1)
    self.doc.put_region(r2)

    # b: sig times = {1, 10}

    b = model.Body(self.doc)
    b.set_begin(Fraction(1))
    b.set_end(Fraction(10))
    self.doc.set_body(b)

    # div1: offset = 1, sig times = {2, 4}

    div1 = model.Div(self.doc)
    div1.add_animation_step(a2)
    div1.set_begin(Fraction(3))
    div1.set_region(r1)
    b.push_child(div1)

    # div2: offset = 1, sig times = {10}

    div2 = model.Div(self.doc)
    div2.set_end(Fraction(12))
    div2.set_region(r2)
    b.push_child(div2)

    # p1: offset = 1, sig times = {}

    p1 = model.P(self.doc)
    div2.push_child(p1)

    # span1: offset = 1, sig times = {3}
    span1 = model.Span(self.doc)
    span1.add_animation_step(a3)
    p1.push_child(span1)

    t1 = model.Text(self.doc, "hello")
    span1.push_child(t1)

  def test_significant_times(self):
    self.assertSequenceEqual(ISD.significant_times(self.doc), sorted((0, 2, 3, 9, 1, 10, 4)))

  def test_isd_0(self):
    isd = ISD.from_model(self.doc, 0)

    regions = list(isd.iter_regions())

    self.assertEqual(len(regions), 1)

    r1 = regions[0]

    self.assertEqual(r1.get_id(), "r1")

    self.assertEqual(len(r1), 0)

  def test_isd_2(self):
    isd = ISD.from_model(self.doc, 2)

    regions = list(isd.iter_regions())

    self.assertEqual(len(regions), 2)

    r1 = regions[0]

    self.assertEqual(r1.get_id(), "r1")

    self.assertEqual(len(r1), 0)

    r2 = regions[1]

    self.assertEqual(r2.get_id(), "r2")

    r2_children = list(r2)

    self.assertEqual(len(r2_children), 1)

    body = r2_children[0]

    self.assertIsInstance(body, model.Body)

    self.assertEqual(len(body), 1)

    div = list(body)[0]

    self.assertIsInstance(div, model.Div)

    self.assertEqual(len(div), 1)

    p = list(div)[0]

    self.assertIsInstance(p, model.P)

    self.assertEqual(len(p), 1)

    span = list(p)[0]

    self.assertIsInstance(span, model.Span)

    self.assertEqual(len(span), 1)

    text = list(span)[0]

    self.assertIsInstance(text, model.Text)

    self.assertEqual(text.get_text(), "hello")

  def test_isd_10(self):
    isd = ISD.from_model(self.doc, 0)

    regions = list(isd.iter_regions())

    self.assertEqual(len(regions), 1)

    r1 = regions[0]

    self.assertEqual(r1.get_id(), "r1")

    self.assertEqual(len(r1), 0)


class IMSCTestSuiteTest(unittest.TestCase):

  def test_display_none_handling(self):
    xml_doc = et.parse("src/test/resources/ttml/imsc-tests/imsc1/ttml/timing/MediaParTiming002.ttml")
    doc = imsc_reader.to_model(xml_doc)
    isd = ISD.from_model(doc, 0)

    regions = list(isd.iter_regions())

    # single default region

    self.assertEqual(len(regions), 1)

    # no content

    self.assertEqual(len(regions[0]), 0)



  def test_imsc_1_test_suite(self):
    for root, _subdirs, files in os.walk("src/test/resources/ttml/imsc-tests/imsc1/ttml"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".ttml":
          with self.subTest(name), self.assertLogs() as logs:
            logging.getLogger().info("*****dummy*****") # dummy log
            tree = et.parse(os.path.join(root, filename))
            m = imsc_reader.to_model(tree)
            self.assertIsNotNone(m)
            sig_times = ISD.significant_times(m)
            for t in sig_times:
              isd = ISD.from_model(m, t)
              self.assertIsNotNone(isd)
            if len(logs.output) > 1:
              self.fail(logs.output)

  def test_imsc_1_1_test_suite(self):
    for root, _subdirs, files in os.walk("src/test/resources/ttml/imsc-tests/imsc1_1/ttml"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".ttml":
          with self.subTest(name), self.assertLogs() as logs:
            logging.getLogger().info("*****dummy*****") # dummy log
            tree = et.parse(os.path.join(root, filename))
            m = imsc_reader.to_model(tree)
            self.assertIsNotNone(m)
            sig_times = ISD.significant_times(m)
            for t in sig_times:
              isd = ISD.from_model(m, t)
              self.assertIsNotNone(isd)
            if len(logs.output) > 1:
              self.fail(logs.output)

class ComputeStyleTest(unittest.TestCase):

  def test_compute_extent_pct(self):
    doc = model.ContentDocument()

    r1 = model.Region("r1", doc)
    r1.set_style(styles.StyleProperties.ShowBackground, styles.ShowBackgroundType.always)
    r1.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        width=styles.LengthType(50, styles.LengthType.Units.pct),
        height=styles.LengthType(25, styles.LengthType.Units.pct)
      )
    )
    doc.put_region(r1)

    isd = ISD.from_model(doc, 0)

    region = list(isd.iter_regions())[0]

    extent: styles.ExtentType = region.get_style(styles.StyleProperties.Extent)

    self.assertEqual(extent.height.value, 25)
    self.assertEqual(extent.height.units, styles.LengthType.Units.rh)

    self.assertEqual(extent.width.value, 50)
    self.assertEqual(extent.width.units, styles.LengthType.Units.rw)

  def test_compute_extent_px(self):
    doc = model.ContentDocument()

    r1 = model.Region("r1", doc)
    r1.set_style(styles.StyleProperties.ShowBackground, styles.ShowBackgroundType.always)
    r1.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        width=styles.LengthType(50, styles.LengthType.Units.px),
        height=styles.LengthType(25, styles.LengthType.Units.px)
      )
    )
    doc.put_region(r1)

    isd = ISD.from_model(doc, 0)

    region = list(isd.iter_regions())[0]

    extent: styles.ExtentType = region.get_style(styles.StyleProperties.Extent)

    self.assertAlmostEqual(extent.width.value, 100*50/doc.get_px_resolution().width)
    self.assertEqual(extent.width.units, styles.LengthType.Units.rw)

    self.assertAlmostEqual(extent.height.value, 100*25/doc.get_px_resolution().height)
    self.assertEqual(extent.height.units, styles.LengthType.Units.rh)

  @unittest.skip("Removing support for 'c' units other with ebutts:linePadding")
  def test_compute_extent_c(self):
    doc = model.ContentDocument()

    r1 = model.Region("r1", doc)
    r1.set_style(styles.StyleProperties.ShowBackground, styles.ShowBackgroundType.always)
    r1.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        width=styles.LengthType(10, styles.LengthType.Units.c),
        height=styles.LengthType(20, styles.LengthType.Units.c)
      )
    )
    doc.put_region(r1)

    isd = ISD.from_model(doc, 0)

    region = list(isd.iter_regions())[0]

    extent: styles.ExtentType = region.get_style(styles.StyleProperties.Extent)

    self.assertAlmostEqual(extent.width.value, 100*10/doc.get_cell_resolution().columns)
    self.assertEqual(extent.width.units, styles.LengthType.Units.rw)

    self.assertAlmostEqual(extent.height.value, 100*20/doc.get_cell_resolution().rows)
    self.assertEqual(extent.height.units, styles.LengthType.Units.rh)

  def test_compute_extent_em(self):
    doc = model.ContentDocument()

    r1 = model.Region("r1", doc)
    r1.set_style(styles.StyleProperties.ShowBackground, styles.ShowBackgroundType.always)
    with self.assertRaises(ValueError) as _context:
      r1.set_style(
        styles.StyleProperties.Extent,
        styles.ExtentType(
          width=styles.LengthType(20, styles.LengthType.Units.em),
          height=styles.LengthType(3, styles.LengthType.Units.em)
        )
      )

  def test_compute_padding(self):
    doc = model.ContentDocument()

    r1 = model.Region("r1", doc)
    r1.set_style(styles.StyleProperties.ShowBackground, styles.ShowBackgroundType.always)
    r1.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        width=styles.LengthType(50, styles.LengthType.Units.pct),
        height=styles.LengthType(25, styles.LengthType.Units.pct)
      )
    )
    r1.set_style(
      styles.StyleProperties.Padding,
      styles.PaddingType(
        before=styles.LengthType(5, styles.LengthType.Units.pct),
        after=styles.LengthType(10, styles.LengthType.Units.pct),
        start=styles.LengthType(15, styles.LengthType.Units.pct),
        end=styles.LengthType(20, styles.LengthType.Units.pct)
      )
    )
    doc.put_region(r1)

    isd = ISD.from_model(doc, 0)

    region = list(isd.iter_regions())[0]

    padding: styles.PaddingType = region.get_style(styles.StyleProperties.Padding)

    self.assertAlmostEqual(padding.before.value, 25 * 0.05)
    self.assertAlmostEqual(padding.after.value, 25 * 0.10)
    self.assertAlmostEqual(padding.start.value, 50 * 0.15)
    self.assertAlmostEqual(padding.end.value, 50 * 0.2)

  def test_compute_style_property(self):
    doc = model.ContentDocument()

    r1 = model.Region("r1", doc)
    r1.set_style(styles.StyleProperties.FontSize, styles.LengthType(value=50, units=styles.LengthType.Units.pct))
    doc.put_region(r1)

    b = model.Body(doc)
    b.set_style(styles.StyleProperties.FontSize, styles.LengthType(value=50, units=styles.LengthType.Units.pct))
    b.set_region(r1)
    doc.set_body(b)

    div1 = model.Div(doc)
    b.push_child(div1)

    p1 = model.P(doc)
    div1.push_child(p1)

    span1 = model.Span(doc)
    p1.push_child(span1)

    t1 = model.Text(doc, "hello")
    span1.push_child(t1)

    isd = ISD.from_model(doc, 0)

    region = list(isd.iter_regions())[0]

    span = region[0][0][0][0]

    fs: styles.LengthType = span.get_style(styles.StyleProperties.FontSize)

    self.assertAlmostEqual(fs.value, 25 / doc.get_cell_resolution().rows)

    self.assertEqual(fs.units, styles.LengthType.Units.rh)

class InheritanceStyleTest(unittest.TestCase):

  def test_text_decoration_inheritance(self):
    doc = model.ContentDocument()

    r1 = model.Region("r1", doc)
    r1.set_style(
      styles.StyleProperties.TextDecoration,
      styles.TextDecorationType(
        line_through=False,
        underline=True,
        overline=True
      )
    )
    doc.put_region(r1)

    b = model.Body(doc)
    b.set_style(
      styles.StyleProperties.TextDecoration,
      styles.TextDecorationType(
        overline=False
      )
    )
    b.set_region(r1)
    doc.set_body(b)

    div1 = model.Div(doc)
    b.push_child(div1)

    p1 = model.P(doc)
    div1.push_child(p1)

    span1 = model.Span(doc)
    p1.push_child(span1)

    t1 = model.Text(doc, "hello")
    span1.push_child(t1)

    isd = ISD.from_model(doc, 0)

    region = list(isd.iter_regions())[0]

    span = region[0][0][0][0]

    self.assertEqual(
      span.get_style(styles.StyleProperties.TextDecoration),
      styles.TextDecorationType(
        line_through=False,
        underline=True,
        overline=False
      )
    )

  def test_textEmphasis_auto(self):
    """https://github.com/sandflow/ttconv/issues/400"""
    xml_str = """<?xml version="1.0" encoding="utf-8"?>
<tt xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling" xml:lang="en">
<head>
<styling>
<initial tts:writingMode="lrtb"/>
<style xml:id="s1" tts:textEmphasis="auto outside"/>
</styling>
</head>
<body>
<div>
<p begin="0s" end="2s"><span style="s1">hello</span></p>
</div>
</body>
</tt>"""

    tree = et.ElementTree(et.fromstring(xml_str))
    doc = imsc_reader.to_model(tree)
    isd = ISD.from_model(doc, 0)

    regions = list(isd.iter_regions())

    span = regions[0][0][0][0][0]

    self.assertEqual(
      span.get_style(styles.StyleProperties.TextEmphasis).position,
      styles.TextEmphasisType.Position.outside
    )

  def test_direction_special_semantics(self):
    """https://github.com/sandflow/ttconv/issues/400"""
    xml_str = """<?xml version="1.0" encoding="utf-8"?>
<tt xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling" xml:lang="en">
<head>
<layout>
<region xml:id="rl" tts:writingMode="rl"/>
<region xml:id="lr" tts:writingMode="rl" tts:direction="ltr"/>
</layout>
</head>
<body>
<div>
<p region="rl" begin="0s" end="1s">tts:direction should be "rtl".</p>
<p region="lr" begin="0s" end="1s">tts:direction should be "ltr".</p>
</div>
</body>
</tt>"""

    tree = et.ElementTree(et.fromstring(xml_str))
    doc = imsc_reader.to_model(tree)

    p1 = (ISD.from_model(doc, 0).get_region("rl"))[0][0][0][0]

    self.assertEqual(
      p1.get_style(styles.StyleProperties.Direction),
      styles.DirectionType.rtl
    )

    p2 = (ISD.from_model(doc, 0).get_region("lr"))[0][0][0][0]

    self.assertEqual(
      p2.get_style(styles.StyleProperties.Direction),
      styles.DirectionType.ltr
    )

class ContentDocument1Test(unittest.TestCase):

  """
    <region xml:id="r1"/>

    <body region="r1">
      <div>
        <p begin="1s" end="3s">
          <span>
          hello
          </span>
          <span begin="1s">
          bye
          </span>
        </p>
      </div>
    </body>
  """

  def setUp(self):
    self.doc = model.ContentDocument()

    r1 = model.Region("r1", self.doc)
    r1.set_style(styles.StyleProperties.ShowBackground, styles.ShowBackgroundType.whenActive)
    self.doc.put_region(r1)

    b = model.Body(self.doc)
    b.set_region(r1)
    self.doc.set_body(b)

    div1 = model.Div(self.doc)
    b.push_child(div1)

    p1 = model.P(self.doc)
    p1.set_begin(1)
    p1.set_end(3)
    div1.push_child(p1)

    span1 = model.Span(self.doc)
    span1.push_child(model.Text(self.doc, "hello"))
    p1.push_child(span1)

    span2 = model.Span(self.doc)
    span2.set_begin(1)
    span2.push_child(model.Text(self.doc, "bye"))
    p1.push_child(span2)

  def test_sig_times(self):
  
    self.assertSequenceEqual(ISD.significant_times(self.doc), sorted((0, 1, 2, 3)))

  def test_isd_0(self):

    isd = ISD.from_model(self.doc, 0)

    self.assertEqual(len(isd), 0)

  def test_isd_1(self):

    isd = ISD.from_model(self.doc, 1)

    self.assertEqual(len(isd), 1)

    p = list(isd.iter_regions())[0][0][0][0]

    self.assertEqual(len(p), 1)

    self.assertEqual(p[0][0].get_text(), "hello")

  def test_isd_2(self):

    isd = ISD.from_model(self.doc, 2)

    self.assertEqual(len(isd), 1)

    p = list(isd.iter_regions())[0][0][0][0]

    self.assertEqual(len(p), 2)

    self.assertEqual(p[0][0].get_text(), "hello")

    self.assertEqual(p[1][0].get_text(), "bye")

  def test_isd_3(self):

    isd = ISD.from_model(self.doc, 0)

    self.assertEqual(len(isd), 0)


class DefaultRegion(unittest.TestCase):

  def test_default_region(self):

    doc = model.ContentDocument()

    b = model.Body(doc)
    doc.set_body(b)

    div1 = model.Div(doc)
    b.push_child(div1)

    p1 = model.P(doc)
    div1.push_child(p1)

    span1 = model.Span(doc)
    span1.push_child(model.Text(doc, "hello"))
    p1.push_child(span1)

    isd = ISD.from_model(doc, 0)

    self.assertEqual(len(isd), 1)

    regions = list(isd.iter_regions())

    self.assertEqual(regions[0].get_id(), ISD.DEFAULT_REGION_ID)

    p = regions[0][0][0][0]

    self.assertEqual(len(p), 1)

    self.assertEqual(p[0][0].get_text(), "hello")

if __name__ == '__main__':
  unittest.main()
