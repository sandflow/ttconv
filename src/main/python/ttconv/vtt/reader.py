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
from html.parser import HTMLParser

from ttconv import model
from ttconv import style_properties as styles
from ttconv.imsc.utils import parse_color

LOGGER = logging.getLogger(__name__)

#
# SRT reader
#

def _none_terminated(iterator):
  for item in iterator:
    yield item
  yield None

class _TextParser(HTMLParser):

  def __init__(self, paragraph: model.P, line_number: int) -> None:
    self.line_num: int = line_number
    self.parent: model.ContentElement = paragraph
    super().__init__()

  def handle_starttag(self, tag, attrs):

    span = model.Span(self.parent.get_doc())
    self.parent.push_child(span)
    self.parent = span

    if tag.lower().startswith("b"):
      span.set_style(styles.StyleProperties.FontWeight, styles.FontWeightType.bold)
    elif tag.lower().startswith("i"):
      span.set_style(styles.StyleProperties.FontStyle, styles.FontStyleType.italic)
    elif tag.lower().startswith("u"):
      span.set_style(styles.StyleProperties.TextDecoration, styles.TextDecorationType(underline=True))
    elif tag.lower().startswith("c"):
      for c in tag.lower().split(".")[1:]:
        if c == "blue":
          span.set_style(styles.StyleProperties.Color, styles.NamedColors.blue.value)
        elif c == "bg_blue":
          span.set_style(styles.StyleProperties.BackgroundColor, styles.NamedColors.blue.value)
    else:
      LOGGER.warning("Unknown tag %s at line %s", tag, self.line_num)
      return

  def handle_endtag(self, tag):
    self.parent = self.parent.parent()

  def handle_data(self, data):
    lines = data.split("\n")

    for i, line in enumerate(lines):
      if i > 0:
        self.parent.push_child(model.Br(self.parent.get_doc()))
      span = model.Span(self.parent.get_doc())
      span.push_child(model.Text(self.parent.get_doc(), line))
      self.parent.push_child(span)

class _State(Enum):
  LOOKING = 1
  TC = 2
  TEXT = 3
  TEXT_MORE = 4
  START = 5
  NOTE = 6

_EMPTY_RE = re.compile(r"\s+")
_TIMECODE_RE = re.compile(r"(?:(?P<begin_h>[0-9]{2,3}):)?(?P<begin_m>[0-9]{2}):(?P<begin_s>[0-9]{2})\.(?P<begin_ms>[0-9]{3})\s+-->\s+(?:(?P<end_h>[0-9]{2,3}):)?(?P<end_m>[0-9]{2}):(?P<end_s>[0-9]{2})\.(?P<end_ms>[0-9]{3})(?:\s+(?P<settings>.+))?")
_DEFAULT_FONT_STACK = ("Verdana", "Arial", "Tiresias", styles.GenericFontFamilyType.sansSerif)
_DEFAULT_FONT_SIZE = styles.LengthType(80, styles.LengthType.Units.pct)
_DEFAULT_OUTLINE_THICKNESS = styles.LengthType(5, styles.LengthType.Units.pct)
_DEFAULT_TEXT_COLOR = styles.NamedColors.white.value
_DEFAULT_OUTLINE_COLOR = styles.NamedColors.black.value
_DEFAULT_LINE_HEIGHT = styles.LengthType(125, styles.LengthType.Units.pct)

_VTT_PCT_RE = re.compile(r"(\d+\.?\d*)%")
_VTT_INT = re.compile(r"(-?\d+)")

def _get_or_make_region(
  doc: model.ContentDocument,
  cue_settings_list: str
  ):
  """Returns a matching region from `doc` or creates one
  """

  writing_direction = styles.WritingModeType.lrtb
  extent = styles.ExtentType(
    height=styles.LengthType(100),
    width=styles.LengthType(100)
  )
  size = styles.LengthType(100)
  alignment = styles.TextAlignType.start

  cue_settings = dict(x.split(":") for x in cue_settings_list.split())

  # writing direction

  value = cue_settings.get("vertical")
  if value == "lr":
    writing_direction = styles.WritingModeType.tblr
  elif value == "rl":
    writing_direction = styles.WritingModeType.tbrl
  elif value is not None:
    LOGGER.warn(f"Bad vertical setting value: {value}")

  # size

  value = cue_settings.get("size")
  if value is not None:
    m = _VTT_PCT_RE.fullmatch(value)
    if m:
      pct = round(float(m.group(1)) * 100)
      if writing_direction in (styles.WritingModeType.tblr, styles.WritingModeType.tbrl):
        extent.height = pct
      else:
        extent.width = pct
    else:
      LOGGER.warn(f"Bad size setting value: {value}")

  # text align

  value = cue_settings.get("align")
  if value == "left":
    alignment = styles.TextAlignType.end if writing_direction ==  styles.WritingModeType.rltb else styles.TextAlignType.start
  elif value == "right":
    alignment = styles.TextAlignType.start if writing_direction ==  styles.WritingModeType.rltb else styles.TextAlignType.end
  elif value == "start":
    alignment = styles.TextAlignType.start
  elif value == "center":
    alignment = styles.TextAlignType.center
  elif value == "end":
    alignment = styles.TextAlignType.end
  elif value is not None:
    LOGGER.warn(f"Bad vertical setting value: {value}")

  # line

  value = cue_settings.get("line")
  if value is not None:
    value.split(",")
    line_align = value[1] if len(value) > 1 else None
    value = value[0]

  found_region = None

  regions = list(doc.iter_regions())

  for r in regions:
    found_region = r
    break

  if found_region is None:
    found_region = model.Region(f"r{len(regions)}", doc)
    found_region.set_style(
      styles.StyleProperties.Origin,
      styles.CoordinateType(
        x=styles.LengthType(5, styles.LengthType.Units.pct),
        y=styles.LengthType(5, styles.LengthType.Units.pct)
      )
    )
    found_region.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        height=styles.LengthType(90, styles.LengthType.Units.pct),
        width=styles.LengthType(90, styles.LengthType.Units.pct)
      )
    )
    found_region.set_style(
      styles.StyleProperties.DisplayAlign,
      styles.DisplayAlignType.after
    )
    found_region.set_style(
      styles.StyleProperties.TextAlign,
      styles.TextAlignType.center
    )
    found_region.set_style(
      styles.StyleProperties.LineHeight,
      _DEFAULT_LINE_HEIGHT
    )
    found_region.set_style(
      styles.StyleProperties.FontFamily,
      _DEFAULT_FONT_STACK
    )
    found_region.set_style(
      styles.StyleProperties.FontSize,
      _DEFAULT_FONT_SIZE
    )
    found_region.set_style(
      styles.StyleProperties.Color,
      _DEFAULT_TEXT_COLOR
    )
    found_region.set_style(
      styles.StyleProperties.TextOutline,
      styles.TextOutlineType(
        _DEFAULT_OUTLINE_THICKNESS,
        _DEFAULT_OUTLINE_COLOR
      )
    )
    doc.put_region(found_region)

  return found_region

def to_model(data_file: typing.IO, _config = None, progress_callback=lambda _: None):
  """Converts an SRT document to the data model"""

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
        LOGGER.warn("The first line of the file does not start with WEBVTT")
      state = _State.LOOKING
      continue

    if state is _State.NOTE:
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
        # we ignore notes
        state = _State.NOTE
        continue

      m = _TIMECODE_RE.search(line)

      if m is None:
        # skip over cue id
        continue

      current_p = model.P(doc)

      current_p.set_begin(
        int(m.group('begin_h') if m.group('begin_h') is not None else 0) * 3600 + 
        int(m.group('begin_m')) * 60 + 
        int(m.group('begin_s')) +
        int(m.group('begin_ms')) / 1000
        )

      current_p.set_end(
        int(m.group('end_h') if m.group('begin_h') is not None else 0) * 3600 + 
        int(m.group('end_m')) * 60 + 
        int(m.group('end_s')) +
        int(m.group('end_ms')) / 1000
        )

      # handle settings

      current_p.set_region(_get_or_make_region(doc, ""))

      state = _State.TEXT

      continue

    if state in (_State.TEXT, _State.TEXT_MORE):

      if line is None or _EMPTY_RE.fullmatch(line):
        subtitle_text = subtitle_text.strip('\r\n')\
          .replace(r"\n\r", "\n")

        parser = _TextParser(current_p, line_index)
        parser.feed(subtitle_text)
        parser.close()

        state = _State.LOOKING
        continue

      if state is _State.TEXT:
        div.push_child(current_p)
        subtitle_text = ""

      if state is _State.TEXT_MORE:
        current_p.push_child(model.Br(current_p.get_doc()))

      subtitle_text += line

      state = _State.TEXT_MORE

      continue

  return doc
