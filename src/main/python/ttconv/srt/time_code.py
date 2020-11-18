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

"""SRT Time Code"""

from __future__ import annotations

from fractions import Fraction
from math import floor
from typing import Union


class SrtTimeCode:
  """SRT time code definition"""

  def __init__(self, hours, minutes, seconds, milliseconds=0):
    self._hours: int = hours
    self._minutes: int = minutes
    self._seconds: int = seconds
    self._milliseconds: int = milliseconds

  @staticmethod
  def from_time_offset(seconds: Union[float, Fraction]) -> SrtTimeCode:
    """Creates SRT time code from time offset in seconds"""
    time_offset = float(seconds)

    h = floor(time_offset / 3600 % 24)
    m = floor(time_offset / 60 % 60)
    s = floor(time_offset % 60)
    ms = int((time_offset % 1) * 1000)

    return SrtTimeCode(h, m, s, ms)

  def to_seconds(self) -> float:
    return self._hours * 3600.0 + self._minutes * 60.0 + self._seconds + self._milliseconds / 1000.0

  def __repr__(self) -> str:
    return ":".join(f'{item:02}' for item in [self._hours, self._minutes, self._seconds]) + "," + f'{self._milliseconds:03}'
