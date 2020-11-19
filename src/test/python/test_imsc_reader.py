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

'''Unit tests for the IMSC reader'''

# pylint: disable=R0201,C0115,C0116

import unittest
import xml.etree.ElementTree as et
import os
import logging
from fractions import Fraction
import ttconv.model as model
import ttconv.style_properties as styles
import ttconv.imsc.reader as imsc_reader
import ttconv.imsc.namespaces as xml_ns

class IMSCReaderTest(unittest.TestCase):

  def setUp(self):
    et.register_namespace("ttml", xml_ns.TTML)
    et.register_namespace("ttp", xml_ns.TTP)
    et.register_namespace("tts", xml_ns.TTS)
    et.register_namespace("ittp", xml_ns.ITTP)
    et.register_namespace("itts", xml_ns.ITTS)

  def test_reader_tt_element_not_root_element(self):

    xml_str = """<?xml version="1.0" encoding="UTF-8"?>
      <not_tt xml:lang="en"
          xmlns="http://www.w3.org/ns/ttml"
          xmlns:ttm="http://www.w3.org/ns/ttml#metadata" 
          xmlns:tts="http://www.w3.org/ns/ttml#styling"
          xmlns:ttp="http://www.w3.org/ns/ttml#parameter" 
          xmlns:ittp="http://www.w3.org/ns/ttml/profile/imsc1#parameter"
          ittp:activeArea="50% 50% 80% 80%"
          tts:extent="640px 480px"
          ttp:profile="http://www.w3.org/ns/ttml/profile/imsc1/text">
      </not_tt>"""

    tt_not_root = et.ElementTree(et.fromstring(xml_str))
    self.assertIsNone(imsc_reader.to_model(tt_not_root))

  def test_body_only(self):
    tree = et.parse('src/test/resources/ttml/body_only.ttml')
    imsc_reader.to_model(tree)

  def test_basic_time_containment_001(self):
    tree = et.parse('src/test/resources/ttml/imsc-tests/imsc1/ttml/timing/BasicTimeContainment001.ttml')
    doc = imsc_reader.to_model(tree)

    body = doc.get_body()

    self.assertIsNone(body.get_begin())
    self.assertEqual(body.get_end(), Fraction(10))

    div = list(body)[0]

    self.assertIsNone(div.get_begin())
    self.assertEqual(div.get_end(), Fraction(10))

    p = list(div)[0]

    self.assertIsNone(p.get_begin())
    self.assertIsNone(p.get_end())

    span_children = [v for v in list(p) if len(list(v)[0].get_text().strip()) > 0]

    self.assertIsNone(span_children[0].get_begin())
    self.assertEqual(span_children[0].get_end(), Fraction(5))

    self.assertIsNone(span_children[1].get_begin())
    self.assertEqual(span_children[1].get_end(), Fraction(10))

  def test_basic_time_containment_002(self):
    tree = et.parse('src/test/resources/ttml/imsc-tests/imsc1/ttml/timing/BasicTimeContainment002.ttml')
    doc = imsc_reader.to_model(tree)

    body = doc.get_body()

    self.assertIsNone(body.get_begin())
    self.assertEqual(body.get_end(), Fraction(20))

    div = list(body)[0]

    self.assertIsNone(div.get_begin())
    self.assertEqual(div.get_end(), Fraction(20))

    p_children = [v for v in list(div) if isinstance(v, model.P)]

    self.assertIsNone(p_children[0].get_begin())
    self.assertEqual(p_children[0].get_end(), Fraction(10))

    self.assertEqual(p_children[1].get_begin(), Fraction(10))
    self.assertEqual(p_children[1].get_end(), Fraction(20))

  def test_basic_time_containment_003(self):
    tree = et.parse('src/test/resources/ttml/imsc-tests/imsc1/ttml/timing/BasicTimeContainment003.ttml')
    doc = imsc_reader.to_model(tree)

    body = doc.get_body()

    self.assertIsNone(body.get_begin())
    self.assertEqual(body.get_end(), Fraction(10))

    div = list(body)[0]

    self.assertIsNone(div.get_begin())
    self.assertEqual(div.get_end(), Fraction(10))

    p_children = [v for v in list(div) if isinstance(v, model.P)]

    self.assertIsNone(p_children[0].get_begin())
    self.assertEqual(p_children[0].get_end(), Fraction(10))

    self.assertEqual(p_children[1].get_begin(), Fraction(10))
    self.assertEqual(p_children[1].get_end(), Fraction(20))

    span_children = [v for v in list(p_children[0]) if len(list(v)[0].get_text().strip()) > 0]

    self.assertEqual(span_children[0].get_begin(), Fraction(5))
    self.assertEqual(span_children[0].get_end(), Fraction(10))

    self.assertEqual(span_children[1].get_begin(), Fraction(10))
    self.assertEqual(span_children[1].get_end(), Fraction(15))

  def test_basic_timing_007(self):
    tree = et.parse('src/test/resources/ttml/imsc-tests/imsc1/ttml/timing/BasicTiming007.ttml')
    doc = imsc_reader.to_model(tree)

    body = doc.get_body()

    self.assertIsNone(body.get_begin())
    self.assertEqual(body.get_end(), Fraction(20))

    div = list(body)[0]

    self.assertIsNone(div.get_begin())
    self.assertEqual(div.get_end(), Fraction(20))

    p = list(div)[0]

    self.assertEqual(p.get_begin(), 5)
    self.assertEqual(p.get_end(), 20)

    span_children = [v for v in list(p) if isinstance(v, model.Span)]

    self.assertEqual(len(span_children), 1)

    self.assertEqual(span_children[0].get_begin(), None)
    self.assertEqual(span_children[0].get_end(), Fraction(10))

  def test_imsc_1_test_suite(self):
    for root, _subdirs, files in os.walk("src/test/resources/ttml/imsc-tests/imsc1/ttml"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".ttml":
          with self.subTest(name), self.assertLogs() as logs:
            logging.getLogger().info("*****dummy*****") # dummy log
            tree = et.parse(os.path.join(root, filename))
            self.assertIsNotNone(imsc_reader.to_model(tree))
            if len(logs.output) > 1:
              self.fail(logs.output)

  def test_imsc_1_1_test_suite(self):
    for root, _subdirs, files in os.walk("src/test/resources/ttml/imsc-tests/imsc1_1/ttml"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".ttml":
          with self.subTest(name):
            tree = et.parse(os.path.join(root, filename))
            self.assertIsNotNone(imsc_reader.to_model(tree))

  def test_referential_styling(self):
    tree = et.parse('src/test/resources/ttml/referential_styling.ttml')
    doc = imsc_reader.to_model(tree)

    divs = list(doc.get_body())

    self.assertEqual(divs[0].get_style(styles.StyleProperties.Color), styles.NamedColors.green.value)
    self.assertEqual(divs[0].get_style(styles.StyleProperties.BackgroundColor), styles.NamedColors.blue.value)

    self.assertEqual(divs[1].get_style(styles.StyleProperties.Color), styles.NamedColors.black.value)
    self.assertEqual(divs[1].get_style(styles.StyleProperties.BackgroundColor), styles.NamedColors.blue.value)

    regions = list(doc.iter_regions())

    self.assertEqual(regions[0].get_style(styles.StyleProperties.Color), styles.NamedColors.blue.value)
    self.assertEqual(regions[0].get_style(styles.StyleProperties.BackgroundColor), styles.NamedColors.yellow.value)

    self.assertEqual(regions[1].get_style(styles.StyleProperties.Color), styles.NamedColors.red.value)
    self.assertEqual(regions[1].get_style(styles.StyleProperties.BackgroundColor), styles.NamedColors.yellow.value)
  
  def test_initial(self):
    tree = et.parse('src/test/resources/ttml/imsc-tests/imsc1_1/ttml/initial/initial002.ttml')
    doc = imsc_reader.to_model(tree)

    self.assertEqual(doc.get_initial_value(styles.StyleProperties.Color), styles.NamedColors.green.value)
    self.assertEqual(doc.get_initial_value(styles.StyleProperties.FontStyle), styles.FontStyleType.italic)

  def test_frame_rate(self):
    tree = et.parse('src/test/resources/ttml/imsc-tests/imsc1/ttml/timing/TimeExpressions001.ttml')
    doc = imsc_reader.to_model(tree)

    # <p begin="0s" end="24f">24f = 1.001s</p>
    p = list(list(doc.get_body())[0])[3]

    self.assertEqual(p.get_end(), Fraction(4394201, 1000))

if __name__ == '__main__':
  unittest.main()
