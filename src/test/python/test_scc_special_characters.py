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

"""Unit tests for the SCC Special and Extended characters"""

# pylint: disable=R0201,C0115,C0116,W0212

import unittest

from ttconv.scc.codes.special_characters import SccSpecialCharacter, SccExtendedCharacter


class SccExtendedCharacterTest(unittest.TestCase):

  def test_scc_special_character_values(self):
    special_char_codes = list(range(0x1130, 0x1140)) + list(range(0x1930, 0x1940))

    extended_char_codes = list(range(0x1220, 0x1240)) + list(range(0x1320, 0x1340)) + \
                          list(range(0x1A20, 0x1A40)) + list(range(0x1B20, 0x1B40))

    for code in special_char_codes:
      self.assertIsNotNone(SccSpecialCharacter.find(code))

    for code in extended_char_codes:
      self.assertIsNotNone(SccExtendedCharacter.find(code))

  def test_scc_special_characters_unicode_values(self):
    spec_char = SccSpecialCharacter.find(0x1130)
    self.assertEqual(SccSpecialCharacter.REGISTERED_MARK_SYMBOL, spec_char)
    self.assertEqual('\u00AE', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1930)
    self.assertEqual(SccSpecialCharacter.REGISTERED_MARK_SYMBOL, spec_char)
    self.assertEqual('\u00AE', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1131)
    self.assertEqual(SccSpecialCharacter.DEGREE_SIGN, spec_char)
    self.assertEqual('\u00B0', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1931)
    self.assertEqual(SccSpecialCharacter.DEGREE_SIGN, spec_char)
    self.assertEqual('\u00B0', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1132)
    self.assertEqual(SccSpecialCharacter.VULGAR_FRACTION_ONE_HALF, spec_char)
    self.assertEqual('\u00BD', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1932)
    self.assertEqual(SccSpecialCharacter.VULGAR_FRACTION_ONE_HALF, spec_char)
    self.assertEqual('\u00BD', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1133)
    self.assertEqual(SccSpecialCharacter.INVERTED_QUESTION_MARK, spec_char)
    self.assertEqual('\u00BF', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1933)
    self.assertEqual(SccSpecialCharacter.INVERTED_QUESTION_MARK, spec_char)
    self.assertEqual('\u00BF', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1134)
    self.assertEqual(SccSpecialCharacter.TRADEMARK_SYMBOL, spec_char)
    self.assertEqual('\u2122', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1934)
    self.assertEqual(SccSpecialCharacter.TRADEMARK_SYMBOL, spec_char)
    self.assertEqual('\u2122', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1135)
    self.assertEqual(SccSpecialCharacter.CENTS_SIGN, spec_char)
    self.assertEqual('\u00A2', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1935)
    self.assertEqual(SccSpecialCharacter.CENTS_SIGN, spec_char)
    self.assertEqual('\u00A2', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1136)
    self.assertEqual(SccSpecialCharacter.POUNDS_STERLING_SIGN, spec_char)
    self.assertEqual('\u00A3', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1936)
    self.assertEqual(SccSpecialCharacter.POUNDS_STERLING_SIGN, spec_char)
    self.assertEqual('\u00A3', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1137)
    self.assertEqual(SccSpecialCharacter.MUSIC_NOTE, spec_char)
    self.assertEqual('\u266A', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1937)
    self.assertEqual(SccSpecialCharacter.MUSIC_NOTE, spec_char)
    self.assertEqual('\u266A', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1138)
    self.assertEqual(SccSpecialCharacter.LOWER_CASE_A_WITH_GRAVE_ACCENT, spec_char)
    self.assertEqual('\u00E0', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1938)
    self.assertEqual(SccSpecialCharacter.LOWER_CASE_A_WITH_GRAVE_ACCENT, spec_char)
    self.assertEqual('\u00E0', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1139)
    self.assertEqual(SccSpecialCharacter.TRANSPARENT_SPACE, spec_char)
    self.assertEqual('\u0020', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x1939)
    self.assertEqual(SccSpecialCharacter.TRANSPARENT_SPACE, spec_char)
    self.assertEqual('\u0020', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x113A)
    self.assertEqual(SccSpecialCharacter.LOWER_CASE_E_WITH_GRAVE_ACCENT, spec_char)
    self.assertEqual('\u00E8', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x193A)
    self.assertEqual(SccSpecialCharacter.LOWER_CASE_E_WITH_GRAVE_ACCENT, spec_char)
    self.assertEqual('\u00E8', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x113B)
    self.assertEqual(SccSpecialCharacter.LOWER_CASE_A_WITH_CIRCUMFLEX, spec_char)
    self.assertEqual('\u00E2', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x193B)
    self.assertEqual(SccSpecialCharacter.LOWER_CASE_A_WITH_CIRCUMFLEX, spec_char)
    self.assertEqual('\u00E2', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x113C)
    self.assertEqual(SccSpecialCharacter.LOWER_CASE_E_WITH_CIRCUMFLEX, spec_char)
    self.assertEqual('\u00EA', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x193C)
    self.assertEqual(SccSpecialCharacter.LOWER_CASE_E_WITH_CIRCUMFLEX, spec_char)
    self.assertEqual('\u00EA', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x113D)
    self.assertEqual(SccSpecialCharacter.LOWER_CASE_I_WITH_CIRCUMFLEX, spec_char)
    self.assertEqual('\u00EE', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x193D)
    self.assertEqual(SccSpecialCharacter.LOWER_CASE_I_WITH_CIRCUMFLEX, spec_char)
    self.assertEqual('\u00EE', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x113E)
    self.assertEqual(SccSpecialCharacter.LOWER_CASE_O_WITH_CIRCUMFLEX, spec_char)
    self.assertEqual('\u00F4', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x193E)
    self.assertEqual(SccSpecialCharacter.LOWER_CASE_O_WITH_CIRCUMFLEX, spec_char)
    self.assertEqual('\u00F4', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x113F)
    self.assertEqual(SccSpecialCharacter.LOWER_CASE_U_WITH_CIRCUMFLEX, spec_char)
    self.assertEqual('\u00FB', spec_char.get_unicode_value())

    spec_char = SccSpecialCharacter.find(0x193F)
    self.assertEqual(SccSpecialCharacter.LOWER_CASE_U_WITH_CIRCUMFLEX, spec_char)
    self.assertEqual('\u00FB', spec_char.get_unicode_value())

  def test_scc_spanish_extended_characters_unicode_values(self):
    extended_char = SccExtendedCharacter.find(0x1220)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_A_WITH_ACUTE, extended_char)
    self.assertEqual('\u00C1', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A20)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_A_WITH_ACUTE, extended_char)
    self.assertEqual('\u00C1', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1221)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_E_WITH_ACUTE, extended_char)
    self.assertEqual('\u00C9', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A21)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_E_WITH_ACUTE, extended_char)
    self.assertEqual('\u00C9', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1222)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_O_WITH_ACUTE, extended_char)
    self.assertEqual('\u00D3', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A22)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_O_WITH_ACUTE, extended_char)
    self.assertEqual('\u00D3', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1223)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_U_WITH_ACUTE, extended_char)
    self.assertEqual('\u00DA', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A23)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_U_WITH_ACUTE, extended_char)
    self.assertEqual('\u00DA', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1224)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_U_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00DC', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A24)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_U_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00DC', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1225)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_U_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00FC', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A25)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_U_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00FC', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1226)
    self.assertEqual(SccExtendedCharacter.LEFT_SINGLE_QUOTATION_MARK, extended_char)
    self.assertEqual('\u2018', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A26)
    self.assertEqual(SccExtendedCharacter.LEFT_SINGLE_QUOTATION_MARK, extended_char)
    self.assertEqual('\u2018', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1227)
    self.assertEqual(SccExtendedCharacter.INVERTED_EXCLAMATION_MARK, extended_char)
    self.assertEqual('\u00A1', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A27)
    self.assertEqual(SccExtendedCharacter.INVERTED_EXCLAMATION_MARK, extended_char)
    self.assertEqual('\u00A1', extended_char.get_unicode_value())

  def test_scc_miscellaneous_extended_characters_unicode_values(self):
    extended_char = SccExtendedCharacter.find(0x1228)
    self.assertEqual(SccExtendedCharacter.ASTERISK, extended_char)
    self.assertEqual('\u002A', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A28)
    self.assertEqual(SccExtendedCharacter.ASTERISK, extended_char)
    self.assertEqual('\u002A', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1229)
    self.assertEqual(SccExtendedCharacter.NEUTRAL_SINGLE_QUOTATION_MARK, extended_char)
    self.assertEqual('\u0027', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A29)
    self.assertEqual(SccExtendedCharacter.NEUTRAL_SINGLE_QUOTATION_MARK, extended_char)
    self.assertEqual('\u0027', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x122A)
    self.assertEqual(SccExtendedCharacter.BOX_DRAWINGS_HEAVY_HORIZONTAL, extended_char)
    self.assertEqual('\u2501', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A2A)
    self.assertEqual(SccExtendedCharacter.BOX_DRAWINGS_HEAVY_HORIZONTAL, extended_char)
    self.assertEqual('\u2501', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x122B)
    self.assertEqual(SccExtendedCharacter.COPYRIGHT_SIGN, extended_char)
    self.assertEqual('\u00A9', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A2B)
    self.assertEqual(SccExtendedCharacter.COPYRIGHT_SIGN, extended_char)
    self.assertEqual('\u00A9', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x122C)
    self.assertEqual(SccExtendedCharacter.SERVICE_MARK, extended_char)
    self.assertEqual('\u2120', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A2C)
    self.assertEqual(SccExtendedCharacter.SERVICE_MARK, extended_char)
    self.assertEqual('\u2120', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x122D)
    self.assertEqual(SccExtendedCharacter.BULLET, extended_char)
    self.assertEqual('\u2022', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A2D)
    self.assertEqual(SccExtendedCharacter.BULLET, extended_char)
    self.assertEqual('\u2022', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x122E)
    self.assertEqual(SccExtendedCharacter.LEFT_DOUBLE_QUOTATION_MARK, extended_char)
    self.assertEqual('\u201C', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A2E)
    self.assertEqual(SccExtendedCharacter.LEFT_DOUBLE_QUOTATION_MARK, extended_char)
    self.assertEqual('\u201C', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x122F)
    self.assertEqual(SccExtendedCharacter.RIGHT_DOUBLE_QUOTATION_MARK, extended_char)
    self.assertEqual('\u201D', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A2F)
    self.assertEqual(SccExtendedCharacter.RIGHT_DOUBLE_QUOTATION_MARK, extended_char)
    self.assertEqual('\u201D', extended_char.get_unicode_value())

  def test_scc_french_extended_characters_unicode_values(self):
    extended_char = SccExtendedCharacter.find(0x1230)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_A_WITH_GRAVE, extended_char)
    self.assertEqual('\u00C0', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A30)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_A_WITH_GRAVE, extended_char)
    self.assertEqual('\u00C0', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1231)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_A_WITH_CIRCUMFLEX, extended_char)
    self.assertEqual('\u00C2', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A31)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_A_WITH_CIRCUMFLEX, extended_char)
    self.assertEqual('\u00C2', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1232)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_C_WITH_CEDILLA, extended_char)
    self.assertEqual('\u00C7', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A32)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_C_WITH_CEDILLA, extended_char)
    self.assertEqual('\u00C7', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1233)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_E_WITH_GRAVE, extended_char)
    self.assertEqual('\u00C8', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A33)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_E_WITH_GRAVE, extended_char)
    self.assertEqual('\u00C8', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1234)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_E_WITH_CIRCUMFLEX, extended_char)
    self.assertEqual('\u00CA', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A34)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_E_WITH_CIRCUMFLEX, extended_char)
    self.assertEqual('\u00CA', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1235)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_E_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00CB', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A35)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_E_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00CB', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1236)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_E_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00EB', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A36)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_E_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00EB', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1237)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_I_WITH_CIRCUMFLEX, extended_char)
    self.assertEqual('\u00CE', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A37)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_I_WITH_CIRCUMFLEX, extended_char)
    self.assertEqual('\u00CE', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1238)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_I_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00CF', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A38)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_I_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00CF', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1239)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_I_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00EF', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A39)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_I_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00EF', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x123A)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_O_WITH_CIRCUMFLEX, extended_char)
    self.assertEqual('\u00D4', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A3A)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_O_WITH_CIRCUMFLEX, extended_char)
    self.assertEqual('\u00D4', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x123B)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_U_WITH_GRAVE, extended_char)
    self.assertEqual('\u00D9', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A3B)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_U_WITH_GRAVE, extended_char)
    self.assertEqual('\u00D9', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x123C)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_U_WITH_GRAVE, extended_char)
    self.assertEqual('\u00F9', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A3C)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_U_WITH_GRAVE, extended_char)
    self.assertEqual('\u00F9', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x123D)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_U_WITH_CIRCUMFLEX, extended_char)
    self.assertEqual('\u00DB', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A3D)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_U_WITH_CIRCUMFLEX, extended_char)
    self.assertEqual('\u00DB', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x123E)
    self.assertEqual(SccExtendedCharacter.LEFT_POINTING_GUILLEMET, extended_char)
    self.assertEqual('\u00AB', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A3E)
    self.assertEqual(SccExtendedCharacter.LEFT_POINTING_GUILLEMET, extended_char)
    self.assertEqual('\u00AB', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x123F)
    self.assertEqual(SccExtendedCharacter.RIGHT_POINTING_GUILLEMET, extended_char)
    self.assertEqual('\u00BB', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1A3F)
    self.assertEqual(SccExtendedCharacter.RIGHT_POINTING_GUILLEMET, extended_char)
    self.assertEqual('\u00BB', extended_char.get_unicode_value())

  def test_scc_portuguese_extended_characters_unicode_values(self):
    extended_char = SccExtendedCharacter.find(0x1320)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_A_WITH_TILDE, extended_char)
    self.assertEqual('\u00C3', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B20)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_A_WITH_TILDE, extended_char)
    self.assertEqual('\u00C3', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1321)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_A_WITH_TILDE, extended_char)
    self.assertEqual('\u00E3', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B21)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_A_WITH_TILDE, extended_char)
    self.assertEqual('\u00E3', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1322)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_I_WITH_ACUTE, extended_char)
    self.assertEqual('\u00CD', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B22)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_I_WITH_ACUTE, extended_char)
    self.assertEqual('\u00CD', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1323)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_I_WITH_GRAVE, extended_char)
    self.assertEqual('\u00CC', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B23)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_I_WITH_GRAVE, extended_char)
    self.assertEqual('\u00CC', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1324)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_I_WITH_GRAVE, extended_char)
    self.assertEqual('\u00EC', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B24)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_I_WITH_GRAVE, extended_char)
    self.assertEqual('\u00EC', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1325)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_O_WITH_GRAVE, extended_char)
    self.assertEqual('\u00D2', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B25)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_O_WITH_GRAVE, extended_char)
    self.assertEqual('\u00D2', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1326)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_O_WITH_GRAVE, extended_char)
    self.assertEqual('\u00F2', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B26)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_O_WITH_GRAVE, extended_char)
    self.assertEqual('\u00F2', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1327)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_O_WITH_TILDE, extended_char)
    self.assertEqual('\u00D5', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B27)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_O_WITH_TILDE, extended_char)
    self.assertEqual('\u00D5', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1328)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_O_WITH_TILDE, extended_char)
    self.assertEqual('\u00F5', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B28)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_O_WITH_TILDE, extended_char)
    self.assertEqual('\u00F5', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1329)
    self.assertEqual(SccExtendedCharacter.BRACE_OPENING, extended_char)
    self.assertEqual('\u007B', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B29)
    self.assertEqual(SccExtendedCharacter.BRACE_OPENING, extended_char)
    self.assertEqual('\u007B', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x132A)
    self.assertEqual(SccExtendedCharacter.BRACE_CLOSING, extended_char)
    self.assertEqual('\u007D', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B2A)
    self.assertEqual(SccExtendedCharacter.BRACE_CLOSING, extended_char)
    self.assertEqual('\u007D', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x132B)
    self.assertEqual(SccExtendedCharacter.REVERSE_SOLIDUS, extended_char)
    self.assertEqual('\u005C', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B2B)
    self.assertEqual(SccExtendedCharacter.REVERSE_SOLIDUS, extended_char)
    self.assertEqual('\u005C', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x132C)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_TURNED_V, extended_char)
    self.assertEqual('\u028C', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B2C)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_TURNED_V, extended_char)
    self.assertEqual('\u028C', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x132D)
    self.assertEqual(SccExtendedCharacter.LOW_LINE, extended_char)
    self.assertEqual('\u005F', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B2D)
    self.assertEqual(SccExtendedCharacter.LOW_LINE, extended_char)
    self.assertEqual('\u005F', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x132E)
    self.assertEqual(SccExtendedCharacter.VERTICAL_LINE, extended_char)
    self.assertEqual('\u007C', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B2E)
    self.assertEqual(SccExtendedCharacter.VERTICAL_LINE, extended_char)
    self.assertEqual('\u007C', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x132F)
    self.assertEqual(SccExtendedCharacter.TILDE, extended_char)
    self.assertEqual('\u007E', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B2F)
    self.assertEqual(SccExtendedCharacter.TILDE, extended_char)
    self.assertEqual('\u007E', extended_char.get_unicode_value())

  def test_scc_german_extended_characters_unicode_values(self):
    extended_char = SccExtendedCharacter.find(0x1330)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_A_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00C4', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B30)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_A_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00C4', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1331)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_A_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00E4', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B31)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_A_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00E4', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1332)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_O_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00D6', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B32)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_O_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00D6', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1333)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_O_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00F6', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B33)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_O_WITH_DIAERESIS, extended_char)
    self.assertEqual('\u00F6', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1334)
    self.assertEqual(SccExtendedCharacter.ESZETT, extended_char)
    self.assertEqual('\u00DF', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B34)
    self.assertEqual(SccExtendedCharacter.ESZETT, extended_char)
    self.assertEqual('\u00DF', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1335)
    self.assertEqual(SccExtendedCharacter.YEN_SIGN, extended_char)
    self.assertEqual('\u00A5', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B35)
    self.assertEqual(SccExtendedCharacter.YEN_SIGN, extended_char)
    self.assertEqual('\u00A5', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1336)
    self.assertEqual(SccExtendedCharacter.CURRENCY_SIGN, extended_char)
    self.assertEqual('\u00A4', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B36)
    self.assertEqual(SccExtendedCharacter.CURRENCY_SIGN, extended_char)
    self.assertEqual('\u00A4', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1337)
    self.assertEqual(SccExtendedCharacter.BOX_DRAWINGS_HEAVY_VERTICAL, extended_char)
    self.assertEqual('\u2503', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B37)
    self.assertEqual(SccExtendedCharacter.BOX_DRAWINGS_HEAVY_VERTICAL, extended_char)
    self.assertEqual('\u2503', extended_char.get_unicode_value())

  def test_scc_danish_extended_characters_unicode_values(self):
    extended_char = SccExtendedCharacter.find(0x1338)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_A_WITH_RING_ABOVE, extended_char)
    self.assertEqual('\u00C5', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B38)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_A_WITH_RING_ABOVE, extended_char)
    self.assertEqual('\u00C5', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1339)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_A_WITH_RING_ABOVE, extended_char)
    self.assertEqual('\u00E5', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B39)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_A_WITH_RING_ABOVE, extended_char)
    self.assertEqual('\u00E5', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x133A)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_O_WITH_STROKE, extended_char)
    self.assertEqual('\u00D8', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B3A)
    self.assertEqual(SccExtendedCharacter.LATIN_CAPITAL_LETTER_O_WITH_STROKE, extended_char)
    self.assertEqual('\u00D8', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x133B)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_O_WITH_STROKE, extended_char)
    self.assertEqual('\u00F8', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B3B)
    self.assertEqual(SccExtendedCharacter.LATIN_SMALL_LETTER_O_WITH_STROKE, extended_char)
    self.assertEqual('\u00F8', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x133C)
    self.assertEqual(SccExtendedCharacter.BOX_DRAWINGS_HEAVY_DOWN_AND_RIGHT, extended_char)
    self.assertEqual('\u250F', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B3C)
    self.assertEqual(SccExtendedCharacter.BOX_DRAWINGS_HEAVY_DOWN_AND_RIGHT, extended_char)
    self.assertEqual('\u250F', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x133D)
    self.assertEqual(SccExtendedCharacter.BOX_DRAWINGS_HEAVY_DOWN_AND_LEFT, extended_char)
    self.assertEqual('\u2513', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B3D)
    self.assertEqual(SccExtendedCharacter.BOX_DRAWINGS_HEAVY_DOWN_AND_LEFT, extended_char)
    self.assertEqual('\u2513', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x133E)
    self.assertEqual(SccExtendedCharacter.BOX_DRAWINGS_HEAVY_UP_AND_RIGHT, extended_char)
    self.assertEqual('\u2517', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B3E)
    self.assertEqual(SccExtendedCharacter.BOX_DRAWINGS_HEAVY_UP_AND_RIGHT, extended_char)
    self.assertEqual('\u2517', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x133F)
    self.assertEqual(SccExtendedCharacter.BOX_DRAWINGS_HEAVY_UP_AND_LEFT, extended_char)
    self.assertEqual('\u251B', extended_char.get_unicode_value())

    extended_char = SccExtendedCharacter.find(0x1B3F)
    self.assertEqual(SccExtendedCharacter.BOX_DRAWINGS_HEAVY_UP_AND_LEFT, extended_char)
    self.assertEqual('\u251B', extended_char.get_unicode_value())


if __name__ == '__main__':
  unittest.main()
