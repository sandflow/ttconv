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

from __future__ import annotations

import typing
from enum import Enum

from ttconv.scc.codes import SccCode


class SccControlCode(SccCode, Enum):
  """SCC Control Code definition"""
  AOF = (0x1422, 0x1C22, 0x1522, 0x1D22)  # Reserved (formerly Alarm Off)
  AON = (0x1423, 0x1C23, 0x1523, 0x1D23)  # Reserved (formerly Alarm On)
  BS = (0x1421, 0x1C21, 0x1521, 0x1D21)  # Backspace
  CR = (0x142D, 0x1C2D, 0x152D, 0x1D2D)  # Carriage Return
  DER = (0x1424, 0x1C24, 0x1524, 0x1D24)  # Delete to End of Row
  EDM = (0x142C, 0x1C2C, 0x152C, 0x1D2C)  # Erase Displayed Memory
  ENM = (0x142E, 0x1C2E, 0x152E, 0x1D2E)  # Erase Non-Displayed Memory
  EOC = (0x142F, 0x1C2F, 0x152F, 0x1D2F)  # End of Caption (Flip Memories)
  FON = (0x1428, 0x1C28, 0x1528, 0x1D28)  # Flash On
  RDC = (0x1429, 0x1C29, 0x1529, 0x1D29)  # Resume Direct Captioning
  RTD = (0x142B, 0x1C2B, 0x152B, 0x1D2B)  # Resume Text Display
  TO1 = (0x1721, 0x1F21, 0x1721, 0x1F21)  # Tab Offset 1 Column
  TO2 = (0x1722, 0x1F22, 0x1722, 0x1F22)  # Tab Offset 2 Columns
  TO3 = (0x1723, 0x1F23, 0x1723, 0x1F23)  # Tab Offset 3 Columns
  TR = (0x142A, 0x1C2A, 0x152A, 0x1D2A)  # Text Restart
  RCL = (0x1420, 0x1C20, 0x1520, 0x1D20)  # Resume caption loading
  RU2 = (0x1425, 0x1C25, 0x1525, 0x1D25)  # Roll-Up Captions-2 Rows
  RU3 = (0x1426, 0x1C26, 0x1526, 0x1D26)  # Roll-Up Captions-3 Rows
  RU4 = (0x1427, 0x1C27, 0x1527, 0x1D27)  # Roll-Up Captions-4 Rows

  def __init__(self, channel_1_field_1: int, channel_2_field_1: int, channel_1_field_2: int, channel_2_field_2: int):
    super().__init__(channel_1_field_1, channel_2_field_1)
    self._channel_1_field_2 = channel_1_field_2
    self._channel_2_field_2 = channel_2_field_2

  def get_name(self) -> str:
    """Retrieves Control Code name"""
    return self.name

  def get_values(self) -> (int, int, int, int):
    """Returns SCC Control Code values"""
    return self._channel_1, self._channel_2, self._channel_1_field_2, self._channel_2_field_2

  @staticmethod
  def find(value: int) -> typing.Optional[SccControlCode]:
    """Find the Control Code corresponding to the specified value"""
    for control_code in list(SccControlCode):
      if control_code.contains_value(value):
        return control_code
    return None
