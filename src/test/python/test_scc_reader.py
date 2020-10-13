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

from ttconv.model import Br
from ttconv.scc.scc_reader import SccWord, SccLine, to_model
from ttconv.scc.time_codes import SccTimeCode
from ttconv.style_properties import StyleProperties, PositionType, LengthType, FontStyleType, NamedColors


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


class SccLineTest(unittest.TestCase):

  def test_scc_line_from_str(self):
    line_str = "01:03:27:29	94ae 94ae 9420 9420 94f2 94f2 c845 d92c 2054 c845 5245 ae80 942c 942c 8080 8080 942f 942f"
    scc_line = SccLine.from_str(line_str)
    self.assertEqual(18, len(scc_line.scc_words))
    self.assertEqual(SccTimeCode(1, 3, 27, 29).to_temporal_offset(), scc_line.time_code.to_temporal_offset())

    self.assertIsNone(SccLine.from_str(""))
    self.assertIsNone(SccLine.from_str("Hello world!"))


class SCCReaderTest(unittest.TestCase):

  def test_scc_pop_on_content(self):
    scc_content = """Scenarist_SCC V1.0

01:02:53:14	94ae 94ae 9420 9420 947a 947a 97a2 97a2 a820 68ef f26e 2068 ef6e 6be9 6e67 2029 942c 942c 8080 8080 942f 942f

01:02:55:14	942c 942c

01:03:27:29	94ae 94ae 9420 9420 94f2 94f2 c845 d92c 2054 c845 91b0 45ae 942c 942c 8080 8080 942f 942f

01:11:31:01	9420 9420 9452 9452 97a1 97a1 54e5 73f4 2080 9132 2043 6170 f4e9 ef6e 2080 94f2 94f2 97a1 97a1 54e5 73f4 2080 91ae 91ae f4e5 73f4 9120 9120 2043 6170 f4e9 ef6e 7380 942c 942c 942f 942f

01:11:33:14	942c 942c
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

    caption1 = p_list[0]
    self.assertEqual("caption1", caption1.get_id())
    self.assertEqual(SccTimeCode.parse("01:02:54:00").to_temporal_offset(), caption1.get_begin())
    self.assertEqual(SccTimeCode.parse("01:02:55:15").to_temporal_offset(), caption1.get_end())

    caption_children = list(caption1)
    self.assertEqual(1, len(caption_children))

    expected_origin = PositionType(x=LengthType(value=26, units=LengthType.Units.c),
                                   y=LengthType(value=17, units=LengthType.Units.c))
    self.assertEqual(expected_origin, caption_children[0].get_style(StyleProperties.Origin))
    texts = list(caption_children[0])
    self.assertEqual("( horn honking )", texts[0].get_text())

    caption2 = p_list[1]
    self.assertEqual("caption2", caption2.get_id())
    self.assertEqual(SccTimeCode.parse("01:03:28:12").to_temporal_offset(), caption2.get_begin())
    self.assertEqual(SccTimeCode.parse("01:11:31:28").to_temporal_offset(), caption2.get_end())

    caption_children = list(caption2)
    self.assertEqual(1, len(caption_children))

    expected_origin = PositionType(x=LengthType(value=8, units=LengthType.Units.c),
                                   y=LengthType(value=17, units=LengthType.Units.c))
    self.assertEqual(expected_origin, caption_children[0].get_style(StyleProperties.Origin))
    texts = list(caption_children[0])
    self.assertEqual("HEY, THE®E.", texts[0].get_text())

    caption3 = p_list[2]
    self.assertEqual("caption3", caption3.get_id())
    self.assertEqual(SccTimeCode.parse("01:11:31:29").to_temporal_offset(), caption3.get_begin())
    self.assertEqual(SccTimeCode.parse("01:11:33:15").to_temporal_offset(), caption3.get_end())

    caption_children = list(caption3)
    self.assertEqual(5, len(caption_children))

    expected_origin = PositionType(x=LengthType(value=9, units=LengthType.Units.c),
                                   y=LengthType(value=16, units=LengthType.Units.c))
    child = caption_children[0]
    self.assertEqual(expected_origin, child.get_style(StyleProperties.Origin))
    texts = list(child)
    self.assertEqual(1, len(texts))
    self.assertEqual("Test ½ Caption ", texts[0].get_text())

    child = caption_children[1]
    self.assertIsInstance(child, Br)

    child = caption_children[2]
    expected_origin = PositionType(x=LengthType(value=9, units=LengthType.Units.c),
                                   y=LengthType(value=17, units=LengthType.Units.c))
    self.assertEqual(expected_origin, child.get_style(StyleProperties.Origin))
    texts = list(child)
    self.assertEqual("Test ", texts[0].get_text())

    child = caption_children[3]
    expected_origin = PositionType(x=LengthType(value=9, units=LengthType.Units.c),
                                   y=LengthType(value=17, units=LengthType.Units.c))
    self.assertEqual(expected_origin, child.get_style(StyleProperties.Origin))
    self.assertEqual(FontStyleType.italic, child.get_style(StyleProperties.FontStyle))
    texts = list(child)
    self.assertEqual("test", texts[0].get_text())

    child = caption_children[4]
    expected_origin = PositionType(x=LengthType(value=9, units=LengthType.Units.c),
                                   y=LengthType(value=17, units=LengthType.Units.c))
    self.assertEqual(expected_origin, child.get_style(StyleProperties.Origin))
    self.assertIsNone(child.get_style(StyleProperties.FontStyle))
    self.assertEqual(NamedColors.white.value, child.get_style(StyleProperties.Color))
    texts = list(child)
    self.assertEqual(" Captions", texts[0].get_text())


  def test_roll_up_content(self):
    scc_content = """Scenarist_SCC V1.0

00:00:00;22	9425 9425 94ad 94ad 9470 9470 3e3e 3e20 c849 ae80

00:00:02;23	9425 9425 94ad 94ad 9470 9470 49a7 cd20 cb45 d649 ce20 43d5 cece 49ce c720 c1ce c420 c154

00:00:04;17	9425 9425 94ad 94ad 9470 9470 49ce d645 d354 4f52 a7d3 20c2 c1ce cb20 5745 20c2 454c 4945 d645 2049 ce80

00:00:06;04	9425 9425 94ad 94ad 9470 9470 c845 4cd0 49ce c720 54c8 4520 4c4f 43c1 4c20 ce45 49c7 c8c2 4f52 c84f 4fc4 d380

00:00:09;21	9425 9425 94ad 94ad 9470 9470 c1ce c420 91ae 91ae 49cd d052 4fd6 49ce c720 9120 9120 54c8 4520 4c49 d645 d320 4f46 20c1 4c4c

00:00:11;07	9425 9425 94ad 94ad 9470 9470 5745 20d3 4552 d645 ae80

00:00:12;07	9425 9425 94ad 94ad 9470 9470 91b0 9131 9132 9132

00:00:13;07	9425 9425 94ad 94ad 9470 9470 c1c2 c3c4 c580 91bf

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
    self.assertEqual(8, len(p_list))

    p = p_list[0]
    self.assertEqual("caption1", p.get_id())
    self.assertEqual(SccTimeCode.parse("00:00:00;23").to_temporal_offset(), p.get_begin())
    self.assertEqual(SccTimeCode.parse("00:00:02;24").to_temporal_offset(), p.get_end())

    p_children = list(p)
    self.assertEqual(1, len(p_children))
    texts = list(p_children[0])
    self.assertEqual(">>> HI.", texts[0].get_text())

    p = p_list[1]
    self.assertEqual("caption2", p.get_id())
    self.assertEqual(SccTimeCode.parse("00:00:02;24").to_temporal_offset(), p.get_begin())
    self.assertEqual(SccTimeCode.parse("00:00:04;18").to_temporal_offset(), p.get_end())

    p_children = list(p)
    self.assertEqual(3, len(p_children))
    texts = list(p_children[0])
    self.assertEqual(">>> HI.", texts[0].get_text())
    self.assertIsInstance(p_children[1], Br)
    texts = list(p_children[2])
    self.assertEqual("I'M KEVIN CUNNING AND AT", texts[0].get_text())

    p = p_list[2]
    self.assertEqual("caption3", p.get_id())
    self.assertEqual(SccTimeCode.parse("00:00:04;18").to_temporal_offset(), p.get_begin())
    self.assertEqual(SccTimeCode.parse("00:00:06;05").to_temporal_offset(), p.get_end())

    p_children = list(p)
    self.assertEqual(3, len(p_children))
    texts = list(p_children[0])
    self.assertEqual("I'M KEVIN CUNNING AND AT", texts[0].get_text())
    self.assertIsInstance(p_children[1], Br)
    texts = list(p_children[2])
    self.assertEqual("INVESTOR'S BANK WE BELIEVE IN", texts[0].get_text())

    p = p_list[3]
    self.assertEqual("caption4", p.get_id())
    self.assertEqual(SccTimeCode.parse("00:00:06;05").to_temporal_offset(), p.get_begin())
    self.assertEqual(SccTimeCode.parse("00:00:09;22").to_temporal_offset(), p.get_end())

    p_children = list(p)
    self.assertEqual(3, len(p_children))
    texts = list(p_children[0])
    self.assertEqual("INVESTOR'S BANK WE BELIEVE IN", texts[0].get_text())
    self.assertIsInstance(p_children[1], Br)
    texts = list(p_children[2])
    self.assertEqual("HELPING THE LOCAL NEIGHBORHOODS", texts[0].get_text())

    p = p_list[4]
    self.assertEqual("caption5", p.get_id())
    self.assertEqual(SccTimeCode.parse("00:00:09;22").to_temporal_offset(), p.get_begin())
    self.assertEqual(SccTimeCode.parse("00:00:11;08").to_temporal_offset(), p.get_end())

    p_children = list(p)
    self.assertEqual(5, len(p_children))
    texts = list(p_children[0])
    self.assertEqual("HELPING THE LOCAL NEIGHBORHOODS", texts[0].get_text())
    self.assertIsInstance(p_children[1], Br)
    texts = list(p_children[2])
    self.assertEqual("AND ", texts[0].get_text())
    texts = list(p_children[3])
    self.assertEqual("IMPROVING ", texts[0].get_text())
    texts = list(p_children[4])
    self.assertEqual("THE LIVES OF ALL", texts[0].get_text())

    p = p_list[5]
    self.assertEqual("caption6", p.get_id())
    self.assertEqual(SccTimeCode.parse("00:00:11;08").to_temporal_offset(), p.get_begin())
    self.assertEqual(SccTimeCode.parse("00:00:12;08").to_temporal_offset(), p.get_end())

    p_children = list(p)
    self.assertEqual(5, len(p_children))
    texts = list(p_children[0])
    self.assertEqual("AND ", texts[0].get_text())
    texts = list(p_children[1])
    self.assertEqual("IMPROVING ", texts[0].get_text())
    texts = list(p_children[2])
    self.assertEqual("THE LIVES OF ALL", texts[0].get_text())
    self.assertIsInstance(p_children[3], Br)
    texts = list(p_children[4])
    self.assertEqual("WE SERVE.", texts[0].get_text())

    p = p_list[6]
    self.assertEqual("caption7", p.get_id())
    self.assertEqual(SccTimeCode.parse("00:00:12;08").to_temporal_offset(), p.get_begin())
    self.assertEqual(SccTimeCode.parse("00:00:13;08").to_temporal_offset(), p.get_end())

    p_children = list(p)
    self.assertEqual(3, len(p_children))
    texts = list(p_children[0])
    self.assertEqual("WE SERVE.", texts[0].get_text())
    self.assertIsInstance(p_children[1], Br)
    texts = list(p_children[2])
    self.assertEqual("®°½", texts[0].get_text())

    p = p_list[7]
    self.assertEqual("caption8", p.get_id())
    self.assertEqual(SccTimeCode.parse("00:00:13;08").to_temporal_offset(), p.get_begin())
    self.assertEqual(SccTimeCode.parse("00:00:13;14").to_temporal_offset(), p.get_end())

    p_children = list(p)
    self.assertEqual(3, len(p_children))
    texts = list(p_children[0])
    self.assertEqual("®°½", texts[0].get_text())
    self.assertIsInstance(p_children[1], Br)
    texts = list(p_children[2])
    self.assertEqual("ABCDEû", texts[0].get_text())

if __name__ == '__main__':
  unittest.main()
