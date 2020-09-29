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

"""SCC Mid Row Codes"""

from __future__ import annotations

import typing
from enum import Enum

from ttconv.style_properties import NamedColors, FontStyleType, TextDecorationType


class SccMidRowCode(Enum):
  """SCC Mid-Row Code values"""
  WHITE = (0x1120, 0x1920)
  WHITE_UNDERLINE = (0x1121, 0x1921)
  GREEN = (0x1122, 0x1922)
  GREEN_UNDERLINE = (0x1123, 0x1923)
  BLUE = (0x1124, 0x1924)
  BLUE_UNDERLINE = (0x1125, 0x1925)
  CYAN = (0x1126, 0x1926)
  CYAN_UNDERLINE = (0x1127, 0x1927)
  RED = (0x1128, 0x1928)
  RED_UNDERLINE = (0x1129, 0x1929)
  YELLOW = (0x112A, 0x192A)
  YELLOW_UNDERLINE = (0x112B, 0x192B)
  MAGENTA = (0x112C, 0x192C)
  MAGENTA_UNDERLINE = (0x112D, 0x192D)
  ITALICS = (0x112E, 0x192E)
  ITALICS_UNDERLINE = (0x112F, 0x192F)

  def __init__(self, channel_1_value: int, channel_2_value: int):
    self._channel_1 = channel_1_value
    self._channel_2 = channel_2_value

  def get_name(self) -> str:
    """Retrieves SCC Mid-Row Code name"""
    return self.name

  def get_color(self) -> typing.Optional[NamedColors]:
    """Returns SCC Mid-Row Code color"""
    style_bits = self._channel_1 & 0x000F

    if style_bits in [0x00, 0x01]:
      return NamedColors.white
    if style_bits in [0x02, 0x03]:
      return NamedColors.green
    if style_bits in [0x04, 0x05]:
      return NamedColors.blue
    if style_bits in [0x06, 0x07]:
      return NamedColors.cyan
    if style_bits in [0x08, 0x09]:
      return NamedColors.red
    if style_bits in [0x0A, 0x0B]:
      return NamedColors.yellow
    if style_bits in [0x0C, 0x0D]:
      return NamedColors.magenta

    return None

  def get_font_style(self) -> typing.Optional[FontStyleType]:
    """Returns SCC Mid-Row Code font style"""
    style_bits = self._channel_1 & 0x000F

    if style_bits in [0x0E, 0x0F]:
      return FontStyleType.italic

    return None

  def get_text_decoration(self) -> typing.Optional[TextDecorationType]:
    """Returns SCC Mid-Row Code text decoration"""
    style_bits = self._channel_1 & 0x000F

    if style_bits % 2 == 1:
      return TextDecorationType.underline

    return None

  def contains_value(self, value: int) -> bool:
    """Returns whether the specified value is contained into the Mid-Row Code channel values"""
    return value in [self._channel_1, self._channel_2]

  @staticmethod
  def find(value: int) -> typing.Optional[SccMidRowCode]:
    """Find the Mid-Row Code corresponding to the specified value"""
    for mid_row_code in list(SccMidRowCode):
      if mid_row_code.contains_value(value):
        return mid_row_code
    return None
