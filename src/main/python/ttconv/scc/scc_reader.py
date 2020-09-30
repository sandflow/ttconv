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


class _SccContext:
  def __init__(self):
    self.div: Optional[Div] = None
    self.count: int = 0
    self.safe_area_x: int = 0
    self.safe_area_y: int = 0


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
    return ''.join([chr(self.byte_1), chr(self.byte_2)])


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

    paragraph = P()
    doc = context.div.get_doc()
    paragraph.set_doc(doc)
    paragraph.set_begin(self.time_code.get_fraction())

    text = ""
    debug = ""
    span = None

    previous_code = None

    column_offset = context.safe_area_x

    for scc_word in self.scc_words:

      if scc_word.byte_1 < 0x20:

        attribute_code = SccAttributeCode.find(scc_word.value)
        control_code = SccControlCode.find(scc_word.value)
        mid_row_code = SccMidRowCode.find(scc_word.value)
        pac = SccPreambleAccessCode.find(scc_word.byte_1, scc_word.byte_2)

        if previous_code and previous_code in [code for code in
                                               (attribute_code, control_code, mid_row_code, pac) if
                                               code is not None]:
          continue

        if control_code:
          if control_code is SccControlCode.TO1:
            column_offset += 1
          if control_code is SccControlCode.TO2:
            column_offset += 2
          if control_code is SccControlCode.TO3:
            column_offset += 3
          previous_code = control_code

        elif mid_row_code:
          span_color = mid_row_code.get_color()
          span_font_style = mid_row_code.get_font_style()
          span_text_decoration = mid_row_code.get_text_decoration()

          if span_color:
            span.set_style(StyleProperties.Color, span_color.value)
          if span_font_style:
            span.set_style(StyleProperties.FontStyle, span_font_style)
          if span_text_decoration:
            span.set_style(StyleProperties.TextDecoration, span_text_decoration)
          previous_code = mid_row_code

        elif pac:
          if span and isinstance(previous_code, str):
            text_elem = Text(doc, text)
            span.push_child(text_elem)

            paragraph.push_child(span)

            text = ""

          column_offset += pac.get_indent()
          row_offset = pac.get_row() + context.safe_area_y

          # create new span
          span = Span()
          span.set_doc(doc)

          x_pct = column_offset / doc.get_cell_resolution().columns
          y_pct = row_offset / doc.get_cell_resolution().rows

          x_position = LengthType(value=x_pct, units=LengthType.Units.pct)
          y_position = LengthType(value=y_pct, units=LengthType.Units.pct)

          span.set_style(StyleProperties.Origin, PositionType(x_position, y_position))

          color = pac.get_color()
          if color:
            span.set_style(StyleProperties.Color, color.value)

          font_style = pac.get_font_style()
          if font_style:
            span.set_style(StyleProperties.FontStyle, font_style)

          text_decoration = pac.get_text_decoration()
          if text_decoration:
            span.set_style(StyleProperties.TextDecoration, text_decoration)

          previous_code = pac

        elif attribute_code:
          # TODO handle attribute code
          pass

      else:
        word = scc_word.to_text()
        text += word
        previous_code = word


    if not span:
      return None

    text_elem = Text(doc, text)
    span.push_child(text_elem)

    paragraph.push_child(span)

    context.count += 1
    paragraph.set_id("caption" + str(context.count))

    return paragraph


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
    scc_line = SccLine.from_str(line)
    if not scc_line:
      continue

    paragraph = scc_line.to_model(context)

    if paragraph:
      context.div.push_child(paragraph)

  return document
