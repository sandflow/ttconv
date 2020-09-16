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
from ttconv.scc import control_codes


class SCCControlCodesTest(unittest.TestCase):

  def test_scc_control_codes(self):
    control_code_values = [0X1420, 0X1421, 0X1422, 0X1423, 0X1424, 0X1425, 0X1426, 0X1427, 0X1428,
                           0X1429, 0X142A, 0X142B, 0X142C, 0X142D, 0X142E, 0X142F, 0X1721, 0X1722,
                           0X1723, 0x1C20, 0x1C21, 0x1C22, 0x1C23, 0x1C24, 0x1C25, 0x1C26, 0x1C27,
                           0x1C28, 0x1C29, 0x1C2A, 0x1C2B, 0x1C2C, 0x1C2D, 0x1C2E, 0x1C2F, 0x1F21,
                           0x1F22, 0x1F23]

    other_code_values = [code for code in range(0x0000, 0xFFFF) if code not in control_code_values]

    for cc in control_code_values:
      self.assertIsNotNone(control_codes.find_control_code(cc))

    for cc in other_code_values:
      self.assertIsNone(control_codes.find_control_code(cc))
