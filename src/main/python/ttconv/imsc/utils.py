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

import logging
import re
import typing
import ttconv.style_properties as styles

LOGGER = logging.getLogger(__name__)

_LENGTH_RE = re.compile(r"^((?:\+|\-)?\d*(?:\.\d+)?)(px|em|c|%|rh|rw)$")

def parse_length(attr_value: str) -> typing.Tuple[float, str]:
  '''Parses the TTML length in `attr_value` into a (length, units) tuple'''

  m = _LENGTH_RE.match(attr_value)

  if m:

    return (float(m.group(1)), m.group(2))

  raise ValueError("Bad length syntax")


_FAMILIES_ESCAPED_CHAR = re.compile(r"\\(.)")
_SINGLE_QUOTE_PATTERN = "(?:'(?P<single_quote>(.+?)(?<!\\\\))')"
_DOUBLE_QUOTE_PATTERN = "(?:\"(?P<double_quote>(.+?)(?<!\\\\))\")"
_NO_QUOTE_PATTERN = "(?P<no_quote>(?:\\\\.|[^'\", ])(?:\\\\.|[^'\",])+)"

_FONT_FAMILY_PATTERN = re.compile(
  "|".join(
    (
      _SINGLE_QUOTE_PATTERN,
      _DOUBLE_QUOTE_PATTERN,
      _NO_QUOTE_PATTERN
    )
  )
)

def parse_font_families(attr_value: str) -> typing.List[str]:
  '''Parses th TTML \\<font-family\\> value in `attr_value` into a list of font families'''

  rslt = []

  for m in _FONT_FAMILY_PATTERN.finditer(attr_value):

    is_quoted = m.lastgroup in ("single_quote", "double_quote")

    escaped_family = _FAMILIES_ESCAPED_CHAR.sub(r"\1", m.group(m.lastgroup))

    if not is_quoted and escaped_family in styles.GenericFontFamilyType.__members__:
      rslt.append(styles.GenericFontFamilyType(escaped_family))
    else:
      rslt.append(escaped_family)
    

  if len(rslt) == 0:
    raise ValueError("Bad syntax")

  return rslt

def serialize_font_family(font_family: typing.Tuple[typing.Union[str, styles.GenericFontFamilyType], ...]):
  '''Serialize model FontFamily to tts:fontFamily
  '''

  def _serialize_one_family(family):
    if isinstance(family, styles.GenericFontFamilyType):
      return family.value
    
    return '"' + family.replace('"', r'\"') + '"'

  return ", ".join(map(_serialize_one_family, font_family))

def parse_position(attr_value: str) -> typing.Tuple[str, styles.LengthType, str, styles.LengthType]:
  '''Parse a TTML \\<position\\> value into offsets from a horizontal and vertical edge
  '''

  length_50pct = styles.LengthType(value=50, units=styles.LengthType.Units.pct)
  length_0pct = styles.LengthType(value=0, units=styles.LengthType.Units.pct)

  h_edges = {"left", "right"}
  v_edges = {"top", "bottom"}

  h_edge: typing.Optional[str] = None
  h_offset: typing.Optional[styles.LengthType] = None
  v_edge: typing.Optional[str] = None
  v_offset: typing.Optional[styles.LengthType] = None

  items = attr_value.split()

  if len(items) in (1, 2):

    # begin processing 1 and 2 components

    while len(items) > 0:

      cur_item = items.pop(0)

      if cur_item in h_edges:

        h_edge = cur_item
        h_offset = length_0pct

      elif cur_item in v_edges:

        v_edge = cur_item
        v_offset = length_0pct

      elif cur_item == "center":

        if h_edge is None:

          h_edge = "left"
          h_offset = length_50pct

        elif v_edge is None:

          v_edge = "top"
          v_offset = length_50pct

      else:

        (value, units) = parse_length(cur_item)

        if h_edge is None:

          h_edge = "left"
          h_offset = styles.LengthType(value, styles.LengthType.Units(units))

        elif v_edge is None:

          v_edge = "top"
          v_offset = styles.LengthType(value, styles.LengthType.Units(units))
    
    # end processing 1 and 2 components

  else:

    # begin processing 3 and 4 components

    while len(items) > 0:

      cur_item = items.pop(0)

      if cur_item in h_edges:

        h_edge = cur_item

        if v_edge is not None and v_offset is None:
          v_offset = length_0pct

      elif cur_item in v_edges:

        v_edge = cur_item

        if h_edge is not None and h_offset is None:
          h_offset = length_0pct

      elif cur_item == "center":

        pass

      else:

        (value, units) = parse_length(cur_item)

        if h_edge is not None and h_offset is None:

          h_offset = styles.LengthType(value, styles.LengthType.Units(units))

        if v_edge is not None and v_offset is None:

          v_offset = styles.LengthType(value, styles.LengthType.Units(units))
    
    # end processing 3 and 4 components

  # fill-in missing components, if any

  if h_offset is None:

    if h_edge is None:
      h_edge = "left"
      h_offset = length_50pct
    else:
      h_offset = length_0pct

  if v_offset is None:

    if v_edge is None:
      v_edge = "top"
      v_offset = length_50pct
    else:
      v_offset = length_0pct


  return (h_edge, h_offset, v_edge, v_offset)
  