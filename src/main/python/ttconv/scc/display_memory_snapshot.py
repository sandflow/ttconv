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


"""Converts SccDisplayMemory into a P element of the data model"""

import logging
import math
from fractions import Fraction
from math import ceil
from typing import List, Optional, Tuple

from ttconv.model import Region, ContentDocument, P, Br, Span, Text
from ttconv.scc.caption_style import SccCaptionStyle
from ttconv.scc.config import TextAlignment
from ttconv.scc.display_memory import SccDisplayMemory, SccPen
from ttconv.scc.utils import get_position_from_offsets, get_extent_from_dimensions, convert_cells_to_percentages
from ttconv.style_properties import CoordinateType, ExtentType, StyleProperties, LengthType, DisplayAlignType, ShowBackgroundType, \
  TextAlignType, NamedColors

LOGGER = logging.getLogger(__name__)

SCC_SAFE_AREA_CELL_RESOLUTION_ROWS = 15
SCC_SAFE_AREA_CELL_RESOLUTION_COLUMNS = 32

SCC_ROOT_CELL_RESOLUTION_ROWS = ceil(SCC_SAFE_AREA_CELL_RESOLUTION_ROWS / 0.80)
SCC_ROOT_CELL_RESOLUTION_COLUMNS = ceil(SCC_SAFE_AREA_CELL_RESOLUTION_COLUMNS / 0.80)


class SccDisplayMemorySnapshot:
  """A copy of the displayed memory during an interval of time, i.e. a
  caption"""

  def __init__(self, memory: SccDisplayMemory, caption_style: SccCaptionStyle,
               begin: Optional[Fraction], end: Optional[Fraction], *,
               safe_area_x_offset: int = 0, safe_area_y_offset: int = 0,
               text_alignment: TextAlignment = TextAlignment.AUTO):
    self._memory = memory
    self._caption_style = caption_style
    self._begin = begin
    self._end = end
    self._safe_area_x_offset = safe_area_x_offset
    self._safe_area_y_offset = safe_area_y_offset
    self._text_alignment = text_alignment

  def is_empty(self) -> bool:
    """Returns whether the caption has no content"""
    return self._memory.is_empty()

  def _row_length(self, row: int) -> int:
    """Returns the number of cells of a row, from its first to its last
    character"""
    return self._memory.get_last_column(row) - self._memory.get_first_column(row) + 1

  def get_origin(self) -> CoordinateType:
    """Returns the origin of the caption in the root area, in cells"""
    if self.is_empty():
      return get_position_from_offsets(self._safe_area_x_offset, self._safe_area_y_offset)

    rows = self._memory.get_rows()
    x_offset = min(self._memory.get_first_column(row) for row in rows)
    y_offset = rows[0] - 1

    return get_position_from_offsets(x_offset + self._safe_area_x_offset, y_offset + self._safe_area_y_offset)

  def get_extent(self) -> ExtentType:
    """Returns the extent of the caption, in cells"""
    if self.is_empty():
      return get_extent_from_dimensions(0, 0)

    rows = self._memory.get_rows()
    width = max(self._row_length(row) for row in rows)

    return get_extent_from_dimensions(width, rows[-1] - rows[0] + 1)

  def _guess_text_alignment(self) -> TextAlignType:
    """Tries to detect the text alignment according to the content
    indentation"""

    if self.is_empty():
      return TextAlignType.start

    memory = self._memory
    rows = memory.get_rows()

    def get_visible_columns(row: int) -> Tuple[int, int]:
      """Returns the first column and the column after the last one of the
      visible characters of a row: leading and trailing spaces count as
      margins"""
      first_column = memory.get_first_column(row)
      cells = memory.get_row_cells(row)
      visible = [first_column + i for (i, cell) in enumerate(cells) if cell is not None and cell.char != " "]

      if len(visible) == 0:
        # a row of spaces is all margin: the left one ends after its last space, the right one starts at its first
        return (first_column + len(cells), first_column)

      return (visible[0], visible[-1] + 1)

    def get_left_offset(row: int) -> int:
      return get_visible_columns(row)[0]

    def get_right_offset(row: int) -> int:
      return SCC_ROOT_CELL_RESOLUTION_COLUMNS - get_visible_columns(row)[1]

    # define borders based on the longest row
    longest_row = max(rows, key=self._row_length)
    left_border = get_left_offset(longest_row)
    right_border = get_right_offset(longest_row)

    # is the text left-aligned?
    if all(get_left_offset(row) == left_border for row in rows):
      return TextAlignType.start

    # is the text right-aligned?
    if all(get_right_offset(row) == right_border for row in rows):
      return TextAlignType.end

    # is the text centered?
    if all(abs(get_left_offset(row) - left_border - (get_right_offset(row) - right_border)) < 2 for row in rows):
      return TextAlignType.center

    # default is left-aligned
    LOGGER.warning("Cannot define the paragraph text alignment. Set it to default left-aligned.")
    return TextAlignType.start

  def to_paragraph(self, doc: ContentDocument, caption_id: str) -> P:
    """Converts the caption into a paragraph of the data model"""

    p = P()
    p.set_doc(doc)
    p.set_id(caption_id)

    if self._begin is not None:
      p.set_begin(self._begin)
    if self._end is not None:
      p.set_end(self._end)

    p.set_region(self._get_region(doc))

    if self._caption_style is SccCaptionStyle.PopOn:
      if self._text_alignment is TextAlignment.AUTO:
        p.set_style(StyleProperties.TextAlign, self._guess_text_alignment())
      else:
        p.set_style(StyleProperties.TextAlign, self._text_alignment.text_align)

    last_row: Optional[int] = None
    for row in self._memory.get_rows():
      if last_row is not None:
        for _ in range(row - last_row):
          p.push_child(Br(doc))
      last_row = row

      for span in self._row_to_spans(doc, row):
        p.push_child(span)

    return p

  def _row_to_spans(self, doc: ContentDocument, row: int) -> List[Span]:
    """Converts a row into spans. A span groups characters that have the same
    attributes. Characters that appear after the begin of the caption start a
    new span at the beginning of each word, and the span begins when its first
    character was written."""

    spans: List[Span] = []

    text = ""
    pen: Optional[SccPen] = None
    appearance: Optional[Fraction] = None
    previous_char: Optional[str] = None

    def flush():
      if text != "":
        spans.append(self._new_span(doc, text, pen, appearance))

    for cell in self._memory.get_row_cells(row):
      if cell is None:
        # gap
        cell_pen = None
        cell_appearance = appearance
        char = " "
      else:
        cell_pen = cell.pen
        cell_appearance = cell.time if self._begin is None or cell.time > self._begin else self._begin
        char = cell.char

      starts_word = char != " " and (previous_char is None or previous_char == " ")

      if text == "" or cell_pen != pen or (cell is not None and cell_appearance != appearance and starts_word):
        flush()
        text = ""
        pen = cell_pen
        appearance = cell_appearance

      text += char
      previous_char = char

    flush()

    return spans

  def _new_span(self, doc: ContentDocument, text: str, pen: Optional[SccPen], appearance: Optional[Fraction]) -> Span:
    span = Span(doc)

    if pen is None:
      # gap between characters of the same row
      span.set_style(StyleProperties.BackgroundColor, NamedColors.transparent.value)
    else:
      if pen.color is not None:
        span.set_style(StyleProperties.Color, pen.color)
      if pen.font_style is not None:
        span.set_style(StyleProperties.FontStyle, pen.font_style)
      if pen.text_decoration is not None:
        span.set_style(StyleProperties.TextDecoration, pen.text_decoration)
      span.set_style(StyleProperties.BackgroundColor,
                     pen.background if pen.background is not None else NamedColors.black.value)

    if self._begin is not None and appearance is not None and appearance > self._begin:
      span.set_begin(appearance - self._begin)

    span.push_child(Text(doc, text))

    return span

  def _get_region(self, doc: ContentDocument) -> Region:
    """Returns a region of the document that matches the caption, which is
    created or extended if needed"""

    matching_region = self._find_matching_region(doc)

    if matching_region is None:
      # Create a new matching region
      matching_region = self._create_matching_region(doc)
    else:
      # Extend region to paragraph if needed
      self._extend_region_to_paragraph(matching_region, doc)

    return matching_region

  def _has_same_origin_as_region(self, region: Region, doc: ContentDocument) -> bool:
    """Checks whether the region origin is the same as the paragraph origin"""
    region_origin: Optional[CoordinateType] = region.get_style(StyleProperties.Origin)

    # Convert paragraph origin units into percentages
    paragraph_origin = convert_cells_to_percentages(self.get_origin(), doc.get_cell_resolution())

    if self._caption_style in (SccCaptionStyle.RollUp, SccCaptionStyle.PaintOn):
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

  def _find_matching_region(self, doc: ContentDocument) -> Optional[Region]:
    """Looks for a region that origin matches with the paragraph origin"""
    for region in doc.iter_regions():
      if self._has_same_origin_as_region(region, doc) and region.get_id().startswith(self._get_region_prefix()):
        return region
    return None

  def _extend_region_to_paragraph(self, region: Region, doc: ContentDocument):
    """Extends region dimensions based on paragraph extent"""
    if not self._has_same_origin_as_region(region, doc):
      raise ValueError("Paragraph origin does not match with region.")

    region_extent = region.get_style(StyleProperties.Extent)

    paragraph_extent = self.get_extent()

    # Convert extent cells to percentages
    paragraph_extent_pct = convert_cells_to_percentages(paragraph_extent, doc.get_cell_resolution())

    if paragraph_extent_pct.width.value > region_extent.width.value:
      # Resets the region width on the paragraph line width (up to the right of the safe area)
      # The region height always remains the same (depending on the region origin)
      region_origin: CoordinateType = region.get_style(StyleProperties.Origin)

      # Convert right cells coordinate to percentages
      right = doc.get_cell_resolution().columns - self._safe_area_x_offset
      right_pct = right * 100 / doc.get_cell_resolution().columns
      available_width_pct = right_pct - region_origin.x.value

      if int(paragraph_extent_pct.width.value) > available_width_pct:
        LOGGER.warning("The paragraph width overflows from the safe area (at %s)", self._begin)

      max_width_pct = round(min(paragraph_extent_pct.width.value, available_width_pct))

      region_extent_pct = get_extent_from_dimensions(max_width_pct, region_extent.height.value, LengthType.Units.pct)
      region.set_style(StyleProperties.Extent, region_extent_pct)

  def _get_region_prefix(self):
    """Returns region prefix based on paragraph style"""
    if self._caption_style is SccCaptionStyle.PaintOn:
      return "paint"
    if self._caption_style is SccCaptionStyle.RollUp:
      return "rollup"
    return "pop"

  def _create_matching_region(self, doc: ContentDocument) -> Region:
    """Creates a new region based on paragraph needs"""
    doc_regions = list(doc.iter_regions())

    paragraph_origin = self.get_origin()
    region = Region(self._get_region_prefix() + str(len(doc_regions) + 1), doc)

    # Convert origin cells to percentages
    if self._caption_style is SccCaptionStyle.RollUp:
      # The region origin x offset
      region_origin = get_position_from_offsets(paragraph_origin.x.value, self._safe_area_y_offset)
      region_origin_pct = convert_cells_to_percentages(region_origin, doc.get_cell_resolution())
    else:
      # The region origin matches with paragraph origin
      region_origin_pct = convert_cells_to_percentages(paragraph_origin, doc.get_cell_resolution())

    region.set_style(StyleProperties.Origin, region_origin_pct)

    # The region width is initialized with he paragraph width (up to the right of the safe area)
    paragraph_extent = self.get_extent()

    right = doc.get_cell_resolution().columns - self._safe_area_x_offset
    # Add 1 cell to bottom since the cursor height is 1
    bottom = doc.get_cell_resolution().rows - self._safe_area_y_offset + 1

    available_width = right - int(paragraph_origin.x.value)
    region_width = min(paragraph_extent.width.value, available_width)

    if self._caption_style is SccCaptionStyle.RollUp:
      # The region height extends from the top row to the bottom row of the safe area
      region_height = bottom - (self._safe_area_y_offset + 1)
      region.set_style(StyleProperties.DisplayAlign, DisplayAlignType.after)
    else:
      # The region height extends from its origin to the bottom of the safe area
      region_height = bottom - int(paragraph_origin.y.value) - 1
      region.set_style(StyleProperties.DisplayAlign, DisplayAlignType.before)

    region_extent = get_extent_from_dimensions(region_width, region_height)

    # Convert extent cells to percentages
    region_extent_pct = convert_cells_to_percentages(region_extent, doc.get_cell_resolution())
    region.set_style(StyleProperties.Extent, region_extent_pct)

    # Set default region style properties
    region.set_style(StyleProperties.ShowBackground, ShowBackgroundType.whenActive)

    doc.put_region(region)

    return region
