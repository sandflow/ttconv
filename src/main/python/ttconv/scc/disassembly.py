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

"""SCC disassembly functions"""
import logging

from ttconv.scc.codes.attribute_codes import SccAttributeCode
from ttconv.scc.codes.control_codes import SccControlCode
from ttconv.scc.codes.extended_characters import SccExtendedCharacter
from ttconv.scc.codes.mid_row_codes import SccMidRowCode
from ttconv.scc.codes.preambles_address_codes import SccPreambleAddressCode
from ttconv.scc.codes.special_characters import SccSpecialCharacter
from ttconv.scc.word import SccWord
from ttconv.style_properties import ColorType, NamedColors, FontStyleType, TextDecorationType

LOGGER = logging.getLogger(__name__)


def get_color_disassembly(color: ColorType) -> str:
  """Get color disassembly code"""
  disassembly = ""

  if color is None:
    return disassembly

  rgb_color = color.components[:-1]
  if rgb_color == NamedColors.white.value.components[:-1]:
    disassembly = "Wh"
  elif rgb_color == NamedColors.green.value.components[:-1]:
    disassembly = "Gr"
  elif rgb_color == NamedColors.blue.value.components[:-1]:
    disassembly = "Bl"
  elif rgb_color == NamedColors.cyan.value.components[:-1]:
    disassembly = "Cy"
  elif rgb_color == NamedColors.red.value.components[:-1]:
    disassembly = "R"
  elif rgb_color == NamedColors.yellow.value.components[:-1]:
    disassembly = "Y"
  elif rgb_color == NamedColors.magenta.value.components[:-1]:
    disassembly = "Ma"
  elif rgb_color == NamedColors.black.value.components[:-1]:
    disassembly = "Bk"

  # Alpha channel
  if color.components[3] == 0:
    disassembly = "T"
  elif color.components[3] == 0x88:
    disassembly += "S"
  elif color.components[3] != 0xFF:
    LOGGER.warning("Skip unsupported %s alpha level in disassembly format.", color.components[3])

  if not disassembly:
    LOGGER.warning("Unsupported '%s' color in disassembly format.", color.components)

  return disassembly


def get_font_style_disassembly(font_style: FontStyleType) -> str:
  """Get font style disassembly code"""
  if font_style is FontStyleType.italic:
    return "I"
  return ""


def get_text_decoration_disassembly(text_decoration: TextDecorationType) -> str:
  """Get text decoration disassembly code"""
  if text_decoration is not None and text_decoration.underline is True:
    return "U"
  return ""


def get_scc_word_disassembly(scc_word: SccWord, show_channel = False) -> str:
  """Returns the disassembly code for specified SCC word"""
  if scc_word.value == 0x0000:
    return "{}"

  if scc_word.byte_1 < 0x20:

    pac = SccPreambleAddressCode.find(scc_word.byte_1, scc_word.byte_2)

    if pac is not None:
      disassembly_code = "{"
      if show_channel:
        disassembly_code += str(pac.get_channel()) + "|"
      disassembly_code += f"{pac.get_row():02}"
      color = pac.get_color()
      indent = pac.get_indent()
      if indent is not None and indent > 0:
        disassembly_code += f"{indent :02}"
      elif color is not None:
        disassembly_code += get_color_disassembly(color)
        disassembly_code += get_font_style_disassembly(pac.get_font_style())
        disassembly_code += get_text_decoration_disassembly(pac.get_text_decoration())
      else:
        disassembly_code += "00"
      disassembly_code += "}"
      return disassembly_code

    attribute_code = SccAttributeCode.find(scc_word.value)

    if attribute_code is not None:
      disassembly_code = "{"
      if show_channel:
        disassembly_code += str(attribute_code.get_channel(scc_word.value)) + "|"
      disassembly_code += "B" if attribute_code.is_background() else ""
      disassembly_code += get_color_disassembly(attribute_code.get_color())
      disassembly_code += get_text_decoration_disassembly(attribute_code.get_text_decoration())
      disassembly_code += "}"
      return disassembly_code

    mid_row_code = SccMidRowCode.find(scc_word.value)

    if mid_row_code is not None:
      disassembly_code = "{"
      if show_channel:
        disassembly_code += str(mid_row_code.get_channel(scc_word.value)) + "|"
      disassembly_code += get_color_disassembly(mid_row_code.get_color())
      disassembly_code += get_font_style_disassembly(mid_row_code.get_font_style())
      disassembly_code += get_text_decoration_disassembly(mid_row_code.get_text_decoration())
      disassembly_code += "}"
      return disassembly_code

    control_code = SccControlCode.find(scc_word.value)

    if control_code is not None:
      disassembly_code = "{"
      if show_channel:
        disassembly_code += str(control_code.get_channel(scc_word.value)) + "|"
      disassembly_code += control_code.get_name()
      disassembly_code += "}"
      return disassembly_code

    # print(f"{hex(scc_word.byte_1)}{hex(scc_word.byte_2)}")
    spec_char = SccSpecialCharacter.find(scc_word.value)

    if spec_char is not None:
      if show_channel:
        disassembly_code = "["
        disassembly_code += str(spec_char.get_channel(scc_word.value))
        disassembly_code += "]"
        disassembly_code += spec_char.get_unicode_value()
        return disassembly_code
      return spec_char.get_unicode_value()

    extended_char = SccExtendedCharacter.find(scc_word.value)

    if extended_char is not None:
      if show_channel:
        disassembly_code = "["
        disassembly_code += str(extended_char.get_channel(scc_word.value))
        disassembly_code += "]"
        disassembly_code += extended_char.get_unicode_value()
        return disassembly_code
      return extended_char.get_unicode_value()

    LOGGER.warning("Unsupported SCC word: %s", hex(scc_word.value))
    return "{??}"

  return scc_word.to_text()
