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

'''IMSC style properties'''

import re
import typing
from fractions import Fraction
import ttconv.style_properties as styles


_HEX_COLOR_RE = re.compile(r"#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})?")
_DEC_COLOR_RE = re.compile(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")
_DEC_COLORA_RE = re.compile(r"rgba\(\s*(\d+),\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")

_LENGTH_RE = re.compile(r"^((?:\+|\-)?\d*(?:\.\d+)?)(px|em|c|%|rh|rw)$")

_FAMILIES_SEPARATOR = re.compile(r"(?<=[^\\]),")
_FAMILIES_ESCAPED_CHAR = re.compile(r"\\(.)")

_CLOCK_TIME_FRACTION_RE = re.compile(r"^(\d{2,}):(\d\d):(\d\d(?:\.\d+)?)$")
_CLOCK_TIME_FRAMES_RE = re.compile(r"^(\d{2,}):(\d\d):(\d\d):(\d{2,})$")
_OFFSET_FRAME_RE = re.compile(r"^(\d+(?:\.\d+)?)f")
_OFFSET_TICK_RE = re.compile(r"^(\d+(?:\.\d+)?)t$")
_OFFSET_MS_RE = re.compile(r"^(\d+(?:\.\d+)?)ms$")
_OFFSET_S_RE = re.compile(r"^(\d+(?:\.\d+)?)s$")
_OFFSET_H_RE = re.compile(r"^(\d+(?:\.\d+)?)h$")
_OFFSET_M_RE = re.compile(r"^(\d+(?:\.\d+)?)m$")


def parse_color(attr_value: str) -> styles.ColorType:
  '''Parses the TTML \\<color\\> value contained in `attr_value`
  '''

  lower_attr_value = str.lower(attr_value)

  if lower_attr_value in styles.NamedColors.__members__:

    return styles.NamedColors[lower_attr_value].value

  m = _HEX_COLOR_RE.match(attr_value)

  if m:

    return styles.ColorType(
      [
        int(m.group(1), 16),
        int(m.group(2), 16),
        int(m.group(3), 16),
        int(m.group(4), 16) if m.group(4) else 255
      ]
    )

  m = _DEC_COLOR_RE.match(attr_value)

  if m:

    return styles.ColorType(
      [
        int(m.group(1)),
        int(m.group(2)),
        int(m.group(3)),
        255
      ]
    )
    
  m = _DEC_COLORA_RE.match(attr_value)

  if m:

    return styles.ColorType(
      [
        int(m.group(1)),
        int(m.group(2)),
        int(m.group(3)),
        int(m.group(4))
      ]
    )

  raise ValueError("Bad Syntax")


def parse_length(attr_value: str) -> typing.Tuple[float, str]:
  '''Parses the TTML length in `attr_value` into a (length, units) tuple'''

  m = _LENGTH_RE.match(attr_value)

  if m:

    return (float(m.group(1)), m.group(2))

  raise ValueError("Bad length syntax")


def parse_font_families(attr_value: str) -> typing.List[str]:
  '''Parses th TTML \\<font-family\\> value in `attr_value` into a list of font families'''

  rslt = []

  for family in map(str.strip, _FAMILIES_SEPARATOR.split(attr_value)):

    unquoted_family = family[1:-1] if family[0] == "'" or family[0] == '"' else family

    rslt.append(_FAMILIES_ESCAPED_CHAR.sub(r"\1", unquoted_family))

  if len(rslt) == 0:
    raise ValueError("Bad syntax")

  return rslt


def parse_time_expression(tick_rate: int, frame_rate: Fraction, time_expr: str) -> Fraction:
  '''Parse a TTML time expression in a fractional number in seconds
  '''

  m = _OFFSET_FRAME_RE.match(time_expr)

  if m and frame_rate:
    return Fraction(m.group(1)) / frame_rate

  m = _OFFSET_TICK_RE.match(time_expr)

  if m and tick_rate:
    return Fraction(m.group(1)) / tick_rate

  m = _OFFSET_MS_RE.match(time_expr)

  if m:
    return Fraction(m.group(1)) / 1000

  m = _OFFSET_S_RE.match(time_expr)

  if m:
    return Fraction(m.group(1))

  m = _OFFSET_M_RE.match(time_expr)

  if m:
    return Fraction(m.group(1)) * 60

  m = _OFFSET_H_RE.match(time_expr)

  if m:
    return Fraction(m.group(1)) * 3600

  m = _CLOCK_TIME_FRACTION_RE.match(time_expr)

  if m:
    return Fraction(m.group(1)) * 3600 + \
            Fraction(m.group(2)) * 60 + \
            Fraction(m.group(3))
  
  m = _CLOCK_TIME_FRAMES_RE.match(time_expr)

  if m and frame_rate:
    frames = Fraction(m.group(4)) if m.group(4) else 0

    if frames >= frame_rate:
      raise ValueError("Frame cound exceeds frame rate")

    return Fraction(m.group(1)) * 3600 + \
            Fraction(m.group(2)) * 60 + \
            Fraction(m.group(3)) + \
            frames / frame_rate

  raise ValueError("Syntax error")
