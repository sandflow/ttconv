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

"""STL configuration"""

from __future__ import annotations
import typing

from dataclasses import dataclass, field
import re

from ttconv.config import ModuleConfiguration
import ttconv.style_properties as styles
from ttconv.imsc import utils
from ttconv.time_code import SmpteTimeCode

_SMPTE_TIME_CODE_DF_PATTERN = re.compile(SmpteTimeCode.SMPTE_TIME_CODE_DF_PATTERN)
_SMPTE_TIME_CODE_NDF_PATTERN = re.compile(SmpteTimeCode.SMPTE_TIME_CODE_NDF_PATTERN)
_MNR_PATTERN = re.compile("^\\d+$")

def _decode_font_stack(value: typing.Optional[str]) -> \
  typing.Optional[typing.Tuple[typing.Union[str, styles.GenericFontFamilyType]]]:
  return value if value is None else tuple(utils.parse_font_families(value))

def _decode_start_tc(value: typing.Optional[str]) -> typing.Optional[str]:
  if value is None:
    return None
  
  if value.upper() == "TCP":
    return "TCP"

  if _SMPTE_TIME_CODE_DF_PATTERN.match(value) or _SMPTE_TIME_CODE_NDF_PATTERN.match(value):
    return value

  raise ValueError(f"Invalid start_tc '{value}' value. Expect: 'TCP' or 'HH:MM:SS:FF'.")

def _decode_max_row_count(value: typing.Optional[str]) -> typing.Optional[typing.Union[int, str]]:
  if value is None:
    return None
  
  if isinstance(value, str) and value.upper() == "MNR":
    return "MNR"

  if isinstance(value, int):
    return value

  raise ValueError(f"Invalid max_row_count '{value}' value. Expect: 'MNR' or integer.")

@dataclass
class STLReaderConfiguration(ModuleConfiguration):
  """STL reader configuration"""

  disable_fill_line_gap: bool = field(default=False, metadata={"decoder": bool})
  program_start_tc: typing.Optional[str] = field(default=None, metadata={"decoder": _decode_start_tc})
  disable_line_padding: bool = field(default=False, metadata={"decoder": bool})
  font_stack: typing.Optional[typing.Tuple[typing.Union[str, styles.GenericFontFamilyType]]] = \
                  field(default=None, metadata={"decoder": _decode_font_stack})
  max_row_count: typing.Optional[typing.Union[int, str]] = field(default=None, metadata={"decoder": _decode_max_row_count})

  @classmethod
  def name(cls):
    return "stl_reader"
