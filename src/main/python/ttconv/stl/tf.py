#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2021, Sandflow Consulting LLC
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

import logging
import codecs

from ttconv import model
import ttconv.style_properties as styles
from ttconv.stl import iso6937

LOGGER = logging.getLogger(__name__)

_CHAR_DECODER_MAP = {
  b'00': iso6937.decode,
  b'01': codecs.getdecoder("iso8859_5"),
  b'02' : codecs.getdecoder("iso8859_6"),
  b'03': codecs.getdecoder("iso8859_7"),
  b'04':codecs.getdecoder("iso8859_8")
}

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

def line_count(text_field) -> int:
  return sum(map(is_newline_code, text_field)) + 1

def is_double_height(text_field) -> bool:
  return any(map(lambda c: c == 0x0D, text_field))

def to_model(element: model.ContentElement, is_teletext, tti_cct, tti_tf):
  
  fg_color = styles.NamedColors.white.value

  bg_color = styles.NamedColors.black.value if is_teletext else styles.NamedColors.transparent.value

  is_italic = False

  is_underline = False

  span_element = None

  text_buffer = bytearray()

  tf_i = 0

  decode_func = _CHAR_DECODER_MAP.get(tti_cct)

  if decode_func is None:
    decode_func = iso6937.decode
    LOGGER.error("Unknown Text Field character set: %s", str(tti_cct))

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
      append_character(c)

    elif is_newline_code(c):
      new_line()

    elif is_control_code(c):
      end_span()

      if c == 0x1C:
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