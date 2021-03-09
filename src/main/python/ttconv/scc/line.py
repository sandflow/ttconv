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

"""SCC line"""

from __future__ import annotations

import logging
import re
from typing import List, Optional

from ttconv.scc.codes.attribute_codes import SccAttributeCode
from ttconv.scc.codes.control_codes import SccControlCode
from ttconv.scc.codes.mid_row_codes import SccMidRowCode
from ttconv.scc.codes.preambles_address_codes import SccPreambleAddressCode
from ttconv.scc.codes.special_characters import SccSpecialCharacter, SccExtendedCharacter
from ttconv.scc.disassembly import get_color_disassembly, get_font_style_disassembly, get_text_decoration_disassembly
from ttconv.scc.style import SccCaptionStyle
from ttconv.scc.word import SccWord
from ttconv.time_code import SmpteTimeCode, FPS_30

LOGGER = logging.getLogger(__name__)

SCC_LINE_PATTERN = '((' + SmpteTimeCode.SMPTE_TIME_CODE_NDF_PATTERN + ')|(' + SmpteTimeCode.SMPTE_TIME_CODE_DF_PATTERN + '))\t.*'


class SccLine:
  """SCC line definition"""

  def __init__(self, time_code: SmpteTimeCode, scc_words: List[SccWord]):
    self.time_code = time_code
    self.scc_words = scc_words

  @staticmethod
  def from_str(line: str) -> Optional[SccLine]:
    """Creates a SCC line instance from the specified string"""
    if not line:
      return None

    regex = re.compile(SCC_LINE_PATTERN)
    match = regex.match(line)

    if match is None:
      return None

    time_code = match.group(1)
    time_offset = SmpteTimeCode.parse(time_code, FPS_30)

    hex_words = line.split('\t')[1].split(' ')
    scc_words = [SccWord.from_str(hex_word) for hex_word in hex_words if hex_word]
    return SccLine(time_offset, scc_words)

  def get_style(self) -> SccCaptionStyle:
    """Analyses the line words to find SCC control codes and define the caption style"""
    scc_words = self.scc_words
    if not scc_words:
      return SccCaptionStyle.Unknown

    for word in scc_words:
      prefix = SccControlCode.find(word.value)

      if prefix in [SccControlCode.RU2, SccControlCode.RU3, SccControlCode.RU4]:
        return SccCaptionStyle.RollUp

      if prefix is SccControlCode.RDC:
        return SccCaptionStyle.PaintOn

      if prefix is SccControlCode.RCL:
        return SccCaptionStyle.PopOn

    return SccCaptionStyle.Unknown

  def to_disassembly(self) -> str:
    """Converts SCC line into the disassembly format"""
    disassembly_line = str(self.time_code) + "\t"

    for scc_word in self.scc_words:

      if scc_word.value == 0x0000:
        disassembly_line += "{}"
        continue

      if scc_word.byte_1 < 0x20:

        attribute_code = SccAttributeCode.find(scc_word.value)
        control_code = SccControlCode.find(scc_word.value)
        mid_row_code = SccMidRowCode.find(scc_word.value)
        pac = SccPreambleAddressCode.find(scc_word.byte_1, scc_word.byte_2)
        spec_char = SccSpecialCharacter.find(scc_word.value)
        extended_char = SccExtendedCharacter.find(scc_word.value)

        if pac is not None:
          disassembly_line += f"{{{pac.get_row():02}"
          color = pac.get_color()
          indent = pac.get_indent()
          if indent is not None and indent > 0:
            disassembly_line += f"{indent :02}"
          elif color is not None:
            disassembly_line += get_color_disassembly(color)
            disassembly_line += get_font_style_disassembly(pac.get_font_style())
            disassembly_line += get_text_decoration_disassembly(pac.get_text_decoration())
          else:
            disassembly_line += "00"
          disassembly_line += "}"

        elif attribute_code is not None:
          disassembly_line += "{"
          disassembly_line += "B" if attribute_code.is_background() else ""
          disassembly_line += get_color_disassembly(attribute_code.get_color())
          disassembly_line += get_text_decoration_disassembly(attribute_code.get_text_decoration())
          disassembly_line += "}"

        elif mid_row_code is not None:
          disassembly_line += "{"
          disassembly_line += get_color_disassembly(mid_row_code.get_color())
          disassembly_line += get_font_style_disassembly(mid_row_code.get_font_style())
          disassembly_line += get_text_decoration_disassembly(mid_row_code.get_text_decoration())
          disassembly_line += "}"

        elif control_code is not None:
          disassembly_line += "{" + control_code.get_name() + "}"

        elif spec_char is not None:
          disassembly_line += spec_char.get_unicode_value()

        elif extended_char is not None:
          disassembly_line += extended_char.get_unicode_value()

        else:
          disassembly_line += "{??}"
          LOGGER.warning("Unsupported SCC word: %s", hex(scc_word.value))

      else:
        disassembly_line += scc_word.to_text()

    return disassembly_line
