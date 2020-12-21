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

"""SCC Background and Foreground Attribute Codes"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from ttconv.scc.codes import SccCode
from ttconv.style_properties import ColorType, NamedColors, TextDecorationType


class SccAttributeCode(SccCode, Enum):
  """SCC Foreground and Background Attribute Codes definition"""
  BWO = (0x1020, 0x1820, ColorType((0xFF, 0xFF, 0xFF, 0xFF)))  # Background White, Opaque
  BWS = (0x1021, 0x1821, ColorType((0xFF, 0xFF, 0xFF, 0x88)))  # Background White, Semi-transparent
  BGO = (0x1022, 0x1822, ColorType((0x00, 0xFF, 0x00, 0xFF)))  # Background Green, Opaque
  BGS = (0x1023, 0x1823, ColorType((0x00, 0xFF, 0x00, 0x88)))  # Background Green, Semi-transparent
  BBO = (0x1024, 0x1824, ColorType((0x00, 0x00, 0xFF, 0xFF)))  # Background Blue, Opaque
  BBS = (0x1025, 0x1825, ColorType((0x00, 0x00, 0xFF, 0x88)))  # Background Blue, Semi-transparent
  BCO = (0x1026, 0x1826, ColorType((0x00, 0xFF, 0xFF, 0xFF)))  # Background Cyan, Opaque
  BCS = (0x1027, 0x1827, ColorType((0x00, 0xFF, 0xFF, 0x88)))  # Background Cyan, Semi-transparent
  BRO = (0x1028, 0x1828, ColorType((0xFF, 0x00, 0x00, 0xFF)))  # Background Red, Opaque
  BRS = (0x1029, 0x1829, ColorType((0xFF, 0x00, 0x00, 0x88)))  # Background Red, Semi-transparent
  BYO = (0x102A, 0x182A, ColorType((0xFF, 0xFF, 0x00, 0xFF)))  # Background Yellow, Opaque
  BYS = (0x102B, 0x182B, ColorType((0xFF, 0xFF, 0x00, 0x88)))  # Background Yellow, Semi-transparent
  BMO = (0x102C, 0x182C, ColorType((0xFF, 0x00, 0xFF, 0xFF)))  # Background Magenta, Opaque
  BMS = (0x102D, 0x182D, ColorType((0xFF, 0x00, 0xFF, 0x88)))  # Background Magenta, Semi-transparent
  BAO = (0x102E, 0x182E, ColorType((0x00, 0x00, 0x00, 0xFF)))  # Background Black, Opaque
  BAS = (0x102F, 0x182F, ColorType((0x00, 0x00, 0x00, 0x88)))  # Background Black, Semi-transparent
  BT = (0x172D, 0x1F2D, ColorType((0x00, 0x00, 0x00, 0x00)))  # Background Transparent
  FA = (0x172E, 0x1F2E, NamedColors.black.value, False)  # Foreground Black
  FAU = (0x172F, 0x1F2F, NamedColors.black.value, False)  # Foreground Black Underline

  def __init__(self, channel_1: int, channel_2: int, color: ColorType, background=True):
    super().__init__(channel_1, channel_2)
    self._color = color
    self._background = background

  def get_color(self) -> ColorType:
    """Returns the corresponding color"""
    return self._color

  def get_name(self) -> str:
    """Returns the Attribute Code name"""
    return self.name

  def is_background(self) -> bool:
    """Returns whether the current code is a background or foreground code"""
    return self._background

  def get_text_decoration(self) -> Optional[TextDecorationType]:
    """Returns the corresponding text decoration"""
    if self is SccAttributeCode.FAU:
      return TextDecorationType(underline=True)
    return None

  @staticmethod
  def find(value: int) -> Optional[SccAttributeCode]:
    """Find the Attribute Code corresponding to the specified value"""
    for attribute_code in list(SccAttributeCode):
      if attribute_code.contains_value(value):
        return attribute_code
    return None
