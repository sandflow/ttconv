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

'''Process IMSC non-style attributes'''

import re
import logging
import math
from fractions import Fraction
import typing
from dataclasses import dataclass
from enum import Enum
from ttconv.time_code import SmpteTimeCode
import ttconv.model as model
import ttconv.imsc.utils as utils
import ttconv.imsc.namespaces as ns
from ttconv.time_code import ClockTime

LOGGER = logging.getLogger(__name__)

class XMLIDAttribute:
  '''xml:id attribute
  '''

  qn = f'{{{ns.XML}}}id'

  @staticmethod
  def extract(ttml_element):
    return ttml_element.attrib.get(XMLIDAttribute.qn)

  @staticmethod
  def set(xml_element, model_value):
    xml_element.set(XMLIDAttribute.qn, model_value)

class XMLLangAttribute:
  '''xml:lang attribute
  '''

  qn = f'{{{ns.XML}}}lang'

  @staticmethod
  def extract(ttml_element):
    return ttml_element.attrib.get(XMLLangAttribute.qn)

  @staticmethod
  def set(ttml_element, lang):
    ttml_element.set(XMLLangAttribute.qn, lang)

class XMLSpaceAttribute:
  '''xml:space attribute
  '''

  qn = f'{{{ns.XML}}}space'

  @staticmethod
  def extract(ttml_element):

    value = ttml_element.attrib.get(XMLSpaceAttribute.qn)

    r = None

    if value is not None:

      try: 
        r = model.WhiteSpaceHandling(value)
      except ValueError:
        LOGGER.error("Bad xml:space value (%s)", value)
    
    return r

  @staticmethod
  def set(ttml_element, xml_space: model.WhiteSpaceHandling):
    ttml_element.set(XMLSpaceAttribute.qn, xml_space.value)


class RegionAttribute:
  '''TTML region attribute'''

  qn = "region"

  @staticmethod
  def extract(ttml_element) -> typing.Optional[str]:
    return ttml_element.attrib.get(RegionAttribute.qn)

  @staticmethod
  def set(ttml_element, region_id: str):
    ttml_element.set(RegionAttribute.qn, region_id)


class CellResolutionAttribute:
  '''ttp:cellResolution attribute
  '''

  qn = f"{{{ns.TTP}}}cellResolution"

  _CELL_RESOLUTION_RE = re.compile(r"(\d+) (\d+)")

  @staticmethod
  def extract(ttml_element) -> model.CellResolutionType:

    cr = ttml_element.attrib.get(CellResolutionAttribute.qn)

    if cr is not None:

      m = CellResolutionAttribute._CELL_RESOLUTION_RE.match(cr)

      if m is not None:

        return model.CellResolutionType(int(m.group(1)), int(m.group(2)))

      LOGGER.error("ttp:cellResolution invalid syntax")

    # default value in TTML

    return model.CellResolutionType(rows=15, columns=32)

  @staticmethod
  def set(ttml_element, res):
    ttml_element.set(CellResolutionAttribute.qn, f"{res.columns} {res.rows}")

class ExtentAttribute:
  '''ttp:extent attribute on \\<tt\\>
  '''

  qn = f"{{{ns.TTS}}}extent"

  @staticmethod
  def extract(ttml_element) -> typing.Optional[model.PixelResolutionType]:

    extent = ttml_element.attrib.get(ExtentAttribute.qn)

    if extent is not None:

      s = extent.split(" ")

      (w, w_units) = utils.parse_length(s[0])

      (h, h_units) = utils.parse_length(s[1])

      if w_units != "px" or h_units != "px":
        LOGGER.error("ttp:extent on <tt> does not use px units")
        return None

      if not w.is_integer() or not h.is_integer():
        LOGGER.error("Pixel resolution dimensions must be integer values")

      return model.PixelResolutionType(int(w), int(h))

    return None

  @staticmethod
  def set(ttml_element, res):
    ttml_element.set(ExtentAttribute.qn, f"{res.width:g}px {res.height:g}px")

class ActiveAreaAttribute:
  '''ittp:activeArea attribute on \\<tt\\>
  '''

  qn = f"{{{ns.ITTP}}}activeArea"

  @staticmethod
  def extract(ttml_element) -> typing.Optional[model.ActiveAreaType]:

    aa = ttml_element.attrib.get(ActiveAreaAttribute.qn)

    if aa is not None:

      s = aa.split(" ")

      if len(s) != 4:
        LOGGER.error("Syntax error in ittp:activeArea on <tt>")
        return None

      (left_offset, left_offset_units) = utils.parse_length(s[0])

      (top_offset, top_offset_units) = utils.parse_length(s[1])

      (w, w_units) = utils.parse_length(s[2])

      (h, h_units) = utils.parse_length(s[3])

      if w_units != "%" or h_units != "%" or left_offset_units != "%" or top_offset_units != "%":
        LOGGER.error("ittp:activeArea on <tt> must use % units")
        return None

      return model.ActiveAreaType(
        left_offset / 100,
        top_offset / 100,
        w / 100,
        h / 100
        )

    return None

  @staticmethod
  def set(ttml_element, active_area):
    ttml_element.set(
      ActiveAreaAttribute.qn, 
      f"{active_area.left_offset * 100:g}% "
      f"{active_area.top_offset * 100:g}% "
      f"{active_area.width * 100:g}% "
      f"{active_area.height * 100:g}%"
    )

class TickRateAttribute:
  '''ttp:tickRate attribute
  '''

  qn = f"{{{ns.TTP}}}tickRate"

  _TICK_RATE_RE = re.compile(r"(\d+)")

  @staticmethod
  def extract(ttml_element) -> int:

    tr = ttml_element.attrib.get(TickRateAttribute.qn)

    if tr is not None:

      m = TickRateAttribute._TICK_RATE_RE.match(tr)

      if m is not None:

        return int(m.group(1))

      LOGGER.error("ttp:tickRate invalid syntax")

    # default value

    return 1

class AspectRatioAttribute:
  '''ittp:aspectRatio attribute
  '''

  qn = f"{{{ns.ITTP}}}aspectRatio"

  _re = re.compile(r"(\d+) (\d+)")

  @staticmethod
  def extract(ttml_element) -> typing.Optional[Fraction]:

    ar_raw = ttml_element.attrib.get(AspectRatioAttribute.qn)

    if ar_raw is None:
      return None

    m = AspectRatioAttribute._re.match(ar_raw)

    if m is None:
      LOGGER.error("ittp:aspectRatio invalid syntax")
      return None

    try:

      return Fraction(int(m.group(1)), int(m.group(2)))

    except ZeroDivisionError:

      LOGGER.error("ittp:aspectRatio denominator is 0")
    
    return None

class DisplayAspectRatioAttribute:
  '''ttp:displayAspectRatio attribute
  '''

  qn = f"{{{ns.TTP}}}displayAspectRatio"

  _re = re.compile(r"(\d+) (\d+)")

  @staticmethod
  def extract(ttml_element) -> typing.Optional[Fraction]:

    ar_raw = ttml_element.attrib.get(DisplayAspectRatioAttribute.qn)

    if ar_raw is None:
      return None

    m = DisplayAspectRatioAttribute._re.match(ar_raw)

    if m is None:
      LOGGER.error("ttp:displayAspectRatio invalid syntax")
      return None

    try:

      return Fraction(int(m.group(1)), int(m.group(2)))

    except ZeroDivisionError:

      LOGGER.error("ttp:displayAspectRatio denominator is 0")
    
    return None

  @staticmethod
  def set(ttml_element, display_aspect_ratio: Fraction):
    ttml_element.set(
      DisplayAspectRatioAttribute.qn, 
      f"{display_aspect_ratio.numerator:g} {display_aspect_ratio.denominator:g}"
    )

class FrameRateAttribute:
  '''ttp:frameRate and ttp:frameRateMultiplier attribute
  '''

  frame_rate_qn = f"{{{ns.TTP}}}frameRate"

  frame_rate_multiplier_qn = f"{{{ns.TTP}}}frameRateMultiplier"

  _FRAME_RATE_RE = re.compile(r"(\d+)")

  _FRAME_RATE_MULT_RE = re.compile(r"(\d+) (\d+)")

  @staticmethod
  def extract(ttml_element) -> Fraction:

    # process ttp:frameRate

    fr = Fraction(30, 1)

    fr_raw = ttml_element.attrib.get(FrameRateAttribute.frame_rate_qn)

    if fr_raw is not None:

      m = FrameRateAttribute._FRAME_RATE_RE.match(fr_raw)

      if m is not None:

        fr = Fraction(m.group(1))

      else:

        LOGGER.error("ttp:frameRate invalid syntax")

    # process ttp:frameRateMultiplier
    
    frm = Fraction(1, 1)

    frm_raw = ttml_element.attrib.get(FrameRateAttribute.frame_rate_multiplier_qn)

    if frm_raw is not None:

      m = FrameRateAttribute._FRAME_RATE_MULT_RE.match(frm_raw)

      if m is not None:

        frm = Fraction(int(m.group(1)), int(m.group(2)))

      else:

        LOGGER.error("ttp:frameRateMultiplier invalid syntax")

    return fr * frm

  @staticmethod
  def set(ttml_element, frame_rate: Fraction):
    rounded_fps = round(frame_rate)

    ttml_element.set(
      FrameRateAttribute.frame_rate_qn, 
      str(rounded_fps)
    )

    fps_multiplier = frame_rate / rounded_fps

    if fps_multiplier != 1:

      ttml_element.set(
        FrameRateAttribute.frame_rate_multiplier_qn, 
        f"{fps_multiplier.numerator:g} {fps_multiplier.denominator:g}"
      )

@dataclass
class TemporalAttributeParsingContext:
  frame_rate: Fraction = Fraction(30, 1)
  tick_rate: int = 1

class TimeExpressionSyntaxEnum(Enum):
  """IMSC time expression configuration values"""
  frames = "frames"
  clock_time = "clock_time"
  clock_time_with_frames = "clock_time_with_frames"

@dataclass
class TemporalAttributeWritingContext:
  frame_rate: typing.Optional[Fraction] = None
  time_expression_syntax: TimeExpressionSyntaxEnum = TimeExpressionSyntaxEnum.clock_time

def to_time_format(context: TemporalAttributeWritingContext, time: Fraction) -> str:
  if context.time_expression_syntax is TimeExpressionSyntaxEnum.clock_time or context.frame_rate is None:
    return str(ClockTime.from_seconds(time))

  if context.time_expression_syntax is TimeExpressionSyntaxEnum.frames:
    return f"{math.ceil(time * context.frame_rate)}f"

  return f"{SmpteTimeCode.from_seconds(time, context.frame_rate)}"

class BeginAttribute:
  '''begin attribute
  '''
  qn = "begin"

  @staticmethod
  def extract(context: TemporalAttributeParsingContext, xml_element) -> typing.Optional[Fraction]:

    # read begin attribute

    begin_raw = xml_element.attrib.get(BeginAttribute.qn)

    try:

      return utils.parse_time_expression(context.tick_rate, context.frame_rate, begin_raw) if begin_raw is not None else None

    except ValueError:

      LOGGER.error("bad begin value")

      return None

  @staticmethod
  def set(context: TemporalAttributeWritingContext, ttml_element, begin:Fraction):
    value = to_time_format(context, begin)
    ttml_element.set(BeginAttribute.qn, value)

class EndAttribute:
  '''end attributes
  '''
  qn = "end"

  @staticmethod
  def extract(context: TemporalAttributeParsingContext, xml_element) -> typing.Optional[Fraction]:

    # read end attribute

    end_raw = xml_element.attrib.get(EndAttribute.qn)

    try:

      return utils.parse_time_expression(context.tick_rate, context.frame_rate, end_raw) if end_raw is not None else None

    except ValueError:

      LOGGER.error("bad end value")

      return None

  @staticmethod
  def set(context: TemporalAttributeWritingContext, ttml_element, end:Fraction):
    value = to_time_format(context, end)
    ttml_element.set(EndAttribute.qn, value)

class DurAttribute:
  '''dur attributes
  '''
  qn = "dur"

  @staticmethod
  def extract(context: TemporalAttributeParsingContext, xml_element) -> typing.Optional[Fraction]:

    dur_raw = xml_element.attrib.get(DurAttribute.qn)

    try:

      return utils.parse_time_expression(context.tick_rate, context.frame_rate, dur_raw) if dur_raw is not None else None

    except ValueError:

      LOGGER.error("bad dur value")

      return None

  @staticmethod
  def set(ttml_element, dur):
    raise NotImplementedError

class TimeContainer(Enum):
  par = "par"
  seq = "seq"

  def is_seq(self) -> bool:
    return self == TimeContainer.seq

  def is_par(self) -> bool:
    return self == TimeContainer.par

class TimeContainerAttribute:
  '''timeContainer attributes
  '''

  qn = "timeContainer"

  @staticmethod
  def extract(xml_elem) -> TimeContainer:

    time_container_raw = xml_elem.attrib.get(TimeContainerAttribute.qn)

    try:

      return TimeContainer(time_container_raw) if time_container_raw is not None else TimeContainer.par

    except ValueError:

      LOGGER.error("bad timeContainer value")

      return TimeContainer.par


class StyleAttribute:
  '''style attribute
  '''
  qn = "style"

  @staticmethod
  def extract(xml_element) -> typing.List[str]:

    raw_value = xml_element.attrib.get(StyleAttribute.qn)

    return raw_value.split(" ") if raw_value is not None else []
