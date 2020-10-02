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

"""SCC Time Codes"""

from __future__ import annotations

import re
import typing
from fractions import Fraction
from math import floor, ceil

DEFAULT_DF_FRAME_RATE = Fraction(30000, 1001)  # default 29.97 fps
DEFAULT_NDF_FRAME_RATE = Fraction(30, 1)  # default 30 fps

SMPTE_TIME_CODE_NDF_PATTERN = ':'.join(['(?P<ndf_h>[0-9]{2})',
                                        '(?P<ndf_m>[0-9]{2})',
                                        '(?P<ndf_s>[0-9]{2})',
                                        '(?P<ndf_f>[0-9]{2})'])

SMPTE_TIME_CODE_DF_PATTERN = '(:|;|.)'.join(['(?P<df_h>[0-9]{2})',
                                             '(?P<df_m>[0-9]{2})',
                                             '(?P<df_s>[0-9]{2})',
                                             '(?P<df_f>[0-9]{2})'])


class SccTimeCode:
  """SCC SMPTE time code definition"""

  def __init__(self, hours: int, minutes: int, seconds: int, frames: int, drop_frame=False):
    self._hours = hours
    self._minutes = minutes
    self._seconds = seconds
    self._frames = frames
    self._drop_frame = drop_frame

  @staticmethod
  def parse(time_code: str) -> SccTimeCode:
    """Reads the time code string and converts to a SccTimeCode instance"""
    non_drop_frame_tc_regex = re.compile(SMPTE_TIME_CODE_NDF_PATTERN)
    match = non_drop_frame_tc_regex.match(time_code)

    if match:
      return SccTimeCode(int(match.group('ndf_h')),
                         int(match.group('ndf_m')),
                         int(match.group('ndf_s')),
                         int(match.group('ndf_f')))

    drop_frame_tc_regex = re.compile(SMPTE_TIME_CODE_DF_PATTERN)
    match = drop_frame_tc_regex.match(time_code)

    return SccTimeCode(int(match.group('df_h')),
                       int(match.group('df_m')),
                       int(match.group('df_s')),
                       int(match.group('df_f')),
                       True)

  @staticmethod
  def _from_frames(nb_frames: int, frame_rate: typing.Optional[Fraction] = None, drop_frame=False) -> (int, int, int, int, bool):
    frame_rate = frame_rate if frame_rate else DEFAULT_DF_FRAME_RATE if drop_frame else DEFAULT_NDF_FRAME_RATE

    h = floor(nb_frames / (60 * 60 * frame_rate))
    m = floor(nb_frames / (60 * frame_rate)) % 60
    s = floor(nb_frames / frame_rate) % 60
    f = ceil(nb_frames % frame_rate)

    return h, m, s, f, drop_frame

  @staticmethod
  def from_frames(nb_frames: int, frame_rate: typing.Optional[Fraction] = None, drop_frame=False) -> SccTimeCode:
    (h, m, s, f, drop_frame) = SccTimeCode._from_frames(nb_frames, frame_rate, drop_frame)
    return SccTimeCode(h, m, s, f, drop_frame)

  def get_hours(self) -> int:
    """Returns time code hours"""
    return self._hours

  def get_minutes(self) -> int:
    """Returns time code minutes"""
    return self._minutes

  def get_seconds(self) -> int:
    """Returns time code seconds"""
    return self._seconds

  def get_frames(self) -> int:
    """Returns time code frames"""
    return self._frames

  def add_frames(self, nb_frames=1):
    frames = self._get_frames() + nb_frames
    (h, m, s, f, _drop_frame) = SccTimeCode._from_frames(frames, drop_frame=self._drop_frame)
    self._hours = h
    self._minutes = m
    self._seconds = s
    self._frames = f

  def is_drop_frame(self) -> bool:
    """Returns whether the time code is drop-frame or not"""
    return self._drop_frame

  def _get_frames(self, frame_rate: typing.Optional[Fraction] = None) -> int:
    frame_rate = self._get_frame_rate(frame_rate)
    return (self._hours * 3600 + self._minutes * 60 + self._seconds) * frame_rate + self._frames

  def _get_frame_rate(self, frame_rate: typing.Optional[Fraction] = None) -> Fraction:
    if frame_rate:
      return frame_rate

    if self.is_drop_frame():
      return DEFAULT_DF_FRAME_RATE

    return DEFAULT_NDF_FRAME_RATE

  def get_fraction(self, frame_rate: typing.Optional[Fraction] = None) -> Fraction:
    """Converts the time code in a second-based fraction"""

    # Do not consider drop frame in the conversion
    base_frame_rate = frame_rate if frame_rate else DEFAULT_NDF_FRAME_RATE

    return Fraction(self._get_frames(frame_rate), base_frame_rate)

  def __repr__(self):
    if self.is_drop_frame():
      return ":".join(f'{item:02}' for item in [self._hours, self._minutes, self._seconds]) + ";" + f'{self._frames:02}'
    return ":".join(f'{item:02}' for item in [self._hours, self._minutes, self._seconds, self._frames])
