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


"""SCC context: a CTA-608 decoder state machine"""

from __future__ import annotations

import logging
from fractions import Fraction
from typing import Iterable, List, Optional, Tuple

from ttconv.model import Div
from ttconv.scc.display_memory_snapshot import SccDisplayMemorySnapshot
from ttconv.scc.caption_style import SccCaptionStyle
from ttconv.scc.codes import SccChannel, SccCode
from ttconv.scc.codes.attribute_codes import SccAttributeCode
from ttconv.scc.codes.control_codes import SccControlCode
from ttconv.scc.codes.mid_row_codes import SccMidRowCode
from ttconv.scc.codes.preambles_address_codes import SccPreambleAddressCode
from ttconv.scc.config import SccReaderConfiguration, TextAlignment
from ttconv.scc.display_memory import MEMORY_COLUMNS, MEMORY_MAX_ROWS, SccCellEvent, SccDisplayMemory, SccPen
from ttconv.time_code import SmpteTimeCode

LOGGER = logging.getLogger(__name__)

class SccContext:
  """CTA-608 decoder"""

  # base row of the Roll-Up window, and row of the cursor, until a PAC is received
  _DEFAULT_BASE_ROW = 15

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

    # Current caption channel (default is CC1)
    self.current_channel = SccChannel.CHANNEL_1

    # Text alignment of Pop-On captions
    self.text_alignment = TextAlignment.AUTO if config is None else config.text_align

    # Caption style (Pop-On, Roll-Up, Paint-On) selected by the last RCL, RUx or RDC code
    self.current_style = SccCaptionStyle.default()

    # Memories
    self.displayed = SccDisplayMemory()
    self.non_displayed = SccDisplayMemory()

    # Cursor, in the memory being written: rows from 1 to 15, columns from 0 to 31
    self.row: int = self._DEFAULT_BASE_ROW
    self._column: int = 0

    # Whether a character was written at the last column since the cursor moved, so that the next character
    # overflows the row, and whether the overflow was reported
    self._is_last_column_written: bool = False
    self._is_overflow_reported: bool = False

    # Attributes of the characters being written
    self.pen: SccPen = SccPen.DEFAULT

    # Roll-Up window: number of rows, and bottom row
    self.roll_up_depth: int = 0
    self.base_row: int = self._DEFAULT_BASE_ROW

    # Begin time and style of the caption being displayed, if any
    self.caption_begin: Optional[Fraction] = None
    self.caption_style: Optional[SccCaptionStyle] = None

  @property
  def column(self) -> int:
    """Column of the cursor"""
    return self._column

  @column.setter
  def column(self, column: int):
    if column != self._column:
      # moving the cursor ends any overflow of the row
      self._is_last_column_written = False
      self._is_overflow_reported = False
    self._column = column

  #
  # captions
  #

  def _end_caption(self, time: Optional[Fraction]):
    """Ends the caption being displayed, if any, and adds it to the model"""
    if self.caption_begin is None:
      return

    begin = self.caption_begin
    self.caption_begin = None

    # captions that have no content or no duration are not added
    if self.displayed.is_empty() or (time is not None and time <= begin):
      return

    caption = SccDisplayMemorySnapshot(self.displayed.make_copy(), self.caption_style, begin, time,
                                       safe_area_x_offset=self.safe_area_x_offset,
                                       safe_area_y_offset=self.safe_area_y_offset,
                                       text_alignment=self.text_alignment)

    # number captions as they are added to the model so that ids are unique and sequential
    self.count += 1
    self.div.push_child(caption.to_paragraph(self.div.get_doc(), "caption" + str(self.count)))

  def _start_caption(self, time: Fraction, caption_style: SccCaptionStyle):
    """Begins a caption if there is none and the displayed memory has content"""
    if self.caption_begin is None and not self.displayed.is_empty():
      self.caption_begin = time
      self.caption_style = caption_style

  #
  # memory operations
  #

  def _get_current_memory(self) -> SccDisplayMemory:
    """Returns the memory written by the current caption style"""
    return self.non_displayed if self.current_style is SccCaptionStyle.PopOn else self.displayed

  def _write_at_cursor(self, char: str, time: Fraction, replace_previous: bool = False):
    """Writes a character at the cursor, and moves the cursor to the next
    column, if any. If replace_previous is true, the character replaces the one
    in the preceding column instead, e.g. extended characters."""
    if replace_previous and self.column > 0:
      self.column -= 1

    memory = self._get_current_memory()

    if not memory.has_row(self.row) and len(memory.get_rows()) >= MEMORY_MAX_ROWS:
      # at most 4 rows have content at any given time: the first character of a
      # fifth row erases the row that got its first character first (CTA-608-E C.5)
      oldest_row = memory.get_oldest_row()
      self._erase_at_positions(memory, memory.get_row_positions(oldest_row), time)

    if self._is_last_column_written and not self._is_overflow_reported:
      self._is_overflow_reported = True
      LOGGER.warning("The text overflows the last column of row %s (at %s): the characters after it replace the "
                     "one in the last column", self.row, f"{float(time):.3f}s")

    previous_cell = memory.get_cell(self.row, self.column)

    if replace_previous and previous_cell is not None:
      # the replaced character was displayed for at most one frame: the new one takes its place
      cell = SccCellEvent(char, self.pen, previous_cell.time)
    else:
      cell = SccCellEvent(char, self.pen, time)

    if not cell.has_same_content(previous_cell):
      if memory is self.displayed and ((previous_cell is not None and not replace_previous)
                                       or self.caption_style is not self.current_style):
        # replacing a displayed character, or adding one in another caption style, ends the caption
        self._end_caption(time)

      memory.set_cell(self.row, self.column, cell)

      if memory is self.displayed:
        self._start_caption(time, self.current_style)

    # characters received at the last column replace the character in that column
    is_last_column = self.column == MEMORY_COLUMNS - 1
    self.column = min(self.column + 1, MEMORY_COLUMNS - 1)
    self._is_last_column_written = is_last_column

  def _erase_at_positions(self, memory: SccDisplayMemory, positions: Iterable[Tuple[int, int]], time: Fraction):
    """Empties the specified positions of a memory"""
    positions = list(positions)

    if memory.is_empty_at(positions):
      return

    caption_style = self.caption_style if self.caption_style is not None else self.current_style

    if memory is self.displayed:
      self._end_caption(time)

    for (row, column) in positions:
      memory.set_cell(row, column, None)

    if memory is self.displayed:
      self._start_caption(time, caption_style)

  def _roll_up_window(self) -> List[int]:
    """Returns the rows of the Roll-Up window, from top to bottom"""
    return list(range(self.base_row - self.roll_up_depth + 1, self.base_row + 1))

  def _move_roll_up_window(self, base_row: int):
    """Moves the Roll-Up window, and the rows it displays, so that its bottom
    row is the specified row."""
    if base_row == self.base_row:
      return

    displayed_rows = [row for row in self.displayed.get_rows() if row in self._roll_up_window()]

    offset = base_row - self.base_row
    for row in sorted(displayed_rows, reverse=offset > 0):
      self.displayed.move_row(row, row + offset)

    self.base_row = base_row

  #
  # codes
  #

  def process_preamble_address_code(self, pac: SccPreambleAddressCode):
    row = pac.get_row()

    if self.current_style is SccCaptionStyle.RollUp:
      # the PAC row is the new base row of the Roll-Up window, which must fit in
      # the screen (see CTA 608, C.4)
      self._move_roll_up_window(max(row, self.roll_up_depth))
      row = self.base_row

    self.row = row
    self.column = pac.get_indent() if pac.get_indent() is not None else 0
    self.pen = SccPen(color=pac.get_color(), font_style=pac.get_font_style(), text_decoration=pac.get_text_decoration())

  def process_mid_row_code(self, mid_row_code: SccMidRowCode, time_code: SmpteTimeCode):
    time = time_code.to_temporal_offset()

    new_pen = self.pen.make_copy(color=mid_row_code.get_color(),
                                       font_style=mid_row_code.get_font_style(),
                                       text_decoration=mid_row_code.get_text_decoration())

    # the space is underlined only if the text on both sides of it is underlined
    self.pen = new_pen.make_copy(
      text_decoration=new_pen.text_decoration if self.pen.is_underlined() and new_pen.is_underlined() else None)
    self._write_at_cursor(" ", time)

    self.pen = new_pen

  def process_attribute_code(self, attribute_code: SccAttributeCode):
    if attribute_code.is_background():
      self.pen = self.pen.make_copy(background=attribute_code.get_color())
    else:
      self.pen = self.pen.make_copy(color=attribute_code.get_color(),
                                          text_decoration=attribute_code.get_text_decoration())

  def process_control_code(self, control_code: SccControlCode, time_code: SmpteTimeCode):
    time = time_code.to_temporal_offset()

    if control_code is SccControlCode.RCL:
      self.current_style = SccCaptionStyle.PopOn

    elif control_code is SccControlCode.RDC:
      self.current_style = SccCaptionStyle.PaintOn

    elif control_code in (SccControlCode.RU2, SccControlCode.RU3, SccControlCode.RU4):
      depth = {SccControlCode.RU2: 2, SccControlCode.RU3: 3, SccControlCode.RU4: 4}[control_code]

      if self.current_style is not SccCaptionStyle.RollUp:
        # Switching to Roll-Up erases both memories, and the cursor moves to the base row (CTA-608-E C.10)
        self._end_caption(time)
        self.displayed.clear()
        self.non_displayed.clear()
        self.base_row = self._DEFAULT_BASE_ROW
        self.row = self.base_row
        self.column = 0

      self.current_style = SccCaptionStyle.RollUp
      self.roll_up_depth = depth

      # the window must fit in the screen
      self._move_roll_up_window(max(self.base_row, depth))
      self.row = self.base_row

      # rows above the window are erased, e.g. when the number of rows decreases
      self._erase_at_positions(self.displayed, [(row, column) for row in range(1, self.base_row - depth + 1)
                                                for column in range(MEMORY_COLUMNS)], time)

    elif control_code is SccControlCode.EOC:
      # Swap the memories
      self._end_caption(time)
      self.displayed, self.non_displayed = self.non_displayed, self.displayed
      self._start_caption(time, SccCaptionStyle.PopOn)

    elif control_code is SccControlCode.EDM:
      self._end_caption(time)
      self.displayed.clear()

    elif control_code is SccControlCode.ENM:
      self.non_displayed.clear()

    elif control_code in (SccControlCode.TO1, SccControlCode.TO2, SccControlCode.TO3):
      offset = {SccControlCode.TO1: 1, SccControlCode.TO2: 2, SccControlCode.TO3: 3}[control_code]
      self.column = min(self.column + offset, MEMORY_COLUMNS - 1)

    elif control_code is SccControlCode.CR:
      self._carriage_return(time)

    elif control_code is SccControlCode.DER:
      # Erases the characters from the cursor to the end of the row
      memory = self._get_current_memory()
      self._erase_at_positions(memory, memory.get_row_positions(self.row, self.column), time)

    elif control_code is SccControlCode.BS:
      # The character is erased, unless the cursor is in the first column
      if self.column > 0:
        self.column -= 1
        self._erase_at_positions(self._get_current_memory(), [(self.row, self.column)], time)

    elif control_code is SccControlCode.FON:
      # Flash On occupies a cell, and is displayed as a space (see 47 CFR Ch. I, § 15.119(i))
      self._write_at_cursor(" ", time)

    else:
      LOGGER.debug("Ignored SCC control code: %s", control_code.get_name())

  def _carriage_return(self, time: Fraction):
    """Rolls the Roll-Up window up one row"""
    if self.current_style is not SccCaptionStyle.RollUp:
      LOGGER.warning("Ignored CR in %s style", self.current_style.name)
      return

    # the new row starts with the default attributes (CTA-608-E C.14)
    self.pen = SccPen.DEFAULT

    window = self._roll_up_window()

    if not self.displayed.is_empty_at([(row, column) for row in window for column in range(MEMORY_COLUMNS)]):
      self._end_caption(time)

      for row in window[:-1]:
        self.displayed.move_row(row + 1, row)
      self.displayed.clear_row(self.base_row)

      self._start_caption(time, SccCaptionStyle.RollUp)

    self.row = self.base_row
    self.column = 0

  def process_text(self, word: str, time_code: SmpteTimeCode):
    time = time_code.to_temporal_offset()

    for char in word:
      self._write_at_cursor(char, time)

  def process_extended_character(self, char: str, time_code: SmpteTimeCode):
    self._write_at_cursor(char, time_code.to_temporal_offset(), replace_previous=True)

  def flush(self, time_code: Optional[SmpteTimeCode] = None):
    self._end_caption(time_code.to_temporal_offset() if time_code is not None else None)
