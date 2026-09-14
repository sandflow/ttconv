#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2026, Sandflow Consulting LLC
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

'''Unit tests for merge_to_rollup document filter'''

# pylint: disable=R0201,C0115,C0116

import io
import unittest
import xml.etree.ElementTree as et
from fractions import Fraction

import ttconv.imsc.reader as imsc_reader
from ttconv.filters.doc.merge_to_rollup import MergeToRollUpDocFilter, MergeToRollUpDocFilterConfig
import ttconv.model as model
import ttconv.style_properties as styles


def _make_p(doc, begin, end, text, color=None):
  p = model.P(doc)
  p.set_begin(begin)
  p.set_end(end)
  if color is not None:
    p.set_style(styles.StyleProperties.Color, color)
  span = model.Span(doc)
  span.push_child(model.Text(doc, text))
  p.push_child(span)
  return p


class MergeToRollUpFilterTests(unittest.TestCase):

  def test_merges_paragraphs_separated_by_less_than_a_frame(self):
    doc = model.ContentDocument()
    body = model.Body(doc)
    doc.set_body(body)
    div = model.Div(doc)
    body.push_child(div)

    white = styles.NamedColors.white.value

    p1 = _make_p(doc, Fraction(0), Fraction(1), "line1", white)
    p2 = _make_p(doc, Fraction(1) + Fraction(1, 60), Fraction(2), "line2", white)

    div.push_child(p1)
    div.push_child(p2)

    MergeToRollUpDocFilter(MergeToRollUpDocFilterConfig(max_gap=Fraction(1, 30))).process(doc)

    paragraphs = [c for c in div if isinstance(c, model.P)]
    self.assertEqual(len(paragraphs), 1)
    self.assertEqual(paragraphs[0].get_begin(), Fraction(0))
    self.assertEqual(paragraphs[0].get_end(), Fraction(2))

    children = list(paragraphs[0])
    self.assertEqual(len(children), 3)
    self.assertIsInstance(children[1], model.Br)

  def test_merges_successive_paragraphs_with_identical_contents(self):
    doc = model.ContentDocument()
    body = model.Body(doc)
    doc.set_body(body)
    div = model.Div(doc)
    body.push_child(div)

    white = styles.NamedColors.white.value

    p1 = _make_p(doc, Fraction(0), Fraction(1), "line1", white)
    p2 = _make_p(doc, Fraction(5), Fraction(6), "line1", white)

    div.push_child(p1)
    div.push_child(p2)

    MergeToRollUpDocFilter(MergeToRollUpDocFilterConfig()).process(doc)

    paragraphs = [c for c in div if isinstance(c, model.P)]
    self.assertEqual(len(paragraphs), 1)
    self.assertEqual(paragraphs[0].get_begin(), Fraction(0))
    self.assertEqual(paragraphs[0].get_end(), Fraction(6))

    children = list(paragraphs[0])
    self.assertEqual(len(children), 1)

  def test_does_not_merge_paragraphs_separated_by_a_large_gap(self):
    doc = model.ContentDocument()
    body = model.Body(doc)
    doc.set_body(body)
    div = model.Div(doc)
    body.push_child(div)

    white = styles.NamedColors.white.value

    p1 = _make_p(doc, Fraction(0), Fraction(1), "line1", white)
    p2 = _make_p(doc, Fraction(2), Fraction(3), "line2", white)

    div.push_child(p1)
    div.push_child(p2)

    MergeToRollUpDocFilter(MergeToRollUpDocFilterConfig()).process(doc)

    paragraphs = [c for c in div if isinstance(c, model.P)]
    self.assertEqual(len(paragraphs), 2)

  def test_merges_ttml_paragraphs_with_identical_contents(self):
    tree = et.parse(io.StringIO('''<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:contentProfiles="http://www.w3.org/ns/ttml/profile/imsc1.1/text">
    <head>
        <layout>
            <region xml:id="r1"/>
        </layout>
    </head>
    <body region="r1">
        <div>
            <p begin="0s" end="1s">Hello</p>
            <p begin="5s" end="6s">Hello</p>
        </div>
    </body>
</tt>
'''))
    doc = imsc_reader.to_model(tree)
    self.assertIsNotNone(doc)

    MergeToRollUpDocFilter(MergeToRollUpDocFilterConfig()).process(doc)

    paragraphs = [e for e in doc.get_body().dfs_iterator() if isinstance(e, model.P)]
    self.assertEqual(len(paragraphs), 1)
    self.assertEqual(paragraphs[0].get_begin(), Fraction(0))
    self.assertEqual(paragraphs[0].get_end(), Fraction(6))

  def test_does_not_merge_ttml_paragraphs_with_different_contents(self):
    tree = et.parse(io.StringIO('''<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:contentProfiles="http://www.w3.org/ns/ttml/profile/imsc1.1/text">
    <head>
        <layout>
            <region xml:id="r1"/>
        </layout>
    </head>
    <body region="r1">
        <div>
            <p begin="0s" end="1s">Hello</p>
            <p begin="5s" end="6s">World</p>
        </div>
    </body>
</tt>
'''))
    doc = imsc_reader.to_model(tree)
    self.assertIsNotNone(doc)

    MergeToRollUpDocFilter(MergeToRollUpDocFilterConfig()).process(doc)

    paragraphs = [e for e in doc.get_body().dfs_iterator() if isinstance(e, model.P)]
    self.assertEqual(len(paragraphs), 2)
    self.assertEqual(paragraphs[0].get_begin(), Fraction(0))
    self.assertEqual(paragraphs[0].get_end(), Fraction(1))
    self.assertEqual(paragraphs[1].get_begin(), Fraction(5))
    self.assertEqual(paragraphs[1].get_end(), Fraction(6))

  def test_does_not_merge_paragraphs_with_different_regions(self):
    doc = model.ContentDocument()
    body = model.Body(doc)
    doc.set_body(body)
    div = model.Div(doc)
    body.push_child(div)

    region1 = model.Region("region1", doc)
    region2 = model.Region("region2", doc)
    doc.put_region(region1)
    doc.put_region(region2)

    white = styles.NamedColors.white.value

    p1 = _make_p(doc, Fraction(0), Fraction(1), "line1", white)
    p1.set_region(region1)
    p2 = _make_p(doc, Fraction(1) + Fraction(1, 60), Fraction(2), "line2", white)
    p2.set_region(region2)

    div.push_child(p1)
    div.push_child(p2)

    MergeToRollUpDocFilter(MergeToRollUpDocFilterConfig()).process(doc)

    paragraphs = [c for c in div if isinstance(c, model.P)]
    self.assertEqual(len(paragraphs), 2)
    self.assertIs(paragraphs[0].get_region(), region1)
    self.assertIs(paragraphs[1].get_region(), region2)

  def test_normalizes_p_with_none_begin_to_zero(self):
    doc = model.ContentDocument()
    body = model.Body(doc)
    doc.set_body(body)
    div = model.Div(doc)
    body.push_child(div)

    p1 = _make_p(doc, None, Fraction(1), "line1")
    div.push_child(p1)

    MergeToRollUpDocFilter(MergeToRollUpDocFilterConfig()).process(doc)

    paragraphs = [c for c in div if isinstance(c, model.P)]
    self.assertEqual(len(paragraphs), 1)
    self.assertEqual(paragraphs[0].get_begin(), Fraction(0))

  def test_raises_on_p_with_none_end(self):
    doc = model.ContentDocument()
    body = model.Body(doc)
    doc.set_body(body)
    div = model.Div(doc)
    body.push_child(div)

    p1 = _make_p(doc, Fraction(0), None, "line1")
    div.push_child(p1)

    with self.assertRaises(ValueError):
      MergeToRollUpDocFilter(MergeToRollUpDocFilterConfig()).process(doc)

  def test_raises_on_non_p_element_with_begin(self):
    doc = model.ContentDocument()
    body = model.Body(doc)
    doc.set_body(body)
    div = model.Div(doc)
    div.set_begin(Fraction(0))
    body.push_child(div)

    with self.assertRaises(ValueError):
      MergeToRollUpDocFilter(MergeToRollUpDocFilterConfig()).process(doc)

  def test_raises_on_overlapping_paragraphs(self):
    doc = model.ContentDocument()
    body = model.Body(doc)
    doc.set_body(body)
    div = model.Div(doc)
    body.push_child(div)

    p1 = _make_p(doc, Fraction(0), Fraction(2), "line1")
    p2 = _make_p(doc, Fraction(1), Fraction(3), "line2")
    div.push_child(p1)
    div.push_child(p2)

    with self.assertRaises(ValueError):
      MergeToRollUpDocFilter(MergeToRollUpDocFilterConfig()).process(doc)


if __name__ == '__main__':
  unittest.main()
