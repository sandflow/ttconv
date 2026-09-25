#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) Sandflow Consulting LLC
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

'''[IMSC Rosetta style definitions](https://github.com/imsc-rosetta/imsc-rosetta-specification/blob/main/documents/styles.md)
'''

from __future__ import annotations
import re
import typing

from ttconv.imsc.namespaces import QName
from ttconv.imsc.validator.event_handler import EventHandler
import ttconv.imsc.validator.other_attributes as other_attrs
import ttconv.imsc.validator.style_attributes as style_attrs
import ttconv.style_properties as ttconv_styles

class StyleElementValidator:
  '''Validates the attributes of a style element.

  `permitted_styles` are the attributes that the validator constrains, each identified by its class in `style_attributes`, or in
  `other_attributes` if it is not a style property. Subclasses override `validate()`, and shall call `super().validate()`.'''
  permitted_styles: typing.AbstractSet[typing.Any]

  def validate(self, style_id: str, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    '''Reports each attribute in `values` that the style shall not specify, i.e., that is not one of `permitted_styles`, to
    `event_handler`.

    `style_id` is the `xml:id` of the style, `line` is its line number, and `values` are the attributes that it specifies, other
    than `xml:id`, as a mapping of their qualified name to their value.'''
    permitted_qnames = {attr.qname for attr in self.permitted_styles}
    for qname in values:
      if qname not in permitted_qnames:
        event_handler.error("Attribute %s is not permitted on style `%s` (line %s)", qname.local_name, style_id, line)

class SinglePropertyValidator(StyleElementValidator):
  '''Validates a style that specifies a single style property, e.g., `tts:color`. A style shall specify the property, unless
  `required` is false, and its value shall satisfy `check()`.

  Subclasses set `attribute` to the class in `style_attributes` of the property, and override `description` and `check()`.'''

  attribute: typing.Any
  required = True

  @property
  def permitted_styles(self) -> typing.AbstractSet[typing.Any]:
    return frozenset((self.attribute,))

  @property
  def description(self) -> str:
    '''Describes the values that satisfy the constraint, e.g., "a percentage"'''
    raise NotImplementedError

  def check(self, value: str) -> bool:
    '''Returns whether `value` is valid'''
    raise NotImplementedError

  def validate(self, style_id: str, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(style_id, values, line, event_handler)
    name = self.attribute.qname.local_name
    value = values.get(self.attribute.qname)
    if value is None:
      if self.required:
        event_handler.error("Attribute %s is required on style `%s` (line %s)", name, style_id, line)
    elif not self.check(value):
      event_handler.error("Attribute %s of style `%s` shall be %s (line %s)", name, style_id, self.description, line)

_HEX6 = re.compile(r"^#[0-9A-F]{6}$")
_HEX8 = re.compile(r"^#[0-9A-F]{8}$")
_OUTLINE_RE = re.compile(r"^#[0-9A-F]{6} 0\.05em$")

class ColorValidator(SinglePropertyValidator):
  '''Validates the `s_fg_xxx` styles. Colors may be adjusted, e.g., to change the shade of yellow, but not the color family.'''

  attribute = style_attrs.Color
  description = "a color in `#RRGGBB` notation using upper case hex digits"

  def check(self, value: str) -> bool:
    return _HEX6.match(value) is not None

class OutlineValidator(SinglePropertyValidator):
  '''Validates the `s_outlinexxx` and `s_dropxxx` styles'''

  attribute = style_attrs.TextOutline
  description = "`#RRGGBB 0.05em` using upper case hex digits"

  def check(self, value: str) -> bool:
    return _OUTLINE_RE.match(value) is not None

class NoOutlineValidator(SinglePropertyValidator):
  '''Validates the `s_nonexxx` styles'''

  attribute = style_attrs.TextOutline
  # tts:textOutline was added to s_nonexxx after the initial revision of the specification
  required = False
  expected = ttconv_styles.SpecialValues.none.value
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class BoxedBackgroundValidator(SinglePropertyValidator):
  '''Validates the `ps_bg_boxedxxx` styles'''

  attribute = style_attrs.BackgroundColor
  description = "a color in `#RRGGBB` notation using upper case hex digits"

  def check(self, value: str) -> bool:
    return _HEX6.match(value) is not None

class GhostBoxedBackgroundValidator(SinglePropertyValidator):
  '''Validates the `ps_bg_ghostboxedxxx` styles'''

  attribute = style_attrs.BackgroundColor
  description = "a color in `#RRGGBBAA` notation using upper case hex digits"

  def check(self, value: str) -> bool:
    return _HEX8.match(value) is not None

_NUMBER = r"\d+(\.\d+)?"
_PERCENT = re.compile(rf"^{_NUMBER}%$")
_PERCENT_PAIR = re.compile(rf"^{_NUMBER}% {_NUMBER}%$")
_RH = re.compile(rf"^{_NUMBER}rh$")
_CELLS = re.compile(rf"^{_NUMBER}c$")
_FLOAT = re.compile(rf"^{_NUMBER}$")
_BOOLEAN = re.compile(r"^(true|false)$")

class ParagraphFontValidator(StyleElementValidator):
  '''Validates the `p_font1` and `p_font2` styles. `tts:fontFamily` may be omitted and has any value.'''

  permitted_styles = frozenset((style_attrs.FontSize, style_attrs.LineHeight, style_attrs.FontFamily))

  def validate(self, style_id: str, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(style_id, values, line, event_handler)
    value = values.get(style_attrs.FontSize.qname)
    if value is None:
      event_handler.error("Attribute fontSize is required on style `%s` (line %s)", style_id, line)
    elif not _PERCENT.match(value):
      event_handler.error("Attribute fontSize of style `%s` shall be a percentage (line %s)", style_id, line)
    value = values.get(style_attrs.LineHeight.qname)
    if value is None:
      event_handler.error("Attribute lineHeight is required on style `%s` (line %s)", style_id, line)
    elif not _PERCENT.match(value):
      event_handler.error("Attribute lineHeight of style `%s` shall be a percentage (line %s)", style_id, line)

FOREGROUND_STYLES = frozenset((
  "s_fg_black", "s_fg_red", "s_fg_yellow", "s_fg_green", "s_fg_cyan", "s_fg_blue", "s_fg_magenta", "s_fg_white",
))

ALIGNMENT_STYLES = frozenset((
  "p_al_start", "p_al_end", "p_al_center",
  "p_al_start_center", "p_al_start_end",
  "p_al_end_start", "p_al_end_center",
  "p_al_center_start", "p_al_center_end",
))

class DefaultRegionValidator(StyleElementValidator):
  '''Validates the properties of the `_r_default` style, and that it references exactly one of `FOREGROUND_STYLES` and exactly
  one of `ALIGNMENT_STYLES`'''

  permitted_styles = frozenset((
    other_attrs.StyleAttribute,
    style_attrs.FontSize,
    style_attrs.LineHeight,
    style_attrs.LinePadding,
    style_attrs.LuminanceGain,
    style_attrs.FillLineGap,
  ))

  def validate(self, style_id: str, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(style_id, values, line, event_handler)
    value = values.get(style_attrs.FontSize.qname)
    if value is None:
      event_handler.error("Attribute fontSize is required on style `%s` (line %s)", style_id, line)
    elif not _RH.match(value):
      event_handler.error("Attribute fontSize of style `%s` shall be a length in `rh` units (line %s)", style_id, line)
    value = values.get(style_attrs.LineHeight.qname)
    if value is None:
      event_handler.error("Attribute lineHeight is required on style `%s` (line %s)", style_id, line)
    elif not _PERCENT.match(value):
      event_handler.error("Attribute lineHeight of style `%s` shall be a percentage (line %s)", style_id, line)
    value = values.get(style_attrs.LinePadding.qname)
    if value is None:
      event_handler.error("Attribute linePadding is required on style `%s` (line %s)", style_id, line)
    elif not _CELLS.match(value):
      event_handler.error("Attribute linePadding of style `%s` shall be a length in `c` units (line %s)", style_id, line)
    value = values.get(style_attrs.LuminanceGain.qname)
    if value is None:
      event_handler.error("Attribute luminanceGain is required on style `%s` (line %s)", style_id, line)
    elif not _FLOAT.match(value):
      event_handler.error("Attribute luminanceGain of style `%s` shall be a number (line %s)", style_id, line)
    value = values.get(style_attrs.FillLineGap.qname)
    if value is None:
      event_handler.error("Attribute fillLineGap is required on style `%s` (line %s)", style_id, line)
    elif not _BOOLEAN.match(value):
      event_handler.error("Attribute fillLineGap of style `%s` shall be `true` or `false` (line %s)", style_id, line)
    value = values.get(other_attrs.StyleAttribute.qname)
    if value is None:
      event_handler.error("Attribute style is required on style `%s` (line %s)", style_id, line)
    else:
      listed = value.split()
      if not (
        len(listed) == 2
        and sum(1 for s in listed if s in FOREGROUND_STYLES) == 1
        and sum(1 for s in listed if s in ALIGNMENT_STYLES) == 1
      ):
        event_handler.error(
          "Attribute style of style `%s` shall be exactly one of %s and exactly one of %s (line %s)",
          style_id, ", ".join(sorted(FOREGROUND_STYLES)), ", ".join(sorted(ALIGNMENT_STYLES)), line,
        )

class QuantisationRegionValidator(StyleElementValidator):
  '''Validates the properties of the `_r_quantisationregion` style'''

  permitted_styles = frozenset((
    style_attrs.Origin,
    style_attrs.Extent,
    style_attrs.FontSize,
    style_attrs.LineHeight,
  ))

  def validate(self, style_id: str, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(style_id, values, line, event_handler)
    value = values.get(style_attrs.Origin.qname)
    if value is None:
      event_handler.error("Attribute origin is required on style `%s` (line %s)", style_id, line)
    elif not _PERCENT_PAIR.match(value):
      event_handler.error("Attribute origin of style `%s` shall be a pair of percentages (line %s)", style_id, line)
    value = values.get(style_attrs.Extent.qname)
    if value is None:
      event_handler.error("Attribute extent is required on style `%s` (line %s)", style_id, line)
    elif not _PERCENT_PAIR.match(value):
      event_handler.error("Attribute extent of style `%s` shall be a pair of percentages (line %s)", style_id, line)
    value = values.get(style_attrs.FontSize.qname)
    if value is None:
      event_handler.error("Attribute fontSize is required on style `%s` (line %s)", style_id, line)
    elif not _RH.match(value):
      event_handler.error("Attribute fontSize of style `%s` shall be a length in `rh` units (line %s)", style_id, line)
    value = values.get(style_attrs.LineHeight.qname)
    if value is None:
      event_handler.error("Attribute lineHeight is required on style `%s` (line %s)", style_id, line)
    elif not _PERCENT.match(value):
      event_handler.error("Attribute lineHeight of style `%s` shall be a percentage (line %s)", style_id, line)

class FixedRegionValidator(StyleElementValidator):
  '''Validates the properties of the `r_default` style, and that it references `_r_default`'''

  permitted_styles = frozenset((
    other_attrs.StyleAttribute,
    style_attrs.Overflow,
    style_attrs.BackgroundColor,
    style_attrs.ShowBackground,
    style_attrs.FontStyle,
    style_attrs.FontWeight,
    style_attrs.FontFamily,
    style_attrs.WrapOption,
  ))

  def validate(self, style_id: str, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(style_id, values, line, event_handler)
    value = values.get(style_attrs.Overflow.qname)
    if value is None:
      event_handler.error("Attribute overflow is required on style `%s` (line %s)", style_id, line)
    elif value != ttconv_styles.OverflowType.visible.value:
      event_handler.error("Attribute overflow of style `%s` shall be `visible` (line %s)", style_id, line)
    value = values.get(style_attrs.BackgroundColor.qname)
    if value is None:
      event_handler.error("Attribute backgroundColor is required on style `%s` (line %s)", style_id, line)
    elif value != "#00000000":
      event_handler.error("Attribute backgroundColor of style `%s` shall be `#00000000` (line %s)", style_id, line)
    value = values.get(style_attrs.ShowBackground.qname)
    if value is None:
      event_handler.error("Attribute showBackground is required on style `%s` (line %s)", style_id, line)
    elif value != ttconv_styles.ShowBackgroundType.whenActive.value:
      event_handler.error("Attribute showBackground of style `%s` shall be `whenActive` (line %s)", style_id, line)
    value = values.get(style_attrs.FontStyle.qname)
    if value is None:
      event_handler.error("Attribute fontStyle is required on style `%s` (line %s)", style_id, line)
    elif value != ttconv_styles.FontStyleType.normal.value:
      event_handler.error("Attribute fontStyle of style `%s` shall be `normal` (line %s)", style_id, line)
    value = values.get(style_attrs.FontWeight.qname)
    if value is None:
      event_handler.error("Attribute fontWeight is required on style `%s` (line %s)", style_id, line)
    elif value != ttconv_styles.FontWeightType.normal.value:
      event_handler.error("Attribute fontWeight of style `%s` shall be `normal` (line %s)", style_id, line)
    value = values.get(style_attrs.FontFamily.qname)
    if value is None:
      event_handler.error("Attribute fontFamily is required on style `%s` (line %s)", style_id, line)
    elif value != ttconv_styles.GenericFontFamilyType.proportionalSansSerif.value:
      event_handler.error("Attribute fontFamily of style `%s` shall be `proportionalSansSerif` (line %s)", style_id, line)
    value = values.get(style_attrs.WrapOption.qname)
    if value is None:
      event_handler.error("Attribute wrapOption is required on style `%s` (line %s)", style_id, line)
    elif value != ttconv_styles.WrapOptionType.noWrap.value:
      event_handler.error("Attribute wrapOption of style `%s` shall be `noWrap` (line %s)", style_id, line)
    value = values.get(other_attrs.StyleAttribute.qname)
    if value is None:
      event_handler.error("Attribute style is required on style `%s` (line %s)", style_id, line)
    elif value != "_r_default":
      event_handler.error("Attribute style of style `%s` shall be `_r_default` (line %s)", style_id, line)

class VerticalRegionValidator(StyleElementValidator):
  '''Validates the properties of the `r_vertical` style, and that it references `_r_vertical`'''

  permitted_styles = frozenset((other_attrs.StyleAttribute, style_attrs.WritingMode))

  def validate(self, style_id: str, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(style_id, values, line, event_handler)
    value = values.get(style_attrs.WritingMode.qname)
    if value is None:
      event_handler.error("Attribute writingMode is required on style `%s` (line %s)", style_id, line)
    elif value != ttconv_styles.WritingModeType.tbrl.value:
      event_handler.error("Attribute writingMode of style `%s` shall be `tbrl` (line %s)", style_id, line)
    value = values.get(other_attrs.StyleAttribute.qname)
    if value is None:
      event_handler.error("Attribute style is required on style `%s` (line %s)", style_id, line)
    elif value != "_r_vertical":
      event_handler.error("Attribute style of style `%s` shall be `_r_vertical` (line %s)", style_id, line)

class FillGapValidator(SinglePropertyValidator):
  '''Validates the properties of the `d_fillgap` style'''

  attribute = style_attrs.FillLineGap
  expected = "true"
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class ForcedValidator(SinglePropertyValidator):
  '''Validates the properties of the `d_forced` style'''

  attribute = style_attrs.ForcedDisplay
  expected = "true"
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class RTLValidator(SinglePropertyValidator):
  '''Validates the properties of the `p_rtl` style'''

  attribute = style_attrs.Direction
  expected = ttconv_styles.DirectionType.rtl.value
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class PAlignmentValidator(StyleElementValidator):
  '''Validates the `p_al_xxx` styles, which specify the alignment of a paragraph and of its rows'''

  permitted_styles = frozenset((style_attrs.MultiRowAlign, style_attrs.TextAlign))

  def __init__(self, text_align: ttconv_styles.TextAlignType, multi_row_align: ttconv_styles.MultiRowAlignType):
    self._text_align = text_align.value
    self._multi_row_align = multi_row_align.value

  def validate(self, style_id: str, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(style_id, values, line, event_handler)
    value = values.get(style_attrs.MultiRowAlign.qname)
    if value is None:
      event_handler.error("Attribute multiRowAlign is required on style `%s` (line %s)", style_id, line)
    elif value != self._multi_row_align:
      event_handler.error("Attribute multiRowAlign of style `%s` shall be `%s` (line %s)", style_id, self._multi_row_align, line)
    value = values.get(style_attrs.TextAlign.qname)
    if value is None:
      event_handler.error("Attribute textAlign is required on style `%s` (line %s)", style_id, line)
    elif value != self._text_align:
      event_handler.error("Attribute textAlign of style `%s` shall be `%s` (line %s)", style_id, self._text_align, line)

class RubyReserveValidator(SinglePropertyValidator):
  '''Validates the properties of the `p_rb_res_outside` style'''

  attribute = style_attrs.RubyReserve
  expected = ttconv_styles.RubyReserveType.Position.outside.value
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class ShearValidator(SinglePropertyValidator):
  '''Validates the properties of the `p_shear` style'''

  attribute = style_attrs.Shear
  expected = "16.67%"
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class ItalicValidator(SinglePropertyValidator):
  '''Validates the properties of the `s_italic` style'''

  attribute = style_attrs.FontStyle
  expected = ttconv_styles.FontStyleType.italic.value
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class BoldValidator(SinglePropertyValidator):
  '''Validates the properties of the `s_bold` style'''

  attribute = style_attrs.FontWeight
  expected = ttconv_styles.FontWeightType.bold.value
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class UnderlineValidator(SinglePropertyValidator):
  '''Validates the properties of the `s_underline` style'''

  attribute = style_attrs.TextDecoration
  expected = "underline"
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class TextCombineValidator(SinglePropertyValidator):
  '''Validates the properties of the `s_combine` style'''

  attribute = style_attrs.TextCombine
  expected = ttconv_styles.TextCombineType.all.value
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class RubyBaseValidator(SinglePropertyValidator):
  '''Validates the properties of the `s_rb_b` style'''

  attribute = style_attrs.Ruby
  expected = "base"
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class RubyTextValidator(SinglePropertyValidator):
  '''Validates the properties of the `s_rb_t` style'''

  attribute = style_attrs.Ruby
  expected = "text"
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class RubyContainerAlignValidator(StyleElementValidator):
  '''Validates the `s_rb_algn_xxx` styles'''

  permitted_styles = frozenset((style_attrs.Ruby, style_attrs.RubyAlign))

  def __init__(self, ruby_align: ttconv_styles.RubyAlignType):
    self._ruby_align = ruby_align.value

  def validate(self, style_id: str, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(style_id, values, line, event_handler)
    value = values.get(style_attrs.Ruby.qname)
    if value is None:
      event_handler.error("Attribute ruby is required on style `%s` (line %s)", style_id, line)
    elif value != "container":
      event_handler.error("Attribute ruby of style `%s` shall be `container` (line %s)", style_id, line)
    value = values.get(style_attrs.RubyAlign.qname)
    if value is None:
      event_handler.error("Attribute rubyAlign is required on style `%s` (line %s)", style_id, line)
    elif value != self._ruby_align:
      event_handler.error("Attribute rubyAlign of style `%s` shall be `%s` (line %s)", style_id, self._ruby_align, line)

class RubyContainerPositionValidator(StyleElementValidator):
  '''Validates the `s_rb_posn_xxx` styles'''

  permitted_styles = frozenset((style_attrs.Ruby, style_attrs.RubyPosition))

  def __init__(self, position: ttconv_styles.AnnotationPositionType):
    self._position = position.value

  def validate(self, style_id: str, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(style_id, values, line, event_handler)
    value = values.get(style_attrs.Ruby.qname)
    if value is None:
      event_handler.error("Attribute ruby is required on style `%s` (line %s)", style_id, line)
    elif value != "container":
      event_handler.error("Attribute ruby of style `%s` shall be `container` (line %s)", style_id, line)
    value = values.get(style_attrs.RubyPosition.qname)
    if value is None:
      event_handler.error("Attribute rubyPosition is required on style `%s` (line %s)", style_id, line)
    elif value != self._position:
      event_handler.error("Attribute rubyPosition of style `%s` shall be `%s` (line %s)", style_id, self._position, line)

class TextEmphasisValidator(SinglePropertyValidator):
  '''Validates the `s_emf_xxx` styles, which emphasize text with a mark placed outside the text'''

  attribute = style_attrs.TextEmphasis

  def __init__(self, mark: ttconv_styles.TextEmphasisType.Style):
    self._expected = f"{mark.value} {ttconv_styles.TextEmphasisType.Position.outside.value}"

  @property
  def description(self) -> str:
    return f"`{self._expected}`"

  def check(self, value: str) -> bool:
    return value == self._expected

# Validators of the `style` attribute of a style, which references other styles

class ReferentialStylingValidator(StyleElementValidator):
  '''Validates that a style references exactly the style `referenced_id`'''

  permitted_styles = frozenset((other_attrs.StyleAttribute,))

  def __init__(self, referenced_id: str):
    self._referenced_id = referenced_id

  def validate(self, style_id: str, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(style_id, values, line, event_handler)
    value = values.get(other_attrs.StyleAttribute.qname)
    if value is None:
      event_handler.error("Attribute style is required on style `%s` (line %s)", style_id, line)
    elif value != self._referenced_id:
      event_handler.error("Attribute style of style `%s` shall be `%s` (line %s)", style_id, self._referenced_id, line)

# styles that may be referenced by `_d_default`
DIV_MODIFIER_STYLES = frozenset(("d_fillgap", "d_forced", "d_outline", "d_drop", "d_none"))

class DivModifiersReferenceValidator(StyleElementValidator):
  '''Validates that a style, if it references styles, references zero or more of `DIV_MODIFIER_STYLES`, without repetition'''

  permitted_styles = frozenset((other_attrs.StyleAttribute,))

  def validate(self, style_id: str, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(style_id, values, line, event_handler)
    value = values.get(other_attrs.StyleAttribute.qname)
    if value is not None:
      listed = value.split()
      if not (set(listed) <= DIV_MODIFIER_STYLES and len(set(listed)) == len(listed)):
        event_handler.error(
          "Attribute style of style `%s` shall be zero or more of %s, without repetition (line %s)",
          style_id, ", ".join(sorted(DIV_MODIFIER_STYLES)), line,
        )

class VerticalRegionReferenceValidator(StyleElementValidator):
  '''Validates that a style, if it references styles, references exactly one of `ALIGNMENT_STYLES`'''

  permitted_styles = frozenset((other_attrs.StyleAttribute,))

  def validate(self, style_id: str, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(style_id, values, line, event_handler)
    value = values.get(other_attrs.StyleAttribute.qname)
    if value is not None:
      listed = value.split()
      if not (len(listed) == 1 and listed[0] in ALIGNMENT_STYLES):
        event_handler.error(
          "Attribute style of style `%s` shall be at most one of %s (line %s)",
          style_id, ", ".join(sorted(ALIGNMENT_STYLES)), line,
        )

QUANTISATION_REGION_STYLE = "_r_quantisationregion"

STYLE_VALIDATORS: typing.Dict[str, typing.Any] = {
  # styles that may be modified

  "_d_default": DivModifiersReferenceValidator(),
  "_r_default": DefaultRegionValidator(),
  "_r_vertical": VerticalRegionReferenceValidator(),
  QUANTISATION_REGION_STYLE: QuantisationRegionValidator(),

  "p_font1": ParagraphFontValidator(),
  "p_font2": ParagraphFontValidator(),

  "s_fg_black": ColorValidator(),
  "s_fg_red": ColorValidator(),
  "s_fg_yellow": ColorValidator(),
  "s_fg_green": ColorValidator(),
  "s_fg_cyan": ColorValidator(),
  "s_fg_blue": ColorValidator(),
  "s_fg_magenta": ColorValidator(),
  "s_fg_white": ColorValidator(),

  "s_outlineblack": OutlineValidator(),
  "s_outlinered": OutlineValidator(),
  "s_outlineyellow": OutlineValidator(),
  "s_outlinegreen": OutlineValidator(),
  "s_outlinecyan": OutlineValidator(),
  "s_outlineblue": OutlineValidator(),
  "s_outlinemagenta": OutlineValidator(),
  "s_outlinewhite": OutlineValidator(),

  "s_dropblack": OutlineValidator(),
  "s_dropred": OutlineValidator(),
  "s_dropyellow": OutlineValidator(),
  "s_dropgreen": OutlineValidator(),
  "s_dropcyan": OutlineValidator(),
  "s_dropblue": OutlineValidator(),
  "s_dropmagenta": OutlineValidator(),
  "s_dropwhite": OutlineValidator(),

  "s_noneblack": NoOutlineValidator(),
  "s_nonered": NoOutlineValidator(),
  "s_noneyellow": NoOutlineValidator(),
  "s_nonegreen": NoOutlineValidator(),
  "s_nonecyan": NoOutlineValidator(),
  "s_noneblue": NoOutlineValidator(),
  "s_nonemagenta": NoOutlineValidator(),
  "s_nonewhite": NoOutlineValidator(),

  "ps_bg_boxedblack": BoxedBackgroundValidator(),
  "ps_bg_boxedred": BoxedBackgroundValidator(),
  "ps_bg_boxedyellow": BoxedBackgroundValidator(),
  "ps_bg_boxedgreen": BoxedBackgroundValidator(),
  "ps_bg_boxedcyan": BoxedBackgroundValidator(),
  "ps_bg_boxedblue": BoxedBackgroundValidator(),
  "ps_bg_boxedmagenta": BoxedBackgroundValidator(),
  "ps_bg_boxedwhite": BoxedBackgroundValidator(),

  "ps_bg_ghostboxedblack": GhostBoxedBackgroundValidator(),
  "ps_bg_ghostboxedred": GhostBoxedBackgroundValidator(),
  "ps_bg_ghostboxedyellow": GhostBoxedBackgroundValidator(),
  "ps_bg_ghostboxedgreen": GhostBoxedBackgroundValidator(),
  "ps_bg_ghostboxedcyan": GhostBoxedBackgroundValidator(),
  "ps_bg_ghostboxedblue": GhostBoxedBackgroundValidator(),
  "ps_bg_ghostboxedmagenta": GhostBoxedBackgroundValidator(),
  "ps_bg_ghostboxedwhite": GhostBoxedBackgroundValidator(),

  # styles that are fixed

  "r_default": FixedRegionValidator(),
  "r_vertical": VerticalRegionValidator(),

  "d_default": ReferentialStylingValidator("_d_default"),
  "d_fillgap": FillGapValidator(),
  "d_forced": ForcedValidator(),
  "d_outline": ReferentialStylingValidator("s_outlineblack"),
  "d_drop": ReferentialStylingValidator("s_dropblack"),
  "d_none": ReferentialStylingValidator("s_noneblack"),

  "p_rtl": RTLValidator(),

  "p_al_start": PAlignmentValidator(ttconv_styles.TextAlignType.start, ttconv_styles.MultiRowAlignType.start),
  "p_al_end": PAlignmentValidator(ttconv_styles.TextAlignType.end, ttconv_styles.MultiRowAlignType.end),
  "p_al_center": PAlignmentValidator(ttconv_styles.TextAlignType.center, ttconv_styles.MultiRowAlignType.center),
  "p_al_start_center": PAlignmentValidator(ttconv_styles.TextAlignType.start, ttconv_styles.MultiRowAlignType.center),
  "p_al_start_end": PAlignmentValidator(ttconv_styles.TextAlignType.start, ttconv_styles.MultiRowAlignType.end),
  "p_al_end_start": PAlignmentValidator(ttconv_styles.TextAlignType.end, ttconv_styles.MultiRowAlignType.start),
  "p_al_end_center": PAlignmentValidator(ttconv_styles.TextAlignType.end, ttconv_styles.MultiRowAlignType.center),
  "p_al_center_start": PAlignmentValidator(ttconv_styles.TextAlignType.center, ttconv_styles.MultiRowAlignType.start),
  "p_al_center_end": PAlignmentValidator(ttconv_styles.TextAlignType.center, ttconv_styles.MultiRowAlignType.end),

  "p_rb_res_outside": RubyReserveValidator(),
  "p_shear": ShearValidator(),

  "s_italic": ItalicValidator(),
  "s_bold": BoldValidator(),
  "s_underline": UnderlineValidator(),
  "s_combine": TextCombineValidator(),

  "s_rb_b": RubyBaseValidator(),
  "s_rb_t": RubyTextValidator(),
  "s_rb_algn_center": RubyContainerAlignValidator(ttconv_styles.RubyAlignType.center),
  "s_rb_algn_around": RubyContainerAlignValidator(ttconv_styles.RubyAlignType.spaceAround),
  "s_rb_posn_outside": RubyContainerPositionValidator(ttconv_styles.AnnotationPositionType.outside),

  "s_emf_fco": TextEmphasisValidator(ttconv_styles.TextEmphasisType.Style.filled_circle),
  "s_emf_fdo": TextEmphasisValidator(ttconv_styles.TextEmphasisType.Style.filled_dot),
  "s_emf_fso": TextEmphasisValidator(ttconv_styles.TextEmphasisType.Style.filled_sesame),
  "s_emf_oco": TextEmphasisValidator(ttconv_styles.TextEmphasisType.Style.open_circle),
  "s_emf_odo": TextEmphasisValidator(ttconv_styles.TextEmphasisType.Style.open_dot),
  "s_emf_oso": TextEmphasisValidator(ttconv_styles.TextEmphasisType.Style.open_sesame),
}
