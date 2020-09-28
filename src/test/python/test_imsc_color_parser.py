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

'''Unit tests for the IMSC \\<color\\> parser'''

# pylint: disable=R0201,C0115,C0116

import unittest
from ttconv.imsc.utils import parse_color
from ttconv.style_properties import ColorType

class IMSCReaderTest(unittest.TestCase):

  tests = [
    ["#FFFFFF", ColorType([255, 255, 255, 255])],
    ["#FFFFFF7F", ColorType([255, 255, 255, 127])],
    ["rgb(255,128,255)", ColorType([255, 128, 255, 255])],
    ["rgb( 255, 128 ,   255   )", ColorType([255, 128, 255, 255])],
    ["rgba(128,255,255,63)", ColorType([128, 255, 255, 63])],
    ["transparent", ColorType([0, 0, 0, 0])],
    ["black", ColorType([0, 0, 0, 255])],
    ["silver", ColorType([0xc0, 0xc0, 0xc0, 255])],
    ["gray", ColorType([0x80, 0x80, 0x80, 255])],
    ["white", ColorType([255, 255, 255, 255])],
    ["maroon", ColorType([0x80, 0, 0, 255])],
    ["red", ColorType([255, 0, 0, 255])],
    ["purple", ColorType([0x80, 0, 0x80, 255])],
    ["fuchsia", ColorType([255, 0, 255, 255])],
    ["magenta", ColorType([255, 0, 255, 255])],
    ["green", ColorType([0, 0x80, 0, 255])],
    ["lime", ColorType([0, 255, 0, 255])],
    ["olive", ColorType([0x80, 0x80, 0, 255])],
    ["yellow", ColorType([255, 255, 0, 255])],
    ["navy", ColorType([0, 0, 0x80, 255])],
    ["blue", ColorType([0, 0, 255, 255])],
    ["teal", ColorType([0, 0x80, 0x80, 255])],
    ["aqua", ColorType([0, 255, 255, 255])],
    ["cyan", ColorType([0, 255, 255, 255])],
    ["Cyan", ColorType([0, 255, 255, 255])],
    ["CYAN", ColorType([0, 255, 255, 255])],
    ["#FFffFF", ColorType([255, 255, 255, 255])],
    ["#FfFFFF7f", ColorType([255, 255, 255, 127])]
  ]

  def test_bad_color(self):
    with self.assertRaises(ValueError):
      parse_color("#red")

  def test_colors(self):
    for test in self.tests:
      with self.subTest(test[0]):
        c = parse_color(test[0])
        self.assertEqual(c, test[1])

if __name__ == '__main__':
  unittest.main()
