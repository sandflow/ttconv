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

class StyleSpecification:
  '''Specifies a style, and validates the attributes of a style element that defines it. Subclasses override `validate()`,
  and shall call `super().validate()`.'''

  # `xml:id` of the style.
  style_id: str

  # attributes that the style may specify, each identified by its class
  permitted_styles: typing.AbstractSet[typing.Any]

  # `div` style that shall be in effect when a `span` references the style, if any
  required_div_style: typing.Optional[typing.Type[StyleSpecification]] = None

  # specification of each style, indexed by `style_id`
  _registry: typing.Dict[str, StyleSpecification] = {}

  def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)
    # concrete styles only, not the intermediate family classes
    if "style_id" in cls.__dict__:
      if cls.style_id in StyleSpecification._registry:
        raise ValueError(f"Style `{cls.style_id}` is specified more than once")
      StyleSpecification._registry[cls.style_id] = cls()

  @staticmethod
  def get(style_id: str) -> typing.Optional[StyleSpecification]:
    '''Returns the specification of the style whose `xml:id` is `style_id`, or `None` if there is none'''
    return StyleSpecification._registry.get(style_id)

  @staticmethod
  def style_ids() -> typing.AbstractSet[str]:
    '''Returns the `xml:id` of every style that is specified'''
    return StyleSpecification._registry.keys()

  def validate(self, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    '''Reports each attribute in `values` that the style shall not specify, i.e., that is not one of `permitted_styles`, to
    `event_handler`.

    `line` is the line number of the style element, and `values` are the attributes that it specifies, other than `xml:id`, as a
    mapping of their qualified name to their value.'''
    permitted_qnames = {attr.qname for attr in self.permitted_styles}
    for qname in values:
      if qname not in permitted_qnames:
        event_handler.error("Attribute %s is not permitted on style `%s` (line %s)", qname.local_name, self.style_id, line)

class SinglePropertySpecification(StyleSpecification):
  '''Specifies a style that specifies a single style property, e.g., `tts:color`, whose value shall satisfy `check()`.
  Subclasses set `attribute` and `description`, and override `check()`.'''

  # class in `style_attributes` of the property
  attribute: typing.Any

  # whether the style shall specify the property
  required = True

  # describes the values that satisfy `check()`, e.g., "a percentage"
  description: str

  def __init__(self):
    self.permitted_styles = frozenset((self.attribute,))

  def check(self, value: str) -> bool:
    '''Returns whether `value` is valid'''
    raise NotImplementedError

  def validate(self, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(values, line, event_handler)
    name = self.attribute.qname.local_name
    value = values.get(self.attribute.qname)
    if value is None:
      if self.required:
        event_handler.error("Attribute %s is required on style `%s` (line %s)", name, self.style_id, line)
    elif not self.check(value):
      event_handler.error("Attribute %s of style `%s` shall be %s (line %s)", name, self.style_id, self.description, line)

_HEX6 = re.compile(r"^#[0-9A-F]{6}$")
_HEX8 = re.compile(r"^#[0-9A-F]{8}$")
_OUTLINE_RE = re.compile(r"^#[0-9A-F]{6} 0\.05em$")

class ColorSpecification(SinglePropertySpecification):
  '''Specifies the `s_fg_xxx` styles. Colors may be adjusted, e.g., to change the shade of yellow, but not the color family.'''

  attribute = style_attrs.Color
  description = "a color in `#RRGGBB` notation using upper case hex digits"

  def check(self, value: str) -> bool:
    return _HEX6.match(value) is not None

class OutlineSpecification(SinglePropertySpecification):
  '''Specifies the `s_outlinexxx` and `s_dropxxx` styles'''

  attribute = style_attrs.TextOutline
  description = "`#RRGGBB 0.05em` using upper case hex digits"

  def check(self, value: str) -> bool:
    return _OUTLINE_RE.match(value) is not None

class SOutlineSpecification(OutlineSpecification):
  '''Specifies the `s_outlinexxx` styles'''

class SDropSpecification(OutlineSpecification):
  '''Specifies the `s_dropxxx` styles'''

class NoOutlineSpecification(SinglePropertySpecification):
  '''Specifies the `s_nonexxx` styles'''

  attribute = style_attrs.TextOutline
  # tts:textOutline was added to s_nonexxx after the initial revision of the specification
  required = False
  expected = ttconv_styles.SpecialValues.none.value
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class BoxedBackgroundSpecification(SinglePropertySpecification):
  '''Specifies the `ps_bg_boxedxxx` styles'''

  attribute = style_attrs.BackgroundColor
  description = "a color in `#RRGGBB` notation using upper case hex digits"

  def check(self, value: str) -> bool:
    return _HEX6.match(value) is not None

class GhostBoxedBackgroundSpecification(SinglePropertySpecification):
  '''Specifies the `ps_bg_ghostboxedxxx` styles'''

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

class ParagraphFontSpecification(StyleSpecification):
  '''Specifies the `p_font1` and `p_font2` styles. `tts:fontFamily` may be omitted and has any value.'''

  permitted_styles = frozenset((style_attrs.FontSize, style_attrs.LineHeight, style_attrs.FontFamily))

  def validate(self, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(values, line, event_handler)
    value = values.get(style_attrs.FontSize.qname)
    if value is None:
      event_handler.error("Attribute fontSize is required on style `%s` (line %s)", self.style_id, line)
    elif not _PERCENT.match(value):
      event_handler.error("Attribute fontSize of style `%s` shall be a percentage (line %s)", self.style_id, line)
    value = values.get(style_attrs.LineHeight.qname)
    if value is None:
      event_handler.error("Attribute lineHeight is required on style `%s` (line %s)", self.style_id, line)
    elif not _PERCENT.match(value):
      event_handler.error("Attribute lineHeight of style `%s` shall be a percentage (line %s)", self.style_id, line)

class PAlignmentSpecification(StyleSpecification):
  '''Specifies the `p_al_xxx` styles, which specify the alignment of a paragraph and of its rows'''

  permitted_styles = frozenset((style_attrs.MultiRowAlign, style_attrs.TextAlign))
  text_align: ttconv_styles.TextAlignType
  multi_row_align: ttconv_styles.MultiRowAlignType

  def validate(self, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(values, line, event_handler)
    value = values.get(style_attrs.MultiRowAlign.qname)
    if value is None:
      event_handler.error("Attribute multiRowAlign is required on style `%s` (line %s)", self.style_id, line)
    elif value != self.multi_row_align.value:
      event_handler.error("Attribute multiRowAlign of style `%s` shall be `%s` (line %s)", self.style_id, self.multi_row_align.value, line)
    value = values.get(style_attrs.TextAlign.qname)
    if value is None:
      event_handler.error("Attribute textAlign is required on style `%s` (line %s)", self.style_id, line)
    elif value != self.text_align.value:
      event_handler.error("Attribute textAlign of style `%s` shall be `%s` (line %s)", self.style_id, self.text_align.value, line)

class RubyContainerAlignSpecification(StyleSpecification):
  '''Specifies the `s_rb_algn_xxx` styles'''

  permitted_styles = frozenset((style_attrs.Ruby, style_attrs.RubyAlign))
  ruby_align: ttconv_styles.RubyAlignType

  def validate(self, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(values, line, event_handler)
    value = values.get(style_attrs.Ruby.qname)
    if value is None:
      event_handler.error("Attribute ruby is required on style `%s` (line %s)", self.style_id, line)
    elif value != "container":
      event_handler.error("Attribute ruby of style `%s` shall be `container` (line %s)", self.style_id, line)
    value = values.get(style_attrs.RubyAlign.qname)
    if value is None:
      event_handler.error("Attribute rubyAlign is required on style `%s` (line %s)", self.style_id, line)
    elif value != self.ruby_align.value:
      event_handler.error("Attribute rubyAlign of style `%s` shall be `%s` (line %s)", self.style_id, self.ruby_align.value, line)

class TextEmphasisSpecification(SinglePropertySpecification):
  '''Specifies the `s_emf_xxx` styles, which emphasize text with a mark placed outside the text'''

  attribute = style_attrs.TextEmphasis
  mark: ttconv_styles.TextEmphasisType.Style

  def __init__(self):
    super().__init__()
    self.expected = f"{self.mark.value} {ttconv_styles.TextEmphasisType.Position.outside.value}"
    self.description = f"`{self.expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class ReferentialStylingSpecification(StyleSpecification):
  '''Specifies a style that references exactly the style `referenced_style`'''

  permitted_styles = frozenset((other_attrs.StyleAttribute,))
  referenced_style: typing.Type[StyleSpecification]

  def validate(self, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(values, line, event_handler)
    value = values.get(other_attrs.StyleAttribute.qname)
    if value is None:
      event_handler.error("Attribute style is required on style `%s` (line %s)", self.style_id, line)
    elif value != self.referenced_style.style_id:
      event_handler.error("Attribute style of style `%s` shall be `%s` (line %s)", self.style_id, self.referenced_style.style_id, line)

class BaseRVertical(StyleSpecification):
  '''Specifies the `_r_vertical` style, which, if it references styles, references exactly one of `ALIGNMENT_STYLES`'''

  style_id = "_r_vertical"
  permitted_styles = frozenset((other_attrs.StyleAttribute,))

  def validate(self, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(values, line, event_handler)
    value = values.get(other_attrs.StyleAttribute.qname)
    if value is not None:
      alignment_ids = {spec.style_id for spec in ALIGNMENT_STYLES}
      listed = value.split()
      if not (len(listed) == 1 and listed[0] in alignment_ids):
        event_handler.error(
          "Attribute style of style `%s` shall be at most one of %s (line %s)",
          self.style_id, ", ".join(sorted(alignment_ids)), line,
        )

class RQuantisationregion(StyleSpecification):
  '''Specifies the `_r_quantisationregion` style'''

  style_id = "_r_quantisationregion"
  permitted_styles = frozenset((
    style_attrs.Origin,
    style_attrs.Extent,
    style_attrs.FontSize,
    style_attrs.LineHeight,
  ))

  def validate(self, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(values, line, event_handler)
    value = values.get(style_attrs.Origin.qname)
    if value is None:
      event_handler.error("Attribute origin is required on style `%s` (line %s)", self.style_id, line)
    elif not _PERCENT_PAIR.match(value):
      event_handler.error("Attribute origin of style `%s` shall be a pair of percentages (line %s)", self.style_id, line)
    value = values.get(style_attrs.Extent.qname)
    if value is None:
      event_handler.error("Attribute extent is required on style `%s` (line %s)", self.style_id, line)
    elif not _PERCENT_PAIR.match(value):
      event_handler.error("Attribute extent of style `%s` shall be a pair of percentages (line %s)", self.style_id, line)
    value = values.get(style_attrs.FontSize.qname)
    if value is None:
      event_handler.error("Attribute fontSize is required on style `%s` (line %s)", self.style_id, line)
    elif not _RH.match(value):
      event_handler.error("Attribute fontSize of style `%s` shall be a length in `rh` units (line %s)", self.style_id, line)
    value = values.get(style_attrs.LineHeight.qname)
    if value is None:
      event_handler.error("Attribute lineHeight is required on style `%s` (line %s)", self.style_id, line)
    elif not _PERCENT.match(value):
      event_handler.error("Attribute lineHeight of style `%s` shall be a percentage (line %s)", self.style_id, line)

class PFont1(ParagraphFontSpecification):
  style_id = "p_font1"

class PFont2(ParagraphFontSpecification):
  style_id = "p_font2"

class SFgBlack(ColorSpecification):
  style_id = "s_fg_black"

class SFgRed(ColorSpecification):
  style_id = "s_fg_red"

class SFgYellow(ColorSpecification):
  style_id = "s_fg_yellow"

class SFgGreen(ColorSpecification):
  style_id = "s_fg_green"

class SFgCyan(ColorSpecification):
  style_id = "s_fg_cyan"

class SFgBlue(ColorSpecification):
  style_id = "s_fg_blue"

class SFgMagenta(ColorSpecification):
  style_id = "s_fg_magenta"

class SFgWhite(ColorSpecification):
  style_id = "s_fg_white"

class SOutlineBlack(SOutlineSpecification):
  style_id = "s_outlineblack"

class SOutlineRed(SOutlineSpecification):
  style_id = "s_outlinered"

class SOutlineYellow(SOutlineSpecification):
  style_id = "s_outlineyellow"

class SOutlineGreen(SOutlineSpecification):
  style_id = "s_outlinegreen"

class SOutlineCyan(SOutlineSpecification):
  style_id = "s_outlinecyan"

class SOutlineBlue(SOutlineSpecification):
  style_id = "s_outlineblue"

class SOutlineMagenta(SOutlineSpecification):
  style_id = "s_outlinemagenta"

class SOutlineWhite(SOutlineSpecification):
  style_id = "s_outlinewhite"

class SDropBlack(SDropSpecification):
  style_id = "s_dropblack"

class SDropRed(SDropSpecification):
  style_id = "s_dropred"

class SDropYellow(SDropSpecification):
  style_id = "s_dropyellow"

class SDropGreen(SDropSpecification):
  style_id = "s_dropgreen"

class SDropCyan(SDropSpecification):
  style_id = "s_dropcyan"

class SDropBlue(SDropSpecification):
  style_id = "s_dropblue"

class SDropMagenta(SDropSpecification):
  style_id = "s_dropmagenta"

class SDropWhite(SDropSpecification):
  style_id = "s_dropwhite"

class SNoneBlack(NoOutlineSpecification):
  style_id = "s_noneblack"

class SNoneRed(NoOutlineSpecification):
  style_id = "s_nonered"

class SNoneYellow(NoOutlineSpecification):
  style_id = "s_noneyellow"

class SNoneGreen(NoOutlineSpecification):
  style_id = "s_nonegreen"

class SNoneCyan(NoOutlineSpecification):
  style_id = "s_nonecyan"

class SNoneBlue(NoOutlineSpecification):
  style_id = "s_noneblue"

class SNoneMagenta(NoOutlineSpecification):
  style_id = "s_nonemagenta"

class SNoneWhite(NoOutlineSpecification):
  style_id = "s_nonewhite"

class DOutline(ReferentialStylingSpecification):
  style_id = "d_outline"
  referenced_style = SOutlineBlack

class DDrop(ReferentialStylingSpecification):
  style_id = "d_drop"
  referenced_style = SDropBlack

class DNone(ReferentialStylingSpecification):
  style_id = "d_none"
  referenced_style = SNoneBlack

# assigned here since the `div` styles reference the `span` styles above
SOutlineSpecification.required_div_style = DOutline
SDropSpecification.required_div_style = DDrop
NoOutlineSpecification.required_div_style = DNone

class PsBgBoxedBlack(BoxedBackgroundSpecification):
  style_id = "ps_bg_boxedblack"

class PsBgBoxedRed(BoxedBackgroundSpecification):
  style_id = "ps_bg_boxedred"

class PsBgBoxedYellow(BoxedBackgroundSpecification):
  style_id = "ps_bg_boxedyellow"

class PsBgBoxedGreen(BoxedBackgroundSpecification):
  style_id = "ps_bg_boxedgreen"

class PsBgBoxedCyan(BoxedBackgroundSpecification):
  style_id = "ps_bg_boxedcyan"

class PsBgBoxedBlue(BoxedBackgroundSpecification):
  style_id = "ps_bg_boxedblue"

class PsBgBoxedMagenta(BoxedBackgroundSpecification):
  style_id = "ps_bg_boxedmagenta"

class PsBgBoxedWhite(BoxedBackgroundSpecification):
  style_id = "ps_bg_boxedwhite"

class PsBgGhostBoxedBlack(GhostBoxedBackgroundSpecification):
  style_id = "ps_bg_ghostboxedblack"

class PsBgGhostBoxedRed(GhostBoxedBackgroundSpecification):
  style_id = "ps_bg_ghostboxedred"

class PsBgGhostBoxedYellow(GhostBoxedBackgroundSpecification):
  style_id = "ps_bg_ghostboxedyellow"

class PsBgGhostBoxedGreen(GhostBoxedBackgroundSpecification):
  style_id = "ps_bg_ghostboxedgreen"

class PsBgGhostBoxedCyan(GhostBoxedBackgroundSpecification):
  style_id = "ps_bg_ghostboxedcyan"

class PsBgGhostBoxedBlue(GhostBoxedBackgroundSpecification):
  style_id = "ps_bg_ghostboxedblue"

class PsBgGhostBoxedMagenta(GhostBoxedBackgroundSpecification):
  style_id = "ps_bg_ghostboxedmagenta"

class PsBgGhostBoxedWhite(GhostBoxedBackgroundSpecification):
  style_id = "ps_bg_ghostboxedwhite"

class RDefault(StyleSpecification):
  '''Specifies the `r_default` style, which references `_r_default`'''

  style_id = "r_default"
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

  def validate(self, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(values, line, event_handler)
    value = values.get(style_attrs.Overflow.qname)
    if value is None:
      event_handler.error("Attribute overflow is required on style `%s` (line %s)", self.style_id, line)
    elif value != ttconv_styles.OverflowType.visible.value:
      event_handler.error("Attribute overflow of style `%s` shall be `visible` (line %s)", self.style_id, line)
    value = values.get(style_attrs.BackgroundColor.qname)
    if value is None:
      event_handler.error("Attribute backgroundColor is required on style `%s` (line %s)", self.style_id, line)
    elif value != "#00000000":
      event_handler.error("Attribute backgroundColor of style `%s` shall be `#00000000` (line %s)", self.style_id, line)
    value = values.get(style_attrs.ShowBackground.qname)
    if value is None:
      event_handler.error("Attribute showBackground is required on style `%s` (line %s)", self.style_id, line)
    elif value != ttconv_styles.ShowBackgroundType.whenActive.value:
      event_handler.error("Attribute showBackground of style `%s` shall be `whenActive` (line %s)", self.style_id, line)
    value = values.get(style_attrs.FontStyle.qname)
    if value is None:
      event_handler.error("Attribute fontStyle is required on style `%s` (line %s)", self.style_id, line)
    elif value != ttconv_styles.FontStyleType.normal.value:
      event_handler.error("Attribute fontStyle of style `%s` shall be `normal` (line %s)", self.style_id, line)
    value = values.get(style_attrs.FontWeight.qname)
    if value is None:
      event_handler.error("Attribute fontWeight is required on style `%s` (line %s)", self.style_id, line)
    elif value != ttconv_styles.FontWeightType.normal.value:
      event_handler.error("Attribute fontWeight of style `%s` shall be `normal` (line %s)", self.style_id, line)
    value = values.get(style_attrs.FontFamily.qname)
    if value is None:
      event_handler.error("Attribute fontFamily is required on style `%s` (line %s)", self.style_id, line)
    elif value != ttconv_styles.GenericFontFamilyType.proportionalSansSerif.value:
      event_handler.error("Attribute fontFamily of style `%s` shall be `proportionalSansSerif` (line %s)", self.style_id, line)
    value = values.get(style_attrs.WrapOption.qname)
    if value is None:
      event_handler.error("Attribute wrapOption is required on style `%s` (line %s)", self.style_id, line)
    elif value != ttconv_styles.WrapOptionType.noWrap.value:
      event_handler.error("Attribute wrapOption of style `%s` shall be `noWrap` (line %s)", self.style_id, line)
    value = values.get(other_attrs.StyleAttribute.qname)
    if value is None:
      event_handler.error("Attribute style is required on style `%s` (line %s)", self.style_id, line)
    elif value != BaseRDefault.style_id:
      event_handler.error("Attribute style of style `%s` shall be `_r_default` (line %s)", self.style_id, line)

class RVertical(StyleSpecification):
  '''Specifies the `r_vertical` style, which references `_r_vertical`'''

  style_id = "r_vertical"
  permitted_styles = frozenset((other_attrs.StyleAttribute, style_attrs.WritingMode))

  def validate(self, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(values, line, event_handler)
    value = values.get(style_attrs.WritingMode.qname)
    if value is None:
      event_handler.error("Attribute writingMode is required on style `%s` (line %s)", self.style_id, line)
    elif value != ttconv_styles.WritingModeType.tbrl.value:
      event_handler.error("Attribute writingMode of style `%s` shall be `tbrl` (line %s)", self.style_id, line)
    value = values.get(other_attrs.StyleAttribute.qname)
    if value is None:
      event_handler.error("Attribute style is required on style `%s` (line %s)", self.style_id, line)
    elif value != BaseRVertical.style_id:
      event_handler.error("Attribute style of style `%s` shall be `_r_vertical` (line %s)", self.style_id, line)

class DFillgap(SinglePropertySpecification):
  '''Specifies the `d_fillgap` style'''

  style_id = "d_fillgap"
  attribute = style_attrs.FillLineGap
  expected = "true"
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class DForced(SinglePropertySpecification):
  '''Specifies the `d_forced` style'''

  style_id = "d_forced"
  attribute = style_attrs.ForcedDisplay
  expected = "true"
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class BaseDDefault(StyleSpecification):
  '''Specifies the `_d_default` style, which, if it references styles, references zero or more of `DIV_MODIFIER_STYLES`,
  without repetition'''

  style_id = "_d_default"
  permitted_styles = frozenset((other_attrs.StyleAttribute,))

  # styles that may be referenced by `_d_default`
  _DIV_MODIFIER_STYLES = frozenset((DFillgap, DForced, DOutline, DDrop, DNone))

  def validate(self, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(values, line, event_handler)
    value = values.get(other_attrs.StyleAttribute.qname)
    if value is not None:
      div_modifier_ids = {spec.style_id for spec in self._DIV_MODIFIER_STYLES}
      listed = value.split()
      if not (set(listed) <= div_modifier_ids and len(set(listed)) == len(listed)):
        event_handler.error(
          "Attribute style of style `%s` shall be zero or more of %s, without repetition (line %s)",
          self.style_id, ", ".join(sorted(div_modifier_ids)), line,
        )

class DDefault(ReferentialStylingSpecification):
  style_id = "d_default"
  referenced_style = BaseDDefault

class PRtl(SinglePropertySpecification):
  '''Specifies the `p_rtl` style'''

  style_id = "p_rtl"
  attribute = style_attrs.Direction
  expected = ttconv_styles.DirectionType.rtl.value
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class PAlStart(PAlignmentSpecification):
  style_id = "p_al_start"
  text_align = ttconv_styles.TextAlignType.start
  multi_row_align = ttconv_styles.MultiRowAlignType.start

class PAlEnd(PAlignmentSpecification):
  style_id = "p_al_end"
  text_align = ttconv_styles.TextAlignType.end
  multi_row_align = ttconv_styles.MultiRowAlignType.end

class PAlCenter(PAlignmentSpecification):
  style_id = "p_al_center"
  text_align = ttconv_styles.TextAlignType.center
  multi_row_align = ttconv_styles.MultiRowAlignType.center

class PAlStartCenter(PAlignmentSpecification):
  style_id = "p_al_start_center"
  text_align = ttconv_styles.TextAlignType.start
  multi_row_align = ttconv_styles.MultiRowAlignType.center

class PAlStartEnd(PAlignmentSpecification):
  style_id = "p_al_start_end"
  text_align = ttconv_styles.TextAlignType.start
  multi_row_align = ttconv_styles.MultiRowAlignType.end

class PAlEndStart(PAlignmentSpecification):
  style_id = "p_al_end_start"
  text_align = ttconv_styles.TextAlignType.end
  multi_row_align = ttconv_styles.MultiRowAlignType.start

class PAlEndCenter(PAlignmentSpecification):
  style_id = "p_al_end_center"
  text_align = ttconv_styles.TextAlignType.end
  multi_row_align = ttconv_styles.MultiRowAlignType.center

class PAlCenterStart(PAlignmentSpecification):
  style_id = "p_al_center_start"
  text_align = ttconv_styles.TextAlignType.center
  multi_row_align = ttconv_styles.MultiRowAlignType.start

class PAlCenterEnd(PAlignmentSpecification):
  style_id = "p_al_center_end"
  text_align = ttconv_styles.TextAlignType.center
  multi_row_align = ttconv_styles.MultiRowAlignType.end

ALIGNMENT_STYLES = frozenset((
  PAlStart, PAlEnd, PAlCenter,
  PAlStartCenter, PAlStartEnd,
  PAlEndStart, PAlEndCenter,
  PAlCenterStart, PAlCenterEnd,
))

class BaseRDefault(StyleSpecification):
  '''Specifies the `_r_default` style, which references exactly one of `FOREGROUND_STYLES` and exactly one of
  `ALIGNMENT_STYLES`'''

  style_id = "_r_default"
  FOREGROUND_STYLES = frozenset((
    SFgBlack, SFgRed, SFgYellow, SFgGreen, SFgCyan, SFgBlue, SFgMagenta, SFgWhite,
  ))
  permitted_styles = frozenset((
    other_attrs.StyleAttribute,
    style_attrs.FontSize,
    style_attrs.LineHeight,
    style_attrs.LinePadding,
    style_attrs.LuminanceGain,
    style_attrs.FillLineGap,
  ))

  def validate(self, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(values, line, event_handler)
    value = values.get(style_attrs.FontSize.qname)
    if value is None:
      event_handler.error("Attribute fontSize is required on style `%s` (line %s)", self.style_id, line)
    elif not _RH.match(value):
      event_handler.error("Attribute fontSize of style `%s` shall be a length in `rh` units (line %s)", self.style_id, line)
    value = values.get(style_attrs.LineHeight.qname)
    if value is None:
      event_handler.error("Attribute lineHeight is required on style `%s` (line %s)", self.style_id, line)
    elif not _PERCENT.match(value):
      event_handler.error("Attribute lineHeight of style `%s` shall be a percentage (line %s)", self.style_id, line)
    value = values.get(style_attrs.LinePadding.qname)
    if value is None:
      event_handler.error("Attribute linePadding is required on style `%s` (line %s)", self.style_id, line)
    elif not _CELLS.match(value):
      event_handler.error("Attribute linePadding of style `%s` shall be a length in `c` units (line %s)", self.style_id, line)
    value = values.get(style_attrs.LuminanceGain.qname)
    if value is None:
      event_handler.error("Attribute luminanceGain is required on style `%s` (line %s)", self.style_id, line)
    elif not _FLOAT.match(value):
      event_handler.error("Attribute luminanceGain of style `%s` shall be a number (line %s)", self.style_id, line)
    value = values.get(style_attrs.FillLineGap.qname)
    if value is None:
      event_handler.error("Attribute fillLineGap is required on style `%s` (line %s)", self.style_id, line)
    elif not _BOOLEAN.match(value):
      event_handler.error("Attribute fillLineGap of style `%s` shall be `true` or `false` (line %s)", self.style_id, line)
    value = values.get(other_attrs.StyleAttribute.qname)
    if value is None:
      event_handler.error("Attribute style is required on style `%s` (line %s)", self.style_id, line)
    else:
      foreground_ids = {spec.style_id for spec in self.FOREGROUND_STYLES}
      alignment_ids = {spec.style_id for spec in ALIGNMENT_STYLES}
      listed = value.split()
      if not (
        len(listed) == 2
        and sum(1 for s in listed if s in foreground_ids) == 1
        and sum(1 for s in listed if s in alignment_ids) == 1
      ):
        event_handler.error(
          "Attribute style of style `%s` shall be exactly one of %s and exactly one of %s (line %s)",
          self.style_id, ", ".join(sorted(foreground_ids)), ", ".join(sorted(alignment_ids)), line,
        )

class PRbResOutside(SinglePropertySpecification):
  '''Specifies the `p_rb_res_outside` style'''

  style_id = "p_rb_res_outside"
  attribute = style_attrs.RubyReserve
  expected = ttconv_styles.RubyReserveType.Position.outside.value
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class PShear(SinglePropertySpecification):
  '''Specifies the `p_shear` style'''

  style_id = "p_shear"
  attribute = style_attrs.Shear
  expected = "16.67%"
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class SItalic(SinglePropertySpecification):
  '''Specifies the `s_italic` style'''

  style_id = "s_italic"
  attribute = style_attrs.FontStyle
  expected = ttconv_styles.FontStyleType.italic.value
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class SBold(SinglePropertySpecification):
  '''Specifies the `s_bold` style'''

  style_id = "s_bold"
  attribute = style_attrs.FontWeight
  expected = ttconv_styles.FontWeightType.bold.value
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class SUnderline(SinglePropertySpecification):
  '''Specifies the `s_underline` style'''

  style_id = "s_underline"
  attribute = style_attrs.TextDecoration
  expected = "underline"
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class SCombine(SinglePropertySpecification):
  '''Specifies the `s_combine` style'''

  style_id = "s_combine"
  attribute = style_attrs.TextCombine
  expected = ttconv_styles.TextCombineType.all.value
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class SRbB(SinglePropertySpecification):
  '''Specifies the `s_rb_b` style'''

  style_id = "s_rb_b"
  attribute = style_attrs.Ruby
  expected = "base"
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class SRbT(SinglePropertySpecification):
  '''Specifies the `s_rb_t` style'''

  style_id = "s_rb_t"
  attribute = style_attrs.Ruby
  expected = "text"
  description = f"`{expected}`"

  def check(self, value: str) -> bool:
    return value == self.expected

class SRbAlgnCenter(RubyContainerAlignSpecification):
  style_id = "s_rb_algn_center"
  ruby_align = ttconv_styles.RubyAlignType.center

class SRbAlgnAround(RubyContainerAlignSpecification):
  style_id = "s_rb_algn_around"
  ruby_align = ttconv_styles.RubyAlignType.spaceAround

class SRbPosnOutside(StyleSpecification):
  '''Specifies the `s_rb_posn_outside` style'''

  style_id = "s_rb_posn_outside"
  permitted_styles = frozenset((style_attrs.Ruby, style_attrs.RubyPosition))
  position = ttconv_styles.AnnotationPositionType.outside

  def validate(self, values: typing.Mapping[QName, str], line: int, event_handler: EventHandler) -> None:
    super().validate(values, line, event_handler)
    value = values.get(style_attrs.Ruby.qname)
    if value is None:
      event_handler.error("Attribute ruby is required on style `%s` (line %s)", self.style_id, line)
    elif value != "container":
      event_handler.error("Attribute ruby of style `%s` shall be `container` (line %s)", self.style_id, line)
    value = values.get(style_attrs.RubyPosition.qname)
    if value is None:
      event_handler.error("Attribute rubyPosition is required on style `%s` (line %s)", self.style_id, line)
    elif value != self.position.value:
      event_handler.error("Attribute rubyPosition of style `%s` shall be `%s` (line %s)", self.style_id, self.position.value, line)

class SEmfFco(TextEmphasisSpecification):
  style_id = "s_emf_fco"
  mark = ttconv_styles.TextEmphasisType.Style.filled_circle

class SEmfFdo(TextEmphasisSpecification):
  style_id = "s_emf_fdo"
  mark = ttconv_styles.TextEmphasisType.Style.filled_dot

class SEmfFso(TextEmphasisSpecification):
  style_id = "s_emf_fso"
  mark = ttconv_styles.TextEmphasisType.Style.filled_sesame

class SEmfOco(TextEmphasisSpecification):
  style_id = "s_emf_oco"
  mark = ttconv_styles.TextEmphasisType.Style.open_circle

class SEmfOdo(TextEmphasisSpecification):
  style_id = "s_emf_odo"
  mark = ttconv_styles.TextEmphasisType.Style.open_dot

class SEmfOso(TextEmphasisSpecification):
  style_id = "s_emf_oso"
  mark = ttconv_styles.TextEmphasisType.Style.open_sesame
