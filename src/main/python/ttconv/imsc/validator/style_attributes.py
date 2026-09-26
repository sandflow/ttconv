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

'''IMSC style properties'''

import re
from ttconv.imsc.validator.attribute_vocabulary import attribute
from ttconv.imsc.validator.other_attributes import ValidationContext
from ttconv.imsc.validator.font_helper import is_quoted_string, is_valid_font_families
from ttconv.imsc.namespaces import QName
import ttconv.imsc.namespaces as xml_ns
import ttconv.style_properties as ttconv_styles
import ttconv.imsc.utils as imsc_utils

_HEX_COLOR_RE = re.compile(r"^#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})?$")
_DEC_COLOR_RE = re.compile(r"^rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$")
_DEC_COLORA_RE = re.compile(r"^rgba\(\s*(\d+),\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$")
_NON_NEGATIVE_NUMBER_RE = re.compile(r"^\d+(\.\d+)?$")

def _validate_color(attr_value: str):
  '''Parses the TTML \\<color\\> value contained in `attr_value`
  '''

  if str.lower(attr_value) in ttconv_styles.NamedColors.__members__:
    return

  m = _HEX_COLOR_RE.match(attr_value)
  if m:
    for i in range(4):
      if m.group(i + 1) is None:
        break
      if int(m.group(i + 1), 16) > 255:
        raise ValueError()
    return

  m = _DEC_COLOR_RE.match(attr_value)
  if m:
    for i in range(3):
      if int(m.group(i + 1)) > 255:
        raise ValueError()
    return
  
  m = _DEC_COLORA_RE.match(attr_value)
  if m:
    for i in range(4):
      if int(m.group(i + 1)) > 255:
        raise ValueError()
    return

  raise ValueError()

@attribute
class BackgroundColor:
  '''Corresponds to tts:backgroundColor.'''

  qname = QName(xml_ns.TTS, "backgroundColor")
  is_inherited = False

  @staticmethod
  def validate(value: str, _ctx : ValidationContext):
    try:
      _validate_color(value)
    except ValueError:
      raise ValueError("Bad backgroundColor value (%s)" % value)

@attribute
class Color:
  '''Corresponds to tts:color.'''

  qname = QName(xml_ns.TTS, "color")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx : ValidationContext):
    try:
      _validate_color(value)
    except ValueError:
      raise ValueError("Bad backgroundColor value (%s)" % value)

@attribute
class Direction:
  '''Corresponds to tts:direction.'''

  qname = QName(xml_ns.TTS, "direction")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("ltr", "rtl"):
      raise ValueError("Bad tts:direction value (%s)" % value)

@attribute
class Disparity:
  '''Corresponds to tts:disparity.
  '''

  qname = QName(xml_ns.TTS, "disparity")
  is_inherited = False

  @staticmethod
  def validate(value: str, ctx: ValidationContext):
    try:
      imsc_utils.parse_length(value)
    except ValueError:
      raise ValueError("Bad tts:disparity value (%s)" % value)

@attribute
class Display:
  '''Corresponds to tts:display.'''

  qname = QName(xml_ns.TTS, "display")
  is_inherited = False

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("auto", "none"):
      raise ValueError("Bad tts:display value (%s)" % value)

@attribute
class DisplayAlign:
  '''Corresponds to tts:displayAlign.'''

  qname = QName(xml_ns.TTS, "displayAlign")
  is_inherited = False

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("before", "center", "after"):
      raise ValueError("Bad tts:displayAlign value (%s)" % value)

@attribute
class Extent:
  '''Corresponds to tts:extent.
  '''

  qname = QName(xml_ns.TTS, "extent")
  is_inherited = False

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value == "auto":
      return
    components = value.split(" ")
    if len(components) != 2:
      raise ValueError("Bad tts:extent value (%s)" % value)
    for length in components:
      try:
        (length_value, _) = imsc_utils.parse_length(length)
      except ValueError:
        raise ValueError("Bad tts:extent value (%s)" % value)
      if length_value < 0:
        raise ValueError("tts:extent lengths must be positive (%s)" % value)

@attribute
class FillLineGap:
  '''Corresponds to itts:fillLineGap.'''

  qname = QName(xml_ns.ITTS, "fillLineGap")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("true", "false"):
      raise ValueError("Bad itts:fillLineGap value (%s)" % value)

@attribute
class ForcedDisplay:
  '''Corresponds to itts:forcedDisplay.'''

  qname = QName(xml_ns.ITTS, "forcedDisplay")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("true", "false"):
      raise ValueError("Bad itts:forcedDisplay value (%s)" % value)

@attribute
class FontFamily:
  '''Corresponds to tts:fontFamily.'''

  qname = QName(xml_ns.TTS, "fontFamily")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx : ValidationContext):
    if not is_valid_font_families(value):
      raise ValueError("Invalid tts:fontFamily value (%s)" % value)


@attribute
class FontSize:
  '''Corresponds to tts:fontSize.'''

  qname = QName(xml_ns.TTS, "fontSize")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    try:
      imsc_utils.parse_length(value)
    except ValueError:
      raise ValueError("Bad tts:fontSize value (%s)" % value)

@attribute
class FontStyle:
  '''Corresponds to tts:fontStyle.'''

  qname = QName(xml_ns.TTS, "fontStyle")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("normal", "italic", "oblique"):
      raise ValueError("Bad tts:fontStyle value (%s)" % value)

@attribute
class FontVariant:
  '''Corresponds to tts:fontVariant.'''

  qname = QName(xml_ns.TTS, "fontVariant")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("normal", "super", "sub"):
      raise ValueError("Bad tts:fontVariant value (%s)" % value)

@attribute
class FontWeight:
  '''Corresponds to tts:fontWeight.'''

  qname = QName(xml_ns.TTS, "fontWeight")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx : ValidationContext):
    try:
      ttconv_styles.FontWeightType[value]
    except KeyError:
      raise ValueError("Bad tts:fontWeight value (%s)" % value)

@attribute
class LineHeight:
  '''tts:lineHeight'''

  qname = QName(xml_ns.TTS, "lineHeight")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value == "normal":
      return
    try:
      (l, _) = imsc_utils.parse_length(value)
    except ValueError:
      raise ValueError("Invalid tts:lineHeight syntax: %s" % value)
    if l < 0:
      raise ValueError("tts:lineHeight %s is less than 0" % value)

@attribute
class LinePadding:
  '''Corresponds to ebutts:linePadding.'''

  qname = QName(xml_ns.EBUTTS, "linePadding")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    try:
      (l, units) = imsc_utils.parse_length(value)
    except ValueError:
      raise ValueError("Bad ebutts:linePadding value (%s)" % value)
    if units != "c":
      raise ValueError("ebutts:linePadding must be expressed in 'c' units (%s)" % value)
    if l < 0:
      raise ValueError("ebutts:linePadding must be non-negative (%s)" % value)

@attribute
class LuminanceGain:
  '''Corresponds to tts:luminanceGain.'''

  qname = QName(xml_ns.TTS, "luminanceGain")
  is_inherited = False

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if not _NON_NEGATIVE_NUMBER_RE.match(value):
      raise ValueError("Bad tts:luminanceGain value (%s)" % value)

@attribute
class MultiRowAlign:
  '''Corresponds to ebutts:multiRowAlign.'''

  qname = QName(xml_ns.EBUTTS, "multiRowAlign")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("start", "center", "end", "auto"):
      raise ValueError("Bad ebutts:multiRowAlign value (%s)" % value)

@attribute
class Opacity:
  '''Corresponds to tts:opacity.'''

  qname = QName(xml_ns.TTS, "opacity")
  is_inherited = False

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    try:
      float(value)
    except ValueError:
      raise ValueError("Bad tts:opacity value (%s)" % value)

@attribute
class Origin:
  '''Corresponds to tts:origin.'''

  qname = QName(xml_ns.TTS, "origin")
  is_inherited = False

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value == "auto":
      return
    components = value.split(" ")
    if len(components) != 2:
      raise ValueError("Bad tts:origin value (%s)" % value)
    for length in components:
      try:
        imsc_utils.parse_length(length)
      except ValueError:
        raise ValueError("Bad tts:origin value (%s)" % value)

@attribute
class Overflow:
  '''Corresponds to tts:overflow.'''

  qname = QName(xml_ns.TTS, "overflow")
  is_inherited = False

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("visible", "hidden"):
      raise ValueError("Bad tts:overflow value (%s)" % value)

@attribute
class Padding:
  '''Corresponds to tts:padding.'''

  qname = QName(xml_ns.TTS, "padding")
  is_inherited = False

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    components = value.split(" ")
    if len(components) < 1 or len(components) > 4:
      raise ValueError("Bad tts:padding value (%s)" % value)
    for length in components:
      try:
        (l, _) = imsc_utils.parse_length(length)
      except ValueError:
        raise ValueError("Bad tts:padding value (%s)" % value)
      if l < 0:
        raise ValueError("ebutts:linePadding must be non-negative (%s)" % value)

@attribute
class Position:
  '''Corresponds to tts:position.'''

  qname = QName(xml_ns.TTS, "position")
  is_inherited = False

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    # TODO: remove this once parse_position() is fixed
    if not 1 <= len(value.split()) <= 4:
      raise ValueError("Bad tts:position value (%s)" % value)
    try:
      imsc_utils.parse_position(value)
    except ValueError:
      raise ValueError("Bad tts:position value (%s)" % value)

@attribute
class Ruby:
  '''Corresponds to tts:ruby.'''

  qname = QName(xml_ns.TTS, "ruby")
  is_inherited = False

  _VALUES = ("none", "container", "base", "baseContainer", "text", "textContainer", "delimiter")

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in Ruby._VALUES:
      raise ValueError("Bad tts:ruby value (%s)" % value)

@attribute
class RubyAlign:
  '''Corresponds to tts:rubyAlign.'''

  qname = QName(xml_ns.TTS, "rubyAlign")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("center", "spaceAround"):
      raise ValueError("Bad tts:rubyAlign value (%s)" % value)

@attribute
class RubyPosition:
  '''Corresponds to tts:rubyPosition.'''

  qname = QName(xml_ns.TTS, "rubyPosition")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("before", "after", "outside"):
      raise ValueError("Bad tts:rubyPosition value (%s)" % value)

@attribute
class RubyReserve:
  '''Corresponds to tts:rubyReserve.'''

  qname = QName(xml_ns.TTS, "rubyReserve")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value == "none":
      return
    components = value.split(" ")
    if len(components) == 0 or len(components) > 2:
      raise ValueError("Bad tts:rubyReserve value (%s)" % value)
    if components[0] not in ("both", "before", "after", "outside"):
      raise ValueError("Bad tts:rubyReserve value (%s)" % value)
    if len(components) == 2:
      try:
        (l, _) = imsc_utils.parse_length(components[1])
      except ValueError:
        raise ValueError("Bad tts:rubyReserve value (%s)" % value)
      if l < 0:
        raise ValueError("Negative length in tts:rubyReserve value (%s)" % value)

@attribute
class Shear:
  '''Corresponds to tts:shear.'''

  qname = QName(xml_ns.TTS, "shear")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    try:
      (_, units) = imsc_utils.parse_length(value)
    except ValueError:
      raise ValueError("Bad tts:shear value (%s)" % value)
    if units != "%":
      raise ValueError("tts:shear must be expressed in %% units (%s)" % value)

@attribute
class ShowBackground:
  '''Corresponds to tts:showBackground.'''

  qname = QName(xml_ns.TTS, "showBackground")
  is_inherited = False

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("always", "whenActive"):
      raise ValueError("Bad tts:showBackground value (%s)" % value)

@attribute
class TextAlign:
  '''Corresponds to tts:textAlign.'''

  qname = QName(xml_ns.TTS, "textAlign")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("left", "right", "center", "start", "end"):
      raise ValueError("Bad tts:textAlign value (%s)" % value)

@attribute
class TextCombine:
  '''Corresponds to tts:textCombine.'''

  qname = QName(xml_ns.TTS, "textCombine")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("none", "all"):
      raise ValueError("Bad tts:textCombine value (%s)" % value)

@attribute
class TextDecoration:
  '''Corresponds to tts:textDecoration.'''

  qname = QName(xml_ns.TTS, "textDecoration")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value == "none":
      return
    valid_tokens = ("underline", "noUnderline", "lineThrough", "noLineThrough", "overline", "noOverline")
    for token in value.split(" "):
      if token not in valid_tokens:
        raise ValueError("Bad tts:textDecoration value (%s)" % value)

@attribute
class TextEmphasis:
  '''Corresponds to tts:textEmphasis.'''

  qname = QName(xml_ns.TTS, "textEmphasis")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value == "none":
      return
    for token in value.split(" "):
      if token in ("auto", "filled", "open", "circle", "dot", "sesame", "outside", "before", "after"):
        continue
      if token == "current":
        raise ValueError("tts:textEmphasis emphasis-color component is not permitted (%s)" % token)
      if is_quoted_string(token):
        raise ValueError("tts:textEmphasis emphasis-style quoted-string component is not permitted (%s)" % token)
      try:
        _validate_color(token)
      except ValueError:
        raise ValueError("Bad tts:textEmphasis value (%s)" % value)
      else:
        raise ValueError("tts:textEmphasis emphasis-color component is not permitted (%s)" % token)

@attribute
class TextOutline:
  '''Corresponds to tts:textOutline.'''

  qname = QName(xml_ns.TTS, "textOutline")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value == "none":
      return
    components = value.split(" ")
    if len(components) == 0 or len(components) > 2:
      raise ValueError("Bad tts:textOutline value (%s)" % value)
    try:
      (l, _) = imsc_utils.parse_length(components[-1])
    except ValueError:
      raise ValueError("Bad tts:textOutline value (%s)" % value)
    if l < 0:
      raise ValueError("tts:textOutline thickness must be non-negative (%s)" % value)
    if len(components) == 2:
      try:
        _validate_color(components[0])
      except ValueError:
        raise ValueError("Bad tts:textOutline value (%s)" % value)

@attribute
class TextShadow:
  '''Corresponds to tts:textShadow.'''

  qname = QName(xml_ns.TTS, "textShadow")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value == "none":
      return
    for shadow in value.split(","):
      components = shadow.split(" ")
      if len(components) < 2 or len(components) > 4:
        raise ValueError("Bad tts:textShadow value (%s)" % value)
      try:
        imsc_utils.parse_length(components[0])
        imsc_utils.parse_length(components[1])
      except ValueError:
        raise ValueError("Bad tts:textShadow value (%s)" % value)
      if len(components) == 3:
        try:
          (l, _) = imsc_utils.parse_length(components[2])
        except ValueError:
          try:
            _validate_color(components[2])
          except ValueError:
            raise ValueError("Bad tts:textShadow value (%s)" % value)
        else:
          if l < 0:
            raise ValueError("Negative length in tts:textShadow value (%s)" % value)
      elif len(components) == 4:
        try:
          (l, _) = imsc_utils.parse_length(components[2])
        except ValueError:
          raise ValueError("Bad tts:textShadow value (%s)" % value)
        if l < 0:
          raise ValueError("Negative length in tts:textShadow value (%s)" % value)
        try:
          _validate_color(components[3])
        except ValueError:
          raise ValueError("Bad tts:textShadow value (%s)" % value)

@attribute
class UnicodeBidi:
  '''Corresponds to tts:unicodeBidi.'''

  qname = QName(xml_ns.TTS, "unicodeBidi")
  is_inherited = False

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("normal", "embed", "bidiOverride"):
      raise ValueError("Bad tts:unicodeBidi value (%s)" % value)

@attribute
class Visibility:
  '''Corresponds to tts:visibility.'''

  qname = QName(xml_ns.TTS, "visibility")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("visible", "hidden"):
      raise ValueError("Bad tts:visibility value (%s)" % value)

@attribute
class WrapOption:
  '''Corresponds to tts:wrapOption.'''

  qname = QName(xml_ns.TTS, "wrapOption")
  is_inherited = True

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("wrap", "noWrap"):
      raise ValueError("Bad tts:wrapOption value (%s)" % value)

@attribute
class WritingMode:
  '''Corresponds to tts:writingMode.'''

  qname = QName(xml_ns.TTS, "writingMode")
  is_inherited = False

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("lr", "rl", "tb", "lrtb", "rltb", "tbrl", "tblr"):
      raise ValueError("Bad tts:writingMode value (%s)" % value)

@attribute
class ZIndex:
  '''Corresponds to tts:zIndex.'''

  qname = QName(xml_ns.TTS, "zIndex")
  is_inherited = False

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value == "auto":
      return
    try:
      int(value)
    except ValueError:
      raise ValueError("Bad tts:zIndex value (%s)" % value)
