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
  AOF = (0X1422, 0x1C22)  # Reserved (formerly Alarm Off)
  AON = (0X1423, 0x1C23)  # Reserved (formerly Alarm On)
  BS = (0X1421, 0x1C21)  # Backspace
  CR = (0X142D, 0x1C2D)  # Carriage Return
  DER = (0X1424, 0x1C24)  # Delete to End of Row
  EDM = (0X142C, 0x1C2C)  # Erase Displayed Memory
  ENM = (0X142E, 0x1C2E)  # Erase Non-Displayed Memory
  EOC = (0X142F, 0x1C2F)  # End of Caption (Flip Memories)
  FON = (0X1428, 0x1C28)  # Flash On
  RDC = (0X1429, 0x1C29)  # Resume Direct Captioning
  RTD = (0X142B, 0x1C2B)  # Resume Text Display
  TO1 = (0X1721, 0x1F21)  # Tab Offset 1 Column
  TO2 = (0X1722, 0x1F22)  # Tab Offset 2 Columns
  TO3 = (0X1723, 0x1F23)  # Tab Offset 3 Columns
  TR = (0X142A, 0x1C2A)  # Text Restart
  RCL = (0X1420, 0x1C20)  # Resume caption loading
  RU2 = (0X1425, 0x1C25)  # Roll-Up Captions-2 Rows
  RU3 = (0X1426, 0x1C26)  # Roll-Up Captions-3 Rows
  RU4 = (0X1427, 0x1C27)  # Roll-Up Captions-4 Rows

  def get_name(self) -> str:
    """Retrieves Control Code name"""
    return self.name

  @staticmethod
  def find(value: int) -> typing.Optional[SccControlCode]:
    """Find the Control Code corresponding to the specified value"""
    for control_code in list(SccControlCode):
      if control_code.contains_value(value):
        return control_code
    return None
