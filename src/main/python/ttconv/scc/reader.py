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
from typing import Optional

from ttconv.model import ContentDocument, Body, Div, CellResolutionType, ActiveAreaType
from ttconv.scc.codes.attribute_codes import SccAttributeCode
from ttconv.scc.codes.control_codes import SccControlCode
from ttconv.scc.codes.mid_row_codes import SccMidRowCode
from ttconv.scc.codes.preambles_address_codes import SccPreambleAddressCode
from ttconv.scc.codes.special_characters import SccSpecialCharacter, SccExtendedCharacter
from ttconv.scc.config import SccReaderConfiguration, TextAlignment
from ttconv.scc.content import ROLL_UP_BASE_ROW
from ttconv.scc.line import SccLine
from ttconv.scc.paragraph import SccCaptionParagraph, SCC_SAFE_AREA_CELL_RESOLUTION_ROWS, SCC_SAFE_AREA_CELL_RESOLUTION_COLUMNS, \
  SCC_ROOT_CELL_RESOLUTION_ROWS, SCC_ROOT_CELL_RESOLUTION_COLUMNS
from ttconv.scc.style import SccCaptionStyle
from ttconv.style_properties import StyleProperties, LengthType, GenericFontFamilyType
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
    self.previous_code_type = None

    # Buffered caption being built
    self.buffered_caption: Optional[SccCaptionParagraph] = None
    # Captions being displayed
    self.active_caption: Optional[SccCaptionParagraph] = None
    # Caption style (Pop-on, Roll-up, Paint-on) currently processed
    self.current_style: Optional[SccCaptionStyle] = None

    # Roll-up caption number of lines
    self.roll_up_depth: int = 0

    # Cursor position in the active area
    self.active_cursor: (int, int) = (0, 0)

    self.current_text_decoration = None
    self.current_color = None
    self.current_font_style = None

    # Text alignment
    self.text_alignment = TextAlignment.AUTO if config is None else config.text_align

  def set_safe_area(self, safe_area_x_offset: int, safe_area_y_offset: int):
    """Sets the safe area"""
    self.safe_area_x_offset = safe_area_x_offset
    self.safe_area_y_offset = safe_area_y_offset

  def has_active_caption(self) -> bool:
    """Returns whether captions are being displayed or not"""
    return self.active_caption is not None

  def set_buffered_caption_begin_time(self, time_code: SmpteTimeCode):
    """Initializes the current buffered caption with begin time"""
    if self.buffered_caption is not None:
      self.buffered_caption.set_begin(time_code)

  def initialize_active_caption(self, begin_time_code: SmpteTimeCode):
    """Initializes the current active caption with id and begin time"""
    if self.active_caption is not None:
      if not self.active_caption.get_id():
        self.count += 1
        self.active_caption.set_id("caption" + str(self.count))

      self.active_caption.set_begin(begin_time_code)

  def push_buffered_to_active_captions(self):
    """Send the current buffered caption to the active captions list"""
    if self.buffered_caption is not None and self.buffered_caption.get_current_text():
      if not self.buffered_caption.get_id():
        self.count += 1
        self.buffered_caption.set_id("caption" + str(self.count))

      self.active_caption = self.buffered_caption
      self.buffered_caption = None

  def flip_buffered_to_active_captions(self, time_code: Optional[SmpteTimeCode] = None):
    """
    Flip the current buffered caption with the last active captions list,
    and push to model if an end time code is specified.
    """
    temporary_caption = None

    if self.has_active_caption():
      temporary_caption = self.active_caption

      if time_code is not None:
        # End of display of active captions
        if self.has_active_caption():
          self.push_active_caption_to_model(time_code)

    self.push_buffered_to_active_captions()

    if temporary_caption is not None:
      self.buffered_caption = temporary_caption

  def push_active_caption_to_model(self, time_code: SmpteTimeCode, clear_active_caption: bool = True):
    """Sets end time to the last active caption, and pushes it into the data model"""
    if self.has_active_caption():
      self.active_cursor = self.active_caption.get_cursor()

      previous_caption = self.active_caption
      previous_caption.set_end(time_code)

      if clear_active_caption:
        self.active_caption = None

      self.div.push_child(previous_caption.to_paragraph(self.div.get_doc()))

  def paint_on_active_caption(self, time_code: SmpteTimeCode):
    """Initialize active caption for paint-on style"""
    active_style = SccCaptionStyle.PaintOn
    copied_lines = []
    cursor = self.active_cursor

    if self.has_active_caption():
      active_style = self.active_caption.get_caption_style()
      cursor = self.active_caption.get_cursor()

      # Copy buffered lines
      copied_lines = self.active_caption.copy_lines()

      # Push active to model if there is one
      self.push_active_caption_to_model(time_code)

    # Initialize new buffered caption
    self.active_caption = SccCaptionParagraph(self.safe_area_x_offset, self.safe_area_y_offset, active_style)
    self.initialize_active_caption(time_code)

    if len(copied_lines) > 0:
      # Set remaining lines to the new buffered caption
      self.active_caption.set_lines(copied_lines)

    self.active_caption.set_cursor_at(cursor[0], cursor[1])

  def process_preamble_address_code(self, pac: SccPreambleAddressCode, time_code: SmpteTimeCode):
    """Processes SCC Preamble Address Code it to the map to model"""

    pac_row = pac.get_row()
    pac_indent = pac.get_indent()

    if self.current_style is SccCaptionStyle.PaintOn:

      self.paint_on_active_caption(time_code)

      if self.active_caption.get_caption_style() is SccCaptionStyle.PaintOn:
        # Clear target row on Paint-On style
        target_row = self.active_caption.get_lines().get(pac_row)
        if target_row is not None:
          target_row.clear()

      self.active_caption.set_cursor_at(pac_row, pac_indent)

      if self.active_caption.get_current_text() is None:
        self.active_caption.new_caption_text()

    elif self.current_style is SccCaptionStyle.RollUp:

      if not self.has_active_caption():
        # If there is no current active caption, initialize an empty new paragraph
        self.active_caption = SccCaptionParagraph(self.safe_area_x_offset, self.safe_area_y_offset, SccCaptionStyle.RollUp)
        self.initialize_active_caption(time_code)

      # Ignore PACs for rows 5-11, but get indent from PACs for rows 1-4 and 12-15. (Roll-Up)
      if pac_row in range(5, 12):
        self.active_caption.set_cursor_at(ROLL_UP_BASE_ROW)
        self.active_caption.new_caption_text()
        return

      # Force roll-up paragraph to belong to the same region
      self.active_caption.set_cursor_at(ROLL_UP_BASE_ROW, pac_indent)

      self.active_caption.new_caption_text()

    else:  # Pop-On Style

      if self.buffered_caption is None:
        self.buffered_caption = SccCaptionParagraph(self.safe_area_x_offset, self.safe_area_y_offset, SccCaptionStyle.PopOn)

      # set cursor in paragraph and create line or text if necessary
      self.buffered_caption.set_cursor_at(pac_row, pac_indent)

      self.buffered_caption.new_caption_text()

    self.current_color = pac.get_color()
    self.current_font_style = pac.get_font_style()
    self.current_text_decoration = pac.get_text_decoration()

    if self.has_active_caption():
      self.active_cursor = self.active_caption.get_cursor()

  def process_mid_row_code(self, mid_row_code: SccMidRowCode, time_code: SmpteTimeCode):
    """Processes SCC Mid-Row Code to map it to the model"""

    # If the Paint-On or Roll-Up style is activated, write directly on active caption
    processed_caption = self.buffered_caption
    if self.current_style in (SccCaptionStyle.PaintOn, SccCaptionStyle.RollUp):
      processed_caption = self.active_caption

    if processed_caption is None:
      raise ValueError("No current SCC caption initialized")

    color = mid_row_code.get_color()
    font_style = mid_row_code.get_font_style()
    text_decoration = mid_row_code.get_text_decoration()

    if self.previous_code_type is not SccMidRowCode:
      # In case of multiple mid-row codes, move right only after the first code

      # If there is already text on the current line
      if processed_caption.get_current_text() is not None \
          and processed_caption.get_current_text().get_text() != "":

        # In case of paint-on replacing text
        if self.current_style is SccCaptionStyle.PaintOn \
            and processed_caption.get_current_line().get_cursor() < processed_caption.get_current_line().get_length():
          processed_caption.append_text(" ")

        else:
          if text_decoration is None:
            processed_caption.new_caption_text()
            processed_caption.append_text(" ")
          else:
            processed_caption.append_text(" ")
            processed_caption.new_caption_text()

      else:
        processed_caption.append_text(" ")

      self.current_color = color
      self.current_font_style = font_style
      self.current_text_decoration = text_decoration

    else:
      if color is not None:
        self.current_color = color
      if font_style is not None:
        self.current_font_style = font_style
      if text_decoration is not None:
        self.current_text_decoration = text_decoration

      processed_caption.append_text(" ")
      processed_caption.new_caption_text()

    if processed_caption.get_caption_style() is SccCaptionStyle.PaintOn:
      processed_caption.get_current_text().set_begin(time_code)

  def process_attribute_code(self, attribute_code: SccAttributeCode):
    """Processes SCC Attribute Code to map it to the model"""

    # If the Paint-On or Roll-Up style is activated, write directly on active caption
    processed_caption = self.buffered_caption
    if self.current_style in (SccCaptionStyle.PaintOn, SccCaptionStyle.RollUp):
      processed_caption = self.active_caption

    if processed_caption is None or processed_caption.get_current_text() is None:
      raise ValueError("No current SCC caption nor content initialized")

    if processed_caption.get_current_text() is not None and processed_caption.get_current_text().get_text():
      processed_caption.new_caption_text()

    if attribute_code.is_background():
      processed_caption.get_current_text().add_style_property(StyleProperties.BackgroundColor, attribute_code.get_color())
    else:
      processed_caption.get_current_text().add_style_property(StyleProperties.Color, attribute_code.get_color())

    processed_caption.get_current_text().add_style_property(StyleProperties.TextDecoration,
                                                            attribute_code.get_text_decoration())

  def process_control_code(self, control_code: SccControlCode, time_code: SmpteTimeCode):
    """Processes SCC Control Code to map it to the model"""

    processed_caption = self.buffered_caption

    if control_code is SccControlCode.RCL:
      # Start a new Pop-On caption
      self.current_style = SccCaptionStyle.PopOn

    elif control_code is SccControlCode.RDC:
      # Start a new Paint-On caption
      self.current_style = SccCaptionStyle.PaintOn

    elif control_code in (SccControlCode.RU2, SccControlCode.RU3, SccControlCode.RU4):
      # Start a new Roll-Up caption
      self.current_style = SccCaptionStyle.RollUp

      if control_code is SccControlCode.RU2:
        self.roll_up_depth = 2

      elif control_code is SccControlCode.RU3:
        self.roll_up_depth = 3

      elif control_code is SccControlCode.RU4:
        self.roll_up_depth = 4

    else:
      # If the Paint-On or Roll-Up style is activated, write directly on active caption
      if self.current_style in (SccCaptionStyle.PaintOn, SccCaptionStyle.RollUp):
        processed_caption = self.active_caption

    if control_code is SccControlCode.EOC:
      # Display caption (Pop-On)
      self.set_buffered_caption_begin_time(time_code)
      self.flip_buffered_to_active_captions(time_code)

      if self.has_active_caption():
        # Set text alignment
        if self.text_alignment == TextAlignment.AUTO:
          text_alignment = self.active_caption.guess_text_alignment()
        else:
          text_alignment = self.text_alignment.text_align

        # Apply text alignment
        self.active_caption.add_style_property(StyleProperties.TextAlign, text_alignment)

    elif control_code is SccControlCode.EDM:
      # Erase displayed captions
      if self.has_active_caption():
        if time_code is not None:
          # End time is exclusive in the model, set it to the next frame
          end_time_code = copy.copy(time_code)
          end_time_code.add_frames()
        else:
          end_time_code = time_code

        self.push_active_caption_to_model(end_time_code)

    elif control_code is SccControlCode.ENM:
      # Erase buffered caption
      self.buffered_caption = None

    elif control_code is SccControlCode.TO1:
      processed_caption.indent_cursor(1)

    elif control_code is SccControlCode.TO2:
      processed_caption.indent_cursor(2)

    elif control_code is SccControlCode.TO3:
      processed_caption.indent_cursor(3)

    elif control_code is SccControlCode.CR:
      # Roll the displayed caption up one row (Roll-Up)

      if self.has_active_caption():
        # Push active caption to model (but don't erase it)
        self.push_active_caption_to_model(time_code, False)
        # Roll the active caption up
        self.active_caption.roll_up()
        # Get the remaining lines to initialize the following caption with the expected depth
        previous_lines = self.active_caption.get_last_caption_lines(self.roll_up_depth - 1)

        # Initialize the new caption with the previous lines
        self.active_caption = SccCaptionParagraph(self.safe_area_x_offset, self.safe_area_y_offset, SccCaptionStyle.RollUp)
        self.initialize_active_caption(time_code)
        self.active_caption.set_lines(previous_lines)

        self.active_caption.set_cursor_at(self.active_cursor[0], self.active_cursor[1])

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
      processed_caption.get_current_text().backspace()

  def process_text(self, word: str, time_code: SmpteTimeCode):
    """Processes SCC text words"""
    if self.current_style is SccCaptionStyle.PaintOn:
      if word.startswith(" "):

        if self.active_caption.get_caption_style() is not SccCaptionStyle.PaintOn:
          self.paint_on_active_caption(time_code)
          self.active_caption.append_text(word)

        else:
          self.active_caption.new_caption_text()
          self.active_caption.append_text(word)
          self.active_caption.get_current_text().set_begin(time_code)


      elif word.endswith(" "):
        self.active_caption.append_text(word)

        if self.active_caption.get_caption_style() is not SccCaptionStyle.PaintOn:
          self.paint_on_active_caption(time_code)
        else:
          self.active_caption.new_caption_text()
          self.active_caption.get_current_text().set_begin(time_code)

      else:
        if not self.has_active_caption():
          self.paint_on_active_caption(time_code)

        self.active_caption.append_text(word)

      self.active_caption.get_current_text().add_style_property(StyleProperties.Color, self.current_color)
      self.active_caption.get_current_text().add_style_property(StyleProperties.FontStyle, self.current_font_style)
      self.active_caption.get_current_text().add_style_property(StyleProperties.TextDecoration, self.current_text_decoration)

    elif self.current_style is SccCaptionStyle.RollUp:
      self.active_caption.append_text(word)

      self.active_caption.get_current_text().add_style_property(StyleProperties.Color, self.current_color)
      self.active_caption.get_current_text().add_style_property(StyleProperties.FontStyle, self.current_font_style)
      self.active_caption.get_current_text().add_style_property(StyleProperties.TextDecoration, self.current_text_decoration)

    else:
      self.buffered_caption.append_text(word)

      self.buffered_caption.get_current_text().add_style_property(StyleProperties.Color, self.current_color)
      self.buffered_caption.get_current_text().add_style_property(StyleProperties.FontStyle, self.current_font_style)
      self.buffered_caption.get_current_text().add_style_property(StyleProperties.TextDecoration, self.current_text_decoration)

    if self.has_active_caption():
      self.active_cursor = self.active_caption.get_cursor()

  def flush(self, time_code: Optional[SmpteTimeCode] = None):
    """Flushes the remaining current caption"""
    if self.has_active_caption():
      self.push_active_caption_to_model(time_code)

    if self.buffered_caption is not None:
      # Remove the buffered caption
      self.buffered_caption = None

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
          self.previous_code_type = type(pac)

        elif attribute_code is not None:
          debug += "[ATC/" + hex(scc_word.value) + "]"
          self.process_attribute_code(attribute_code)
          self.previous_code_type = type(attribute_code)

        elif mid_row_code is not None:
          debug += "[MRC|" + mid_row_code.get_name() + "/" + hex(scc_word.value) + "]"
          self.process_mid_row_code(mid_row_code, line.time_code)
          self.previous_code_type = type(mid_row_code)

        elif control_code is not None:
          debug += "[CC|" + control_code.get_name() + "/" + hex(scc_word.value) + "]"
          self.process_control_code(control_code, line.time_code)
          self.previous_code_type = type(control_code)


        elif spec_char is not None:
          word = spec_char.get_unicode_value()
          debug += word
          self.process_text(word, line.time_code)
          self.previous_code_type = type(spec_char)

        elif extended_char is not None:
          if self.current_style in (SccCaptionStyle.PaintOn, SccCaptionStyle.RollUp):
            self.active_caption.get_current_text().backspace()
          else:
            self.buffered_caption.get_current_text().backspace()

          word = extended_char.get_unicode_value()
          debug += word
          self.process_text(word, line.time_code)
          self.previous_code_type = type(extended_char)

        else:
          debug += "[??/" + hex(scc_word.value) + "]"
          LOGGER.warning("Unsupported SCC word: %s", hex(scc_word.value))
          self.previous_code_type = None

      else:
        word = scc_word.to_text()
        debug += word
        self.process_text(word, line.time_code)
        self.previous_code_type = str

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

  # The active area is equivalent to the safe area
  active_area = ActiveAreaType(
    left_offset=context.safe_area_x_offset / root_cell_resolution.columns,
    top_offset=context.safe_area_y_offset / root_cell_resolution.rows,
    width=(root_cell_resolution.columns - (context.safe_area_x_offset * 2)) / root_cell_resolution.columns,
    height=(root_cell_resolution.rows - (context.safe_area_y_offset * 2)) / root_cell_resolution.rows,
  )
  document.set_active_area(active_area)

  body = Body()
  body.set_doc(document)
  document.set_body(body)

  # the default value of LineHeight ("normal") typically translates to 125% of the font size, which causes regions to overflow.
  body.set_style(StyleProperties.LineHeight, LengthType(value=100, units=LengthType.Units.pct))

  # use a more readable font than the default Courier
  body.set_style(StyleProperties.FontFamily, ("Consolas", "Monaco", GenericFontFamilyType.monospace))

  # add line padding
  body.set_style(StyleProperties.LinePadding, LengthType(value=0.25, units=LengthType.Units.c))

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
