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

from ttconv.model import Document, Body, Div, CellResolutionType
from ttconv.scc.codes.attribute_codes import SccAttributeCode
from ttconv.scc.codes.control_codes import SccControlCode
from ttconv.scc.codes.mid_row_codes import SccMidRowCode
from ttconv.scc.codes.preambles_address_codes import SccPreambleAddressCode
from ttconv.scc.codes.special_characters import SccSpecialAndExtendedCharacter
from ttconv.scc.content import SccCaptionContent, SccCaptionLineBreak, SccCaptionText
from ttconv.scc.disassembly import get_color_disassembly, get_font_style_disassembly, get_text_decoration_disassembly
from ttconv.scc.paragraph import SccCaptionParagraph
from ttconv.scc.style import SccCaptionStyle
from ttconv.scc.time_codes import SccTimeCode, SMPTE_TIME_CODE_NDF_PATTERN, SMPTE_TIME_CODE_DF_PATTERN
from ttconv.style_properties import StyleProperties

LOGGER = logging.getLogger(__name__)

SCC_LINE_PATTERN = '((' + SMPTE_TIME_CODE_NDF_PATTERN + ')|(' + SMPTE_TIME_CODE_DF_PATTERN + '))\t.*'

PARITY_BIT_MASK = 0b01111111


class _SccContext:
  def __init__(self):
    self.div: Optional[Div] = None
    self.count: int = 0
    self.safe_area_x_offset: int = 0
    self.safe_area_y_offset: int = 0
    self.previous_code = 0
    self.current_caption: Optional[SccCaptionParagraph] = None
    self.previous_captions: List[SccCaptionParagraph] = []

  def set_safe_area(self, safe_area_x_offset: int, safe_area_y_offset: int):
    """Sets the safe area"""
    self.safe_area_x_offset = safe_area_x_offset
    self.safe_area_y_offset = safe_area_y_offset

  def set_current_to_previous(self):
    """Rotates current caption to previous caption"""
    if self.current_caption:
      self.previous_captions.append(self.current_caption)
      self.current_caption = None

  def init_current_caption(self, time_code: SccTimeCode):
    """Initializes the current caption with id and begin time"""
    if self.current_caption:
      self.count += 1
      self.current_caption.set_id("caption" + str(self.count))
      self.current_caption.set_begin(time_code)

  def push_previous_caption(self, time_code: SccTimeCode, index: int = 0):
    """Sets previous caption end time, pushes it into the data model and resets it"""
    if len(self.previous_captions) > 0:
      previous_caption = self.previous_captions.pop(index)
      previous_caption.set_end(time_code)
      self.div.push_child(previous_caption.to_paragraph(self.div.get_doc()))

  def process_preamble_address_code(self, pac: SccPreambleAddressCode, time_code: SccTimeCode):
    """Processes SCC Preamble Address Code it to the map to model"""
    if not self.current_caption:
      raise ValueError("No current SCC caption initialized")

    pac_row = pac.get_row()
    pac_indent = pac.get_indent()

    if self.current_caption.get_style() is SccCaptionStyle.PaintOn:
      if self.current_caption.get_current_text() and self.safe_area_y_offset + pac_row == self.current_caption.get_row_offset() + 1:
        # Creates a new Paragraph if the new caption is contiguous (Paint-On)
        self.set_current_to_previous()

        self.current_caption = SccCaptionParagraph(self.safe_area_x_offset, self.safe_area_y_offset, SccCaptionStyle.PaintOn)
        self.init_current_caption(time_code)

      elif len(self.previous_captions) > 0 and self.previous_captions[0].get_current_text() \
          and self.safe_area_y_offset + pac_row == self.previous_captions[0].get_row_offset():
        # Pushes and erases displayed row so that it can be replaced by current row (Paint-On)
        self.push_previous_caption(self.current_caption.get_begin())

    self.current_caption.new_caption_text()

    if self.current_caption.get_style() is SccCaptionStyle.RollUp:
      # Ignore PACs for rows 5-11, but get indent from PACs for rows 1-4 and 12-15. (Roll-Up)
      if pac_row in range(5, 12):
        self.current_caption.apply_current_text_offsets()
        return

      self.current_caption.set_column_offset(pac_indent)
    else:
      self.current_caption.set_row_offset(pac_row)
      self.current_caption.set_column_offset(pac_indent)

    self.current_caption.get_current_text().add_style_property(StyleProperties.Color, pac.get_color())
    self.current_caption.get_current_text().add_style_property(StyleProperties.FontStyle, pac.get_font_style())
    self.current_caption.get_current_text().add_style_property(StyleProperties.TextDecoration, pac.get_text_decoration())

    self.current_caption.apply_current_text_offsets()

  def process_mid_row_code(self, mid_row_code: SccMidRowCode):
    """Processes SCC Mid-Row Code to map it to the model"""
    if not self.current_caption:
      raise ValueError("No current SCC caption initialized")

    self.current_caption.new_caption_text()
    self.current_caption.apply_current_text_offsets()

    self.current_caption.get_current_text().add_style_property(StyleProperties.Color, mid_row_code.get_color())
    self.current_caption.get_current_text().add_style_property(StyleProperties.FontStyle, mid_row_code.get_font_style())
    self.current_caption.get_current_text().add_style_property(StyleProperties.TextDecoration, mid_row_code.get_text_decoration())

  def process_attribute_code(self, attribute_code: SccAttributeCode):
    """Processes SCC Attribute Code to map it to the model"""
    if not self.current_caption or not self.current_caption.get_current_text():
      raise ValueError("No current SCC caption nor content initialized")

    if attribute_code.is_background():
      self.current_caption.get_current_text().add_style_property(StyleProperties.BackgroundColor, attribute_code.get_color())
    else:
      self.current_caption.get_current_text().add_style_property(StyleProperties.Color, attribute_code.get_color())

    self.current_caption.get_current_text().add_style_property(StyleProperties.TextDecoration, attribute_code.get_text_decoration())

  def process_control_code(self, control_code: SccControlCode, time_code: SccTimeCode):
    """Processes SCC Control Code to map it to the model"""

    if control_code is SccControlCode.RCL:
      # Start a new Pop-On caption
      self.current_caption = SccCaptionParagraph(self.safe_area_x_offset, self.safe_area_y_offset, SccCaptionStyle.PopOn)

    elif control_code is SccControlCode.RDC:
      # Start a new Paint-On caption
      self.set_current_to_previous()

      self.current_caption = SccCaptionParagraph(self.safe_area_x_offset, self.safe_area_y_offset, SccCaptionStyle.PaintOn)
      self.init_current_caption(time_code)

    elif control_code in (SccControlCode.RU2, SccControlCode.RU3, SccControlCode.RU4):
      # Start a new Roll-Up caption
      self.set_current_to_previous()

      previous_last_lines: List[SccCaptionContent] = []
      if len(self.previous_captions) > 0:

        if control_code is SccControlCode.RU2:
          previous_last_lines = self.previous_captions[0].get_last_caption_lines(1)

        elif control_code is SccControlCode.RU3:
          previous_last_lines = self.previous_captions[0].get_last_caption_lines(2)

        elif control_code is SccControlCode.RU4:
          previous_last_lines = self.previous_captions[0].get_last_caption_lines(3)

        previous_last_lines.append(SccCaptionLineBreak())

      self.push_previous_caption(time_code)

      self.current_caption = SccCaptionParagraph(self.safe_area_x_offset, self.safe_area_y_offset, SccCaptionStyle.RollUp)
      self.current_caption.set_contents(previous_last_lines)
      self.init_current_caption(time_code)
      self.current_caption.apply_roll_up_row_offsets()

    elif control_code is SccControlCode.EOC:
      # Display caption (Pop-On)
      self.init_current_caption(time_code)
      self.set_current_to_previous()

    elif control_code is SccControlCode.EDM:
      # Erase displayed caption (Pop-On)
      if len(self.previous_captions) > 0:
        # Set line breaks depending on the position of the content
        last_text: Optional[SccCaptionText] = None
        for (index, content) in enumerate(self.previous_captions[0].get_contents()):
          if not isinstance(content, SccCaptionText):
            continue

          if last_text and self.previous_captions[0].get_current_text().is_contiguous(last_text):
            self.previous_captions[0].insert_content(index, SccCaptionLineBreak())

          last_text = content

      self.push_previous_caption(time_code)

    elif control_code is SccControlCode.TO1:
      self.current_caption.indent(1)

    elif control_code is SccControlCode.TO2:
      self.current_caption.indent(2)

    elif control_code is SccControlCode.TO3:
      self.current_caption.indent(3)

    elif control_code is SccControlCode.CR:
      # Roll the display up one row (Roll-Up)
      # Not used in this implementation since this SCC reader does not really map the roll-up effect,
      # but it erases the displayed paragraph and resets a new paragraph with the resulting rows.
      pass

    elif control_code is SccControlCode.DER:
      # Delete to End of Row (Paint-On)
      # The DER may be issued from any point on a row to delete all displayable characters, transparent
      # spaces, and mid-row codes from (and including) the current cell to the end of the row.
      # Not used in this implementation since this SCC reader does not map the text overlapping into
      # the model (i.e. a row is erased when a PAC is received, so before a new caption is written onto it).
      pass

  def process_text(self, word: str, time_code: SccTimeCode):
    """Processes SCC text words"""
    if self.current_caption.get_style() is SccCaptionStyle.PaintOn:
      if word.startswith(" "):
        self.current_caption.new_caption_text()
        self.current_caption.get_current_text().append(word)
        self.current_caption.apply_current_text_offsets()
        self.current_caption.get_current_text().set_begin(time_code)
        return

      if word.endswith(" "):
        self.current_caption.get_current_text().append(word)
        self.current_caption.new_caption_text()
        self.current_caption.apply_current_text_offsets()
        self.current_caption.get_current_text().set_begin(time_code)
        return

    self.current_caption.get_current_text().append(word)

  def flush(self, time_code: SccTimeCode):
    """Flushes the remaining current caption"""
    if self.current_caption:
      self.set_current_to_previous()
      while len(self.previous_captions) > 0:
        self.push_previous_caption(time_code)
      self.current_caption = None


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

  def to_model(self, context: _SccContext) -> SccTimeCode:
    """Converts the SCC line to the data model"""

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
        pac = SccPreambleAddressCode.find(scc_word.byte_1, scc_word.byte_2)
        spec_char = SccSpecialAndExtendedCharacter.find(scc_word.value)

        if pac:
          debug += "[PAC|" + str(pac.get_row()) + "|" + str(pac.get_indent())
          if pac.get_color():
            debug += "|" + str(pac.get_color())
          debug += "/" + hex(scc_word.value) + "]"
          context.process_preamble_address_code(pac, self.time_code)

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
          context.process_text(word, self.time_code)

        else:
          debug += "[??/" + hex(scc_word.value) + "]"
          LOGGER.warning("Unsupported SCC word: %s", hex(scc_word.value))

        context.previous_code = scc_word.value

      else:
        word = scc_word.to_text()
        debug += word
        context.process_text(word, self.time_code)
        context.previous_code = scc_word.value

    LOGGER.debug(debug)

    return self.time_code

  def to_disassembly(self) -> str:
    """Converts SCC line into the disassembly format"""
    disassembly_line = str(self.time_code) + "\t"

    for scc_word in self.scc_words:

      if scc_word.value == 0x0000:
        disassembly_line = "{}"

      if scc_word.byte_1 < 0x20:

        attribute_code = SccAttributeCode.find(scc_word.value)
        control_code = SccControlCode.find(scc_word.value)
        mid_row_code = SccMidRowCode.find(scc_word.value)
        pac = SccPreambleAddressCode.find(scc_word.byte_1, scc_word.byte_2)
        spec_char = SccSpecialAndExtendedCharacter.find(scc_word.value)

        if pac:
          disassembly_line += f"{{{pac.get_row():02}"
          color = pac.get_color()
          indent = pac.get_indent()
          if indent and indent > 0:
            disassembly_line += f"{indent :02}"
          elif color:
            disassembly_line += get_color_disassembly(color)
            disassembly_line += get_font_style_disassembly(pac.get_font_style())
            disassembly_line += get_text_decoration_disassembly(pac.get_text_decoration())
          else:
            disassembly_line += "00"
          disassembly_line += "}"

        elif attribute_code:
          disassembly_line += "{"
          disassembly_line += "B" if attribute_code.is_background() else ""
          disassembly_line += get_color_disassembly(attribute_code.get_color())
          disassembly_line += get_text_decoration_disassembly(attribute_code.get_text_decoration())
          disassembly_line += "}"

        elif mid_row_code:
          disassembly_line += "{"
          disassembly_line += get_color_disassembly(mid_row_code.get_color())
          disassembly_line += get_font_style_disassembly(mid_row_code.get_font_style())
          disassembly_line += get_text_decoration_disassembly(mid_row_code.get_text_decoration())
          disassembly_line += "}"

        elif control_code:
          disassembly_line += "{" + control_code.get_name() + "}"

        elif spec_char:
          disassembly_line += spec_char.get_unicode_value()

        else:
          disassembly_line += "{??}"
          LOGGER.warning("Unsupported SCC word: %s", hex(scc_word.value))

      else:
        disassembly_line += scc_word.to_text()

    return disassembly_line


#
# SCC reader
#

def to_model(scc_content: str):
  """Converts a SCC document to the data model"""

  context = _SccContext()
  document = Document()

  # Safe area must be a 32x15 grid, that represents 80% of the root area
  root_cell_resolution = CellResolutionType(rows=19, columns=40)
  document.set_cell_resolution(root_cell_resolution)

  context.set_safe_area(int((root_cell_resolution.columns - 32) / 2), int((root_cell_resolution.rows - 15) / 2))

  body = Body()
  body.set_doc(document)
  document.set_body(body)

  context.div = Div()
  context.div.set_doc(document)
  body.push_child(context.div)

  time_code = None
  for line in scc_content.splitlines():
    LOGGER.debug(line)
    scc_line = SccLine.from_str(line)

    if not scc_line:
      continue

    time_code = scc_line.to_model(context)

  context.flush(time_code)

  return document


def to_disassembly(scc_content: str) -> str:
  """Dumps a SCC document into the disassembly format"""
  disassembly = ""
  for line in scc_content.splitlines():
    LOGGER.debug(line)
    scc_line = SccLine.from_str(line)

    if not scc_line:
      continue

    line_to_disassembly = scc_line.to_disassembly()
    LOGGER.debug(line_to_disassembly)

    disassembly += line_to_disassembly + "\n"

  return disassembly
