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
