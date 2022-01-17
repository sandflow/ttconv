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

"""Unit tests for the VTT paragraph"""

# pylint: disable=R0201,C0115,C0116,W0212

from fractions import Fraction
import unittest

from ttconv.vtt.cue import VttCue


class VttCueTest(unittest.TestCase):

  def test_paragraph(self):
    paragraph = VttCue(123)

    self.assertRaisesRegex(ValueError, "VTT paragraph begin time code must be set.", paragraph.to_string)

    paragraph.set_begin(Fraction(1234, 1))
    self.assertEqual("00:20:34.000", str(paragraph.get_begin()))

    self.assertRaisesRegex(ValueError, "VTT paragraph end time code must be set.", paragraph.to_string)

    paragraph.set_end(Fraction(1234, 1))
    self.assertEqual("00:20:34.000", str(paragraph.get_end()))

    self.assertRaisesRegex(ValueError, "VTT paragraph end time code must be greater than the begin time code.", paragraph.to_string)

    paragraph.set_end(Fraction(2345, 1))
    self.assertEqual("00:39:05.000", str(paragraph.get_end()))

    self.assertEqual("123\n00:20:34.000 --> 00:39:05.000\n", str(paragraph))
    self.assertEqual("123\n00:20:34.000 --> 00:39:05.000\n", paragraph.to_string())

    paragraph.append_text("Hello world!")

    self.assertEqual("123\n00:20:34.000 --> 00:39:05.000\nHello world!\n", str(paragraph))
    self.assertEqual("123\n00:20:34.000 --> 00:39:05.000\nHello world!\n", paragraph.to_string())

if __name__ == '__main__':
  unittest.main()
