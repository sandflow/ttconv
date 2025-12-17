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

"""Time Code"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from fractions import Fraction
from math import floor, ceil
from typing import Optional, Union


class _HHMMSSTimeExpression(ABC):
  """Time code basic definition"""

  def __init__(self, hours: int, minutes: int, seconds: int):
    self._hours = hours
    self._minutes = minutes
    self._seconds = seconds

  def get_hours(self) -> int:
    """Returns time code hours"""
    return self._hours

  def get_minutes(self) -> int:
    """Returns time code minutes"""
    return self._minutes

  def get_seconds(self) -> int:
    """Returns time code seconds"""
    return self._seconds

class ClockTime(_HHMMSSTimeExpression):
  """Millisecond-based time code definition"""

  TIME_CODE_PATTERN = ':'.join(['(?P<h>[0-9]{2,})',
                                '(?P<m>[0-9]{2})',
                                '(?P<s>[0-9]{2})']) + \
                      '(.|,)' + '(?P<ms>[0-9]{2,3})'

  def __init__(self, hours: int, minutes: int, seconds: int, milliseconds: int):
    super().__init__(hours, minutes, seconds)
    self._milliseconds = milliseconds
    self._ms_separator = "."

  def get_milliseconds(self) -> int:
    """Returns time code milliseconds"""
    return self._milliseconds

  def to_seconds(self) -> Fraction:
    """Converts current time code to seconds"""
    return self.get_hours() * 3600 + \
           self.get_minutes() * 60 + \
           self.get_seconds() + \
           Fraction(self._milliseconds, 1000)

  @staticmethod
  def parse(time_code: str) -> ClockTime:
    """Reads the time code string and converts to a ClockTime instance"""
    tc_regex = re.compile(ClockTime.TIME_CODE_PATTERN)
    match = tc_regex.match(time_code)

    if match is not None:
      return ClockTime(int(match.group('h')),
                       int(match.group('m')),
                       int(match.group('s')),
                       int(match.group('ms')))

    raise ValueError("Invalid time code format")

  @staticmethod
  def from_seconds(seconds: Union[float, Fraction]) -> ClockTime:
    """Creates a time code from time offset in seconds (rounds to the closest millisecond)"""

    if seconds < 0:
      raise ValueError("Seconds must not be less than zero")

    seconds = round(seconds, 3)

    h = floor(seconds / 3600)
    m = floor(seconds / 60 % 60)
    s = floor(seconds % 60)
    ms = round((seconds % 1) * 1000)

    return ClockTime(h, m, s, ms)

  def set_separator(self, separator: str):
    """Sets separator character before the millisecond digits into the literal representation of this time code"""
    self._ms_separator = separator

  def __str__(self):
    return ":".join(f'{item:02d}' for item in [self._hours, self._minutes, self._seconds]) \
           + self._ms_separator + f'{self._milliseconds:03}'

  def __eq__(self, other: ClockTime):
    if not isinstance(other, ClockTime):
      return False
    return self._hours == other.get_hours() and \
           self._minutes == other.get_minutes() and \
           self._seconds == other.get_seconds() and \
           self._milliseconds == other.get_milliseconds()


FPS_23_98 = Fraction(24000, 1001)
FPS_24 = Fraction(24, 1)
FPS_25 = Fraction(25, 1)
FPS_29_97 = Fraction(30000, 1001)
FPS_30 = Fraction(30, 1)
FPS_50 = Fraction(50, 1)
FPS_59_94 = Fraction(60000, 1001)
FPS_60 = Fraction(60, 1)


class SmpteTimeCode(_HHMMSSTimeExpression):
  """Frame-based time code definition"""

  _NDF_TC_PATTERN = ':'.join(['(?P<ndf_h>[0-9]{2})',
                                          '(?P<ndf_m>[0-9]{2})',
                                          '(?P<ndf_s>[0-9]{2})',
                                          '(?P<ndf_f>[0-9]{2})'])
  
  _NDF_TC_RE = re.compile(_NDF_TC_PATTERN)

  _DF_TC_PATTERN = '(:|;|.|,)'.join(['(?P<df_h>[0-9]{2})',
                                                 '(?P<df_m>[0-9]{2})',
                                                 '(?P<df_s>[0-9]{2})',
                                                 '(?P<df_f>[0-9]{2})'])
  
  DF_TC_RE = re.compile(_DF_TC_PATTERN)

  def __init__(self, hours: int, minutes: int, seconds: int, frames: int, frame_rate: Fraction, is_df: Optional[bool] = None):
    super().__init__(hours, minutes, seconds)
    self._frames: int = frames
    self._frame_rate: Fraction = frame_rate

    if is_df is None:
       self._is_drop_frame = frame_rate.denominator == 1001
    else:
      if is_df and frame_rate.denominator != 1001:
        raise ValueError("The numerator of the frame rate of a drop frame timecode must be 1001")
      self._is_drop_frame: bool = is_df

  def get_frames(self) -> int:
    """Returns time code frames"""
    return self._frames

  def get_frame_rate(self) -> Fraction:
    """Returns time code frame rate"""
    return self._frame_rate

  def to_frames(self) -> int:
    """Converts current time code into a number of frames"""
    dropped_frames = 0

    fps = ceil(self._frame_rate)

    if self.is_drop_frame():
      drop_frames_per_minute = round(60 * (fps - self._frame_rate))  # 2 at 29.97 fps

      nb_of_minute_tens = self._hours * 6 + floor(self._minutes / 10)
      nb_of_drop_frames_in_tens = drop_frames_per_minute * 9 * nb_of_minute_tens
      remaining_minutes = self._minutes % 10
      nb_of_drop_frames_in_remaining = drop_frames_per_minute * remaining_minutes

      dropped_frames = nb_of_drop_frames_in_tens + nb_of_drop_frames_in_remaining

    whole_seconds = self.get_hours() * 3600 + \
        self.get_minutes() * 60 + \
        self.get_seconds()
    
    return int(whole_seconds * fps) + self._frames - dropped_frames

  def to_seconds(self) -> Fraction:
    """Converts current time code into seconds"""
    return self.to_frames() / self._frame_rate

  def to_temporal_offset(self) -> Fraction:
    """Converts current time code into a second-based fraction"""
    nb_frames = self.to_frames()
    return Fraction(nb_frames, self._frame_rate)

  def is_drop_frame(self) -> bool:
    """Returns whether the time code is drop-frame or not"""
    return self._is_drop_frame

  def add_frames(self, nb_frames=1):
    """Add frames to the current time code"""
    frames = self.to_frames() + nb_frames

    new_time_code = SmpteTimeCode.from_frames(frames, self._frame_rate)

    self._hours = new_time_code.get_hours()
    self._minutes = new_time_code.get_minutes()
    self._seconds = new_time_code.get_seconds()
    self._frames = new_time_code.get_frames()

  @staticmethod
  def parse(time_code: str, frame_rate: Fraction) -> SmpteTimeCode:
    """Reads the time code string and converts to a SmpteTimeCode instance"""
    
    match = SmpteTimeCode._NDF_TC_RE.match(time_code)

    if match is not None:
      # NDF timecode
      return SmpteTimeCode(int(match.group('ndf_h')),
                           int(match.group('ndf_m')),
                           int(match.group('ndf_s')),
                           int(match.group('ndf_f')),
                           frame_rate,
                           False)

    if frame_rate.denominator != 1001:
      frame_rate = frame_rate * Fraction(1000, 1001)

    match = SmpteTimeCode.DF_TC_RE.match(time_code)

    if match is not None:
      return SmpteTimeCode(int(match.group('df_h')),
                           int(match.group('df_m')),
                           int(match.group('df_s')),
                           int(match.group('df_f')),
                           frame_rate,
                           True)

    raise ValueError("Invalid time code format")

  @staticmethod
  def from_frames(nb_frames: Union[int, Fraction], frame_rate: Fraction, is_df: Optional[bool] = None) -> SmpteTimeCode:
    """Creates a time code from a number of frames and a frame rate"""
    if frame_rate is None:
      raise ValueError("Cannot compute time code from frames without frame rate")

    if nb_frames is None or nb_frames < 0:
      raise ValueError("Number of frames must not None and must not be less than zero")

    if is_df is None:
       drop_frame: bool = frame_rate.denominator == 1001
    else:
      if is_df and frame_rate.denominator != 1001:
        raise ValueError("The numerator of the frame rate of a drop frame timecode must be 1001")
      drop_frame: bool = is_df

    fps = ceil(frame_rate)

    if drop_frame:
      # add two dropped frames every minute, but not when the minute count is divisible by 10

      nb_frames_in_one_minute = 60 * frame_rate  # 1798 at 29.97 fps
      nb_frames_in_ten_minutes = round(10 * nb_frames_in_one_minute)  # 17982 at 29.97 fps
      drop_frames_per_minute = round(60 * (fps - frame_rate))  # 2 at 29.97 fps

      nb_of_minute_tens = floor(nb_frames / nb_frames_in_ten_minutes)
      nb_of_remaining_frames = round(nb_frames % nb_frames_in_ten_minutes)

      nb_of_drop_frames_in_tens = drop_frames_per_minute * 9 * nb_of_minute_tens

      nb_of_remaining_minutes = floor((nb_of_remaining_frames - drop_frames_per_minute) / round(nb_frames_in_one_minute))

      if nb_of_remaining_minutes < 0:
        nb_of_remaining_minutes = 0

      nb_of_drop_frames_in_minutes = nb_of_remaining_minutes * drop_frames_per_minute

      nb_frames += nb_of_drop_frames_in_tens + nb_of_drop_frames_in_minutes

    h = floor(nb_frames / (60 * 60 * fps))
    m = floor(nb_frames / (60 * fps)) % 60
    s = floor(nb_frames / fps) % 60
    f = ceil(nb_frames % fps)

    return SmpteTimeCode(h, m, s, f, frame_rate, drop_frame)

  @staticmethod
  def from_seconds(seconds: Union[float, Fraction], frame_rate: Fraction) -> SmpteTimeCode:
    """Creates a time code from time offset in seconds and a frame rate"""
    if frame_rate is None:
      raise ValueError("Cannot compute SMPTE time code from seconds without frame rate")

    return SmpteTimeCode.from_frames(int(seconds * frame_rate), frame_rate)

  def __str__(self):
    if self.is_drop_frame():
      return ":".join(f'{item:02}' for item in [self._hours, self._minutes, self._seconds]) + ";" + f'{self._frames:02}'
    return ":".join(f'{item:02}' for item in [self._hours, self._minutes, self._seconds, self._frames])

  def __repr__(self):
    return f"{self} at {float(self._frame_rate)} fps"

  def __eq__(self, other: SmpteTimeCode):
    if not isinstance(other, SmpteTimeCode):
      return False
    return self._hours == other.get_hours() and \
           self._minutes == other.get_minutes() and \
           self._seconds == other.get_seconds() and \
           self._frames == other.get_frames() and \
           self._is_drop_frame == other.is_drop_frame()
