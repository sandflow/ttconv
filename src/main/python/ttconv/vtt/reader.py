#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2022, Sandflow Consulting LLC
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

"""VTT reader"""

from __future__ import annotations

from dataclasses import dataclass
import typing
import re
import logging
from enum import Enum

from ttconv import model
from ttconv import style_properties as styles
from ttconv.vtt.tokenizer import EndTagToken, StartTagToken, StringToken, CueTextTokenizer, TimestampTagToken, Token

LOGGER = logging.getLogger(__name__)

def _none_terminated(iterator):
  for item in iterator:
    yield item
  yield None

def _parse_cue_text(cue_text: str, paragraph: model.P, line_number: int):
  parser = _TextCueParser(paragraph, line_number)

  for token in CueTextTokenizer(cue_text):
    parser.handle_token(token)

class _TextCueParser:

  def __init__(self, paragraph: model.P, line_number: int) -> None:
    self.line_num: int = line_number
    self.paragraph: model.P = paragraph
    self.parent: model.ContentElement = paragraph

    # handle the special case of ruby elements where children cannot be added one by one
    self.ruby_rbc: typing.Optional[model.Rbc] = None
    self.ruby_rtc: typing.Optional[model.Rtc] = None

  def handle_token(self, token: Token) -> None:
    if isinstance(token, StartTagToken):
      self._handle_starttag(token)
    elif isinstance(token, EndTagToken):
      self._handle_endtag(token)
    elif isinstance(token, StringToken):
      self._handle_string(token)
    elif isinstance(token, TimestampTagToken):
      self._handle_ts(token)
    else:
      raise ValueError("Unknown token type")

  def _handle_ts(self, token: TimestampTagToken):

    ts = vtt_timestamp_to_secs(token.timestamp)
    if ts is None:
      LOGGER.warning("Invalid timestamp tag %s at line %s", token.timestamp, self.line_num)
      return

    # we handle only top-level timestamp tags
    if self.parent.get_begin() is None:
      LOGGER.warning("Nested timestamp tag %s at line %s", token.timestamp, self.line_num)
      return

    p_begin = self.paragraph.get_begin()
    if p_begin is None or p_begin >= ts:
      LOGGER.warning("Invalid timestamp tag %s", token.timestamp)

    span = self._make_span(self.paragraph)
    span.set_begin(ts - p_begin)
    self.paragraph.push_child(span)
    self.parent = span

  def _handle_starttag(self, token: StartTagToken):

    tag = token.tag.lower()

    if tag.startswith("ruby"):
      if self.ruby_rbc is not None or self.ruby_rtc is not None:
        raise RuntimeError("Nested ruby tags are not allowed.")
      span = model.Ruby(self.parent.get_doc())

      # wrap <rb> and <rt> into <rbc> and <rtc>

      self.ruby_rbc = model.Rbc(self.parent.get_doc())
      self.ruby_rtc = model.Rtc(self.parent.get_doc())
      span.push_children([self.ruby_rbc, self.ruby_rtc])
      self.parent.push_child(span)
      self.parent = span
      return

    if tag.startswith("rt"):
      span = model.Rt(self.parent.get_doc())
      self.ruby_rtc.push_child(span)
      self.parent = span
      return

    # all other tags can be handled as a span

    span = self._make_span(self.parent)
    self.parent.push_child(span)
    self.parent = span

    if isinstance(span.parent(), model.P):
      span.set_style(styles.StyleProperties.BackgroundColor, _DEFAULT_BG_COLOR)

    if tag.startswith("b"):
      span.set_style(styles.StyleProperties.FontWeight, styles.FontWeightType.bold)

    elif tag.startswith("i"):
      span.set_style(styles.StyleProperties.FontStyle, styles.FontStyleType.italic)

    elif tag.startswith("u"):
      span.set_style(styles.StyleProperties.TextDecoration, styles.TextDecorationType(underline=True))

    elif tag.startswith("lang"):
      try:
        span.set_lang(token.annotation)
      except IndexError:
        LOGGER.warning("Lang tag without language present")

    elif tag.startswith("c"):
      if token.classes is not None:
        for c in token.classes:
          try:
            if c.startswith("bg_"):
              bg_color =  styles.NamedColors[c[3:]]
              span.set_style(styles.StyleProperties.BackgroundColor, bg_color.value)
            else:
              color =  styles.NamedColors[c]
              span.set_style(styles.StyleProperties.Color, color.value)
          except KeyError:
            LOGGER.warning("Ignoring class %s", c)

    elif tag == "v":
      pass

    else:
      LOGGER.warning("Unknown tag %s at line %s", tag, self.line_num)
      return

  def _handle_endtag(self, _token: EndTagToken):

    if isinstance(self.parent, model.Ruby):
      self.ruby_rbc = None
      self.ruby_rtc = None
    elif isinstance(self.parent, (model.Rt, model.Rb)):
      # this is needed since <rb> and <rt> are nested in <rbc> and <rtc>
      self.parent = self.parent.parent()

    self.parent = self.parent.parent()

  def _handle_string(self, token: StringToken):
    lines = token.value.split("\n")

    for i, line in enumerate(lines):
      if i > 0:
        self.parent.push_child(model.Br(self.parent.get_doc()))
      span = self._make_span(self.parent)
      span.push_child(model.Text(self.parent.get_doc(), line))
      if isinstance(self.parent, model.Ruby):
        rb = model.Rb(self.parent.get_doc())
        rb.push_child(span)
        self.ruby_rbc.push_child(rb)
      else:
        self.parent.push_child(span)

  def _make_span(self, parent: model.ContentElement) -> model.Span:
    span = model.Span(self.parent.get_doc())
    if isinstance(parent, model.P):
      span.set_style(styles.StyleProperties.BackgroundColor, _DEFAULT_BG_COLOR)
    return span


_EMPTY_RE = re.compile(r"[\n\r]*")
_DEFAULT_FONT_STACK = (styles.GenericFontFamilyType.sansSerif,)
_DEFAULT_FONT_SIZE_PCT = 5
_DEFAULT_FONT_SIZE = styles.LengthType(15 * _DEFAULT_FONT_SIZE_PCT, styles.LengthType.Units.pct) # 5vh for ttp:cellResolution="32 15"
_DEFAULT_TEXT_COLOR = styles.NamedColors.white.value
_DEFAULT_LINE_PADDING = styles.LengthType(0.5, styles.LengthType.Units.c)
_DEFAULT_LINE_HEIGHT = styles.LengthType(125, styles.LengthType.Units.pct)
_DEFAULT_LINE_HEIGHT_PCT = _DEFAULT_FONT_SIZE_PCT *_DEFAULT_LINE_HEIGHT.value/100
_DEFAULT_BG_COLOR = styles.ColorType((0, 0, 0, 204))
_DEFAULT_ROWS = 23
_DEFAULT_COLS = 40

_VTT_PCT_RE = re.compile(r"(\d+\.?\d*)%")

def parse_vtt_pct(value: str):
  """Parse a WebVTT precentage value"""
  m = _VTT_PCT_RE.fullmatch(value)
  if m:
    v = round(float(m.group(1)))
    return v if 0 <= v <= 100 else None
  return None

# integer has at most 20 digits
_VTT_INT_RE = re.compile(r"(-?\d{1,20})")

def parse_vtt_int(value: str):
  """Parse a WebVTT integer value"""
  m = _VTT_INT_RE.fullmatch(value)
  if m:
    return int(m.group(1))
  return None

@dataclass
class _RegionParams:
  extent : typing.Optional[styles.ExtentType] = None
  origin : typing.Optional[styles.CoordinateType] = None
  writing_mode : typing.Optional[styles.WritingModeType] = None
  text_align : typing.Optional[styles.TextAlignType] = None
  display_align : typing.Optional[styles.DisplayAlignType] = None
  
def make_region_params(cue_settings: dict[str, str]) -> _RegionParams:
  """Compute region style parameters from cue settings
  """
  r = _RegionParams()

  # writing_mode
  r.writing_mode = styles.WritingModeType.lrtb
  value = cue_settings.get("vertical")
  if value == "lr":
    r.writing_mode = styles.WritingModeType.tblr
  elif value == "rl":
    r.writing_mode = styles.WritingModeType.tbrl
  elif value is not None:
    LOGGER.warning("Bad vertical setting value: %s", value)

  # cue text align
  cue_text_align = "center"
  value = cue_settings.get("align")
  if value in ("left", "right", "start", "center", "end"):
    cue_text_align = value
  elif value is not None:
    LOGGER.warning("Bad align setting value: %s", cue_text_align)

  # cue size

  cue_size = 100
  value = cue_settings.get("size")
  if value is not None:
    value = parse_vtt_pct(value)
    if value is not None:
      cue_size = value
    else:
      LOGGER.warning("Bad size setting value: %s", value)

  # line setting

  cue_line_align = "start"
  cue_snap_to_lines = True
  cue_line_num = -1

  value = cue_settings.get("line")
  if value is not None:
    value = value.split(",")

    v = parse_vtt_pct(value[0])
    if v is not None:
      cue_line_num = v
      cue_snap_to_lines = False
    else:
      v = parse_vtt_int(value[0])
      if v is not None:
        cue_line_num = v
      else:
        LOGGER.warning("Bad line setting value: %s", value)

    if len(value) == 2:
      if value[1] in ("start", "center", "end"):
        cue_line_align = value[1]
      else:
        LOGGER.warning("Bad line alignment setting value: %s", value[1])

  # position

  cue_position = None
  cue_position_align = None

  value = cue_settings.get("position")
  if value is not None:
    value = value.split(",")

    # position value
    cue_position = parse_vtt_pct(value[0])
    if cue_position is None:
      LOGGER.warning("Bad position alignment setting value: %s", cue_position)
    else:
      # position alignment
      if len(value) > 1:
        if value[1] in ("center", "line-left", "line-right"):
          cue_position_align = value[1]
        else:
          LOGGER.warning("Bad position alignment setting value: %s", value[1])

  if cue_position_align is None:
    if cue_text_align == "start":
      cue_position_align = "line-right" if r.writing_mode == styles.WritingModeType.rltb else "line-left"
    elif cue_text_align == "end":
      cue_position_align = "line-left" if r.writing_mode == styles.WritingModeType.rltb else "line-right"
    elif cue_text_align == "left":
      cue_position_align = "line-left"
    elif cue_text_align == "right":
      cue_position_align = "line-right"
    elif cue_text_align == "center":
      cue_position_align = "center"
    else:
      raise RuntimeError("Invalid cue text alignment setting")  

  if cue_position is None or not (0 <= cue_position <= 100):
    if cue_text_align == "left":
      cue_position = 0
    elif cue_text_align == "right":
      cue_position = 100
    else:
      cue_position = 50

  # text_align

  r.text_align = styles.TextAlignType.center
  if cue_text_align == "left":
    r.text_align = styles.TextAlignType.end if r.writing_mode == styles.WritingModeType.rltb else styles.TextAlignType.start
  elif cue_text_align == "right":
    r.text_align = styles.TextAlignType.start if r.writing_mode == styles.WritingModeType.rltb else styles.TextAlignType.end
  elif cue_text_align == "start":
    r.text_align = styles.TextAlignType.start
  elif cue_text_align == "center":
    r.text_align = styles.TextAlignType.center
  elif cue_text_align == "end":
    r.text_align = styles.TextAlignType.end
  else:
    raise RuntimeError("Invalid cue text alignment setting")
  
  # display_align

  if cue_line_align == "center":
    r.display_align = styles.DisplayAlignType.center
  elif cue_line_align == "end":
    r.display_align = styles.DisplayAlignType.after
  elif cue_line_align == "start":
    r.display_align = styles.DisplayAlignType.before
  else:
    raise RuntimeError("Invalid line alignment setting")

  # compute region origin and extent

  if cue_position_align == "line-left":
    max_ipd_size = 100 - cue_position
  elif cue_position_align == "line-right":
    max_ipd_size = cue_position
  elif cue_position_align == "center":
    if cue_position <= 50:
      max_ipd_size = cue_position * 2
    else:
      max_ipd_size = (100 - cue_position) * 2
  else:
    raise RuntimeError("Invalid position alignment")

  ipd_size = max(_DEFAULT_FONT_SIZE_PCT, min(cue_size, max_ipd_size))

  if cue_position_align == "line-left":
    ipd_origin = min(cue_position, 100 - ipd_size)
  elif cue_position_align == "line-right":
    ipd_origin = max(0, cue_position - ipd_size)
  elif cue_position_align == "center":
    ipd_origin = max(min(cue_position - ipd_size / 2, 100 - ipd_size), 0)
  else:
    raise RuntimeError("Invalid position alignment")

  if cue_snap_to_lines:
    if cue_line_num >= 0:
      bpd_origin = _DEFAULT_LINE_HEIGHT_PCT * cue_line_num
    else:
      bpd_origin = 100 + cue_line_num * _DEFAULT_LINE_HEIGHT_PCT
  else:
    bpd_origin = cue_line_num

  if cue_line_align == "center":
    bpd_size = max(_DEFAULT_LINE_HEIGHT_PCT, min(bpd_origin * 2, (100 - bpd_origin) * 2))
  elif cue_line_align == "end":
    bpd_size = bpd_origin
  elif cue_line_align == "start":
    bpd_size = 100 - bpd_origin
  
  bpd_size = max(_DEFAULT_LINE_HEIGHT_PCT, bpd_size)

  if cue_line_align == "center":
    bpd_origin = max(min(bpd_origin - bpd_size / 2, 100 - bpd_size), 0)
  elif cue_line_align == "end":
    bpd_origin = max(0, bpd_origin - bpd_size)
  elif cue_line_align == "start":
    bpd_origin = min(bpd_origin, 100 - bpd_size)

  if r.writing_mode in (styles.WritingModeType.lrtb, styles.WritingModeType.rltb):
    r.extent = styles.ExtentType(
      height=styles.LengthType(bpd_size),
      width=styles.LengthType(ipd_size)
    )
    r.origin = styles.CoordinateType(
      x=styles.LengthType(ipd_origin),
      y=styles.LengthType(bpd_origin)
    )
  else:
    r.extent = styles.ExtentType(
      height=styles.LengthType(ipd_size),
      width=styles.LengthType(bpd_size)
    )
    r.origin = styles.CoordinateType(
      x=styles.LengthType(bpd_origin),
      y=styles.LengthType(ipd_origin)
    )
  
  return r

def _get_or_make_region(
  doc: model.ContentDocument,
  cue_settings_list: str
  ):
  """Returns a matching region from `doc` or creates one
  """

  cue_settings = dict(filter(lambda x: len(x) == 2, [x.split(":") for x in cue_settings_list]))

  if len(cue_settings) > 0:
    p = make_region_params(cue_settings)
  else:
    # maintain compatibility with earlier versions
    p = _RegionParams(
      extent = styles.ExtentType(
        height=styles.LengthType(100 - 200/_DEFAULT_ROWS),
        width=styles.LengthType(100 - 200/_DEFAULT_COLS)
      ),
      origin = styles.CoordinateType(
        x=styles.LengthType(100/_DEFAULT_COLS),
        y=styles.LengthType(100/_DEFAULT_ROWS)
      ),
      writing_mode=styles.WritingModeType.lrtb,
      text_align=styles.TextAlignType.center,
      display_align=styles.DisplayAlignType.after
    )

  # look for a matching region

  found_region = None
  regions = list(doc.iter_regions())
  for r in regions:

    if r.get_style(styles.StyleProperties.WritingMode) != p.writing_mode:
      continue

    if r.get_style(styles.StyleProperties.Extent) != p.extent:
      continue

    if r.get_style(styles.StyleProperties.Origin) != p.origin:
      continue

    if r.get_style(styles.StyleProperties.TextAlign) != p.text_align:
      continue

    if r.get_style(styles.StyleProperties.DisplayAlign) != p.display_align:
      continue

    found_region = r
    break

  if found_region is None:
    found_region = model.Region(f"r{len(regions)}", doc)
    found_region.set_style(styles.StyleProperties.Origin, p.origin)
    found_region.set_style(styles.StyleProperties.Extent, p.extent)
    found_region.set_style(styles.StyleProperties.DisplayAlign, p.display_align)
    found_region.set_style(styles.StyleProperties.TextAlign, p.text_align)
    found_region.set_style(styles.StyleProperties.WritingMode, p.writing_mode)
    found_region.set_style(styles.StyleProperties.LineHeight, _DEFAULT_LINE_HEIGHT)
    found_region.set_style(styles.StyleProperties.FontFamily, _DEFAULT_FONT_STACK)
    found_region.set_style(styles.StyleProperties.FontSize, _DEFAULT_FONT_SIZE)
    found_region.set_style(styles.StyleProperties.Color, _DEFAULT_TEXT_COLOR)
    found_region.set_style(styles.StyleProperties.LinePadding, _DEFAULT_LINE_PADDING)
    found_region.set_style(styles.StyleProperties.FillLineGap, True)
    doc.put_region(found_region)

  return found_region

_VTT_TS_RE = re.compile(r"(?:(?P<hh>[0-9]{2,}):)?(?P<mm>[0-9]{2}):(?P<ss>[0-9]{2})\.(?P<ms>[0-9]{3})")
_VTT_TS_TAG_RE = re.compile(r"<((?:[0-9]{2,3}:)?[0-9]{2}:[0-9]{2}\.[0-9]{3})>")

def vtt_timestamp_to_secs(vtt_ts: str):
  m = _VTT_TS_RE.fullmatch(vtt_ts)

  if m:
    return int(m.group('hh') if m.group('hh') is not None else 0) * 3600 + \
      int(m.group('mm')) * 60 + \
      int(m.group('ss')) + \
      int(m.group('ms')) / 1000

  return None

def to_model(data_file: typing.IO, _config = None, progress_callback=lambda _: None):
  """Converts a WebVTT document to the data model"""

  class _State(Enum):
    LOOKING = 1
    TC = 2
    TEXT = 3
    TEXT_MORE = 4
    START = 5
    NOTE = 6
    STYLE = 7


  doc = model.ContentDocument()

  body = model.Body(doc)
  doc.set_body(body)

  div = model.Div(doc)
  body.push_child(div)

  lines : str = data_file.readlines()

  state = _State.START
  current_p = None

  for line_index, line in enumerate(_none_terminated(lines)):

    if state is _State.START:
      if not line.startswith("WEBVTT"):
        LOGGER.warning("The first line of the file does not start with WEBVTT")
      state = _State.LOOKING
      continue

    if state in (_State.NOTE, _State.STYLE):
      # we skip over notes

      if line is None:
        break

      if _EMPTY_RE.fullmatch(line):
        state = _State.LOOKING
        continue

    if state is _State.LOOKING:
      if line is None:
        break

      if _EMPTY_RE.fullmatch(line):
        continue

      if line.startswith("NOTE "):
        state = _State.NOTE
        continue

      if line.startswith("STYLE"):
        state = _State.STYLE
        continue

      if "-->" not in line:
        # skip over cue id
        continue

      progress_callback(line_index/len(lines))

      cue_params = line.split()

      if len(cue_params) < 3:
        LOGGER.warning("Invalid line %s", line_index)
        continue

      start_time = vtt_timestamp_to_secs(cue_params[0])
      if start_time is None:
        LOGGER.warning("Invalid timestamp %s at %s", cue_params[0], line_index)
        continue

      end_time = vtt_timestamp_to_secs(cue_params[2])
      if end_time is None:
        LOGGER.warning("Invalid timestamp %s at %s", cue_params[2], line_index)
        continue

      current_p = model.P(doc)

      current_p.set_begin(start_time)

      current_p.set_end(end_time)

      # handle settings

      current_p.set_region(_get_or_make_region(doc, cue_params[3:]))

      state = _State.TEXT
      subtitle_text = None
      continue

    if state in (_State.TEXT, _State.TEXT_MORE):

      if line is None or _EMPTY_RE.fullmatch(line):
        if subtitle_text is not None:
          _parse_cue_text(
            subtitle_text.strip('\r\n').replace(r"\n\r", "\n"),
            current_p,
            line_index
          )
        else:
          LOGGER.warning("Ignoring cue due to a spurious blank line at line %s", line_index)

        state = _State.LOOKING
        continue

      if state is _State.TEXT:
        div.push_child(current_p)
        subtitle_text = ""

      subtitle_text += line

      state = _State.TEXT_MORE

      continue

  return doc
