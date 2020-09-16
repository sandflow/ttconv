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

"""Unit tests for the SCC Mid-Row Codes"""

# pylint: disable=R0201,C0115,C0116

import unittest
from ttconv.scc import mid_row_codes


class SCCMidRowCodesTest(unittest.TestCase):

  def test_scc_control_codes(self):
    mid_row_code_values = [0x1120, 0x1920, 0x1121, 0x1921, 0x1122, 0x1922, 0x1123, 0x1923, 0x1124,
                           0x1924, 0x1125, 0x1925, 0x1126, 0x1926, 0x1127, 0x1927, 0x1128, 0x1928,
                           0x1129, 0x1929, 0x112A, 0x192A, 0x112B, 0x192B, 0x112C, 0x192C, 0x112D,
                           0x192D, 0x112E, 0x192E, 0x112F, 0x192F]

    other_code_values = [code for code in range(0x0000, 0xFFFF) if code not in mid_row_code_values]

    for mrc in mid_row_code_values:
      self.assertIsNotNone(mid_row_codes.find_mid_row_code(mrc))

    for mrc in other_code_values:
      self.assertIsNone(mid_row_codes.find_mid_row_code(mrc))
