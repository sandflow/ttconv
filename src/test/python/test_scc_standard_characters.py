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

"""Unit tests for the SCC Standard characters mapping"""

# pylint: disable=R0201,C0115,C0116,W0212

import unittest

from ttconv.scc.codes.characters import unicode_to_scc
from ttconv.scc.codes.standard_characters import SCC_STANDARD_CHARACTERS_MAPPING


class SccStandardCharactersTest(unittest.TestCase):

  def test_unicode_to_scc_standard_character(self):
    for scc_char, unicode_char in SCC_STANDARD_CHARACTERS_MAPPING.items():
      with self.subTest(unicode_char=unicode_char):
        self.assertEqual(unicode_to_scc(unicode_char)[0], scc_char)

  def test_scc_standard_character_values(self):
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x20], " ")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x21], "!")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x22], '"')
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x23], "#")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x24], "$")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x25], "%")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x26], "&")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x27], "'")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x28], "(")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x29], ")")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x2A], "á")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x2B], "+")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x2C], ",")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x2D], "-")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x2E], ".")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x2F], "/")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x30], "0")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x31], "1")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x32], "2")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x33], "3")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x34], "4")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x35], "5")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x36], "6")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x37], "7")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x38], "8")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x39], "9")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x3A], ":")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x3B], ";")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x3C], "<")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x3D], "=")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x3E], ">")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x3F], "?")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x40], "@")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x41], "A")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x42], "B")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x43], "C")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x44], "D")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x45], "E")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x46], "F")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x47], "G")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x48], "H")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x49], "I")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x4A], "J")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x4B], "K")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x4C], "L")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x4D], "M")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x4E], "N")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x4F], "O")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x50], "P")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x51], "Q")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x52], "R")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x53], "S")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x54], "T")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x55], "U")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x56], "V")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x57], "W")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x58], "X")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x59], "Y")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x5A], "Z")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x5B], "[")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x5C], "é")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x5D], "]")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x5E], "í")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x5F], "ó")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x60], "ú")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x61], "a")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x62], "b")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x63], "c")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x64], "d")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x65], "e")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x66], "f")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x67], "g")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x68], "h")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x69], "i")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x6A], "j")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x6B], "k")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x6C], "l")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x6D], "m")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x6E], "n")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x6F], "o")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x70], "p")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x71], "q")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x72], "r")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x73], "s")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x74], "t")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x75], "u")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x76], "v")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x77], "w")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x78], "x")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x79], "y")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x7A], "z")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x7B], "ç")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x7C], "÷")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x7D], "Ñ")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x7E], "ñ")
    self.assertEqual(SCC_STANDARD_CHARACTERS_MAPPING[0x7F], "█")
