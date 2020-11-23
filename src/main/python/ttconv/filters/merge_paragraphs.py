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

"""Paragraphs merging filter"""

import logging

from ttconv.filters import Filter
from ttconv.isd import ISD
from ttconv.model import Div, P, Br, ContentElement

LOGGER = logging.getLogger(__name__)


class ParagraphsMergingFilter(Filter):
  """Filter for merging ISD document paragraphs per region into a single paragraph"""

  def _get_paragraphs(self, element: ContentElement):
    """Retrieves child paragraphs"""
    paragraphs = []

    for child in element:
      if isinstance(child, Div):
        paragraphs = paragraphs + self._get_paragraphs(child)
      elif isinstance(child, P):
        paragraphs.append(child)

    return paragraphs

  def process(self, isd: ISD):
    """Merges the ISD document paragraphs for each regions"""
    LOGGER.debug("Apply paragraphs merging filter to ISD.")

    for region in isd.iter_regions():

      for body in region:

        target_div = Div(isd)
        target_paragraph = P(isd)
        target_div.push_child(target_paragraph)

        original_divs = list(body)

        paragraphs = []
        for div in original_divs:
          paragraphs += self._get_paragraphs(div)

        if len(paragraphs) <= 1:
          continue

        LOGGER.warning("Merging ISD paragraphs.")

        for div in original_divs:
          div.remove()

        for (index, p) in enumerate(paragraphs):
          for span in list(p):
            # Remove child from its parent body
            span.remove()

            # Add it to the target paragraph
            target_paragraph.push_child(span)

          # Separate each merged paragraph by a Br element
          if index < len(paragraphs) - 1:
            target_paragraph.push_child(Br(isd))

        body.push_child(target_div)
