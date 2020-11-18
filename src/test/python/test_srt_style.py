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

"""Unit tests for the SRT style"""

# pylint: disable=R0201,C0115,C0116,W0212

from unittest import TestCase

from ttconv.model import Span
from ttconv.srt import style
from ttconv.style_properties import StyleProperties, FontWeightType, FontStyleType, TextDecorationType, ColorType, NamedColors


class SrtStyleTest(TestCase):

  def test_style_is_bold(self):
    element = Span()

    self.assertFalse(style.is_element_bold(element))

    element.set_style(StyleProperties.FontWeight, FontWeightType.normal)

    self.assertFalse(style.is_element_bold(element))

    element.set_style(StyleProperties.FontWeight, FontWeightType.bold)

    self.assertTrue(style.is_element_bold(element))

  def test_style_is_italic(self):
    element = Span()

    self.assertFalse(style.is_element_italic(element))

    element.set_style(StyleProperties.FontStyle, FontStyleType.oblique)

    self.assertFalse(style.is_element_italic(element))

    element.set_style(StyleProperties.FontStyle, FontStyleType.normal)

    self.assertFalse(style.is_element_italic(element))

    element.set_style(StyleProperties.FontStyle, FontStyleType.italic)

    self.assertTrue(style.is_element_italic(element))

  def test_style_is_underlined(self):
    element = Span()

    self.assertFalse(style.is_element_underlined(element))

    element.set_style(StyleProperties.TextDecoration, TextDecorationType(line_through=True))

    self.assertFalse(style.is_element_underlined(element))

    element.set_style(StyleProperties.TextDecoration, TextDecorationType(overline=True))

    self.assertFalse(style.is_element_underlined(element))

    element.set_style(StyleProperties.TextDecoration, TextDecorationType(underline=True))

    self.assertTrue(style.is_element_underlined(element))

  def test_style_font_color(self):
    element = Span()

    self.assertIsNone(style.get_font_color(element))

    element.set_style(StyleProperties.Color, None)

    self.assertIsNone(style.get_font_color(element))

    element.set_style(StyleProperties.Color, ColorType((0x12, 0x34, 0x56, 0x78)))

    self.assertEqual("#12345678", style.get_font_color(element))

    element.set_style(StyleProperties.Color, NamedColors.white.value)

    self.assertEqual("#ffffffff", style.get_font_color(element))

    element.set_style(StyleProperties.Color, NamedColors.transparent.value)

    self.assertEqual("#00000000", style.get_font_color(element))
