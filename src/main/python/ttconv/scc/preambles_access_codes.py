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

"""SCC Preamble Access Codes"""

from __future__ import annotations

from typing import Optional

from ttconv.style_properties import NamedColors, TextDecorationType, \
  FontStyleType


class _SccPacDescriptionBits:
  """Helper class for SCC PAC description bits handling"""
  def __init__(self, bits: int):
    self._bits = bits

  def get_underline(self) -> bool:
    """Returns whether the PAC description bits sets the underline decoration"""
    return self._bits % 2 == 1

  def get_italic(self) -> bool:
    """Returns whether the PAC description bits sets the italic style"""
    return self._bits in [0x0E, 0x0F]

  def get_color(self) -> Optional[NamedColors]:
    """Returns the color from the PAC description bits"""

    if self._bits not in list(range(0x00, 0x20)):
      return None

    if self._bits in [0x00, 0x01]:
      return NamedColors.white

    if self._bits in [0x02, 0x03]:
      return NamedColors.green

    if self._bits in [0x04, 0x05]:
      return NamedColors.blue

    if self._bits in [0x06, 0x07]:
      return NamedColors.cyan

    if self._bits in [0x08, 0x09]:
      return NamedColors.red

    if self._bits in [0x0A, 0x0B]:
      return NamedColors.yellow

    if self._bits in [0x0C, 0x0D]:
      return NamedColors.yellow

    if self._bits > 0x0D:
      return NamedColors.white

    return None

  def get_indent(self) -> Optional[int]:
    """Returns the column offset from the PAC description bits"""
    if self._bits in list(range(0x10, 0x20)):
      return (self._bits - 0x10) - (self._bits % 2) * 4

    return None


class SccPreambleAccessCode:
  """SCC PAC definition"""

  def __init__(self, row: int,
               color: Optional[NamedColors] = None,
               italic=False,
               underline=False,
               indent: Optional[int] = None):
    self._row = row
    self._indent = indent
    self._color = color
    self._font_style = FontStyleType.italic if italic else None
    self._text_decoration = TextDecorationType.underline if underline else None

  def get_row(self) -> int:
    """Returns the PAC row"""
    return self._row

  def get_indent(self) -> Optional[int]:
    """Returns PAC column offset"""
    return self._indent

  def get_color(self) -> Optional[NamedColors]:
    """Returns PAC color"""
    return self._color

  def get_font_style(self) -> Optional[FontStyleType]:
    """Returns PAC font style"""
    return self._font_style

  def get_text_decoration(self) -> Optional[TextDecorationType]:
    """Returns PAC text decoration"""
    return self._text_decoration

  @staticmethod
  def from_bytes(byte_1: int, byte_2: int) -> Optional[SccPreambleAccessCode]:
    """Decodes SCC PAC from specified bytes"""
    row = SccPreambleAccessCode._get_row(byte_1, byte_2)
    desc_bits = SccPreambleAccessCode._get_description_bits(byte_2)

    if row is None or desc_bits is None:
      return None

    color = desc_bits.get_color()
    indent = desc_bits.get_indent()
    underline = desc_bits.get_underline()
    italic = desc_bits.get_italic()

    return SccPreambleAccessCode(row, color, italic, underline, indent)

  @staticmethod
  def _get_row(byte_1: int, byte_2: int) -> Optional[int]:
    """Decodes SCC PAC row number from specified bytes"""
    if byte_1 not in list(range(0x10, 0x20)):
      return None

    row_bits = ((byte_1 & 0x0F) % 0X08, byte_2 & 0x60)

    if row_bits == (0x01, 0x40):
      return 1
    if row_bits == (0x01, 0x60):
      return 2
    if row_bits == (0x02, 0x40):
      return 3
    if row_bits == (0x02, 0x60):
      return 4
    if row_bits == (0x05, 0x40):
      return 5
    if row_bits == (0x05, 0x60):
      return 6
    if row_bits == (0x06, 0x40):
      return 7
    if row_bits == (0x06, 0x60):
      return 8
    if row_bits == (0x07, 0x40):
      return 9
    if row_bits == (0x07, 0x60):
      return 10
    if row_bits == (0x00, 0x40):
      return 11
    if row_bits == (0x03, 0x40):
      return 12
    if row_bits == (0x03, 0x60):
      return 13
    if row_bits == (0x04, 0x40):
      return 14
    if row_bits == (0x04, 0x60):
      return 15

    return None

  @staticmethod
  def _get_description_bits(byte_2: int) -> Optional[_SccPacDescriptionBits]:
    """Extracts descriptions bits from second byte of the input pair"""
    if byte_2 not in list(range(0x40, 0x80)):
      return None
    return _SccPacDescriptionBits(byte_2 & 0x1F)
