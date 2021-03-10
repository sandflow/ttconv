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
from typing import Optional, List

from ttconv.model import ContentDocument, Body, Div, CellResolutionType
from ttconv.scc.codes.attribute_codes import SccAttributeCode
from ttconv.scc.codes.control_codes import SccControlCode
from ttconv.scc.codes.mid_row_codes import SccMidRowCode
from ttconv.scc.codes.preambles_address_codes import SccPreambleAddressCode
from ttconv.scc.codes.special_characters import SccSpecialCharacter, SccExtendedCharacter
from ttconv.scc.config import SccReaderConfiguration, TextAlignment
from ttconv.scc.content import SccCaptionContent, SccCaptionLineBreak, SccCaptionText
from ttconv.scc.line import SccLine
from ttconv.scc.paragraph import SccCaptionParagraph, SCC_SAFE_AREA_CELL_RESOLUTION_ROWS, SCC_SAFE_AREA_CELL_RESOLUTION_COLUMNS, \
  SCC_ROOT_CELL_RESOLUTION_ROWS, SCC_ROOT_CELL_RESOLUTION_COLUMNS
from ttconv.scc.style import SccCaptionStyle
from ttconv.style_properties import StyleProperties, NamedColors, LengthType
from ttconv.time_code import SmpteTimeCode

LOGGER = logging.getLogger(__name__)


class _SccContext:
  def __init__(self, config: Optional[SccReaderConfiguration] = None):
    # Caption paragraphs container
    self.div: Optional[Div] = None

    # Caption paragraphs counter
    self.count: int = 0

    # Screen safe area offsets
    self.safe_area_x_offset: int = 0
    self.safe_area_y_offset: int = 0

    # Previously read SCC word value
    self.previous_code = 0

    # Buffered caption being built
    self.buffered_caption: Optional[SccCaptionParagraph] = None
    # Captions being displayed
    self.active_captions: List[SccCaptionParagraph] = []

    # Text alignment
    self.text_alignment = TextAlignment.AUTO if config is None else config.text_align

  def set_safe_area(self, safe_area_x_offset: int, safe_area_y_offset: int):
    """Sets the safe area"""
    self.safe_area_x_offset = safe_area_x_offset
    self.safe_area_y_offset = safe_area_y_offset

  def has_active_captions(self):
    """Returns whether captions are being displayed or not"""
    return len(self.active_captions) > 0

  def set_buffered_caption_begin_time(self, time_code: SmpteTimeCode):
    """Initializes the current buffered caption with begin time"""
    if self.buffered_caption is not None:
      self.buffered_caption.set_begin(time_code)

  def push_buffered_to_active_captions(self):
    """Send the current buffered caption to the active captions list"""
    if self.buffered_caption is not None and self.buffered_caption.get_current_text():
      if not self.buffered_caption.get_id():
        self.count += 1
        self.buffered_caption.set_id("caption" + str(self.count))

      self.active_captions.append(self.buffered_caption)
      self.buffered_caption = None

  def flip_buffered_to_active_captions(self, time_code: Optional[SmpteTimeCode] = None):
    """
    Flip the current buffered caption with the last active captions list,
    and push to model if an end time code is specified.
    """
    temporary_caption = None

    if self.has_active_captions():
      # FIXME should be every active captions
      temporary_caption = self.active_captions[-1]

      if time_code is not None:
        # End of display of active captions
        while self.has_active_captions():
          self.push_active_caption_to_model(time_code)

    self.push_buffered_to_active_captions()

    if temporary_caption is not None:
      self.buffered_caption = temporary_caption

  def push_active_caption_to_model(self, time_code: Optional[SmpteTimeCode], index: int = 0):
    """Sets end time to the last active caption, and pushes it into the data model"""
    if self.has_active_captions():
      previous_caption = self.active_captions.pop(index)
      previous_caption.set_end(time_code)

      if previous_caption.get_style_property(StyleProperties.BackgroundColor) is None:
        previous_caption.add_style_property(StyleProperties.BackgroundColor, NamedColors.black.value)

      self.div.push_child(previous_caption.to_paragraph(self.div.get_doc()))

  def process_preamble_address_code(self, pac: SccPreambleAddressCode, time_code: SmpteTimeCode):
    """Processes SCC Preamble Address Code it to the map to model"""
    if self.buffered_caption is None:
      raise ValueError("No current SCC caption initialized")

    pac_row = pac.get_row()
    pac_indent = pac.get_indent()

    if self.buffered_caption.get_caption_style() is SccCaptionStyle.PaintOn:
      if self.buffered_caption.get_current_text() is not None \
          and self.safe_area_y_offset + pac_row == self.buffered_caption.get_row_offset() + 1:
        # Creates a new Paragraph if the new caption is contiguous (Paint-On)
        self.push_buffered_to_active_captions()

        self.buffered_caption = SccCaptionParagraph(self.safe_area_x_offset, self.safe_area_y_offset, SccCaptionStyle.PaintOn)
        self.set_buffered_caption_begin_time(time_code)

      elif self.has_active_captions() and self.active_captions[0].get_current_text() is not None \
          and self.safe_area_y_offset + pac_row == self.active_captions[0].get_row_offset() \
          and self.active_captions[0].get_caption_style() is SccCaptionStyle.PaintOn:
        # Pushes and erases displayed row so that it can be replaced by current row (Paint-On)
        self.push_active_caption_to_model(self.buffered_caption.get_begin())

    self.buffered_caption.new_caption_text()

    if self.buffered_caption.get_caption_style() is SccCaptionStyle.RollUp:
      # Ignore PACs for rows 5-11, but get indent from PACs for rows 1-4 and 12-15. (Roll-Up)
      if pac_row in range(5, 12):
        self.buffered_caption.apply_current_text_offsets()
        return

      # Force roll-up paragraph to belong to the same region
      # self.buffered_caption.set_column_offset(pac_indent)
    else:
      self.buffered_caption.set_row_offset(pac_row)
      self.buffered_caption.set_column_offset(pac_indent)

    self.buffered_caption.get_current_text().add_style_property(StyleProperties.Color, pac.get_color())
    self.buffered_caption.get_current_text().add_style_property(StyleProperties.FontStyle, pac.get_font_style())
    self.buffered_caption.get_current_text().add_style_property(StyleProperties.TextDecoration, pac.get_text_decoration())

    self.buffered_caption.apply_current_text_offsets()

  def process_mid_row_code(self, mid_row_code: SccMidRowCode, time_code: SmpteTimeCode):
    """Processes SCC Mid-Row Code to map it to the model"""
    if self.buffered_caption is None:
      raise ValueError("No current SCC caption initialized")

    if self.buffered_caption.get_current_text() is not None and self.buffered_caption.get_current_text().get_text():
      self.buffered_caption.new_caption_text()
      self.buffered_caption.apply_current_text_offsets()

    self.buffered_caption.get_current_text().add_style_property(StyleProperties.Color, mid_row_code.get_color())
    self.buffered_caption.get_current_text().add_style_property(StyleProperties.FontStyle, mid_row_code.get_font_style())
    self.buffered_caption.get_current_text().add_style_property(StyleProperties.TextDecoration, mid_row_code.get_text_decoration())

    # The cursor moves one column to the right after each Mid-Row Code
    self.buffered_caption.get_current_text().append(" ")

    if self.buffered_caption.get_caption_style() is SccCaptionStyle.PaintOn:
      self.buffered_caption.get_current_text().set_begin(time_code)

  def process_attribute_code(self, attribute_code: SccAttributeCode):
    """Processes SCC Attribute Code to map it to the model"""
    if self.buffered_caption is None or self.buffered_caption.get_current_text() is None:
      raise ValueError("No current SCC caption nor content initialized")

    if self.buffered_caption.get_current_text() is not None and self.buffered_caption.get_current_text().get_text():
      self.buffered_caption.new_caption_text()
      self.buffered_caption.apply_current_text_offsets()

    if attribute_code.is_background():
      self.buffered_caption.get_current_text().add_style_property(StyleProperties.BackgroundColor, attribute_code.get_color())
    else:
      self.buffered_caption.get_current_text().add_style_property(StyleProperties.Color, attribute_code.get_color())

    self.buffered_caption.get_current_text().add_style_property(StyleProperties.TextDecoration,
                                                                attribute_code.get_text_decoration())

  def process_control_code(self, control_code: SccControlCode, time_code: SmpteTimeCode):
    """Processes SCC Control Code to map it to the model"""

    if control_code is SccControlCode.RCL:
      # Start a new Pop-On caption
      self.buffered_caption = SccCaptionParagraph(self.safe_area_x_offset, self.safe_area_y_offset, SccCaptionStyle.PopOn)

    elif control_code is SccControlCode.RDC:
      # Start a new Paint-On caption
      self.push_buffered_to_active_captions()

      self.buffered_caption = SccCaptionParagraph(self.safe_area_x_offset, self.safe_area_y_offset, SccCaptionStyle.PaintOn)
      self.set_buffered_caption_begin_time(time_code)

    elif control_code in (SccControlCode.RU2, SccControlCode.RU3, SccControlCode.RU4):
      # Start a new Roll-Up caption
      self.push_buffered_to_active_captions()

      previous_last_lines: List[SccCaptionContent] = []
      if self.has_active_captions():

        if control_code is SccControlCode.RU2:
          previous_last_lines = self.active_captions[-1].get_last_caption_lines(1)

        elif control_code is SccControlCode.RU3:
          previous_last_lines = self.active_captions[-1].get_last_caption_lines(2)

        elif control_code is SccControlCode.RU4:
          previous_last_lines = self.active_captions[-1].get_last_caption_lines(3)

        previous_last_lines.append(SccCaptionLineBreak())

      self.push_active_caption_to_model(time_code)

      self.buffered_caption = SccCaptionParagraph(self.safe_area_x_offset, self.safe_area_y_offset, SccCaptionStyle.RollUp)
      self.buffered_caption.set_contents(previous_last_lines)
      self.set_buffered_caption_begin_time(time_code)
      self.buffered_caption.apply_roll_up_row_offsets()

    elif control_code is SccControlCode.EOC:
      # Display caption (Pop-On)
      self.set_buffered_caption_begin_time(time_code)
      self.flip_buffered_to_active_captions(time_code)

      if self.has_active_captions():
        # Set line breaks depending on the position of the content

        contents = []
        last_active_caption = self.active_captions[-1]
        initial_length = len(last_active_caption.get_contents())

        for index in range(0, initial_length):
          content = last_active_caption.get_contents()[index - 1]
          if not isinstance(content, SccCaptionText):
            continue

          next_content = last_active_caption.get_contents()[index]
          if not isinstance(next_content, SccCaptionText):
            continue

          if next_content.is_contiguous(content):
            contents.append(SccCaptionLineBreak())

          contents.append(next_content)

        last_active_caption.set_contents(contents)

        if self.text_alignment == TextAlignment.AUTO:
          text_alignment = last_active_caption.guess_text_alignment()
        else:
          text_alignment = self.text_alignment.text_align

        # Apply text alignment
        last_active_caption.add_style_property(StyleProperties.TextAlign, text_alignment)

    elif control_code is SccControlCode.EDM:
      # Erase displayed captions
      while self.has_active_captions():
        self.push_active_caption_to_model(time_code)

    elif control_code is SccControlCode.ENM:
      # Erase buffered caption
      self.buffered_caption = None

    elif control_code is SccControlCode.TO1:
      self.buffered_caption.indent(1)

    elif control_code is SccControlCode.TO2:
      self.buffered_caption.indent(2)

    elif control_code is SccControlCode.TO3:
      self.buffered_caption.indent(3)

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

    elif control_code is SccControlCode.BS:
      # Backspace
      # When a Backspace is received, the cursor moves to the left one column position erasing
      # the character or Mid-Row Code occupying that location, unless the cursor is in Column 1
      self.buffered_caption.get_current_text().backspace()

  def process_text(self, word: str, time_code: SmpteTimeCode):
    """Processes SCC text words"""
    if self.buffered_caption.get_caption_style() is SccCaptionStyle.PaintOn:
      if word.startswith(" "):
        self.buffered_caption.new_caption_text()
        self.buffered_caption.get_current_text().append(word)
        self.buffered_caption.apply_current_text_offsets()
        self.buffered_caption.get_current_text().set_begin(time_code)
        return

      if word.endswith(" "):
        self.buffered_caption.get_current_text().append(word)
        self.buffered_caption.new_caption_text()
        self.buffered_caption.apply_current_text_offsets()
        self.buffered_caption.get_current_text().set_begin(time_code)
        return

    self.buffered_caption.get_current_text().append(word)

  def flush(self, time_code: Optional[SmpteTimeCode] = None):
    """Flushes the remaining current caption"""
    if self.buffered_caption is not None:
      self.push_buffered_to_active_captions()
      self.buffered_caption = None

    while self.has_active_captions():
      self.push_active_caption_to_model(time_code)

  def process_line(self, line: SccLine) -> SmpteTimeCode:
    """Converts the SCC line to the data model"""

    debug = str(line.time_code) + "\t"

    for scc_word in line.scc_words:

      if self.previous_code == scc_word.value:
        continue

      line.time_code.add_frames()

      if scc_word.value == 0x0000:
        continue

      if scc_word.byte_1 < 0x20:

        control_code = SccControlCode.find(scc_word.value)
        if control_code is not None \
            and control_code is SccControlCode.find(self.previous_code):
          # Skip duplicated control code from 'Field 2'
          line.time_code.add_frames(-1)
          continue

        attribute_code = SccAttributeCode.find(scc_word.value)
        mid_row_code = SccMidRowCode.find(scc_word.value)
        pac = SccPreambleAddressCode.find(scc_word.byte_1, scc_word.byte_2)
        spec_char = SccSpecialCharacter.find(scc_word.value)
        extended_char = SccExtendedCharacter.find(scc_word.value)

        if pac is not None:
          debug += "[PAC|" + str(pac.get_row()) + "|" + str(pac.get_indent())
          if pac.get_color() is not None:
            debug += "|" + str(pac.get_color())
          if pac.get_font_style() is not None:
            debug += "|I"
          if pac.get_text_decoration() is not None:
            debug += "|U"
          debug += "/" + hex(scc_word.value) + "]"
          self.process_preamble_address_code(pac, line.time_code)

        elif attribute_code is not None:
          debug += "[ATC/" + hex(scc_word.value) + "]"
          self.process_attribute_code(attribute_code)

        elif mid_row_code is not None:
          debug += "[MRC|" + mid_row_code.get_name() + "/" + hex(scc_word.value) + "]"
          self.process_mid_row_code(mid_row_code, line.time_code)

        elif control_code is not None:
          debug += "[CC|" + control_code.get_name() + "/" + hex(scc_word.value) + "]"
          self.process_control_code(control_code, line.time_code)

        elif spec_char is not None:
          word = spec_char.get_unicode_value()
          debug += word
          self.process_text(word, line.time_code)

        elif extended_char is not None:
          self.buffered_caption.get_current_text().backspace()
          word = extended_char.get_unicode_value()
          debug += word
          self.process_text(word, line.time_code)

        else:
          debug += "[??/" + hex(scc_word.value) + "]"
          LOGGER.warning("Unsupported SCC word: %s", hex(scc_word.value))

        self.previous_code = scc_word.value

      else:
        word = scc_word.to_text()
        debug += word
        self.process_text(word, line.time_code)
        self.previous_code = scc_word.value

    LOGGER.debug(debug)

    return line.time_code


#
# SCC reader
#

def to_model(scc_content: str, config: Optional[SccReaderConfiguration] = None, progress_callback=lambda _: None):
  """Converts a SCC document to the data model"""

  context = _SccContext(config)
  document = ContentDocument()

  # Safe area must be a 32x15 grid, that represents 80% of the root area
  root_cell_resolution = CellResolutionType(rows=SCC_ROOT_CELL_RESOLUTION_ROWS, columns=SCC_ROOT_CELL_RESOLUTION_COLUMNS)
  document.set_cell_resolution(root_cell_resolution)

  context.set_safe_area(int((root_cell_resolution.columns - SCC_SAFE_AREA_CELL_RESOLUTION_COLUMNS) / 2),
                        int((root_cell_resolution.rows - SCC_SAFE_AREA_CELL_RESOLUTION_ROWS) / 2))

  body = Body()
  body.set_doc(document)
  document.set_body(body)

  # the default value of LineHeight ("normal") typically translates to 125% of the font size, which causes regions to overflow.
  body.set_style(StyleProperties.LineHeight, LengthType(value=100, units=LengthType.Units.pct))

  context.div = Div()
  context.div.set_doc(document)
  body.push_child(context.div)

  lines = scc_content.splitlines()
  nb_lines = len(lines)

  for (index, line) in enumerate(lines):
    LOGGER.debug(line)
    scc_line = SccLine.from_str(line)

    progress_callback((index + 1) / nb_lines)

    if scc_line is None:
      continue

    context.process_line(scc_line)

  context.flush()

  return document


def to_disassembly(scc_content: str) -> str:
  """Dumps a SCC document into the disassembly format"""
  disassembly = ""
  for line in scc_content.splitlines():
    LOGGER.debug(line)
    scc_line = SccLine.from_str(line)

    if scc_line is None:
      continue

    line_to_disassembly = scc_line.to_disassembly()
    LOGGER.debug(line_to_disassembly)

    disassembly += line_to_disassembly + "\n"

  return disassembly
