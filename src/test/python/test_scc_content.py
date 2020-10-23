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

"""Unit tests for the SCC elements"""

# pylint: disable=R0201,C0115,C0116,W0212

import unittest

from ttconv.scc.content import SccCaptionText
from ttconv.style_properties import PositionType, LengthType, StyleProperties, NamedColors


class SccCaptionTextTest(unittest.TestCase):

  def test_offsets_and_position(self):
    caption_text = SccCaptionText()

    caption_text.set_x_offset(None)
    caption_text.set_y_offset(None)

    expected = PositionType(LengthType(value=0, units=LengthType.Units.c), LengthType(value=0, units=LengthType.Units.c))
    self.assertEqual(expected, caption_text.get_position())

    caption_text.set_x_offset(12)
    caption_text.set_y_offset(8)

    expected = PositionType(LengthType(value=12, units=LengthType.Units.c), LengthType(value=8, units=LengthType.Units.c))
    self.assertEqual(expected, caption_text.get_position())

    other_caption_text = SccCaptionText()
    other_caption_text.set_x_offset(12)
    other_caption_text.set_y_offset(8)

    self.assertTrue(caption_text.has_same_origin(other_caption_text))
    self.assertFalse(caption_text.is_contiguous(other_caption_text))

    caption_text.set_y_offset(9)
    self.assertFalse(caption_text.has_same_origin(other_caption_text))
    self.assertTrue(caption_text.is_contiguous(other_caption_text))

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
