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

"""SCC reader"""

import re
import logging
from typing import List
from ttconv.model import Document, P, Body, Div
from ttconv.scc import time_codes

LOGGER = logging.getLogger(__name__)

SCC_LINE_PATTERN = '((' + time_codes.SMPTE_TIME_CODE_NDF_PATTERN \
                   + ')|(' + time_codes.SMPTE_TIME_CODE_DF_PATTERN + '))\t.*'

PARITY_BIT_MASK = 0b01111111


class _SccContext:
  def __init__(self):
    self.div = None
    self.count = 0


def _is_hex_word(word: str) -> bool:
  """Checks whether the specified word is a 2-bytes hexadecimal word"""
  if len(word) != 4:
    return False
  try:
    int(word, 16)
  except ValueError:
    return False
  return True


def _decipher_parity_bit(byte: int):
  """Extracts the byte value removing the odd parity bit"""
  return byte & PARITY_BIT_MASK


def _decipher_hex_word(hex_word) -> (int, int, int):
  """
  Extracts hexadecimal word bytes and returns the value of each byte
  and the value of the whole word as a tuple
  """
  if not _is_hex_word(hex_word):
    raise ValueError("Expected a 2-bytes hexadecimal word, instead got ", hex_word)

  data = bytes.fromhex(hex_word)
  byte_1 = _decipher_parity_bit(data[0])
  byte_2 = _decipher_parity_bit(data[1])
  word_value = byte_1 * 0x100 + byte_2

  return byte_1, byte_2, word_value


def _word_to_chars(word_value: int) -> List[chr]:
  """Converts a word value to a char array"""
  if word_value > 0xFFFF:
    raise ValueError("Expected a 2-bytes integer value, instead got ", word_value)

  chars = word_value.to_bytes(2, byteorder='big')
  return [chr(chars[0]), chr(chars[1])]


def _read_word(hex_word: str) -> List[chr]:
  """Reads the SCC hexadecimal word content"""
  if hex_word == "":
    return []

  (byte_1, _byte_2, word_value) = _decipher_hex_word(hex_word)

  if byte_1 < 0x20:
    # XXXX: handle control codes
    return []
  else:
    return _word_to_chars(word_value)


def _read_line(context: _SccContext, line: str):
  """Reads the SCC line content"""
  if line == '':
    return
  chars = []

  regex = re.compile(SCC_LINE_PATTERN)
  match = regex.match(line)

  if match:
    paragraph = P()
    context.count += 1
    paragraph.set_id("caption" + str(context.count))

    time_code = match.group(1)
    time_offset = time_codes.parse(time_code)
    paragraph.set_begin(time_offset)

    hex_words = line.split('\t')[1].split(' ')
    for hex_word in hex_words:
      chars += _read_word(hex_word)

    paragraph.set_doc(context.div.get_doc())
    context.div.push_child(paragraph)


#
# scc reader
#

def to_model(scc_content: str):
  """Converts a SCC document to the data model"""

  context = _SccContext()
  document = Document()

  body = Body()
  body.set_doc(document)
  document.set_body(body)

  context.div = Div()
  context.div.set_doc(document)
  body.push_child(context.div)

  for line in scc_content.splitlines():
    _read_line(context, line)

  return document
