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

"""SCC reader"""

from __future__ import annotations

import logging
import re
from typing import Optional, List

from ttconv.model import Document, P, Body, Div, Text, Span, CellResolutionType
from ttconv.scc.codes.attribute_codes import SccAttributeCode
from ttconv.scc.codes.control_codes import SccControlCode
from ttconv.scc.codes.mid_row_codes import SccMidRowCode
from ttconv.scc.codes.preambles_access_codes import SccPreambleAccessCode
from ttconv.scc.scc_caption_style import SccCaptionStyle
from ttconv.scc.time_codes import SccTimeCode, SMPTE_TIME_CODE_NDF_PATTERN, SMPTE_TIME_CODE_DF_PATTERN
from ttconv.style_properties import StyleProperties, PositionType, LengthType

LOGGER = logging.getLogger(__name__)

SCC_LINE_PATTERN = '((' + SMPTE_TIME_CODE_NDF_PATTERN + ')|(' + SMPTE_TIME_CODE_DF_PATTERN + '))\t.*'

PARITY_BIT_MASK = 0b01111111

DEBUG = False


class _SccContext:
  def __init__(self):
    self.div: Optional[Div] = None
    self.count: int = 0
    self.safe_area_x: int = 0
    self.safe_area_y: int = 0
    self.column_offset = self.safe_area_x
    self.previous_code = 0
    self.previous_paragraph = None
    self.current_text = ""
    self.current_paragraph: Optional[P] = None
    self.current_span: Optional[Span] = None

  def new_paragraph(self):
    """Adds the current P reference to the model if present, and re-initializes it"""
    self.column_offset = self.safe_area_x
    self.current_paragraph = P()
    self.current_paragraph.set_doc(self.div.get_doc())

  def push_span(self):
    """Adds the current Span reference to the model if present, and drop it"""
    if self.current_span and self.current_text:
      self.current_span.push_child(Text(self.div.get_doc(), self.current_text))
      self.current_paragraph.push_child(self.current_span)

      self.current_text = ""
      self.current_span = None

  def new_span(self):
    """Set current Span with a new instance"""
    self.current_span = Span()
    self.current_span.set_doc(self.div.get_doc())

  def process_preamble_access_code(self, pac: SccPreambleAccessCode):
    """Processes SCC Preamble Access Code it to the map to model"""
    self.column_offset += pac.get_indent()
    row_offset = pac.get_row() + self.safe_area_y

    x_cell_offset = self.column_offset
    y_cell_offset = row_offset

    x_position = LengthType(value=x_cell_offset, units=LengthType.Units.c)
    y_position = LengthType(value=y_cell_offset, units=LengthType.Units.c)

    self.current_span.set_style(StyleProperties.Origin, PositionType(x_position, y_position))

    color = pac.get_color()
    if color:
      self.current_span.set_style(StyleProperties.Color, color.value)

    font_style = pac.get_font_style()
    if font_style:
      self.current_span.set_style(StyleProperties.FontStyle, font_style)

    text_decoration = pac.get_text_decoration()
    if text_decoration:
      self.current_span.set_style(StyleProperties.TextDecoration, text_decoration)

  def process_mid_row_code(self, mid_row_code: SccMidRowCode):
    """Processes SCC Mid-Row Code to map it to the model"""
    span_color = mid_row_code.get_color()
    span_font_style = mid_row_code.get_font_style()
    span_text_decoration = mid_row_code.get_text_decoration()

    if span_color:
      self.current_span.set_style(StyleProperties.Color, span_color.value)
    if span_font_style:
      self.current_span.set_style(StyleProperties.FontStyle, span_font_style)
    if span_text_decoration:
      self.current_span.set_style(StyleProperties.TextDecoration, span_text_decoration)

  def process_attribute_code(self, attribute_code: SccAttributeCode):
    """Processes SCC Attribute Code to map it to the model"""
    if attribute_code.is_background():
      self.current_span.set_style(StyleProperties.BackgroundColor, attribute_code.get_color())
    else:
      self.current_span.set_style(StyleProperties.Color, attribute_code.get_color())

    text_decoration = attribute_code.get_text_decoration()
    if text_decoration:
      self.current_span.set_style(StyleProperties.TextDecoration, text_decoration)

  def process_control_code(self, control_code: SccControlCode, time_code: SccTimeCode):
    """Processes SCC Control Code to map it to the model"""
    if control_code is SccControlCode.RCL:
      # Start a new Pop-On caption
      self.new_paragraph()

    if control_code is SccControlCode.EOC:
      # Display caption
      self.push_span()
      self.previous_paragraph = self.current_paragraph
      self.new_span()

      if self.current_paragraph:
        self.count += 1
        self.current_paragraph.set_id("caption" + str(self.count))
        self.current_paragraph.set_begin(time_code.to_temporal_offset())

    if control_code is SccControlCode.EDM:
      # Erase displayed caption
      if self.previous_paragraph:
        self.previous_paragraph.set_end(time_code.to_temporal_offset())
        self.div.push_child(self.previous_paragraph)
        self.previous_paragraph = None

    if control_code is SccControlCode.TO1:
      self.column_offset += 1
    if control_code is SccControlCode.TO2:
      self.column_offset += 2
    if control_code is SccControlCode.TO3:
      self.column_offset += 3


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
    return ''.join(chr(byte) for byte in [self.byte_1, self.byte_2] if byte != 0x00)


class SccLine:
  """SCC line definition"""

  def __init__(self, time_code: SccTimeCode, scc_words: List[SccWord]):
    self.time_code = time_code
    self.scc_words = scc_words

  @staticmethod
  def from_str(line: str) -> Optional[SccLine]:
    """Creates a SCC line instance from the specified string"""
    if line == "":
      return None

    regex = re.compile(SCC_LINE_PATTERN)
    match = regex.match(line)

    if not match:
      return None

    time_code = match.group(1)
    time_offset = SccTimeCode.parse(time_code)

    hex_words = line.split('\t')[1].split(' ')
    scc_words = [SccWord.from_str(hex_word) for hex_word in hex_words if len(hex_word)]
    return SccLine(time_offset, scc_words)

  def get_style(self) -> SccCaptionStyle:
    """Analyses the line words ordering to get the caption style"""
    scc_words = self.scc_words
    if scc_words == "":
      return SccCaptionStyle.Unknown

    prefix = SccControlCode.find(scc_words[0].value)

    if prefix in [SccControlCode.RU2, SccControlCode.RU3, SccControlCode.RU4]:
      return SccCaptionStyle.RollUp

    if prefix is SccControlCode.RDC:
      return SccCaptionStyle.PaintOn

    if prefix is SccControlCode.RCL:
      return SccCaptionStyle.PopOn

    return SccCaptionStyle.Unknown

  def to_model(self, context: _SccContext) -> Optional[P]:
    """Converts the SCC line to the data model"""

    if self.get_style() not in (SccCaptionStyle.PopOn, SccCaptionStyle.Unknown):
      raise ValueError(f"Unsupported caption style: {self.get_style()}")

    debug = str(self.time_code) + "\t"

    for scc_word in self.scc_words:

      if context.previous_code == scc_word.value:
        continue

      self.time_code.add_frames()

      if scc_word.value == 0x0000:
        continue

      if scc_word.byte_1 < 0x20:

        attribute_code = SccAttributeCode.find(scc_word.value)
        control_code = SccControlCode.find(scc_word.value)
        mid_row_code = SccMidRowCode.find(scc_word.value)
        pac = SccPreambleAccessCode.find(scc_word.byte_1, scc_word.byte_2)

        if pac:
          debug += "[PAC|" + str(pac.get_row()) + "|" + str(pac.get_color().name) + "/" + hex(scc_word.value) + "]"
          context.push_span()
          context.new_span()
          context.process_preamble_access_code(pac)

        elif attribute_code:
          debug += "[ATC/" + hex(scc_word.value) + "]"
          context.process_attribute_code(attribute_code)

        elif mid_row_code:
          debug += "[MRC|" + mid_row_code.get_name() + "/" + hex(scc_word.value) + "]"
          context.push_span()
          context.new_span()
          context.process_mid_row_code(mid_row_code)

        elif control_code:
          debug += "[CC|" + control_code.get_name() + "/" + hex(scc_word.value) + "]"

          context.process_control_code(control_code, self.time_code)
          context.previous_code = scc_word.value

        else:
          debug += "[??/" + hex(scc_word.value) + "]"

        context.previous_code = scc_word.value

      else:
        word = scc_word.to_text()
        debug += word
        context.current_text += word
        context.previous_code = scc_word.value

    if DEBUG:
      print(debug)

    if not context.current_span:
      return None

    return context.current_paragraph


#
# scc reader
#

def to_model(scc_content: str):
  """Converts a SCC document to the data model"""

  context = _SccContext()
  document = Document()

  # safe area must be a 32x15 grid, that represents 80% of the root area
  root_cell_resolution = CellResolutionType(rows=19, columns=40)
  document.set_cell_resolution(root_cell_resolution)

  context.safe_area_x = (root_cell_resolution.columns - 32) / 2
  context.safe_area_y = (root_cell_resolution.rows - 15) / 2

  body = Body()
  body.set_doc(document)
  document.set_body(body)

  context.div = Div()
  context.div.set_doc(document)
  body.push_child(context.div)

  for line in scc_content.splitlines():
    if DEBUG:
      print(line)
    scc_line = SccLine.from_str(line)
    if not scc_line:
      continue

    scc_line.to_model(context)

  return document
