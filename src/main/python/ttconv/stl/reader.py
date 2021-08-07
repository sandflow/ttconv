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

"""STL reader"""

from __future__ import annotations

import logging
import typing
import collections
import struct
import itertools
import codecs
from fractions import Fraction

from ttconv.time_code import SmpteTimeCode 
from ttconv import model
import ttconv.style_properties as styles
from ttconv.stl.config import STLReaderConfiguration
import ttconv.stl.iso6937 as iso6937

LOGGER = logging.getLogger(__name__)


GSIBlock = collections.namedtuple(
  "GSI",
  ["CPN", "DFC", "DSC", "CCT", "LC", "OPT", "OET", "TPT", "TET", "TN", "TCD", "SLR", "CD", "RD", "RN", \
    "TNB", "TNS", "TNG", "MNC", "MNR", "TCS", "TCP", "TCF", "TND", "DSN", "CO", "PUB", "EN", "ECD", "UDA"]
)

TTIBlock = collections.namedtuple(
  "TTI",
  ["SGN", "SN", "EBN", "CS", "TCIh", "TCIm", "TCIs", "TCIf", "TCOh", "TCOm", "TCOs", "TCOf", "VP", "JC", "CF", "TF"]
)

_UNUSED_SPACE_CODE = 0x8F

def is_character_code(c) -> bool:
  return 0x20 <= c <= 0x7F or 0xA0 <= c <= 0xFF

def is_printable_code(c) -> bool:
  return is_character_code(c) and c != 0x20
 
def is_control_code(c) -> bool:
  return 0x00 <= c <= 0x07 or 0x0A <= c <= 0x0D or 0x1C <= c <= 0x1D or 0x80 <= c <= 0x85

def is_newline_code(c) -> bool:
  return c == 0x8A

def is_unused_space_code(c) -> bool:
  return c == _UNUSED_SPACE_CODE

def is_space_code(c) -> bool:
  return c == 0x20

def is_lwsp_code(c) -> bool:
  return is_control_code(c) or is_newline_code(c) or is_space_code(c)

def note_decode_error(error):
  LOGGER.warning("Unknown character: %s", hex(error.object[error.start]))
  return ("�", error.end)

codecs.register_error("note", note_decode_error)

def process_tti_tf(element: model.ContentElement, tti_cct, tti_tf):
  
  fg_color = styles.NamedColors.white.value

  bg_color = styles.NamedColors.transparent.value

  is_italic = False

  is_underline = False

  span_element = None

  text_buffer = bytearray()

  tf_i = 0

  if tti_cct == b'00':
    decode_func = iso6937.decode
  elif tti_cct == b'01':
    decode_func = codecs.getdecoder("iso8859_5")
  elif tti_cct == b'02':
    decode_func = codecs.getdecoder("iso8859_6")
  elif tti_cct == b'03':
    decode_func = codecs.getdecoder("iso8859_7")
  elif tti_cct == b'04':
    decode_func = codecs.getdecoder("iso8859_8")
  else:
    raise NotImplementedError

  def peek_next_char() -> int:
    return _UNUSED_SPACE_CODE if tf_i >= len(tti_tf) else tti_tf[tf_i + 1]

  def peek_prev_char() -> int:
    return _UNUSED_SPACE_CODE if tf_i <= 0 else tti_tf[tf_i - 1]

  def next_char() -> int:
    nonlocal tf_i
    c = peek_next_char()
    tf_i = min(tf_i + 1, len(tti_tf))
    return c

  def cur_char() -> int:
    return _UNUSED_SPACE_CODE if tf_i >= len(tti_tf) else tti_tf[tf_i]

  def start_span():
    nonlocal span_element
    nonlocal bg_color
    nonlocal fg_color
    nonlocal is_underline
    nonlocal is_italic

    if span_element is None:
      span_element = model.Span(element.get_doc())
      span_element.set_style(styles.StyleProperties.BackgroundColor, bg_color)
      span_element.set_style(styles.StyleProperties.Color, fg_color)
      if is_underline:
        span_element.set_style(
          styles.StyleProperties.TextDecoration,
          styles.TextDecorationType(underline=True)
        )
      if is_italic:
        span_element.set_style(
          styles.StyleProperties.FontStyle,
          styles.FontStyleType.italic
        )

  def end_span():
    nonlocal span_element

    if len(text_buffer) > 0 and span_element is not None:
      text_element = model.Text(element.get_doc())
      text_element.set_text(decode_func(text_buffer, errors="note")[0])

      span_element.push_child(text_element)
      element.push_child(span_element)
      span_element = None
      text_buffer.clear()

  def append_character(c):
    if c != 0x20 or (is_printable_code(peek_next_char()) and is_printable_code(peek_prev_char())):
      start_span()
      text_buffer.append(c)

  def new_line():
    if not is_newline_code(peek_next_char()) and not is_unused_space_code(peek_next_char()):
      end_span()
      element.push_child(model.Br(element.get_doc()))
      start_span()

  while True:

    c = cur_char()

    if is_unused_space_code(c):
      break

    if is_character_code(c):
      # start_span()
      append_character(c)

    elif is_newline_code(c):
      new_line()

    elif is_control_code(c):
      end_span()

      if c in (0x84, 0x0B, 0x1C):
        bg_color = styles.NamedColors.black.value
      elif c == 0x85:
        bg_color = styles.NamedColors.transparent.value
      elif c == 0x1D:
        bg_color = fg_color
      elif c == 0x00:
        fg_color = styles.NamedColors.black.value
      elif c == 0x01:
        fg_color = styles.NamedColors.red.value
      elif c == 0x02:
        fg_color = styles.NamedColors.lime.value
      elif c == 0x03:
        fg_color = styles.NamedColors.yellow.value
      elif c == 0x04:
        fg_color = styles.NamedColors.blue.value
      elif c == 0x05:
        fg_color = styles.NamedColors.magenta.value
      elif c == 0x06:
        fg_color = styles.NamedColors.cyan.value
      elif c == 0x07:
        fg_color = styles.NamedColors.white.value
      elif c == 0x80:
        is_italic = True
      elif c == 0x81:
        is_italic = False
      elif c == 0x82:
        is_underline = True
      elif c == 0x83:
        is_underline = False

      append_character(0x20)

    next_char()

  end_span()


#
# STL reader
#

def to_model(stl_document: typing.IO, _config: typing.Optional[STLReaderConfiguration] = None, progress_callback=lambda _: None):
  """Converts an STL document to the data model"""

  gsi_block = GSIBlock._make(
    struct.unpack(
      '3s8sc2s2s32s32s32s32s32s32s16s6s6s2s5s5s3s2s2s1s8s8s1s1s3s32s32s32s75x576s',
      stl_document.read(1024)
    )
  )

  if gsi_block.DFC == b'STL25.01':
    gsi_fps = Fraction(25)
  elif gsi_block.DFC == b'STL30.01':
    gsi_fps = Fraction(30000, 1001)
  elif gsi_block.DFC == b'STL50.01':
    gsi_fps = Fraction(50)
    LOGGER.warning("Non-standard 50 fps frame rate")
  else:
    LOGGER.error("Unknown frame rate %s, defaulting to 25 fps", gsi_block.DFC)
    gsi_fps = Fraction(25)

  gsi_cct = gsi_block.CCT

  # language code LC

  # max number of rows

  if gsi_block.DSC in (0x31, 0x32):
    # teletext
    gsi_mnr = 23
  else:
    # open or undefined
    gsi_mnr = int(gsi_block.MNR)

  tti_block_count = int(gsi_block.TNB)

  doc = model.ContentDocument()

  # assume 44x23 character matrix within a ‘Subtitle Safe Area’ of ~90% of the width and ~80% height of the related video object
  doc.set_cell_resolution(
    model.CellResolutionType(
      columns=44,
      rows=29)
  )

  body = model.Body(doc)
  doc.set_body(body)

  sgn_map = {}

  region_map = {}

  last_sn = None

  is_in_extension = False

  tti_tf = b''

  for i in itertools.count():
    
    buf = stl_document.read(128)

    if not buf:
      break

    tti_block = TTIBlock._make(
      struct.unpack(
        '<BHBBBBBBBBBBBBB112s',
        buf
      )
    )

    tti_ebn = tti_block.EBN

    if 0xEF < tti_ebn < 0xFF:
      # skip user data and reserved blocks
      continue

    if is_in_extension:

      # if we are within an extension block, only accumulate the text information

      tti_tf += tti_block.TF
      
    else:

      # otherwise, initilialize the subtitle information

      tti_tf = tti_block.TF

      tti_sn = tti_block.SN
      tti_sgn = int(tti_block.SGN)
      tti_cs = tti_block.CS
      tti_tci = SmpteTimeCode(tti_block.TCIh, tti_block.TCIm, tti_block.TCIs, tti_block.TCIf, gsi_fps)
      tti_tco = SmpteTimeCode(tti_block.TCOh, tti_block.TCOm, tti_block.TCOs, tti_block.TCOf, gsi_fps)
      tti_jc = tti_block.JC
      tti_vp = tti_block.VP

    # continue accumulating if we have an extension block

    if tti_ebn != 0xFF:
      is_in_extension = True
      continue

    is_in_extension = False

    # create a new subtitle if SN changes and we are not in cumulative mode

    if tti_sn is not last_sn and tti_cs in (0x00, 0x01):

      # find the div to which the subtitle belongs, based on SGN

      cur_div = sgn_map.get(tti_sgn)

      # create the div if it does not exist

      if cur_div is None:
        cur_div = model.Div(doc)
        body.push_child(cur_div)
        sgn_map[tti_sgn] = cur_div

      # create the p that will hold the subtitle

      sub_element = model.P(doc)

      if tti_jc == 0x01:
        sub_element.set_style(styles.StyleProperties.TextAlign, styles.TextAlignType.start)
      elif tti_jc == 0x03:
        sub_element.set_style(styles.StyleProperties.TextAlign, styles.TextAlignType.end)
      else:
        sub_element.set_style(styles.StyleProperties.TextAlign, styles.TextAlignType.center)

      # assume that VP < MNR/2 means bottom-aligned and otherwise top-aligned
      # probably should offer an option to override this

      if tti_vp > gsi_mnr / 2:
        region = region_map.get(0)

        if region is None:
          region = model.Region("bottom", doc)
          region.set_style(
            styles.StyleProperties.Extent,
            styles.ExtentType(
              height=styles.LengthType(value=80, units=styles.LengthType.Units.pct),
              width=styles.LengthType(value=90, units=styles.LengthType.Units.pct),
            )
          )
          region.set_style(
            styles.StyleProperties.Origin,
            styles.CoordinateType(
              x=styles.LengthType(5, styles.LengthType.Units.pct),
              y=styles.LengthType(10, styles.LengthType.Units.pct)
            )
          )
          region.set_style(
            styles.StyleProperties.DisplayAlign,
            styles.DisplayAlignType.after
          )
          doc.put_region(region)
          region_map[0] = region
      else:
        region = region_map.get(1)

        if region is None:
          region = model.Region("top", doc)
          region.set_style(
            styles.StyleProperties.Extent,
            styles.ExtentType(
              height=styles.LengthType(value=80, units=styles.LengthType.Units.pct),
              width=styles.LengthType(value=90, units=styles.LengthType.Units.pct),
            )
          )
          region.set_style(
            styles.StyleProperties.Origin,
            styles.CoordinateType(
              x=styles.LengthType(5, styles.LengthType.Units.pct),
              y=styles.LengthType(10, styles.LengthType.Units.pct)
            )
          )
          region.set_style(
            styles.StyleProperties.DisplayAlign,
            styles.DisplayAlignType.before
          )
          doc.put_region(region)
          region_map[1] = region

      sub_element.set_region(region)

      cur_div.push_child(sub_element)

    if tti_cs in (0x01, 0x02, 0x03):

      # create a nested span if we are in cumulative mode

      cur_element = model.Span(doc)
      sub_element.push_child(cur_element)
      sub_element.push_child(model.Br(doc))

    else :

      cur_element = sub_element

    cur_element.set_begin(tti_tci.to_temporal_offset())
    cur_element.set_end(tti_tco.to_temporal_offset())
    process_tti_tf(cur_element, gsi_cct, tti_tf)
    progress_callback(i/tti_block_count)

  return doc
