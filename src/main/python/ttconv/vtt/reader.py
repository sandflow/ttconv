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

    span = self._make_span(self.parent)
    self.parent.push_child(span)
    self.parent = span

    ts = vtt_timestamp_to_secs(token.timestamp)
    parent_begin = None
    parent = self.parent
    while parent is not None:
      parent_begin = parent.get_begin()
      if parent_begin is not None:
        break
      parent = parent.parent()
    if ts is not None and parent_begin is not None and parent_begin <= ts:
      span.set_begin(ts - parent_begin)
    else:
      LOGGER.warning("Invalid timestamp tag %s", token.timestamp)

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


_EMPTY_RE = re.compile(r"\s+")
_DEFAULT_FONT_STACK = (styles.GenericFontFamilyType.sansSerif,)
_DEFAULT_FONT_SIZE = styles.LengthType(15 * 5, styles.LengthType.Units.pct) # 5vh for ttp:cellResolution="32 15"
_DEFAULT_TEXT_COLOR = styles.NamedColors.white.value
_DEFAULT_LINE_PADDING = styles.LengthType(0.5, styles.LengthType.Units.c)
_DEFAULT_LINE_HEIGHT = styles.LengthType(125, styles.LengthType.Units.pct)
_DEFAULT_BG_COLOR = styles.ColorType((0, 0, 0, 204))
_DEFAULT_ROWS = 23
_DEFAULT_COLS = 40

_VTT_PCT_RE = re.compile(r"(\d+\.?\d*)%")

def parse_vtt_pct(value: str):
  """Parse a WebVTT precentage value"""
  m = _VTT_PCT_RE.fullmatch(value)
  if m:
    return round(float(m.group(1)))
  return None

# integer has at most 20 digits
_VTT_INT_RE = re.compile(r"(-?\d{1,20})")

def parse_vtt_int(value: str):
  """Parse a WebVTT integer value"""
  m = _VTT_INT_RE.fullmatch(value)
  if m:
    return int(m.group(1))
  return None

def _get_or_make_region(
  doc: model.ContentDocument,
  cue_settings_list: str
  ):
  """Returns a matching region from `doc` or creates one
  """

  writing_mode = styles.WritingModeType.lrtb
  text_align = styles.TextAlignType.center
  display_align = styles.DisplayAlignType.after
  extent_height = 100 - 200/_DEFAULT_ROWS
  extent_width = 100 - 200/_DEFAULT_COLS
  origin_x = 100/_DEFAULT_COLS
  origin_y = 100/_DEFAULT_ROWS

  cue_settings = dict(filter(lambda x: len(x) == 2, [x.split(":") for x in cue_settings_list]))

  # writing direction

  value = cue_settings.get("vertical")
  if value == "lr":
    writing_mode = styles.WritingModeType.tblr
  elif value == "rl":
    writing_mode = styles.WritingModeType.tbrl
  elif value is not None:
    LOGGER.warning("Bad vertical setting value: %s", value)


  # size

  value = cue_settings.get("size")
  if value is not None:
    pct = parse_vtt_pct(value)
    if pct is not None:
      if writing_mode in (styles.WritingModeType.tblr, styles.WritingModeType.tbrl):
        extent_height = pct
      else:
        extent_width = pct
    else:
      LOGGER.warning("Bad size setting value: %s", value)

  # text align

  value = cue_settings.get("align")
  if value == "left":
    text_align = styles.TextAlignType.end if writing_mode == styles.WritingModeType.rltb else styles.TextAlignType.start
  elif value == "right":
    text_align = styles.TextAlignType.start if writing_mode == styles.WritingModeType.rltb else styles.TextAlignType.end
  elif value == "start":
    text_align = styles.TextAlignType.start
  elif value == "center":
    text_align = styles.TextAlignType.center
  elif value == "end":
    text_align = styles.TextAlignType.end
  elif value is not None:
    LOGGER.warning("Bad alignment setting value: %s", value)

  # line

  value = cue_settings.get("line")
  if value is not None:
    value = value.split(",")
    line_align = value[1] if len(value) > 1 else "start"

    line_offset = parse_vtt_pct(value[0])
    if line_offset is None:
      line_num = parse_vtt_int(value[0])
      if line_num is not None:
        if writing_mode in (styles.WritingModeType.rltb, styles.WritingModeType.lrtb):
          line_offset = 100 * line_num/_DEFAULT_ROWS if line_num > 0 else 100 - 100 * line_num/_DEFAULT_ROWS
        else:
          line_offset = 100 * line_num/_DEFAULT_COLS if line_num > 0 else 100 - 100 * line_num/_DEFAULT_COLS

    if line_offset is not None:
      if line_align == "center":
        if writing_mode in (styles.WritingModeType.rltb, styles.WritingModeType.lrtb):
          extent_height = min(line_offset, 100 - line_offset) * 2
          origin_y = line_offset - extent_height / 2
        else:
          extent_width = min(line_offset, 100 - line_offset) * 2
          origin_x = line_offset - extent_height / 2
        display_align = styles.DisplayAlignType.center
      elif line_align == "start":
        if writing_mode in (styles.WritingModeType.rltb, styles.WritingModeType.lrtb):
          extent_height = 100 - line_offset
          origin_y = line_offset
        else:
          extent_width = 100 - line_offset
          origin_x = line_offset
        display_align = styles.DisplayAlignType.before
      elif line_align == "end":
        if writing_mode in (styles.WritingModeType.rltb, styles.WritingModeType.lrtb):
          extent_height = line_offset
          origin_y = 0
        else:
          extent_width = line_offset
          origin_x = 0
        display_align = styles.DisplayAlignType.after
      else:
        LOGGER.warning("Bad line alignment setting value: %s", line_align)

    else:
      LOGGER.warning("Bad line setting value: %s", cue_settings.get("line"))

  # position

  value = cue_settings.get("position")
  if value is not None:
    value = value.split(",")

    if len(value) > 1 and value[1] in ("center", "line-left", "line-right"):
      line_align = value[1]
    else:
      if text_align == styles.TextAlignType.start:
        line_align = "line-right" if writing_mode == styles.WritingModeType.rltb else "line-left"
      elif text_align == styles.TextAlignType.end:
        line_align = "line-left" if writing_mode == styles.WritingModeType.rltb else "line-right"
      else:
        line_align = "center"

    position = parse_vtt_pct(value[0])
    if position is not None:
      if line_align == "center":
        if writing_mode in (styles.WritingModeType.rltb, styles.WritingModeType.lrtb):
          origin_x = position - extent_width / 2
        else:
          origin_y = position - extent_height / 2
      elif line_align == "line-left":
        if writing_mode in (styles.WritingModeType.rltb, styles.WritingModeType.lrtb):
          origin_x = position
        else:
          origin_y = position
      elif line_align == "line-right":
        if writing_mode in (styles.WritingModeType.rltb, styles.WritingModeType.lrtb):
          origin_x = position - extent_width
        else:
          origin_y = position - extent_height
      else:
        LOGGER.warning("Bad position alignment setting value: %s", line_align)

    else:
      LOGGER.warning("Bad position setting value: %s", cue_settings.get("position"))


  extent = styles.ExtentType(
    height=styles.LengthType(extent_height),
    width=styles.LengthType(extent_width)
  )
  origin = styles.CoordinateType(
    x=styles.LengthType(origin_x),
    y=styles.LengthType(origin_y)
  )

  found_region = None
  regions = list(doc.iter_regions())
  for r in regions:

    if r.get_style(styles.StyleProperties.WritingMode) != writing_mode:
      continue

    if r.get_style(styles.StyleProperties.Extent) != extent:
      continue

    if r.get_style(styles.StyleProperties.Origin) != origin:
      continue

    if r.get_style(styles.StyleProperties.TextAlign) != text_align:
      continue

    if r.get_style(styles.StyleProperties.DisplayAlign) != display_align:
      continue

    found_region = r
    break

  if found_region is None:
    found_region = model.Region(f"r{len(regions)}", doc)
    found_region.set_style(styles.StyleProperties.Origin, origin)
    found_region.set_style(styles.StyleProperties.Extent, extent)
    found_region.set_style(styles.StyleProperties.DisplayAlign, display_align)
    found_region.set_style(styles.StyleProperties.TextAlign, text_align)
    found_region.set_style(styles.StyleProperties.WritingMode, writing_mode)
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

      continue

    if state in (_State.TEXT, _State.TEXT_MORE):

      if line is None or _EMPTY_RE.fullmatch(line):
        subtitle_text = subtitle_text.strip('\r\n').replace(r"\n\r", "\n")

        _parse_cue_text(subtitle_text, current_p, line_index)

        state = _State.LOOKING
        continue

      if state is _State.TEXT:
        div.push_child(current_p)
        subtitle_text = ""

      subtitle_text += line

      state = _State.TEXT_MORE

      continue

  return doc
