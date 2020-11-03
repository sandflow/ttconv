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

"""SCC caption paragraph"""

import copy
import logging
import math
from typing import Optional, List

from ttconv.model import Region, Document, P, Br, Span, Text
from ttconv.scc.content import SccCaptionText, SccCaptionContent, ROLL_UP_BASE_ROW, SccCaptionLineBreak
from ttconv.scc.style import SccCaptionStyle
from ttconv.scc.time_codes import SccTimeCode
from ttconv.scc.utils import get_position_from_offsets, get_extent_from_dimensions, convert_cells_to_percentages
from ttconv.style_properties import PositionType, ExtentType, StyleProperties, LengthType, DisplayAlignType

LOGGER = logging.getLogger(__name__)


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
    self._caption_style: SccCaptionStyle = caption_style
    self._style_properties = {}

  def set_id(self, caption_id: str):
    """Sets caption identifier"""
    self._caption_id = caption_id

  def get_id(self) -> str:
    """Returns the caption identifier"""
    return self._caption_id

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

  def get_safe_area_x_offset(self):
    """Returns the safe area x offset"""
    return self._safe_area_x_offset

  def get_safe_area_y_offset(self):
    """Returns the safe area y offset"""
    return self._safe_area_y_offset

  def get_caption_style(self) -> SccCaptionStyle:
    """Returns the caption style"""
    return self._caption_style

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

  def get_style_properties(self) -> dict:
    """Sets the style properties map"""
    return self._style_properties

  def add_style_property(self, style_property, value):
    """Adds a style property"""
    if value is None:
      return
    self._style_properties[style_property] = value

  def get_style_property(self, style_property) -> Optional:
    """Returns the style property value"""
    return self._style_properties.get(style_property)

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
    if self._caption_style is not SccCaptionStyle.RollUp:
      raise RuntimeError(f"Cannot set Roll-Up row offset for {self._caption_style}-styled caption.")

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

      return get_position_from_offsets(min(x_offsets), min(y_offsets))

    return get_position_from_offsets(self._safe_area_x_offset, self._safe_area_y_offset)

  def get_extent(self) -> ExtentType:
    """Computes and returns the current paragraph extent, based on its content"""
    lines: List[str] = []
    last_line = []
    separator = " " if self._caption_style is SccCaptionStyle.PaintOn else ""
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

    return get_extent_from_dimensions(max_text_lengths, nb_lines)

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

    # Set the region to current caption
    region = _SccParagraphRegion(self, doc)
    p.set_region(region.get_region())

    # Set the paragraph style
    for (prop, value) in self.get_style_properties().items():
      p.set_style(prop, value)

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


class _SccParagraphRegion:
  """SCC paragraph region utility class"""

  def __init__(self, paragraph: SccCaptionParagraph, doc: Document):
    self._paragraph = paragraph
    self._doc = doc

    cell_resolution = doc.get_cell_resolution()
    x_offset = self._paragraph.get_safe_area_x_offset()
    y_offset = self._paragraph.get_safe_area_y_offset()

    self._left = x_offset
    self._top = y_offset
    self._right = cell_resolution.columns - x_offset
    # Add 1 cell to bottom since the cursor height is 1
    self._bottom = cell_resolution.rows - y_offset + 1

  def get_region(self) -> Region:
    """Get a paragraph matching region"""

    matching_region = self._find_matching_region()

    if matching_region:
      # Extend region to paragraph if needed
      self._extend_region_to_paragraph(matching_region)
    else:
      # Create a new matching region
      matching_region = self._create_matching_region()

    return matching_region

  def _has_same_origin_as_region(self, region: Region) -> bool:
    """Checks whether the region origin is the same as the paragraph origin"""
    region_origin: Optional[PositionType] = region.get_style(StyleProperties.Origin)

    # Convert paragraph origin units into percentages
    paragraph_origin = convert_cells_to_percentages(self._paragraph.get_origin(), self._doc.get_cell_resolution())

    if self._paragraph.get_caption_style() in (SccCaptionStyle.RollUp, SccCaptionStyle.PaintOn):
      return region_origin \
             and region_origin.x.units is paragraph_origin.x.units \
             and region_origin.y.units is paragraph_origin.y.units \
             and math.isclose(region_origin.x.value, paragraph_origin.x.value, abs_tol=0.001) \
             and region_origin.y.value <= paragraph_origin.y.value

    return region_origin \
       and region_origin.x.units is paragraph_origin.x.units \
       and region_origin.y.units is paragraph_origin.y.units \
       and math.isclose(region_origin.x.value, paragraph_origin.x.value, abs_tol=0.001) \
       and math.isclose(region_origin.y.value, paragraph_origin.y.value, abs_tol=0.001)

  def _find_matching_region(self) -> Optional[Region]:
    """Looks for a region that origin matches with the paragraph origin"""
    for region in self._doc.iter_regions():
      if self._has_same_origin_as_region(region):
        return region
    return None

  def _extend_region_to_paragraph(self, region: Region):
    """Extends region dimensions based on paragraph extent"""
    if not self._has_same_origin_as_region(region):
      raise ValueError("Paragraph origin does not match with region.")

    region_extent = region.get_style(StyleProperties.Extent)

    paragraph_extent = self._paragraph.get_extent()

    # Convert extent cells to percentages
    paragraph_extent_pct = convert_cells_to_percentages(paragraph_extent, self._doc.get_cell_resolution())

    if paragraph_extent_pct.width.value > region_extent.width.value:
      # Resets the region width on the paragraph line width (up to the right of the safe area)
      # The region height always remains the same (depending on the region origin)
      region_origin: PositionType = region.get_style(StyleProperties.Origin)

      # Convert right cells coordinate to percentages
      right_pct = self._right * 100 / self._doc.get_cell_resolution().columns
      available_width_pct = right_pct - region_origin.x.value

      if int(paragraph_extent_pct.width.value) > available_width_pct:
        LOGGER.warning("The paragraph width overflows from the safe area (at %s)", self._paragraph.get_begin())

      max_width_pct = round(min(paragraph_extent_pct.width.value, available_width_pct))

      region_extent_pct = get_extent_from_dimensions(max_width_pct, region_extent.height.value, LengthType.Units.pct)
      region.set_style(StyleProperties.Extent, region_extent_pct)

  def _get_region_prefix(self):
    """Returns region prefix based on paragraph style"""
    if self._paragraph.get_caption_style() is SccCaptionStyle.PaintOn:
      return "paint"
    if self._paragraph.get_caption_style() is SccCaptionStyle.PopOn:
      return "pop"
    if self._paragraph.get_caption_style() is SccCaptionStyle.RollUp:
      return "rollup"
    return "region"

  def _create_matching_region(self) -> Region:
    """Creates a new region based on paragraph needs"""
    doc_regions = list(self._doc.iter_regions())

    paragraph_origin = self._paragraph.get_origin()
    region = Region(self._get_region_prefix() + str(len(doc_regions) + 1), self._doc)

    # Convert origin cells to percentages
    if self._paragraph.get_caption_style() is SccCaptionStyle.RollUp:
      # The region origin x offset
      region_origin = get_position_from_offsets(paragraph_origin.x.value, self._top)
      region_origin_pct = convert_cells_to_percentages(region_origin, self._doc.get_cell_resolution())
    else:
      # The region origin matches with paragraph origin
      region_origin_pct = convert_cells_to_percentages(paragraph_origin, self._doc.get_cell_resolution())

    region.set_style(StyleProperties.Origin, region_origin_pct)

    # The region width is initialized with he paragraph width (up to the right of the safe area)
    paragraph_extent = self._paragraph.get_extent()

    available_width = self._right - int(paragraph_origin.x.value)
    region_width = min(paragraph_extent.width.value, available_width)

    if self._paragraph.get_caption_style() is SccCaptionStyle.RollUp:
      # The region height extends from the top row to the bottom row of the safe area
      region_height = self._bottom - (self._top + 1)
      region.set_style(StyleProperties.DisplayAlign, DisplayAlignType.after)
    else:
      # The region height extends from its origin to the bottom of the safe area
      region_height = self._bottom - int(paragraph_origin.y.value)
      region.set_style(StyleProperties.DisplayAlign, DisplayAlignType.before)

    region_extent = get_extent_from_dimensions(region_width, region_height)

    # Convert extent cells to percentages
    region_extent_pct = convert_cells_to_percentages(region_extent, self._doc.get_cell_resolution())
    region.set_style(StyleProperties.Extent, region_extent_pct)

    self._doc.put_region(region)

    return region
