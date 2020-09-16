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

"""SCC Preamble Access Codes"""


class SccPreambleAccessCode:
  """SCC PAC definition"""

  def __init__(self, row, description):
    self._row = row
    self._description = description


def get_pac_row(byte_1, byte_2):
  """Decodes SCC PAC row number from specified bytes"""
  if byte_1 not in list(range(0x10, 0x20)):
    return None

  row_bits = ((byte_1 & 0x0F) % 0X08, byte_2 & 0x60)

  if row_bits == (0x01, 0x40):
    return 1
  if row_bits == (0x01, 0x60):
    return 2
  if row_bits == (0x02, 0x40):
    return 3
  if row_bits == (0x02, 0x60):
    return 4
  if row_bits == (0x05, 0x40):
    return 5
  if row_bits == (0x05, 0x60):
    return 6
  if row_bits == (0x06, 0x40):
    return 7
  if row_bits == (0x06, 0x60):
    return 8
  if row_bits == (0x07, 0x40):
    return 9
  if row_bits == (0x07, 0x60):
    return 10
  if row_bits == (0x00, 0x40):
    return 11
  if row_bits == (0x03, 0x40):
    return 12
  if row_bits == (0x03, 0x60):
    return 13
  if row_bits == (0x04, 0x40):
    return 14
  if row_bits == (0x04, 0x60):
    return 15

  return None


def get_pac_description(byte_2):
  """Decodes SCC PAC description from specified bytes"""
  if byte_2 not in list(range(0x40, 0x80)):
    return None

  desc_bits = byte_2 & 0x1F

  if desc_bits == 0x00:
    return "White"
  if desc_bits == 0x01:
    return "White Underline"
  if desc_bits == 0x02:
    return "Green"
  if desc_bits == 0x03:
    return "Green Underline"
  if desc_bits == 0x04:
    return "Blue"
  if desc_bits == 0x05:
    return "Blue Underline"
  if desc_bits == 0x06:
    return "Cyan"
  if desc_bits == 0x07:
    return "Cyan Underline"
  if desc_bits == 0x08:
    return "Red"
  if desc_bits == 0x09:
    return "Red Underline"
  if desc_bits == 0x0A:
    return "Yellow"
  if desc_bits == 0x0B:
    return "Yellow Underline"
  if desc_bits == 0x0C:
    return "Magenta"
  if desc_bits == 0x0D:
    return "Magenta Underline"
  if desc_bits == 0x0E:
    return "White Italics"
  if desc_bits == 0x0F:
    return "White Italics Underline"
  if desc_bits == 0x10:
    return "White Indent 0"
  if desc_bits == 0x11:
    return "White Indent 0 Underline"
  if desc_bits == 0x12:
    return "White Indent 4"
  if desc_bits == 0x13:
    return "White Indent 4 Underline"
  if desc_bits == 0x14:
    return "White Indent 8"
  if desc_bits == 0x15:
    return "White Indent 8 Underline"
  if desc_bits == 0x16:
    return "White Indent 12"
  if desc_bits == 0x17:
    return "White Indent 12 Underline"
  if desc_bits == 0x18:
    return "White Indent 16"
  if desc_bits == 0x19:
    return "White Indent 16 Underline"
  if desc_bits == 0x1A:
    return "White Indent 20"
  if desc_bits == 0x1B:
    return "White Indent 20 Underline"
  if desc_bits == 0x1C:
    return "White Indent 24"
  if desc_bits == 0x1D:
    return "White Indent 24 Underline"
  if desc_bits == 0x1E:
    return "White Indent 28"
  if desc_bits == 0x1F:
    return "White Indent 28 Underline"

  return None


def get_pac(byte_1, byte_2):
  """Decodes SCC PAC from specified bytes"""
  row = get_pac_row(byte_1, byte_2)
  description = get_pac_description(byte_2)

  if row and description:
    return SccPreambleAccessCode(row, description)
  return None
