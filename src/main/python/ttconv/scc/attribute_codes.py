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

"""SCC Background and Foreground Attribute Code"""

from enum import Enum
from typing import Optional

from ttconv.style_properties import ColorType, NamedColors, TextDecorationType


class SccAttributeCode:
  """SCC Attribute Codes definition"""
  def __init__(self, channel_1: int, channel_2: int, color: ColorType, background=True):
    self._channel_1 = channel_1
    self._channel_2 = channel_2
    self._color = color
    self._background = background

  def get_color(self) -> ColorType:
    """Returns the corresponding color"""
    return self._color

  def is_background(self) -> bool:
    """Returns whether the current code is a background or foreground code"""
    return self._background

  def get_text_decoration(self) -> Optional[TextDecorationType]:
    """Returns the corresponding text decoration"""
    if self is SccAttributeCodes.FAU:
      return TextDecorationType.underline.value
    return None

  def contains_value(self, value: int) -> bool:
    """Returns whether the specified value is contained into the Attribute Code channels values"""
    return value in [self._channel_1, self._channel_2]



class SccAttributeCodes(Enum):
  """Enumeration of the SCC Foreground and Background Attribute Codes"""
  BWO = SccAttributeCode(0x1020, 0x1820, ColorType((0xFF, 0xFF, 0xFF, 0xFF)))  # Background White, Opaque
  BWS = SccAttributeCode(0x1021, 0x1821, ColorType((0xFF, 0xFF, 0xFF, 0x88)))  # Background White, Semi-transparent
  BGO = SccAttributeCode(0x1022, 0x1822, ColorType((0x00, 0xFF, 0x00, 0xFF)))  # Background Green, Opaque
  BGS = SccAttributeCode(0x1023, 0x1823, ColorType((0x00, 0xFF, 0x00, 0x88)))  # Background Green, Semi-transparent
  BBO = SccAttributeCode(0x1024, 0x1824, ColorType((0x00, 0x00, 0xFF, 0xFF)))  # Background Blue, Opaque
  BBS = SccAttributeCode(0x1025, 0x1825, ColorType((0x00, 0x00, 0xFF, 0x88)))  # Background Blue, Semi-transparent
  BCO = SccAttributeCode(0x1026, 0x1826, ColorType((0x00, 0xFF, 0xFF, 0xFF)))  # Background Cyan, Opaque
  BCS = SccAttributeCode(0x1027, 0x1827, ColorType((0x00, 0xFF, 0xFF, 0x88)))  # Background Cyan, Semi-transparent
  BRO = SccAttributeCode(0x1028, 0x1828, ColorType((0xFF, 0x00, 0x00, 0xFF)))  # Background Red, Opaque
  BRS = SccAttributeCode(0x1029, 0x1829, ColorType((0xFF, 0x00, 0x00, 0x88)))  # Background Red, Semi-transparent
  BYO = SccAttributeCode(0x102A, 0x182A, ColorType((0xFF, 0xFF, 0x00, 0xFF)))  # Background Yellow, Opaque
  BYS = SccAttributeCode(0x102B, 0x182B, ColorType((0xFF, 0xFF, 0x00, 0x88)))  # Background Yellow, Semi-transparent
  BMO = SccAttributeCode(0x102C, 0x182C, ColorType((0xFF, 0x00, 0xFF, 0xFF)))  # Background Magenta, Opaque
  BMS = SccAttributeCode(0x102D, 0x182D, ColorType((0xFF, 0x00, 0xFF, 0x88)))  # Background Magenta, Semi-transparent
  BAO = SccAttributeCode(0x102E, 0x182E, ColorType((0x00, 0x00, 0x00, 0xFF)))  # Background Black, Opaque
  BAS = SccAttributeCode(0x102F, 0x182F, ColorType((0x00, 0x00, 0x00, 0x88)))  # Background Black, Semi-transparent
  BT = SccAttributeCode(0x172D, 0x1F2D, ColorType((0x00, 0x00, 0x00, 0x00)))  # Background Transparent
  FA = SccAttributeCode(0x172E, 0x1F2E, NamedColors.black.value, False)  # Foreground Black
  FAU = SccAttributeCode(0x172F, 0x1F2F, NamedColors.black.value, False)  # Foreground Black Underline

  @staticmethod
  def find(value: int) -> Optional[SccAttributeCode]:
    """Find the Attribute Code corresponding to the specified value"""
    for attribute_code in list(SccAttributeCodes):
      if attribute_code.value.contains_value(value):
        return attribute_code
    return None
