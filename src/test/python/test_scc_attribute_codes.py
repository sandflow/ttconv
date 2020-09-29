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

from unittest import TestCase

from ttconv.scc.attribute_codes import SccAttributeCode, SccAttributeCodes

VALID_VALUES = [0x1020, 0x1820, 0x1021, 0x1821, 0x1022, 0x1822, 0x1023, 0x1823, 0x1024, 0x1824, 0x1025, 0x1825,
                0x1026, 0x1826, 0x1027, 0x1827, 0x1028, 0x1828, 0x1029, 0x1829, 0x102A, 0x182A, 0x102B, 0x182B,
                0x102C, 0x182C, 0x102D, 0x182D, 0x102E, 0x182E, 0x102F, 0x182F, 0x172D, 0x1F2D, 0x172E, 0x1F2E,
                0x172F, 0x1F2F]


class TestSccAttributeCodes(TestCase):

  def test_scc_attribute_codes(self):
    self.assertEqual(SccAttributeCodes.BWO,
                     SccAttributeCodes.find(VALID_VALUES[0]))
    self.assertEqual(SccAttributeCodes.BWO,
                     SccAttributeCodes.find(VALID_VALUES[1]))
    self.assertEqual(SccAttributeCodes.BWS,
                     SccAttributeCodes.find(VALID_VALUES[2]))
    self.assertEqual(SccAttributeCodes.BWS,
                     SccAttributeCodes.find(VALID_VALUES[3]))
    self.assertEqual(SccAttributeCodes.BGO,
                     SccAttributeCodes.find(VALID_VALUES[4]))
    self.assertEqual(SccAttributeCodes.BGO,
                     SccAttributeCodes.find(VALID_VALUES[5]))
    self.assertEqual(SccAttributeCodes.BGS,
                     SccAttributeCodes.find(VALID_VALUES[6]))
    self.assertEqual(SccAttributeCodes.BGS,
                     SccAttributeCodes.find(VALID_VALUES[7]))
    self.assertEqual(SccAttributeCodes.BBO,
                     SccAttributeCodes.find(VALID_VALUES[8]))
    self.assertEqual(SccAttributeCodes.BBO,
                     SccAttributeCodes.find(VALID_VALUES[9]))
    self.assertEqual(SccAttributeCodes.BBS,
                     SccAttributeCodes.find(VALID_VALUES[10]))
    self.assertEqual(SccAttributeCodes.BBS,
                     SccAttributeCodes.find(VALID_VALUES[11]))
    self.assertEqual(SccAttributeCodes.BCO,
                     SccAttributeCodes.find(VALID_VALUES[12]))
    self.assertEqual(SccAttributeCodes.BCO,
                     SccAttributeCodes.find(VALID_VALUES[13]))
    self.assertEqual(SccAttributeCodes.BCS,
                     SccAttributeCodes.find(VALID_VALUES[14]))
    self.assertEqual(SccAttributeCodes.BCS,
                     SccAttributeCodes.find(VALID_VALUES[15]))
    self.assertEqual(SccAttributeCodes.BRO,
                     SccAttributeCodes.find(VALID_VALUES[16]))
    self.assertEqual(SccAttributeCodes.BRO,
                     SccAttributeCodes.find(VALID_VALUES[17]))
    self.assertEqual(SccAttributeCodes.BRS,
                     SccAttributeCodes.find(VALID_VALUES[18]))
    self.assertEqual(SccAttributeCodes.BRS,
                     SccAttributeCodes.find(VALID_VALUES[19]))
    self.assertEqual(SccAttributeCodes.BYO,
                     SccAttributeCodes.find(VALID_VALUES[20]))
    self.assertEqual(SccAttributeCodes.BYO,
                     SccAttributeCodes.find(VALID_VALUES[21]))
    self.assertEqual(SccAttributeCodes.BYS,
                     SccAttributeCodes.find(VALID_VALUES[22]))
    self.assertEqual(SccAttributeCodes.BYS,
                     SccAttributeCodes.find(VALID_VALUES[23]))
    self.assertEqual(SccAttributeCodes.BMO,
                     SccAttributeCodes.find(VALID_VALUES[24]))
    self.assertEqual(SccAttributeCodes.BMO,
                     SccAttributeCodes.find(VALID_VALUES[25]))
    self.assertEqual(SccAttributeCodes.BMS,
                     SccAttributeCodes.find(VALID_VALUES[26]))
    self.assertEqual(SccAttributeCodes.BMS,
                     SccAttributeCodes.find(VALID_VALUES[27]))
    self.assertEqual(SccAttributeCodes.BAO,
                     SccAttributeCodes.find(VALID_VALUES[28]))
    self.assertEqual(SccAttributeCodes.BAO,
                     SccAttributeCodes.find(VALID_VALUES[29]))
    self.assertEqual(SccAttributeCodes.BAS,
                     SccAttributeCodes.find(VALID_VALUES[30]))
    self.assertEqual(SccAttributeCodes.BAS,
                     SccAttributeCodes.find(VALID_VALUES[31]))
    self.assertEqual(SccAttributeCodes.BT,
                     SccAttributeCodes.find(VALID_VALUES[32]))
    self.assertEqual(SccAttributeCodes.BT,
                     SccAttributeCodes.find(VALID_VALUES[33]))
    self.assertEqual(SccAttributeCodes.FA,
                     SccAttributeCodes.find(VALID_VALUES[34]))
    self.assertEqual(SccAttributeCodes.FA,
                     SccAttributeCodes.find(VALID_VALUES[35]))
    self.assertEqual(SccAttributeCodes.FAU,
                     SccAttributeCodes.find(VALID_VALUES[36]))
    self.assertEqual(SccAttributeCodes.FAU,
                     SccAttributeCodes.find(VALID_VALUES[37]))

  def test_scc_attribute_codes_invalid(self):
    other_code_values = [code for code in range(0x0000, 0xFFFF) if code not in VALID_VALUES]

    for cc in other_code_values:
      self.assertIsNone(SccAttributeCodes.find(cc))
