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

"""Unit tests for the default style properties filter"""

# pylint: disable=R0201,C0115,C0116
from fractions import Fraction
from unittest import TestCase

from ttconv.filters.default_style_properties import DefaultStylePropertiesFilter
from ttconv.isd import ISD
from ttconv.model import P, Document, Region, Body, Div, Span, Text
from ttconv.style_properties import StyleProperties, NamedColors, FontStyleType, TextAlignType, LengthType


class DefaultStylesFilterTest(TestCase):
  style_filter = DefaultStylePropertiesFilter()

  def test_process_element(self):
    p = P()
    for style in StyleProperties.ALL:
      p.set_style(style, style.make_initial_value())

    self.assertEqual(len(StyleProperties.ALL), len(p._styles))

    self.style_filter.process_element(p, {})

    self.assertEqual(0, len(p._styles))

  def test_process_isd(self):
    doc = Document()

    r1 = Region("r1", doc)
    for style in Region._applicableStyles:
      r1.set_style(style, style.make_initial_value())
    r1.set_style(StyleProperties.LuminanceGain, 2.0)
    doc.put_region(r1)

    r2 = Region("r2", doc)
    r2.set_style(StyleProperties.BackgroundColor, NamedColors.red.value)
    r2.set_style(StyleProperties.Color, NamedColors.yellow.value)
    doc.put_region(r2)

    b = Body(doc)
    b.set_begin(Fraction(1))
    b.set_end(Fraction(10))
    doc.set_body(b)

    div1 = Div(doc)
    div1.set_region(r1)
    b.push_child(div1)

    p1 = P(doc)
    div1.push_child(p1)

    span1 = Span(doc)
    span1.set_style(StyleProperties.Color, NamedColors.white.value)
    span1.set_style(StyleProperties.FontStyle, FontStyleType.italic)
    p1.push_child(span1)

    t1 = Text(doc, "hello")
    span1.push_child(t1)

    div2 = Div(doc)
    div2.set_end(Fraction(12))
    div2.set_region(r2)
    b.push_child(div2)

    p2 = P(doc)
    p2.set_style(StyleProperties.BackgroundColor, NamedColors.blue.value)
    p2.set_style(StyleProperties.TextAlign, TextAlignType.center)
    div2.push_child(p2)

    span2 = Span(doc)
    span2.set_style(StyleProperties.Color, NamedColors.white.value)
    p2.push_child(span2)

    t2 = Text(doc, "world")
    span2.push_child(t2)

    significant_times = sorted(ISD.significant_times(doc))
    self.assertTrue(5, len(significant_times))

    isd = ISD.from_model(doc, significant_times[1])

    r1 = isd.get_region("r1")
    r2 = isd.get_region("r2")

    # print("======== BEFORE FILTER =======")
    # isd.print_children()

    self.assertEqual(len(Region._applicableStyles), len(r1._styles))
    self.assertEqual(2.0, r1.get_style(StyleProperties.LuminanceGain))

    self.assertEqual(len(Region._applicableStyles), len(r2._styles))
    self.assertEqual(NamedColors.red.value, r2.get_style(StyleProperties.BackgroundColor))

    body1 = list(r1)[0]
    div1 = list(body1)[0]
    p1 = list(div1)[0]
    span1 = list(p1)[0]

    self.assertEqual(len(P._applicableStyles), len(p1._styles))

    self.assertEqual(len(Span._applicableStyles), len(span1._styles))
    self.assertEqual(NamedColors.white.value, span1.get_style(StyleProperties.Color))
    self.assertEqual(FontStyleType.italic, span1.get_style(StyleProperties.FontStyle))

    body2 = list(r2)[0]
    div2 = list(body2)[0]
    p2 = list(div2)[0]
    span2 = list(p2)[0]

    self.assertEqual(len(P._applicableStyles), len(p2._styles))
    self.assertEqual(NamedColors.blue.value, p2.get_style(StyleProperties.BackgroundColor))
    self.assertEqual(TextAlignType.center, p2.get_style(StyleProperties.TextAlign))

    # print("\n======== FILTER =======")

    self.style_filter.process(isd)

    # print("======== AFTER FILTER =======")
    # isd.print_children()

    self.assertEqual(1, len(r1._styles))
    self.assertEqual(2.0, r1.get_style(StyleProperties.LuminanceGain))

    self.assertEqual(0, len(div1._styles))

    self.assertEqual(1, len(p1._styles))
    # FIXME: Line padding is default and should be filtered
    self.assertEqual(LengthType(value=6.666666666666667, units=LengthType.Units.rh), p2.get_style(StyleProperties.LinePadding))

    self.assertEqual(2, len(span1._styles))
    self.assertEqual(FontStyleType.italic, span1.get_style(StyleProperties.FontStyle))
    # FIXME: Font size is default and should be filtered
    self.assertEqual(LengthType(value=6.666666666666667, units=LengthType.Units.rh), span1.get_style(StyleProperties.FontSize))

    self.assertEqual(1, len(r2._styles))
    self.assertEqual(NamedColors.red.value, r2.get_style(StyleProperties.BackgroundColor))

    self.assertEqual(0, len(div2._styles))

    self.assertEqual(3, len(p2._styles))
    self.assertEqual(NamedColors.blue.value, p2.get_style(StyleProperties.BackgroundColor))
    self.assertEqual(TextAlignType.center, p2.get_style(StyleProperties.TextAlign))
    # FIXME: Line padding is default and should be filtered
    self.assertEqual(LengthType(value=6.666666666666667, units=LengthType.Units.rh), p2.get_style(StyleProperties.LinePadding))

    # FIXME: Font size is default and should be filtered
    self.assertEqual(1, len(span2._styles))
    self.assertEqual(LengthType(value=6.666666666666667, units=LengthType.Units.rh), span2.get_style(StyleProperties.FontSize))
