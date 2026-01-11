#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) Sandflow Consulting LLC
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

'''Common utilities'''

import re
import typing
from fractions import Fraction
import ttconv.style_properties as styles

_HEX_COLOR_RE = re.compile(r"#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})?")
_DEC_COLOR_RE = re.compile(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")
_DEC_COLORA_RE = re.compile(r"rgba\(\s*(\d+),\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")

def parse_color(attr_value: str) -> styles.ColorType:
  '''Parses the TTML \\<color\\> value contained in `attr_value`
  '''

  lower_attr_value = str.lower(attr_value)

  if lower_attr_value in styles.NamedColors.__members__:

    return styles.NamedColors[lower_attr_value].value

  m = _HEX_COLOR_RE.match(attr_value)

  if m:

    return styles.ColorType(
      (
        int(m.group(1), 16),
        int(m.group(2), 16),
        int(m.group(3), 16),
        int(m.group(4), 16) if m.group(4) else 255
      )
    )

  m = _DEC_COLOR_RE.match(attr_value)

  if m:

    return styles.ColorType(
      (
        int(m.group(1)),
        int(m.group(2)),
        int(m.group(3)),
        255
      )
    )

  m = _DEC_COLORA_RE.match(attr_value)

  if m:

    return styles.ColorType(
      (
        int(m.group(1)),
        int(m.group(2)),
        int(m.group(3)),
        int(m.group(4))
      )
    )

  raise ValueError("Bad Syntax")


class DisjointIntervals:
  """A set of disjoint intervals"""

  def __init__(self):
    self._intervals: typing.List[typing.Tuple[Fraction, typing.Optional[Fraction]]] = []

  @staticmethod
  def _bisect_left(a, x, lo=0, key=None):
    """Polyfill for bisect.bisect_left with key argument
    TODO: replace with standard library version when Python 3.10+ is minimum requirement
    """
    if lo < 0:
      raise ValueError('lo must be non-negative')
    
    hi = len(a)

    if key is None:
      key = lambda v: v
    
    while lo < hi:
      mid = (lo + hi) // 2
      v = key(a[mid])
      if v is not None and v < x:
        lo = mid + 1
      else:
        hi = mid
    return lo

  @staticmethod
  def _bisect_right(a, x, lo=0, key=None):
    """Polyfill for bisect.bisect_right with key argument
    TODO: replace with standard library version when Python 3.10+ is minimum requirement
    """
    if lo < 0:
      raise ValueError('lo must be non-negative')
    hi = len(a)

    if key is None:
      key = lambda v: v

    while lo < hi:
      mid = (lo + hi) // 2
      v = key(a[mid])
      if v is None or x < v:
        hi = mid
      else:
        lo = mid + 1

    return lo

  @staticmethod
  def _within_interval(x: Fraction, interval: typing.Tuple[Fraction, typing.Optional[Fraction]]) -> bool:
    start, end = interval
    return (x >= start) and (end is None or x < end)

  def add(self, start: Fraction, end: typing.Optional[Fraction]):
    """Adds an interval to the set, merging overlapping intervals"""

    if start is None:
      raise ValueError("Interval start must be specified")

    if end is not None and start >= end:
      raise ValueError("Interval start must be strictly less than end")
    
    if len(self._intervals) == 0:
      self._intervals.append((start, end))
      return

    # look for lower bound
    # find the first interval that ends at or after the new interval starts
    low = DisjointIntervals._bisect_left(self._intervals, start, key=lambda x: x[1])

    if low < len(self._intervals):
      # if such an interval exists, the new start is the minimum of the new start and the start of that interval
      start = min(start, self._intervals[low][0])

    # look for upper bound
    if end is None:
      hi = len(self._intervals)
    else:
      # find the first interval that starts after the new interval ends
      hi = DisjointIntervals._bisect_right(self._intervals, end, lo=low, key=lambda x: x[0])

    if hi > low:
      # if such an interval exists, the new end is the maximum of the new end and the end of the last merged interval
      last_end = self._intervals[hi - 1][1]
      if last_end is None or (end is not None and last_end > end):
        end = last_end

    # replace the range of overlapping intervals with the merged interval
    self._intervals[low : hi] = [(start, end)]

  def contains(self, x: Fraction) -> bool:
    """Returns whether the point is contained in one of the intervals"""
    if len(self._intervals) == 0:
      idx = 0
    if len(self._intervals) == 1:
      idx = 1
    else:
      idx = DisjointIntervals._bisect_right(self._intervals, x, key=lambda i: i[0])

    return idx > 0 and DisjointIntervals._within_interval(x, self._intervals[idx - 1])

  def __len__(self):
    return len(self._intervals)

  def __iter__(self):
    return iter(self._intervals)
