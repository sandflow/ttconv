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

"""Unit tests for the SCC Mid-Row Codes"""

# pylint: disable=R0201,C0115,C0116

import unittest
from typing import Optional

from ttconv.scc.codes.mid_row_codes import SccMidRowCode
from ttconv.style_properties import NamedColors, FontStyleType, TextDecorationType, ColorType

MID_ROW_CODE_VALUES = [0x1120, 0x1920, 0x1121, 0x1921, 0x1122, 0x1922, 0x1123, 0x1923, 0x1124,
                       0x1924, 0x1125, 0x1925, 0x1126, 0x1926, 0x1127, 0x1927, 0x1128, 0x1928,
                       0x1129, 0x1929, 0x112A, 0x192A, 0x112B, 0x192B, 0x112C, 0x192C, 0x112D,
                       0x192D, 0x112E, 0x192E, 0x112F, 0x192F]


class SCCMidRowCodesTest(unittest.TestCase):

  def check_mid_row_code(self, mrc, expected_value: SccMidRowCode, expected_color: Optional[ColorType],
                         expected_font_style: Optional[FontStyleType], expected_text_decoration: Optional[TextDecorationType]):
    self.assertEqual(expected_value, mrc)
    self.assertEqual(expected_color, mrc.get_color())
    self.assertEqual(expected_font_style, mrc.get_font_style())
    self.assertEqual(expected_text_decoration, mrc.get_text_decoration())

  def test_scc_mid_row_codes_valid_white(self):
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[0]), SccMidRowCode.WHITE, NamedColors.white.value, None, None)
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[1]), SccMidRowCode.WHITE, NamedColors.white.value, None, None)

  def test_scc_mid_row_codes_valid_white_underline(self):
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[2]), SccMidRowCode.WHITE_UNDERLINE, NamedColors.white.value,
                            None, TextDecorationType(underline=TextDecorationType.Action.add))
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[3]), SccMidRowCode.WHITE_UNDERLINE, NamedColors.white.value,
                            None, TextDecorationType(underline=TextDecorationType.Action.add))

  def test_scc_mid_row_codes_valid_green(self):
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[4]), SccMidRowCode.GREEN, NamedColors.green.value, None, None)
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[5]), SccMidRowCode.GREEN, NamedColors.green.value, None, None)

  def test_scc_mid_row_codes_valid_green_underline(self):
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[6]), SccMidRowCode.GREEN_UNDERLINE, NamedColors.green.value,
                            None, TextDecorationType(underline=TextDecorationType.Action.add))
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[7]), SccMidRowCode.GREEN_UNDERLINE, NamedColors.green.value,
                            None, TextDecorationType(underline=TextDecorationType.Action.add))

  def test_scc_mid_row_codes_valid_blue(self):
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[8]), SccMidRowCode.BLUE, NamedColors.blue.value, None, None)
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[9]), SccMidRowCode.BLUE, NamedColors.blue.value, None, None)

  def test_scc_mid_row_codes_valid_blue_underline(self):
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[10]), SccMidRowCode.BLUE_UNDERLINE, NamedColors.blue.value, None,
                            TextDecorationType(underline=TextDecorationType.Action.add))
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[11]), SccMidRowCode.BLUE_UNDERLINE, NamedColors.blue.value, None,
                            TextDecorationType(underline=TextDecorationType.Action.add))

  def test_scc_mid_row_codes_valid_cyan(self):
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[12]), SccMidRowCode.CYAN, NamedColors.cyan.value, None, None)
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[13]), SccMidRowCode.CYAN, NamedColors.cyan.value, None, None)

  def test_scc_mid_row_codes_valid_cyan_underline(self):
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[14]), SccMidRowCode.CYAN_UNDERLINE, NamedColors.cyan.value, None,
                            TextDecorationType(underline=TextDecorationType.Action.add))
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[15]), SccMidRowCode.CYAN_UNDERLINE, NamedColors.cyan.value, None,
                            TextDecorationType(underline=TextDecorationType.Action.add))

  def test_scc_mid_row_codes_valid_red(self):
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[16]), SccMidRowCode.RED, NamedColors.red.value, None, None)
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[17]), SccMidRowCode.RED, NamedColors.red.value, None, None)

  def test_scc_mid_row_codes_valid_red_underline(self):
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[18]), SccMidRowCode.RED_UNDERLINE, NamedColors.red.value, None,
                            TextDecorationType(underline=TextDecorationType.Action.add))
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[19]), SccMidRowCode.RED_UNDERLINE, NamedColors.red.value, None,
                            TextDecorationType(underline=TextDecorationType.Action.add))

  def test_scc_mid_row_codes_valid_yellow(self):
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[20]), SccMidRowCode.YELLOW, NamedColors.yellow.value, None, None)
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[21]), SccMidRowCode.YELLOW, NamedColors.yellow.value, None, None)

  def test_scc_mid_row_codes_valid_yellow_underline(self):
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[22]), SccMidRowCode.YELLOW_UNDERLINE, NamedColors.yellow.value,
                            None, TextDecorationType(underline=TextDecorationType.Action.add))
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[23]), SccMidRowCode.YELLOW_UNDERLINE, NamedColors.yellow.value,
                            None, TextDecorationType(underline=TextDecorationType.Action.add))

  def test_scc_mid_row_codes_valid_magenta(self):
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[24]), SccMidRowCode.MAGENTA, NamedColors.magenta.value, None,
                            None)
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[25]), SccMidRowCode.MAGENTA, NamedColors.magenta.value, None,
                            None)

  def test_scc_mid_row_codes_valid_magenta_underline(self):
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[26]), SccMidRowCode.MAGENTA_UNDERLINE, NamedColors.magenta.value,
                            None, TextDecorationType(underline=TextDecorationType.Action.add))
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[27]), SccMidRowCode.MAGENTA_UNDERLINE, NamedColors.magenta.value,
                            None, TextDecorationType(underline=TextDecorationType.Action.add))

  def test_scc_mid_row_codes_valid_italics(self):
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[28]), SccMidRowCode.ITALICS, None, FontStyleType.italic, None)
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[29]), SccMidRowCode.ITALICS, None, FontStyleType.italic, None)

  def test_scc_mid_row_codes_valid_italics_underline(self):
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[30]), SccMidRowCode.ITALICS_UNDERLINE, None,
                            FontStyleType.italic, TextDecorationType(underline=TextDecorationType.Action.add))
    self.check_mid_row_code(SccMidRowCode.find(MID_ROW_CODE_VALUES[31]), SccMidRowCode.ITALICS_UNDERLINE, None,
                            FontStyleType.italic, TextDecorationType(underline=TextDecorationType.Action.add))

  def test_scc_mid_row_codes_invalid(self):
    other_code_values = [code for code in range(0x0000, 0xFFFF) if code not in MID_ROW_CODE_VALUES]

    for mrc in other_code_values:
      self.assertIsNone(SccMidRowCode.find(mrc))
