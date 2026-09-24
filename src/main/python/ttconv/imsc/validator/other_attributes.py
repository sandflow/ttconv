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

'''Process IMSC non-style attributes'''

from __future__ import annotations

import re
from fractions import Fraction
import typing
from dataclasses import dataclass, field
from enum import Enum

from ttconv.imsc.namespaces import QName
import ttconv.imsc.namespaces as ns
import ttconv.imsc.utils as imsc_utils
from ttconv.imsc.validator.attribute_vocabulary import attribute
from ttconv.imsc.validator.ttml_profile_helper import absolutize_profile_designator, is_ttml2_profile_designator
from ttconv.imsc.validator.uri_helper import is_uri
from ttconv.imsc.validator.lang_helper import is_valid_language_tag
from ttconv.imsc.validator.xml_helper import is_valid_xml_name, xml_qname_parts

_LWSP_RE = re.compile(r"[ \t\r\n]+")

class TimeBase(Enum):
  clock = "clock"
  media = "media"
  smpte = "smpte"

class DropMode(Enum):
  nonDrop = "nonDrop"
  dropNTSC = "dropNTSC"
  dropPAL = "dropPAL"

class TimeExpressionSyntaxEnum(Enum):
  """IMSC time expression configuration values"""
  frames = "frames"
  clock_time = "clock_time"
  clock_time_with_frames = "clock_time_with_frames"

@dataclass
class TemporalAttributeParsingContext:
  frame_rate: Fraction = Fraction(30, 1)
  tick_rate: int = 1
  time_base: TimeBase = TimeBase.media
  drop_mode: DropMode = DropMode.nonDrop

@dataclass
class ValidationContext:
  target_region_ids: typing.Set[str] = field(default_factory=set)
  region_ids: typing.Set[str] = field(default_factory=set)
  xml_ids: typing.Set[str] = field(default_factory=set)
  tick_rate: int = 1
  time_base: TimeBase = TimeBase.media
  drop_mode: DropMode = DropMode.nonDrop
  frame_rate: int = 30
  frame_rate_mult: Fraction = Fraction(1)
  sig_agent_ids: typing.Set[str] = field(default_factory=set)
  target_sig_agent_ids: typing.Set[str] = field(default_factory=set)
  target_style_ids: typing.Set[str] = field(default_factory=set)
  namespaces: dict[str, list[str]] = field(default_factory=dict)

@attribute
class XMLIDAttribute:
  '''xml:id attribute
  '''

  qname = QName(ns.XML, "id")

  @staticmethod
  def validate(value: str, ctx : ValidationContext):
    if not is_valid_xml_name(value):
      raise ValueError("Bad xml:id value")

    if value in ctx.xml_ids:
      raise ValueError("Duplicate xml:id value")
    else:
      ctx.xml_ids.add(value)

@attribute
class XMLLangAttribute:
  '''xml:lang attribute
  '''

  qname = QName(ns.XML, "lang")

  @staticmethod
  def validate(value, _):
    if len(value) > 0 and not is_valid_language_tag(value):
      raise ValueError("Invalid language tag `%s` for xml:lang" % value)

@attribute
class XMLSpaceAttribute:
  '''xml:space attribute
  '''

  qname = QName(ns.XML, "space")

  @staticmethod
  def validate(value, _):
    if not value in ("preserve", "default"):
      raise ValueError("Bad xml:space value (%s)" % value)

@attribute
class RegionAttribute:
  '''TTML region attribute'''

  qname = QName(None, "region")

  @staticmethod
  def validate(value, ctx: ValidationContext):
    if not is_valid_xml_name(value):
      raise ValueError("Bad region id value: `%s`" % value)

    ctx.target_region_ids.add(value)

@attribute
class UseAttribute:
  '''use attribute on ttp:profile
  '''

  qname = QName(None, "use")

  @staticmethod
  def validate(value, _ctx: ValidationContext):
    if not is_ttml2_profile_designator(value):
      raise ValueError("Bad use attribute value (%s)" % value)

@attribute
class FeatureValueAttribute:
  '''value attribute on ttp:feature / ttp:extension
  '''

  qname = QName(None, "value")

  @staticmethod
  def validate(value, _ctx: ValidationContext):
    if value not in ("required", "optional", "prohibited", "use"):
      raise ValueError("Bad value attribute value (%s)" % value)

@attribute
class ContentProfilesAttribute:
  '''ttp:contentProfiles attribute
  '''

  qname = QName(ns.TTP, "contentProfiles")

  _CONTENT_PROFILES_RE = re.compile(r"\S+(?:\s+\S+)*")

  @staticmethod
  def validate(value, _):
    if len(value) == 0:
      raise ValueError("ttp:contentProfiles is the empty string")

    # TODO: validation/valid/ttml2-valid-content-profiles-quantified-all-single.xml does not use LWSP
    c = _LWSP_RE.split(value)
    if len(c) > 2 and c[0] == "all(" and c[-1] == ")":
      c = c[1:-1]
    for d in c:
      if not is_ttml2_profile_designator(d):
        raise ValueError("ttp:contentProfiles: '%s' is not a valid profile reference" % d)

    ad = list(map(absolutize_profile_designator, c))
    if len(set(ad)) != len(ad):
      raise ValueError("ttp:contentProfiles: '%s' contains duplicate profile references" % value)

@attribute
class ProfileAttribute:
  '''ttp:profile attribute
  '''

  qname = QName(ns.TTP, "profile")

  @staticmethod
  def validate(value, _):
    if not is_ttml2_profile_designator(value):
      raise ValueError("ttp:profile '%s' is not a valid profile reference" % value)

@attribute
class CellResolutionAttribute:
  '''ttp:cellResolution attribute
  '''

  qname = QName(ns.TTP, "cellResolution")

  _CELL_RESOLUTION_RE = re.compile(r"^(\d+) (\d+)$")

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    m = CellResolutionAttribute._CELL_RESOLUTION_RE.match(value)
    if m is not None:
      if int(m.group(1)) > 0 and int(m.group(2)) > 0:
        return
    raise ValueError("Bad ttp:cellResolution value (%s)" % value)

@attribute
class ExtentAttribute:
  '''ttp:extent attribute on \\<tt\\>
  '''

  qname = QName(ns.TTS, "extent")

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    s = value.split(" ")
    if len(s) != 2:
      raise ValueError("Bad tts:extent value (%s)" % value)
    try:
      (w, w_units) = imsc_utils.parse_length(s[0])
      (h, h_units) = imsc_utils.parse_length(s[1])
    except ValueError:
      raise ValueError("Bad tts:extent value (%s)" % value)
    if w_units != "px" or h_units != "px":
      raise ValueError("tts:extent on <tt> must use px units (%s)" % value)
    if not w.is_integer() or not h.is_integer():
      raise ValueError("tts:extent on <tt> dimensions must be integer values (%s)" % value)

@attribute
class ActiveAreaAttribute:
  '''ittp:activeArea attribute on \\<tt\\>
  '''

  qname = QName(ns.ITTP, "activeArea")

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    s = value.split(" ")
    if len(s) != 4:
      raise ValueError("Bad ittp:activeArea value (%s)" % value)
    try:
      units = [imsc_utils.parse_length(c)[1] for c in s]
    except ValueError:
      raise ValueError("Bad ittp:activeArea value (%s)" % value)
    if any(u != "%" for u in units):
      raise ValueError("ittp:activeArea must use %% units (%s)" % value)

@attribute
class TickRateAttribute:
  '''ttp:tickRate attribute
  '''

  qname = QName(ns.TTP, "tickRate")

  _TICK_RATE_RE = re.compile(r"^(\d+)$")

  @staticmethod
  def validate(value: str, ctx: ValidationContext):
    m = TickRateAttribute._TICK_RATE_RE.match(value)
    t = None if m is None else int(m.group(1))
    if t is None or t == 0:
      raise ValueError("Bad ttp:tickRate value (%s)" % value)
    ctx.tick_rate = t

@attribute
class AspectRatioAttribute:
  '''ittp:aspectRatio attribute
  '''

  qname = QName(ns.ITTP, "aspectRatio")

  _re = re.compile(r"^(\d+) (\d+)$")

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    m = AspectRatioAttribute._re.match(value)
    if m is None:
      raise ValueError("Bad ittp:aspectRatio value (%s)" % value)
    if int(m.group(2)) == 0:
      raise ValueError("ittp:aspectRatio denominator is 0")

@attribute
class ProgressivelyDecodableAttribute:
  '''ittp:progressivelyDecodable attribute
  '''

  qname = QName(ns.ITTP, "progressivelyDecodable")

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("true", "false"):
      raise ValueError("Bad ittp:progressivelyDecodable value (%s)" % value)

@attribute
class DisplayAspectRatioAttribute:
  '''ttp:displayAspectRatio attribute
  '''

  qname = QName(ns.TTP, "displayAspectRatio")

  _re = re.compile(r"^(\d+) (\d+)$")

  @staticmethod
  def extract(value: str) -> Fraction:
    m = DisplayAspectRatioAttribute._re.match(value)
    if m is None:
      raise ValueError("Bad ttp:displayAspectRatio value (%s)" % value)
    numerator = int(m.group(1))
    denominator = int(m.group(2))
    if denominator == 0:
      raise ValueError("ttp:displayAspectRatio denominator is 0")
    if numerator == 0:
      raise ValueError("ttp:displayAspectRatio numerator is 0")
    return Fraction(numerator, denominator)

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    DisplayAspectRatioAttribute.extract(value)

@attribute
class FrameRateAttribute:
  '''ttp:frameRate attribute
  '''

  qname = QName(ns.TTP, "frameRate")

  _FRAME_RATE_RE = re.compile(r"^(\d+)$")

  @staticmethod
  def extract(value: str) -> int:
    m = FrameRateAttribute._FRAME_RATE_RE.match(value)
    if m is not None:
      fps = int(m.group(1))
      if fps > 0:
        return fps
    raise ValueError("Bad ttp:frameRate value (%s)" % value)

  @staticmethod
  def validate(value: str, ctx: ValidationContext):
    ctx.frame_rate = FrameRateAttribute.extract(value)

@attribute
class FrameRateMultiplierAttribute:
  '''ttp:frameRateMultiplier attribute
  '''

  qname = QName(ns.TTP, "frameRateMultiplier")

  _FRAME_RATE_MULT_RE = re.compile(r"^(\d+) (\d+)$")

  @staticmethod
  def extract(value: str) -> Fraction:
    m = FrameRateMultiplierAttribute._FRAME_RATE_MULT_RE.match(value)
    if m is None:
      raise ValueError("Bad ttp:frameRateMultiplier value (%s)" % value)
    if int(m.group(2)) == 0:
      raise ValueError("ttp:frameRateMultiplier denominator is 0")

    return Fraction(int(m.group(1)), int(m.group(2)))

  @staticmethod
  def validate(value: str, ctx: ValidationContext):
    ctx.frame_rate_mult = FrameRateMultiplierAttribute.extract(value)

@dataclass
class TemporalAttributeWritingContext:
  frame_rate: typing.Optional[Fraction] = None
  time_expression_syntax: TimeExpressionSyntaxEnum = TimeExpressionSyntaxEnum.clock_time

_CLOCK_TIME_FRACTION_RE = re.compile(r"^(\d{2,}):(\d\d):(\d\d(?:\.\d+)?)$")
_CLOCK_TIME_FRAMES_RE = re.compile(r"^(\d{2,}):(\d\d):(\d\d):(\d{2,})$")
_OFFSET_FRAME_RE = re.compile(r"^(\d+(?:\.\d+)?)f")
_OFFSET_TICK_RE = re.compile(r"^(\d+(?:\.\d+)?)t$")
_OFFSET_MS_RE = re.compile(r"^(\d+(?:\.\d+)?)ms$")
_OFFSET_S_RE = re.compile(r"^(\d+(?:\.\d+)?)s$")
_OFFSET_H_RE = re.compile(r"^(\d+(?:\.\d+)?)h$")
_OFFSET_M_RE = re.compile(r"^(\d+(?:\.\d+)?)m$")


def parse_time_expression(ctx: TemporalAttributeParsingContext, time_expr: str) -> Fraction:
  '''Parse a TTML time expression in a fractional number in seconds
  '''

  m = _OFFSET_FRAME_RE.match(time_expr)

  if m and ctx.frame_rate is not None:
    return Fraction(m.group(1)) / ctx.frame_rate

  m = _OFFSET_TICK_RE.match(time_expr)

  if m and ctx.tick_rate is not None:
    return Fraction(m.group(1)) / ctx.tick_rate

  m = _OFFSET_MS_RE.match(time_expr)

  if m:
    return Fraction(m.group(1)) / 1000

  m = _OFFSET_S_RE.match(time_expr)

  if m:
    return Fraction(m.group(1))

  m = _OFFSET_M_RE.match(time_expr)

  if m:
    return Fraction(m.group(1)) * 60

  m = _OFFSET_H_RE.match(time_expr)

  if m:
    return Fraction(m.group(1)) * 3600

  m = _CLOCK_TIME_FRACTION_RE.match(time_expr)

  if m:
    hh = Fraction(m.group(1))
    mm = Fraction(m.group(2))
    if mm > 59:
      raise ValueError("Minutes field exceeds 59 in %s" % time_expr)
    ss = Fraction(m.group(3))
    if ss > 60:
      raise ValueError("Seconds field exceeds 60 in %s" % time_expr)
    return hh * 3600 + mm * 60 + ss

  m = _CLOCK_TIME_FRAMES_RE.match(time_expr)

  if m and ctx.frame_rate is not None:
    frames = int(m.group(4)) if m.group(4) else 0

    if frames >= ctx.frame_rate:
      raise ValueError("Frame count %s exceeds frame rate %s" % (frames, ctx.frame_rate))

    hh = int(m.group(1))
    mm = int(m.group(2))
    if mm > 59:
      raise ValueError("Minutes field exceeds 59 in %s" % time_expr)
    ss = int(m.group(3))
    if ss > 60:
      raise ValueError("Seconds field exceeds 60 in %s" % time_expr)

    return Fraction(hh * 3600 + mm * 60 + ss) + Fraction(frames) / ctx.frame_rate

  raise ValueError("Syntax error")

@attribute
class BeginAttribute:
  '''begin attribute
  '''

  qname = QName(None, "begin")

  @staticmethod
  def validate(value: str, ctx: ValidationContext):
    try:
      parse_time_expression(
        TemporalAttributeParsingContext(
          frame_rate=ctx.frame_rate * ctx.frame_rate_mult,
          tick_rate=ctx.tick_rate,
          time_base=ctx.time_base
        ),
        value
      )
    except ValueError:
      raise ValueError("Bad begin attribute value (%s)" % value)

@attribute
class EndAttribute:
  '''end attributes
  '''

  qname = QName(None, "end")

  @staticmethod
  def validate(value: str, ctx: ValidationContext):
    try:
      parse_time_expression(
        TemporalAttributeParsingContext(
          frame_rate=ctx.frame_rate * ctx.frame_rate_mult,
          tick_rate=ctx.tick_rate,
          time_base=ctx.time_base
        ),
        value
      )
    except ValueError:
      raise ValueError("Bad end attribute value (%s)" % value)

@attribute
class DurAttribute:
  '''dur attributes
  '''

  qname = QName(None, "dur")

  @staticmethod
  def validate(value: str, ctx: ValidationContext):
    try:
      parse_time_expression(
        TemporalAttributeParsingContext(
          frame_rate=ctx.frame_rate * ctx.frame_rate_mult,
          tick_rate=ctx.tick_rate,
          time_base=ctx.time_base
        ),
        value
      )
    except ValueError:
      raise ValueError("Bad dur attribute value (%s)" % value)

class TimeContainer(Enum):
  par = "par"
  seq = "seq"

  def is_seq(self) -> bool:
    return self == TimeContainer.seq

  def is_par(self) -> bool:
    return self == TimeContainer.par

@attribute
class TimeContainerAttribute:
  '''timeContainer attributes
  '''

  qname = QName(None, "timeContainer")

  @staticmethod
  def validate(value: str, _ctx: ValidationContext):
    if value not in ("par", "seq"):
      raise ValueError("Bad timeContainer value (%s)" % value)

@attribute
class StyleAttribute:
  '''style attribute
  '''

  qname = QName(None, "style")

  @staticmethod
  def parse(value: str):
    return _LWSP_RE.split(value)

  @staticmethod
  def validate(value: str, ctx: ValidationContext):
    for style_id in StyleAttribute.parse(value):
      if not is_valid_xml_name(style_id):
        raise ValueError("Bad style attribute value: `%s`" % style_id)
      ctx.target_style_ids.add(style_id)

@attribute
class TimeBaseAttribute:
  '''ttp:timeBase attribute
  '''

  qname = QName(ns.TTP, "timeBase")

  @staticmethod
  def extract(value: str) -> TimeBase:
    if value not in ("clock", "media", "smpte"):
      raise ValueError("Bad ttp:timeBase value (%s)" % value)
    return TimeBase(value)

  @staticmethod
  def validate(value: str, ctx: ValidationContext):
    ctx.time_base = TimeBaseAttribute.extract(value)

@attribute
class DropModeAttribute:
  '''ttp:dropMode attribute
  '''

  qname = QName(ns.TTP, "dropMode")

  @staticmethod
  def validate(value: str, ctx: ValidationContext):
    if value not in ("nonDrop", "dropNTSC", "dropPAL"):
      raise ValueError("Bad ttp:dropMode value (%s)" % value)
    ctx.drop_mode = DropMode(value)

@attribute
class XMLBaseAttribute:
  '''xml:base attribute
  '''

  qname = QName(ns.XML, "base")

  @staticmethod
  def validate(value, _):
    if not is_uri(value):
      raise ValueError("xml:base: '%s' is not a valid URI-reference" % value)

@attribute
class AgentAttribute:
  '''agent attribute
  '''
  qname = QName(None, "agent")

  @staticmethod
  def validate(value, ctx: ValidationContext):
    if not is_valid_xml_name(value):
      raise ValueError("Bad agent id value: `%s`" % value)

    ctx.target_sig_agent_ids.add(value)

@attribute
class AgentTypeAttribute:
  '''ttm:agent type attribute
  '''
  qname = QName(None, "type")
  @staticmethod
  def validate(value, _):
    if not value in ("person", "character", "group", "organization", "other"):
      raise ValueError("Bad ttm:agent type value (%s)" % value)

@attribute
class NameTypeAttribute:
  '''ttm:name type attribute
  '''
  qname = QName(None, "type")
  @staticmethod
  def validate(value, _):
    if not value in ("full", "family", "given", "alias", "other"):
      raise ValueError("Bad ttm:name type value (%s)" % value)

@attribute
class ItemNameAttribute:
  '''ttm:item name attribute
  '''
  qname = QName(None, "name")
  @staticmethod
  def validate(value, ctx: ValidationContext):
    if value in ("altText", "usesForced"):
      return
    prefix, local_part = xml_qname_parts(value)
    if prefix is not None and prefix not in ctx.namespaces:
      raise ValueError("Unknown prefix in ttm:item name value `%s`" % value)
    if local_part is None:
      raise ValueError("Bad ttm:item name value (%s)" % value)

@attribute
class MetadataAgentAttribute:
  '''ttm:agent attribute
  '''
  qname = QName(ns.TTM, "agent")
  @staticmethod
  def validate(value, ctx):
    for agent_id in _LWSP_RE.split(value):
      if not is_valid_xml_name(agent_id):
        raise ValueError("Bad ttm:agent attribute value: `%s`" % agent_id)
      ctx.target_sig_agent_ids.add(agent_id)

@attribute
class MetadataRoleAttribute:
  '''ttm:role attribute
  '''
  qname = QName(ns.TTM, "role")

  # see 14.2.2 at https://www.w3.org/TR/ttml2
  _ROLE_TOKENS = frozenset((
    "action", "caption", "description", "dialog", "expletive", "kinesic",
    "lyrics", "music", "narration", "quality", "sound", "source",
    "suppressed", "reproduction", "thought", "title", "transcription",
  ))

  @staticmethod
  def validate(value, _):
    for token in _LWSP_RE.split(value):
      if token in MetadataRoleAttribute._ROLE_TOKENS or token.startswith("x-"):
        continue
      raise ValueError("Bad ttm:role value (%s)" % token)
