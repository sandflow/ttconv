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

"""SRT writer"""

import logging

import ttconv.model as model
import ttconv.srt.style as style
from ttconv.srt.time_code import SrtTimeCode

LOGGER = logging.getLogger(__name__)


class SrtContext:
  """SRT writer context"""

  def __init__(self):
    self._captions_counter: int = 0
    self._content: str = ""

  def get_content(self) -> str:
    """Returns SRT content"""
    return self._content

  def write_element(self, element: model.ContentElement):
    """Converts model element to SRT content"""
    if isinstance(element, model.Div):
      for elem in list(element):
        self.write_element(elem)

    if isinstance(element, model.P):

      if self._captions_counter > 0:
        self._content += "\n\n"

      begin = element.get_begin()
      end = element.get_end()

      if begin is None:
        if self._captions_counter > 0:
          raise ValueError("No begin time for paragraph:", element)
        begin = 0.0

      if end is None:
        raise ValueError("No end time for paragraph:", element)

      self._captions_counter += 1

      self._content += str(self._captions_counter) + "\n"
      self._content += str(SrtTimeCode.from_time_offset(begin)) + " --> " + str(SrtTimeCode.from_time_offset(end)) + "\n"

      for elem in list(element):
        self.write_element(elem)

    if isinstance(element, model.Span):
      is_bold = style.is_element_bold(element)
      is_italic = style.is_element_italic(element)
      is_underlined = style.is_element_underlined(element)
      font_color = style.get_font_color(element)

      if font_color is not None:
        self._content += style.FONT_COLOR_TAG_IN.format(font_color)

      if is_bold:
        self._content += style.BOLD_TAG_IN
      if is_italic:
        self._content += style.ITALIC_TAG_IN
      if is_underlined:
        self._content += style.UNDERLINE_TAG_IN

      for elem in list(element):
        self.write_element(elem)

      if is_underlined:
        self._content += style.UNDERLINE_TAG_OUT
      if is_italic:
        self._content += style.ITALIC_TAG_OUT
      if is_bold:
        self._content += style.BOLD_TAG_OUT
      if font_color is not None:
        self._content += style.FONT_COLOR_TAG_OUT

    if isinstance(element, model.Br):
      self._content += "\n"

    if isinstance(element, model.Text):
      self._content += element.get_text()

    # TODO: handle element alignment
    # TODO: handle region style


#
# srt writer
#

def from_model(model_doc: model.Document) -> str:
  """Converts the data model to a SRT document"""
  body = model_doc.get_body()

  context = SrtContext()
  for div in list(body):
    context.write_element(div)

  return context.get_content()
