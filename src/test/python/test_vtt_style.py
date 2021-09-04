#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2021, Sandflow Consulting LLC
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

"""Unit tests for the VTT style"""

# pylint: disable=R0201,C0115,C0116,W0212

import unittest

from ttconv.model import Span
from ttconv.vtt import style
from ttconv.style_properties import StyleProperties, FontWeightType, FontStyleType, TextDecorationType, ColorType, NamedColors


class VttStyleTest(unittest.TestCase):

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

  def test_style_color(self):
    element = Span()

    self.assertIsNone(style.get_color(element))

    element.set_style(StyleProperties.Color, None)

    self.assertIsNone(style.get_color(element))

    element.set_style(StyleProperties.Color, ColorType((0x12, 0x34, 0x56, 0x78)))

    self.assertEqual("#12345678", style.get_color(element))

    element.set_style(StyleProperties.Color, NamedColors.white.value)

    self.assertEqual("#ffffffff", style.get_color(element))

    element.set_style(StyleProperties.Color, NamedColors.transparent.value)

    self.assertEqual("#00000000", style.get_color(element))

  def test_style_background_color(self):
    element = Span()

    self.assertIsNone(style.get_background_color(element))

    element.set_style(StyleProperties.BackgroundColor, None)

    self.assertIsNone(style.get_background_color(element))

    element.set_style(StyleProperties.BackgroundColor, ColorType((0x12, 0x34, 0x56, 0x78)))

    self.assertEqual("#12345678", style.get_background_color(element))

    element.set_style(StyleProperties.BackgroundColor, NamedColors.white.value)

    self.assertEqual("#ffffffff", style.get_background_color(element))

    element.set_style(StyleProperties.BackgroundColor, NamedColors.transparent.value)

    self.assertEqual("#00000000", style.get_background_color(element))

  def test_style_color_classname(self):
    self.assertEqual("fg_color_00000000", style.get_color_classname("#00000000"))

    self.assertEqual("white", style.get_color_classname("#ffffffff"))

    self.assertEqual("lime", style.get_color_classname("#00ff00ff"))

    self.assertEqual("cyan", style.get_color_classname("#00ffffff"))

    self.assertEqual("red", style.get_color_classname("#ff0000ff"))

    self.assertEqual("yellow", style.get_color_classname("#ffff00ff"))

    self.assertEqual("magenta", style.get_color_classname("#ff00ffff"))

    self.assertEqual("blue", style.get_color_classname("#0000ffff"))

    self.assertEqual("black", style.get_color_classname("#000000ff"))

  def test_style_background_color_classname(self):
    self.assertEqual("bg_color_00000000", style.get_background_color_classname("#00000000"))

    self.assertEqual("bg_white", style.get_background_color_classname("#ffffffff"))

    self.assertEqual("bg_lime", style.get_background_color_classname("#00ff00ff"))

    self.assertEqual("bg_cyan", style.get_background_color_classname("#00ffffff"))

    self.assertEqual("bg_red", style.get_background_color_classname("#ff0000ff"))

    self.assertEqual("bg_yellow", style.get_background_color_classname("#ffff00ff"))

    self.assertEqual("bg_magenta", style.get_background_color_classname("#ff00ffff"))

    self.assertEqual("bg_blue", style.get_background_color_classname("#0000ffff"))

    self.assertEqual("bg_black", style.get_background_color_classname("#000000ff"))

if __name__ == '__main__':
  unittest.main()
