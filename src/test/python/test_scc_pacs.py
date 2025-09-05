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

from ttconv.scc.codes.preambles_address_codes import SccPreambleAddressCode
from ttconv.style_properties import TextDecorationType, NamedColors, FontStyleType


class SCCPreambleAddressCodesTest(unittest.TestCase):

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
        pac = SccPreambleAddressCode.find(b1, b2)

        if b2 > 0x5F and b1 % 0x08 == 0:  # row 11 case
          self.assertIsNone(pac)
        else:
          self.assertIsNotNone(pac)

      for b2 in other_bytes_2:
        self.assertIsNone(SccPreambleAddressCode.find(b1, b2))

    for b1 in channel_2_byte_1:
      for b2 in byte_2_range:
        pac = SccPreambleAddressCode.find(b1, b2)

        if b2 > 0x5F and b1 % 0x08 == 0:  # row 11 case
          self.assertIsNone(pac)
        else:
          self.assertIsNotNone(pac)

      for b2 in other_bytes_2:
        self.assertIsNone(SccPreambleAddressCode.find(b1, b2))

    for b1 in other_bytes_1:
      for b2 in range(0x00, 0xFF):
        self.assertIsNone(SccPreambleAddressCode.find(b1, b2))

  def check_scc_pac_attributes(self, pac, channel, row, indent, color, font_style, text_decoration):
    self.assertEqual(channel, pac.get_channel().value)
    self.assertEqual(row, pac.get_row())
    self.assertEqual(indent, pac.get_indent())
    self.assertEqual(color, pac.get_color())
    self.assertEqual(font_style, pac.get_font_style())
    self.assertEqual(text_decoration, pac.get_text_decoration())

  def test_scc_pac_white(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x40), 1, 1, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x60), 1, 2, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x40), 1, 3, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x60), 1, 4, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x40), 1, 5, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x60), 1, 6, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x40), 1, 7, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x60), 1, 8, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x40), 1, 9, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x60), 1, 10, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x40), 1, 11, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x40), 1, 12, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x60), 1, 13, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x40), 1, 14, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x60), 1, 15, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x40), 2, 1, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x60), 2, 2, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x40), 2, 3, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x60), 2, 4, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x40), 2, 5, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x60), 2, 6, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x40), 2, 7, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x60), 2, 8, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x40), 2, 9, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x60), 2, 10, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x40), 2, 11, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x40), 2, 12, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x60), 2, 13, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x40), 2, 14, None, NamedColors.white.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x60), 2, 15, None, NamedColors.white.value, None, None)

  def test_scc_pac_white_underline(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x41), 1, 1, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x61), 1, 2, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x41), 1, 3, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x61), 1, 4, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x41), 1, 5, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x61), 1, 6, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x41), 1, 7, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x61), 1, 8, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x41), 1, 9, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x61), 1, 10, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x41), 1, 11, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x41), 1, 12, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x61), 1, 13, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x41), 1, 14, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x61), 1, 15, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x41), 2, 1, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x61), 2, 2, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x41), 2, 3, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x61), 2, 4, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x41), 2, 5, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x61), 2, 6, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x41), 2, 7, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x61), 2, 8, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x41), 2, 9, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x61), 2, 10, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x41), 2, 11, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x41), 2, 12, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x61), 2, 13, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x41), 2, 14, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x61), 2, 15, None, NamedColors.white.value, None,
                                  TextDecorationType(underline=True))

  def test_scc_pac_green(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x42), 1, 1, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x62), 1, 2, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x42), 1, 3, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x62), 1, 4, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x42), 1, 5, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x62), 1, 6, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x42), 1, 7, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x62), 1, 8, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x42), 1, 9, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x62), 1, 10, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x42), 1, 11, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x42), 1, 12, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x62), 1, 13, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x42), 1, 14, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x62), 1, 15, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x42), 2, 1, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x62), 2, 2, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x42), 2, 3, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x62), 2, 4, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x42), 2, 5, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x62), 2, 6, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x42), 2, 7, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x62), 2, 8, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x42), 2, 9, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x62), 2, 10, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x42), 2, 11, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x42), 2, 12, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x62), 2, 13, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x42), 2, 14, None, NamedColors.green.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x62), 2, 15, None, NamedColors.green.value, None, None)

  def test_scc_pac_green_underline(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x43), 1, 1, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x63), 1, 2, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x43), 1, 3, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x63), 1, 4, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x43), 1, 5, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x63), 1, 6, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x43), 1, 7, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x63), 1, 8, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x43), 1, 9, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x63), 1, 10, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x43), 1, 11, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x43), 1, 12, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x63), 1, 13, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x43), 1, 14, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x63), 1, 15, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x43), 2, 1, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x63), 2, 2, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x43), 2, 3, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x63), 2, 4, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x43), 2, 5, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x63), 2, 6, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x43), 2, 7, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x63), 2, 8, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x43), 2, 9, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x63), 2, 10, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x43), 2, 11, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x43), 2, 12, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x63), 2, 13, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x43), 2, 14, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x63), 2, 15, None, NamedColors.green.value, None,
                                  TextDecorationType(underline=True))

  def test_scc_pac_blue(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x44), 1, 1, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x64), 1, 2, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x44), 1, 3, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x64), 1, 4, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x44), 1, 5, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x64), 1, 6, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x44), 1, 7, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x64), 1, 8, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x44), 1, 9, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x64), 1, 10, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x44), 1, 11, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x44), 1, 12, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x64), 1, 13, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x44), 1, 14, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x64), 1, 15, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x44), 2, 1, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x64), 2, 2, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x44), 2, 3, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x64), 2, 4, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x44), 2, 5, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x64), 2, 6, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x44), 2, 7, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x64), 2, 8, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x44), 2, 9, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x64), 2, 10, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x44), 2, 11, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x44), 2, 12, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x64), 2, 13, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x44), 2, 14, None, NamedColors.blue.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x64), 2, 15, None, NamedColors.blue.value, None, None)

  def test_scc_pac_blue_underline(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x45), 1, 1, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x65), 1, 2, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x45), 1, 3, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x65), 1, 4, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x45), 1, 5, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x65), 1, 6, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x45), 1, 7, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x65), 1, 8, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x45), 1, 9, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x65), 1, 10, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x45), 1, 11, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x45), 1, 12, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x65), 1, 13, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x45), 1, 14, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x65), 1, 15, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x45), 2, 1, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x65), 2, 2, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x45), 2, 3, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x65), 2, 4, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x45), 2, 5, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x65), 2, 6, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x45), 2, 7, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x65), 2, 8, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x45), 2, 9, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x65), 2, 10, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x45), 2, 11, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x45), 2, 12, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x65), 2, 13, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x45), 2, 14, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x65), 2, 15, None, NamedColors.blue.value, None,
                                  TextDecorationType(underline=True))

  def test_scc_pac_cyan(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x46), 1, 1, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x66), 1, 2, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x46), 1, 3, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x66), 1, 4, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x46), 1, 5, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x66), 1, 6, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x46), 1, 7, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x66), 1, 8, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x46), 1, 9, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x66), 1, 10, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x46), 1, 11, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x46), 1, 12, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x66), 1, 13, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x46), 1, 14, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x66), 1, 15, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x46), 2, 1, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x66), 2, 2, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x46), 2, 3, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x66), 2, 4, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x46), 2, 5, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x66), 2, 6, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x46), 2, 7, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x66), 2, 8, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x46), 2, 9, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x66), 2, 10, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x46), 2, 11, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x46), 2, 12, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x66), 2, 13, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x46), 2, 14, None, NamedColors.cyan.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x66), 2, 15, None, NamedColors.cyan.value, None, None)

  def test_scc_pac_cyan_underline(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x47), 1, 1, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x67), 1, 2, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x47), 1, 3, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x67), 1, 4, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x47), 1, 5, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x67), 1, 6, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x47), 1, 7, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x67), 1, 8, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x47), 1, 9, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x67), 1, 10, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x47), 1, 11, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x47), 1, 12, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x67), 1, 13, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x47), 1, 14, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x67), 1, 15, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x47), 2, 1, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x67), 2, 2, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x47), 2, 3, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x67), 2, 4, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x47), 2, 5, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x67), 2, 6, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x47), 2, 7, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x67), 2, 8, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x47), 2, 9, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x67), 2, 10, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x47), 2, 11, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x47), 2, 12, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x67), 2, 13, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x47), 2, 14, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x67), 2, 15, None, NamedColors.cyan.value, None,
                                  TextDecorationType(underline=True))

  def test_scc_pac_red(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x48), 1, 1, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x68), 1, 2, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x48), 1, 3, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x68), 1, 4, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x48), 1, 5, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x68), 1, 6, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x48), 1, 7, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x68), 1, 8, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x48), 1, 9, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x68), 1, 10, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x48), 1, 11, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x48), 1, 12, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x68), 1, 13, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x48), 1, 14, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x68), 1, 15, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x48), 2, 1, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x68), 2, 2, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x48), 2, 3, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x68), 2, 4, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x48), 2, 5, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x68), 2, 6, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x48), 2, 7, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x68), 2, 8, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x48), 2, 9, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x68), 2, 10, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x48), 2, 11, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x48), 2, 12, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x68), 2, 13, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x48), 2, 14, None, NamedColors.red.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x68), 2, 15, None, NamedColors.red.value, None, None)

  def test_scc_pac_red_underline(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x49), 1, 1, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x69), 1, 2, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x49), 1, 3, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x69), 1, 4, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x49), 1, 5, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x69), 1, 6, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x49), 1, 7, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x69), 1, 8, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x49), 1, 9, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x69), 1, 10, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x49), 1, 11, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x49), 1, 12, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x69), 1, 13, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x49), 1, 14, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x69), 1, 15, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x49), 2, 1, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x69), 2, 2, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x49), 2, 3, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x69), 2, 4, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x49), 2, 5, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x69), 2, 6, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x49), 2, 7, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x69), 2, 8, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x49), 2, 9, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x69), 2, 10, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x49), 2, 11, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x49), 2, 12, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x69), 2, 13, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x49), 2, 14, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x69), 2, 15, None, NamedColors.red.value, None,
                                  TextDecorationType(underline=True))

  def test_scc_pac_yellow(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x4A), 1, 1, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x6A), 1, 2, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x4A), 1, 3, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x6A), 1, 4, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x4A), 1, 5, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x6A), 1, 6, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x4A), 1, 7, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x6A), 1, 8, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x4A), 1, 9, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x6A), 1, 10, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x4A), 1, 11, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x4A), 1, 12, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x6A), 1, 13, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x4A), 1, 14, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x6A), 1, 15, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x4A), 2, 1, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x6A), 2, 2, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x4A), 2, 3, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x6A), 2, 4, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x4A), 2, 5, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x6A), 2, 6, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x4A), 2, 7, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x6A), 2, 8, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x4A), 2, 9, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x6A), 2, 10, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x4A), 2, 11, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x4A), 2, 12, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x6A), 2, 13, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x4A), 2, 14, None, NamedColors.yellow.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x6A), 2, 15, None, NamedColors.yellow.value, None, None)

  def test_scc_pac_yellow_underline(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x4B), 1, 1, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x6B), 1, 2, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x4B), 1, 3, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x6B), 1, 4, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x4B), 1, 5, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x6B), 1, 6, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x4B), 1, 7, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x6B), 1, 8, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x4B), 1, 9, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x6B), 1, 10, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x4B), 1, 11, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x4B), 1, 12, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x6B), 1, 13, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x4B), 1, 14, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x6B), 1, 15, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x4B), 2, 1, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x6B), 2, 2, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x4B), 2, 3, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x6B), 2, 4, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x4B), 2, 5, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x6B), 2, 6, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x4B), 2, 7, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x6B), 2, 8, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x4B), 2, 9, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x6B), 2, 10, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x4B), 2, 11, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x4B), 2, 12, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x6B), 2, 13, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x4B), 2, 14, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x6B), 2, 15, None, NamedColors.yellow.value, None,
                                  TextDecorationType(underline=True))

  def test_scc_pac_magenta(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x4C), 1, 1, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x6C), 1, 2, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x4C), 1, 3, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x6C), 1, 4, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x4C), 1, 5, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x6C), 1, 6, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x4C), 1, 7, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x6C), 1, 8, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x4C), 1, 9, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x6C), 1, 10, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x4C), 1, 11, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x4C), 1, 12, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x6C), 1, 13, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x4C), 1, 14, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x6C), 1, 15, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x4C), 2, 1, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x6C), 2, 2, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x4C), 2, 3, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x6C), 2, 4, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x4C), 2, 5, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x6C), 2, 6, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x4C), 2, 7, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x6C), 2, 8, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x4C), 2, 9, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x6C), 2, 10, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x4C), 2, 11, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x4C), 2, 12, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x6C), 2, 13, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x4C), 2, 14, None, NamedColors.magenta.value, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x6C), 2, 15, None, NamedColors.magenta.value, None, None)

  def test_scc_pac_magenta_underline(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x4D), 1, 1, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x6D), 1, 2, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x4D), 1, 3, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x6D), 1, 4, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x4D), 1, 5, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x6D), 1, 6, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x4D), 1, 7, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x6D), 1, 8, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x4D), 1, 9, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x6D), 1, 10, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x4D), 1, 11, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x4D), 1, 12, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x6D), 1, 13, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x4D), 1, 14, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x6D), 1, 15, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x4D), 2, 1, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x6D), 2, 2, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x4D), 2, 3, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x6D), 2, 4, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x4D), 2, 5, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x6D), 2, 6, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x4D), 2, 7, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x6D), 2, 8, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x4D), 2, 9, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x6D), 2, 10, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x4D), 2, 11, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x4D), 2, 12, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x6D), 2, 13, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x4D), 2, 14, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x6D), 2, 15, None, NamedColors.magenta.value, None,
                                  TextDecorationType(underline=True))

  def test_scc_pac_white_italics(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x4E), 1, 1, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x6E), 1, 2, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x4E), 1, 3, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x6E), 1, 4, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x4E), 1, 5, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x6E), 1, 6, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x4E), 1, 7, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x6E), 1, 8, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x4E), 1, 9, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x6E), 1, 10, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x4E), 1, 11, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x4E), 1, 12, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x6E), 1, 13, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x4E), 1, 14, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x6E), 1, 15, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x4E), 2, 1, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x6E), 2, 2, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x4E), 2, 3, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x6E), 2, 4, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x4E), 2, 5, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x6E), 2, 6, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x4E), 2, 7, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x6E), 2, 8, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x4E), 2, 9, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x6E), 2, 10, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x4E), 2, 11, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x4E), 2, 12, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x6E), 2, 13, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x4E), 2, 14, None, NamedColors.white.value, FontStyleType.italic,
                                  None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x6E), 2, 15, None, NamedColors.white.value, FontStyleType.italic,
                                  None)

  def test_scc_pac_white_italics_underline(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x4F), 1, 1, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x6F), 1, 2, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x4F), 1, 3, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x6F), 1, 4, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x4F), 1, 5, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x6F), 1, 6, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x4F), 1, 7, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x6F), 1, 8, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x4F), 1, 9, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x6F), 1, 10, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x4F), 1, 11, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x4F), 1, 12, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x6F), 1, 13, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x4F), 1, 14, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x6F), 1, 15, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x4F), 2, 1, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x6F), 2, 2, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x4F), 2, 3, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x6F), 2, 4, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x4F), 2, 5, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x6F), 2, 6, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x4F), 2, 7, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x6F), 2, 8, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x4F), 2, 9, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x6F), 2, 10, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x4F), 2, 11, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x4F), 2, 12, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x6F), 2, 13, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x4F), 2, 14, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x6F), 2, 15, None, NamedColors.white.value, FontStyleType.italic,
                                  TextDecorationType(underline=True))

  def test_scc_pac_indent_0(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x50), 1, 1, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x70), 1, 2, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x50), 1, 3, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x70), 1, 4, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x50), 1, 5, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x70), 1, 6, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x50), 1, 7, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x70), 1, 8, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x50), 1, 9, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x70), 1, 10, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x50), 1, 11, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x50), 1, 12, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x70), 1, 13, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x50), 1, 14, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x70), 1, 15, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x50), 2, 1, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x70), 2, 2, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x50), 2, 3, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x70), 2, 4, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x50), 2, 5, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x70), 2, 6, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x50), 2, 7, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x70), 2, 8, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x50), 2, 9, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x70), 2, 10, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x50), 2, 11, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x50), 2, 12, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x70), 2, 13, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x50), 2, 14, 0, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x70), 2, 15, 0, None, None, None)

  def test_scc_pac_indent_0_underline(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x51), 1, 1, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x71), 1, 2, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x51), 1, 3, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x71), 1, 4, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x51), 1, 5, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x71), 1, 6, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x51), 1, 7, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x71), 1, 8, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x51), 1, 9, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x71), 1, 10, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x51), 1, 11, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x51), 1, 12, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x71), 1, 13, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x51), 1, 14, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x71), 1, 15, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x51), 2, 1, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x71), 2, 2, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x51), 2, 3, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x71), 2, 4, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x51), 2, 5, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x71), 2, 6, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x51), 2, 7, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x71), 2, 8, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x51), 2, 9, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x71), 2, 10, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x51), 2, 11, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x51), 2, 12, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x71), 2, 13, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x51), 2, 14, 0, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x71), 2, 15, 0, None, None,
                                  TextDecorationType(underline=True))

  def test_scc_pac_indent_4(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x52), 1, 1, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x72), 1, 2, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x52), 1, 3, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x72), 1, 4, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x52), 1, 5, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x72), 1, 6, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x52), 1, 7, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x72), 1, 8, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x52), 1, 9, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x72), 1, 10, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x52), 1, 11, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x52), 1, 12, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x72), 1, 13, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x52), 1, 14, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x72), 1, 15, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x52), 2, 1, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x72), 2, 2, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x52), 2, 3, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x72), 2, 4, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x52), 2, 5, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x72), 2, 6, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x52), 2, 7, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x72), 2, 8, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x52), 2, 9, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x72), 2, 10, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x52), 2, 11, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x52), 2, 12, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x72), 2, 13, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x52), 2, 14, 4, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x72), 2, 15, 4, None, None, None)

  def test_scc_pac_indent_4_underline(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x53), 1, 1, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x73), 1, 2, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x53), 1, 3, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x73), 1, 4, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x53), 1, 5, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x73), 1, 6, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x53), 1, 7, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x73), 1, 8, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x53), 1, 9, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x73), 1, 10, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x53), 1, 11, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x53), 1, 12, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x73), 1, 13, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x53), 1, 14, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x73), 1, 15, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x53), 2, 1, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x73), 2, 2, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x53), 2, 3, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x73), 2, 4, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x53), 2, 5, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x73), 2, 6, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x53), 2, 7, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x73), 2, 8, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x53), 2, 9, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x73), 2, 10, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x53), 2, 11, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x53), 2, 12, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x73), 2, 13, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x53), 2, 14, 4, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x73), 2, 15, 4, None, None,
                                  TextDecorationType(underline=True))

  def test_scc_pac_indent_8(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x54), 1, 1, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x74), 1, 2, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x54), 1, 3, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x74), 1, 4, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x54), 1, 5, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x74), 1, 6, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x54), 1, 7, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x74), 1, 8, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x54), 1, 9, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x74), 1, 10, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x54), 1, 11, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x54), 1, 12, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x74), 1, 13, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x54), 1, 14, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x74), 1, 15, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x54), 2, 1, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x74), 2, 2, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x54), 2, 3, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x74), 2, 4, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x54), 2, 5, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x74), 2, 6, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x54), 2, 7, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x74), 2, 8, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x54), 2, 9, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x74), 2, 10, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x54), 2, 11, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x54), 2, 12, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x74), 2, 13, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x54), 2, 14, 8, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x74), 2, 15, 8, None, None, None)

  def test_scc_pac_indent_8_underline(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x55), 1, 1, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x75), 1, 2, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x55), 1, 3, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x75), 1, 4, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x55), 1, 5, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x75), 1, 6, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x55), 1, 7, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x75), 1, 8, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x55), 1, 9, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x75), 1, 10, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x55), 1, 11, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x55), 1, 12, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x75), 1, 13, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x55), 1, 14, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x75), 1, 15, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x55), 2, 1, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x75), 2, 2, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x55), 2, 3, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x75), 2, 4, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x55), 2, 5, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x75), 2, 6, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x55), 2, 7, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x75), 2, 8, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x55), 2, 9, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x75), 2, 10, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x55), 2, 11, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x55), 2, 12, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x75), 2, 13, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x55), 2, 14, 8, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x75), 2, 15, 8, None, None,
                                  TextDecorationType(underline=True))

  def test_scc_pac_indent_12(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x56), 1, 1, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x76), 1, 2, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x56), 1, 3, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x76), 1, 4, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x56), 1, 5, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x76), 1, 6, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x56), 1, 7, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x76), 1, 8, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x56), 1, 9, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x76), 1, 10, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x56), 1, 11, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x56), 1, 12, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x76), 1, 13, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x56), 1, 14, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x76), 1, 15, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x56), 2, 1, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x76), 2, 2, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x56), 2, 3, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x76), 2, 4, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x56), 2, 5, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x76), 2, 6, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x56), 2, 7, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x76), 2, 8, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x56), 2, 9, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x76), 2, 10, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x56), 2, 11, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x56), 2, 12, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x76), 2, 13, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x56), 2, 14, 12, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x76), 2, 15, 12, None, None, None)

  def test_scc_pac_indent_12_underline(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x57), 1, 1, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x77), 1, 2, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x57), 1, 3, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x77), 1, 4, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x57), 1, 5, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x77), 1, 6, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x57), 1, 7, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x77), 1, 8, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x57), 1, 9, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x77), 1, 10, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x57), 1, 11, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x57), 1, 12, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x77), 1, 13, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x57), 1, 14, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x77), 1, 15, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x57), 2, 1, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x77), 2, 2, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x57), 2, 3, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x77), 2, 4, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x57), 2, 5, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x77), 2, 6, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x57), 2, 7, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x77), 2, 8, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x57), 2, 9, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x77), 2, 10, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x57), 2, 11, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x57), 2, 12, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x77), 2, 13, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x57), 2, 14, 12, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x77), 2, 15, 12, None, None,
                                  TextDecorationType(underline=True))

  def test_scc_pac_indent_16(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x58), 1, 1, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x78), 1, 2, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x58), 1, 3, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x78), 1, 4, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x58), 1, 5, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x78), 1, 6, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x58), 1, 7, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x78), 1, 8, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x58), 1, 9, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x78), 1, 10, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x58), 1, 11, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x58), 1, 12, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x78), 1, 13, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x58), 1, 14, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x78), 1, 15, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x58), 2, 1, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x78), 2, 2, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x58), 2, 3, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x78), 2, 4, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x58), 2, 5, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x78), 2, 6, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x58), 2, 7, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x78), 2, 8, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x58), 2, 9, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x78), 2, 10, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x58), 2, 11, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x58), 2, 12, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x78), 2, 13, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x58), 2, 14, 16, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x78), 2, 15, 16, None, None, None)

  def test_scc_pac_indent_16_underline(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x59), 1, 1, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x79), 1, 2, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x59), 1, 3, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x79), 1, 4, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x59), 1, 5, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x79), 1, 6, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x59), 1, 7, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x79), 1, 8, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x59), 1, 9, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x79), 1, 10, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x59), 1, 11, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x59), 1, 12, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x79), 1, 13, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x59), 1, 14, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x79), 1, 15, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x59), 2, 1, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x79), 2, 2, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x59), 2, 3, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x79), 2, 4, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x59), 2, 5, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x79), 2, 6, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x59), 2, 7, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x79), 2, 8, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x59), 2, 9, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x79), 2, 10, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x59), 2, 11, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x59), 2, 12, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x79), 2, 13, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x59), 2, 14, 16, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x79), 2, 15, 16, None, None,
                                  TextDecorationType(underline=True))

  def test_scc_pac_indent_20(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x5A), 1, 1, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x7A), 1, 2, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x5A), 1, 3, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x7A), 1, 4, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x5A), 1, 5, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x7A), 1, 6, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x5A), 1, 7, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x7A), 1, 8, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x5A), 1, 9, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x7A), 1, 10, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x5A), 1, 11, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x5A), 1, 12, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x7A), 1, 13, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x5A), 1, 14, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x7A), 1, 15, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x5A), 2, 1, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x7A), 2, 2, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x5A), 2, 3, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x7A), 2, 4, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x5A), 2, 5, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x7A), 2, 6, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x5A), 2, 7, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x7A), 2, 8, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x5A), 2, 9, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x7A), 2, 10, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x5A), 2, 11, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x5A), 2, 12, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x7A), 2, 13, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x5A), 2, 14, 20, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x7A), 2, 15, 20, None, None, None)

  def test_scc_pac_indent_20_underline(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x5B), 1, 1, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x7B), 1, 2, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x5B), 1, 3, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x7B), 1, 4, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x5B), 1, 5, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x7B), 1, 6, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x5B), 1, 7, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x7B), 1, 8, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x5B), 1, 9, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x7B), 1, 10, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x5B), 1, 11, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x5B), 1, 12, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x7B), 1, 13, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x5B), 1, 14, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x7B), 1, 15, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x5B), 2, 1, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x7B), 2, 2, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x5B), 2, 3, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x7B), 2, 4, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x5B), 2, 5, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x7B), 2, 6, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x5B), 2, 7, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x7B), 2, 8, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x5B), 2, 9, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x7B), 2, 10, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x5B), 2, 11, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x5B), 2, 12, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x7B), 2, 13, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x5B), 2, 14, 20, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x7B), 2, 15, 20, None, None,
                                  TextDecorationType(underline=True))

  def test_scc_pac_indent_24(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x5C), 1, 1, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x7C), 1, 2, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x5C), 1, 3, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x7C), 1, 4, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x5C), 1, 5, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x7C), 1, 6, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x5C), 1, 7, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x7C), 1, 8, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x5C), 1, 9, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x7C), 1, 10, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x5C), 1, 11, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x5C), 1, 12, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x7C), 1, 13, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x5C), 1, 14, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x7C), 1, 15, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x5C), 2, 1, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x7C), 2, 2, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x5C), 2, 3, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x7C), 2, 4, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x5C), 2, 5, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x7C), 2, 6, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x5C), 2, 7, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x7C), 2, 8, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x5C), 2, 9, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x7C), 2, 10, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x5C), 2, 11, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x5C), 2, 12, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x7C), 2, 13, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x5C), 2, 14, 24, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x7C), 2, 15, 24, None, None, None)

  def test_scc_pac_indent_24_underline(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x5D), 1, 1, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x7D), 1, 2, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x5D), 1, 3, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x7D), 1, 4, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x5D), 1, 5, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x7D), 1, 6, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x5D), 1, 7, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x7D), 1, 8, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x5D), 1, 9, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x7D), 1, 10, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x5D), 1, 11, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x5D), 1, 12, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x7D), 1, 13, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x5D), 1, 14, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x7D), 1, 15, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x5D), 2, 1, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x7D), 2, 2, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x5D), 2, 3, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x7D), 2, 4, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x5D), 2, 5, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x7D), 2, 6, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x5D), 2, 7, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x7D), 2, 8, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x5D), 2, 9, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x7D), 2, 10, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x5D), 2, 11, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x5D), 2, 12, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x7D), 2, 13, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x5D), 2, 14, 24, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x7D), 2, 15, 24, None, None,
                                  TextDecorationType(underline=True))

  def test_scc_pac_indent_28(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x5E), 1, 1, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x7E), 1, 2, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x5E), 1, 3, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x7E), 1, 4, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x5E), 1, 5, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x7E), 1, 6, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x5E), 1, 7, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x7E), 1, 8, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x5E), 1, 9, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x7E), 1, 10, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x5E), 1, 11, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x5E), 1, 12, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x7E), 1, 13, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x5E), 1, 14, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x7E), 1, 15, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x5E), 2, 1, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x7E), 2, 2, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x5E), 2, 3, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x7E), 2, 4, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x5E), 2, 5, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x7E), 2, 6, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x5E), 2, 7, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x7E), 2, 8, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x5E), 2, 9, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x7E), 2, 10, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x5E), 2, 11, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x5E), 2, 12, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x7E), 2, 13, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x5E), 2, 14, 28, None, None, None)
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x7E), 2, 15, 28, None, None, None)

  def test_scc_pac_indent_28_underline(self):
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x5F), 1, 1, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x11, 0x7F), 1, 2, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x5F), 1, 3, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x12, 0x7F), 1, 4, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x5F), 1, 5, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x15, 0x7F), 1, 6, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x5F), 1, 7, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x16, 0x7F), 1, 8, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x5F), 1, 9, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x17, 0x7F), 1, 10, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x10, 0x5F), 1, 11, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x5F), 1, 12, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x13, 0x7F), 1, 13, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x5F), 1, 14, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x14, 0x7F), 1, 15, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x5F), 2, 1, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x19, 0x7F), 2, 2, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x5F), 2, 3, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1A, 0x7F), 2, 4, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x5F), 2, 5, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1D, 0x7F), 2, 6, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x5F), 2, 7, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1E, 0x7F), 2, 8, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x5F), 2, 9, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1F, 0x7F), 2, 10, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x18, 0x5F), 2, 11, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x5F), 2, 12, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1B, 0x7F), 2, 13, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x5F), 2, 14, 28, None, None,
                                  TextDecorationType(underline=True))
    self.check_scc_pac_attributes(SccPreambleAddressCode.find(0x1C, 0x7F), 2, 15, 28, None, None,
                                  TextDecorationType(underline=True))

  def test_ch1_values(self):
    pac = SccPreambleAddressCode(1, 1, NamedColors.white, None, False, False)
    self.assertEqual(
      pac.get_ch1_packet(),
      0x1140
    )

    pac = SccPreambleAddressCode(1, 14, NamedColors.white, 4, False, True)
    self.assertEqual(
      pac.get_ch1_packet(),
      0x1453
    )

if __name__ == '__main__':
  unittest.main()
