#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2025, Sandflow Consulting LLC
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

"""IMSC 1.1 Text Profile conformance filter.

Validates a ContentDocument against IMSC 1.1 Text Profile constraints
per https://www.w3.org/TR/ttml-imsc1.1/ sections 6, 7.12, and 8.4.

On success, adds the IMSC 1.1 Text Profile designator to the document's
content profiles. On failure, raises ValueError on the first violation found.
"""

from __future__ import annotations

from dataclasses import dataclass

from ttconv.config import ModuleConfiguration
from ttconv.filters.document_filter import DocumentFilter
from ttconv.imsc.designators import IMSC_11_TEXT_PROFILE_DESIGNATOR
from ttconv.isd import ISD
import ttconv.model as model
import ttconv.style_properties as styles

# Section 6: allowed element types.
_ALLOWED_ELEMENT_TYPES = (
  model.Body,
  model.Div,
  model.P,
  model.Span,
  model.Br,
  model.Text,
  model.Ruby,
  model.Rb,
  model.Rt,
  model.Rp,
  model.Rbc,
  model.Rtc,
  model.Region,
)

# Section 6: explicit list of the 36 IMSC 1.1 Text Profile style properties.
_IMSC_11_TEXT_STYLE_PROPS = frozenset([
  styles.StyleProperties.BackgroundColor,
  styles.StyleProperties.Color,
  styles.StyleProperties.Direction,
  styles.StyleProperties.Disparity,
  styles.StyleProperties.Display,
  styles.StyleProperties.DisplayAlign,
  styles.StyleProperties.Extent,
  styles.StyleProperties.FillLineGap,
  styles.StyleProperties.FontFamily,
  styles.StyleProperties.FontSize,
  styles.StyleProperties.FontStyle,
  styles.StyleProperties.FontWeight,
  styles.StyleProperties.LineHeight,
  styles.StyleProperties.LinePadding,
  styles.StyleProperties.LuminanceGain,
  styles.StyleProperties.MultiRowAlign,
  styles.StyleProperties.Opacity,
  styles.StyleProperties.Origin,
  styles.StyleProperties.Overflow,
  styles.StyleProperties.Padding,
  styles.StyleProperties.Position,
  styles.StyleProperties.RubyAlign,
  styles.StyleProperties.RubyPosition,
  styles.StyleProperties.RubyReserve,
  styles.StyleProperties.Shear,
  styles.StyleProperties.ShowBackground,
  styles.StyleProperties.TextAlign,
  styles.StyleProperties.TextCombine,
  styles.StyleProperties.TextDecoration,
  styles.StyleProperties.TextEmphasis,
  styles.StyleProperties.TextOutline,
  styles.StyleProperties.TextShadow,
  styles.StyleProperties.UnicodeBidi,
  styles.StyleProperties.Visibility,
  styles.StyleProperties.WrapOption,
  styles.StyleProperties.WritingMode,
])


def _iter_lengths(value):
  """Yields all LengthType values embedded in a style value."""
  if isinstance(value, styles.LengthType):
    yield value
  elif isinstance(value, styles.ExtentType):
    yield value.width
    yield value.height
  elif isinstance(value, styles.CoordinateType):
    yield value.x
    yield value.y
  elif isinstance(value, styles.PositionType):
    yield value.h_offset
    yield value.v_offset
  elif isinstance(value, styles.PaddingType):
    yield value.before
    yield value.end
    yield value.after
    yield value.start
  elif isinstance(value, styles.TextOutlineType):
    yield value.thickness
  elif isinstance(value, styles.RubyReserveType):
    if value.length is not None:
      yield value.length
  elif isinstance(value, styles.TextShadowType):
    for shadow in value.shadows:
      yield shadow.x_offset
      yield shadow.y_offset
      if shadow.blur_radius is not None:
        yield shadow.blur_radius


def _validate_regions(doc):
  """Validates region-specific structural constraints across the document."""

  has_any_origin = False
  has_any_position = False

  for region in doc.iter_regions():
    # Section 8.4.2: tts:extent SHALL be present on all region elements.
    # Check both specified style and document initial value.
    extent = region.get_style(styles.StyleProperties.Extent)
    if extent is None:
      extent = doc.get_initial_value(styles.StyleProperties.Extent)
    if extent is None:
      raise ValueError(
        f"Region '{region.get_id()}': tts:extent SHALL be present "
        f"on all region elements (section 8.4.2)"
      )

    # Section 8.4.7/8.4.8: origin and position SHALL NOT coexist on same region
    has_origin = region.has_style(styles.StyleProperties.Origin)
    has_position = region.has_style(styles.StyleProperties.Position)
    if has_origin and has_position:
      raise ValueError(
        f"Region '{region.get_id()}': tts:origin and tts:position "
        f"SHALL NOT both be present (section 8.4.7)"
      )

    # Section 8.4.7: tts:origin SHALL use px units or percentage values
    if has_origin:
      has_any_origin = True
      origin = region.get_style(styles.StyleProperties.Origin)
      if origin is not None:
        for length in (origin.x, origin.y):
          if length.units not in (styles.LengthType.Units.pct, styles.LengthType.Units.px):
            raise ValueError(
              f"Region '{region.get_id()}': tts:origin SHALL use px or % "
              f"units only, found '{length.units}' (section 8.4.7)"
            )

    if has_position:
      has_any_position = True

  # Section 8.4.7/8.4.8: document-wide mutual exclusion
  if has_any_origin and has_any_position:
    raise ValueError(
      "tts:origin and tts:position SHALL NOT both be present "
      "in a Document Instance (section 8.4.7/8.4.8)"
    )


def _validate_element_styles(element):
  """Validates specified styles on a ContentDocument element."""

  if not isinstance(element, _ALLOWED_ELEMENT_TYPES):
    raise ValueError(f"Unsupported element type: {type(element).__name__}")

  elem_name = type(element).__name__

  for style_prop in element.iter_styles():
    if style_prop not in _IMSC_11_TEXT_STYLE_PROPS:
      raise ValueError(
        f"{elem_name}: style property "
        f"'{style_prop.__name__}' is not in the IMSC 1.1 Text Profile"
      )

    value = element.get_style(style_prop)

    # Section 8.4.12: linePadding SHALL use c units only
    if style_prop is styles.StyleProperties.LinePadding \
        and value.units != styles.LengthType.Units.c:
      raise ValueError(
        f"{elem_name}: LinePadding SHALL use c units only, "
        f"found '{value.units}' (section 8.4.12)"
      )

    # Section 7.2.18: c units SHALL NOT be present outside of ebutts:linePadding
    if style_prop is not styles.StyleProperties.LinePadding:
      for length in _iter_lengths(value):
        if length.units == styles.LengthType.Units.c:
          raise ValueError(
            f"{elem_name}: {style_prop.__name__} uses 'c' unit, "
            f"only allowed on LinePadding (section 7.2.18)"
          )

    # Section 8.4.13: ebutts:multiRowAlign SHALL only appear on p elements
    if style_prop is styles.StyleProperties.MultiRowAlign \
        and not isinstance(element, model.P):
      raise ValueError(
        f"{elem_name}: MultiRowAlign SHALL only appear on p elements "
        f"(section 8.4.13)"
      )

    # Section 8.4.11: textShadow SHALL NOT have more than 4 shadows
    if style_prop is styles.StyleProperties.TextShadow \
        and value is not styles.SpecialValues.none \
        and len(value.shadows) > 4:
      raise ValueError(
        f"{elem_name}: TextShadow has {len(value.shadows)} shadows, "
        f"maximum 4 allowed (section 8.4.11)"
      )


def _regions_overlap(r1: ISD.Region, r2: ISD.Region) -> bool:
  """Returns True if two ISD regions spatially overlap.

  Compares bounding rectangles defined by tts:origin and tts:extent.
  After ISD computation both properties use rw (x-axis) and rh (y-axis)
  units, so the values are directly comparable.
  """
  o1 = r1.get_style(styles.StyleProperties.Origin)
  e1 = r1.get_style(styles.StyleProperties.Extent)
  o2 = r2.get_style(styles.StyleProperties.Origin)
  e2 = r2.get_style(styles.StyleProperties.Extent)

  if o1 is None or e1 is None or o2 is None or e2 is None:
    return False

  # r1 bounding box
  x1, y1 = o1.x.value, o1.y.value
  x2, y2 = x1 + e1.width.value, y1 + e1.height.value

  # r2 bounding box
  ax1, ay1 = o2.x.value, o2.y.value
  ax2, ay2 = ax1 + e2.width.value, ay1 + e2.height.value

  return not (x2 <= ax1 or ax2 <= x1 or y2 <= ay1 or ay2 <= y1)


def _validate_isd_element(element):
  """Validates resolved style values on an ISD element.

  Checks are performed on fully resolved styles (inherited, initial,
  and computed) to catch violations that specified-style checks miss.
  """
  elem_name = type(element).__name__

  # Section 8.4.11: textShadow SHALL NOT have more than 4 shadows
  ts_value = element.get_style(styles.StyleProperties.TextShadow)
  if ts_value is not None and ts_value is not styles.SpecialValues.none:
    if len(ts_value.shadows) > 4:
      raise ValueError(
        f"{elem_name}: TextShadow has {len(ts_value.shadows)} "
        f"shadows, maximum 4 allowed (section 8.4.11)"
      )

  # Section 8.4.9: tts:rubyAlign SHALL be "center" or "spaceAround"
  # (defense-in-depth; model enum already constrains this)
  ruby_align = element.get_style(styles.StyleProperties.RubyAlign)
  if ruby_align is not None and \
      ruby_align not in (styles.RubyAlignType.center, styles.RubyAlignType.spaceAround):
    raise ValueError(
      f"{elem_name}: RubyAlign value '{ruby_align}' not allowed, "
      f"must be center or spaceAround (section 8.4.9)"
    )

  # Section 8.4.10: textOutline thickness SHALL NOT exceed 10% of fontSize
  text_outline = element.get_style(styles.StyleProperties.TextOutline)
  if text_outline is not None and text_outline is not styles.SpecialValues.none:
    font_size = element.get_style(styles.StyleProperties.FontSize)
    if font_size is not None and isinstance(font_size, styles.LengthType) \
        and text_outline.thickness.units == font_size.units:
      if text_outline.thickness.value > 0.1 * font_size.value:
        raise ValueError(
          f"{elem_name}: TextOutline thickness ({text_outline.thickness.value}) "
          f"exceeds 10% of fontSize ({font_size.value}) (section 8.4.10)"
        )




@dataclass
class IMSC11TextFilterConfig(ModuleConfiguration):
  """Configuration for the IMSC 1.1 Text Profile conformance filter."""

  @classmethod
  def name(cls):
    return "imsc11text"


class IMSC11TextFilter(DocumentFilter):
  """Validates a ContentDocument against IMSC 1.1 Text Profile constraints.

  On success, adds the IMSC 1.1 Text Profile designator to the document's
  content profiles. On failure, raises ValueError with the first violation.
  """

  @classmethod
  def get_config_class(cls) -> ModuleConfiguration:
    return IMSC11TextFilterConfig

  def __init__(self, config: IMSC11TextFilterConfig = None):
    super().__init__(config or IMSC11TextFilterConfig())

  def process(self, doc: model.ContentDocument):

    # ContentDocument structural checks on regions
    _validate_regions(doc)

    # ContentDocument specified-style checks on regions
    for region in doc.iter_regions():
      _validate_element_styles(region)

    # ContentDocument specified-style checks on body elements
    body = doc.get_body()
    if body is not None:
      for element in body.dfs_iterator():
        _validate_element_styles(element)

    # Section 7.12.6: px requires tts:extent on tt is not implementable at filter
    # level because the model stores tts:extent on tt as px_resolution (with a
    # default of 1920x1080), making it impossible to distinguish "explicitly set"
    # from "not present". The IMSC reader enforces this at parse time.

    # Section 7.12.7: ttp:frameRate constraints are not implementable at filter
    # level because the model stores timing as Fraction offsets and does not
    # preserve the original format or frameRate attribute.

    # ISD-based resolved style checks
    isd_sequence = ISD.generate_isd_sequence(doc)
    for _, isd in isd_sequence:
      # Section 7.12.1.3: no more than 4 regions per ISD
      regions = list(isd.iter_regions())
      if len(regions) > 4:
        raise ValueError(
          f"ISD has {len(regions)} regions, "
          f"maximum 4 allowed (section 7.12.1.3)"
        )

      for i in range(0, len(regions)):
        for j in range(i + 1, len(regions)):
          if _regions_overlap(regions[i], regions[j]):
            raise ValueError(
              f"Regions '{regions[i].get_id()}' and '{regions[j].get_id()}' "
              f"spatially overlap (section 7.12.1.3)"
            )

      for isd_region in regions:
        for element in isd_region.dfs_iterator():
          _validate_isd_element(element)

    # Success: add designator to content profiles
    content_profiles = doc.get_content_profiles()
    if content_profiles is None:
      content_profiles = set()
    content_profiles.add(IMSC_11_TEXT_PROFILE_DESIGNATOR)
    doc.set_content_profiles(content_profiles)
