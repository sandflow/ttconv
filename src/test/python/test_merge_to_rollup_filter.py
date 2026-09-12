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

import unittest
from fractions import Fraction

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

    MergeToRollUpDocFilter(MergeToRollUpDocFilterConfig()).process(doc)

    paragraphs = [c for c in div if isinstance(c, model.P)]
    self.assertEqual(len(paragraphs), 1)
    self.assertEqual(paragraphs[0].get_begin(), Fraction(0))
    self.assertEqual(paragraphs[0].get_end(), Fraction(2))

    children = list(paragraphs[0])
    self.assertEqual(len(children), 3)
    self.assertIsInstance(children[1], model.Br)

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


if __name__ == '__main__':
  unittest.main()
