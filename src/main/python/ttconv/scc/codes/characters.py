#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2025, Sandflow Consulting LLC
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

"""SCC characters utility functions"""

from __future__ import annotations

from ttconv.scc.codes.special_characters import SccSpecialCharacter
from ttconv.scc.codes.standard_characters import TO_SCC_BYTES

def unicode_to_scc(c: str) -> bytes:
  """Convert a Unicode character to an SCC character string"""

  if len(c) != 1:
    raise ValueError("Can only convert a single character")

  b = bytearray()

  scc_c = TO_SCC_BYTES.get(c, None)

  if scc_c is not None:
    b.append(scc_c)

  else:
    scc_c = SccSpecialCharacter.from_unicode(c)

    if scc_c is not None:
      b.append(scc_c.get_ch1_value() // 256)
      b.append(scc_c.get_ch1_value() % 256)

    else:
      b.append(0x20)  # Standard

  return b