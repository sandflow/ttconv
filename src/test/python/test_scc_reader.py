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

from ttconv.scc.scc_reader import SccWord, SccLine, to_model
from ttconv.scc.time_codes import SccTimeCode


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
    self.assertEqual('\x7f\x00', scc_word.to_text())
    scc_word = SccWord.from_value(0x01)
    self.assertEqual('\x00\x01', scc_word.to_text())

    self.assertRaises(ValueError, SccWord.from_value, 0x01020304)


class SccLineTest(unittest.TestCase):

  def test_scc_line_from_str(self):
    line_str = "01:03:27:29	94ae 94ae 9420 9420 94f2 94f2 c845 d92c 2054 c845 5245 ae80 942c 942c 8080 8080 942f 942f"
    scc_line = SccLine.from_str(line_str)
    self.assertEqual(18, len(scc_line.scc_words))
    self.assertEqual(SccTimeCode(1, 3, 27, 29).get_fraction(), scc_line.time_code.get_fraction())

    self.assertIsNone(SccLine.from_str(""))
    self.assertIsNone(SccLine.from_str("Hello world!"))


class SCCReaderTest(unittest.TestCase):

  def test_scc_text_content(self):
    scc_content = """Scenarist_SCC V1.0

01:02:53:14	94ae 94ae 9420 9420 947a 947a 97a2 97a2 a820 68ef f26e 2068 ef6e 6be9 6e67 2029 942c 942c 8080 8080 942f 942f

01:02:55:14	942c 942c

01:03:27:29	94ae 94ae 9420 9420 94f2 94f2 c845 d92c 2054 c845 5245 ae80 942c 942c 8080 8080 942f 942f

00:01:14:20	9425 9425 94ad 94ad 9470 9470 d94f d552 20d0 4cc1 4345 2054 4f20 4c45 c152 ce20 c1ce c420 54c1 4ccb
"""

    doc = to_model(scc_content)
    self.assertIsNotNone(doc)

    body = doc.get_body()
    self.assertIsNotNone(body)

    div_list = list(body)
    self.assertEqual(1, len(div_list))
    div = div_list[0]
    self.assertIsNotNone(div)

    p_list = list(div)
    self.assertEqual(3, len(p_list))

    count = 1
    for p in div:
      self.assertIsNotNone(p)
      self.assertEqual("caption" + str(count), p.get_id())
      count += 1


if __name__ == '__main__':
  unittest.main()
