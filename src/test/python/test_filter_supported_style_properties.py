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

"""Unit tests for the supported style properties filter"""

# pylint: disable=R0201,C0115,C0116,W0212
from fractions import Fraction
from unittest import TestCase

from ttconv.filters.supported_style_properties import SupportedStylePropertiesFilter
from ttconv.isd import ISD
from ttconv.model import P, ContentDocument, Region, Body, Div, Span, Text
from ttconv.style_properties import StyleProperties, NamedColors, FontStyleType, DirectionType, ExtentType, LengthType


class SupportedStylePropertiesFilterTest(TestCase):

  def test_process_element(self):
    supported_style_properties = SupportedStylePropertiesFilter({
      StyleProperties.Color: [
        NamedColors.red.value
      ],
      StyleProperties.Extent: []
    })

    p = P()
    for style in StyleProperties.ALL:
      p.set_style(style, style.make_initial_value())

    self.assertEqual(len(StyleProperties.ALL), len(p._styles))
    self.assertEqual(StyleProperties.Color.make_initial_value(), p.get_style(StyleProperties.Color))
    self.assertEqual(StyleProperties.Extent.make_initial_value(), p.get_style(StyleProperties.Extent))

    supported_style_properties._process_element(p)

    self.assertIsNone(p.get_style(StyleProperties.Color))
    self.assertEqual(StyleProperties.Extent.make_initial_value(), p.get_style(StyleProperties.Extent))
    self.assertEqual(1, len(p._styles))

    p.set_style(StyleProperties.Color, NamedColors.red.value)

    supported_style_properties._process_element(p)

    self.assertEqual(2, len(p._styles))
    self.assertEqual(NamedColors.red.value, p.get_style(StyleProperties.Color))
    self.assertEqual(StyleProperties.Extent.make_initial_value(), p.get_style(StyleProperties.Extent))

  def test_process_isd(self):
    supported_style_properties = SupportedStylePropertiesFilter({
      StyleProperties.BackgroundColor: [
        NamedColors.red.value
      ],
      StyleProperties.Extent: []
    })

    doc = ContentDocument()

    r1 = Region("r1", doc)
    r1.set_style(StyleProperties.BackgroundColor, NamedColors.red.value)
    r1.set_style(StyleProperties.LuminanceGain, 2.0)
    doc.put_region(r1)

    b = Body(doc)
    b.set_begin(Fraction(1))
    b.set_end(Fraction(10))
    doc.set_body(b)

    div1 = Div(doc)
    div1.set_region(r1)
    b.push_child(div1)

    p1 = P(doc)
    p1.set_style(StyleProperties.BackgroundColor, NamedColors.white.value)
    p1.set_style(StyleProperties.Direction, DirectionType.rtl)
    div1.push_child(p1)

    span1 = Span(doc)
    span1.set_style(StyleProperties.BackgroundColor, NamedColors.red.value)
    span1.set_style(StyleProperties.FontStyle, FontStyleType.italic)
    span1.set_style(StyleProperties.Direction, DirectionType.ltr)
    p1.push_child(span1)

    t1 = Text(doc, "hello")
    span1.push_child(t1)

    significant_times = sorted(ISD.significant_times(doc))
    self.assertEqual(3, len(significant_times))

    isd = ISD.from_model(doc, significant_times[1])

    r1 = isd.get_region("r1")

    self.assertEqual(len(Region._applicableStyles), len(r1._styles))
    self.assertEqual(NamedColors.red.value, r1.get_style(StyleProperties.BackgroundColor))
    self.assertEqual(2.0, r1.get_style(StyleProperties.LuminanceGain))

    body1 = list(r1)[0]
    div1 = list(body1)[0]
    p1 = list(div1)[0]
    span1 = list(p1)[0]

    self.assertEqual(len(P._applicableStyles), len(p1._styles))
    self.assertEqual(NamedColors.white.value, p1.get_style(StyleProperties.BackgroundColor))
    self.assertEqual(DirectionType.rtl, p1.get_style(StyleProperties.Direction))

    self.assertEqual(len(Span._applicableStyles), len(span1._styles))
    self.assertEqual(NamedColors.red.value, span1.get_style(StyleProperties.BackgroundColor))
    self.assertEqual(FontStyleType.italic, span1.get_style(StyleProperties.FontStyle))
    self.assertEqual(DirectionType.ltr, span1.get_style(StyleProperties.Direction))

    supported_style_properties.process(isd)

    self.assertEqual(2, len(r1._styles))
    self.assertEqual(NamedColors.red.value, r1.get_style(StyleProperties.BackgroundColor))
    self.assertEqual(ExtentType(
      height=LengthType(value=0.0, units=LengthType.Units.rh),
      width=LengthType(value=0.0, units=LengthType.Units.rw)
    ), r1.get_style(StyleProperties.Extent))

    self.assertEqual(0, len(p1._styles))
    self.assertIsNone(p1.get_style(StyleProperties.BackgroundColor))
    self.assertIsNone(p1.get_style(StyleProperties.Direction))

    self.assertEqual(1, len(span1._styles))
    self.assertEqual(NamedColors.red.value, span1.get_style(StyleProperties.BackgroundColor))
    self.assertIsNone(span1.get_style(StyleProperties.FontStyle))
    self.assertIsNone(span1.get_style(StyleProperties.Direction))
