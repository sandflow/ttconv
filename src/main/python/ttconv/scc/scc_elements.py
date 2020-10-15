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

"""SCC elements"""

from __future__ import annotations

import copy
import logging
from enum import Enum
from typing import List, Optional

from ttconv.model import Document, P, Span, Br, Text
from ttconv.scc.time_codes import SccTimeCode
from ttconv.style_properties import PositionType, LengthType, StyleProperties

ROLL_UP_BASE_ROW = 15

class SccCaptionStyle(Enum):
  """SCC caption style"""
  Unknown = 0
  RollUp = 1
  PaintOn = 2
  PopOn = 3


class SccCaptionContent:
  """Caption content"""


class SccCaptionLineBreak(SccCaptionContent):
  """Caption line break element"""


class SccCaptionText(SccCaptionContent):
  """Caption text content"""

  def __init__(self):
    self.x_offset: int = 0
    self.y_offset: int = 0
    self.style_properties = {}
    self.text: str = ""
    self._position = None
    self._new_line = False

  def set_x_offset(self, indent: Optional[int]):
    """Sets the x offset"""
    self.x_offset = indent if indent else 0

  def set_y_offset(self, row: Optional[int]):
    """Sets the y offset"""
    self.y_offset = row if row else 0

  def add_style_property(self, style_property, value):
    """Adds a style property"""
    if value is None:
      return
    self.style_properties[style_property] = value

  def get_position(self) -> PositionType:
    """Returns current row and column offsets as a cell-based PositionType"""
    x_position = LengthType(value=self.x_offset, units=LengthType.Units.c)
    y_position = LengthType(value=self.y_offset, units=LengthType.Units.c)

    return PositionType(x_position, y_position)

  def has_same_style_properties(self, other):
    """Returns whether the current text has the same style properties as the other text"""
    return self.style_properties == other.style_properties

  def is_contiguous(self, other: SccCaptionText) -> bool:
    """Returns whether the current text is contiguous according to the other text"""
    return self.x_offset == other.x_offset and self.y_offset == other.y_offset + 1

  def has_same_origin(self, other: SccCaptionText) -> bool:
    """Returns whether the current text has the same origin as the other text"""
    return self.x_offset == other.x_offset and self.y_offset == other.y_offset


class SccCaptionParagraph:
  """Caption paragraph"""

  def __init__(self, safe_area_x_offset: int = 0, safe_area_y_offset: int = 0,
               caption_style: SccCaptionStyle = SccCaptionStyle.Unknown):
    self._caption_id: str = ""
    self._begin: Optional[SccTimeCode] = None
    self._end: Optional[SccTimeCode] = None
    self._safe_area_x_offset = safe_area_x_offset
    self._safe_area_y_offset = safe_area_y_offset
    self._column_offset: int = safe_area_x_offset
    self._row_offset: int = safe_area_y_offset
    self.current_text: Optional[SccCaptionText] = None
    self.caption_contents: List[SccCaptionContent] = []
    self._style: SccCaptionStyle = caption_style

  def set_id(self, caption_id: str):
    """Sets caption identifier"""
    self._caption_id = caption_id

  def set_begin(self, time_code):
    """Sets caption begin time code"""
    self._begin = copy.copy(time_code)

  def set_end(self, time_code):
    """Sets caption end time code"""
    self._end = copy.copy(time_code)

  def set_column_offset(self, indent: Optional[int]):
    """Sets the paragraph x offset"""
    self._column_offset = self._safe_area_x_offset + (indent if indent else 0)

  def set_row_offset(self, row: Optional[int]):
    """Sets the paragraph y offset"""
    self._row_offset = self._safe_area_y_offset + (row if row else 0)

  def new_caption_text(self):
    """Appends a new caption text content, and keeps reference on it"""
    self.caption_contents.append(SccCaptionText())
    self.current_text = self.caption_contents[-1]

  def set_current_text_offsets(self):
    """Sets the x and y offsets of the current text"""
    self.current_text.set_x_offset(self._column_offset)
    self.current_text.set_y_offset(self._row_offset)

  def set_roll_up_row_offsets(self):
    """Sets Roll-up captions row offset in relation to the base row 15"""
    if self._style is not SccCaptionStyle.RollUp:
      raise RuntimeError(f"Cannot set Roll-Up row offset for {self._style}-styled caption.")

    count = 0
    for caption_content in reversed(self.caption_contents):
      if not isinstance(caption_content, SccCaptionText):
        count += 1
        continue
      caption_content.set_y_offset(self._safe_area_y_offset + ROLL_UP_BASE_ROW - count)

    self.set_row_offset(ROLL_UP_BASE_ROW)

  def indent(self, indent: int):
    """Indents the current text (x offset)"""
    self._column_offset += indent
    self.current_text.set_x_offset(self._column_offset)

  def get_style(self) -> SccCaptionStyle:
    """Returns the caption style"""
    return self._style

  def get_last_caption_lines(self, expected_lines: int) -> List[SccCaptionText]:
    """Returns the caption text elements from the expected number of last lines"""
    last_lines = []
    added_lines = 0
    for caption in reversed(self.caption_contents):
      if isinstance(caption, SccCaptionLineBreak):
        added_lines += 1

      if added_lines == expected_lines:
        return last_lines

      last_lines.insert(0, caption)

    return last_lines

  def to_paragraph(self, doc: Document) -> P:
    """Converts and returns current caption paragraph into P instance"""
    p = P()
    p.set_doc(doc)
    p.set_id(self._caption_id)

    if self._begin:
      p.set_begin(self._begin.to_temporal_offset())
    if self._end:
      p.set_end(self._end.to_temporal_offset())

    for caption_content in self.caption_contents:

      if isinstance(caption_content, SccCaptionLineBreak):
        p.push_child(Br(doc))
        continue

      if isinstance(caption_content, SccCaptionText):
        span = Span(doc)

        origin = caption_content.get_position()
        span.set_style(StyleProperties.Origin, origin)

        for (prop, value) in caption_content.style_properties.items():
          span.set_style(prop, value)

        span.push_child(Text(doc, caption_content.text))

        p.push_child(span)

    return p
