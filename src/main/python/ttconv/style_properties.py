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
import numbers
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


@dataclass(frozen=True)
class LengthType:
  '''Length type as defined in TTML
  '''

  class Units(Enum):
    '''Units of length
    '''
    em = "em"
    pct = "%"
    rh = "rh"
    rw = "rw"
    c = "c"
    px = "px"

  value: numbers.Number = 0
  units: Units = Units.pct

  def __post_init__(self):
    if not isinstance(self.value, numbers.Number):
      raise ValueError("The length value must be a number")

    if not isinstance(self.units, LengthType.Units):
      raise ValueError("Invalid units")

@dataclass(frozen=True)
class ColorType:
  '''<color> type as defined in TTML
  '''

  class Colorimetry(Enum):
    '''Supported colorimetry systems
    '''
    RGBA8 = "RGBA8"

  components: tuple = (255, 255, 255, 255)
  ident: Colorimetry = Colorimetry.RGBA8


class NamedColors(Enum):
  '''TTML \\<named-color\\> 
  '''
  transparent = ColorType((0, 0, 0, 0))
  black = ColorType((0, 0, 0, 255))
  silver = ColorType((192, 192, 192, 255))
  gray = ColorType((128, 128, 128, 255))
  white = ColorType((255, 255, 255, 255))
  maroon = ColorType((128, 0, 0, 255))
  red = ColorType((255, 0, 0, 255))
  purple = ColorType((128, 0, 128, 255))
  fuchsia = ColorType((255, 0, 255, 255))
  magenta = ColorType((255, 0, 255, 255))
  green = ColorType((0, 128, 0, 255))
  lime = ColorType((0, 255, 0, 255))
  olive = ColorType((128, 128, 0, 255))
  yellow = ColorType((255, 255, 0, 255))
  navy = ColorType((0, 0, 128, 255))
  blue = ColorType((0, 0, 255, 255))
  teal = ColorType((0, 128, 128, 255))
  aqua = ColorType((0, 255, 255, 255))
  cyan = ColorType((0, 255, 255, 255))


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

@dataclass(frozen=True)
class ExtentType:
  '''tts:extent value
  '''

  height: LengthType = LengthType()
  width: LengthType = LengthType()

class GenericFontFamilyType(Enum):
  '''\\<generic-family-name\\>
  '''
  default = "default"
  monospace = "monospace"
  sansSerif = "sansSerif"
  serif = "serif"
  monospaceSansSerif = "monospaceSansSerif"
  monospaceSerif = "monospaceSerif"
  proportionalSansSerif = "proportionalSansSerif"
  proportionalSerif = "proportionalSerif"

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

@dataclass(frozen=True)
class PaddingType:
  '''tts:padding value
  '''

  before: LengthType = LengthType()
  end: LengthType = LengthType()
  after: LengthType = LengthType()
  start: LengthType = LengthType()


class RubyAlignType(Enum):
  '''tts:rubyAlign value
  '''
  center = "center"
  spaceAround = "spaceAround" 


@dataclass(frozen=True)
class RubyReserveType:
  '''TTML \\<ruby-reserve\\>
  '''

  class Position(Enum):
    '''TTML \\<ruby-reserve\\> position'''
    both = "both"
    before = "before"
    after = "after"
    outside = "outside" 

  position: Position = Position.outside
  length: LengthType = None

class ShowBackgroundType(Enum):
  '''tts:showBackground values
  '''
  always = "always"
  whenActive = "whenActive"

class SpecialValues(Enum):
  '''Special style property values
  '''
  normal = "normal"
  none = "none"

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

  underline: typing.Optional[bool] = None
  line_through: typing.Optional[bool] = None
  overline: typing.Optional[bool] = None


@dataclass(frozen=True)
class TextEmphasisType:
  '''TTML \\<text-emphasis\\>
  '''

  class Style(Enum):
    '''Combines \\<emphasis-style\\> and \\<emphasis-symbol\\>
    '''
    auto = "auto"
    filled_circle = "filled circle"
    filled_dot = "filled dot"
    filled_sesame = "filled sesame"
    open_circle = "open circle"
    open_dot = "open dot"
    open_sesame = "open sesame"

  class Position(Enum):
    ''' \\<emphasis-position\\>
    '''
    outside = "outside"
    before = "before"
    after = "after"

  style: Style = Style.auto
  color: ColorType = None
  position: Position = Position.outside

  def __post_init__(self):
    if not isinstance(self.style, TextEmphasisType.Style):
      raise ValueError("Style must be a text emphasis style enumeration value")

    if not (self.color is None or isinstance(self.color, ColorType)):
      raise ValueError("The color must be None or a valid color")

    if not isinstance(self.position, TextEmphasisType.Position):
      raise ValueError("Position must be a text emphasis position enumeration value")


@dataclass(frozen=True)
class TextOutlineType:
  '''TTML \\<text-outline\\>
  '''

  thickness: LengthType
  color: ColorType = None

  def __post_init__(self):
    if self.thickness is None or not isinstance(self.thickness, LengthType):
      raise ValueError("The thickness value must be a length")

    if not (self.color is None or isinstance(self.color, ColorType)):
      raise ValueError("The color must be None or a valid color")

@dataclass(frozen=True)
class TextShadowType:
  '''TTML \\<text-shadow\\>
  '''

  @dataclass(frozen=True)
  class Shadow:
    '''Represents one shadow value
    '''
    x_offset: LengthType
    y_offset: LengthType
    blur_radius: typing.Optional[LengthType] = None
    color: typing.Optional[ColorType] = None

  shadows: typing.Tuple[TextShadowType.Shadow]


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


@dataclass(frozen=True)
class CoordinateType:
  '''Coordinates (`x`, `y`) in the root container region, as measure from the left and top edges, respectively.
  '''
  x: LengthType
  y: LengthType


@dataclass(frozen=True)
class PositionType:
  '''Offsets (`h_offset`, `v_offset`) in the root container region, as measure from the `h_edge` and `v_edge` edges, respectively.
  '''
  class HEdge(Enum):
    left = "left"
    right = "right"

  class VEdge(Enum):
    top = "top"
    bottom = "bottom"

  h_offset: LengthType
  v_offset: LengthType
  h_edge: HEdge = HEdge.left
  v_edge: VEdge = VEdge.top

#
# Style properties
#

class StyleProperty:
  '''Abstract base class for all style properties'''

  @classmethod
  def is_inherited(cls) -> bool:
    '''True if a child element inherits the value of the property from its parent
    '''
    raise NotImplementedError

  @classmethod
  def is_animatable(cls) -> bool:
    '''True if the property can be use in a `DiscreteAnimationStep` instance
    '''
    raise NotImplementedError

  @staticmethod
  def validate(value: typing.Any) -> bool:
    '''Returns whether the value is valid for the style property.'''
    raise NotImplementedError

  @staticmethod
  def make_initial_value() -> typing.Any:
    '''Creates an instance of the initial value of the style property.'''
    raise NotImplementedError

class StyleProperties:
  '''Container for all style properties
  
  Class variables:

  * `ALL`: set of all style properties
  '''

  class BackgroundColor(StyleProperty):
    '''Corresponds to tts:backgroundColor.'''

    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return NamedColors.transparent.value

    @staticmethod
    def validate(value):
      return isinstance(value, ColorType)


  class Color(StyleProperty):
    '''Corresponds to tts:color.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return NamedColors.white.value

    @staticmethod
    def validate(value):
      return isinstance(value, ColorType) 


  class Direction(StyleProperty):
    '''Corresponds to tts:direction.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return DirectionType.ltr

    @staticmethod
    def validate(value):
      return isinstance(value, DirectionType) 

  class Disparity(StyleProperty):
    '''Corresponds to tts:disparity.'''

    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return LengthType()

    @staticmethod
    def validate(value):
      return isinstance(value, LengthType) 

  class Display(StyleProperty):
    '''Corresponds to tts:display.'''

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

    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return ExtentType(
        height=LengthType(value=100, units=LengthType.Units.pct),
        width=LengthType(value=100, units=LengthType.Units.pct)
      )

    @staticmethod
    def validate(value: ExtentType):
      return isinstance(value, ExtentType) \
        and value.width.units in (LengthType.Units.pct, LengthType.Units.px, LengthType.Units.c, LengthType.Units.rw)  \
        and value.height.units in (LengthType.Units.pct, LengthType.Units.px, LengthType.Units.c, LengthType.Units.rh)


  class FillLineGap(StyleProperty):
    '''Corresponds to itts:fillLineGap.'''

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

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return (GenericFontFamilyType.default,)

    @staticmethod
    def validate(value: typing.Tuple[typing.Union[str, GenericFontFamilyType]]):
      return isinstance(value, tuple) and all(lambda i: isinstance(i, (str, GenericFontFamilyType)) for i in value)


  class FontSize(StyleProperty):
    '''Corresponds to tts:fontSize.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return LengthType(1, LengthType.Units.c)

    @staticmethod
    def validate(value):
      return isinstance(value, LengthType)


  class FontStyle(StyleProperty):
    '''Corresponds to tts:fontStyle.'''

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

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return FontWeightType.normal

    @staticmethod
    def validate(value):
      return isinstance(value, FontWeightType)


  class LineHeight(StyleProperty):
    '''Corresponds to tts:lineHeight.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return SpecialValues.normal

    @staticmethod
    def validate(value):
      return value == SpecialValues.normal or isinstance(value, LengthType)


  class LinePadding(StyleProperty):
    '''Corresponds to ebutts:linePadding.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return LengthType(value=1, units=LengthType.Units.c)

    @staticmethod
    def validate(value: LengthType):
      return isinstance(value, LengthType) and \
        value.units in (LengthType.Units.c, LengthType.Units.rh, LengthType.Units.rw)


  class LuminanceGain(StyleProperty):
    '''Corresponds to tts:luminanceGain.'''

    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return 1.0

    @staticmethod
    def validate(value: numbers.Number):
      return isinstance(value, numbers.Number)


  class MultiRowAlign(StyleProperty):
    '''Corresponds to ebutts:multiRowAlign.'''

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

    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return 1.0

    @staticmethod
    def validate(value: numbers.Number):
      return isinstance(value, numbers.Number)


  class Origin(StyleProperty):
    '''Corresponds to tts:origin.'''

    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return CoordinateType(
        LengthType(0, LengthType.Units.pct),
        LengthType(0, LengthType.Units.pct)
      )

    @staticmethod
    def validate(value: CoordinateType):
      return isinstance(value, CoordinateType) \
        and value.x.units in (LengthType.Units.pct, LengthType.Units.px, LengthType.Units.c, LengthType.Units.rw)  \
        and value.y.units in (LengthType.Units.pct, LengthType.Units.px, LengthType.Units.c, LengthType.Units.rh)


  class Overflow(StyleProperty):
    '''Corresponds to tts:overflow.'''

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
    
    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return PaddingType()

    @staticmethod
    def validate(value):
      return isinstance(value, PaddingType)


  class Position(StyleProperty):
    '''Corresponds to tts:position.'''

    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return PositionType(
        LengthType(0, LengthType.Units.pct),
        LengthType(0, LengthType.Units.pct)
      )

    @staticmethod
    def validate(value: PositionType):
      return isinstance(value, PositionType) \
        and value.h_offset.units in (LengthType.Units.pct, LengthType.Units.px, LengthType.Units.c, LengthType.Units.rw)  \
        and value.v_offset.units in (LengthType.Units.pct, LengthType.Units.px, LengthType.Units.c, LengthType.Units.rh)

  class RubyAlign(StyleProperty):
    '''Corresponds to tts:rubyAlign.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return RubyAlignType.center

    @staticmethod
    def validate(value):
      return isinstance(value, RubyAlignType)


  class RubyPosition(StyleProperty):
    '''Corresponds to tts:rubyPosition.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return AnnotationPositionType.outside

    @staticmethod
    def validate(value):
      return isinstance(value, AnnotationPositionType)


  class RubyReserve(StyleProperty):
    '''Corresponds to tts:rubyReserve.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return SpecialValues.none

    @staticmethod
    def validate(value):
      return value == SpecialValues.none or isinstance(value, RubyReserveType)


  class Shear(StyleProperty):
    '''Corresponds to tts:shear.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return 0.0

    @staticmethod
    def validate(value: numbers.Number):
      return isinstance(value, numbers.Number)

  class ShowBackground(StyleProperty):
    '''Corresponds to tts:showBackground.'''

    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return ShowBackgroundType.always

    @staticmethod
    def validate(value):
      return isinstance(value, ShowBackgroundType)


  class TextAlign(StyleProperty):
    '''Corresponds to tts:textAlign.'''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return TextAlignType.start

    @staticmethod
    def validate(value):
      return isinstance(value, TextAlignType)


  class TextCombine(StyleProperty):
    '''Corresponds to tts:textCombine
    '''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return TextCombineType.none

    @staticmethod
    def validate(value):
      return isinstance(value, TextCombineType)


  class TextDecoration(StyleProperty):
    '''Corresponds to tts:textDecoration
    '''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return TextDecorationType(
        underline=False,
        overline=False,
        line_through=False
      )

    @staticmethod
    def validate(value):
      return isinstance(value, TextDecorationType)


  class TextEmphasis(StyleProperty):
    '''Corresponds to tts:textEmphasis
    '''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return SpecialValues.none

    @staticmethod
    def validate(value):
      return value is SpecialValues.none or isinstance(value, TextEmphasisType)


  class TextOutline(StyleProperty):
    '''Corresponds to tts:textOutline
    '''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return SpecialValues.none

    @staticmethod
    def validate(value):
      return value == SpecialValues.none or isinstance(value, TextOutlineType)


  class TextShadow(StyleProperty):
    '''Corresponds to tts:textShadow
    '''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return SpecialValues.none

    @staticmethod
    def validate(value):
      return value == SpecialValues.none or isinstance(value, TextShadowType)


  class UnicodeBidi(StyleProperty):
    '''Corresponds to tts:unicodeBidi
    '''

    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return UnicodeBidiType.normal

    @staticmethod
    def validate(value):
      return isinstance(value, UnicodeBidiType)


  class Visibility(StyleProperty):
    '''Corresponds to tts:visibility
    '''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return VisibilityType.visible

    @staticmethod
    def validate(value):
      return isinstance(value, VisibilityType)


  class WrapOption(StyleProperty):
    '''Corresponds to tts:wrapOption
    '''

    is_inherited = True
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return WrapOptionType.wrap

    @staticmethod
    def validate(value):
      return isinstance(value, WrapOptionType)


  class WritingMode(StyleProperty):
    '''Corresponds to tts:writingMode
    '''

    is_inherited = False
    is_animatable = True

    @staticmethod
    def make_initial_value():
      return WritingModeType.lrtb

    @staticmethod
    def validate(value):
      return isinstance(value, WritingModeType)

  ALL = {v: StyleProperty for n, v in list(locals().items()) if callable(v)}
