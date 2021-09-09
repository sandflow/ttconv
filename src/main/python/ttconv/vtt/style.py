#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2021, Sandflow Consulting LLC
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

"""VTT style"""

from typing import Dict, Optional

from ttconv.model import ContentElement
from ttconv.style_properties import FontWeightType, StyleProperties, FontStyleType, TextDecorationType

BOLD_TAG_IN = "<b>"
BOLD_TAG_OUT = "</b>"

ITALIC_TAG_IN = "<i>"
ITALIC_TAG_OUT = "</i>"

UNDERLINE_TAG_IN = "<u>"
UNDERLINE_TAG_OUT = "</u>"

COLOR_TAG_IN = "<c.{}>"
COLOR_TAG_OUT = "</c>"

BG_COLOR_TAG_IN = "<c.{}>"
BG_COLOR_TAG_OUT = "</c>"

DEFAULT_TEXT_COLORS: Dict[str, str] = {
  "#ffffffff": "white",
  "#00ff00ff": "lime",
  "#00ffffff": "cyan",
  "#ff0000ff": "red",
  "#ffff00ff": "yellow",
  "#ff00ffff": "magenta",
  "#0000ffff": "blue",
  "#000000ff": "black"
}

DEFAULT_BACKGROUND_COLORS: Dict[str, str] = {
  "#ffffffff": "bg_white",
  "#00ff00ff": "bg_lime",
  "#00ffffff": "bg_cyan",
  "#ff0000ff": "bg_red",
  "#ffff00ff": "bg_yellow",
  "#ff00ffff": "bg_magenta",
  "#0000ffff": "bg_blue",
  "#000000ff": "bg_black"
}

def is_element_bold(element: ContentElement) -> bool:
  """Returns whether the element text is bold"""
  font_weight: Optional[FontWeightType] = element.get_style(StyleProperties.FontWeight)
  return font_weight is not None and font_weight is FontWeightType.bold


def is_element_italic(element: ContentElement) -> bool:
  """Returns whether the element text is italic"""
  font_style: Optional[FontStyleType] = element.get_style(StyleProperties.FontStyle)
  return font_style is not None and font_style is FontStyleType.italic


def is_element_underlined(element: ContentElement) -> bool:
  """Returns whether the element text is underlined"""
  text_decoration: Optional[TextDecorationType] = element.get_style(StyleProperties.TextDecoration)
  return text_decoration is not None and text_decoration.underline is True


def get_color(element: ContentElement) -> Optional[str]:
  """Returns the text color hex code if present"""
  color = element.get_style(StyleProperties.Color)

  if color is None:
    return None

  (r, g, b, a) = color.components
  return "#{:02x}{:02x}{:02x}{:02x}".format(r, g, b, a)

def get_background_color(element: ContentElement) -> Optional[str]:
  """Returns the background color hex code"""
  background_color = element.get_style(StyleProperties.BackgroundColor)
  
  if background_color is None:
    return None

  (r, g, b, a) = background_color.components
  return "#{:02x}{:02x}{:02x}{:02x}".format(r, g, b, a)
  

def get_color_classname(color_value: str):
  """Returns CSS color classname"""

  if DEFAULT_TEXT_COLORS.get(color_value) is not None:
    return DEFAULT_TEXT_COLORS.get(color_value)

  return f'fg_color_{color_value[1:]}'

def get_background_color_classname(color_value: str):
  """Returns CSS background color classname"""

  if DEFAULT_BACKGROUND_COLORS.get(color_value) is not None:
    return DEFAULT_BACKGROUND_COLORS.get(color_value)

  return f'bg_color_{color_value[1:]}'
