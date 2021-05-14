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
from math import ceil
from typing import Optional, List, Dict, Union

from ttconv.model import Region, ContentDocument, P, Br, Span, Text
from ttconv.scc.content import SccCaptionText, SccCaptionLine
from ttconv.scc.style import SccCaptionStyle
from ttconv.scc.utils import get_position_from_offsets, get_extent_from_dimensions, convert_cells_to_percentages
from ttconv.style_properties import CoordinateType, ExtentType, StyleProperties, LengthType, DisplayAlignType, ShowBackgroundType, \
  TextAlignType, NamedColors
from ttconv.time_code import SmpteTimeCode

LOGGER = logging.getLogger(__name__)

SCC_SAFE_AREA_CELL_RESOLUTION_ROWS = 15
SCC_SAFE_AREA_CELL_RESOLUTION_COLUMNS = 32

SCC_ROOT_CELL_RESOLUTION_ROWS = ceil(SCC_SAFE_AREA_CELL_RESOLUTION_ROWS / 0.80)
SCC_ROOT_CELL_RESOLUTION_COLUMNS = ceil(SCC_SAFE_AREA_CELL_RESOLUTION_COLUMNS / 0.80)


class SccCaptionParagraph:
  """Caption paragraph"""

  def __init__(self, safe_area_x_offset: int = 0, safe_area_y_offset: int = 0,
               caption_style: SccCaptionStyle = SccCaptionStyle.Unknown):
    self._caption_id: str = ""
    self._begin: Optional[SmpteTimeCode] = None
    self._end: Optional[SmpteTimeCode] = None
    self._safe_area_x_offset = safe_area_x_offset
    self._safe_area_y_offset = safe_area_y_offset

    # Paragraph offsets (= origin) in the root area
    self._column_offset: int = safe_area_x_offset
    self._row_offset: int = safe_area_y_offset

    # Position of the cursor in the active area
    self._cursor: (int, int) = (0, 0)
    # Line where the cursor is currently positioned
    self._current_line: Optional[SccCaptionLine] = None
    # Lines per row in the active area (will be separated by line-breaks)
    self._caption_lines: Dict[int, SccCaptionLine] = {}

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

  def get_begin(self) -> SmpteTimeCode:
    """Returns the caption begin time code"""
    return self._begin

  def set_end(self, time_code):
    """Sets caption end time code"""
    self._end = copy.copy(time_code)

  def get_end(self) -> SmpteTimeCode:
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

  def get_current_line(self) -> Optional[SccCaptionLine]:
    """Returns the current caption line"""
    return self._current_line

  def get_current_text(self) -> Optional[SccCaptionText]:
    """Returns the current caption text"""
    if self._current_line is None:
      return None
    return self._current_line.get_current_text()

  def append_text(self, text: str):
    """Append text to current line text content"""
    self.get_current_line().add_text(text)
    self.indent_cursor(len(text))

  def set_lines(self, lines: Union[List[SccCaptionLine], Dict[int, SccCaptionLine]]):
    """Sets paragraph lines"""
    if isinstance(lines, dict):
      self._caption_lines = lines
      return

    for line in lines:
      self._caption_lines[line.get_row()] = line

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

  def set_cursor_at(self, row: int, indent: Optional[int] = None):
    """Set cursor position and initialize a new line if necessary"""

    # Remove current line if empty (useless)
    if self._current_line is not None and self._current_line.is_empty():
      del self._caption_lines[self._current_line.get_row()]

    self._cursor = (row, indent if indent is not None else 0)

    if self._caption_lines.get(row) is None:
      self.new_caption_line()

    self._current_line = self._caption_lines.get(row)

    if indent is not None:
      self._current_line.set_cursor(self._cursor[1] - self._current_line.get_indent())

  def get_cursor(self) -> (int, int):
    """Returns cursor coordinates"""
    return self._cursor

  def indent_cursor(self, indent: int):
    """Set cursor position of the current row"""
    self._cursor = (self._cursor[0], self._cursor[1] + indent)

    if self._current_line.is_empty():
      # If the current line is empty, set cursor indent as a line tabulation
      self._current_line.indent(indent)
    else:
      self._current_line.set_cursor(self._cursor[1] - self._current_line.get_indent())

  def get_lines(self) -> Dict[int, SccCaptionLine]:
    """Returns the paragraph lines per row"""
    return self._caption_lines

  def copy_lines(self) -> Dict[int, SccCaptionLine]:
    """Copy paragraph lines (without time attributes)"""
    lines_copy = {}
    for row, orig_line in self._caption_lines.items():
      new_line = SccCaptionLine(orig_line.get_row(), orig_line.get_indent())

      for orig_text in orig_line.get_texts():
        new_text = SccCaptionText(orig_text.get_text())
        for style_type, style_value in orig_text.get_style_properties().items():
          new_text.add_style_property(style_type, style_value)
        new_line.add_text(new_text)
      lines_copy[row] = new_line

    return lines_copy

  def new_caption_text(self):
    """Appends a new caption text content, and keeps reference on it"""
    if self._current_line is None:
      LOGGER.warning("Add a new caption line to add new caption text")
      self.new_caption_line()

    self._current_line.add_text(SccCaptionText())

  def new_caption_line(self):
    """Appends a new caption text content, and keeps reference on it"""
    self._caption_lines[self._cursor[0]] = SccCaptionLine(self._cursor[0], self._cursor[1])
    self._current_line = self._caption_lines[self._cursor[0]]

  def roll_up(self):
    """Set specified lines on a roll-up configuration"""
    if self._caption_style is not SccCaptionStyle.RollUp:
      raise RuntimeError(f"Cannot roll-Up {self._caption_style.name}-styled caption.")

    rows_to_roll_up = list(sorted(self._caption_lines.keys()))

    # Roll each line one row up
    for row in rows_to_roll_up:
      line = self._caption_lines.pop(row)
      if row == 0:
        continue
      line.set_row(row - 1)
      self._caption_lines[line.get_row()] = line

  def get_origin(self) -> CoordinateType:
    """Computes and returns the current paragraph origin, based on its content"""
    if len(self._caption_lines) > 0:
      x_offsets = [text.get_indent() for text in self._caption_lines.values()]
      y_offsets = [text.get_row() - 1 for text in self._caption_lines.values()]

      return get_position_from_offsets(min(x_offsets) + self._safe_area_x_offset, min(y_offsets) + self._safe_area_y_offset)

    return get_position_from_offsets(self._safe_area_x_offset, self._safe_area_y_offset)

  def get_extent(self) -> ExtentType:
    """Computes and returns the current paragraph extent, based on its content"""
    if len(self._caption_lines) == 0:
      return get_extent_from_dimensions(0, 0)

    paragraph_rows = self._caption_lines.keys()
    nb_lines = max(paragraph_rows) - min(paragraph_rows) + 1
    max_text_lengths = max([line.get_length() for line in self._caption_lines.values()])

    return get_extent_from_dimensions(max_text_lengths, nb_lines)

  def get_last_caption_lines(self, expected_lines: int) -> List[SccCaptionLine]:
    """Returns the caption text elements from the expected number of last lines"""
    if expected_lines <= 0:
      return []

    sorted_lines = list(dict(sorted(self._caption_lines.items())).values())
    return sorted_lines[-expected_lines:]

  def guess_text_alignment(self) -> TextAlignType:
    """Tries to detect the text alignment according to the content indentation"""

    def get_line_right_offset(line: SccCaptionLine) -> int:
      return SCC_ROOT_CELL_RESOLUTION_COLUMNS - (line.get_indent() + line.get_length())

    # look for longest line
    longest_line = max(self._caption_lines.values(), key=lambda line: line.get_length())

    # define borders based on the longest line
    left_border = longest_line.get_indent() + longest_line.get_leading_spaces()
    right_border = get_line_right_offset(longest_line) + longest_line.get_trailing_spaces()

    # is the text left-aligned?
    if all(l.get_indent() + l.get_leading_spaces() - left_border == 0 for l in self._caption_lines.values()):
      return TextAlignType.start

    # is the text right-aligned?
    if all(get_line_right_offset(l) + l.get_trailing_spaces() - right_border == 0 for l in self._caption_lines.values()):
      return TextAlignType.end

    # is the text centered?
    if all(abs(l.get_indent() + l.get_leading_spaces() - left_border - (
        get_line_right_offset(l) + l.get_trailing_spaces() - right_border)) < 2 for l in self._caption_lines.values()):
      return TextAlignType.center

    # default is left-aligned
    LOGGER.warning("Cannot define the paragraph text alignment. Set it to default left-aligned.")
    return TextAlignType.start

  def to_paragraph(self, doc: ContentDocument) -> P:
    """Converts and returns current caption paragraph into P instance"""

    # Set up a new paragraph
    p = P()
    p.set_doc(doc)
    p.set_id(self._caption_id)

    if self._begin is not None:
      p.set_begin(self._begin.to_temporal_offset())
    if self._end is not None:
      p.set_end(self._end.to_temporal_offset())

    # Set the region to current caption
    region = _SccParagraphRegion(self, doc)
    p.set_region(region.get_region())

    # Set the paragraph style
    for (prop, value) in self.get_style_properties().items():
      p.set_style(prop, value)

    # Add caption content (text and line-breaks)
    last_row: Optional[int] = None
    for row, caption_line in sorted(self._caption_lines.items()):

      if last_row is not None:
        for _ in range(0, abs(last_row - row)):
          p.push_child(Br(doc))

      last_row = row

      for caption_text in caption_line.get_texts():

        # Skip empty texts
        if caption_text.is_empty():
          continue

        span = Span(doc)

        if caption_text.get_begin() is not None:

          begin = caption_text.get_begin().to_temporal_offset()

          if self.get_caption_style() is SccCaptionStyle.PaintOn:
            # Compute paragraph-relative begin time
            begin -= self._begin.to_temporal_offset()

          span.set_begin(begin)

        if caption_text.get_end() is not None:

          end = caption_text.get_end().to_temporal_offset()

          if self.get_caption_style() is SccCaptionStyle.PaintOn:
            # Compute paragraph-relative end time
            end -= self._end.to_temporal_offset()

          span.set_end(end)

        for (prop, value) in caption_text.get_style_properties().items():
          span.set_style(prop, value)

        if StyleProperties.BackgroundColor not in caption_text.get_style_properties():
          span.set_style(StyleProperties.BackgroundColor, NamedColors.black.value)

        span.push_child(Text(doc, caption_text.get_text()))

        p.push_child(span)

    return p

  def __repr__(self) -> str:
    return "<" + self.__class__.__name__ + " " + str(self.__dict__) + ">"


class _SccParagraphRegion:
  """SCC paragraph region utility class"""

  def __init__(self, paragraph: SccCaptionParagraph, doc: ContentDocument):
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

    if matching_region is None:
      # Create a new matching region
      matching_region = self._create_matching_region()
    else:
      # Extend region to paragraph if needed
      self._extend_region_to_paragraph(matching_region)

    return matching_region

  def _has_same_origin_as_region(self, region: Region) -> bool:
    """Checks whether the region origin is the same as the paragraph origin"""
    region_origin: Optional[CoordinateType] = region.get_style(StyleProperties.Origin)

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
      if self._has_same_origin_as_region(region) and region.get_id().startswith(self._get_region_prefix()):
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
      region_origin: CoordinateType = region.get_style(StyleProperties.Origin)

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
      region_height = self._bottom - int(paragraph_origin.y.value) - 1
      region.set_style(StyleProperties.DisplayAlign, DisplayAlignType.before)

    region_extent = get_extent_from_dimensions(region_width, region_height)

    # Convert extent cells to percentages
    region_extent_pct = convert_cells_to_percentages(region_extent, self._doc.get_cell_resolution())
    region.set_style(StyleProperties.Extent, region_extent_pct)

    # Set default region style properties
    region.set_style(StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    self._doc.put_region(region)

    return region
