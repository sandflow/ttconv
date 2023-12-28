#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2023, Sandflow Consulting LLC
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

"""Defines the Least common denominator (LCD) filter."""

from __future__ import annotations
import logging
import typing
from dataclasses import dataclass, field
from numbers import Number

from ttconv.config import ModuleConfiguration
from ttconv.filters.document_filter import DocumentFilter
from ttconv.filters.remove_animations import RemoveAnimationFilter
from ttconv.filters.supported_style_properties import SupportedStylePropertiesFilter
from ttconv.isd import StyleProcessors
from ttconv.model import ContentDocument, ContentElement, Region, P
from ttconv.style_properties import TextAlignType, ColorType, CoordinateType, DisplayAlignType, ExtentType, LengthType, StyleProperties, WritingModeType, NamedColors
import ttconv.utils

LOGGER = logging.getLogger(__name__)

def _replace_regions(element: ContentElement, region_aliases: typing.Mapping[Region, Region]):
  merged_region = region_aliases.get(element.get_region())
  if merged_region is not None:
    element.set_region(merged_region)
  for child in element:
    _replace_regions(child, region_aliases)

def _apply_bg_color(element: ContentElement, bg_color: ColorType):
  if isinstance(element, P):
    element.set_style(StyleProperties.BackgroundColor, bg_color)
  else:
    for child in element:
      _apply_bg_color(child, bg_color)

def _safe_area_decoder(s: Number) -> int:
  safe_area = int(s)
  if 30 < safe_area < 0:
    raise ValueError("Safe area must be an integer between 0 and 30")
  return safe_area

def _color_decoder(s: typing.Optional[ColorType]) -> typing.Optional[ColorType]:
  if s is None:
    return None

  if not isinstance(s, str):
    raise ValueError("Color specification must be a string")

  return ttconv.utils.parse_color(s)

@dataclass
class LCDDocFilterConfig(ModuleConfiguration):
  """Configuration class for the Least common denominator (LCD) filter"""

  @classmethod
  def name(cls):
    return "lcd"

  # specifies the safe area as an integer percentage
  safe_area: typing.Optional[int] = field(default=10, metadata={"decoder": _safe_area_decoder})

  # preserve text alignment
  preserve_text_align: typing.Optional[bool] = field(default=False, metadata={"decoder": bool})

  # overrides the text color
  color: typing.Optional[ColorType] = field(default=None, metadata={"decoder": _color_decoder})

  # overrides the background color
  bg_color: typing.Optional[ColorType] = field(default=None, metadata={"decoder": _color_decoder})

class LCDDocFilter(DocumentFilter):
  """Merges regions and removes all text formatting with the exception of color
  and text alignment."""

  @classmethod
  def get_config_class(cls) -> ModuleConfiguration:
    return LCDDocFilterConfig

  def __init__(self, config: LCDDocFilterConfig):
    super().__init__(config)

  def process(self, doc: ContentDocument) -> ContentDocument:

    # clean-up styles

    supported_styles = {
      StyleProperties.DisplayAlign: [],
      StyleProperties.Extent: [],
      StyleProperties.Origin: [],
      StyleProperties.Position: []
    }

    if self.config.preserve_text_align:
      supported_styles.update({StyleProperties.TextAlign: []})

    if self.config.color is None:
      supported_styles.update({StyleProperties.Color: []})

    if self.config.bg_color is None:
      supported_styles.update({StyleProperties.BackgroundColor: []})

    style_filter = SupportedStylePropertiesFilter(supported_styles)

    style_filter.process_initial_values(doc)

    if doc.get_body() is not None:
      style_filter.process_element(doc.get_body())

    # clean-up animations

    animation_filter = RemoveAnimationFilter()

    if doc.get_body() is not None:
      animation_filter.process_element(doc.get_body())

    # clean-up regions

    initial_extent = doc.get_initial_value(StyleProperties.Extent)
    initial_origin = doc.get_initial_value(StyleProperties.Origin)
    initial_writing_mode = doc.get_initial_value(StyleProperties.WritingMode)
    initial_display_align = doc.get_initial_value(StyleProperties.DisplayAlign)

    retained_regions = dict()
    replaced_regions = dict()

    for region in doc.iter_regions():

      # cleanup animations
      animation_filter.process_element(region)

      # cleanup styles
      style_filter.process_element(region)

      # compute origin
      if (region.get_style(StyleProperties.Origin)) is not None:
        StyleProcessors.Origin.compute(None, region)

      if (region.get_style(StyleProperties.Position)) is not None:
        StyleProcessors.Position.compute(None, region)
        region.set_style(StyleProperties.Position, None)

      if region.get_style(StyleProperties.Origin) is None:
        region.set_style(StyleProperties.Origin, initial_origin if initial_origin is not None \
                         else StyleProperties.Origin.make_initial_value())

      # compute extent
      if (region.get_style(StyleProperties.Extent)) is not None:
        StyleProcessors.Extent.compute(None, region)

      if region.get_style(StyleProperties.Extent) is None:
        region.set_style(StyleProperties.Extent, initial_extent if initial_extent is not None \
                         else StyleProperties.Extent.make_initial_value() )

      # computer writing_mode and display_align

      writing_mode = region.get_style(StyleProperties.WritingMode)
      if writing_mode is None:
        writing_mode = initial_writing_mode if initial_writing_mode is not None \
                        else StyleProperties.WritingMode.make_initial_value()

      display_align = region.get_style(StyleProperties.DisplayAlign)
      if display_align is None:
        display_align = initial_display_align if initial_display_align is not None \
                        else StyleProperties.DisplayAlign.make_initial_value()

      # determine new displayAlign value
      new_display_align = DisplayAlignType.after

      if writing_mode in (WritingModeType.lrtb, WritingModeType.rltb):
        if display_align == DisplayAlignType.before and region.get_style(StyleProperties.Origin).y.value < 50:
          new_display_align = DisplayAlignType.before
        elif region.get_style(StyleProperties.Origin).y.value + region.get_style(StyleProperties.Extent).height.value < 50:
          new_display_align = DisplayAlignType.before
      elif writing_mode == WritingModeType.tblr:
        if display_align == DisplayAlignType.before and region.get_style(StyleProperties.Origin).x.value < 50:
          new_display_align = DisplayAlignType.before
        elif region.get_style(StyleProperties.Origin).x.value + region.get_style(StyleProperties.Extent).width.value < 50:
            new_display_align = DisplayAlignType.before
      else: # writing_mode == WritingModeType.tbrl
        if display_align == DisplayAlignType.before and region.get_style(StyleProperties.Origin).x.value >= 50:
            new_display_align = DisplayAlignType.before
        elif region.get_style(StyleProperties.Origin).x.value + region.get_style(StyleProperties.Extent).width.value >= 50:
            new_display_align = DisplayAlignType.before

      region.set_style(StyleProperties.DisplayAlign, new_display_align)

      # reposition region
      region.set_style(
        StyleProperties.Origin,
        CoordinateType(
          x=LengthType(self.config.safe_area, LengthType.Units.pct),
          y=LengthType(self.config.safe_area, LengthType.Units.pct)
        )
      )

      region.set_style(
        StyleProperties.Extent,
        ExtentType(
          height=LengthType(value=100 - 2 * self.config.safe_area, units=LengthType.Units.pct),
          width=LengthType(value=100 - 2 * self.config.safe_area, units=LengthType.Units.pct)
        )
      )

      # check if a similar region has already been processed

      fingerprint = (
          region.get_begin() or 0,
          region.get_end() or None,
          writing_mode,
          new_display_align
        )

      retained_region = retained_regions.get(fingerprint)

      if retained_region is None:
        retained_regions[fingerprint] = region
      else:
        replaced_regions[region] = retained_region

    # prune aliased regions
    if doc.get_body() is not None:
      _replace_regions(doc.get_body(), replaced_regions)

    for region in list(doc.iter_regions()):
      if region in replaced_regions:
        doc.remove_region(region.get_id())

    # apply background color
    if self.config.bg_color is not None:
      _apply_bg_color(doc.get_body(), self.config.bg_color)

    # apply text color
    if doc.get_body() is not None and self.config.color is not None:
      doc.get_body().set_style(StyleProperties.Color, self.config.color)

    # apply text align
    if doc.get_body() is not None and not self.config.preserve_text_align:
      doc.get_body().set_style(StyleProperties.TextAlign, TextAlignType.center)
