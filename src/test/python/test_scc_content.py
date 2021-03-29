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

"""Unit tests for the SCC content"""

# pylint: disable=R0201,C0115,C0116,W0212

import unittest

from ttconv.scc.content import SccCaptionText, SccCaptionLine
from ttconv.style_properties import StyleProperties, NamedColors


class SccCaptionLineTest(unittest.TestCase):

  def test_line(self):
    row = 6
    indent = 2
    caption_line = SccCaptionLine(row, indent)

    self.assertEqual(row, caption_line.get_row())
    self.assertEqual(indent, caption_line.get_indent())

    caption_line.set_row(7)
    caption_line.indent(2)

    self.assertEqual(7, caption_line.get_row())
    self.assertEqual(4, caption_line.get_indent())

    self.assertIsNone(caption_line.get_current_text())
    self.assertEqual(0, caption_line.get_cursor())
    self.assertEqual(0, caption_line.get_length())
    self.assertTrue(caption_line.is_empty())
    self.assertListEqual([], caption_line.get_texts())

    caption_line.set_cursor(10)
    self.assertEqual(0, caption_line.get_cursor())

    caption_line.add_text("Hello ")
    caption_text = caption_line.get_current_text()

    self.assertIsNotNone(caption_text)
    self.assertEqual("Hello ", caption_text.get_text())
    self.assertEqual(6, caption_text.get_cursor())
    self.assertEqual(6, caption_text.get_length())

    self.assertEqual(6, caption_line.get_cursor())
    self.assertEqual(6, caption_line.get_length())
    self.assertListEqual([caption_text], caption_line.get_texts())

    another_caption_text = SccCaptionText()
    another_caption_text.append("World!")

    caption_line.add_text(another_caption_text)

    self.assertEqual(another_caption_text, caption_line.get_current_text())
    self.assertEqual("World!", another_caption_text.get_text())
    self.assertEqual(6, another_caption_text.get_cursor())
    self.assertEqual(6, another_caption_text.get_length())

    self.assertEqual(12, caption_line.get_cursor())
    self.assertEqual(12, caption_line.get_length())
    self.assertListEqual([caption_text, another_caption_text], caption_line.get_texts())

    caption_line.set_cursor(6)
    self.assertEqual(another_caption_text, caption_line.get_current_text())

    caption_line.add_text("hello")

    self.assertEqual("hello!", another_caption_text.get_text())
    self.assertEqual(5, another_caption_text.get_cursor())
    self.assertEqual(6, another_caption_text.get_length())

    self.assertEqual(11, caption_line.get_cursor())
    self.assertEqual(12, caption_line.get_length())
    self.assertListEqual([caption_text, another_caption_text], caption_line.get_texts())

    caption_line.set_cursor(5)
    self.assertEqual(caption_text, caption_line.get_current_text())
    self.assertEqual(5, caption_text.get_cursor())

    caption_line.add_text(", abcd")

    self.assertEqual("Hello,", caption_text.get_text())
    self.assertEqual(6, caption_text.get_cursor())
    self.assertEqual(6, caption_text.get_length())

    self.assertEqual(another_caption_text, caption_line.get_current_text())
    self.assertEqual(" abcd!", another_caption_text.get_text())
    self.assertEqual(5, another_caption_text.get_cursor())
    self.assertEqual(6, another_caption_text.get_length())

    self.assertEqual(11, caption_line.get_cursor())
    self.assertEqual(12, caption_line.get_length())
    self.assertListEqual([caption_text, another_caption_text], caption_line.get_texts())

    caption_line.set_cursor(7)
    self.assertEqual(another_caption_text, caption_line.get_current_text())
    self.assertEqual(1, another_caption_text.get_cursor())

    caption_line.add_text("123456789")

    self.assertEqual(another_caption_text, caption_line.get_current_text())
    self.assertEqual(" 123456789", another_caption_text.get_text())
    self.assertEqual(10, another_caption_text.get_cursor())
    self.assertEqual(10, another_caption_text.get_length())

    self.assertEqual(16, caption_line.get_cursor())
    self.assertEqual(16, caption_line.get_length())
    self.assertListEqual([caption_text, another_caption_text], caption_line.get_texts())


class SccCaptionTextTest(unittest.TestCase):

  def test_text_insertion(self):
    caption_text = SccCaptionText()
    self.assertEqual(0, caption_text.get_cursor())
    caption_text.append("Lorem ")
    self.assertEqual(6, caption_text.get_cursor())
    self.assertEqual("Lorem ", caption_text.get_text())

    caption_text.append("ipsum")
    self.assertEqual(11, caption_text.get_cursor())
    self.assertEqual("Lorem ipsum", caption_text.get_text())

    caption_text.set_cursor_at(0)
    self.assertEqual(0, caption_text.get_cursor())
    self.assertEqual("Lorem ipsum", caption_text.get_text())

    caption_text.append("Hello")
    self.assertEqual(5, caption_text.get_cursor())
    self.assertEqual("Hello ipsum", caption_text.get_text())

    caption_text.set_cursor_at(6)
    caption_text.append("World!")
    self.assertEqual(12, caption_text.get_cursor())
    self.assertEqual("Hello World!", caption_text.get_text())

    caption_text.set_cursor_at(5)
    caption_text.append("! Abc")
    self.assertEqual(10, caption_text.get_cursor())
    self.assertEqual("Hello! Abcd!", caption_text.get_text())

  def test_style_properties(self):
    caption_text = SccCaptionText()

    caption_text.add_style_property(StyleProperties.Color, None)
    self.assertEqual(0, len(caption_text.get_style_properties()))

    caption_text.add_style_property(StyleProperties.Color, NamedColors.fuchsia.value)
    self.assertEqual(1, len(caption_text.get_style_properties()))
    self.assertEqual(NamedColors.fuchsia.value, caption_text.get_style_properties()[StyleProperties.Color])

    other_caption_text = SccCaptionText()
    self.assertFalse(caption_text.has_same_style_properties(other_caption_text))

    other_caption_text.add_style_property(StyleProperties.Color, NamedColors.fuchsia.value)
    self.assertTrue(caption_text.has_same_style_properties(other_caption_text))


if __name__ == '__main__':
  unittest.main()
