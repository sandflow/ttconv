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

'''Style properties'''

from __future__ import annotations
import typing
from dataclasses import dataclass
from enum import Enum

#
# Types
#

class AnnotationPositionType(Enum):
  '''<\\annotation-position\\> value
  '''
  before = "before"
  after = "after"
  outside = "outside" 

class LengthUnits(Enum):
  '''Units of length
  '''
  em = "em"
  pct = "%"
  rh = "rh"
  rw = "rw"
  c = "c"

class LengthType:
  '''Length type as defined in TTML
  '''

  def __init__(self, value: float = 0, units: LengthUnits = LengthUnits.rh):
    self.value = value
    self.units = units



class Colorimetry(Enum):
  '''Supported colorimetry systems
  '''
  RGBA8 = "RGBA8"

class ColorType:
  '''<color> type as defined in TTML
  '''

  def __init__(
      self,
      components: typing.Optional[typing.List[float]] = None,
      ident: Colorimetry = Colorimetry.RGBA8
  ):
    self.ident = ident
    self.components = components or [255, 255, 255, 255]

  def __eq__(self, other):
    return self.ident == other.ident and self.components == other.components


class NamedColors(Enum):
  '''TTML \\<named-color\\> 
  '''
  transparent = ColorType([0, 0, 0, 0])
  black = ColorType([0, 0, 0, 255])
  silver = ColorType([192, 192, 192, 255])
  gray = ColorType([128, 128, 128, 255])
  white = ColorType([255, 255, 255, 255])
  maroon = ColorType([128, 0, 0, 255])
  red = ColorType([255, 0, 0, 255])
  purple = ColorType([128, 0, 128, 255])
  fuchsia = ColorType([255, 0, 255, 255])
  magenta = ColorType([255, 0, 255, 255])
  green = ColorType([0, 128, 0, 255])
  lime = ColorType([0, 255, 0, 255])
  olive = ColorType([128, 128, 0, 255])
  yellow = ColorType([255, 255, 0, 255])
  navy = ColorType([0, 0, 128, 255])
  blue = ColorType([0, 0, 255, 255])
  teal = ColorType([0, 128, 128, 255])
  aqua = ColorType([0, 255, 255, 255])
  cyan = ColorType([0, 255, 255, 255])


class DirectionType(Enum):
  '''tts:direction values
  '''
  ltr = "ltr"
  rtl = "rtl" 
class DisplayType(Enum):
  '''tts:display value
  '''
  auto = "auto"
  none = "none" 


class DisplayAlignType(Enum):
  '''tts:displayAlign value
  '''
  before = "before"
  center = "center"
  after = "after" 


class ExtentType:
  '''tts:extent value

  Instance variables:

  `height`

  `width`
  '''

  def __init__(self, height: LengthType = None, width: LengthType = None):
    self.height = height or LengthType()
    self.width = width or LengthType()


class FontStyleType(Enum):
  '''tts:fontStyle value
  '''
  normal = "normal"
  italic = "italic"
  oblique = "oblique" 


class FontWeightType(Enum):
  '''tts:fontWeight value
  '''
  normal = "normal"
  bold = "bold" 


class MultiRowAlignType(Enum):
  '''ebutts:multiRowAlign value
  '''
  start = "start"
  center = "center"
  end = "end"
  auto = "auto"


class OverflowType(Enum):
  '''tts:overflow value
  '''
  visible = "visible"
  hidden = "hidden" 


class PaddingType:
  '''tts:padding value
  '''

  def __init__(
      self,
      before: LengthType = None,
      end: LengthType = None,
      after: LengthType = None,
      start: LengthType = None
    ):
    self.before = before or LengthType()
    self.end = end or LengthType()
    self.after = after or LengthType()
    self.start = start or LengthType()

class RubyAlignType(Enum):
  '''tts:rubyAlign value
  '''
  center = "center"
  spaceAround = "spaceAround" 

class RubeReserveType:
  '''TTML \\<ruby-reserve\\>
  '''

  class Position(Enum):
    both = "both"
    before = "before"
    after = "after"
    outside = "outside" 

  def __init__(self, position: RubeReserveType.Position = 0, length: LengthUnits = None):
    self.position = position
    self.length = length

class TextAlignType(Enum):
  '''tts:textAlign value
  '''
  center = "center"
  start = "start"
  end = "end"

class TextCombineType(Enum):
  '''TTML \\<text-combine\\>
  '''
  none = "none"
  all = "all"

@dataclass(frozen=True)
class TextDecorationType:
  '''TTML \\<text-decoration\\>
  '''

  class Action(Enum):
    none = "none"
    add = "add"
    remove = "remove"

  underline: Action = Action.none
  line_through: Action = Action.none
  overline: Action = Action.none


@dataclass(frozen=True)
class TextEmphasisType:
  '''TTML \\<text-emphasis\\>
  '''

  class Style(Enum):
    none = "none"
    auto = "auto"
    filled = "filled"
    open = "open"

  class Symbol(Enum):
    circle = "circle"
    dot = "dot"
    sesame = "sesame"

  class Position(Enum):
    outside = "outside"
    before = "before"
    after = "after"

  style: Style = Style.none
  symbol: Symbol = None
  color: ColorType = None
  position: Position = None

@dataclass(frozen=True)
class TextOutlineType:
  '''TTML \\<text-outline\\>
  '''

  color: ColorType = None
  thickness: LengthType = None

@dataclass(frozen=True)
class TextShadowType:
  '''TTML \\<text-shadow\\>
  '''

  @dataclass(frozen=True)
  class Shadow:
    x_offset: LengthType
    y_offset: LengthType
    blur_radius: LengthType
    color: ColorType

  shadows: typing.List[TextShadowType.Shadow]

class UnicodeBidiType(Enum):
  '''tts:unicodeBidi values
  '''
  normal = "normal"
  embed = "embed"
  bidiOverride = "bidiOverride"

class VisibilityType(Enum):
  '''tts:visibility value
  '''
  visible = "visible"
  hidden = "hidden" 

class WrapOptionType(Enum):
  '''tts:wrapOptionType value
  '''
  wrap = "wrap"
  noWrap = "noWrap" 

class WritingModeType(Enum):
  '''tts:writingModeType value
  '''
  lrtb = "lrtb"
  rltb = "rltb"
  tbrl = "tbrl" 
  tblr = "tblr" 

class PositionType:
  '''Coordinates in the root container region

  Instance variables:

  `x`: coordinate, measured from the left of the root container region.

  `y` : coordinate, measured from the top of the root container region.
  '''

  def __init__(self, x: LengthType = None, y: LengthType = None):
    self.x = x or LengthType()
    self.y = y or LengthType()

#
# Style properties
#

class StyleProperty:
  '''Abstract base class for all style properties'''

  @staticmethod
  def validate(value: typing.Any) -> bool:
    '''Returns whether the value is valid for the style property.'''
    raise Exception("Not implemented in the base class")

  @staticmethod
  def make_initial_value() -> typing.Any:
    '''Creates an instance of the initial value of the style property.'''
    raise Exception("Not implemented in the base class")

class StyleProperties:
  '''Container for all style properties
  
  Class variables:

  * `ALL`: set of all style properties
  '''

  class BackgroundColor(StyleProperty):
    '''Corresponds to tts:backgroundColor.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "backgroundColor"
    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return NamedColors.transparent

    @staticmethod
    def validate(value):
      return isinstance(value, ColorType)


  class Color(StyleProperty):
    '''Corresponds to tts:color.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "color"
    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return NamedColors.white

    @staticmethod
    def validate(value):
      return isinstance(value, ColorType) 


  class Direction(StyleProperty):
    '''Corresponds to tts:direction.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "direction"
    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return DirectionType.ltr

    @staticmethod
    def validate(value):
      return isinstance(value, DirectionType) 


  class Display(StyleProperty):
    '''Corresponds to tts:display.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "display"
    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return DisplayType.auto

    @staticmethod
    def validate(value):
      return isinstance(value, DisplayType) 


  class DisplayAlign(StyleProperty):
    '''Corresponds to tts:displayAlign.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "displayAlign"
    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return DisplayAlignType.before

    @staticmethod
    def validate(value):
      return isinstance(value, DisplayAlignType) 


  class Extent(StyleProperty):
    '''Corresponds to tts:extent.
    '''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "extent"
    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return LengthType()

    @staticmethod
    def validate(value: ExtentType):
      return isinstance(value, ExtentType) 


  class FillLineGap(StyleProperty):
    '''Corresponds to itts:fillLineGap.'''

    ns = "http://www.w3.org/ns/ttml/profile/imsc1#styling"
    local_name = "fillLineGap"
    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return False

    @staticmethod
    def validate(value: bool):
      return isinstance(value, bool)


  class FontFamily(StyleProperty):
    '''Corresponds to tts:fontFamily.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "fontFamily"
    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return ["default"]

    @staticmethod
    def validate(value: typing.List[str]):
      return isinstance(value, list) and all(lambda i: isinstance(i, str) for i in value)


  class FontSize(StyleProperty):
    '''Corresponds to tts:fontSize.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "fontSize"
    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return LengthType(1, LengthUnits.c)

    @staticmethod
    def validate(value):
      return isinstance(value, LengthType)


  class FontStyle(StyleProperty):
    '''Corresponds to tts:fontStyle.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "fontStyle"
    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return FontStyleType.normal

    @staticmethod
    def validate(value):
      return isinstance(value, FontStyleType)


  class FontWeight(StyleProperty):
    '''Corresponds to tts:fontWeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "fontWeight"
    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return FontWeightType.normal

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, FontWeightType)


  class LineHeight(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return "normal"

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class LinePadding(StyleProperty):
    '''Corresponds to ebutts:linePadding.'''

    ns = "urn:ebu:tt:style"
    local_name = "linePadding"
    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return LengthType()

    @staticmethod
    def validate(value: LengthType):
      return isinstance(value, LengthType) and value.units == LengthUnits.c


  class MultiRowAlign(StyleProperty):
    '''Corresponds to ebutts:multiRowAlign.'''

    ns = "urn:ebu:tt:style"
    local_name = "multiRowAlign"
    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return MultiRowAlignType.auto

    @staticmethod
    def validate(value):
      return isinstance(value, MultiRowAlignType)


  class Opacity(StyleProperty):
    '''Corresponds to tts:opacity.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "opacity"
    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return 1.0

    @staticmethod
    def validate(value: float):
      return isinstance(value, float)


  class Origin(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return PositionType()

    @staticmethod
    def validate(value):
      return isinstance(value, PositionType)


  class Overflow(StyleProperty):
    '''Corresponds to tts:overflow.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "overflow"
    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return OverflowType.hidden

    @staticmethod
    def validate(value):
      return isinstance(value, OverflowType)


  class Padding(StyleProperty):
    '''Corresponds to tts:padding.'''
    
    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "padding"
    is_inherited = False
    is_animatable = True

    @staticmethod
    def validate(value):
      return isinstance(value, PaddingType)


  class RubyAlign(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return "normal"

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class RubyPosition(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return "normal"

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class RubyReserve(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return "normal"

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class Shear(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return "normal"

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)


  class TextAlign(StyleProperty):
    '''Corresponds to tts:textAlign.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return "normal"

    @staticmethod
    def validate(value):
      return isinstance(value, TextAlignType)


  class TextCombine(StyleProperty):
    '''Corresponds to tts:textCombine.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return TextCombineType.none

    @staticmethod
    def validate(value):
      return isinstance(value, TextCombineType)


  class TextDecoration(StyleProperty):
    '''Corresponds to tts:textDecoration.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return "none"

    @staticmethod
    def validate(value):
      return value == "none" or isinstance(value, TextDecorationType)


  class TextEmphasis(StyleProperty):
    '''Corresponds to tts:textEmphasis.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return TextEmphasisType()

    @staticmethod
    def validate(value):
      return isinstance(value, TextEmphasisType)


  class TextOutline(StyleProperty):
    '''Corresponds to tts:textOutline.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return "none"

    @staticmethod
    def validate(value):
      return value == "none" or isinstance(value, TextOutlineType)


  class TextShadow(StyleProperty):
    '''Corresponds to tts:textShadow.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return "none"

    @staticmethod
    def validate(value):
      return value == "none" or isinstance(value, TextShadowType)


  class UnicodeBidi(StyleProperty):
    '''Corresponds to tts:unicodeBidi.'''

    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return UnicodeBidiType.normal

    @staticmethod
    def validate(value):
      return isinstance(value, UnicodeBidiType)


  class Visibility(StyleProperty):
    '''Corresponds to tts:visibility.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return VisibilityType.visible

    @staticmethod
    def validate(value):
      return isinstance(value, VisibilityType)


  class WrapOption(StyleProperty):
    '''Corresponds to tts:wrapOption.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return WrapOptionType.wrap

    @staticmethod
    def validate(value):
      return isinstance(value, WrapOptionType)


  class WritingMode(StyleProperty):
    '''Corresponds to tts:writingMode.'''

    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return WritingModeType.lrtb

    @staticmethod
    def validate(value):
      return isinstance(value, WritingModeType)

  ALL = {v for n, v in list(locals().items()) if callable(v)}
