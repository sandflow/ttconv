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
    self.assertEqual(111694, time_code.get_nb_frames())
    self.assertAlmostEqual(111694 / 30, float(time_code.get_fraction()), delta=0.001)
    self.assertEqual("01:02:03:04", str(time_code))

  def test_parse_drop_frame_time_code(self):
    time_code = SccTimeCode.parse("01:02:03;04")
    self.assertEqual(1, time_code.get_hours())
    self.assertEqual(2, time_code.get_minutes())
    self.assertEqual(3, time_code.get_seconds())
    self.assertEqual(4, time_code.get_frames())
    self.assertTrue(time_code.is_drop_frame())
    self.assertEqual(111582, time_code.get_nb_frames())
    self.assertAlmostEqual(111582 / 30, float(time_code.get_fraction()), delta=0.001)
    self.assertEqual("01:02:03;04", str(time_code))

    time_code = SccTimeCode.parse("01;02;03;04")
    self.assertEqual(1, time_code.get_hours())
    self.assertEqual(2, time_code.get_minutes())
    self.assertEqual(3, time_code.get_seconds())
    self.assertEqual(4, time_code.get_frames())
    self.assertTrue(time_code.is_drop_frame())
    self.assertEqual(111582, time_code.get_nb_frames())
    self.assertAlmostEqual(111582 / 30, float(time_code.get_fraction()), delta=0.001)
    self.assertEqual("01:02:03;04", str(time_code))

    time_code = SccTimeCode.parse("01:02:03.04")
    self.assertEqual(1, time_code.get_hours())
    self.assertEqual(2, time_code.get_minutes())
    self.assertEqual(3, time_code.get_seconds())
    self.assertEqual(4, time_code.get_frames())
    self.assertTrue(time_code.is_drop_frame())
    self.assertEqual(111582, time_code.get_nb_frames())
    self.assertAlmostEqual(111582 / 30, float(time_code.get_fraction()), delta=0.001)
    self.assertEqual("01:02:03;04", str(time_code))

    time_code = SccTimeCode.parse("01.02.03.04")
    self.assertEqual(1, time_code.get_hours())
    self.assertEqual(2, time_code.get_minutes())
    self.assertEqual(3, time_code.get_seconds())
    self.assertEqual(4, time_code.get_frames())
    self.assertTrue(time_code.is_drop_frame())
    self.assertEqual(111582, time_code.get_nb_frames())
    self.assertAlmostEqual(111582 / 30, float(time_code.get_fraction()), delta=0.001)
    self.assertEqual("01:02:03;04", str(time_code))

  def test_time_code_frames_conversion(self):
    time_code = SccTimeCode.from_frames(1795)
    self.assertEqual("00:00:59:25", str(time_code))
    self.assertEqual(1795, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1796)
    self.assertEqual("00:00:59:26", str(time_code))
    self.assertEqual(1796, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1797)
    self.assertEqual("00:00:59:27", str(time_code))
    self.assertEqual(1797, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1798)
    self.assertEqual("00:00:59:28", str(time_code))
    self.assertEqual(1798, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1799)
    self.assertEqual("00:00:59:29", str(time_code))
    self.assertEqual(1799, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1800)
    self.assertEqual("00:01:00:00", str(time_code))
    self.assertEqual(1800, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1801)
    self.assertEqual("00:01:00:01", str(time_code))
    self.assertEqual(1801, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1802)
    self.assertEqual("00:01:00:02", str(time_code))
    self.assertEqual(1802, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1803)
    self.assertEqual("00:01:00:03", str(time_code))
    self.assertEqual(1803, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1804)
    self.assertEqual("00:01:00:04", str(time_code))
    self.assertEqual(1804, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1805)
    self.assertEqual("00:01:00:05", str(time_code))
    self.assertEqual(1805, time_code.get_nb_frames())

    time_code = SccTimeCode.from_frames(17977)
    self.assertEqual("00:09:59:07", str(time_code))
    self.assertEqual(17977, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17978)
    self.assertEqual("00:09:59:08", str(time_code))
    self.assertEqual(17978, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17979)
    self.assertEqual("00:09:59:09", str(time_code))
    self.assertEqual(17979, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17980)
    self.assertEqual("00:09:59:10", str(time_code))
    self.assertEqual(17980, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17981)
    self.assertEqual("00:09:59:11", str(time_code))
    self.assertEqual(17981, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17982)
    self.assertEqual("00:09:59:12", str(time_code))
    self.assertEqual(17982, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17983)
    self.assertEqual("00:09:59:13", str(time_code))
    self.assertEqual(17983, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17984)
    self.assertEqual("00:09:59:14", str(time_code))
    self.assertEqual(17984, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17985)
    self.assertEqual("00:09:59:15", str(time_code))
    self.assertEqual(17985, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17986)
    self.assertEqual("00:09:59:16", str(time_code))
    self.assertEqual(17986, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17987)
    self.assertEqual("00:09:59:17", str(time_code))
    self.assertEqual(17987, time_code.get_nb_frames())

  def test_drop_frame_time_code_frames_conversion(self):
    time_code = SccTimeCode.from_frames(1795, drop_frame=True)
    self.assertEqual("00:00:59;25", str(time_code))
    self.assertEqual(1795, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1796, drop_frame=True)
    self.assertEqual("00:00:59;26", str(time_code))
    self.assertEqual(1796, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1797, drop_frame=True)
    self.assertEqual("00:00:59;27", str(time_code))
    self.assertEqual(1797, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1798, drop_frame=True)
    self.assertEqual("00:00:59;28", str(time_code))
    self.assertEqual(1798, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1799, drop_frame=True)
    self.assertEqual("00:00:59;29", str(time_code))
    self.assertEqual(1799, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1800, drop_frame=True)
    self.assertEqual("00:01:00;02", str(time_code))
    self.assertEqual(1800, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1801, drop_frame=True)
    self.assertEqual("00:01:00;03", str(time_code))
    self.assertEqual(1801, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1802, drop_frame=True)
    self.assertEqual("00:01:00;04", str(time_code))
    self.assertEqual(1802, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1803, drop_frame=True)
    self.assertEqual("00:01:00;05", str(time_code))
    self.assertEqual(1803, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1804, drop_frame=True)
    self.assertEqual("00:01:00;06", str(time_code))
    self.assertEqual(1804, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(1805, drop_frame=True)
    self.assertEqual("00:01:00;07", str(time_code))
    self.assertEqual(1805, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17977, drop_frame=True)

    self.assertEqual("00:09:59;25", str(time_code))
    self.assertEqual(17977, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17978, drop_frame=True)
    self.assertEqual("00:09:59;26", str(time_code))
    self.assertEqual(17978, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17979, drop_frame=True)
    self.assertEqual("00:09:59;27", str(time_code))
    self.assertEqual(17979, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17980, drop_frame=True)
    self.assertEqual("00:09:59;28", str(time_code))
    self.assertEqual(17980, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17981, drop_frame=True)
    self.assertEqual("00:09:59;29", str(time_code))
    self.assertEqual(17981, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17982, drop_frame=True)
    self.assertEqual("00:10:00;00", str(time_code))
    self.assertEqual(17982, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17983, drop_frame=True)
    self.assertEqual("00:10:00;01", str(time_code))
    self.assertEqual(17983, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17984, drop_frame=True)
    self.assertEqual("00:10:00;02", str(time_code))
    self.assertEqual(17984, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17985, drop_frame=True)
    self.assertEqual("00:10:00;03", str(time_code))
    self.assertEqual(17985, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17986, drop_frame=True)
    self.assertEqual("00:10:00;04", str(time_code))
    self.assertEqual(17986, time_code.get_nb_frames())
    time_code = SccTimeCode.from_frames(17987, drop_frame=True)
    self.assertEqual("00:10:00;05", str(time_code))
    self.assertEqual(17987, time_code.get_nb_frames())

  def test_from_frames(self):
    time_code = SccTimeCode.from_frames(111694)
    self.assertEqual(1, time_code.get_hours())
    self.assertEqual(2, time_code.get_minutes())
    self.assertEqual(3, time_code.get_seconds())
    self.assertEqual(4, time_code.get_frames())
    self.assertFalse(time_code.is_drop_frame())
    self.assertEqual(111694, time_code.get_nb_frames())
    self.assertEqual("01:02:03:04", str(time_code))

    time_code = SccTimeCode.from_frames(111582, drop_frame=True)
    self.assertEqual(1, time_code.get_hours())
    self.assertEqual(2, time_code.get_minutes())
    self.assertEqual(3, time_code.get_seconds())
    self.assertEqual(4, time_code.get_frames())
    self.assertTrue(time_code.is_drop_frame())
    self.assertEqual(111582, time_code.get_nb_frames())
    self.assertEqual("01:02:03;04", str(time_code))

  def test_add_frames(self):
    time_code = SccTimeCode.parse("01:02:03:04")
    time_code.add_frames(30)
    self.assertEqual(1, time_code.get_hours())
    self.assertEqual(2, time_code.get_minutes())
    self.assertEqual(4, time_code.get_seconds())
    self.assertEqual(4, time_code.get_frames())
    self.assertFalse(time_code.is_drop_frame())
    self.assertEqual(111724, time_code.get_nb_frames())
    self.assertAlmostEqual(111724 / 30, float(time_code.get_fraction()), delta=0.001)
    self.assertEqual("01:02:04:04", str(time_code))

    time_code = SccTimeCode.parse("00:00:59;29")
    time_code.add_frames()
    self.assertEqual(0, time_code.get_hours())
    self.assertEqual(1, time_code.get_minutes())
    self.assertEqual(0, time_code.get_seconds())
    self.assertEqual(2, time_code.get_frames())
    self.assertTrue(time_code.is_drop_frame())
    self.assertEqual(1800, time_code.get_nb_frames())
    self.assertAlmostEqual(1800 / 30, float(time_code.get_fraction()), delta=0.001)
    self.assertEqual("00:01:00;02", str(time_code))

    time_code = SccTimeCode.parse("00:19:59;29")
    time_code.add_frames()
    self.assertEqual(0, time_code.get_hours())
    self.assertEqual(20, time_code.get_minutes())
    self.assertEqual(0, time_code.get_seconds())
    self.assertEqual(0, time_code.get_frames())
    self.assertTrue(time_code.is_drop_frame())
    self.assertEqual(35964, time_code.get_nb_frames())
    self.assertAlmostEqual(35964 / 30, float(time_code.get_fraction()), delta=0.001)
    self.assertEqual("00:20:00;00", str(time_code))
