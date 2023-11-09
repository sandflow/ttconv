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

from ttconv.scc.caption_style import SccCaptionStyle
from ttconv.scc.codes import SccChannel
from ttconv.scc.codes.attribute_codes import SccAttributeCode
from ttconv.scc.codes.control_codes import SccControlCode
from ttconv.scc.codes.extended_characters import SccExtendedCharacter
from ttconv.scc.codes.mid_row_codes import SccMidRowCode
from ttconv.scc.codes.preambles_address_codes import SccPreambleAddressCode
from ttconv.scc.codes.special_characters import SccSpecialCharacter
from ttconv.scc.context import SccContext
from ttconv.scc.disassembly import get_scc_word_disassembly
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

  def to_disassembly(self, show_channels = False) -> str:
    """Converts SCC line into the disassembly format"""
    disassembly_line = str(self.time_code) + "\t"

    for scc_word in self.scc_words:
      disassembly_line += get_scc_word_disassembly(scc_word, show_channels)

    return disassembly_line

  def process(self, context: SccContext) -> SmpteTimeCode:
    """Converts the SCC line to the data model"""

    debug = str(self.time_code) + "\t"

    for scc_word in self.scc_words:

      if context.previous_word is not None and context.previous_word.value == scc_word.value and context.previous_word.is_code():
        context.previous_word = None
        continue

      self.time_code.add_frames()

      if scc_word.value == 0x0000:
        continue

      if scc_word.byte_1 < 0x20:

        scc_code = scc_word.get_code()
        caption_channel = scc_word.get_channel()

        if caption_channel is not SccChannel.CHANNEL_1:
          if context.current_channel is not caption_channel:
            LOGGER.warning("Skip Caption Channel 2 content")
          context.current_channel = caption_channel
          continue

        context.current_channel = caption_channel

        if isinstance(scc_code, SccPreambleAddressCode):
          debug += scc_code.debug(scc_word.value)
          context.process_preamble_address_code(scc_code, self.time_code)
          context.previous_word_type = type(scc_code)

        elif isinstance(scc_code, SccAttributeCode):
          debug += scc_code.debug(scc_word.value)
          context.process_attribute_code(scc_code)
          context.previous_word_type = type(scc_code)

        elif isinstance(scc_code, SccMidRowCode):
          debug += scc_code.debug(scc_word.value)
          context.process_mid_row_code(scc_code, self.time_code)
          context.previous_word_type = type(scc_code)

        elif isinstance(scc_code, SccControlCode):
          debug += scc_code.debug(scc_word.value)
          context.process_control_code(scc_code, self.time_code)
          context.previous_word_type = type(scc_code)

        elif isinstance(scc_code, SccSpecialCharacter):
          word = scc_code.get_unicode_value()
          debug += word
          context.process_text(word, self.time_code)
          context.previous_word_type = type(scc_code)

        elif isinstance(scc_code, SccExtendedCharacter):
          context.backspace()

          word = scc_code.get_unicode_value()
          debug += word
          context.process_text(word, self.time_code)
          context.previous_word_type = type(scc_code)

        else:
          debug += "[??/" + hex(scc_word.value) + "]"
          LOGGER.warning("Unsupported SCC word: %s", hex(scc_word.value))
          context.previous_word_type = None

      else:
        if context.current_channel is not SccChannel.CHANNEL_1:
          # LOGGER.warning("Skip Caption Channel 2 code")
          continue

        text = scc_word.to_text()
        debug += text
        context.process_text(text, self.time_code)
        context.previous_word_type = str

      context.previous_word = scc_word

    LOGGER.debug(debug)

    return self.time_code
