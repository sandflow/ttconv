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

"""SCC caption line"""

from __future__ import annotations

import logging
from typing import List, Union

from ttconv.scc.caption_text import SccCaptionText

LOGGER = logging.getLogger(__name__)


class SccCaptionLine:
  """Caption paragraph line"""

  @staticmethod
  def default():
    """Initializes a default caption paragraph line"""
    return SccCaptionLine(0, 0)

  def __init__(self, row: int, indent: int):
    self._row: int = row  # Row in the active area
    self._indent: int = indent  # Indentation in the active area

    self._cursor: int = 0  # Position of the cursor on the line
    self._current_text: SccCaptionText = SccCaptionText()  # Text content where the cursor is
    self._texts: List[SccCaptionText] = [self._current_text]

  def add_text(self, text: Union[SccCaptionText, str]):
    """Add text to line"""

    if isinstance(text, SccCaptionText):
      self._texts.append(text)
      self._current_text = self._texts[-1]
      self._cursor = self.get_length()

    elif isinstance(text, str):
      remaining_text = text

      # While the cursor is not on the last text element, and some text remains
      while self._current_text is not self._texts[-1] and len(remaining_text) > 0:
        available = self._current_text.get_length() - self._current_text.get_cursor()
        text_to_write = remaining_text[:available]

        # Replace current text element content
        self._append_text(text_to_write)
        remaining_text = remaining_text[available:]

      # If some text remains on the last text element
      if len(remaining_text) > 0:
        assert self._current_text is self._texts[-1]

        # Replace and append to current text element content
        self._append_text(remaining_text)

    else:
      raise ValueError("Unsupported text type for SCC caption line")

  def _append_text(self, text: str):
    """Appends text and update cursor position"""
    self._current_text.append(text)
    if self._cursor < 0:
      self._cursor = 0

    self.set_cursor(self._cursor + len(text))

  def indent(self, indent: int):
    """Indent current line"""
    self._indent += indent

  def get_current_text(self) -> SccCaptionText:
    """Returns current text content"""
    return self._current_text

  def get_texts(self) -> List[SccCaptionText]:
    """Returns the text contents of the line"""
    return self._texts

  def get_length(self) -> int:
    """Returns the total text length"""
    return sum([text.get_length() for text in self._texts])

  def set_cursor(self, column: int):
    """Set cursor position"""
    if column > self.get_length():
      LOGGER.warning("Expected cursor position is beyond the line length: force cursor at the end of the line.")
      column = self.get_length()

    self._cursor = column

    diff = self._cursor
    for index, text in enumerate(self._texts):
      is_last_text = index == len(self._texts) - 1
      if diff > text.get_length() or (diff == text.get_length() and not is_last_text):
        diff -= text.get_length()
      else:
        self._current_text = text
        self._current_text.set_cursor_at(diff)
        return

  def get_cursor(self) -> int:
    """Returns the cursor position in the line"""
    return self._cursor

  def set_row(self, row: int):
    """Sets the line row"""
    self._row = row

  def get_row(self) -> int:
    """Returns the line row"""
    return self._row

  def get_indent(self) -> int:
    """Returns the line indentation"""
    return self._indent

  def clear(self):
    """Clears the line text contents"""
    self._texts.clear()
    self._current_text = SccCaptionText()
    self._texts = [self._current_text]
    self.set_cursor(0)

  def is_empty(self) -> bool:
    """Returns whether the line text is empty or not"""
    return self.get_length() == 0

  def get_leading_spaces(self) -> int:
    """Returns the number of leading space characters of the line"""
    index = 0
    leading_spaces = 0

    while index < len(self.get_texts()):
      first_text = self.get_texts()[index].get_text()
      if first_text.isspace():
        leading_spaces += len(first_text)
        index += 1
      else:
        break

    return leading_spaces + len(first_text) - len(first_text.lstrip())

  def get_trailing_spaces(self) -> int:
    """Returns the number of trailing space characters of the line"""
    index = 1
    trailing_spaces = 0
    last_text = self.get_texts()[-index].get_text()

    while last_text.isspace() and index < len(self.get_texts()):
      trailing_spaces += len(last_text)
      index += 1
      last_text = self.get_texts()[-index].get_text()

    return trailing_spaces + len(last_text) - len(last_text.rstrip())

  def __repr__(self):
    return "<" + self.__class__.__name__ + " " + str(self.__dict__) + ">"
