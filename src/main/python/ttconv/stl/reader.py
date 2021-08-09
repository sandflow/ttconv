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

"""STL reader"""

from __future__ import annotations

import typing
import itertools
import logging


from ttconv import model
import ttconv.style_properties as styles
import ttconv.stl.tf
from ttconv.stl.config import STLReaderConfiguration

from ttconv.stl import blocks

LOGGER = logging.getLogger(__name__)

#
# STL reader
#

def to_model(stl_document: typing.IO, _config: typing.Optional[STLReaderConfiguration] = None, progress_callback=lambda _: None):
  """Converts an STL document to the data model"""

  gsi_block = blocks.GSI(stl_document.read(1024))

  doc = model.ContentDocument()

  # assume 44x23 character matrix within a ‘Subtitle Safe Area’ of ~90% of the width and ~80% height of the related video object
  doc.set_cell_resolution(
    model.CellResolutionType(
      columns=44,
      rows=29)
  )

  body = model.Body(doc)
  doc.set_body(body)

  sgn_map = {}

  region_map = {}

  last_sn = None

  is_in_extension = False

  for i in itertools.count():
    
    tti_buf = stl_document.read(128)

    if not tti_buf:
      break

    tti = blocks.TTI(gsi_block, tti_buf)

    if 0xEF < tti.get_ebn() < 0xFF:
      # skip user data and reserved blocks
      continue

    if not is_in_extension:
      tti_tf = b''

    tti_tf += tti.get_tf()

    # continue accumulating if we have an extension block

    if tti.get_ebn() != 0xFF:
      is_in_extension = True
      continue

    is_in_extension = False

    # create a new subtitle if SN changes and we are not in cumulative mode

    if tti.get_sn() is not last_sn and tti.get_cs() in (0x00, 0x01):

      # find the div to which the subtitle belongs, based on SGN

      cur_div = sgn_map.get(tti.get_sgn())

      # create the div if it does not exist

      if cur_div is None:
        cur_div = model.Div(doc)
        body.push_child(cur_div)
        sgn_map[tti.get_sgn()] = cur_div

      # create the p that will hold the subtitle

      sub_element = model.P(doc)

      if tti.get_jc() == 0x01:
        sub_element.set_style(styles.StyleProperties.TextAlign, styles.TextAlignType.start)
      elif tti.get_jc() == 0x03:
        sub_element.set_style(styles.StyleProperties.TextAlign, styles.TextAlignType.end)
      else:
        sub_element.set_style(styles.StyleProperties.TextAlign, styles.TextAlignType.center)

      # assume that VP < MNR/2 means bottom-aligned and otherwise top-aligned
      # probably should offer an option to override this

      if tti.get_vp() > gsi_block.get_mnr() / 2:
        region = region_map.get(0)

        if region is None:
          region = model.Region("bottom", doc)
          region.set_style(
            styles.StyleProperties.Extent,
            styles.ExtentType(
              height=styles.LengthType(80, styles.LengthType.Units.pct),
              width=styles.LengthType(90, styles.LengthType.Units.pct),
            )
          )
          region.set_style(
            styles.StyleProperties.Origin,
            styles.CoordinateType(
              x=styles.LengthType(5, styles.LengthType.Units.pct),
              y=styles.LengthType(10, styles.LengthType.Units.pct)
            )
          )
          region.set_style(
            styles.StyleProperties.DisplayAlign,
            styles.DisplayAlignType.after
          )
          doc.put_region(region)
          region_map[0] = region
      else:
        region = region_map.get(1)

        if region is None:
          region = model.Region("top", doc)
          region.set_style(
            styles.StyleProperties.Extent,
            styles.ExtentType(
              height=styles.LengthType(80, styles.LengthType.Units.pct),
              width=styles.LengthType(90, styles.LengthType.Units.pct),
            )
          )
          region.set_style(
            styles.StyleProperties.Origin,
            styles.CoordinateType(
              x=styles.LengthType(5, styles.LengthType.Units.pct),
              y=styles.LengthType(10, styles.LengthType.Units.pct)
            )
          )
          region.set_style(
            styles.StyleProperties.DisplayAlign,
            styles.DisplayAlignType.before
          )
          doc.put_region(region)
          region_map[1] = region

      sub_element.set_region(region)

      cur_div.push_child(sub_element)

    if tti.get_cs() in (0x01, 0x02, 0x03):

      # create a nested span if we are in cumulative mode

      cur_element = model.Span(doc)
      sub_element.push_child(cur_element)
      sub_element.push_child(model.Br(doc))

    else :

      cur_element = sub_element

    cur_element.set_begin(tti.get_tci().to_temporal_offset())
    cur_element.set_end(tti.get_tco().to_temporal_offset())
    ttconv.stl.tf.process_tti_tf(cur_element, gsi_block.get_cct(), tti_tf)
    progress_callback(i/gsi_block.get_block_count())

  return doc
