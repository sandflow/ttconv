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

import copy
import logging
import re
from typing import Optional, List

from ttconv.model import Document, P, Body, Div, Text, Span, CellResolutionType, Br
from ttconv.scc.codes.attribute_codes import SccAttributeCode
from ttconv.scc.codes.control_codes import SccControlCode
from ttconv.scc.codes.mid_row_codes import SccMidRowCode
from ttconv.scc.codes.preambles_access_codes import SccPreambleAccessCode
from ttconv.scc.codes.special_characters import SccSpecialAndExtendedCharacter
from ttconv.scc.scc_caption_style import SccCaptionStyle
from ttconv.scc.time_codes import SccTimeCode, SMPTE_TIME_CODE_NDF_PATTERN, SMPTE_TIME_CODE_DF_PATTERN
from ttconv.style_properties import StyleProperties, PositionType, LengthType

LOGGER = logging.getLogger(__name__)

SCC_LINE_PATTERN = '((' + SMPTE_TIME_CODE_NDF_PATTERN + ')|(' + SMPTE_TIME_CODE_DF_PATTERN + '))\t.*'

PARITY_BIT_MASK = 0b01111111

DEBUG = False


class SccCaptionText:
  """Caption text content"""

  def __init__(self):
    self.x_offset: int = 0
    self.y_offset: int = 0
    self.style_properties = {}
    self.text: str = ""
    self._position = None

  def set_x_offset(self, indent: Optional[int]):
    """Sets the x offset"""
    self.x_offset = indent if indent else 0

  def set_y_offset(self, row: Optional[int]):
    """Sets the y offset"""
    self.y_offset = row if row else 0

  def add_style_property(self, style_property, value):
    """Adds a style property"""
    if value is None:
      return
    self.style_properties[style_property] = value

  def get_position(self) -> PositionType:
    """Returns current row and column offsets as a cell-based PositionType"""
    x_position = LengthType(value=self.x_offset, units=LengthType.Units.c)
    y_position = LengthType(value=self.y_offset, units=LengthType.Units.c)

    return PositionType(x_position, y_position)

  def is_contiguous(self, other: SccCaptionText) -> bool:
    """Returns whether the current text is contiguous according to the other text"""
    return self.x_offset == other.x_offset and self.y_offset == other.y_offset + 1 and self.style_properties == other.style_properties


class SccCaptionParagraph:
  """Caption paragraph"""

  def __init__(self, safe_area_x_offset: int = 0, safe_area_y_offset: int = 0,
               caption_style: SccCaptionStyle = SccCaptionStyle.Unknown):
    self._caption_id: str = ""
    self._begin: Optional[SccTimeCode] = None
    self._end: Optional[SccTimeCode] = None
    self._safe_area_x_offset = safe_area_x_offset
    self._safe_area_y_offset = safe_area_y_offset
    self._column_offset: int = safe_area_x_offset
    self._row_offset: int = safe_area_y_offset
    self.current_text: Optional[SccCaptionText] = None
    self.caption_texts: List[SccCaptionText] = []
    self._style: SccCaptionStyle = caption_style

  def set_id(self, caption_id: str):
    """Sets caption identifier"""
    self._caption_id = caption_id

  def set_begin(self, time_code):
    """Sets caption begin time code"""
    self._begin = copy.copy(time_code)

  def set_end(self, time_code):
    """Sets caption end time code"""
    self._end = copy.copy(time_code)

  def set_column_offset(self, indent: Optional[int]):
    """Sets the paragraph x offset"""
    self._column_offset = self._safe_area_x_offset + (indent if indent else 0)

  def set_row_offset(self, row: Optional[int]):
    """Sets the paragraph y offset"""
    self._row_offset = self._safe_area_y_offset + (row if row else 0)

  def new_caption_line(self):
    """Appends a new caption text content, and keeps reference on it"""
    self.caption_texts.append(SccCaptionText())
    self.current_text = self.caption_texts[-1]

  def set_current_text_offsets(self):
    """Sets the x and y offsets of the current text"""
    self.current_text.set_x_offset(self._column_offset)
    self.current_text.set_y_offset(self._row_offset)

  def indent(self, indent: int):
    """Indents the current text (x offset)"""
    self._column_offset += indent
    self.current_text.set_x_offset(self._column_offset)

  def to_paragraph(self, doc: Document) -> P:
    """Converts and returns current caption paragraph into P instance"""
    p = P()
    p.set_doc(doc)
    p.set_id(self._caption_id)
    p.set_begin(self._begin.to_temporal_offset())
    p.set_end(self._end.to_temporal_offset())

    last_line: Optional[SccCaptionText] = None
    last_span: Optional[Span] = None

    for caption_line in self.caption_texts:

      if self._style is SccCaptionStyle.PopOn and last_span and last_line and caption_line.is_contiguous(last_line):
        last_span.push_child(Br(doc))
        last_span.push_child(Text(doc, caption_line.text))

      else:
        span = Span(doc)

        origin = caption_line.get_position()
        span.set_style(StyleProperties.Origin, origin)

        for (prop, value) in caption_line.style_properties.items():
          span.set_style(prop, value)

        span.push_child(Text(doc, caption_line.text))

        p.push_child(span)
        last_span = span

      last_line = caption_line

    return p


class _SccContext:
  def __init__(self):
    self.div: Optional[Div] = None
    # self.regions: List[Region] = []
    self.count: int = 0
    self.safe_area_x_offset: int = 0
    self.safe_area_y_offset: int = 0
    self.previous_code = 0
    self.current_caption: Optional[SccCaptionParagraph] = None
    self.previous_caption: Optional[SccCaptionParagraph] = None

  def set_safe_area(self, safe_area_x_offset: int, safe_area_y_offset: int):
    """Sets the safe area"""
    self.safe_area_x_offset = safe_area_x_offset
    self.safe_area_y_offset = safe_area_y_offset

  def set_current_to_previous(self):
    """Rotates current caption to previous caption"""
    self.previous_caption = self.current_caption
    self.current_caption = None

  def init_current_caption(self, time_code: SccTimeCode):
    """Initializes the current caption with id and begin time"""
    if self.current_caption:
      self.count += 1
      self.current_caption.set_id("caption" + str(self.count))
      self.current_caption.set_begin(time_code)

  def close_previous_caption(self, time_code: SccTimeCode):
    """Sets previous caption end time, pushes it into the data model and resets it"""
    if self.previous_caption:
      self.previous_caption.set_end(time_code)
      self.div.push_child(self.previous_caption.to_paragraph(self.div.get_doc()))
      self.previous_caption = None

  def process_preamble_access_code(self, pac: SccPreambleAccessCode):
    """Processes SCC Preamble Access Code it to the map to model"""
    if not self.current_caption:
      raise ValueError("No current SCC caption initialized")

    self.current_caption.new_caption_line()

    self.current_caption.set_column_offset(pac.get_indent())
    self.current_caption.set_row_offset(pac.get_row())
    self.current_caption.set_current_text_offsets()

    self.current_caption.current_text.add_style_property(StyleProperties.Color, pac.get_color())
    self.current_caption.current_text.add_style_property(StyleProperties.FontStyle, pac.get_font_style())
    self.current_caption.current_text.add_style_property(StyleProperties.TextDecoration, pac.get_text_decoration())

  def process_mid_row_code(self, mid_row_code: SccMidRowCode):
    """Processes SCC Mid-Row Code to map it to the model"""
    if not self.current_caption:
      raise ValueError("No current SCC caption initialized")

    self.current_caption.new_caption_line()
    self.current_caption.set_current_text_offsets()

    self.current_caption.current_text.add_style_property(StyleProperties.Color, mid_row_code.get_color())
    self.current_caption.current_text.add_style_property(StyleProperties.FontStyle, mid_row_code.get_font_style())
    self.current_caption.current_text.add_style_property(StyleProperties.TextDecoration, mid_row_code.get_text_decoration())

  def process_attribute_code(self, attribute_code: SccAttributeCode):
    """Processes SCC Attribute Code to map it to the model"""
    if not self.current_caption or not self.current_caption.current_text:
      raise ValueError("No current SCC caption nor content initialized")

    if attribute_code.is_background():
      self.current_caption.current_text.add_style_property(StyleProperties.BackgroundColor, attribute_code.get_color())
    else:
      self.current_caption.current_text.add_style_property(StyleProperties.Color, attribute_code.get_color())

    self.current_caption.current_text.add_style_property(StyleProperties.TextDecoration, attribute_code.get_text_decoration())

  def process_control_code(self, control_code: SccControlCode, time_code: SccTimeCode):
    """Processes SCC Control Code to map it to the model"""

    if control_code is SccControlCode.RCL:
      # Start a new Pop-On caption
      self.current_caption = SccCaptionParagraph(self.safe_area_x_offset, self.safe_area_y_offset, SccCaptionStyle.PopOn)


    if control_code is SccControlCode.EOC:
      # Display caption (Pop-On)
      self.init_current_caption(time_code)
      self.set_current_to_previous()

    if control_code is SccControlCode.EDM:
      # Erase displayed caption (Pop-On)
      self.close_previous_caption(time_code)

    if control_code is SccControlCode.TO1:
      self.current_caption.indent(1)
    if control_code is SccControlCode.TO2:
      self.current_caption.indent(2)
    if control_code is SccControlCode.TO3:
      self.current_caption.indent(3)

  def process_text(self, word):
    """Processes SCC text words"""
    self.current_caption.current_text.text += word


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

  def to_model(self, context: _SccContext):
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
        spec_char = SccSpecialAndExtendedCharacter.find(scc_word.value)

        if pac:
          debug += "[PAC|" + str(pac.get_row()) + "|" + str(pac.get_indent())
          if pac.get_color():
            debug += "|" + str(pac.get_color())
          debug += "/" + hex(scc_word.value) + "]"
          context.process_preamble_access_code(pac)

        elif attribute_code:
          debug += "[ATC/" + hex(scc_word.value) + "]"
          context.process_attribute_code(attribute_code)

        elif mid_row_code:
          debug += "[MRC|" + mid_row_code.get_name() + "/" + hex(scc_word.value) + "]"
          context.process_mid_row_code(mid_row_code)

        elif control_code:
          debug += "[CC|" + control_code.get_name() + "/" + hex(scc_word.value) + "]"
          context.process_control_code(control_code, self.time_code)

        elif spec_char:
          word = spec_char.get_unicode_value()
          debug += word
          context.process_text(word)

        else:
          debug += "[??/" + hex(scc_word.value) + "]"

        context.previous_code = scc_word.value

      else:
        word = scc_word.to_text()
        debug += word
        context.process_text(word)
        context.previous_code = scc_word.value

    if DEBUG:
      print(debug)




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

  context.set_safe_area(int((root_cell_resolution.columns - 32) / 2), int((root_cell_resolution.rows - 15) / 2))

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
