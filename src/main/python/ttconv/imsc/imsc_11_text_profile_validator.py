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

'''Validates a ContentDocument against IMSC 1.1 Text Profile constraints.

Based on https://www.w3.org/TR/ttml-imsc1.1/ sections 6, 7.12, and 8.4.
'''

import typing

import ttconv.model as model
import ttconv.style_properties as styles
from ttconv.imsc import style_properties as imsc_styles

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

_IMSC_11_TEXT_STYLE_PROPS = frozenset(imsc_styles.StyleProperties.BY_MODEL_PROP.keys())

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

# All TTML2 length units permitted in the Text Profile (section 6).
_ALL_PERMITTED_UNITS = frozenset([
  styles.LengthType.Units.pct,
  styles.LengthType.Units.px,
  styles.LengthType.Units.em,
  styles.LengthType.Units.c,
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


def _check_length_negative(
  violations: typing.List[str],
  element: model.ContentElement,
  style_prop: typing.Type[styles.StyleProperty],
  length: styles.LengthType,
  context: str,
):
  '''Section 8.4.5: negative lengths SHALL NOT be used except on
  tts:disparity and tts:textShadow.'''
  if style_prop not in _NEGATIVE_LENGTH_ALLOWED_PROPS and length.value < 0:
    violations.append(
      f"{type(element).__name__}: {context} has negative value "
      f"({length.value}), not allowed per section 8.4.5"
    )


def _check_length_units(
  violations: typing.List[str],
  element: model.ContentElement,
  style_prop: typing.Type[styles.StyleProperty],
  value: typing.Any,
):
  '''Checks length unit and value constraints per IMSC 1.1 Text Profile.'''

  # Section 8.4.7: origin SHALL use px or %
  if style_prop is styles.StyleProperties.Origin:
    for axis, length in (("x", value.x), ("y", value.y)):
      if length.units not in _ORIGIN_ALLOWED_UNITS:
        violations.append(
          f"{type(element).__name__}: Origin.{axis} uses unit "
          f"'{length.units.value}', allowed: pct, px (section 8.4.7)"
        )
      _check_length_negative(violations, element, style_prop, length, f"Origin.{axis}")

  # Section 8.4.2: extent SHALL use px, %, or rh/rw
  elif style_prop is styles.StyleProperties.Extent:
    for axis, length in (("width", value.width), ("height", value.height)):
      if length.units not in _EXTENT_ALLOWED_UNITS:
        violations.append(
          f"{type(element).__name__}: Extent.{axis} uses unit "
          f"'{length.units.value}', allowed: pct, px, rh, rw (section 8.4.2)"
        )
      _check_length_negative(violations, element, style_prop, length, f"Extent.{axis}")

  # Section 8.4.8: position SHALL use px, %, or rh/rw
  elif style_prop is styles.StyleProperties.Position:
    for axis, length in (("h_offset", value.h_offset), ("v_offset", value.v_offset)):
      if length.units not in _POSITION_ALLOWED_UNITS:
        violations.append(
          f"{type(element).__name__}: Position.{axis} uses unit "
          f"'{length.units.value}', allowed: pct, px, rh, rw (section 8.4.8)"
        )
      _check_length_negative(violations, element, style_prop, length, f"Position.{axis}")

  elif style_prop is styles.StyleProperties.FontSize:
    _check_length_negative(violations, element, style_prop, value, "FontSize")

  elif style_prop is styles.StyleProperties.LineHeight:
    if value is not styles.SpecialValues.normal:
      _check_length_negative(violations, element, style_prop, value, "LineHeight")

  # Section 8.4.12: linePadding only supports c units
  elif style_prop is styles.StyleProperties.LinePadding:
    if value.units not in _LINE_PADDING_ALLOWED_UNITS:
      violations.append(
        f"{type(element).__name__}: LinePadding uses unit "
        f"'{value.units.value}', allowed: c (section 8.4.12)"
      )
    _check_length_negative(violations, element, style_prop, value, "LinePadding")

  elif style_prop is styles.StyleProperties.Padding:
    for side, length in (
      ("before", value.before), ("end", value.end),
      ("after", value.after), ("start", value.start),
    ):
      _check_length_negative(violations, element, style_prop, length, f"Padding.{side}")

  # Section 8.4.10: textOutline thickness constraint
  elif style_prop is styles.StyleProperties.TextOutline:
    if value is not None and value is not styles.SpecialValues.none:
      _check_length_negative(violations, element, style_prop, value.thickness, "TextOutline.thickness")

  # Section 8.4.11: textShadow SHALL NOT have more than 4 shadows
  elif style_prop is styles.StyleProperties.TextShadow:
    if value is not None and value is not styles.SpecialValues.none:
      if len(value.shadows) > 4:
        violations.append(
          f"{type(element).__name__}: TextShadow has {len(value.shadows)} shadows, "
          f"maximum 4 allowed (section 8.4.11)"
        )


def _validate_element(
  violations: typing.List[str],
  element: model.ContentElement,
):
  '''Validates a single element against IMSC 1.1 Text Profile constraints.'''

  if not isinstance(element, _ALLOWED_ELEMENT_TYPES):
    violations.append(
      f"Unsupported element type: {type(element).__name__}"
    )
    return

  for style_prop in element.iter_styles():
    if style_prop not in _IMSC_11_TEXT_STYLE_PROPS:
      violations.append(
        f"{type(element).__name__}: style property "
        f"'{style_prop.__name__}' is not in the IMSC 1.1 Text Profile"
      )
      continue

    value = element.get_style(style_prop)
    _check_length_units(violations, element, style_prop, value)

  # Section 8.4.9: rubyAlign SHALL be center or spaceAround.
  # The model already constrains RubyAlignType to {center, spaceAround},
  # so this is enforced at set_style() time.


def _validate_region(
  violations: typing.List[str],
  region: model.Region,
):
  '''Validates region-specific constraints.'''

  _validate_element(violations, region)

  # Section 8.4.2: tts:extent SHALL be present on all region elements
  if region.get_style(styles.StyleProperties.Extent) is None:
    violations.append(
      f"Region '{region.get_id()}': tts:extent SHALL be present "
      f"on all region elements (section 8.4.2)"
    )

  # Section 8.4.7/8.4.8: origin and position SHALL NOT coexist
  has_origin = region.has_style(styles.StyleProperties.Origin)
  has_position = region.has_style(styles.StyleProperties.Position)
  if has_origin and has_position:
    violations.append(
      f"Region '{region.get_id()}': tts:origin and tts:position "
      f"SHALL NOT both be present (section 8.4.7)"
    )


def validate_imsc_11_text_profile(
  doc: model.ContentDocument,
) -> typing.List[str]:
  '''Validates a ContentDocument against IMSC 1.1 Text Profile constraints.

  Based on https://www.w3.org/TR/ttml-imsc1.1/ sections 6, 7.12, and 8.4.

  Returns an empty list if the document conforms, or a list of violation
  descriptions otherwise.
  '''
  violations: typing.List[str] = []

  for region in doc.iter_regions():
    _validate_region(violations, region)

  body = doc.get_body()
  if body is not None:
    for element in body.dfs_iterator():
      _validate_element(violations, element)

  return violations
