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

"""SRT paragraph"""

from fractions import Fraction
from typing import Optional, Union

from ttconv.srt.time_code import SrtTimeCode


class SrtParagraph:
  """SRT paragraph definition class"""

  def __init__(self, identifier: int):
    self._id: int = identifier
    self._begin: Optional[SrtTimeCode] = None
    self._end: Optional[SrtTimeCode] = None
    self._text: str = ""

  def set_begin(self, offset: Fraction):
    """Sets the paragraph begin time code"""
    self._begin = SrtTimeCode.from_time_offset(offset)

  def get_begin(self) -> Optional[SrtTimeCode]:
    """Returns the paragraph begin time code"""
    return self._begin

  def set_end(self, offset: Union[Fraction, float]):
    """Sets the paragraph end time code"""
    self._end = SrtTimeCode.from_time_offset(offset)

  def get_end(self) -> Optional[SrtTimeCode]:
    """Returns the paragraph end time code"""
    return self._end

  def is_only_whitespace(self):
    """Returns whether the paragraph tex contains only whitespace"""
    return self._text.isspace()

  def append_text(self, text: str):
    """Appends text to the paragraph"""
    self._text += text

  def to_string(self) -> str:
    """Returns the SRT paragraph as a formatted string"""
    if self._begin is None:
      raise ValueError("SRT paragraph begin time code must be set.")

    if self._end is None:
      raise ValueError("SRT paragraph end time code must be set.")

    if self._end.to_seconds() <= self._begin.to_seconds():
      raise ValueError("SRT paragraph end time code must be greater than the begin time code.")

    return str(self)

  def __str__(self) -> str:
    return "\n".join((str(self._id), str(self._begin) + " --> " + str(self._end), str(self._text))) \
           + ("\n" if self._text else "")
