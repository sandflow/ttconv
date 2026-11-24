#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2026, Sandflow Consulting LLC
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

"""Models the display memories of a CTA-608 decoder"""

from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
from typing import ClassVar, Dict, Iterable, List, Optional, Tuple

from ttconv.style_properties import ColorType, FontStyleType, TextDecorationType

MEMORY_ROWS = 15
MEMORY_COLUMNS = 32

# maximum number of rows that have content at any given time (CTA-608-E C.5)
MEMORY_MAX_ROWS = 4


@dataclass(frozen=True)
class SccPen:
  """Models the pen of a CTA-608 decoder"""
  color: Optional[ColorType] = None
  font_style: Optional[FontStyleType] = None
  text_decoration: Optional[TextDecorationType] = None
  background: Optional[ColorType] = None

  # the pen with the default attributes, set below
  DEFAULT: ClassVar[SccPen]

  def make_copy(self, **attributes) -> SccPen:
    """Returns a copy of the pen with the specified attributes changed"""
    return replace(self, **attributes)

  def is_underlined(self) -> bool:
    """Returns whether the pen underlines characters"""
    return self.text_decoration is not None and self.text_decoration.underline is True


SccPen.DEFAULT = SccPen()


@dataclass(frozen=True)
class SccCellEvent:
  """Captures the writing of one character in one cell at a given time"""
  # character written
  char: str
  # pen attributes at the time of writing
  pen: SccPen
  # time, in seconds, at which the character was written
  time: Fraction

  def has_same_content(self, other: Optional[SccCellEvent]) -> bool:
    """Returns whether the character as displayed are identical, regadless of
    their time coordinates"""
    return other is not None and self.char == other.char and self.pen == other.pen


class SccDisplayMemory:
  """Simulates the display and non-display memory of CTA-608 decoder. Rows are
  numbered from 1 to 15, and columns from 0 to 31."""

  def __init__(self):
    self._rows: Dict[int, List[Optional[SccCellEvent]]] = {}

  def get_cell(self, row: int, column: int) -> Optional[SccCellEvent]:
    """Returns the cell at the specified position, None if it is empty"""
    cells = self._rows.get(row)
    return cells[column] if cells is not None else None

  def set_cell(self, row: int, column: int, cell: Optional[SccCellEvent]):
    """Writes the cell at the specified position, or empties the position if
    cell is None"""
    cells = self._rows.get(row)

    if cells is None:
      if cell is None:
        return
      cells = [None] * MEMORY_COLUMNS
      self._rows[row] = cells

    cells[column] = cell

    if cell is None and all(c is None for c in cells):
      del self._rows[row]

  def is_empty_at(self, positions: Iterable[Tuple[int, int]]) -> bool:
    """Returns whether all the specified positions are empty"""
    return all(self.get_cell(row, column) is None for (row, column) in positions)

  def get_row_positions(self, row: int, first_column: int = 0) -> List[Tuple[int, int]]:
    """Returns the positions of a row, from the specified column to the end of
    the row"""
    return [(row, column) for column in range(first_column, MEMORY_COLUMNS)]

  def clear_row(self, row: int):
    """Empties a row"""
    self._rows.pop(row, None)

  def clear(self):
    """Empties the memory"""
    self._rows.clear()

  def is_empty(self) -> bool:
    """Returns whether the memory has no content"""
    return len(self._rows) == 0

  def get_rows(self) -> List[int]:
    """Returns the numbers of the rows that have content, in ascending order"""
    return sorted(self._rows.keys())

  def has_row(self, row: int) -> bool:
    """Returns whether a row has content"""
    return row in self._rows

  def get_oldest_row(self) -> Optional[int]:
    """Returns the row that has content and got its first character before the
    other rows, None if the memory is empty"""
    return next(iter(self._rows), None)

  def get_first_column(self, row: int) -> int:
    """Returns the column of the first character of a row that has content"""
    return next(column for (column, cell) in enumerate(self._rows[row]) if cell is not None)

  def get_last_column(self, row: int) -> int:
    """Returns the column of the last character of a row that has content"""
    cells = self._rows[row]
    return next(column for column in range(len(cells) - 1, -1, -1) if cells[column] is not None)

  def get_row_cells(self, row: int) -> List[Optional[SccCellEvent]]:
    """Returns the cells of a row that has content, from its first to its last
    character, None being an empty cell between characters"""
    return self._rows[row][self.get_first_column(row):self.get_last_column(row) + 1]

  def move_row(self, from_row: int, to_row: int):
    """Moves the content of a row to another row, replacing its content"""
    cells = self._rows.pop(from_row, None)

    if cells is None:
      self._rows.pop(to_row, None)
    else:
      self._rows[to_row] = cells

  def make_copy(self) -> SccDisplayMemory:
    """Returns a copy of the memory, which is not affected by later changes of
    the memory"""
    memory = SccDisplayMemory()
    memory._rows = {row: list(cells) for (row, cells) in self._rows.items()}  # pylint: disable=protected-access
    return memory
