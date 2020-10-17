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

'''Unit tests for the IMSC \\<time-expression\\> parser'''

# pylint: disable=R0201,C0115,C0116

import unittest
from fractions import Fraction
from ttconv.imsc.utils import parse_time_expression

class IMSCTimeExpressionsTest(unittest.TestCase):

  tests = [
    ("1.2s", Fraction(24000, 1001), 60, Fraction(12, 10)),
    ("1.2m", Fraction(24000, 1001), 60, Fraction(72)),
    ("1.2h", Fraction(24000, 1001), 60, Fraction(4320)),
    ("24f", Fraction(24000, 1001), 60, Fraction(1001, 1000)),
    ("120t", Fraction(24000, 1001), 60, Fraction(2)),
    ("01:02:03", Fraction(24000, 1001), 60, Fraction(3723)),
    ("01:02:03.235", Fraction(24000, 1001), 60, Fraction(3723235, 1000)),
    ("01:02:03.2350", Fraction(24000, 1001), 60, Fraction(3723235, 1000)),
    ("01:02:03:20", Fraction(24000, 1001), 60, Fraction(3723) + 20/Fraction(24000, 1001)),
    ("100:00:00.1", Fraction(24000, 1001), 60, 360000 + Fraction(1, 10)),
    ("100:00:00:10", Fraction(24000, 1001), 60, 360000 + 10/Fraction(24000, 1001))
  ]

  def test_timing_expressions(self):
    for test in self.tests:
      with self.subTest(test[0]):
        c = parse_time_expression(test[2], test[1], test[0])
        self.assertEqual(c, test[3])
        self.assertTrue(isinstance(c, Fraction))

  def test_bad_frame_count(self):
    with self.assertRaises(ValueError):
      parse_time_expression(None, 24, "100:00:00:100")

  def test_bad_syntax(self):
    with self.assertRaises(ValueError):
      parse_time_expression(60, 24, "100:00:00;01")


if __name__ == '__main__':
  unittest.main()
