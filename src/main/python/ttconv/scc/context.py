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

"""SCC context"""

from __future__ import annotations

import copy
import logging
from fractions import Fraction
from typing import Optional, Tuple

from ttconv.model import Div
from ttconv.scc.caption_paragraph import SccCaptionParagraph, SCC_SAFE_AREA_CELL_RESOLUTION_COLUMNS
from ttconv.scc.caption_style import SccCaptionStyle
from ttconv.scc.codes import SccChannel, SccCode
from ttconv.scc.codes.attribute_codes import SccAttributeCode
from ttconv.scc.codes.control_codes import SccControlCode
from ttconv.scc.codes.mid_row_codes import SccMidRowCode
from ttconv.scc.codes.preambles_address_codes import SccPreambleAddressCode
from ttconv.scc.config import SccReaderConfiguration, TextAlignment
from ttconv.style_properties import StyleProperties
from ttconv.time_code import SmpteTimeCode, FPS_29_97

ROLL_UP_BASE_ROW = 15

LOGGER = logging.getLogger(__name__)


class SccContext:
  """SCC context for reader"""

  def __init__(self, safe_area_x_offset: int, safe_area_y_offset: int, config: Optional[SccReaderConfiguration] = None):
    # Caption paragraphs container
    self.div: Optional[Div] = None

    # Caption paragraphs counter
    self.count: int = 0

    # Screen safe area offsets
    self.safe_area_x_offset = safe_area_x_offset
    self.safe_area_y_offset = safe_area_y_offset

    # Decoded control code of the immediately preceding word, if that word was a Channel 1 control code
    self.preceding_cc: Optional[SccCode | SccPreambleAddressCode] = None
    # Frame number at which the preceding control code was received
    self.preceding_cc_frame: Optional[int] = None

    # Time of the previous word that was processed, to tell whether a word is sent in the frame that follows it
    self.previous_word_offset: Optional[Fraction] = None

    # Caption style (Pop-on, Roll-up, Paint-on) currently processed
    self.current_style = SccCaptionStyle.default()
    # Buffered caption being built
    self.buffered_caption = None
    # Captions being displayed
    self.active_caption: Optional[SccCaptionParagraph] = None

    # Current caption channel (default is CC1)
    self.current_channel = SccChannel.CHANNEL_1

    # Roll-up caption number of lines
    self.roll_up_depth: int = 0

    # Roll-up caption base row
    self.roll_up_base_row: int = ROLL_UP_BASE_ROW

    # Cursor position in the active area
    self.active_cursor: Tuple[int, int] = (0, 0)

    # Current text styles, None meaning the default
    self.current_text_decoration = None
    self.current_color = None
    self.current_background = None
    self.current_font_style = None

    # Text alignment
    self.text_alignment = TextAlignment.AUTO if config is None else config.text_align

    self.new_buffered_caption()

  def new_active_caption(self, begin_time_code: SmpteTimeCode, caption_style: SccCaptionStyle = SccCaptionStyle.Unknown):
    """Initializes a new caption being displayed"""
    self.active_caption = SccCaptionParagraph(self.safe_area_x_offset, self.safe_area_y_offset, caption_style)
    self.active_caption.set_base_row(self.roll_up_base_row)
    self.active_caption.set_begin(begin_time_code)

  def new_buffered_caption(self):
    """Resets buffered caption"""
    self.buffered_caption = SccCaptionParagraph(self.safe_area_x_offset, self.safe_area_y_offset, SccCaptionStyle.PopOn)

  def get_caption_to_process(self, time_code: SmpteTimeCode) -> Optional[SccCaptionParagraph]:
    """Returns the caption currently being processed"""
    if self.current_style in (SccCaptionStyle.PaintOn, SccCaptionStyle.RollUp):
      # If the Paint-On or Roll-Up style is activated, write directly on active caption
      if not self.has_active_caption():
        self.new_active_caption(time_code, self.current_style)
      return self.active_caption
    if self.current_style is SccCaptionStyle.PopOn:
      # For Pop-On style, write first on a buffered caption
      return self.buffered_caption

    LOGGER.warning("SCC caption style not defined")
    return None

  def has_active_caption(self) -> bool:
    """Returns whether captions are being displayed or not"""
    # return self.active_caption.get_begin() is not None
    return self.active_caption is not None

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
        self.push_active_caption_to_model(time_code)

    # Send the current buffered caption to the active captions list
    self.active_caption = self.buffered_caption
    self.new_buffered_caption()

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

      if not previous_caption.is_empty():
        # number captions as they are added to the model so that ids are unique and sequential
        self.count += 1
        previous_caption.set_id("caption" + str(self.count))
        self.div.push_child(previous_caption.to_paragraph(self.div.get_doc()))

  def backspace(self, time_code: SmpteTimeCode):
    """Move the cursors in a column to the left"""
    caption = self.get_caption_to_process(time_code)
    (row, indent) = caption.get_cursor()

    if indent >= SCC_SAFE_AREA_CELL_RESOLUTION_COLUMNS:
      # After a character in the last column the cursor moves to the column before it, and the
      # character there is erased (CTA-608-E C.13)
      caption.set_cursor_at(row, SCC_SAFE_AREA_CELL_RESOLUTION_COLUMNS - 2)
      caption.append_text(" ")
      caption.set_cursor_at(row, SCC_SAFE_AREA_CELL_RESOLUTION_COLUMNS - 2)
      return

    erased_text = caption.get_current_text()
    if erased_text.is_empty():
      # the character to erase is at the end of an earlier text of the line
      erased_text = next((text for text in reversed(caption.get_current_line().get_texts()) if not text.is_empty()),
                         erased_text)
    erased_text.backspace()
    caption.set_cursor_at(row, max(indent - 1, 0))

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
    self.new_active_caption(time_code, active_style)

    if len(copied_lines) > 0:
      # Set remaining lines to the new buffered caption
      self.active_caption.set_lines(copied_lines)

    self.active_caption.set_cursor_at(cursor[0], cursor[1])

  def move_roll_up_base_row(self, base_row: int, time_code: SmpteTimeCode):
    """Moves the roll-up caption that is displayed to a new base row"""
    shift = base_row - self.roll_up_base_row
    self.roll_up_base_row = base_row

    if not self.has_active_caption():
      return

    if self.active_caption.is_empty():
      self.active_caption.set_base_row(base_row)
      return

    # The caption is displayed on the rows it had up to now
    moved_lines = self.active_caption.copy_lines()
    self.push_active_caption_to_model(time_code)

    self.new_active_caption(time_code, SccCaptionStyle.RollUp)
    self.active_caption.set_lines({row + shift: line for row, line in moved_lines.items()})
    for row, line in self.active_caption.get_lines().items():
      line.set_row(row)

  def process_preamble_address_code(self, pac: SccPreambleAddressCode, time_code: SmpteTimeCode):
    """Processes SCC Preamble Address Code it to the map to model"""

    pac_row = pac.get_row()
    pac_indent = pac.get_indent()

    if self.current_style is SccCaptionStyle.PaintOn:

      self.paint_on_active_caption(time_code)

      # A row that is written again from its first cell is replaced. (A PAC does not erase anything in CTA-608-E: the
      # text that follows overwrites the characters, which this reader does not map, and the end of the row is deleted
      # by a DER. A PAC for the middle of a row only moves the cursor.)
      target_row = self.active_caption.get_lines().get(pac_row)
      if target_row is not None and (pac_indent or 0) <= target_row.get_indent():
        target_row.clear()

      self.active_caption.set_cursor_at(pac_row, pac_indent)

    elif self.current_style is SccCaptionStyle.RollUp:

      if not self.has_active_caption():
        # If there is no current active caption, initialize an empty new paragraph
        self.new_active_caption(time_code, SccCaptionStyle.RollUp)

      if self.active_caption.get_begin() is None:
        self.active_caption.set_begin(time_code)

      # The PAC row is the base row of the roll-up caption, but the rows of the caption have to fit above it
      # (CTA-608-E C.4, C.7)
      base_row = max(pac_row, self.roll_up_depth)

      if base_row != self.roll_up_base_row:
        self.move_roll_up_base_row(base_row, time_code)

      self.active_caption.set_cursor_at(base_row, pac_indent)

      self.active_caption.new_caption_text()

    elif self.current_style is SccCaptionStyle.PopOn:
      # set cursor in paragraph and create line or text if necessary
      self.buffered_caption.set_cursor_at(pac_row, pac_indent)

    else:
      LOGGER.warning("SCC caption style not defined")

    self.current_color = pac.get_color()
    self.current_font_style = pac.get_font_style()
    self.current_text_decoration = pac.get_text_decoration()
    self.current_background = None

    if self.has_active_caption():
      self.active_cursor = self.active_caption.get_cursor()

  def process_mid_row_code(self, mid_row_code: SccMidRowCode, time_code: SmpteTimeCode):
    """Processes SCC Mid-Row Code to map it to the model"""

    processed_caption = self.get_caption_to_process(time_code)

    color = mid_row_code.get_color()
    font_style = mid_row_code.get_font_style()
    text_decoration = mid_row_code.get_text_decoration()

    # If there is already text on the current line
    if processed_caption is not None \
        and processed_caption.get_current_text() is not None \
        and not processed_caption.get_current_text().is_empty():

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

    elif processed_caption is not None:
      processed_caption.append_text(" ")

    self.current_color = color
    self.current_font_style = font_style
    self.current_text_decoration = text_decoration

    if processed_caption is not None \
        and processed_caption.get_caption_style() is SccCaptionStyle.PaintOn:
      processed_caption.get_current_text().set_begin(time_code)

  def process_attribute_code(self, attribute_code: SccAttributeCode, time_code: SmpteTimeCode):
    """Processes SCC Attribute Code to map it to the model"""

    processed_caption = self.get_caption_to_process(time_code)

    if processed_caption is None:
      LOGGER.warning("No current SCC caption nor content initialized")
      return

    if processed_caption.get_current_text().get_text():
      processed_caption.new_caption_text()

    if attribute_code.is_background():
      self.current_background = attribute_code.get_color()
    else:
      self.current_color = attribute_code.get_color()
      self.current_text_decoration = attribute_code.get_text_decoration()

  def reset_current_char_styles(self):
    """Resets the current character styles to their defaults"""
    self.current_text_decoration = None
    self.current_color = None
    self.current_background = None
    self.current_font_style = None

  def process_control_code(self, control_code: SccControlCode, time_code: SmpteTimeCode):
    """Processes SCC Control Code to map it to the model"""

    if control_code is SccControlCode.RCL:
      # Start a new Pop-On caption
      self.current_style = SccCaptionStyle.PopOn

    elif control_code is SccControlCode.RDC:
      # Start a new Paint-On caption
      self.current_style = SccCaptionStyle.PaintOn

    elif control_code in (SccControlCode.RU2, SccControlCode.RU3, SccControlCode.RU4):
      
      if self.current_style is not SccCaptionStyle.RollUp:
        # Switching to roll-up style erases both display and non-display memories
        # (CTA-608-E C.10)
        self.push_active_caption_to_model(time_code)
        self.new_buffered_caption()

      # Start a new Roll-Up caption
      self.current_style = SccCaptionStyle.RollUp

      if control_code is SccControlCode.RU2:
        self.roll_up_depth = 2

      elif control_code is SccControlCode.RU3:
        self.roll_up_depth = 3

      elif control_code is SccControlCode.RU4:
        self.roll_up_depth = 4

      if not self.has_active_caption() or self.active_caption.is_empty():
        # The base row is row 15 when no roll-up caption is displayed (CTA-608-E C.15)
        self.roll_up_base_row = ROLL_UP_BASE_ROW

      self.roll_up_base_row = max(self.roll_up_base_row, self.roll_up_depth)

      if not self.has_active_caption():
        # If there is currently no active caption, initialize an empty new paragraph
        self.new_active_caption(time_code, SccCaptionStyle.RollUp)

        self.active_caption.set_caption_style(SccCaptionStyle.RollUp)
        self.active_caption.set_cursor_at(self.roll_up_base_row, 0)
        self.active_caption.new_caption_line()
        self.active_caption.new_caption_text()

        self.active_cursor = self.active_caption.get_cursor()

    elif control_code is SccControlCode.EOC:
      # Display caption (Pop-On)
      self.buffered_caption.set_begin(time_code)
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
        self.push_active_caption_to_model(time_code)

    elif control_code is SccControlCode.ENM:
      # Erase buffered caption
      self.new_buffered_caption()

    elif control_code is SccControlCode.FON:
      # Flash On is displayed as a space (see 47 CFR Ch. I, § 15.119(i))
      self.process_text(" ", time_code)

    elif control_code is SccControlCode.TO1:
      self.get_caption_to_process(time_code).tab_cursor(1)

    elif control_code is SccControlCode.TO2:
      self.get_caption_to_process(time_code).tab_cursor(2)

    elif control_code is SccControlCode.TO3:
      self.get_caption_to_process(time_code).tab_cursor(3)

    elif control_code is SccControlCode.CR:
      # Roll the displayed caption up one row (Roll-Up)

      # the new row starts with the default style (see CTA 608, C.14)
      self.reset_current_char_styles()

      if self.has_active_caption():
        if self.active_caption.get_caption_style() is not SccCaptionStyle.RollUp:
          LOGGER.warning("Cannot roll-up active %s-styled caption, erase it instead.", self.active_caption.get_caption_style().name)
          self.push_active_caption_to_model(time_code)
          return

        if self.active_caption.is_empty():
          # nothing is displayed: there is nothing to roll up
          previous_lines = []
        else:
          # Push active caption to model (but don't erase it)
          self.push_active_caption_to_model(time_code, False)
          # Roll the active caption up
          self.active_caption.roll_up()
          # Get the remaining lines to initialize the following caption with the expected depth
          previous_lines = self.active_caption.get_last_caption_lines(self.roll_up_depth - 1)

        # Initialize the new caption with the previous lines
        self.new_active_caption(time_code, SccCaptionStyle.RollUp)
        self.active_caption.set_lines(previous_lines)

        self.active_caption.set_cursor_at(self.roll_up_base_row)

    elif control_code is SccControlCode.DER:
      # Delete to End of Row: the characters from (and including) the current cell to the end of the row are deleted
      # (CTA-608-E B.3). A row of a Paint-On caption is erased by it, not by a PAC.
      if self.current_style is SccCaptionStyle.PaintOn and self.has_active_caption() \
          and not self.active_caption.is_empty():
        # What is displayed until the code is received
        self.paint_on_active_caption(time_code)

      caption = self.get_caption_to_process(time_code)
      if caption is not None:
        caption.delete_to_end_of_row()

    elif control_code is SccControlCode.BS:
      # Backspace
      # When a Backspace is received, the cursor moves to the left one column position erasing
      # the character or Mid-Row Code occupying that location, unless the cursor is in Column 1
      if self.current_style is SccCaptionStyle.PaintOn and self.has_active_caption() \
          and not self.active_caption.is_empty():
        # The character is on screen until the code erases it: end the paragraph that shows it here
        self.paint_on_active_caption(time_code)

      self.backspace(time_code)

  def process_text(self, word: str, time_code: SmpteTimeCode):
    """Processes SCC text words"""
    if self.current_style is SccCaptionStyle.PaintOn:
      if not self.has_active_caption():
        LOGGER.warning("Initialize active caption buffer to handle paint-on text at %s", time_code)
        self.paint_on_active_caption(time_code)

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

        elif self.previous_word_offset is not None \
            and time_code.to_temporal_offset() - self.previous_word_offset > 1 / FPS_29_97:
          # Not sent in the frame after the previous word: the text before it was on screen alone for a while
          if not self.active_caption.get_current_text().is_empty():
            self.active_caption.new_caption_text()
          self.active_caption.get_current_text().set_begin(time_code)

        self.active_caption.append_text(word)

      self.active_caption.get_current_text().add_style_property(StyleProperties.Color, self.current_color)
      self.active_caption.get_current_text().add_style_property(StyleProperties.FontStyle, self.current_font_style)
      self.active_caption.get_current_text().add_style_property(StyleProperties.TextDecoration, self.current_text_decoration)
      if self.current_background is not None:
        self.active_caption.get_current_text().add_style_property(StyleProperties.BackgroundColor, self.current_background)

    elif self.current_style is SccCaptionStyle.RollUp:
      if not self.has_active_caption():
        LOGGER.warning("Initialize active caption buffer to handle roll-up text at %s", time_code)
        self.new_active_caption(time_code, self.current_style)

      self.active_caption.append_text(word)

      self.active_caption.get_current_text().add_style_property(StyleProperties.Color, self.current_color)
      self.active_caption.get_current_text().add_style_property(StyleProperties.FontStyle, self.current_font_style)
      self.active_caption.get_current_text().add_style_property(StyleProperties.TextDecoration, self.current_text_decoration)
      if self.current_background is not None:
        self.active_caption.get_current_text().add_style_property(StyleProperties.BackgroundColor, self.current_background)

    elif self.current_style is SccCaptionStyle.PopOn:
      self.buffered_caption.append_text(word)

      self.buffered_caption.get_current_text().add_style_property(StyleProperties.Color, self.current_color)
      self.buffered_caption.get_current_text().add_style_property(StyleProperties.FontStyle, self.current_font_style)
      self.buffered_caption.get_current_text().add_style_property(StyleProperties.TextDecoration, self.current_text_decoration)
      if self.current_background is not None:
        self.buffered_caption.get_current_text().add_style_property(StyleProperties.BackgroundColor, self.current_background)

    if self.has_active_caption():
      self.active_cursor = self.active_caption.get_cursor()

  def flush(self, time_code: Optional[SmpteTimeCode] = None):
    """Flushes the remaining current caption"""
    if self.has_active_caption():
      self.push_active_caption_to_model(time_code)

    # Remove the buffered caption
    self.new_buffered_caption()
