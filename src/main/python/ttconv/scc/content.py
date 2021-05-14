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

"""SCC caption content"""

from __future__ import annotations

import copy
import logging
from typing import Optional, List, Union

from ttconv.time_code import SmpteTimeCode

LOGGER = logging.getLogger(__name__)

ROLL_UP_BASE_ROW = 15


class SccCaptionLine:
  """Caption paragraph line"""

  def __init__(self, row: int, indent: int):
    self._texts: List[SccCaptionText] = []
    self._row: int = row  # Row in the active area
    self._indent: int = indent  # Indentation in the active area

    self._cursor: int = 0  # Position of the cursor on the line
    self._current_text: Optional[SccCaptionText] = None  # Text content where the cursor is

  def add_text(self, text: Union[SccCaptionText, str]):
    """Add text to line"""

    if isinstance(text, SccCaptionText):
      self._texts.append(text)
      self._current_text = self._texts[-1]
      self._cursor = self.get_length()

    elif isinstance(text, str):

      if self._current_text is None:
        # Initialize a new text element if necessary
        self._texts.append(SccCaptionText(text))
        self._current_text = self._texts[-1]
        self._cursor = self._current_text.get_length()

      else:
        remaining_text = text

        # While the cursor is not on the last text element, and some text remains
        while self._current_text is not self._texts[-1] and len(remaining_text) > 0:
          available = self._current_text.get_length() - self.get_current_text().get_cursor()
          text_to_write = remaining_text[:available]

          # Replace current text element content
          self._current_text.append(text_to_write)
          self.set_cursor(self._cursor + len(text_to_write))
          remaining_text = remaining_text[available:]

        # If some text remains on the last text element
        if len(remaining_text) > 0:
          assert self._current_text is self._texts[-1]

          # Replace and append to current text element content
          self._current_text.append(remaining_text)
          self.set_cursor(self._cursor + len(remaining_text))

    else:
      raise ValueError("Unsupported text type for SCC caption line")

  def indent(self, indent: int):
    """Indent current line"""
    self._indent += indent

  def get_current_text(self) -> Optional[SccCaptionText]:
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
    self._current_text = None
    self.set_cursor(0)

  def is_empty(self) -> bool:
    """Returns whether the line text is empty or not"""
    # no caption texts or an empty text
    return len(self._texts) == 0 or (len(self._texts) == 1 and self._texts[-1].get_text() == "")

  def get_leading_spaces(self) -> int:
    """Returns the number of leading space characters of the line"""
    index = 0
    leading_spaces = 0
    first_text = self.get_texts()[index].get_text()

    while first_text.isspace() and index < len(self.get_texts()):
      leading_spaces += len(first_text)
      index += 1
      first_text = self.get_texts()[index].get_text()

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


class SccCaptionText:
  """Caption text content with specific positional, temporal and styling attributes"""

  def __init__(self, text: Optional[str] = ""):
    self._begin: Optional[SmpteTimeCode] = None
    self._end: Optional[SmpteTimeCode] = None
    self._style_properties = {}
    self._text: str = ""
    self._cursor = 0  # Cursor in the text

    if text is not None and text != "":
      self.append(text)

  def set_begin(self, time_code: SmpteTimeCode):
    """Sets begin time code"""
    self._begin = copy.copy(time_code)

  def get_begin(self) -> SmpteTimeCode:
    """Returns the begin time code"""
    return self._begin

  def set_end(self, time_code: SmpteTimeCode):
    """Sets end time code"""
    self._end = copy.copy(time_code)

  def get_end(self) -> SmpteTimeCode:
    """Returns the end time code"""
    return self._end

  def get_text(self) -> str:
    """Returns the text"""
    return self._text

  def get_length(self) -> int:
    """Returns text length"""
    return len(self._text)

  def is_empty(self) -> bool:
    """Returns whether the text is empty or not"""
    return self.get_length() == 0

  def append(self, text: str):
    """Add or replace text content at cursor position"""
    # print("Append text: ", text, "to", self._text, "at", self._cursor)
    self._text = self._text[:self._cursor] + text + self._text[(self._cursor + len(text)):]
    self._cursor += len(text)
    # print("\t=>", self._text, ", cursor:", self._cursor)

  def set_cursor_at(self, position: int):
    """Set text cursor position"""
    self._cursor = position

  def get_cursor(self) -> int:
    """Returns the cursor position"""
    return self._cursor

  def backspace(self):
    """Remove last character"""
    self._text = self._text[:-1]

  def get_style_properties(self) -> dict:
    """Sets the style properties map"""
    return self._style_properties

  def add_style_property(self, style_property, value):
    """Adds a style property"""
    if value is None:
      return
    self._style_properties[style_property] = value

  def has_same_style_properties(self, other):
    """Returns whether the current text has the same style properties as the other text"""
    return self._style_properties == other.get_style_properties()

  def __repr__(self):
    return "<" + self.__class__.__name__ + " " + str(self.__dict__) + ">"
