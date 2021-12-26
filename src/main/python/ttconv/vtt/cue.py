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

"""WebVTT paragraph"""

from enum import Enum
import re
from fractions import Fraction
from typing import Optional, Union

from ttconv.time_code import ClockTime


class VttCue:
  """VTT cue class"""

  class LineAlignment(Enum):
    """WebVTT line alignment cue setting"""
    start = "start"
    center = "center"
    end = "end"

  _EOL_SEQ_RE = re.compile(r"\n{2,}")

  def __init__(self, identifier: int):
    self._id: int = identifier
    self._begin: Optional[ClockTime] = None
    self._end: Optional[ClockTime] = None
    self._text: str = ""
    self._line: int = None
    self._align: VttCue.LineAlignment = None

  def set_begin(self, offset: Fraction):
    """Sets the paragraph begin time code"""
    self._begin = ClockTime.from_seconds(offset)
    self._begin.set_separator(".")

  def get_begin(self) -> Optional[ClockTime]:
    """Returns the paragraph begin time code"""
    return self._begin

  def set_end(self, offset: Optional[Union[Fraction, float]]):
    """Sets the paragraph end time code"""
    if offset is not None:
      self._end = ClockTime.from_seconds(offset)
      self._end.set_separator(".")
    else:
      self._end = None

  def get_end(self) -> Optional[ClockTime]:
    """Returns the paragraph end time code"""
    return self._end

  def set_line(self, line: int):
    """Sets the WebVTT line cue setting (in whole percent)"""
    self._line = line

  def get_line(self) -> Optional[int]:
    """Return the WebVTT line cue setting (in whole percent)"""
    return self._line

  def set_align(self, align: LineAlignment):
    """Sets the WebVTT line alignment cue setting"""
    self._align = align

  def get_align(self) -> Optional[LineAlignment]:
    """Return the WebVTT line alignment cue setting"""
    return self._align

  def is_only_whitespace_or_empty(self):
    """Returns whether the paragraph text contains only whitespace or is empty"""
    return len(self._text) == 0 or self._text.isspace()

  def normalize_eol(self):
    """Remove line breaks at the beginning and end of the paragraph, and replace
    line break sequences with a single line break"""
    self._text = VttCue._EOL_SEQ_RE.sub("\n", self._text).strip("\n\r")

  def append_text(self, text: str):
    """Appends text to the paragraph"""
    self._text += text

  def to_string(self) -> str:
    """Returns the VTT paragraph as a formatted string"""
    if self._begin is None:
      raise ValueError("VTT paragraph begin time code must be set.")

    if self._end is None:
      raise ValueError("VTT paragraph end time code must be set.")

    if self._end.to_seconds() <= self._begin.to_seconds():
      raise ValueError("VTT paragraph end time code must be greater than the begin time code.")

    return str(self)

  def __str__(self) -> str:

    # cue identifier
    t = f"{self._id}\n"
    
    # cue timing
    t += f"{self._begin} --> {self._end}"

    # cue line position
    if self._line is not None:
      t += f" line:{self._line}%"

      if self._align is not None:
        t += f",{self._align.value}"

    t += "\n"

    # cue body
    if self._text:
      t += self._text + "\n"

    return t
