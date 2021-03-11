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

"""Unit tests for the SCC words"""

# pylint: disable=R0201,C0115,C0116,W0212

import unittest

from ttconv.scc.word import SccWord


class SccWordTest(unittest.TestCase):

  def test_scc_word_is_hex_word(self):
    self.assertTrue(SccWord._is_hex_word("0000"))
    self.assertTrue(SccWord._is_hex_word("FFFF"))
    self.assertFalse(SccWord._is_hex_word("000"))
    self.assertFalse(SccWord._is_hex_word("12345"))
    self.assertFalse(SccWord._is_hex_word("GHIJ"))

  def test_scc_word_decipher_parity_bit(self):
    self.assertEqual(0b00000000, SccWord._decipher_parity_bit(0b10000000))
    self.assertEqual(0b00000010, SccWord._decipher_parity_bit(0b00000010))
    self.assertEqual(0b00001010, SccWord._decipher_parity_bit(0b10001010))

    translated_values = [
      0x80, 0x01, 0x02, 0x83, 0x04, 0x85, 0x86, 0x07, 0x08, 0x89, 0x8a, 0x0b, 0x8c, 0x0d, 0x0e, 0x8f,
      0x10, 0x91, 0x92, 0x13, 0x94, 0x15, 0x16, 0x97, 0x98, 0x19, 0x1a, 0x9b, 0x1c, 0x9d, 0x9e, 0x1f,
      0x20, 0xa1, 0xa2, 0x23, 0xa4, 0x25, 0x26, 0xa7, 0xa8, 0x29, 0x2a, 0xab, 0x2c, 0xad, 0xae, 0x2f,
      0xb0, 0x31, 0x32, 0xb3, 0x34, 0xb5, 0xb6, 0x37, 0x38, 0xb9, 0xba, 0x3b, 0xbc, 0x3d, 0x3e, 0xbf,
      0x40, 0xc1, 0xc2, 0x43, 0xc4, 0x45, 0x46, 0xc7, 0xc8, 0x49, 0x4a, 0xcb, 0x4c, 0xcd, 0xce, 0x4f,
      0xd0, 0x51, 0x52, 0xd3, 0x54, 0xd5, 0xd6, 0x57, 0x58, 0xd9, 0xda, 0x5b, 0xdc, 0x5d, 0x5e, 0xdf,
      0xe0, 0x61, 0x62, 0xe3, 0x64, 0xe5, 0xe6, 0x67, 0x68, 0xe9, 0xea, 0x6b, 0xec, 0x6d, 0x6e, 0xef,
      0x70, 0xf1, 0xf2, 0x73, 0xf4, 0x75, 0x76, 0xf7, 0xf8, 0x79, 0x7a, 0xfb, 0x7c, 0xfd, 0xfe, 0x7f
    ]

    for i in range(0x00, 0x80):
      self.assertEqual(i, SccWord._decipher_parity_bit(translated_values[i]))

  def test_scc_word_from_value(self):
    scc_word = SccWord.from_value(0x01)
    self.assertEqual((0x00, 0x01, 0x0001), (scc_word.byte_1, scc_word.byte_2, scc_word.value))
    scc_word = SccWord.from_value(0x0000)
    self.assertEqual((0x00, 0x00, 0x0000), (scc_word.byte_1, scc_word.byte_2, scc_word.value))
    scc_word = SccWord.from_value(0x1a2b)
    self.assertEqual((0x1a, 0x2b, 0x1a2b), (scc_word.byte_1, scc_word.byte_2, scc_word.value))
    scc_word = SccWord.from_value(0xffff)
    self.assertEqual((0x7f, 0x7f, 0x7f7f), (scc_word.byte_1, scc_word.byte_2, scc_word.value))

    self.assertRaises(ValueError, SccWord.from_value, 0x12345)

  def test_scc_word_from_bytes(self):
    scc_word = SccWord.from_bytes(0x00, 0x00)
    self.assertEqual((0x00, 0x00, 0x0000), (scc_word.byte_1, scc_word.byte_2, scc_word.value))
    scc_word = SccWord.from_bytes(0x1a, 0x2b)
    self.assertEqual((0x1a, 0x2b, 0x1a2b), (scc_word.byte_1, scc_word.byte_2, scc_word.value))
    scc_word = SccWord.from_bytes(0xff, 0xff)
    self.assertEqual((0x7f, 0x7f, 0x7f7f), (scc_word.byte_1, scc_word.byte_2, scc_word.value))

    self.assertRaises(ValueError, SccWord.from_bytes, 0x123, 0x45)
    self.assertRaises(ValueError, SccWord.from_bytes, 0x12, 0x345)

  def test_scc_word_from_str(self):
    scc_word = SccWord.from_str("0000")
    self.assertEqual((0x00, 0x00, 0x0000), (scc_word.byte_1, scc_word.byte_2, scc_word.value))
    scc_word = SccWord.from_str("1a2b")
    self.assertEqual((0x1a, 0x2b, 0x1a2b), (scc_word.byte_1, scc_word.byte_2, scc_word.value))
    scc_word = SccWord.from_str("ffff")
    self.assertEqual((0x7f, 0x7f, 0x7f7f), (scc_word.byte_1, scc_word.byte_2, scc_word.value))

    self.assertRaises(ValueError, SccWord.from_str, "ttml")
    self.assertRaises(ValueError, SccWord.from_str, "Hello")

  def test_scc_word_to_text(self):
    scc_word = SccWord.from_value(0x1234)
    self.assertEqual('\x12\x34', scc_word.to_text())
    scc_word = SccWord.from_value(0xFF00)
    self.assertEqual('\x7f', scc_word.to_text())
    scc_word = SccWord.from_value(0x01)
    self.assertEqual('\x01', scc_word.to_text())

    self.assertRaises(ValueError, SccWord.from_value, 0x01020304)
