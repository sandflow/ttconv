#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) Sandflow Consulting LLC
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


'''Unit tests for ttconv.imsc.validator.style_attributes'''

import unittest

from ttconv.imsc.validator.style_attributes import TextShadow

class TextShadowTest(unittest.TestCase):

  def test_valid_values(self):
    for value in (
      "none",
      "1px 1px",
      "1%  1%",
      "1px 1px 2px red",
      "1px 1px,2px 2px",
      "1px 1px, 2px 2px",
      "1px 1px ,  2px 2px",
      "1px 1px rgb(255,0,0)",
      "1px 1px 2px rgb(255, 0, 0)",
      "1px 1px rgba(255,0,0,128), 2px 2px red",
      " 1px\t1px\n,\r2px 2px ",
    ):
      with self.subTest(value):
        TextShadow.validate(value, None)

  def test_invalid_values(self):
    for value in (
      "",
      "1px",
      "a b",
      "1px 1px,",
      ",1px 1px",
      "1px 1px 2px 3px red",
      "1px 1px -2px",
      "1px 1px rgb(255,0)",
      "1px 1px,,2px 2px",
      "1px 1px rgb(255,0,0",
      "1px 1px rgb(255,(0),0)",
      "1px 1px red)",
      " , ",
    ):
      with self.subTest(value):
        with self.assertRaises(ValueError):
          TextShadow.validate(value, None)

if __name__ == "__main__":
  unittest.main()
