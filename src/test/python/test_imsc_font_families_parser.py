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

'''Unit tests for the IMSC \\<fontFamily\\> parser'''

# pylint: disable=R0201,C0115,C0116

import unittest
from ttconv.imsc.utils import parse_font_families, serialize_font_family
import ttconv.style_properties as styles

class IMSCReaderTest(unittest.TestCase):

  _parse_tests = [
    ["default", [styles.GenericFontFamilyType.default]],
    ["'default'", ["default"]],
    ["foo, 'bar good'", ["foo", "bar good"]],
    ['foo, "bar good"', ["foo", "bar good"]],
    [r'foo, "bar \good"', ["foo", "bar good"]],
    [r'foo, "bar \,good"', ["foo", "bar ,good"]],
    [r'foo, "bar,good"', ["foo", "bar,good"]]
  ]

  def test_parse_font_families(self):
    for test in self._parse_tests:
      with self.subTest(test[0]):
        c = parse_font_families(test[0])
        self.assertEqual(c, test[1])


  _serialize_tests = [
    [(styles.GenericFontFamilyType.default,), "default"],
    [("default",), '"default"'],
    [(styles.GenericFontFamilyType.proportionalSansSerif, "bar good"), 'proportionalSansSerif, "bar good"'],
    [("foo", "bar, good"), r'"foo", "bar, good"'],
    [("bar\"good",), r'"bar\"good"']
  ]

  def test_serialize_font_families(self):
    for test in self._serialize_tests:
      with self.subTest(test[0]):
        c = serialize_font_family(test[0])
        self.assertEqual(c, test[1])

if __name__ == '__main__':
  unittest.main()
