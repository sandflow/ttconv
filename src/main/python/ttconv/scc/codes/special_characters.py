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

"""SCC Special and Extended characters"""

from __future__ import annotations

import typing
from enum import Enum

from ttconv.scc.codes import SccCode


class SccSpecialCharacter(SccCode, Enum):
  """SCC Special character definition"""

  # Special characters specified in CEA-608
  REGISTERED_MARK_SYMBOL = (0x1130, 0x1930, '\u00AE')  # ® Registered mark symbol
  DEGREE_SIGN = (0x1131, 0x1931, '\u00B0')  # ° Degree sign
  VULGAR_FRACTION_ONE_HALF = (0x1132, 0x1932, '\u00BD')  # ¿ Inverse question mark
  INVERTED_QUESTION_MARK = (0x1133, 0x1933, '\u00BF')  # ½ Vulgar one half fraction
  TRADEMARK_SYMBOL = (0x1134, 0x1934, '\u2122')  # ™ Trademark symbol
  CENTS_SIGN = (0x1135, 0x1935, '\u00A2')  # ¢ Cents sign
  POUNDS_STERLING_SIGN = (0x1136, 0x1936, '\u00A3')  # £ Pounds Sterling sign
  MUSIC_NOTE = (0x1137, 0x1937, '\u266A')  # ♪ Music note
  LOWER_CASE_A_WITH_GRAVE_ACCENT = (0x1138, 0x1938, '\u00E0')  # à Lower-case a with grave accent
  TRANSPARENT_SPACE = (0x1139, 0x1939, '\u0020')  # Transparent space
  LOWER_CASE_E_WITH_GRAVE_ACCENT = (0x113A, 0x193A, '\u00E8')  # è Lower-case e with grave accent
  LOWER_CASE_A_WITH_CIRCUMFLEX = (0x113B, 0x193B, '\u00E2')  # â Lower-case a with circumflex
  LOWER_CASE_E_WITH_CIRCUMFLEX = (0x113C, 0x193C, '\u00EA')  # ê Lower-case e with circumflex
  LOWER_CASE_I_WITH_CIRCUMFLEX = (0x113D, 0x193D, '\u00EE')  # î Lower-case i with circumflex
  LOWER_CASE_O_WITH_CIRCUMFLEX = (0x113E, 0x193E, '\u00F4')  # ô Lower-case o with circumflex
  LOWER_CASE_U_WITH_CIRCUMFLEX = (0x113F, 0x193F, '\u00FB')  # û Lower-case u with circumflex

  def __init__(self, channel_1: int, channel_2: int, unicode: chr):
    super().__init__(channel_1, channel_2)
    self._unicode = unicode

  def get_unicode_value(self) -> chr:
    """Returns the special or extended character unicode value"""
    return self._unicode

  @staticmethod
  def find(value: int) -> typing.Optional[SccSpecialCharacter]:
    """Find the special character corresponding to the specified value"""
    for spec_char in list(SccSpecialCharacter):
      if spec_char.contains_value(value):
        return spec_char
    return None


class SccExtendedCharacter(SccCode, Enum):
  """SCC Extended character definition"""

  # Spanish extended characters
  LATIN_CAPITAL_LETTER_A_WITH_ACUTE = (0x1220, 0x1A20, '\u00C1')  # Á capital A with acute accent
  LATIN_CAPITAL_LETTER_E_WITH_ACUTE = (0x1221, 0x1A21, '\u00C9')  # É capital E with acute accent
  LATIN_CAPITAL_LETTER_O_WITH_ACUTE = (0x1222, 0x1A22, '\u00D3')  # Ó capital O with acute accent
  LATIN_CAPITAL_LETTER_U_WITH_ACUTE = (0x1223, 0x1A23, '\u00DA')  # Ú capital U with acute accent
  LATIN_CAPITAL_LETTER_U_WITH_DIAERESIS = (0x1224, 0x1A24, '\u00DC')  # Ü capital U with diaeresis or umlaut
  LATIN_SMALL_LETTER_U_WITH_DIAERESIS = (0x1225, 0x1A25, '\u00FC')  # ü small u with diaeresis or umlaut
  LEFT_SINGLE_QUOTATION_MARK = (0x1226, 0x1A26, '\u2018')  # ‘ opening single quote
  INVERTED_EXCLAMATION_MARK = (0x1227, 0x1A27, '\u00A1')  # ¡ inverted exclamation mark

  # Miscellaneous extended characters
  ASTERISK = (0x1228, 0x1A28, '\u002A')  # * Asterisk
  NEUTRAL_SINGLE_QUOTATION_MARK = (0x1229, 0x1A29, '\u0027')  # ' plain single quote
  BOX_DRAWINGS_HEAVY_HORIZONTAL = (0x122A, 0x1A2A, '\u2501')  # — em dash
  COPYRIGHT_SIGN = (0x122B, 0x1A2B, '\u00A9')  # © Copyright
  SERVICE_MARK = (0x122C, 0x1A2C, '\u2120')  # SM Servicemark
  BULLET = (0x122D, 0x1A2D, '\u2022')  # ● round bullet
  LEFT_DOUBLE_QUOTATION_MARK = (0x122E, 0x1A2E, '\u201C')  # “ opening double quotes
  RIGHT_DOUBLE_QUOTATION_MARK = (0x122F, 0x1A2F, '\u201D')  # ” closing double quotes

  # French extended characters
  LATIN_CAPITAL_LETTER_A_WITH_GRAVE = (0x1230, 0x1A30, '\u00C0')  # À capital A with grave accent
  LATIN_CAPITAL_LETTER_A_WITH_CIRCUMFLEX = (0x1231, 0x1A31, '\u00C2')  # Â capital A with circumflex accent
  LATIN_CAPITAL_LETTER_C_WITH_CEDILLA = (0x1232, 0x1A32, '\u00C7')  # Ç capital C with cedilla
  LATIN_CAPITAL_LETTER_E_WITH_GRAVE = (0x1233, 0x1A33, '\u00C8')  # È capital E with grave accent
  LATIN_CAPITAL_LETTER_E_WITH_CIRCUMFLEX = (0x1234, 0x1A34, '\u00CA')  # Ê capital E with circumflex accent
  LATIN_CAPITAL_LETTER_E_WITH_DIAERESIS = (0x1235, 0x1A35, '\u00CB')  # Ë capital E with diaeresis or umlaut mark
  LATIN_SMALL_LETTER_E_WITH_DIAERESIS = (0x1236, 0x1A36, '\u00EB')  # ë small e with diaeresis or umlaut mark
  LATIN_CAPITAL_LETTER_I_WITH_CIRCUMFLEX = (0x1237, 0x1A37, '\u00CE')  # Î capital I with circumflex accent
  LATIN_CAPITAL_LETTER_I_WITH_DIAERESIS = (0x1238, 0x1A38, '\u00CF')  # Ï capital I with diaeresis or umlaut mark
  LATIN_SMALL_LETTER_I_WITH_DIAERESIS = (0x1239, 0x1A39, '\u00EF')  # ï small i with diaeresis or umlaut mark
  LATIN_CAPITAL_LETTER_O_WITH_CIRCUMFLEX = (0x123A, 0x1A3A, '\u00D4')  # Ô capital O with circumflex
  LATIN_CAPITAL_LETTER_U_WITH_GRAVE = (0x123B, 0x1A3B, '\u00D9')  # Ù capital U with grave accent
  LATIN_SMALL_LETTER_U_WITH_GRAVE = (0x123C, 0x1A3C, '\u00F9')  # ù small u with grave accent
  LATIN_CAPITAL_LETTER_U_WITH_CIRCUMFLEX = (0x123D, 0x1A3D, '\u00DB')  # Û capital U with circumflex accent
  LEFT_POINTING_GUILLEMET = (0x123E, 0x1A3E, '\u00AB')  # « opening guillemets
  RIGHT_POINTING_GUILLEMET = (0x123F, 0x1A3F, '\u00BB')  # » closing guillemets

  # Portuguese extended characters
  LATIN_CAPITAL_LETTER_A_WITH_TILDE = (0x1320, 0x1B20, '\u00C3')  # Ã capital A with tilde
  LATIN_SMALL_LETTER_A_WITH_TILDE = (0x1321, 0x1B21, '\u00E3')  # ã small a with tilde
  LATIN_CAPITAL_LETTER_I_WITH_ACUTE = (0x1322, 0x1B22, '\u00CD')  # Í capital I with acute accent
  LATIN_CAPITAL_LETTER_I_WITH_GRAVE = (0x1323, 0x1B23, '\u00CC')  # Ì capital I with grave accent
  LATIN_SMALL_LETTER_I_WITH_GRAVE = (0x1324, 0x1B24, '\u00EC')  # ì small i with grave accent
  LATIN_CAPITAL_LETTER_O_WITH_GRAVE = (0x1325, 0x1B25, '\u00D2')  # Ò capital O with grave accent
  LATIN_SMALL_LETTER_O_WITH_GRAVE = (0x1326, 0x1B26, '\u00F2')  # ò small o with grave accent
  LATIN_CAPITAL_LETTER_O_WITH_TILDE = (0x1327, 0x1B27, '\u00D5')  # Õ capital O with tilde
  LATIN_SMALL_LETTER_O_WITH_TILDE = (0x1328, 0x1B28, '\u00F5')  # õ small o with tilde
  BRACE_OPENING = (0x1329, 0x1B29, '\u007B')  # { opening brace
  BRACE_CLOSING = (0x132A, 0x1B2A, '\u007D')  # } closing brace
  REVERSE_SOLIDUS = (0x132B, 0x1B2B, '\u005C')  # \ backslash
  LATIN_SMALL_LETTER_TURNED_V = (0x132C, 0x1B2C, '\u028C')  # ^ caret
  LOW_LINE = (0x132D, 0x1B2D, '\u005F')  # _ Underbar
  VERTICAL_LINE = (0x132E, 0x1B2E, '\u007C')  # | pipe
  TILDE = (0x132F, 0x1B2F, '\u007E')  # ~ tilde

  # German extended characters
  LATIN_CAPITAL_LETTER_A_WITH_DIAERESIS = (0x1330, 0x1B30, '\u00C4')  # Ä Capital A with diaeresis or umlaut mark
  LATIN_SMALL_LETTER_A_WITH_DIAERESIS = (0x1331, 0x1B31, '\u00E4')  # ä small a with diaeresis or umlaut mark
  LATIN_CAPITAL_LETTER_O_WITH_DIAERESIS = (0x1332, 0x1B32, '\u00D6')  # Ö Capital O with diaeresis or umlaut mark
  LATIN_SMALL_LETTER_O_WITH_DIAERESIS = (0x1333, 0x1B33, '\u00F6')  # ö small o with diaeresis or umlaut mark
  ESZETT = (0x1334, 0x1B34, '\u00DF')  # ß eszett (mall sharp s)
  YEN_SIGN = (0x1335, 0x1B35, '\u00A5')  # ¥ yen
  CURRENCY_SIGN = (0x1336, 0x1B36, '\u00A4')  # ¤ non-specific currency sign
  BOX_DRAWINGS_HEAVY_VERTICAL = (0x1337, 0x1B37, '\u2503')  # | Vertical bar

  # Danish extended characters
  LATIN_CAPITAL_LETTER_A_WITH_RING_ABOVE = (0x1338, 0x1B38, '\u00C5')  # Å capital A with ring
  LATIN_SMALL_LETTER_A_WITH_RING_ABOVE = (0x1339, 0x1B39, '\u00E5')  # å small a with ring
  LATIN_CAPITAL_LETTER_O_WITH_STROKE = (0x133A, 0x1B3A, '\u00D8')  # Ø capital O with slash
  LATIN_SMALL_LETTER_O_WITH_STROKE = (0x133B, 0x1B3B, '\u00F8')  # ø small o with slash
  BOX_DRAWINGS_HEAVY_DOWN_AND_RIGHT = (0x133C, 0x1B3C, '\u250F')  # ⎡ upper left corner
  BOX_DRAWINGS_HEAVY_DOWN_AND_LEFT = (0x133D, 0x1B3D, '\u2513')  # ⎤ upper right corner
  BOX_DRAWINGS_HEAVY_UP_AND_RIGHT = (0x133E, 0x1B3E, '\u2517')  # ⎣ lower left corner
  BOX_DRAWINGS_HEAVY_UP_AND_LEFT = (0x133F, 0x1B3F, '\u251B')  # ⎦ lower right corner

  def __init__(self, channel_1: int, channel_2: int, unicode: chr):
    super().__init__(channel_1, channel_2)
    self._unicode = unicode

  def get_unicode_value(self) -> chr:
    """Returns the special or extended character unicode value"""
    return self._unicode

  @staticmethod
  def find(value: int) -> typing.Optional[SccExtendedCharacter]:
    """Find the special character corresponding to the specified value"""
    for spec_char in list(SccExtendedCharacter):
      if spec_char.contains_value(value):
        return spec_char
    return None
