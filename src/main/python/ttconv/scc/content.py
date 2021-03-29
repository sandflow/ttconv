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
from typing import Optional, List, Union

from ttconv.scc.utils import get_position_from_offsets
from ttconv.style_properties import CoordinateType
from ttconv.time_code import SmpteTimeCode

ROLL_UP_BASE_ROW = 15


class SccCaptionLine:
  """Caption paragraph line"""

  def __init__(self, row: int, indent: int):
    self._texts: List[SccCaptionText] = []
    self._row: int = row  # Row in the active area
    self._indent: int = indent  # Indentation in the active area

  def add_text(self, text: Union[SccCaptionText, str]):
    """Add text to line"""

    if isinstance(text, SccCaptionText):
      self._texts.append(text)

    elif isinstance(text, str):

      if len(self._texts) == 0:
        self._texts.append(SccCaptionText())
      self._texts[-1].append(text)

    else:
      raise ValueError("Unsupported text type for SCC caption line")

  def indent(self, indent: int):
    """Indent current line"""
    self._indent += indent

  def get_current_text(self) -> Optional[SccCaptionText]:
    """Returns current text content"""

    if len(self._texts) == 0:
      return None
    return self._texts[-1]

  def get_texts(self) -> List[SccCaptionText]:
    """Returns the text contents of the line"""
    return self._texts

  def get_length(self) -> int:
    """Returns the total text length"""
    return sum([len(text.get_text()) for text in self._texts])

  def set_row(self, row: int):
    """Sets the line row"""
    self._row = row

  def get_row(self) -> int:
    """Returns the line row"""
    return self._row

  def get_indent(self) -> int:
    """Returns the line indentation"""
    return self._indent

  def is_empty(self) -> bool:
    """Returns whether the line text is empty or not"""
    # no caption texts or an empty text
    return len(self._texts) == 0 or (len(self._texts) == 1 and self._texts[-1].get_text() == "")

  def __repr__(self):
    return "<" + self.__class__.__name__ + " " + str(self.__dict__) + ">"


class SccCaptionText:
  """Caption text content with specific positional, temporal and styling attributes"""

  def __init__(self):
    self._begin: Optional[SmpteTimeCode] = None
    self._end: Optional[SmpteTimeCode] = None
    self._style_properties = {}
    self._text: str = ""
    self._x_offset: int = 0
    self._y_offset: int = 0

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

  def append(self, text: str):
    """Concatenates text content to caption text"""
    self._text += text

  def backspace(self):
    """Remove last character"""
    self._text = self._text[:-1]

  def set_x_offset(self, indent: Optional[int]):
    """Sets the x offset"""
    self._x_offset = indent if indent is not None else 0

  def get_x_offset(self) -> int:
    """Returns the x offset"""
    return self._x_offset

  def set_y_offset(self, row: Optional[int]):
    """Sets the y offset"""
    self._y_offset = row if row is not None else 0

  def get_y_offset(self) -> int:
    """Returns the y offset"""
    return self._y_offset

  def get_position(self) -> CoordinateType:
    """Returns current row and column offsets as a cell-based CoordinateType"""
    return get_position_from_offsets(self._x_offset, self._y_offset)

  def get_style_properties(self) -> dict:
    """Sets the style properties map"""
    return self._style_properties

  def add_style_property(self, style_property, value):
    """Adds a style property"""
    if value is None:
      return
    self._style_properties[style_property] = value

  def is_strictly_contiguous(self, other: SccCaptionText) -> bool:
    """Returns whether the current text is contiguous according to the other text, based on rows and columns"""
    return self._x_offset == other.get_x_offset() and self.is_contiguous(other)

  def is_contiguous(self, other: SccCaptionText) -> bool:
    """Returns whether the current text is contiguous according to the other text, only based on rows"""
    return self._y_offset == other.get_y_offset() + 1

  def has_same_style_properties(self, other):
    """Returns whether the current text has the same style properties as the other text"""
    return self._style_properties == other.get_style_properties()

  def has_same_origin(self, other: SccCaptionText) -> bool:
    """Returns whether the current text has the same origin as the other text"""
    return self._x_offset == other.get_x_offset() and self._y_offset == other.get_y_offset()

  def __repr__(self):
    return "<" + self.__class__.__name__ + " " + str(self.__dict__) + ">"
