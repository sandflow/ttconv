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

"""SCC caption style"""

from enum import Enum


class SccCaptionStyle(Enum):
  """SCC caption style"""
  Unknown = 0

  # SCC Roll-Up captions are composed with:
  #  - RU2 or RU3 or RU4 (to select the Roll-Up style and the number of displayed rows)
  #  - CR (to roll the displayed rows up)
  #  - PAC (to set row, indent and/or attributes)
  #  - text
  RollUp = 1

  # SCC Paint-On captions are composed with:
  #  - RDC (to select the Paint-On style)
  #  - PAC (to set row, indent and/or attributes)
  #  - text
  #  - PAC (to change row, indent and/or attributes)
  #  - text or DER (to erase the following text of the current row)
  PaintOn = 2

  # SCC Pop-On captions are composed with:
  #  - RCL (to select the Pop-On style)
  #  - ENM (to clear the memory, optional)
  #  - PAC (to set row, indent and/or attributes)
  #  - text
  #  - PAC (to change row, indent and/or attributes)
  #  - text
  #  etc.
  #  - EDM (to erase the displayed caption, optional)
  #  - EOC (to display the current caption)
  PopOn = 3
