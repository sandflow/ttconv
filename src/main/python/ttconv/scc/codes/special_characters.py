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

"""SCC Special characters"""

from __future__ import annotations

import typing

from ttconv.scc.codes import SccCode


class SccSpecialCharacter(SccCode):
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
