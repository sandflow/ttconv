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

"""SCC caption text"""

from __future__ import annotations

import logging
import copy
from typing import Optional

from ttconv.time_code import SmpteTimeCode

LOGGER = logging.getLogger(__name__)


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
    if self._cursor < 0:
      # Insert space characters before current text
      self._text = ' ' * -self._cursor + self._text
      self._cursor = 0

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
    self._cursor = max(self._cursor - 1, 0)

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
