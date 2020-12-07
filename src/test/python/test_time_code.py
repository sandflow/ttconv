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
from unittest import TestCase

from ttconv.time_code import TimeCode


class TimeCodeTest(TestCase):

  def test_time_code(self):
    seconds = 123.45
    time_code = TimeCode.from_seconds(seconds)
    self.assertEqual("00:02:03.450", str(time_code))
    time_code.set_separator(",")
    self.assertEqual("00:02:03,450", str(time_code))
    self.assertEqual(seconds, time_code.to_seconds())

    seconds = 3723.4567
    time_code = TimeCode.from_seconds(seconds)
    self.assertEqual("01:02:03.456", str(time_code))
    time_code.set_separator(",")
    self.assertEqual("01:02:03,456", str(time_code))
    self.assertAlmostEqual(seconds, time_code.to_seconds(), delta=0.001)

    seconds = Fraction(3600, 4)
    time_code = TimeCode.from_seconds(seconds)
    self.assertEqual("00:15:00.000", str(time_code))
    time_code.set_separator(",")
    self.assertEqual("00:15:00,000", str(time_code))
    self.assertEqual(seconds, time_code.to_seconds())

    one_day_in_seconds = 24 * 3600

    seconds = -1.500
    time_code = TimeCode.from_seconds(seconds)
    self.assertEqual("23:59:58.500", str(time_code))
    time_code.set_separator(",")
    self.assertEqual("23:59:58,500", str(time_code))
    self.assertEqual(one_day_in_seconds + seconds, time_code.to_seconds())

    seconds = 1.500
    time_code = TimeCode.from_seconds(one_day_in_seconds + seconds)
    self.assertEqual("00:00:01.500", str(time_code))
    time_code.set_separator(",")
    self.assertEqual("00:00:01,500", str(time_code))
    self.assertEqual(seconds, time_code.to_seconds())
