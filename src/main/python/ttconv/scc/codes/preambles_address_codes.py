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

"""SCC Preamble Address Codes"""

from __future__ import annotations

from typing import Optional

from ttconv.scc.codes import SCC_COLOR_MAPPING
from ttconv.style_properties import NamedColors, TextDecorationType, \
  FontStyleType, ColorType

_ROW_MAPPING = {
  (0x01, 0x40): 1,
  (0x01, 0x60): 2,
  (0x02, 0x40): 3,
  (0x02, 0x60): 4,
  (0x05, 0x40): 5,
  (0x05, 0x60): 6,
  (0x06, 0x40): 7,
  (0x06, 0x60): 8,
  (0x07, 0x40): 9,
  (0x07, 0x60): 10,
  (0x00, 0x40): 11,
  (0x03, 0x40): 12,
  (0x03, 0x60): 13,
  (0x04, 0x40): 14,
  (0x04, 0x60): 15
}


class _SccPacDescriptionBits:
  """Helper class for SCC PAC description bits handling"""

  def __init__(self, bits: int):
    self._bits = bits

  def get_underline(self) -> bool:
    """Returns whether the PAC description bits sets the underline decoration"""
    return self._bits % 2 == 1

  def get_italic(self) -> bool:
    """Returns whether the PAC description bits sets the italic style"""
    return self._bits in (0x0E, 0x0F)

  def get_color(self) -> Optional[ColorType]:
    """Returns the color from the PAC description bits"""

    if self._bits not in list(range(0x00, 0x10)):
      return None

    if self._bits in (0x00, 0x01, 0x0E, 0x0F):
      return NamedColors.white.value

    return SCC_COLOR_MAPPING.get(self._bits, None)

  def get_indent(self) -> Optional[int]:
    """Returns the column offset from the PAC description bits"""
    if self._bits in list(range(0x10, 0x20)):
      return ((self._bits - 0x10) - (self._bits % 2)) * 2

    return None


class SccPreambleAddressCode:
  """SCC PAC definition"""

  def __init__(self, byte_1: int, byte_2: int):
    row = SccPreambleAddressCode._get_row(byte_1, byte_2)
    if row is None:
      raise ValueError("Failed to extract PAC row from specified bytes:", hex(byte_1), hex(byte_2))

    desc_bits = SccPreambleAddressCode._get_description_bits(byte_2)
    if desc_bits is None:
      raise ValueError("Failed to extract PAC description from specified bytes:", hex(byte_1), hex(byte_2))

    self._row = row
    self._color: Optional[ColorType] = desc_bits.get_color()
    self._indent: Optional[int] = desc_bits.get_indent()
    self._font_style: Optional[bool] = FontStyleType.italic if desc_bits.get_italic() else None
    self._text_decoration: Optional[TextDecorationType] = \
      TextDecorationType(underline=True) if desc_bits.get_underline() else None
    self._channel = 2 if byte_1 & 0x08 else 1

  def get_row(self) -> int:
    """Returns the PAC row"""
    return self._row

  def get_indent(self) -> Optional[int]:
    """Returns PAC column offset"""
    return self._indent

  def get_color(self) -> Optional[ColorType]:
    """Returns PAC color"""
    return self._color

  def get_font_style(self) -> Optional[FontStyleType]:
    """Returns PAC font style"""
    return self._font_style

  def get_text_decoration(self) -> Optional[TextDecorationType]:
    """Returns PAC text decoration"""
    return self._text_decoration

  def get_channel(self):
    """Returns PAC channel"""
    return self._channel

  def __eq__(self, other) -> bool:
    """Overrides default implementation"""
    return isinstance(other, SccPreambleAddressCode) \
           and self.get_row() == other.get_row() \
           and self.get_indent() == other.get_indent() \
           and self.get_color() == other.get_color() \
           and self.get_font_style() == other.get_font_style() \
           and self.get_text_decoration() == other.get_text_decoration()

  @staticmethod
  def find(byte_1: int, byte_2: int) -> Optional[SccPreambleAddressCode]:
    """Find the SCC PAC corresponding to the specified bytes"""
    try:
      return SccPreambleAddressCode(byte_1, byte_2)
    except ValueError as _e:
      return None

  @staticmethod
  def _get_row(byte_1: int, byte_2: int) -> Optional[int]:
    """Decodes SCC PAC row number from specified bytes"""
    if byte_1 not in list(range(0x10, 0x20)):
      return None

    row_bits = ((byte_1 & 0x0F) % 0X08, byte_2 & 0x60)

    return _ROW_MAPPING.get(row_bits, None)

  @staticmethod
  def _get_description_bits(byte_2: int) -> Optional[_SccPacDescriptionBits]:
    """Extracts descriptions bits from second byte of the input pair"""
    if byte_2 not in list(range(0x40, 0x80)):
      return None
    return _SccPacDescriptionBits(byte_2 & 0x1F)
