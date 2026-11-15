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

"""Unit tests for the SCC caption memories"""

# pylint: disable=R0201,C0115,C0116,W0212

import unittest
from fractions import Fraction

from ttconv.scc.display_memory import MEMORY_COLUMNS, SccCellEvent, SccDisplayMemory, SccPen
from ttconv.style_properties import NamedColors, TextDecorationType


def cell(char: str, pen: SccPen = SccPen.DEFAULT, time: int = 0) -> SccCellEvent:
  return SccCellEvent(char, pen, Fraction(time))


def row_text(memory: SccDisplayMemory, row: int) -> str:
  """Returns the text of a row, from its first to its last character, empty
  cells being spaces"""
  return "".join(" " if cell is None else cell.char for cell in memory.get_row_cells(row))


class SccDisplayMemoryTest(unittest.TestCase):

  def test_set_and_get(self):
    memory = SccDisplayMemory()
    self.assertTrue(memory.is_empty())
    self.assertIsNone(memory.get_cell(15, 0))

    memory.set_cell(15, 3, cell("A"))
    memory.set_cell(2, 31, cell("B"))

    self.assertFalse(memory.is_empty())
    self.assertEqual([2, 15], memory.get_rows())
    self.assertEqual("A", memory.get_cell(15, 3).char)
    self.assertEqual("B", memory.get_cell(2, 31).char)
    self.assertIsNone(memory.get_cell(15, 4))

    # emptying the last cell of a row removes the row
    memory.set_cell(2, 31, None)
    self.assertEqual([15], memory.get_rows())

    # emptying an empty cell does nothing
    memory.set_cell(7, 0, None)
    self.assertEqual([15], memory.get_rows())

  def test_is_empty_at(self):
    memory = SccDisplayMemory()
    memory.set_cell(15, 3, cell("A"))

    self.assertFalse(memory.is_empty_at(memory.get_row_positions(15)))
    self.assertFalse(memory.is_empty_at(memory.get_row_positions(15, 3)))
    self.assertTrue(memory.is_empty_at(memory.get_row_positions(15, 4)))
    self.assertTrue(memory.is_empty_at(memory.get_row_positions(14)))
    self.assertTrue(memory.is_empty_at([]))
    self.assertEqual(MEMORY_COLUMNS, len(memory.get_row_positions(1)))

  def test_clear(self):
    memory = SccDisplayMemory()
    memory.set_cell(14, 0, cell("A"))
    memory.set_cell(15, 0, cell("B"))

    memory.clear_row(14)
    self.assertEqual([15], memory.get_rows())

    memory.clear()
    self.assertTrue(memory.is_empty())

  def test_move_row(self):
    memory = SccDisplayMemory()
    memory.set_cell(14, 0, cell("A"))
    memory.set_cell(15, 0, cell("B"))

    # the content of the destination row is replaced
    memory.move_row(15, 14)
    self.assertEqual([14], memory.get_rows())
    self.assertEqual("B", memory.get_cell(14, 0).char)

    # moving an empty row empties the destination row
    memory.move_row(15, 14)
    self.assertTrue(memory.is_empty())

  def test_make_copy(self):
    memory = SccDisplayMemory()
    memory.set_cell(15, 0, cell("A"))

    copy = memory.make_copy()
    memory.set_cell(15, 1, cell("B"))
    memory.set_cell(14, 0, cell("C"))

    self.assertEqual([15], copy.get_rows())
    self.assertEqual("A", row_text(copy, 15))

  def test_row_queries(self):
    memory = SccDisplayMemory()
    for (column, char) in ((3, " "), (4, "A"), (5, "B"), (8, "C"), (9, " "), (10, " ")):
      memory.set_cell(15, column, cell(char))

    self.assertEqual(3, memory.get_first_column(15))
    self.assertEqual(10, memory.get_last_column(15))
    self.assertEqual(8, len(memory.get_row_cells(15)))
    self.assertIsNone(memory.get_row_cells(15)[3])
    self.assertEqual(" AB  C  ", row_text(memory, 15))


  def test_pen(self):
    self.assertFalse(SccPen.DEFAULT.is_underlined())

    pen = SccPen.DEFAULT.make_copy(color=NamedColors.red.value, text_decoration=TextDecorationType(underline=True))
    self.assertTrue(pen.is_underlined())
    self.assertEqual(NamedColors.red.value, pen.color)
    self.assertIsNone(SccPen.DEFAULT.color)

  def test_cell_has_same_content(self):
    self.assertTrue(cell("A", time=1).has_same_content(cell("A", time=2)))
    self.assertFalse(cell("A").has_same_content(cell("B")))
    self.assertFalse(cell("A").has_same_content(cell("A", SccPen.DEFAULT.make_copy(color=NamedColors.red.value))))
    self.assertFalse(cell("A").has_same_content(None))


if __name__ == '__main__':
  unittest.main()
