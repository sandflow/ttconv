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
import ttconv.imsc.namespaces as xml_ns
import ttconv.style_properties as styles
import ttconv.imsc.utils as utils

class StyleParsingContext:
  pass

class StyleProperty:
  '''Base class for style properties'''

  @classmethod
  def extract(cls, context: StyleParsingContext, xml_attrib: str):
    '''Converts an IMSC style property to a data model value'''

  @classmethod
  def set(cls, xml_element, model_value):
    '''Converts an data model value to an IMSC style property'''

class StyleProperties:
  '''TTML style properties

  Class variables:
  
  `BY_QNAME`: mapping of qualified name to StyleProperty class
  '''

  class BackgroundColor(StyleProperty):
    '''Corresponds to tts:backgroundColor.'''

    ns = xml_ns.TTS
    local_name = "backgroundColor"
    model_prop = styles.StyleProperties.BackgroundColor

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return utils.parse_color(xml_attrib)

    @classmethod
    def set(cls, xml_element, model_value: styles.ColorType):
      xml_element.set(
        f"{{{cls.ns}}}{cls.local_name}",
        StyleProperties.to_ttml_color(model_value)
      )

  class Color(StyleProperty):
    '''Corresponds to tts:color.'''

    ns = xml_ns.TTS
    local_name = "color"
    model_prop = styles.StyleProperties.Color

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return utils.parse_color(xml_attrib)

    @classmethod
    def set(cls, xml_element, model_value):
      xml_element.set(
        f"{{{cls.ns}}}{cls.local_name}",
        StyleProperties.to_ttml_color(model_value)
      )

  class Direction(StyleProperty):
    '''Corresponds to tts:direction.'''

    ns = xml_ns.TTS
    local_name = "direction"
    model_prop = styles.StyleProperties.Direction

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.DirectionType[xml_attrib]

    @classmethod
    def set(cls, xml_element, model_value):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class Disparity(StyleProperty):
    '''Corresponds to tts:disparity.
    '''

    ns = xml_ns.TTS
    local_name = "disparity"
    model_prop = styles.StyleProperties.Disparity

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return StyleProperties.ttml_length_to_model(context, xml_attrib)

    @classmethod
    def set(cls, xml_element, model_value: styles.LengthType):
      xml_element.set(
        f"{{{cls.ns}}}{cls.local_name}",
        StyleProperties.to_ttml_length(model_value)
      )
      
      
  class Display(StyleProperty):
    '''Corresponds to tts:display.'''

    ns = xml_ns.TTS
    local_name = "display"
    model_prop = styles.StyleProperties.Display

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.DisplayType[xml_attrib]

    @classmethod
    def set(cls, xml_element, model_value: styles.DisplayType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class DisplayAlign(StyleProperty):
    '''Corresponds to tts:displayAlign.'''

    ns = xml_ns.TTS
    local_name = "displayAlign"
    model_prop = styles.StyleProperties.DisplayAlign

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.DisplayAlignType[xml_attrib]

    @classmethod
    def set(cls, xml_element, model_value: styles.DisplayAlignType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class Extent(StyleProperty):
    '''Corresponds to tts:extent.
    '''

    ns = xml_ns.TTS
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

    @classmethod
    def set(cls, xml_element, model_value):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", 
      f"{model_value.height.value}{model_value.height.units.value} {model_value.width.value}{model_value.width.units.value}")


  class FillLineGap(StyleProperty):
    '''Corresponds to itts:fillLineGap.'''

    ns = xml_ns.ITTS
    local_name = "fillLineGap"
    model_prop = styles.StyleProperties.FillLineGap

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return xml_attrib == "true"

    @classmethod
    def set(cls, xml_element, model_value: bool):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", "true" if model_value else "false")


  class FontFamily(StyleProperty):
    '''Corresponds to tts:fontFamily.'''

    ns = xml_ns.TTS
    local_name = "fontFamily"
    model_prop = styles.StyleProperties.FontFamily

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):

      return list(map(
        lambda f: "monospaceSerif" if f == "default" else f,
        utils.parse_font_families(xml_attrib)
      ))

    @classmethod
    def set(cls, xml_element, model_value):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value[0])


  class FontSize(StyleProperty):
    '''Corresponds to tts:fontSize.'''

    ns = xml_ns.TTS
    local_name = "fontSize"
    model_prop = styles.StyleProperties.FontSize

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return StyleProperties.ttml_length_to_model(context, xml_attrib)

    @classmethod
    def set(cls, xml_element, model_value):
      xml_element.set(
        f"{{{cls.ns}}}{cls.local_name}", 
        StyleProperties.to_ttml_length(model_value)
      )


  class FontStyle(StyleProperty):
    '''Corresponds to tts:fontStyle.'''

    ns = xml_ns.TTS
    local_name = "fontStyle"
    model_prop = styles.StyleProperties.FontStyle

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.FontStyleType[xml_attrib]

    @classmethod
    def set(cls, xml_element, model_value: styles.FontStyleType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class FontWeight(StyleProperty):
    '''Corresponds to tts:fontWeight.'''

    ns = xml_ns.TTS
    local_name = "fontWeight"
    model_prop = styles.StyleProperties.FontWeight

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.FontWeightType[xml_attrib]

    @classmethod
    def set(cls, xml_element, model_value: styles.FontWeightType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class LineHeight(StyleProperty):
    '''tts:lineHeight'''

    ns = xml_ns.TTS
    local_name = "lineHeight"
    model_prop = styles.StyleProperties.LineHeight

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.SpecialValues.normal \
        if xml_attrib == "normal" \
        else StyleProperties.ttml_length_to_model(context, xml_attrib)

    @classmethod
    def set(cls, xml_element, model_value):
      xml_element.set(
        f"{{{cls.ns}}}{cls.local_name}", 
        StyleProperties.to_ttml_length(model_value) \
          if model_value is not styles.SpecialValues.normal \
          else "normal"
      )


  class LinePadding(StyleProperty):
    '''Corresponds to ebutts:linePadding.'''

    ns = xml_ns.EBUTTS
    local_name = "linePadding"
    model_prop = styles.StyleProperties.LinePadding

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      lp = StyleProperties.ttml_length_to_model(context, xml_attrib)

      if lp.units != styles.LengthType.Units.c:
        raise ValueError("ebutts:linePadding must be expressed in 'c'")

    @classmethod
    def set(cls, xml_element, model_value: styles.LengthType):
      xml_element.set(
        f"{{{cls.ns}}}{cls.local_name}",
        StyleProperties.to_ttml_length(model_value)
        )


  class LuminanceGain(StyleProperty):
    '''Corresponds to tts:luminanceGain.'''

    ns = xml_ns.TTS
    local_name = "luminanceGain"
    model_prop = styles.StyleProperties.LuminanceGain

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return float(xml_attrib)

    @classmethod
    def set(cls, xml_element, model_value):
      xml_element.set(
        f"{{{cls.ns}}}{cls.local_name}",
        f"{model_value}"
      )


  class MultiRowAlign(StyleProperty):
    '''Corresponds to ebutts:multiRowAlign.'''

    ns = xml_ns.EBUTTS
    local_name = "multiRowAlign"
    model_prop = styles.StyleProperties.MultiRowAlign

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.MultiRowAlignType[xml_attrib]

    @classmethod
    def set(cls, xml_element, model_value: styles.MultiRowAlignType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class Opacity(StyleProperty):
    '''Corresponds to tts:opacity.'''

    ns = xml_ns.TTS
    local_name = "opacity"
    model_prop = styles.StyleProperties.Opacity

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return float(xml_attrib)

    @classmethod
    def set(cls, xml_element, model_value):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", f"{model_value}")


  class Origin(StyleProperty):
    '''Corresponds to tts:origin.'''

    ns = xml_ns.TTS
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

    @classmethod
    def set(cls, xml_element, model_value):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", 
      f"{model_value.x.value}{model_value.x.units.value} {model_value.y.value}{model_value.y.units.value}")


  class Overflow(StyleProperty):
    '''Corresponds to tts:overflow.'''

    ns = xml_ns.TTS
    local_name = "overflow"
    model_prop = styles.StyleProperties.Overflow

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.OverflowType[xml_attrib]

    @classmethod
    def set(cls, xml_element, model_value: styles.OverflowType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class Padding(StyleProperty):
    '''Corresponds to tts:padding.'''
    
    ns = xml_ns.TTS
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

    @classmethod
    def set(cls, xml_element, model_value: styles.PaddingType):
      xml_element.set(
        f"{{{cls.ns}}}{cls.local_name}",
        f"{StyleProperties.to_ttml_length(model_value.before)}"
        f" {StyleProperties.to_ttml_length(model_value.end)}"
        f" {StyleProperties.to_ttml_length(model_value.after)}"
        f" {StyleProperties.to_ttml_length(model_value.start)}"
      )


  class Position(StyleProperty):
    '''Corresponds to tts:position.'''

    ns = xml_ns.TTS
    local_name = "position"
    model_prop = styles.StyleProperties.Origin

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):

      return styles.PositionType(
        x=styles.LengthType(),
        y=styles.LengthType()
      )

    @classmethod
    def set(cls, xml_element, model_value):
      # TODO: the data model does not support tts:position
      pass


  class RubyAlign(StyleProperty):
    '''Corresponds to tts:rubyAlign.'''

    ns = xml_ns.TTS
    local_name = "rubyAlign"
    model_prop = styles.StyleProperties.RubyAlign

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.RubyAlignType[xml_attrib]

    @classmethod
    def set(cls, xml_element, model_value: styles.RubyAlignType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class RubyPosition(StyleProperty):
    '''Corresponds to tts:rubyPosition.'''

    ns = xml_ns.TTS
    local_name = "rubyPosition"
    model_prop = styles.StyleProperties.RubyPosition
  
    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.AnnotationPositionType[xml_attrib]

    @classmethod
    def set(cls, xml_element, model_value: styles.AnnotationPositionType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class RubyReserve(StyleProperty):
    '''Corresponds to tts:rubyReserve.'''

    ns = xml_ns.TTS
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

    @classmethod
    def set(cls, xml_element, model_value):
      if isinstance(model_value, styles.RubyReserveType):
        value = model_value.position.value
        if model_value.length is not None:
          value += f" {StyleProperties.to_ttml_length(model_value.length)}"
      elif model_value == styles.SpecialValues.none:
        value = model_value.value
      else:
        raise TypeError

      xml_element.set(
        f"{{{cls.ns}}}{cls.local_name}",
        value
      )


  class Shear(StyleProperty):
    '''Corresponds to tts:shear.'''

    ns = xml_ns.TTS
    local_name = "shear"
    model_prop = styles.StyleProperties.Shear

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):

      (value, units) = utils.parse_length(xml_attrib)

      if units != "%":
        raise ValueError(r"tts:shear must be expressed in % units")

      return value if abs(value) <= 100 else math.copysign(100, value)

    @classmethod
    def set(cls, xml_element, model_value: float):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", f"{model_value}%")


  class TextAlign(StyleProperty):
    '''Corresponds to tts:textAlign.'''

    ns = xml_ns.TTS
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

    @classmethod
    def set(cls, xml_element, model_value: styles.TextAlignType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class TextCombine(StyleProperty):
    '''Corresponds to tts:textCombine.'''

    ns = xml_ns.TTS
    local_name = "textCombine"
    model_prop = styles.StyleProperties.TextCombine

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.TextCombineType[xml_attrib]

    @classmethod
    def set(cls, xml_element, model_value: styles.TextCombineType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class TextDecoration(StyleProperty):
    '''Corresponds to tts:textDecoration.'''

    ns = xml_ns.TTS
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

    @classmethod
    def set(cls, xml_element, model_value: styles.TextDecorationType):
      
      if model_value == styles.SpecialValues.none:
        attrib_value = "none"
      else:
        actual_values = []

        if model_value.underline == styles.TextDecorationType.Action.add:
          actual_values.append("underline")
        elif model_value.underline == styles.TextDecorationType.Action.remove:
          actual_values.append("noUnderline")

        if model_value.line_through == styles.TextDecorationType.Action.add:
          actual_values.append("lineThrough")
        elif model_value.line_through == styles.TextDecorationType.Action.remove:
          actual_values.append("noLineThrough")

        if model_value.overline == styles.TextDecorationType.Action.add:
          actual_values.append("overline")
        elif model_value.overline == styles.TextDecorationType.Action.remove:
          actual_values.append("noOverline")

        attrib_value = " ".join(actual_values)

      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", attrib_value)


  class TextEmphasis(StyleProperty):
    '''Corresponds to tts:textEmphasis.'''

    ns = xml_ns.TTS
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

    @classmethod
    def set(cls, xml_element, model_value: styles.TextEmphasisType):
      actual_values = []

      actual_values.append(model_value.style.value)

      if model_value.symbol is not None:
        actual_values.append(model_value.symbol.value)

      if model_value.color is not None:
        actual_values.append(StyleProperties.to_ttml_color(model_value.color))

      if model_value.position is not None:
        actual_values.append(model_value.position.value) 

      xml_element.set(
        f"{{{cls.ns}}}{cls.local_name}",
        " ".join(actual_values)
      )


  class TextOutline(StyleProperty):
    '''Corresponds to tts:textOutline.'''

    ns = xml_ns.TTS
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

    @classmethod
    def set(cls, xml_element, model_value):
      if isinstance(model_value, styles.TextOutlineType):
        values = []

        if model_value.color is not None:
          values.append(StyleProperties.to_ttml_color(model_value.color))

        if model_value.thickness is not None:
          values.append(StyleProperties.to_ttml_length(model_value.thickness))

      elif model_value == styles.SpecialValues.none:
        values = [model_value.value]
      else:
        raise TypeError
      
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", " ".join(values))


  class TextShadow(StyleProperty):
    '''Corresponds to tts:textShadow.'''

    ns = xml_ns.TTS
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

    @classmethod
    def set(cls, xml_element, model_value):
      if isinstance(model_value, styles.TextShadowType):
        actual_values = []

        for shadow in model_value.shadows:
          value = f"{StyleProperties.to_ttml_length(shadow.x_offset)}" \
                    f" {StyleProperties.to_ttml_length(shadow.y_offset)}"
          
          if shadow.blur_radius is not None:
            value += f" {StyleProperties.to_ttml_length(shadow.blur_radius)}"

          if shadow.color is not None:
            value += f" {StyleProperties.to_ttml_color(shadow.color)}"

          actual_values.append(value)

      elif model_value == styles.SpecialValues.none:

        actual_values = [model_value.value]

      else:

        raise TypeError

      xml_element.set(
        f"{{{cls.ns}}}{cls.local_name}",
        ", ".join(actual_values)
      )


  class UnicodeBidi(StyleProperty):
    '''Corresponds to tts:unicodeBidi.'''

    ns = xml_ns.TTS
    local_name = "unicodeBidi"
    model_prop = styles.StyleProperties.UnicodeBidi

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.UnicodeBidiType[xml_attrib]

    @classmethod
    def set(cls, xml_element, model_value: styles.UnicodeBidiType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class Visibility(StyleProperty):
    '''Corresponds to tts:visibility.'''

    ns = xml_ns.TTS
    local_name = "visibility"
    model_prop = styles.StyleProperties.Visibility
    
    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.VisibilityType[xml_attrib]

    @classmethod
    def set(cls, xml_element, model_value: styles.VisibilityType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class WrapOption(StyleProperty):
    '''Corresponds to tts:wrapOption.'''

    ns = xml_ns.TTS
    local_name = "wrapOption"
    model_prop = styles.StyleProperties.WrapOption

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.WrapOptionType[xml_attrib]

    @classmethod
    def set(cls, xml_element, model_value: styles.WrapOptionType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class WritingMode(StyleProperty):
    '''Corresponds to tts:writingMode.'''

    ns = xml_ns.TTS
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

    @classmethod
    def set(cls, xml_element, model_value: styles.WritingModeType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  BY_QNAME = {
    f"{{{v.ns}}}{v.local_name}" : v
    for n, v in list(locals().items()) if inspect.isclass(v)
    }

  BY_MODEL_PROP = {
    v.model_prop : v
    for n, v in list(locals().items()) if inspect.isclass(v)
    }

  @classmethod
  def ttml_length_to_model(cls, _context: StyleParsingContext, xml_attrib: str):
    (value, units) = utils.parse_length(xml_attrib)

    return styles.LengthType(value, styles.LengthType.Units(units))

  @staticmethod
  def to_ttml_color(model_value: styles.ColorType):
    assert model_value.ident == styles.ColorType.Colorimetry.RGBA8
    color_str = f"#{model_value.components[0]:02x}" \
                 f"{model_value.components[1]:02x}"  \
                 f"{model_value.components[2]:02x}"
    if not model_value.components[3] & 0xFF:
       color_str = f"{color_str}{model_value.components[3]:02x}"
    
    return color_str

  @staticmethod
  def to_ttml_length(model_value: styles.LengthType):
    return f"{model_value.value}{model_value.units.value}"
