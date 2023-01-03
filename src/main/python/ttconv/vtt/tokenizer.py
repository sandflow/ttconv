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

"""WebVTT Cue Text tokenizer. See https://www.w3.org/TR/webvtt1/#webvtt-cue-text-tokenizer"""

from __future__ import annotations
from enum import Enum
import re
from typing import List, Optional
import html

class StringBuf:
  """Simple class that allows a string to be built from the concatenation of
  multiple strings, starting with an initial string."""
  def __init__(self, initial_value: str = None) -> None:
    self.buf: List[str] = [initial_value] if initial_value is not None else []

  def append(self, s: str) -> None:
    self.buf.append(s)

  def extend(self, sb: StringBuf) -> None:
    self.buf.extend(sb.buf)

  def __str__(self) -> str:
    return "".join(self.buf)

  def is_empty(self) -> bool:
    return len(self.buf) == 0 or all(map(lambda x: len(x) == 0, self.buf))

class Token:
  """Base class for WebVTT Cue Text tokens."""
  pass

class StringToken(Token):
  """WebVTT Cue Text string token."""
  def __init__(self, value: str = "") -> None:
    super().__init__()
    self.value = value

class StartTagToken(Token):
  """WebVTT Cue Text start tag token"""
  def __init__(self, tag: str = "", classes: Optional[List[str]] = None, annotation: Optional[str] = None) -> None:
    super().__init__()
    self.tag = tag
    self.classes = classes
    self.annotation = annotation

class EndTagToken(Token):
  """WebVTT Cue Text end tag token"""
  def __init__(self, tag: str = "") -> None:
    super().__init__()
    self.tag = tag

class TimestampTagToken(Token):
  """WebVTT Cue Text timestamp tag token"""
  def __init__(self, timestamp: str = "") -> None:
    super().__init__()
    self.timestamp = timestamp


def CueTextTokenizer(cue_text: str):
  """Generator that outputs a sequence of WebVTT Cue Text tokens from a WebVTT
  Cue Text."""
  EOF_MARKER = -1

  class _State(Enum):
    data = 1
    tag = 2
    data_cref = 3
    start_tag = 4
    start_tag_annot = 5
    start_tag_class = 6
    end_tag = 7
    ts_tag = 8
    annot_cref = 3

  cue_text: str = cue_text
  position: int = 0

  # token loop
  while position < len(cue_text):
    state: _State = _State.data
    result: StringBuf = StringBuf()
    classes: List[str] = []
    buffer: StringBuf = StringBuf()

    # codepoint loop
    while True:
      c = ord(cue_text[position]) if position < len(cue_text) else EOF_MARKER

      if state is _State.data:
        if c == ord("&"):
          state = _State.data_cref
          buffer = StringBuf("&")
        elif c == ord("<"):
          if result.is_empty():
            state = _State.tag
          else:
            yield StringToken(str(result))
            break
        elif c == EOF_MARKER:
          yield StringToken(str(result))
          break
        else:
          result.append(chr(c))

      elif state is _State.data_cref:
        if c == ord(";"):
          coded_entity = str(buffer)
          decoded_entity = html.unescape(coded_entity)
          if decoded_entity == coded_entity :
            result.extend(buffer)
          else:
            result.append(decoded_entity)
          state = _State.data
        elif c == EOF_MARKER:
          result.extend(buffer)
          state = _State.data
          continue
        else:
          buffer.append(chr(c))

      elif state is _State.tag:
        if c in (0x09, 0x0A, 0x0C, 0x20):
          state = _State.start_tag_annot
        elif c == ord("."):
          state = _State.start_tag_class
        elif c == ord("/"):
          state = _State.end_tag
        elif ord("0") <= c <= ord("9"):
          result = StringBuf(chr(c))
          state = _State.ts_tag
        elif c in (ord(">"), EOF_MARKER):
          if c == ord(">"):
            position += 1
          yield StringToken()
          break
        else:
          result = StringBuf(chr(c))
          state = _State.start_tag

      elif state is _State.start_tag:
        if c in (0x09, 0x0C, 0x20):
          state = _State.start_tag_annot
        elif c == 0x0A:
          buffer = StringBuf(chr(c))
          state = _State.start_tag_annot
        elif c is ord("."):
          state = _State.start_tag_class
        elif c in (ord(">"), EOF_MARKER):
          if c == ord(">"):
            position += 1
          yield StartTagToken(str(result))
          break
        else:
          result.append(chr(c))

      elif state is _State.start_tag_class:
        if c in (0x09, 0x0C, 0x20):
          classes.append(str(buffer))
          buffer = StringBuf()
          state = _State.start_tag_annot
        elif c == 0x0A:
          classes.append(str(buffer))
          buffer = StringBuf(chr(c))
          state = _State.start_tag_annot
        elif c is ord("."):
          classes.append(str(buffer))
          buffer = StringBuf()
        elif c in (EOF_MARKER, ord(">")):
          if c == ord(">"):
            position += 1
          classes.append(str(buffer))
          yield StartTagToken(str(result), classes)
          break
        else:
          buffer.append(chr(c))

      elif state is _State.start_tag_annot:

        if c == ord("&"):
          state = _State.annot_cref
          buffer = StringBuf("&")
        elif c in (ord(">"), EOF_MARKER):
          if c == ord(">"):
            position += 1
          annot = re.sub(r"\s+", " ", str(buffer).strip())
          yield StartTagToken(str(result), classes, annot)
          break
        else:
          buffer.append(chr(c))

      elif state is _State.annot_cref:
        if c == ord(";"):
          coded_entity = str(buffer)
          decoded_entity = html.unescape(coded_entity)
          if decoded_entity == coded_entity:
            result.extend(buffer)
          else:
            result.append(decoded_entity)
          state = _State.start_tag_annot
        elif c in (EOF_MARKER, ord(">")):
          result.extend(buffer)
          state = _State.start_tag_annot
          continue
        else:
          buffer.append(chr(c))

      elif state is _State.end_tag:
        if c in (ord(">"), EOF_MARKER):
          if c == ord(">"):
            position += 1
          yield EndTagToken(str(result))
          break
        result.append(chr(c))

      elif state is _State.ts_tag:
        if c in (ord(">"), EOF_MARKER):
          if c == ord(">"):
            position += 1
          yield TimestampTagToken(str(result))
          break
        result.append(chr(c))

      else:
        raise RuntimeError("Bad state")

      position += 1
