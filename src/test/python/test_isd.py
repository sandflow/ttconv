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

'''Unit tests for the date model'''

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

class ISDTest(unittest.TestCase):

  '''
  <region xml:id="r1" tts:showBackground="always"/>
  <region xml:id="r2" begin="2s" end="9s">
    <set tts:color="red"/>
  </region>

  <body begin="1s" end="10s">
    <div begin="3s" region="r1">
      <set begin="1s" tts:color="green"/>
    </div>
    <div end="12s" region="r2">
      <p>
        <span>hello</span>
      </p>
    </div>
  </body>
  '''

  def setUp(self):
    self.doc = model.Document()

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
    r1.set_style(styles.StyleProperties.ShowBackground, styles.ShowBackgroundType.always)
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
    self.assertEqual(ISD.significant_times(self.doc), set((0, 2, 3, 9, 1, 10, 4)))

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

    self.assertEqual(span.get_style(styles.StyleProperties.Color), styles.NamedColors.blue.value)

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

if __name__ == '__main__':
  unittest.main()
