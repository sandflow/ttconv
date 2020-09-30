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

"""Unit tests for the SCC PACs"""

# pylint: disable=R0201,C0115,C0116

import unittest
from ttconv.scc.codes.preambles_access_codes import SccPreambleAccessCode


class SCCPreambleAccessCodesTest(unittest.TestCase):

  def test_scc_pac_values(self):
    channel_1_byte_1 = [0x11, 0x12, 0x15, 0x16, 0x17, 0x10, 0x13, 0x14]
    channel_2_byte_1 = [0x19, 0x1A, 0x1D, 0x1E, 0x1F, 0x18, 0x1B, 0x1C]

    all_range = list(range(0x00, 0XFF))
    byte_2_range = range(0x40, 0x80)

    other_bytes_1 = [item for item in all_range
                     if item not in channel_1_byte_1 and item not in channel_2_byte_1]
    other_bytes_2 = [item for item in all_range if item not in list(byte_2_range)]

    for b1 in channel_1_byte_1:
      for b2 in byte_2_range:
        pac = SccPreambleAccessCode.find(b1, b2)

        if b2 > 0x5F and b1 % 0x08 == 0:  # row 11 case
          self.assertIsNone(pac)
        else:
          self.assertIsNotNone(pac)

      for b2 in other_bytes_2:
        self.assertIsNone(SccPreambleAccessCode.find(b1, b2))

    for b1 in channel_2_byte_1:
      for b2 in byte_2_range:
        pac = SccPreambleAccessCode.find(b1, b2)

        if b2 > 0x5F and b1 % 0x08 == 0:  # row 11 case
          self.assertIsNone(pac)
        else:
          self.assertIsNotNone(pac)

      for b2 in other_bytes_2:
        self.assertIsNone(SccPreambleAccessCode.find(b1, b2))

    for b1 in other_bytes_1:
      for b2 in range(0x00, 0xFF):
        self.assertIsNone(SccPreambleAccessCode.find(b1, b2))


if __name__ == '__main__':
  unittest.main()
