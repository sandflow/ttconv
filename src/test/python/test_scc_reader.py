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

"""Unit tests for the SCC reader"""

# pylint: disable=R0201,C0115,C0116,W0212

import unittest
from ttconv.scc import scc_reader


class SCCReaderTest(unittest.TestCase):

  def test_scc_is_hex_word(self):
    self.assertTrue(scc_reader._is_hex_word("0000"))
    self.assertTrue(scc_reader._is_hex_word("FFFF"))
    self.assertFalse(scc_reader._is_hex_word("000"))
    self.assertFalse(scc_reader._is_hex_word("12345"))
    self.assertFalse(scc_reader._is_hex_word("GHIJ"))

  def test_scc_decipher_parity_bit(self):
    self.assertEqual(0b00000000, scc_reader._decipher_parity_bit(0b10000000))
    self.assertEqual(0b00000010, scc_reader._decipher_parity_bit(0b00000010))
    self.assertEqual(0b00001010, scc_reader._decipher_parity_bit(0b10001010))

  def test_decipher_hex_word(self):
    self.assertEqual((0x00, 0x00, 0x0000), scc_reader._decipher_hex_word("0000"))
    self.assertEqual((0x1a, 0x2b, 0x1a2b), scc_reader._decipher_hex_word("1a2b"))
    self.assertEqual((0x7f, 0x7f, 0x7f7f), scc_reader._decipher_hex_word("ffff"))

    self.assertRaises(ValueError, scc_reader._decipher_hex_word, "ttml")
    self.assertRaises(ValueError, scc_reader._decipher_hex_word, "Hello")

  def test_word_to_chars(self):
    self.assertEqual(['\x12', '\x34'], scc_reader._word_to_chars(0x1234))
    self.assertEqual(['\xff', '\x00'], scc_reader._word_to_chars(0xFF00))
    self.assertEqual(['\x00', '\x01'], scc_reader._word_to_chars(0x01))

    self.assertRaises(ValueError, scc_reader._word_to_chars, 0x01020304)

  def test_scc_text_content(self):
    scc_content = """Scenarist_SCC V1.0

01:02:53:14	94ae 94ae 9420 9420 947a 947a 97a2 97a2 a820 68ef f26e 2068 ef6e 6be9 6e67 2029 942c 942c 8080 8080 942f 942f

01:02:55:14	942c 942c

01:03:27:29	94ae 94ae 9420 9420 94f2 94f2 c845 d92c 2054 c845 5245 ae80 942c 942c 8080 8080 942f 942f

00:01:14:20	9425 9425 94ad 94ad 9470 9470 d94f d552 20d0 4cc1 4345 2054 4f20 4c45 c152 ce20 c1ce c420 54c1 4ccb
"""

    doc = scc_reader.to_model(scc_content)
    self.assertIsNotNone(doc)

    body = doc.get_body()
    self.assertIsNotNone(doc)

    div_list = list(body)
    self.assertEqual(1, len(div_list))
    div = div_list[0]
    self.assertIsNotNone(div)

    p_list = list(div)
    self.assertEqual(4, len(p_list))
    count = 1
    for p in div:
      self.assertIsNotNone(p)
      self.assertEqual("caption" + str(count), p.get_id())
      count += 1


if __name__ == '__main__':
  unittest.main()
