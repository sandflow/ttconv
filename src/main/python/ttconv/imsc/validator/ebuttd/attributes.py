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

'''Attributes whose values are constrained by
[EBU Tech 3380 (EBU-TT-D)](https://tech.ebu.ch/publications/tech3380).
'''

from __future__ import annotations

from fractions import Fraction
import re
import typing

from ttconv.imsc.namespaces import QName
import ttconv.imsc.validator.other_attributes as other_attrs
import ttconv.imsc.validator.style_attributes as style_attrs
from ttconv.imsc.validator.font_helper import is_valid_font_families
import ttconv.style_properties as styles

# <whiteSpace> of Annex B
_WSP_RE = re.compile(r"[ \t\r\n]+")

# non-negative-number of Annex B, i.e., "5." is not permitted
_NON_NEG_NUMBER = r"(?:[0-9]+|[0-9]*\.[0-9]+)"

# ebuttdt:distributionLengthType
_LENGTH_RE = re.compile(rf"({_NON_NEG_NUMBER})%")

# ebuttdt:linePaddingType
_LINE_PADDING_RE = re.compile(rf"({_NON_NEG_NUMBER})c")

# ebuttdt:distributionColorType
_COLOR_RE = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{8})")

# ebuttdt:cellResolutionType
_CELL_RESOLUTION_RE = re.compile(r"[1-9][0-9]*[ \t\r\n]+[1-9][0-9]*")

# ebuttdt:distributionMediaTimingType
_MEDIA_TIMING_RE = re.compile(r"([0-9]{2,}):([0-5][0-9]):([0-5][0-9]|60)(?:\.([0-9]+))?")

def parse_pct_length(value: str) -> Fraction:
  '''Returns the number of percent in the `ebuttdt:distributionLengthType` `value`, or raises `ValueError`'''
  m = _LENGTH_RE.fullmatch(value)
  if m is None:
    raise ValueError(f"`{value}` is not a non-negative number followed by `%`")
  return Fraction(m.group(1))

def parse_media_time(value: str) -> Fraction:
  '''Returns the number of seconds denoted by the `ebuttdt:distributionMediaTimingType` `value`, or raises `ValueError`'''
  m = _MEDIA_TIMING_RE.fullmatch(value)
  if m is None:
    raise ValueError(f"`{value}` is not in `hours:minutes:seconds[.fraction]` format")
  hours, minutes, seconds, fraction = m.groups()
  return Fraction(int(hours) * 3600 + int(minutes) * 60 + int(seconds)) + \
    (Fraction(int(fraction), 10 ** len(fraction)) if fraction is not None else 0)

def _validate_enumeration(value: str, qname: QName, values: typing.Tuple[str, ...]):
  if value not in values:
    raise ValueError("%s shall be one of %s, not `%s`" % (qname.local_name, ", ".join(f"`{v}`" for v in values), value))

def _validate_color(value: str, qname: QName):
  if _COLOR_RE.fullmatch(value) is None:
    raise ValueError("%s shall be `#RRGGBB` or `#RRGGBBAA`, not `%s`" % (qname.local_name, value))

def _validate_pct_lengths(value: str, qname: QName):
  try:
    for component in _WSP_RE.split(value):
      parse_pct_length(component)
  except ValueError as e:
    raise ValueError("Bad %s value: %s" % (qname.local_name, e)) from e

# style properties of tt:style

class FontStyle(style_attrs.FontStyle):
  '''tts:fontStyle'''

  @staticmethod
  def validate(value: str, _ctx):
    _validate_enumeration(value, FontStyle.qname, (styles.FontStyleType.normal.value, styles.FontStyleType.italic.value))

class TextDecoration(style_attrs.TextDecoration):
  '''tts:textDecoration'''

  @staticmethod
  def validate(value: str, _ctx):
    _validate_enumeration(value, TextDecoration.qname, ("none", "underline"))

class Color(style_attrs.Color):
  '''ebuttdt:distributionColorType'''

  @staticmethod
  def validate(value: str, _ctx):
    _validate_color(value, Color.qname)

class BackgroundColor(style_attrs.BackgroundColor):
  '''ebuttdt:distributionColorType'''

  @staticmethod
  def validate(value: str, _ctx):
    _validate_color(value, BackgroundColor.qname)

class FontSize(style_attrs.FontSize):
  '''tts:fontSize'''

  @staticmethod
  def validate(value: str, _ctx):
    _validate_pct_lengths(value, FontSize.qname)

class FontFamily(style_attrs.FontFamily):
  '''ebuttdt:fontFamilyType'''

  @staticmethod
  def validate(value: str, _ctx):
    # unquoted names are either generic family names, all of which are permitted by TTML 1.0, or family names
    if not is_valid_font_families(value):
      raise ValueError("Bad tts:fontFamily value (%s)" % value)

class LineHeight(style_attrs.LineHeight):
  '''ebuttdt:distributionLineHeightType'''

  @staticmethod
  def validate(value: str, _ctx):
    if value == "normal":
      return
    try:
      parse_pct_length(value)
    except ValueError as e:
      raise ValueError("tts:lineHeight shall be `normal` or a percentage: %s" % e) from e

class LinePadding(style_attrs.LinePadding):
  '''ebuttdt:linePaddingType'''

  @staticmethod
  def validate(value: str, _ctx):
    if _LINE_PADDING_RE.fullmatch(value) is None:
      raise ValueError("ebutts:linePadding shall be a non-negative number followed by `c`, not `%s`" % value)

# style properties of tt:region

class Origin(style_attrs.Origin):
  '''tts:origin'''

  @staticmethod
  def validate(value: str, _ctx):
    _validate_pct_lengths(value, Origin.qname)

class Extent(style_attrs.Extent):
  '''tts:extent'''

  @staticmethod
  def validate(value: str, _ctx):
    _validate_pct_lengths(value, Extent.qname)

class Padding(style_attrs.Padding):
  '''tts:padding'''

  @staticmethod
  def validate(value: str, _ctx):
    _validate_pct_lengths(value, Padding.qname)

# non-style attributes

class TimeBase(other_attrs.TimeBaseAttribute):
  '''ttp:timeBase, which is always `media`'''

  @staticmethod
  def validate(value: str, ctx):
    if value != "media":
      raise ValueError("ttp:timeBase shall be `media`, not `%s`" % value)
    other_attrs.TimeBaseAttribute.validate(value, ctx)

class CellResolution(other_attrs.CellResolutionAttribute):
  '''ebuttdt:cellResolutionType'''

  @staticmethod
  def validate(value: str, _ctx):
    if _CELL_RESOLUTION_RE.fullmatch(value) is None:
      raise ValueError("ttp:cellResolution shall consist of two positive integers, not `%s`" % value)

def _validate_media_time(value: str, qname: QName, ctx: typing.Any):
  try:
    parse_media_time(value)
  except ValueError as e:
    raise ValueError("Bad %s value: %s" % (qname.local_name, e)) from e

  if "." in value and len(value.split(".", 1)[1]) > 3:
    ctx.event_handler.warn("The fraction of %s=`%s` should be limited to three digits", qname.local_name, value)

class Begin(other_attrs.BeginAttribute):
  '''ebuttdt:distributionMediaTimingType'''

  @staticmethod
  def validate(value: str, ctx: typing.Any):
    _validate_media_time(value, Begin.qname, ctx)

class End(other_attrs.EndAttribute):
  '''ebuttdt:distributionMediaTimingType'''

  @staticmethod
  def validate(value: str, ctx: typing.Any):
    _validate_media_time(value, End.qname, ctx)
