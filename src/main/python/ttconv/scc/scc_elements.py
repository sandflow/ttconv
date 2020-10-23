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
from enum import Enum
from typing import List, Optional

from ttconv.model import Document, P, Span, Br, Text, Region
from ttconv.scc.time_codes import SccTimeCode
from ttconv.style_properties import PositionType, LengthType, StyleProperties, ExtentType

ROLL_UP_BASE_ROW = 15


def _get_position_from_offsets(x_offset, y_offset, units=LengthType.Units.c) -> PositionType:
  """Converts offsets into position"""
  x_position = LengthType(value=x_offset, units=units)
  y_position = LengthType(value=y_offset, units=units)

  return PositionType(x_position, y_position)


def _get_extent_from_dimensions(width, height, units=LengthType.Units.c) -> ExtentType:
  """Converts dimensions into extent"""
  height = LengthType(value=height, units=units)
  width = LengthType(value=width, units=units)

  return ExtentType(height, width)


class SccCaptionStyle(Enum):
  """SCC caption style"""
  Unknown = 0

  # SCC Roll-Up captions are composed with:
  #  - RU2 or RU3 or RU4 (to select the Roll-Up style and the number of displayed rows)
  #  - CR (to roll the displayed rows up)
  #  - PAC (to set row, indent and/or attributes)
  #  - text
  RollUp = 1

  # SCC Paint-On captions are composed with:
  #  - RDC (to select the Paint-On style)
  #  - PAC (to set row, indent and/or attributes)
  #  - text
  #  - PAC (to change row, indent and/or attributes)
  #  - text or DER (to erase the following text of the current row)
  PaintOn = 2

  # SCC Pop-On captions are composed with:
  #  - RCL (to select the Pop-On style)
  #  - ENM (to clear the memory, optional)
  #  - PAC (to set row, indent and/or attributes)
  #  - text
  #  - PAC (to change row, indent and/or attributes)
  #  - text
  #  etc.
  #  - EDM (to erase the displayed caption, optional)
  #  - EOC (to display the current caption)
  PopOn = 3


class SccCaptionContent:
  """Caption content base class"""


class SccCaptionLineBreak(SccCaptionContent):
  """Caption line break element"""

  def __repr__(self):
    return "<" + self.__class__.__name__ + ">"


class SccCaptionText(SccCaptionContent):
  """Caption text content"""

  def __init__(self):
    self._begin: Optional[SccTimeCode] = None
    self._end: Optional[SccTimeCode] = None
    self._style_properties = {}
    self._text: str = ""
    self._x_offset: int = 0
    self._y_offset: int = 0

  def set_begin(self, time_code: SccTimeCode):
    """Sets begin time code"""
    self._begin = copy.copy(time_code)

  def get_begin(self) -> SccTimeCode:
    """Returns the begin time code"""
    return self._begin

  def set_end(self, time_code: SccTimeCode):
    """Sets end time code"""
    self._end = copy.copy(time_code)

  def get_end(self) -> SccTimeCode:
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
    self._x_offset = indent if indent else 0

  def get_x_offset(self) -> int:
    """Returns the x offset"""
    return self._x_offset

  def set_y_offset(self, row: Optional[int]):
    """Sets the y offset"""
    self._y_offset = row if row else 0

  def get_y_offset(self) -> int:
    """Returns the y offset"""
    return self._y_offset

  def get_position(self) -> PositionType:
    """Returns current row and column offsets as a cell-based PositionType"""
    return _get_position_from_offsets(self._x_offset, self._y_offset)

  def get_style_properties(self) -> dict:
    """Sets the style properties map"""
    return self._style_properties

  def add_style_property(self, style_property, value):
    """Adds a style property"""
    if value is None:
      return
    self._style_properties[style_property] = value

  def is_contiguous(self, other: SccCaptionText) -> bool:
    """Returns whether the current text is contiguous according to the other text"""
    return self._x_offset == other.get_x_offset() and self._y_offset == other.get_y_offset() + 1

  def has_same_style_properties(self, other):
    """Returns whether the current text has the same style properties as the other text"""
    return self._style_properties == other.get_style_properties()

  def has_same_origin(self, other: SccCaptionText) -> bool:
    """Returns whether the current text has the same origin as the other text"""
    return self._x_offset == other.get_x_offset() and self._y_offset == other.get_y_offset()

  def __repr__(self):
    return "<" + self.__class__.__name__ + " " + str(self.__dict__) + ">"


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
    self._current_text: Optional[SccCaptionText] = None
    self._caption_contents: List[SccCaptionContent] = []
    self._style: SccCaptionStyle = caption_style

  def set_id(self, caption_id: str):
    """Sets caption identifier"""
    self._caption_id = caption_id

  def set_begin(self, time_code):
    """Sets caption begin time code"""
    self._begin = copy.copy(time_code)

  def get_begin(self) -> SccTimeCode:
    """Returns the caption begin time code"""
    return self._begin

  def set_end(self, time_code):
    """Sets caption end time code"""
    self._end = copy.copy(time_code)

  def get_end(self) -> SccTimeCode:
    """Returns the caption end time code"""
    return self._end

  def get_style(self) -> SccCaptionStyle:
    """Returns the caption style"""
    return self._style

  def set_column_offset(self, indent: Optional[int]):
    """Sets the paragraph x offset"""
    self._column_offset = self._safe_area_x_offset + (indent if indent else 0)

  def get_column_offset(self) -> int:
    """Returns the paragraph x offset"""
    return self._column_offset

  def set_row_offset(self, row: Optional[int]):
    """Sets the paragraph y offset"""
    self._row_offset = self._safe_area_y_offset + (row if row else 0)

  def get_row_offset(self) -> int:
    """Returns the paragraph y offset"""
    return self._row_offset

  def get_current_text(self) -> Optional[SccCaptionText]:
    """Returns the current caption text"""
    return self._current_text

  def set_contents(self, contents: List[SccCaptionContent]):
    """Sets paragraph contents"""
    self._caption_contents = contents

  def insert_content(self, index: int, content: SccCaptionContent):
    """Inserts content to paragraph contents at specified index"""
    self._caption_contents.insert(index, content)

  def get_contents(self) -> List[SccCaptionContent]:
    """Returns the paragraph contents"""
    return self._caption_contents

  def new_caption_text(self):
    """Appends a new caption text content, and keeps reference on it"""
    self._caption_contents.append(SccCaptionText())
    self._current_text = self._caption_contents[-1]

  def apply_current_text_offsets(self):
    """Applies the x and y offsets of the current text"""
    self._current_text.set_x_offset(self._column_offset)
    self._current_text.set_y_offset(self._row_offset)

  def indent(self, indent: int):
    """Indents the current text (x offset)"""
    self._column_offset += indent
    self._current_text.set_x_offset(self._column_offset)

  def apply_roll_up_row_offsets(self):
    """Applies the row offset in relation to the base row 15 for Roll-Up captions"""
    if self._style is not SccCaptionStyle.RollUp:
      raise RuntimeError(f"Cannot set Roll-Up row offset for {self._style}-styled caption.")

    line_count = 0
    for caption_content in reversed(self._caption_contents):
      if not isinstance(caption_content, SccCaptionText):
        line_count += 1
        continue
      caption_content.set_y_offset(self._safe_area_y_offset + ROLL_UP_BASE_ROW - line_count)

    self.set_row_offset(ROLL_UP_BASE_ROW)

  def get_origin(self) -> PositionType:
    """Computes and returns the current paragraph origin, based on its content"""
    if len(self._caption_contents) > 0:
      x_offsets = [text.get_x_offset() for text in self._caption_contents if isinstance(text, SccCaptionText)]
      y_offsets = [text.get_y_offset() for text in self._caption_contents if isinstance(text, SccCaptionText)]

      return _get_position_from_offsets(min(x_offsets), min(y_offsets))

    return _get_position_from_offsets(self._safe_area_x_offset, self._safe_area_y_offset)

  def get_extent(self) -> ExtentType:
    """Computes and returns the current paragraph extent, based on its content"""
    lines: List[str] = []
    last_line = []
    separator = " " if self._style is SccCaptionStyle.PaintOn else ""
    for caption_content in self._caption_contents:
      if isinstance(caption_content, SccCaptionLineBreak):
        lines.append(separator.join(last_line))
        last_line = []
        continue

      if isinstance(caption_content, SccCaptionText):
        last_line.append(caption_content.get_text())

    if len(last_line) > 0:
      lines.append(separator.join(last_line))

    nb_lines = len(lines)
    max_text_lengths = max([len(line) for line in lines]) if len(lines) > 0 else 0

    return _get_extent_from_dimensions(max_text_lengths, nb_lines)

  def get_last_caption_lines(self, expected_lines: int) -> List[SccCaptionContent]:
    """Returns the caption text elements from the expected number of last lines"""
    last_lines = []
    added_lines = 0
    for caption in reversed(self._caption_contents):
      if isinstance(caption, SccCaptionLineBreak):
        added_lines += 1

      if added_lines == expected_lines:
        return last_lines

      last_lines.insert(0, caption)

    return last_lines

  def has_same_origin_as_region(self, region: Region) -> bool:
    """Checks whether the region origin is the same as the current paragraph origin"""
    region_origin: Optional[PositionType] = region.get_style(StyleProperties.Origin)
    # Consider region origin units are cells
    return region_origin \
           and region_origin.x.value is self.get_origin().x.value \
           and region_origin.y.value is self.get_origin().y.value

  def find_matching_region(self, doc: Document) -> Optional[Region]:
    """Looks for a region that origin matches with the current paragraph origin"""
    for region in doc.iter_regions():
      if self.has_same_origin_as_region(region):
        return region
    return None

  def extend_region_to_paragraph(self, region: Region):
    """Extends region dimensions based on current paragraph extent"""
    if not self.has_same_origin_as_region(region):
      raise ValueError("Paragraph origin does not match with region.")

    region_extent = region.get_style(StyleProperties.Extent)

    max_width = max(self.get_extent().width.value, region_extent.width.value)
    max_height = max(self.get_extent().height.value, region_extent.height.value)

    new_extent = _get_extent_from_dimensions(max_width, max_height)

    region.set_style(StyleProperties.Extent, new_extent)

  def get_region_prefix(self):
    """Returns region prefix based on current paragraph style"""
    if self._style is SccCaptionStyle.PaintOn:
      return "paint"
    if self._style is SccCaptionStyle.PopOn:
      return "pop"
    if self._style is SccCaptionStyle.RollUp:
      return "rollup"
    return "region"

  def create_matching_region(self, doc: Document) -> Region:
    """Creates a new region based on current paragraph needs"""
    doc_regions = list(doc.iter_regions())

    region = Region(self.get_region_prefix() + str(len(doc_regions) + 1), doc)
    region.set_style(StyleProperties.Origin, self.get_origin())
    region.set_style(StyleProperties.Extent, self.get_extent())

    doc.put_region(region)

    return region

  def to_paragraph(self, doc: Document) -> P:
    """Converts and returns current caption paragraph into P instance"""

    # Set up a new paragraph
    p = P()
    p.set_doc(doc)
    p.set_id(self._caption_id)

    if self._begin:
      p.set_begin(self._begin.to_temporal_offset())
    if self._end:
      p.set_end(self._end.to_temporal_offset())

    # Set a matching region
    matching_region = self.find_matching_region(doc)

    if matching_region:
      # Extend region to paragraph if needed
      self.extend_region_to_paragraph(matching_region)
    else:
      # Create a new matching region
      matching_region = self.create_matching_region(doc)

    # Set the region to current caption
    p.set_region(matching_region)

    # Add caption content (text and line-breaks)
    for caption_content in self._caption_contents:

      if isinstance(caption_content, SccCaptionLineBreak):
        p.push_child(Br(doc))
        continue

      if isinstance(caption_content, SccCaptionText):
        span = Span(doc)

        if caption_content.get_begin():
          span.set_begin(caption_content.get_begin().to_temporal_offset())

        if caption_content.get_end():
          span.set_end(caption_content.get_end().to_temporal_offset())

        for (prop, value) in caption_content.get_style_properties().items():
          span.set_style(prop, value)

        span.push_child(Text(doc, caption_content.get_text()))

        p.push_child(span)

    return p

  def __repr__(self) -> str:
    return "<" + self.__class__.__name__ + " " + str(self.__dict__) + ">"
