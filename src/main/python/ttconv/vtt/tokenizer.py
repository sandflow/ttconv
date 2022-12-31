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

EOF_MARKER = -1

class StringBuf:
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
  pass

class StringToken(Token):
  def __init__(self, value: str = "") -> None:
    super().__init__()
    self.value = value

class StartTagToken(Token):
  def __init__(self, tag: str = "", classes: Optional[List[str]] = None, annotation: Optional[str] = None) -> None:
    super().__init__()
    self.tag = tag
    self.classes = classes
    self.annotation = annotation

class EndTagToken(Token):
  def __init__(self, tag: str = "") -> None:
    super().__init__()
    self.tag = tag

class TimestampTagToken(Token):
  def __init__(self, tag: str = "") -> None:
    super().__init__()
    self.tag = tag


class Tokenizer:
  class State(Enum):
    data = 1
    tag = 2
    data_cref = 3
    start_tag = 4
    start_tag_annot = 5
    start_tag_class = 6
    end_tag = 7
    ts_tag = 8
    annot_cref = 3

  def __init__(self, cue_text: str) -> None:
    self.cue_text: str = cue_text
    self.position: int = 0

  def next(self) -> Optional[Token]:
    if self.position >= len(self.cue_text):
      return None

    state: Tokenizer.State = Tokenizer.State.data
    result: StringBuf = StringBuf()
    classes: List[str] = []
    buffer: StringBuf = StringBuf()

    while True:
      c = ord(self.cue_text[self.position]) if self.position < len(self.cue_text) else EOF_MARKER

      if state is Tokenizer.State.data:

        if c == ord("&"):
          state = Tokenizer.State.data_cref
          buffer = StringBuf("&")
        elif c == ord("<"):
          if result.is_empty():
            state = Tokenizer.State.tag
          else:
            return StringToken(str(result))
        elif c == EOF_MARKER:
          return StringToken(str(result))
        else:
          result.append(chr(c))

      elif state is Tokenizer.State.data_cref:
        if c == ord(";"):
          coded_entity = str(buffer)
          decoded_entity = html.unescape(coded_entity)
          if decoded_entity == coded_entity :
            result.extend(buffer)
          else:
            result.append(decoded_entity)
          state = Tokenizer.State.data
        elif c == EOF_MARKER:
          result.extend(buffer)
          state = Tokenizer.State.data
          continue
        else:
          buffer.append(chr(c))

      elif state is Tokenizer.State.tag:
        if c in (0x09, 0x0A, 0x0C, 0x20):
          state = Tokenizer.State.start_tag_annot
        elif c == ord("."):
          state = Tokenizer.State.start_tag_class
        elif c == ord("/"):
          state = Tokenizer.State.end_tag
        elif ord("0") <= c <= ord("9"):
          state = Tokenizer.State.ts_tag
        elif c == ord(">"):
          self.position += 1
          return StringToken()
        elif c == EOF_MARKER:
          return StringToken()
        else:
          result = StringBuf(chr(c))
          state = Tokenizer.State.start_tag

      elif state is Tokenizer.State.start_tag:
        if c in (0x09, 0x0C, 0x20):
          state = Tokenizer.State.start_tag_annot
        elif c == 0x0A:
          buffer = StringBuf(chr(c))
          state = Tokenizer.State.start_tag_annot
        elif c is ord("."):
          state = Tokenizer.State.start_tag_class
        elif c == ord(">"):
          self.position += 1
          return StartTagToken(str(result))
        elif c == EOF_MARKER:
          return StartTagToken(str(result))
        else:
          result.append(chr(c))

      elif state is Tokenizer.State.start_tag_class:
        if c in (0x09, 0x0C, 0x20):
          classes.append(str(buffer))
          buffer = StringBuf()
          state = Tokenizer.State.start_tag_annot
        elif c == 0x0A:
          classes.append(str(buffer))
          buffer = StringBuf(chr(c))
          state = Tokenizer.State.start_tag_annot
        elif c is ord("."):
          classes.append(str(buffer))
          buffer = StringBuf()
        elif c == ord(">"):
          self.position += 1
          classes.append(str(buffer))
          return StartTagToken(str(result), classes)
        elif c == EOF_MARKER:
          classes.append(str(buffer))
          return StartTagToken(str(result), classes)
        else:
          buffer.append(chr(c))

      elif state is Tokenizer.State.start_tag_annot:

        if c == ord("&"):
          state = Tokenizer.State.annot_cref
          buffer = StringBuf("&")
        elif c in (ord(">"), EOF_MARKER):
          if c == ord(">"):
            self.position += 1
          annot = re.sub(r"\s+", " ", str(buffer).strip())
          return StartTagToken(str(result), classes, annot)
        else:
          buffer.append(chr(c))

      elif state is Tokenizer.State.annot_cref:
        if c == ord(";"):
          coded_entity = str(buffer)
          decoded_entity = html.unescape(coded_entity)
          if decoded_entity == coded_entity:
            result.extend(buffer)
          else:
            result.append(decoded_entity)
          state = Tokenizer.State.start_tag_annot
        elif c in (EOF_MARKER, ord(">")):
          result.extend(buffer)
          state = Tokenizer.State.start_tag_annot
          continue
        else:
          buffer.append(chr(c))

      elif state is Tokenizer.State.end_tag:
        if c in (ord(">"), EOF_MARKER):
          if c == ord(">"):
            self.position += 1
          return EndTagToken(str(result))

        result.append(chr(c))

      elif state is Tokenizer.State.ts_tag:
        if c in (ord(">"), EOF_MARKER):
          if c == ord(">"):
            self.position += 1
          return TimestampTagToken(str(result))

        result.append(chr(c))

      else:
        raise RuntimeError("Bad state")

      self.position += 1