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

"""STL text field (TF) processing"""

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

def _is_character_code(c) -> bool:
  return 0x20 <= c <= 0x7F or 0xA0 <= c <= 0xFF

def _is_printable_code(c) -> bool:
  return _is_character_code(c) and c != 0x20
 
def _is_control_code(c) -> bool:
  return 0x00 <= c <= 0x07 or 0x0A <= c <= 0x0D or 0x1C <= c <= 0x1D or 0x80 <= c <= 0x85

def _is_newline_code(c) -> bool:
  return c == 0x8A

def _is_unused_space_code(c) -> bool:
  return c == _UNUSED_SPACE_CODE

def _is_space_code(c) -> bool:
  return c == 0x20

def _is_lwsp_code(c) -> bool:
  return _is_control_code(c) or _is_newline_code(c) or _is_space_code(c)

def _note_decode_error(error):
  LOGGER.warning("Unknown character: %s", hex(error.object[error.start]))
  return ("�", error.end)

codecs.register_error("note", _note_decode_error)

def line_count(text_field: bytes, is_double_height: bool) -> int:
  """Returns the number of lines separated by one or more newline characters
  in the TF field `text_field`
  """
  count = 0
  was_eol = False

  for c in text_field:
    if _is_newline_code(c):
      if is_double_height:
        if was_eol:
          was_eol = False
        else:
          count += 1
          was_eol = True
      else:
        count += 1
        was_eol = True
    else:
      was_eol= False

  return count + 1

def has_double_height_char(text_field) -> bool:
  """Returns true if TF field `text_field` contains any double-height characters"""
  return any(map(lambda c: c == 0x0D, text_field))

class _TextFieldIterator:

  def __init__(self, text_field):
    self.pos = 0
    self.tf = text_field

  def __iter__(self):
    return self

  def peek_next(self) -> int:
    return _UNUSED_SPACE_CODE if self.pos + 1 >= len(self.tf) else self.tf[self.pos + 1]

  def peek_prev(self) -> int:
    return _UNUSED_SPACE_CODE if self.pos <= 0 else self.tf[self.pos - 1]

  def cur(self) -> int:
    return _UNUSED_SPACE_CODE if self.pos >= len(self.tf) else self.tf[self.pos]

  def __next__(self) -> int:
    c = self.peek_next()
    self.pos = min(self.pos + 1, len(self.tf))
    return c

class _Context:

  def __init__(self, parent_element: model.ContentElement, is_teletext: bool, decode_func):
    self.fg_color = None
    self.bg_color = None
    self.is_italic = None
    self.is_underline = None
    self.reset_styles(is_teletext)

    self.span = None
    self.parent = parent_element
    self.decode_func = decode_func
    self.text_buffer = bytearray()

  def reset_styles(self, is_teletext: bool):
    self.fg_color = styles.NamedColors.white.value
    self.bg_color = styles.NamedColors.black.value if is_teletext else styles.NamedColors.transparent.value
    self.is_italic = False
    self.is_underline = False

  def set_bg_color(self, color: styles.ColorType):
    self.bg_color = color 

  def get_bg_color(self) -> styles.ColorType:
    return self.bg_color

  def set_fg_color(self, color: styles.ColorType):
    self.fg_color = color 

  def get_fg_color(self) -> styles.ColorType:
    return self.fg_color

  def set_underline(self, is_underline: bool):
    self.is_underline = is_underline

  def get_underline(self) -> bool:
    return self.is_underline

  def set_italic(self, is_italic: bool):
    self.is_italic = is_italic

  def get_italic(self) -> bool:
    return self.is_italic

  def start_span(self):
    if self.span is None:
      self.span = model.Span(self.parent.get_doc())

      self.span.set_style(styles.StyleProperties.BackgroundColor, self.get_bg_color())

      self.span.set_style(styles.StyleProperties.Color, self.get_fg_color())

      if self.get_underline():
        self.span.set_style(
          styles.StyleProperties.TextDecoration,
          styles.TextDecorationType(underline=True)
        )

      if self.get_italic():
        self.span.set_style(
          styles.StyleProperties.FontStyle,
          styles.FontStyleType.italic
        )

  def end_span(self):
    if len(self.text_buffer) > 0 and self.span is not None:
      text_element = model.Text(self.parent.get_doc())
      text_element.set_text(self.decode_func(self.text_buffer, errors="note")[0])

      self.span.push_child(text_element)
      self.parent.push_child(self.span)
      self.span = None
      self.text_buffer.clear()

  def append_character(self, c):
    self.start_span()
    self.text_buffer.append(c)


def to_model(element: model.ContentElement, is_teletext: bool, tti_cct: bytes, tti_tf: bytes):
  """Converts the EBU STL text field `tti_tf` to a sequence of span elements and 
  appends them to the content element `element`. `is_teletext` indicates whether the text
  field is interpreted as teletext or open/undefined. `tti_cct` specifies the text field code page as
  signaled in the TTI CCT field.
  """

  tf_iter = _TextFieldIterator(tti_tf)

  decode_func = _CHAR_DECODER_MAP.get(tti_cct)

  if decode_func is None:
    decode_func = iso6937.decode
    LOGGER.error("Unknown Text Field character set: %s", str(tti_cct))

  context = _Context(element, is_teletext, decode_func)

  while True:

    c = tf_iter.cur()

    if _is_unused_space_code(c):
      break

    if _is_character_code(c):
      if _is_printable_code(c) or (_is_printable_code(tf_iter.peek_next()) and _is_printable_code(tf_iter.peek_prev())):
        context.append_character(c)

    elif _is_newline_code(c):
      if not _is_newline_code(tf_iter.peek_next()) and not _is_unused_space_code(tf_iter.peek_next()):
        context.end_span()
        element.push_child(model.Br(element.get_doc()))
        if is_teletext:
          context.reset_styles(is_teletext)

    elif _is_control_code(c):
      context.end_span()

      if c == 0x1C:
        context.set_bg_color(styles.NamedColors.black.value)
      elif c == 0x85:
        context.set_bg_color(styles.NamedColors.transparent.value)
      elif c == 0x1D:
        context.set_bg_color(context.get_fg_color())
      elif c == 0x00:
        context.set_fg_color(styles.NamedColors.black.value)
      elif c == 0x01:
        context.set_fg_color(styles.NamedColors.red.value)
      elif c == 0x02:
        context.set_fg_color(styles.NamedColors.lime.value)
      elif c == 0x03:
        context.set_fg_color(styles.NamedColors.yellow.value)
      elif c == 0x04:
        context.set_fg_color(styles.NamedColors.blue.value)
      elif c == 0x05:
        context.set_fg_color(styles.NamedColors.magenta.value)
      elif c == 0x06:
        context.set_fg_color(styles.NamedColors.cyan.value)
      elif c == 0x07:
        context.set_fg_color(styles.NamedColors.white.value)
      elif c == 0x80:
        context.set_italic(True)
      elif c == 0x81:
        context.set_italic(False)
      elif c == 0x82:
        context.set_underline(True)
      elif c == 0x83:
        context.set_underline(False)

      if (_is_printable_code(tf_iter.peek_next()) and _is_printable_code(tf_iter.peek_prev())):
        context.append_character(0X20)

    next(tf_iter)

  context.end_span()
