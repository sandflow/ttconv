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

"""Unit tests for the SCC Time Codes"""

# pylint: disable=R0201,C0115,C0116,W0212

from unittest import TestCase

from ttconv.scc.time_codes import SccTimeCode


class SccTimeCodesTest(TestCase):

  def test_parse_non_drop_frame_time_code(self):
    time_code = SccTimeCode.parse("01:02:03:04")
    self.assertEqual(1, time_code.get_hours())
    self.assertEqual(2, time_code.get_minutes())
    self.assertEqual(3, time_code.get_seconds())
    self.assertEqual(4, time_code.get_frames())
    self.assertFalse(time_code.is_drop_frame())
    self.assertEqual(111694, int(time_code._get_frames()))
    self.assertAlmostEqual(3723.133, float(time_code.get_fraction()), delta=0.001)

  def test_parse_drop_frame_time_code(self):
    time_code = SccTimeCode.parse("01:02:03;04")
    self.assertEqual(1, time_code.get_hours())
    self.assertEqual(2, time_code.get_minutes())
    self.assertEqual(3, time_code.get_seconds())
    self.assertEqual(4, time_code.get_frames())
    self.assertTrue(time_code.is_drop_frame())
    self.assertEqual(111582, int(time_code._get_frames()))
    self.assertAlmostEqual(3719.414, float(time_code.get_fraction()), delta=0.001)

    time_code = SccTimeCode.parse("01;02;03;04")
    self.assertEqual(1, time_code.get_hours())
    self.assertEqual(2, time_code.get_minutes())
    self.assertEqual(3, time_code.get_seconds())
    self.assertEqual(4, time_code.get_frames())
    self.assertTrue(time_code.is_drop_frame())
    self.assertEqual(111582, int(time_code._get_frames()))
    self.assertAlmostEqual(3719.414, float(time_code.get_fraction()), delta=0.001)

    time_code = SccTimeCode.parse("01:02:03.04")
    self.assertEqual(1, time_code.get_hours())
    self.assertEqual(2, time_code.get_minutes())
    self.assertEqual(3, time_code.get_seconds())
    self.assertEqual(4, time_code.get_frames())
    self.assertTrue(time_code.is_drop_frame())
    self.assertEqual(111582, int(time_code._get_frames()))
    self.assertAlmostEqual(3719.414, float(time_code.get_fraction()), delta=0.001)

    time_code = SccTimeCode.parse("01.02.03.04")
    self.assertEqual(1, time_code.get_hours())
    self.assertEqual(2, time_code.get_minutes())
    self.assertEqual(3, time_code.get_seconds())
    self.assertEqual(4, time_code.get_frames())
    self.assertTrue(time_code.is_drop_frame())
    self.assertEqual(111582, int(time_code._get_frames()))
    self.assertAlmostEqual(3719.414, float(time_code.get_fraction()), delta=0.001)
