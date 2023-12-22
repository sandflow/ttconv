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

"""Filter for style properties supported by the output"""

import logging
from typing import Dict, List, Type

from ttconv.filters.isd_filter import ISDFilter
from ttconv.isd import ISD
from ttconv.model import ContentElement
from ttconv.style_properties import StyleProperty
import ttconv.filters.supported_style_properties

LOGGER = logging.getLogger(__name__)


class SupportedStylePropertiesISDFilter(ISDFilter):
  """Filter that remove unsupported style properties"""

  def __init__(self, supported_style_properties: Dict[Type[StyleProperty], List]):
    self.filter = ttconv.filters.supported_style_properties.SupportedStylePropertiesFilter(supported_style_properties)

  def process(self, isd: ISD):
    """Filter ISD document style properties"""
    LOGGER.debug("Filter default style properties from ISD.")

    for region in isd.iter_regions():
      self.filter.process_element(region)
