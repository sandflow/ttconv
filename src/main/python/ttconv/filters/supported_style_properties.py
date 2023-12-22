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

"""Filters style properties"""

import logging
from typing import Dict, List, Type

from ttconv.model import ContentDocument, ContentElement
from ttconv.style_properties import StyleProperty

class SupportedStylePropertiesFilter:
  """Filter that removes unsupported style properties"""

  def __init__(self, supported_style_properties: Dict[Type[StyleProperty], List]):
    self.supported_style_properties = supported_style_properties

  def process_initial_values(self, doc: ContentDocument):
    """Removes initial values that target unsupported style properties"""
    for style_prop, value in list(doc.iter_initial_values()):

      if style_prop in self.supported_style_properties:
        supported_values = self.supported_style_properties[style_prop]

        if len(supported_values) == 0 or value in supported_values:
          continue

      doc.put_initial_value(style_prop, None)

  def process_element(self, element: ContentElement, recursive = True):
    """Removes unsupported style properties from content elements"""

    for style_prop in list(element.iter_styles()):

      if style_prop in self.supported_style_properties:
        value = element.get_style(style_prop)
        supported_values = self.supported_style_properties[style_prop]

        if len(supported_values) == 0 or value in supported_values:
          continue

      element.set_style(style_prop, None)

    if recursive:
      for child in element:
        self.process_element(child)