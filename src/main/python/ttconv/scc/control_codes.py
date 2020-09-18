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

"""SCC Control Codes"""
import typing
from enum import Enum


class SccControlCode(Enum):
  """SCC Control Code definition"""
  AOF = ("Reserved (formerly Alarm Off)", 0X1422, 0x1C22)
  AON = ("Reserved (formerly Alarm On)", 0X1423, 0x1C23)
  BS = ("Backspace", 0X1421, 0x1C21)
  CR = ("Carriage Return", 0X142D, 0x1C2D)
  DER = ("Delete to End of Row", 0X1424, 0x1C24)
  EDM = ("Erase Displayed Memory", 0X142C, 0x1C2C)
  ENM = ("Erase Non-Displayed Memory", 0X142E, 0x1C2E)
  EOC = ("End of Caption (Flip Memories)", 0X142F, 0x1C2F)
  FON = ("Flash On", 0X1428, 0x1C28)
  RDC = ("Resume Direct Captioning", 0X1429, 0x1C29)
  RTD = ("Resume Text Display", 0X142B, 0x1C2B)
  TO1 = ("Tab Offset 1 Column", 0X1721, 0x1F21)
  TO2 = ("Tab Offset 2 Columns", 0X1722, 0x1F22)
  TO3 = ("Tab Offset 3 Columns", 0X1723, 0x1F23)
  TR = ("Text Restart", 0X142A, 0x1C2A)
  RCL = ("Resume caption loading", 0X1420, 0x1C20)
  RU2 = ("Roll-Up Captions-2 Rows", 0X1425, 0x1C25)
  RU3 = ("Roll-Up Captions-3 Rows", 0X1426, 0x1C26)
  RU4 = ("Roll-Up Captions-4 Rows", 0X1427, 0x1C27)

  def __init__(self, description: str, data_channel_1_value: int,
               data_channel_2_value: int):
    self._description = description
    self._data_channel_values = [data_channel_1_value, data_channel_2_value]

  def get_name(self) -> str:
    """Retrieves Control Code name"""
    return self.name

  def get_description(self) -> str:
    """Retrieves Control Code description"""
    return self._description

  def contains_value(self, value: int) -> bool:
    """Returns whether the specified value is contained into the Control Code channels values"""
    return value in self._data_channel_values



def find_control_code(value: int) -> typing.Optional[SccControlCode]:
  """Find the Control Code corresponding to the specified value"""
  for control_code in list(SccControlCode):
    if control_code.contains_value(value):
      return control_code
  return None
