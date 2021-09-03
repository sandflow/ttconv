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

"""CEA-608 Standard characters"""

from __future__ import annotations

SCC_STANDARD_CHARACTERS_MAPPING = dict([
  (0x20, " "),  # Standard space
  (0x21, "!"),  # Exclamation mark
  (0x22, "``"),  # Quotation mark
  (0x23, "#"),  # Pounds (number) sign
  (0x24, "$"),  # Dollar sign
  (0x25, "%"),  # Percentage sign
  (0x26, "&"),  # Ampersand
  (0x27, "'"),  # Apostrophe
  (0x28, "("),  # Open parentheses
  (0x29, ")"),  # Close parentheses
  (0x2A, "\u00E1"),  # á Lower-case a with acute accent
  (0x2B, "+"),  # Plus sign
  (0x2C, ","),  # Comma
  (0x2D, "-"),  # Minus (hyphen) sign
  (0x2E, "."),  # Period
  (0x2F, "/"),  # Slash
  (0x30, "0"),  # Zero
  (0x31, "1"),  # One
  (0x32, "2"),  # Two
  (0x33, "3"),  # Three
  (0x34, "4"),  # Four
  (0x35, "5"),  # Five
  (0x36, "6"),  # Six
  (0x37, "7"),  # Seven
  (0x38, "8"),  # Eight
  (0x39, "9"),  # Nine
  (0x3A, ":"),  # Colon
  (0x3B, ";"),  # Semi-colon
  (0x3C, "<"),  # Less than sign
  (0x3D, "="),  # Equal sign
  (0x3E, ">"),  # Greater than sign
  (0x3F, "?"),  # Question mark
  (0x40, "@"),  # At sign
  (0x41, "A"),  # Upper-case A
  (0x42, "B"),  # Upper-case B
  (0x43, "C"),  # Upper-case C
  (0x44, "D"),  # Upper-case D
  (0x45, "E"),  # Upper-case E
  (0x46, "F"),  # Upper-case F
  (0x47, "G"),  # Upper-case G
  (0x48, "H"),  # Upper-case H
  (0x49, "I"),  # Upper-case I
  (0x4A, "J"),  # Upper-case J
  (0x4B, "K"),  # Upper-case K
  (0x4C, "L"),  # Upper-case L
  (0x4D, "M"),  # Upper-case M
  (0x4E, "N"),  # Upper-case N
  (0x4F, "O"),  # Upper-case O
  (0x50, "P"),  # Upper-case P
  (0x51, "Q"),  # Upper-case Q
  (0x52, "R"),  # Upper-case R
  (0x53, "S"),  # Upper-case S
  (0x54, "T"),  # Upper-case T
  (0x55, "U"),  # Upper-case U
  (0x56, "V"),  # Upper-case V
  (0x57, "W"),  # Upper-case W
  (0x58, "X"),  # Upper-case X
  (0x59, "Y"),  # Upper-case Y
  (0x5A, "Z"),  # Upper-case Z
  (0x5B, "["),  # Open bracket
  (0x5C, "\u00E9"),  # é Lower-case e with acute accent
  (0x5D, "]"),  # Close bracket
  (0x5E, "\u00ED"),  # í Lower-case i with acute accent
  (0x5F, "\u00F3"),  # ó Lower-case o with acute accent
  (0x60, "\u00FA"),  # ú Lower-case u with acute accent
  (0x61, "a"),  # Lower-case a
  (0x62, "b"),  # Lower-case b
  (0x63, "c"),  # Lower-case c
  (0x64, "d"),  # Lower-case d
  (0x65, "e"),  # Lower-case e
  (0x66, "f"),  # Lower-case f
  (0x67, "g"),  # Lower-case g
  (0x68, "h"),  # Lower-case h
  (0x69, "i"),  # Lower-case i
  (0x6A, "j"),  # Lower-case j
  (0x6B, "k"),  # Lower-case k
  (0x6C, "l"),  # Lower-case l
  (0x6D, "m"),  # Lower-case m
  (0x6E, "n"),  # Lower-case n
  (0x6F, "o"),  # Lower-case o
  (0x70, "p"),  # Lower-case p
  (0x71, "q"),  # Lower-case q
  (0x72, "r"),  # Lower-case r
  (0x73, "s"),  # Lower-case s
  (0x74, "t"),  # Lower-case t
  (0x75, "u"),  # Lower-case u
  (0x76, "v"),  # Lower-case v
  (0x77, "w"),  # Lower-case w
  (0x78, "x"),  # Lower-case x
  (0x79, "y"),  # Lower-case y
  (0x7A, "z"),  # Lower-case z
  (0x7B, "\u00E7"),  # ç Lower-case c with cedilla
  (0x7C, "\u00F7"),  # ÷ Division sign
  (0x7D, "\u00D1"),  # Ñ Upper-case N with tilde
  (0x7E, "\u00F1"),  # ñ Lower-case n with tilde
  (0x7F, "\u2588"),  # █ Solid block
])
