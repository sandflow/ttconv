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

"""Style properties default values filter"""

import logging
from typing import Dict, Type, Any

from ttconv.filters import Filter
from ttconv.isd import ISD
from ttconv.model import ContentElement
from ttconv.style_properties import StyleProperty

LOGGER = logging.getLogger(__name__)


class DefaultStylePropertyValuesFilter(Filter):
  """Filter that remove default style properties"""

  def __init__(self, style_property_default_values: Dict[Type[StyleProperty], Any]):
    self.style_property_default_values = style_property_default_values

  def _process_element(self, element: ContentElement):
    """Filter ISD element style properties"""

    element_styles = list(element.iter_styles())
    for style_prop in element_styles:

      value = element.get_style(style_prop)
      default_value = self.style_property_default_values.get(style_prop)

      parent = element.parent()
      if parent is not None and style_prop.is_inherited:
        # If the parent style property value has not been removed, it means
        # the value is not set to default, and so that the child style property
        # value may have been "forced" to the default value, so let's skip it.
        parent_value = parent.get_style(style_prop)
        if parent_value is not None and parent_value is not value:
          continue

      # Remove the style property if its value is default (and if it is not inherited)
      if default_value is not None and value == default_value:
        element.set_style(style_prop, None)

    for child in element:
      self._process_element(child)

  def process(self, isd: ISD):
    """Filter ISD document style properties"""
    LOGGER.debug("Apply default style properties filter to ISD.")

    for region in isd.iter_regions():
      self._process_element(region)
