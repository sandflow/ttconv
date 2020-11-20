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

"""Regions merging filter"""

import logging

from ttconv.filters import Filter
from ttconv.isd import ISD
from ttconv.model import Body

LOGGER = logging.getLogger(__name__)


class RegionsMergingFilter(Filter):
  """Filter for merging ISD document regions into a single region"""

  def process(self, isd: ISD):
    """Merges the ISD document regions"""
    LOGGER.debug("Apply regions merging filter to ISD.")

    original_regions = list(isd.iter_regions())

    not_empty_regions = 0
    for region in original_regions:
      not_empty_regions += len(region)

    if len(original_regions) <= 1 or not_empty_regions <= 1:
      return

    LOGGER.warning("Merging ISD regions.")

    target_body = Body(isd)
    region_ids = []

    for region in original_regions:
      region_id = region.get_id()
      for body in region:

        for child in body:
          # Remove child from its parent body
          child.remove()

          # Add it to the target body
          target_body.push_child(child)

      region_ids.append(region_id)
      isd.remove_region(region_id)

    target_region = ISD.Region("_".join(region_ids), isd)
    target_region.push_child(target_body)

    isd.put_region(target_region)
