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

from ttconv.style_properties import ColorType, NamedColors, FontStyleType, TextDecorationType


def get_color_disassembly(color: ColorType) -> str:
  """Get color disassembly code"""
  disassembly = ""

  if color is NamedColors.white.value:
    disassembly = "Wh"
  elif color is NamedColors.green.value:
    disassembly = "Gr"
  elif color is NamedColors.blue.value:
    disassembly = "Bl"
  elif color is NamedColors.cyan.value:
    disassembly = "Cy"
  elif color is NamedColors.red.value:
    disassembly = "R"
  elif color is NamedColors.yellow.value:
    disassembly = "Y"
  elif color is NamedColors.magenta.value:
    disassembly = "Ma"
  elif color is NamedColors.black.value:
    disassembly = "Bk"
  elif color is NamedColors.transparent.value:
    disassembly = "T"

  # Alpha channel
  if color.components[3] == 0x88:
    disassembly += "S"

  return disassembly


def get_font_style_disassembly(font_style: FontStyleType) -> str:
  """Get font style disassembly code"""
  if font_style is FontStyleType.italic:
    return "I"
  return ""


def get_text_decoration_disassembly(text_decoration: TextDecorationType) -> str:
  """Get text decoration disassembly code"""
  if text_decoration is TextDecorationType.underline:
    return "U"
  return ""
