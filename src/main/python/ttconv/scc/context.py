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
from typing import Optional, Type, Tuple

from ttconv.model import Div
from ttconv.scc.caption_paragraph import SccCaptionParagraph
from ttconv.scc.caption_style import SccCaptionStyle
from ttconv.scc.codes import SccChannel
from ttconv.scc.codes.attribute_codes import SccAttributeCode
from ttconv.scc.codes.control_codes import SccControlCode
from ttconv.scc.codes.mid_row_codes import SccMidRowCode
from ttconv.scc.codes.preambles_address_codes import SccPreambleAddressCode
from ttconv.scc.config import SccReaderConfiguration, TextAlignment
from ttconv.scc.word import SccWord
from ttconv.style_properties import StyleProperties
from ttconv.time_code import SmpteTimeCode

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

    # Previously read SCC word value
    self.previous_word: Optional[SccWord] = None
    self.previous_word_type: Optional[Type] = None

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

    # Cursor position in the active area
    self.active_cursor: Tuple[int, int] = (0, 0)

    self.current_text_decoration = None
    self.current_color = None
    self.current_font_style = None

    # Text alignment
    self.text_alignment = TextAlignment.AUTO if config is None else config.text_align

    self.new_buffered_caption()

  def new_active_caption(self, begin_time_code: SmpteTimeCode, caption_style: SccCaptionStyle = SccCaptionStyle.Unknown):
    """Initializes a new caption being displayed"""
    self.active_caption = SccCaptionParagraph(self.safe_area_x_offset, self.safe_area_y_offset, caption_style)
    self.count += 1
    self.active_caption.set_id("caption" + str(self.count))
    self.active_caption.set_begin(begin_time_code)

  def new_buffered_caption(self):
    """Resets buffered caption"""
    self.buffered_caption = SccCaptionParagraph(self.safe_area_x_offset, self.safe_area_y_offset, SccCaptionStyle.PopOn)

  def get_caption_to_process(self) -> Optional[SccCaptionParagraph]:
    """Returns the caption currently being processed"""
    if self.current_style in (SccCaptionStyle.PaintOn, SccCaptionStyle.RollUp):
      # If the Paint-On or Roll-Up style is activated, write directly on active caption
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
    if not self.buffered_caption.get_id():
      self.count += 1
      self.buffered_caption.set_id("caption" + str(self.count))

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
        self.div.push_child(previous_caption.to_paragraph(self.div.get_doc()))

  def backspace(self):
    """Move the cursors in a column to the left"""
    self.get_caption_to_process().get_current_text().backspace()
    (row, indent) = self.get_caption_to_process().get_cursor()
    self.get_caption_to_process().set_cursor_at(row, max(indent - 1, 0))

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

    elif self.current_style is SccCaptionStyle.RollUp:

      if not self.has_active_caption():
        # If there is no current active caption, initialize an empty new paragraph
        self.new_active_caption(time_code, SccCaptionStyle.RollUp)

      if self.active_caption.get_begin() is None:
        self.active_caption.set_begin(time_code)

      # Ignore PACs for rows 5-11, but get indent from PACs for rows 1-4 and 12-15. (Roll-Up)
      if pac_row in range(5, 12):
        self.active_caption.set_cursor_at(ROLL_UP_BASE_ROW)
        self.active_caption.new_caption_text()
        return

      # Force roll-up paragraph to belong to the same region
      self.active_caption.set_cursor_at(ROLL_UP_BASE_ROW, pac_indent)

      self.active_caption.new_caption_text()

    elif self.current_style is SccCaptionStyle.PopOn:
      # set cursor in paragraph and create line or text if necessary
      self.buffered_caption.set_cursor_at(pac_row, pac_indent)

    else:
      LOGGER.warning("SCC caption style not defined")

    self.current_color = pac.get_color()
    self.current_font_style = pac.get_font_style()
    self.current_text_decoration = pac.get_text_decoration()

    if self.has_active_caption():
      self.active_cursor = self.active_caption.get_cursor()

  def process_mid_row_code(self, mid_row_code: SccMidRowCode, time_code: SmpteTimeCode):
    """Processes SCC Mid-Row Code to map it to the model"""

    processed_caption = self.get_caption_to_process()

    color = mid_row_code.get_color()
    font_style = mid_row_code.get_font_style()
    text_decoration = mid_row_code.get_text_decoration()

    if self.previous_word_type is not SccMidRowCode:
      # In case of multiple mid-row codes, move right only after the first code

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

    else:
      if color is not None:
        self.current_color = color
      if font_style is not None:
        self.current_font_style = font_style
      if text_decoration is not None:
        self.current_text_decoration = text_decoration

      if processed_caption is not None:
        processed_caption.append_text(" ")
        processed_caption.new_caption_text()

    if processed_caption is not None \
        and processed_caption.get_caption_style() is SccCaptionStyle.PaintOn:
      processed_caption.get_current_text().set_begin(time_code)

  def process_attribute_code(self, attribute_code: SccAttributeCode):
    """Processes SCC Attribute Code to map it to the model"""

    processed_caption = self.get_caption_to_process()

    if processed_caption is None:
      LOGGER.warning("No current SCC caption nor content initialized")
      return

    if processed_caption.get_current_text().get_text():
      processed_caption.new_caption_text()

    if attribute_code.is_background():
      processed_caption.get_current_text().add_style_property(StyleProperties.BackgroundColor, attribute_code.get_color())
    else:
      processed_caption.get_current_text().add_style_property(StyleProperties.Color, attribute_code.get_color())

    processed_caption.get_current_text().add_style_property(StyleProperties.TextDecoration,
                                                            attribute_code.get_text_decoration())

  def process_control_code(self, control_code: SccControlCode, time_code: SmpteTimeCode):
    """Processes SCC Control Code to map it to the model"""

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

      if not self.has_active_caption():
        # If there is currently no active caption, initialize an empty new paragraph
        self.new_active_caption(time_code, SccCaptionStyle.RollUp)

        self.active_caption.set_caption_style(SccCaptionStyle.RollUp)
        self.active_caption.set_cursor_at(ROLL_UP_BASE_ROW, 0)
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
        if time_code is not None:
          # End time is exclusive in the model, set it to the next frame
          end_time_code = copy.copy(time_code)
          end_time_code.add_frames()
        else:
          end_time_code = time_code

        self.push_active_caption_to_model(end_time_code)

    elif control_code is SccControlCode.ENM:
      # Erase buffered caption
      self.new_buffered_caption()

    elif control_code is SccControlCode.TO1:
      self.get_caption_to_process().indent_cursor(1)

    elif control_code is SccControlCode.TO2:
      self.get_caption_to_process().indent_cursor(2)

    elif control_code is SccControlCode.TO3:
      self.get_caption_to_process().indent_cursor(3)

    elif control_code is SccControlCode.CR:
      # Roll the displayed caption up one row (Roll-Up)

      if self.has_active_caption():
        if self.active_caption.get_caption_style() is not SccCaptionStyle.RollUp:
          LOGGER.warning("Cannot roll-up active %s-styled caption, erase it instead.", self.active_caption.get_caption_style().name)
          self.push_active_caption_to_model(time_code)
          return

        if self.active_caption.get_current_text().is_empty():
          self.count -= 1
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

        self.active_caption.set_cursor_at(ROLL_UP_BASE_ROW)

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
      self.backspace()

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

        self.active_caption.append_text(word)

      self.active_caption.get_current_text().add_style_property(StyleProperties.Color, self.current_color)
      self.active_caption.get_current_text().add_style_property(StyleProperties.FontStyle, self.current_font_style)
      self.active_caption.get_current_text().add_style_property(StyleProperties.TextDecoration, self.current_text_decoration)

    elif self.current_style is SccCaptionStyle.RollUp:
      if not self.has_active_caption():
        LOGGER.warning("Initialize active caption buffer to handle roll-up text at %s", time_code)
        self.new_active_caption(time_code, self.current_style)

      self.active_caption.append_text(word)

      self.active_caption.get_current_text().add_style_property(StyleProperties.Color, self.current_color)
      self.active_caption.get_current_text().add_style_property(StyleProperties.FontStyle, self.current_font_style)
      self.active_caption.get_current_text().add_style_property(StyleProperties.TextDecoration, self.current_text_decoration)

    elif self.current_style is SccCaptionStyle.PopOn:
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

    # Remove the buffered caption
    self.new_buffered_caption()
