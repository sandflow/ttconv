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

"""Unit tests for the SCC Special characters"""

# pylint: disable=R0201,C0115,C0116,W0212

import unittest

from ttconv.scc.codes.characters import unicode_to_scc
from ttconv.scc.codes.extended_characters import SccExtendedCharacter
from ttconv.scc.codes.special_characters import SccSpecialCharacter


class SccSpecialCharactersTest(unittest.TestCase):

  def test_unicode_to_scc_special_character(self):
    for spec_char in list(SccSpecialCharacter):
      unicode_char = spec_char.get_unicode_value()
      with self.subTest(unicode_char=unicode_char):
        # skip the TRANSPARENT_SPACE character
        if unicode_char == " ":
          continue
        self.assertEqual(int.from_bytes(unicode_to_scc(unicode_char), byteorder='big'), spec_char.get_ch1_value())


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


if __name__ == '__main__':
  unittest.main()
