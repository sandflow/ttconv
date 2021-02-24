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
from typing import Optional

from ttconv.time_code import SmpteTimeCode
from ttconv.scc.utils import get_position_from_offsets
from ttconv.style_properties import CoordinateType

ROLL_UP_BASE_ROW = 15


class SccCaptionContent:
  """Caption content base class"""


class SccCaptionLineBreak(SccCaptionContent):
  """Caption line break element"""

  def __repr__(self):
    return "<" + self.__class__.__name__ + ">"


class SccCaptionText(SccCaptionContent):
  """Caption text content"""

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
