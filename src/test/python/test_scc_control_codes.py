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

"""Unit tests for the SCC Control codes"""

# pylint: disable=R0201,C0115,C0116

import unittest
from ttconv.scc.codes.control_codes import SccControlCode

CONTROL_CODE_VALUES = [0X1422, 0x1C22, 0X1423, 0x1C23, 0X1421, 0x1C21, 0X142D, 0x1C2D, 0X1424,
                       0x1C24, 0X142C, 0x1C2C, 0X142E, 0x1C2E, 0X142F, 0x1C2F, 0X1428, 0x1C28,
                       0X1429, 0x1C29, 0X142B, 0x1C2B, 0X1721, 0x1F21, 0X1722, 0x1F22, 0X1723,
                       0x1F23, 0X142A, 0x1C2A, 0X1420, 0x1C20, 0X1425, 0x1C25, 0X1426, 0x1C26,
                       0X1427, 0x1C27]


class SCCControlCodesTest(unittest.TestCase):

  def test_scc_control_codes(self):
    self.assertEqual(SccControlCode.AOF,
                     SccControlCode.find(CONTROL_CODE_VALUES[0]))
    self.assertEqual(SccControlCode.AOF,
                     SccControlCode.find(CONTROL_CODE_VALUES[1]))
    self.assertEqual(SccControlCode.AON,
                     SccControlCode.find(CONTROL_CODE_VALUES[2]))
    self.assertEqual(SccControlCode.AON,
                     SccControlCode.find(CONTROL_CODE_VALUES[3]))
    self.assertEqual(SccControlCode.BS,
                     SccControlCode.find(CONTROL_CODE_VALUES[4]))
    self.assertEqual(SccControlCode.BS,
                     SccControlCode.find(CONTROL_CODE_VALUES[5]))
    self.assertEqual(SccControlCode.CR,
                     SccControlCode.find(CONTROL_CODE_VALUES[6]))
    self.assertEqual(SccControlCode.CR,
                     SccControlCode.find(CONTROL_CODE_VALUES[7]))
    self.assertEqual(SccControlCode.DER,
                     SccControlCode.find(CONTROL_CODE_VALUES[8]))
    self.assertEqual(SccControlCode.DER,
                     SccControlCode.find(CONTROL_CODE_VALUES[9]))
    self.assertEqual(SccControlCode.EDM,
                     SccControlCode.find(CONTROL_CODE_VALUES[10]))
    self.assertEqual(SccControlCode.EDM,
                     SccControlCode.find(CONTROL_CODE_VALUES[11]))
    self.assertEqual(SccControlCode.ENM,
                     SccControlCode.find(CONTROL_CODE_VALUES[12]))
    self.assertEqual(SccControlCode.ENM,
                     SccControlCode.find(CONTROL_CODE_VALUES[13]))
    self.assertEqual(SccControlCode.EOC,
                     SccControlCode.find(CONTROL_CODE_VALUES[14]))
    self.assertEqual(SccControlCode.EOC,
                     SccControlCode.find(CONTROL_CODE_VALUES[15]))
    self.assertEqual(SccControlCode.FON,
                     SccControlCode.find(CONTROL_CODE_VALUES[16]))
    self.assertEqual(SccControlCode.FON,
                     SccControlCode.find(CONTROL_CODE_VALUES[17]))
    self.assertEqual(SccControlCode.RDC,
                     SccControlCode.find(CONTROL_CODE_VALUES[18]))
    self.assertEqual(SccControlCode.RDC,
                     SccControlCode.find(CONTROL_CODE_VALUES[19]))
    self.assertEqual(SccControlCode.RTD,
                     SccControlCode.find(CONTROL_CODE_VALUES[20]))
    self.assertEqual(SccControlCode.RTD,
                     SccControlCode.find(CONTROL_CODE_VALUES[21]))
    self.assertEqual(SccControlCode.TO1,
                     SccControlCode.find(CONTROL_CODE_VALUES[22]))
    self.assertEqual(SccControlCode.TO1,
                     SccControlCode.find(CONTROL_CODE_VALUES[23]))
    self.assertEqual(SccControlCode.TO2,
                     SccControlCode.find(CONTROL_CODE_VALUES[24]))
    self.assertEqual(SccControlCode.TO2,
                     SccControlCode.find(CONTROL_CODE_VALUES[25]))
    self.assertEqual(SccControlCode.TO3,
                     SccControlCode.find(CONTROL_CODE_VALUES[26]))
    self.assertEqual(SccControlCode.TO3,
                     SccControlCode.find(CONTROL_CODE_VALUES[27]))
    self.assertEqual(SccControlCode.TR,
                     SccControlCode.find(CONTROL_CODE_VALUES[28]))
    self.assertEqual(SccControlCode.TR,
                     SccControlCode.find(CONTROL_CODE_VALUES[29]))
    self.assertEqual(SccControlCode.RCL,
                     SccControlCode.find(CONTROL_CODE_VALUES[30]))
    self.assertEqual(SccControlCode.RCL,
                     SccControlCode.find(CONTROL_CODE_VALUES[31]))
    self.assertEqual(SccControlCode.RU2,
                     SccControlCode.find(CONTROL_CODE_VALUES[32]))
    self.assertEqual(SccControlCode.RU2,
                     SccControlCode.find(CONTROL_CODE_VALUES[33]))
    self.assertEqual(SccControlCode.RU3,
                     SccControlCode.find(CONTROL_CODE_VALUES[34]))
    self.assertEqual(SccControlCode.RU3,
                     SccControlCode.find(CONTROL_CODE_VALUES[35]))
    self.assertEqual(SccControlCode.RU4,
                     SccControlCode.find(CONTROL_CODE_VALUES[36]))
    self.assertEqual(SccControlCode.RU4,
                     SccControlCode.find(CONTROL_CODE_VALUES[37]))

  def test_scc_control_codes_invalid(self):
    other_code_values = [code for code in range(0x0000, 0xFFFF) if code not in CONTROL_CODE_VALUES]

    for cc in other_code_values:
      self.assertIsNone(SccControlCode.find(cc))

if __name__ == '__main__':
  unittest.main()
