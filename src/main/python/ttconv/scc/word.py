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

"""SCC word"""

from __future__ import annotations

from ttconv.scc.codes.standard_characters import SCC_STANDARD_CHARACTERS_MAPPING

PARITY_BIT_MASK = 0b01111111


class SccWord:
  """SCC hexadecimal word definition"""

  def __init__(self):
    self.value = None
    self.byte_1 = None
    self.byte_2 = None

  @staticmethod
  def _is_hex_word(word: str) -> bool:
    """Checks whether the specified word is a 2-bytes hexadecimal word"""
    if len(word) != 4:
      return False
    try:
      int(word, 16)
    except ValueError:
      return False
    return True

  @staticmethod
  def _decipher_parity_bit(byte: int):
    """Extracts the byte value removing the odd parity bit"""
    return byte & PARITY_BIT_MASK

  @staticmethod
  def from_value(value: int) -> SccWord:
    """Creates a SCC word from the specified integer value"""
    if value > 0xFFFF:
      raise ValueError("Expected a 2-bytes int value, instead got ", hex(value))
    data = value.to_bytes(2, byteorder='big')
    return SccWord.from_bytes(data[0], data[1])

  @staticmethod
  def from_bytes(byte_1: int, byte_2: int) -> SccWord:
    """Creates a SCC word from the specified bytes"""
    if byte_1 > 0xFF or byte_2 > 0xFF:
      raise ValueError(f"Expected two 1-byte int values, instead got {hex(byte_1)} and {hex(byte_2)}")
    scc_word = SccWord()
    scc_word.byte_1 = SccWord._decipher_parity_bit(byte_1)
    scc_word.byte_2 = SccWord._decipher_parity_bit(byte_2)
    scc_word.value = scc_word.byte_1 * 0x100 + scc_word.byte_2

    return scc_word

  @staticmethod
  def from_str(hex_word: str) -> SccWord:
    """Extracts hexadecimal word bytes to create a SCC word"""
    if not SccWord._is_hex_word(hex_word):
      raise ValueError("Expected a 2-bytes hexadecimal word, instead got ", hex_word)

    data = bytes.fromhex(hex_word)
    return SccWord.from_bytes(data[0], data[1])

  def to_text(self) -> str:
    """Converts SCC word to text"""
    return ''.join(SCC_STANDARD_CHARACTERS_MAPPING.get(byte, chr(byte)) for byte in [self.byte_1, self.byte_2] if byte != 0x00)
