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

# Section 8.4.7: tts:origin SHALL use px units or percentage values.
_ORIGIN_ALLOWED_UNITS = frozenset([
  styles.LengthType.Units.pct,
  styles.LengthType.Units.px,
])

# Section 8.4.2: tts:extent SHALL use px units, percentage values,
# or root container relative units.
_EXTENT_ALLOWED_UNITS = frozenset([
  styles.LengthType.Units.pct,
  styles.LengthType.Units.px,
  styles.LengthType.Units.rh,
  styles.LengthType.Units.rw,
])

# Section 8.4.8: tts:position SHALL use px units, percentage values
# or root container relative units.
_POSITION_ALLOWED_UNITS = frozenset([
  styles.LengthType.Units.pct,
  styles.LengthType.Units.px,
  styles.LengthType.Units.rh,
  styles.LengthType.Units.rw,
])

# Section 8.4.12: ebutts:linePadding only supports c length units.
_LINE_PADDING_ALLOWED_UNITS = frozenset([
  styles.LengthType.Units.c,
])

# Section 8.4.5: properties that allow negative lengths.
_NEGATIVE_LENGTH_ALLOWED_PROPS = frozenset([
  styles.StyleProperties.Disparity,
  styles.StyleProperties.TextShadow,
])

# Section 7.12.9: rh and rw units SHALL only appear on these properties.
_RH_RW_ALLOWED_PROPS = frozenset([
  styles.StyleProperties.Extent,
  styles.StyleProperties.Position,
  styles.StyleProperties.Origin,
])


def _check_negative(style_prop, length, context):
  """Section 8.4.5: negative lengths SHALL NOT be used except on
  tts:disparity and tts:textShadow."""
  if style_prop not in _NEGATIVE_LENGTH_ALLOWED_PROPS and length.value < 0:
    raise ValueError(
      f"{context} has negative value ({length.value}), "
      f"not allowed per section 8.4.5"
    )


def _check_rh_rw(style_prop, length, context):
  """Section 7.12.9: rh/rw units SHALL only appear on Extent, Position,
  and Origin."""
  if style_prop not in _RH_RW_ALLOWED_PROPS and \
    length.units in (styles.LengthType.Units.rh, styles.LengthType.Units.rw):
    raise ValueError(
      f"{context} uses '{length.units.value}' unit, "
      f"rh/rw only allowed on Extent, Position, Origin (section 7.12.9)"
    )


def _check_length_constraints(element, style_prop, value):
  """Checks length unit and value constraints per IMSC 1.1 Text Profile."""
  elem_name = type(element).__name__

  if style_prop is styles.StyleProperties.Origin:
    for axis, length in (("x", value.x), ("y", value.y)):
      ctx = f"{elem_name}: Origin.{axis}"
      if length.units not in _ORIGIN_ALLOWED_UNITS:
        raise ValueError(
          f"{ctx} uses unit '{length.units.value}', "
          f"allowed: pct, px (section 8.4.7)"
        )
      _check_negative(style_prop, length, ctx)

  elif style_prop is styles.StyleProperties.Extent:
    for axis, length in (("width", value.width), ("height", value.height)):
      ctx = f"{elem_name}: Extent.{axis}"
      if length.units not in _EXTENT_ALLOWED_UNITS:
        raise ValueError(
          f"{ctx} uses unit '{length.units.value}', "
          f"allowed: pct, px, rh, rw (section 8.4.2)"
        )
      _check_negative(style_prop, length, ctx)

  elif style_prop is styles.StyleProperties.Position:
    for axis, length in (("h_offset", value.h_offset), ("v_offset", value.v_offset)):
      ctx = f"{elem_name}: Position.{axis}"
      if length.units not in _POSITION_ALLOWED_UNITS:
        raise ValueError(
          f"{ctx} uses unit '{length.units.value}', "
          f"allowed: pct, px, rh, rw (section 8.4.8)"
        )
      _check_negative(style_prop, length, ctx)

  elif style_prop is styles.StyleProperties.FontSize:
    ctx = f"{elem_name}: FontSize"
    _check_negative(style_prop, value, ctx)
    _check_rh_rw(style_prop, value, ctx)

  elif style_prop is styles.StyleProperties.LineHeight:
    if value is not styles.SpecialValues.normal:
      ctx = f"{elem_name}: LineHeight"
      _check_negative(style_prop, value, ctx)
      _check_rh_rw(style_prop, value, ctx)

  elif style_prop is styles.StyleProperties.LinePadding:
    ctx = f"{elem_name}: LinePadding"
    if value.units not in _LINE_PADDING_ALLOWED_UNITS:
      raise ValueError(
        f"{ctx} uses unit '{value.units.value}', "
        f"allowed: c (section 8.4.12)"
      )
    _check_negative(style_prop, value, ctx)

  elif style_prop is styles.StyleProperties.Padding:
    for side, length in (
      ("before", value.before), ("end", value.end),
      ("after", value.after), ("start", value.start),
    ):
      ctx = f"{elem_name}: Padding.{side}"
      _check_negative(style_prop, length, ctx)
      _check_rh_rw(style_prop, length, ctx)

  elif style_prop is styles.StyleProperties.TextOutline:
    if value is not None and value is not styles.SpecialValues.none:
      ctx = f"{elem_name}: TextOutline.thickness"
      _check_negative(style_prop, value.thickness, ctx)
      _check_rh_rw(style_prop, value.thickness, ctx)

  elif style_prop is styles.StyleProperties.TextShadow:
    if value is not None and value is not styles.SpecialValues.none:
      if len(value.shadows) > 4:
        raise ValueError(
          f"{elem_name}: TextShadow has {len(value.shadows)} shadows, "
          f"maximum 4 allowed (section 8.4.11)"
        )

  elif style_prop is styles.StyleProperties.Disparity:
    if isinstance(value, styles.LengthType):
      ctx = f"{elem_name}: Disparity"
      _check_rh_rw(style_prop, value, ctx)

  elif style_prop is styles.StyleProperties.RubyReserve:
    if value is not styles.SpecialValues.none and hasattr(value, 'length') and value.length is not None:
      ctx = f"{elem_name}: RubyReserve.length"
      _check_negative(style_prop, value.length, ctx)
      _check_rh_rw(style_prop, value.length, ctx)


def _validate_region(region):
  """Validates region-specific structural constraints."""

  # Section 8.4.2: tts:extent SHALL be present on all region elements.
  # Check both specified style and document initial value.
  extent = region.get_style(styles.StyleProperties.Extent)
  if extent is None:
    doc = region.get_doc()
    extent = doc.get_initial_value(styles.StyleProperties.Extent)
  if extent is None:
    raise ValueError(
      f"Region '{region.get_id()}': tts:extent SHALL be present "
      f"on all region elements (section 8.4.2)"
    )

  # Section 8.4.7/8.4.8: origin and position SHALL NOT coexist
  has_origin = region.has_style(styles.StyleProperties.Origin)
  has_position = region.has_style(styles.StyleProperties.Position)
  if has_origin and has_position:
    raise ValueError(
      f"Region '{region.get_id()}': tts:origin and tts:position "
      f"SHALL NOT both be present (section 8.4.7)"
    )


def _validate_element_styles(element):
  """Validates specified styles on a ContentDocument element."""

  if not isinstance(element, _ALLOWED_ELEMENT_TYPES):
    raise ValueError(f"Unsupported element type: {type(element).__name__}")

  for style_prop in element.iter_styles():
    if style_prop not in _IMSC_11_TEXT_STYLE_PROPS:
      raise ValueError(
        f"{type(element).__name__}: style property "
        f"'{style_prop.__name__}' is not in the IMSC 1.1 Text Profile"
      )

    value = element.get_style(style_prop)
    _check_length_constraints(element, style_prop, value)


def _check_isd_negative(elem_name, value, context):
  """Checks a single resolved length for negative value."""
  if isinstance(value, styles.LengthType) and value.value < 0:
    raise ValueError(
      f"{elem_name}: resolved {context} is negative "
      f"({value.value}), not allowed per section 8.4.5"
    )


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

  # Section 8.4.5: negative lengths SHALL NOT be used
  # (except on tts:disparity and tts:textShadow).
  # Checking on resolved ISD values catches inherited/initial negatives.

  extent = element.get_style(styles.StyleProperties.Extent)
  if extent is not None:
    _check_isd_negative(elem_name, extent.width, "Extent.width")
    _check_isd_negative(elem_name, extent.height, "Extent.height")

  origin = element.get_style(styles.StyleProperties.Origin)
  if origin is not None:
    _check_isd_negative(elem_name, origin.x, "Origin.x")
    _check_isd_negative(elem_name, origin.y, "Origin.y")

  font_size = element.get_style(styles.StyleProperties.FontSize)
  if font_size is not None:
    _check_isd_negative(elem_name, font_size, "FontSize")

  line_height = element.get_style(styles.StyleProperties.LineHeight)
  if line_height is not None and line_height is not styles.SpecialValues.normal:
    _check_isd_negative(elem_name, line_height, "LineHeight")

  padding = element.get_style(styles.StyleProperties.Padding)
  if padding is not None:
    _check_isd_negative(elem_name, padding.before, "Padding.before")
    _check_isd_negative(elem_name, padding.end, "Padding.end")
    _check_isd_negative(elem_name, padding.after, "Padding.after")
    _check_isd_negative(elem_name, padding.start, "Padding.start")

  text_outline = element.get_style(styles.StyleProperties.TextOutline)
  if text_outline is not None and text_outline is not styles.SpecialValues.none:
    _check_isd_negative(elem_name, text_outline.thickness, "TextOutline.thickness")

  line_padding = element.get_style(styles.StyleProperties.LinePadding)
  if line_padding is not None:
    _check_isd_negative(elem_name, line_padding, "LinePadding")


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
    for region in doc.iter_regions():
      _validate_region(region)

    # ContentDocument specified-style checks on regions
    for region in doc.iter_regions():
      _validate_element_styles(region)

    # ContentDocument specified-style checks on body elements
    body = doc.get_body()
    if body is not None:
      for element in body.dfs_iterator():
        _validate_element_styles(element)

    # ISD-based resolved style checks
    isd_sequence = ISD.generate_isd_sequence(doc)
    for _, isd in isd_sequence:
      for isd_region in isd.iter_regions():
        for element in isd_region.dfs_iterator():
          _validate_isd_element(element)

    # Success: add designator to content profiles
    content_profiles = doc.get_content_profiles()
    if content_profiles is None:
      content_profiles = set()
    content_profiles.add(IMSC_11_TEXT_PROFILE_DESIGNATOR)
    doc.set_content_profiles(content_profiles)
