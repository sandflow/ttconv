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

"""Unit tests for the Time Code"""

# pylint: disable=R0201,C0115,C0116,W0212

from fractions import Fraction
import unittest

from ttconv.time_code import ClockTime


class TimeCodeTest(unittest.TestCase):

  def test_time_code(self):
    seconds = 123.45
    time_code = ClockTime.from_seconds(seconds)
    self.assertEqual("00:02:03.450", str(time_code))
    time_code.set_separator(",")
    self.assertEqual("00:02:03,450", str(time_code))
    self.assertEqual(seconds, time_code.to_seconds())

    seconds = 3723.4567
    time_code = ClockTime.from_seconds(seconds)
    self.assertEqual("01:02:03.457", str(time_code))
    time_code.set_separator(",")
    self.assertEqual("01:02:03,457", str(time_code))
    self.assertAlmostEqual(seconds, time_code.to_seconds(), delta=0.001)

    seconds = Fraction(3600, 4)
    time_code = ClockTime.from_seconds(seconds)
    self.assertEqual("00:15:00.000", str(time_code))
    time_code.set_separator(",")
    self.assertEqual("00:15:00,000", str(time_code))
    self.assertEqual(seconds, time_code.to_seconds())

    one_day_in_seconds = 24 * 3600

    seconds = one_day_in_seconds + 1.500
    time_code = ClockTime.from_seconds(seconds)
    self.assertEqual("24:00:01.500", str(time_code))
    time_code.set_separator(",")
    self.assertEqual("24:00:01,500", str(time_code))
    self.assertEqual(seconds, time_code.to_seconds())

  def test_from_seconds_rounding_up(self):
      seconds = Fraction(41039999,7500)
      time_code = ClockTime.from_seconds(seconds)
      self.assertEqual(time_code.get_hours(), 1)
      self.assertEqual(time_code.get_minutes(), 31)
      self.assertEqual(time_code.get_seconds(), 12)
      self.assertEqual(time_code.get_milliseconds(), 0)


  def test_from_seconds_rounding_down(self):
      seconds = 5471.9994
      time_code = ClockTime.from_seconds(seconds)
      self.assertEqual(time_code.get_hours(), 1)
      self.assertEqual(time_code.get_minutes(), 31)
      self.assertEqual(time_code.get_seconds(), 11)
      self.assertEqual(time_code.get_milliseconds(), 999)

if __name__ == '__main__':
  unittest.main()
