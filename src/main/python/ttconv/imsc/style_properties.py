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

import inspect
import math
import typing
import ttconv.style_properties as styles
import ttconv.imsc.utils as utils

class StyleParsingContext:
  pass

class StyleProperty:
  '''Base class for style properties'''

  @classmethod
  def extract(cls, context: StyleParsingContext, xml_attrib: str):
    '''Converts an IMSC style property to a data model value'''

class StyleProperties:
  '''TTML style properties

  Class variables:
  
  `BY_QNAME`: mapping of qualified name to StyleProperty class
  '''

  class BackgroundColor(StyleProperty):
    '''Corresponds to tts:backgroundColor.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "backgroundColor"
    model_prop = styles.StyleProperties.BackgroundColor

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return utils.parse_color(xml_attrib)

  class Color(StyleProperty):
    '''Corresponds to tts:color.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "color"
    model_prop = styles.StyleProperties.Color

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return utils.parse_color(xml_attrib)


  class Direction(StyleProperty):
    '''Corresponds to tts:direction.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "direction"
    model_prop = styles.StyleProperties.Direction

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.DirectionType[xml_attrib]


  class Disparity(StyleProperty):
    '''Corresponds to tts:disparity.
    '''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "disparity"
    model_prop = styles.StyleProperties.Disparity

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return StyleProperties.ttml_length_to_model(context, xml_attrib)
      
      
  class Display(StyleProperty):
    '''Corresponds to tts:display.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "display"
    model_prop = styles.StyleProperties.Display

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.DisplayType[xml_attrib]


  class DisplayAlign(StyleProperty):
    '''Corresponds to tts:displayAlign.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "displayAlign"
    model_prop = styles.StyleProperties.DisplayAlign

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.DisplayAlignType[xml_attrib]

  class Extent(StyleProperty):
    '''Corresponds to tts:extent.
    '''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "extent"
    model_prop = styles.StyleProperties.Extent

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      if xml_attrib == "auto":

        return styles.ExtentType(
          height=styles.LengthType(1, styles.LengthType.Units.rh),
          width=styles.LengthType(1, styles.LengthType.Units.rw)
        )

      s = xml_attrib.split(" ")

      if len(s) != 2:
        raise ValueError("Bad tts:extent syntax")

      return styles.ExtentType(
        height=StyleProperties.ttml_length_to_model(context, s[1]),
        width=StyleProperties.ttml_length_to_model(context, s[0])
      )


  class FillLineGap(StyleProperty):
    '''Corresponds to itts:fillLineGap.'''

    ns = "http://www.w3.org/ns/ttml/profile/imsc1#styling"
    local_name = "fillLineGap"
    model_prop = styles.StyleProperties.FillLineGap

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return xml_attrib == "true"

  class FontFamily(StyleProperty):
    '''Corresponds to tts:fontFamily.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "fontFamily"
    model_prop = styles.StyleProperties.FontFamily

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):

      return list(map(
        lambda f: "monospaceSerif" if f == "default" else f,
        utils.parse_font_families(xml_attrib)
      ))

  class FontSize(StyleProperty):
    '''Corresponds to tts:fontSize.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "fontSize"
    model_prop = styles.StyleProperties.FontSize

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return StyleProperties.ttml_length_to_model(context, xml_attrib)


  class FontStyle(StyleProperty):
    '''Corresponds to tts:fontStyle.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "fontStyle"
    model_prop = styles.StyleProperties.FontStyle

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.FontStyleType[xml_attrib]


  class FontWeight(StyleProperty):
    '''Corresponds to tts:fontWeight.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "fontWeight"
    model_prop = styles.StyleProperties.FontWeight

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.FontWeightType[xml_attrib]


  class LineHeight(StyleProperty):
    '''tts:lineHeight'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    model_prop = styles.StyleProperties.LineHeight

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.SpecialValues.normal \
        if xml_attrib == "normal" \
        else StyleProperties.ttml_length_to_model(context, xml_attrib)

  class LinePadding(StyleProperty):
    '''Corresponds to ebutts:linePadding.'''

    ns = "urn:ebu:tt:style"
    local_name = "linePadding"
    model_prop = styles.StyleProperties.LinePadding

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      lp = StyleProperties.ttml_length_to_model(context, xml_attrib)

      if lp.units != styles.LengthType.Units.c:
        raise ValueError("ebutts:linePadding must be expressed in 'c'")


  class LuminanceGain(StyleProperty):
    '''Corresponds to tts:luminanceGain.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "luminanceGain"
    model_prop = styles.StyleProperties.LuminanceGain

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return float(xml_attrib)


  class MultiRowAlign(StyleProperty):
    '''Corresponds to ebutts:multiRowAlign.'''

    ns = "urn:ebu:tt:style"
    local_name = "multiRowAlign"
    model_prop = styles.StyleProperties.MultiRowAlign

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.MultiRowAlignType[xml_attrib]


  class Opacity(StyleProperty):
    '''Corresponds to tts:opacity.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "opacity"
    model_prop = styles.StyleProperties.Opacity

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return float(xml_attrib)


  class Origin(StyleProperty):
    '''Corresponds to tts:origin.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "origin"
    model_prop = styles.StyleProperties.Origin

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):

      if xml_attrib == "auto":

        r = styles.PositionType(
          x=styles.LengthType(0, styles.LengthType.Units.pct),
          y=styles.LengthType(0, styles.LengthType.Units.pct)
        )

      else:
        s = xml_attrib.split(" ")

        if len(s) != 2:
          raise ValueError("tts:origin has not two components")

        r = styles.PositionType(
          x=StyleProperties.ttml_length_to_model(context, s[0]),
          y=StyleProperties.ttml_length_to_model(context, s[1])
        )

      return r

  class Overflow(StyleProperty):
    '''Corresponds to tts:overflow.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "overflow"
    model_prop = styles.StyleProperties.Overflow

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.OverflowType[xml_attrib]


  class Padding(StyleProperty):
    '''Corresponds to tts:padding.'''
    
    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "padding"
    model_prop = styles.StyleProperties.Padding

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      s = xml_attrib.split(" ")

      if len(s) == 1:

        before = end = after = start = StyleProperties.ttml_length_to_model(context, s[0])

      elif len(s) == 2:

        before = after = StyleProperties.ttml_length_to_model(context, s[0])
        end = start = StyleProperties.ttml_length_to_model(context, s[1])

      elif len(s) == 3:

        before = StyleProperties.ttml_length_to_model(context, s[0])
        end = start = StyleProperties.ttml_length_to_model(context, s[1])
        after = StyleProperties.ttml_length_to_model(context, s[2])

      elif len(s) == 4:

        before = StyleProperties.ttml_length_to_model(context, s[0])
        end = StyleProperties.ttml_length_to_model(context, s[1])
        after = StyleProperties.ttml_length_to_model(context, s[2])
        start = StyleProperties.ttml_length_to_model(context, s[3])

      else:

        raise ValueError("Bad syntax")

      return styles.PaddingType(before, end, after, start)

  class Position(StyleProperty):
    '''Corresponds to tts:position.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "position"
    model_prop = styles.StyleProperties.Origin

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):

      return styles.PositionType(
        x=styles.LengthType(),
        y=styles.LengthType()
      )

  class RubyAlign(StyleProperty):
    '''Corresponds to tts:rubyAlign.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "rubyAlign"
    model_prop = styles.StyleProperties.RubyAlign

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.RubyAlignType[xml_attrib]


  class RubyPosition(StyleProperty):
    '''Corresponds to tts:rubyPosition.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "rubyPosition"
    model_prop = styles.StyleProperties.RubyPosition
  
    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.AnnotationPositionType[xml_attrib]

  class RubyReserve(StyleProperty):
    '''Corresponds to tts:rubyReserve.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "rubyReserve"
    model_prop = styles.StyleProperties.RubyReserve

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      
      if xml_attrib == "none":
        return styles.SpecialValues.none

      s = xml_attrib.split(" ")

      if len(s) == 0 or len(s) > 2:
        raise ValueError("Bad syntax")

      rr_pos = styles.RubyReserveType.Position[s[0]]

      rr_length = StyleProperties.ttml_length_to_model(context, s[1]) if len(s) == 2 else None

      return styles.RubyReserveType(rr_pos, rr_length)


  class Shear(StyleProperty):
    '''Corresponds to tts:shear.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "shear"
    model_prop = styles.StyleProperties.Shear

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):

      (value, units) = utils.parse_length(xml_attrib)

      if units != "%":
        raise ValueError(r"tts:shear must be expressed in % units")

      return value if abs(value) <= 100 else math.copysign(100, value)


  class TextAlign(StyleProperty):
    '''Corresponds to tts:textAlign.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "textAlign"
    model_prop = styles.StyleProperties.TextAlign
  
    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      
      if xml_attrib == "left":

        r = styles.TextAlignType.start

      elif xml_attrib == "right":

        r = styles.TextAlignType.end

      else:
      
        r = styles.TextAlignType[xml_attrib]

      return r

  class TextCombine(StyleProperty):
    '''Corresponds to tts:textCombine.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "textCombine"
    model_prop = styles.StyleProperties.TextCombine

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.TextCombineType[xml_attrib]


  class TextDecoration(StyleProperty):
    '''Corresponds to tts:textDecoration.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "textDecoration"
    model_prop = styles.StyleProperties.TextDecoration

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      if xml_attrib == "none":
        return styles.SpecialValues.none

      s = xml_attrib.split(" ")

      underline = styles.TextDecorationType.Action.none
      line_through = styles.TextDecorationType.Action.none
      overline = styles.TextDecorationType.Action.none

      if "underline" in s:
        underline = styles.TextDecorationType.Action.add
      elif "noUnderline" in s:
        underline = styles.TextDecorationType.Action.remove
        
      if "lineThrough" in s:
        line_through = styles.TextDecorationType.Action.add
      elif "noLineThrough" in s:
        line_through = styles.TextDecorationType.Action.remove

      if "overline" in s:
        overline = styles.TextDecorationType.Action.add
      elif "noOverline" in s:
        overline = styles.TextDecorationType.Action.remove

      return styles.TextDecorationType(
        underline=underline,
        line_through=line_through,
        overline=overline
      )

  class TextEmphasis(StyleProperty):
    '''Corresponds to tts:textEmphasis.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "textEmphasis"
    model_prop = styles.StyleProperties.TextEmphasis

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      
      style = None
      symbol = None
      color = None
      position = None

      for c in xml_attrib.split(" "):
        
        if c in styles.TextEmphasisType.Style.__members__:
          
          style = styles.TextEmphasisType.Style[c]

        elif c in styles.TextEmphasisType.Symbol.__members__:

          symbol = styles.TextEmphasisType.Symbol[c]

        elif c in styles.TextEmphasisType.Position.__members__:

          position = styles.TextEmphasisType.Position[c]

        elif c == "current":

          color = None

        else:

          color = utils.parse_color(c)

      if style is None and symbol is None:

        style = styles.TextEmphasisType.Style.auto

      else:

        symbol = symbol or styles.TextEmphasisType.Symbol.circle
        style = style or styles.TextEmphasisType.Style.filled

      position = position or styles.TextEmphasisType.Position.outside

      return styles.TextEmphasisType(
        style=style,
        color=color,
        position=position,
        symbol=symbol
      )
        
  class TextOutline(StyleProperty):
    '''Corresponds to tts:textOutline.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "textOutline"
    model_prop = styles.StyleProperties.TextOutline

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str) -> typing.Union[str, styles.TextOutlineType]:
      
      if xml_attrib == "none":
        return styles.SpecialValues.none

      s = xml_attrib.split(" ")

      if len(s) == 0 or len(s) > 2:
        raise ValueError("Bad syntax")

      thickness = StyleProperties.ttml_length_to_model(context, s[-1])

      color = utils.parse_color(s[0]) if len(s) == 2 else None
      
      return styles.TextOutlineType(
        color=color,
        thickness=thickness
      )

  class TextShadow(StyleProperty):
    '''Corresponds to tts:textShadow.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "textShadow"
    model_prop = styles.StyleProperties.TextShadow

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str) -> typing.Union[str, styles.TextOutlineType]:
      
      if xml_attrib == "none":
        return styles.SpecialValues.none

      shadows = []

      for shadow in xml_attrib.split(","):

        cs = shadow.split(" ")

        if len(cs) < 1 or len(cs) > 4:
          raise ValueError("Invalid Syntax")
        
        x_offset = StyleProperties.ttml_length_to_model(context, cs[0])

        y_offset = StyleProperties.ttml_length_to_model(context, cs[1])

        blur_radius = None
        color = None

        if len(cs) == 3:

          try:

            blur_radius = StyleProperties.ttml_length_to_model(context, cs[2])

          except ValueError:

            color = utils.parse_color(cs[2])

        else: # len(cs) == 4

          blur_radius = StyleProperties.ttml_length_to_model(context, cs[2])
          color = utils.parse_color(cs[3])

        shadows.append(
          styles.TextShadowType.Shadow(
            x_offset=x_offset,
            y_offset=y_offset,
            blur_radius=blur_radius,
            color=color
          )
        )

      return styles.TextShadowType(shadows)

  class UnicodeBidi(StyleProperty):
    '''Corresponds to tts:unicodeBidi.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "unicodeBidi"
    model_prop = styles.StyleProperties.UnicodeBidi

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.UnicodeBidiType[xml_attrib]

  class Visibility(StyleProperty):
    '''Corresponds to tts:visibility.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "visibility"
    model_prop = styles.StyleProperties.Visibility
    
    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.VisibilityType[xml_attrib]

  class WrapOption(StyleProperty):
    '''Corresponds to tts:wrapOption.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "wrapOption"
    model_prop = styles.StyleProperties.WrapOption

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.WrapOptionType[xml_attrib]

  class WritingMode(StyleProperty):
    '''Corresponds to tts:writingMode.'''

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "writingMode"
    model_prop = styles.StyleProperties.WritingMode

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):

      if xml_attrib == "lr":
        return styles.WritingModeType.lrtb

      if xml_attrib == "rl":
        return styles.WritingModeType.rltb

      if xml_attrib == "tb":
        return styles.WritingModeType.tbrl

      return styles.WritingModeType[xml_attrib]

  BY_QNAME = {
    f"{{{v.ns}}}{v.local_name}" : v
    for n, v in list(locals().items()) if inspect.isclass(v)
    }

  @classmethod
  def ttml_length_to_model(cls, _context: StyleParsingContext, xml_attrib: str):
    (value, units) = utils.parse_length(xml_attrib)

    return styles.LengthType(value, styles.LengthType.Units(units))
