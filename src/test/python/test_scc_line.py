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

"""Unit tests for the SCC lines"""

# pylint: disable=R0201,C0115,C0116,W0212
import unittest

from ttconv.scc.line import SccLine
from ttconv.scc.caption_style import SccCaptionStyle
from ttconv.time_code import SmpteTimeCode, FPS_30


class SccLineTest(unittest.TestCase):

  def test_scc_line_from_str_with_pop_on_style(self):
    line_str = "01:03:27:29	94ae 94ae 9420 9420 94f2 94f2 c845 d92c 2054 c845 5245 ae80 942c 942c 8080 8080 942f 942f"
    scc_line = SccLine.from_str(line_str)
    self.assertEqual(18, len(scc_line.scc_words))
    self.assertEqual(SmpteTimeCode(1, 3, 27, 29, FPS_30).to_temporal_offset(), scc_line.time_code.to_temporal_offset())
    self.assertEqual("01:03:27:29	{ENM}{ENM}{RCL}{RCL}{1504}{1504}HEY, THERE.{EDM}{EDM}{}{}{EOC}{EOC}", scc_line.to_disassembly())
    self.assertEqual(SccCaptionStyle.PopOn, scc_line.get_style())

  def test_scc_line_from_invalid_str(self):
    self.assertIsNone(SccLine.from_str(""))
    self.assertIsNone(SccLine.from_str("Hello world!"))

  def test_scc_line_from_str_with_unknown_style(self):
    line_str = "01:03:27:29	"
    scc_line = SccLine.from_str(line_str)
    self.assertEqual(0, len(scc_line.scc_words))
    self.assertEqual(SmpteTimeCode(1, 3, 27, 29, FPS_30).to_temporal_offset(), scc_line.time_code.to_temporal_offset())
    self.assertEqual("01:03:27:29	", scc_line.to_disassembly())
    self.assertEqual(SccCaptionStyle.Unknown, scc_line.get_style())

    line_str = "01:03:27:29	9024 c845 d92c 2054 c845 5245 ae80 9f9f"
    scc_line = SccLine.from_str(line_str)
    self.assertEqual(8, len(scc_line.scc_words))
    self.assertEqual(SmpteTimeCode(1, 3, 27, 29, FPS_30).to_temporal_offset(), scc_line.time_code.to_temporal_offset())
    self.assertEqual("01:03:27:29	{BBl}HEY, THERE.{??}", scc_line.to_disassembly())
    self.assertEqual(SccCaptionStyle.Unknown, scc_line.get_style())

  def test_scc_line_from_str_with_roll_up_style(self):
    line_str = "01:03:27:29	9425 9425 94ad 94ad 94c8 94c8 c845 d92c 2054 c845 5245 ae80"
    scc_line = SccLine.from_str(line_str)
    self.assertEqual(12, len(scc_line.scc_words))
    self.assertEqual(SmpteTimeCode(1, 3, 27, 29, FPS_30).to_temporal_offset(), scc_line.time_code.to_temporal_offset())
    self.assertEqual("01:03:27:29	{RU2}{RU2}{CR}{CR}{14R}{14R}HEY, THERE.", scc_line.to_disassembly())
    self.assertEqual(SccCaptionStyle.RollUp, scc_line.get_style())

  def test_scc_line_from_str_with_paint_on_style(self):
    line_str = "01:03:27:29	9429 9429 94f2 94f2 c845 d92c 2054 c845 5245 ae80"
    scc_line = SccLine.from_str(line_str)
    self.assertEqual(10, len(scc_line.scc_words))
    self.assertEqual(SmpteTimeCode(1, 3, 27, 29, FPS_30).to_temporal_offset(), scc_line.time_code.to_temporal_offset())
    self.assertEqual("01:03:27:29	{RDC}{RDC}{1504}{1504}HEY, THERE.", scc_line.to_disassembly())
    self.assertEqual(SccCaptionStyle.PaintOn, scc_line.get_style())
