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
import ttconv.model as model

class StyleParsingContext:
  doc: model.ContentDocument

class StyleProperty:
  '''Base class for style properties'''

  @property
  @classmethod
  def model_prop(cls):
    raise NotImplementedError

  @property
  @classmethod
  def ns(cls): # pylint: disable=invalid-name
    raise NotImplementedError

  @property
  @classmethod
  def local_name(cls):
    raise NotImplementedError

  @classmethod
  def has_px(cls, _attrib_value: typing.Any) -> bool:
    return False

  @classmethod
  def extract(cls, context: StyleParsingContext, xml_attrib: str):
    '''Converts an IMSC style property to a data model value'''
    raise NotImplementedError

  @classmethod
  def to_model(cls, context: StyleParsingContext, xml_element) -> typing.Tuple[model.StyleProperty, typing.Any]:
    '''Extracts the value of the style property from a TTML element and returns a tuple consisting of 
    the matching model style property and the value of the model style property'''
    return (
      cls.model_prop,
      cls.extract(context, xml_element.get(f"{{{cls.ns}}}{cls.local_name}"))
    )

  @classmethod
  def from_model(cls, xml_element, model_value):
    '''Converts an data model value to an IMSC style property'''
    raise NotImplementedError

class StyleProperties:
  '''TTML style properties

  Class variables:
  
  `BY_QNAME`: mapping of qualified name to StyleProperty class
  `BY_MODEL_PROP`: mapping of model style property classes to StyleProperty classes
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
    def from_model(cls, xml_element, model_value: styles.ColorType):
      if model_value != styles.NamedColors.transparent.value:
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
    def from_model(cls, xml_element, model_value):
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
    def from_model(cls, xml_element, model_value):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class Disparity(StyleProperty):
    '''Corresponds to tts:disparity.
    '''

    ns = xml_ns.TTS
    local_name = "disparity"
    model_prop = styles.StyleProperties.Disparity

    @classmethod
    def has_px(cls, attrib_value: styles.LengthType) -> bool:
      return attrib_value.units == styles.LengthType.Units.px 

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return StyleProperties.ttml_length_to_model(context, xml_attrib)

    @classmethod
    def from_model(cls, xml_element, model_value: styles.LengthType):
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
    def from_model(cls, xml_element, model_value: styles.DisplayType):
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
    def from_model(cls, xml_element, model_value: styles.DisplayAlignType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class Extent(StyleProperty):
    '''Corresponds to tts:extent.
    '''

    ns = xml_ns.TTS
    local_name = "extent"
    model_prop = styles.StyleProperties.Extent

    @classmethod
    def has_px(cls, attrib_value: styles.ExtentType) -> bool:
      return attrib_value.height.units == styles.LengthType.Units.px or \
        attrib_value.width.units == styles.LengthType.Units.px

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
    def from_model(cls, xml_element, model_value):
      xml_element.set(
        f"{{{cls.ns}}}{cls.local_name}", 
        f"{StyleProperties.to_ttml_length(model_value.width)}"
        f" {StyleProperties.to_ttml_length(model_value.height)}"
      )


  class FillLineGap(StyleProperty):
    '''Corresponds to itts:fillLineGap.'''

    ns = xml_ns.ITTS
    local_name = "fillLineGap"
    model_prop = styles.StyleProperties.FillLineGap

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return xml_attrib == "true"

    @classmethod
    def from_model(cls, xml_element, model_value: bool):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", "true" if model_value else "false")


  class FontFamily(StyleProperty):
    '''Corresponds to tts:fontFamily.'''

    ns = xml_ns.TTS
    local_name = "fontFamily"
    model_prop = styles.StyleProperties.FontFamily

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):

      return tuple(
        map(
          lambda f: styles.GenericFontFamilyType.monospaceSerif if f is styles.GenericFontFamilyType.default else f,
          utils.parse_font_families(xml_attrib)
        )
      )

    @classmethod
    def from_model(cls, xml_element, model_value):
      xml_element.set(
        f"{{{cls.ns}}}{cls.local_name}",
        utils.serialize_font_family(model_value)
    )


  class FontSize(StyleProperty):
    '''Corresponds to tts:fontSize.'''

    ns = xml_ns.TTS
    local_name = "fontSize"
    model_prop = styles.StyleProperties.FontSize

    @classmethod
    def has_px(cls, attrib_value: styles.LengthType) -> bool:
      return attrib_value.units == styles.LengthType.Units.px 

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return StyleProperties.ttml_length_to_model(context, xml_attrib)

    @classmethod
    def from_model(cls, xml_element, model_value):
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
    def from_model(cls, xml_element, model_value: styles.FontStyleType):
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
    def from_model(cls, xml_element, model_value: styles.FontWeightType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class LineHeight(StyleProperty):
    '''tts:lineHeight'''

    ns = xml_ns.TTS
    local_name = "lineHeight"
    model_prop = styles.StyleProperties.LineHeight

    @classmethod
    def has_px(cls, attrib_value: styles.LengthType) -> bool:
      if attrib_value is not styles.SpecialValues.normal:
        return attrib_value.units == styles.LengthType.Units.px

      return False

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.SpecialValues.normal \
        if xml_attrib == "normal" \
        else StyleProperties.ttml_length_to_model(context, xml_attrib)

    @classmethod
    def from_model(cls, xml_element, model_value):
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

      return lp

    @classmethod
    def from_model(cls, xml_element, model_value: styles.LengthType):
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
    def from_model(cls, xml_element, model_value):
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
    def from_model(cls, xml_element, model_value: styles.MultiRowAlignType):
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
    def from_model(cls, xml_element, model_value):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", f"{model_value}")


  class Origin(StyleProperty):
    '''Corresponds to tts:origin.'''

    ns = xml_ns.TTS
    local_name = "origin"
    model_prop = styles.StyleProperties.Origin

    @classmethod
    def has_px(cls, attrib_value: styles.CoordinateType) -> bool:
      return attrib_value.x.units == styles.LengthType.Units.px or \
        attrib_value.y.units == styles.LengthType.Units.px

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):

      if xml_attrib == "auto":

        r = styles.CoordinateType(
          x=styles.LengthType(0, styles.LengthType.Units.pct),
          y=styles.LengthType(0, styles.LengthType.Units.pct)
        )

      else:
        s = xml_attrib.split(" ")

        if len(s) != 2:
          raise ValueError("tts:origin has not two components")

        r = styles.CoordinateType(
          x=StyleProperties.ttml_length_to_model(context, s[0]),
          y=StyleProperties.ttml_length_to_model(context, s[1])
        )

      return r

    @classmethod
    def from_model(cls, xml_element, model_value):
      xml_element.set(
        f"{{{cls.ns}}}{cls.local_name}", 
        f"{model_value.x.value:g}{model_value.x.units.value} {model_value.y.value:g}{model_value.y.units.value}"
      )


  class Overflow(StyleProperty):
    '''Corresponds to tts:overflow.'''

    ns = xml_ns.TTS
    local_name = "overflow"
    model_prop = styles.StyleProperties.Overflow

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.OverflowType[xml_attrib]

    @classmethod
    def from_model(cls, xml_element, model_value: styles.OverflowType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class Padding(StyleProperty):
    '''Corresponds to tts:padding.'''
    
    ns = xml_ns.TTS
    local_name = "padding"
    model_prop = styles.StyleProperties.Padding

    @classmethod
    def has_px(cls, attrib_value: styles.PaddingType) -> bool:
      return attrib_value.after.units == styles.LengthType.Units.px or \
        attrib_value.before.units == styles.LengthType.Units.px or \
        attrib_value.start.units == styles.LengthType.Units.px or \
        attrib_value.end.units == styles.LengthType.Units.px

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
    def from_model(cls, xml_element, model_value: styles.PaddingType):
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
    model_prop = styles.StyleProperties.Position

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):

      (h_edge, h_offset, v_edge, v_offset) = utils.parse_position(xml_attrib)

      return styles.PositionType(
        h_offset=h_offset,
        v_offset=v_offset,
        h_edge=styles.PositionType.HEdge(h_edge),
        v_edge=styles.PositionType.VEdge(v_edge)
      )

    @classmethod
    def from_model(cls, xml_element, model_value: styles.PositionType):
      xml_element.set(
        f"{{{cls.ns}}}{cls.local_name}", 
        f"{model_value.h_edge.value} " \
        f"{model_value.h_offset.value:g}{model_value.h_offset.units.value} " \
        f"{model_value.v_edge.value} " \
        f"{model_value.v_offset.value:g}{model_value.v_offset.units.value}"
      )


  class RubyAlign(StyleProperty):
    '''Corresponds to tts:rubyAlign.'''

    ns = xml_ns.TTS
    local_name = "rubyAlign"
    model_prop = styles.StyleProperties.RubyAlign

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.RubyAlignType[xml_attrib]

    @classmethod
    def from_model(cls, xml_element, model_value: styles.RubyAlignType):
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
    def from_model(cls, xml_element, model_value: styles.AnnotationPositionType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class RubyReserve(StyleProperty):
    '''Corresponds to tts:rubyReserve.'''

    ns = xml_ns.TTS
    local_name = "rubyReserve"
    model_prop = styles.StyleProperties.RubyReserve

    @classmethod
    def has_px(cls, attrib_value: styles.RubyReserveType) -> bool:
      return attrib_value.length is not None and attrib_value.length.units == styles.LengthType.Units.px

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
    def from_model(cls, xml_element, model_value):
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
    def from_model(cls, xml_element, model_value: float):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", f"{model_value}%")


  class ShowBackground(StyleProperty):
    '''Corresponds to tts:showBackground.'''

    ns = xml_ns.TTS
    local_name = "showBackground"
    model_prop = styles.StyleProperties.ShowBackground
    
    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      return styles.ShowBackgroundType[xml_attrib]

    @classmethod
    def from_model(cls, xml_element, model_value: styles.VisibilityType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


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
    def from_model(cls, xml_element, model_value: styles.TextAlignType):
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
    def from_model(cls, xml_element, model_value: styles.TextCombineType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  class TextDecoration(StyleProperty):
    '''Corresponds to tts:textDecoration.'''

    ns = xml_ns.TTS
    local_name = "textDecoration"
    model_prop = styles.StyleProperties.TextDecoration




    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str):
      
      if xml_attrib == "none":

        underline = False
        line_through = False
        overline = False

      else:

        s = xml_attrib.split(" ")

        underline = None
        line_through = None
        overline = None

        if "underline" in s:
          underline = True
        elif "noUnderline" in s:
          underline = False
          
        if "lineThrough" in s:
          line_through = True
        elif "noLineThrough" in s:
          line_through = False

        if "overline" in s:
          overline = True
        elif "noOverline" in s:
          overline = False

      return styles.TextDecorationType(
        underline=underline,
        line_through=line_through,
        overline=overline
      )

    @classmethod
    def from_model(cls, xml_element, model_value: styles.TextDecorationType):
      
      actual_values = []

      if model_value.underline is True:
        actual_values.append("underline")
      elif model_value.underline is False:
        actual_values.append("noUnderline")

      if model_value.line_through is True:
        actual_values.append("lineThrough")
      elif model_value.line_through is False:
        actual_values.append("noLineThrough")

      if model_value.overline is True:
        actual_values.append("overline")
      elif model_value.overline is False:
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
      style_style = None
      style_symbol = None
      color = None
      position = None

      for c in xml_attrib.split(" "):

        if c == "none":

          return styles.SpecialValues.none

        if c == "auto":

          style = styles.TextEmphasisType.Style.auto

        elif c in ("filled", "open"):
          
          style_style = c

        elif c in ("circle", "dot", "sesame"):

          style_symbol = c

        elif c in styles.TextEmphasisType.Position.__members__:

          position = styles.TextEmphasisType.Position[c]

        elif c == "current":

          color = None

        else:

          color = utils.parse_color(c)

      if style_style is None and style_symbol is None:

        style = styles.TextEmphasisType.Style.auto

      else:

        style_style = style_style if style_style is not None else "circle"
        style_symbol = style_symbol if style_symbol is not None else "filled"
        style = styles.TextEmphasisType.Style(f"{style_style} {style_symbol}")

      position = position if position is not None else styles.TextEmphasisType.Position.outside

      return styles.TextEmphasisType(
        style=style,
        color=color,
        position=position
      )

    @classmethod
    def from_model(cls, xml_element, model_value: styles.TextEmphasisType):
      actual_values = []

      actual_values.append(model_value.style.value)

      if model_value.color is not None:
        actual_values.append(StyleProperties.to_ttml_color(model_value.color))

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
    def has_px(cls, attrib_value: styles.TextOutlineType) -> bool:
      if attrib_value is not styles.SpecialValues.none:
        return attrib_value.thickness.units == styles.LengthType.Units.px

      return False

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str) -> typing.Union[styles.TextOutlineType, styles.SpecialValues]:
      
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
    def from_model(cls, xml_element, model_value):
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
    def has_px(cls, attrib_value: styles.TextShadowType) -> bool:

      for shadow in attrib_value.shadows:
        if shadow.x_offset.units == styles.LengthType.Units.px or \
          shadow.y_offset.units == styles.LengthType.Units.px:
          return True
        if shadow.blur_radius is not None:
          if shadow.blur_radius.units == styles.LengthType.Units.px:
            return True
      
      return False

    @classmethod
    def extract(cls, context: StyleParsingContext, xml_attrib: str) -> typing.Union[styles.TextShadowType, styles.SpecialValues]:
      
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

      return styles.TextShadowType(tuple(shadows))

    @classmethod
    def from_model(cls, xml_element, model_value):
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
    def from_model(cls, xml_element, model_value: styles.UnicodeBidiType):
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
    def from_model(cls, xml_element, model_value: styles.VisibilityType):
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
    def from_model(cls, xml_element, model_value: styles.WrapOptionType):
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
    def from_model(cls, xml_element, model_value: styles.WritingModeType):
      xml_element.set(f"{{{cls.ns}}}{cls.local_name}", model_value.value)


  BY_QNAME = {
    f"{{{style_prop.ns}}}{style_prop.local_name}" : style_prop
    for style_name, style_prop in list(locals().items()) if inspect.isclass(style_prop)
    }

  BY_MODEL_PROP = {
    style_prop.model_prop : style_prop
    for style_name, style_prop in list(locals().items()) if inspect.isclass(style_prop) and style_prop.model_prop is not None
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
    if model_value.components[3] != 0xFF:
      color_str = f"{color_str}{model_value.components[3]:02x}"
    
    return color_str

  @staticmethod
  def to_ttml_length(model_value: styles.LengthType):
    return f"{model_value.value:g}{model_value.units.value}"
