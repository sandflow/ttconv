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

"""SCC Codes"""

from enum import Enum
from typing import Tuple, Optional
from ttconv.style_properties import NamedColors

SCC_COLOR_MAPPING = {
  0x00: NamedColors.white.value,
  0x01: NamedColors.white.value,
  0x02: NamedColors.green.value,
  0x03: NamedColors.green.value,
  0x04: NamedColors.blue.value,
  0x05: NamedColors.blue.value,
  0x06: NamedColors.cyan.value,
  0x07: NamedColors.cyan.value,
  0x08: NamedColors.red.value,
  0x09: NamedColors.red.value,
  0x0A: NamedColors.yellow.value,
  0x0B: NamedColors.yellow.value,
  0x0C: NamedColors.magenta.value,
  0x0D: NamedColors.magenta.value
}

class SccChannel(Enum):
  """SCC Caption Channel"""
  CHANNEL_1 = 1
  CHANNEL_2 = 2

  def __str__(self):
    return "CC" + str(self.value)


class SccCode(Enum):
  """SCC codes base definition class"""

  def __init__(self, channel_1: int, channel_2: int):
    if channel_1 > 0xFFFF or channel_2 > 0xFFFF:
      raise ValueError("Expected 2-bytes values")

    self._channel_1 = channel_1
    self._channel_2 = channel_2

  def get_values(self) -> Tuple[int, int]:
    """Returns SCC Code values"""
    return self._channel_1, self._channel_2

  def get_channel(self, value: int) -> Optional[SccChannel]:
    """Returns caption channel corresponding to the specified code value"""
    if value == self._channel_1:
      return SccChannel.CHANNEL_1

    if value == self._channel_2:
      return SccChannel.CHANNEL_2

    return None

  def contains_value(self, value: int) -> bool:
    """Returns whether the specified value is contained into the SCC code channels values"""
    return value in self.get_values()
