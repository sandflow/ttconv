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
from numbers import Number


from ttconv import model
import ttconv.style_properties as styles
import ttconv.stl.tf
from ttconv.stl.config import STLReaderConfiguration

from ttconv.stl import blocks

LOGGER = logging.getLogger(__name__)

#
# STL reader
#

DEFAULT_HORIZONTAL_SAFE_MARGIN_PCT = 5
DEFAULT_VERTICAL_SAFE_MARGIN_PCT = 10
DEFAULT_TELETEXT_ROWS = 23
DEFAULT_TELETEXT_COLS = 40
DEFAULT_LINE_HEIGHT_PCT = 125
DEFAULT_SINGLE_HEIGHT_FONT_SIZE_PCT = 80
DEFAULT_DOUBLE_HEIGHT_FONT_SIZE_PCT = 160

def get_region(doc: model.ContentDocument, x_origin: Number, y_origin: Number, width: Number, height: Number, display_align: styles.DisplayAlignType):

  found_region = None

  regions = list(doc.iter_regions())

  for r in regions:
    r_origin: styles.CoordinateType = r.get_style(styles.StyleProperties.Origin)
    assert r_origin is not None
    assert r_origin.x.units is styles.LengthType.Units.pct
    assert r_origin.y.units is styles.LengthType.Units.pct
    if r_origin.x.value != x_origin or r_origin.y.value != y_origin:
      continue

    r_extent: styles.ExtentType = r.get_style(styles.StyleProperties.Extent)
    assert r_extent is not None
    assert r_extent.height.units is styles.LengthType.Units.pct
    assert r_extent.width.units is styles.LengthType.Units.pct
    if r_extent.height.value != height or r_extent.width.value != width:
      continue  

    r_display_align: styles.DisplayAlignType = r.get_style(styles.StyleProperties.DisplayAlign)
    assert r_display_align is not None
    if r_display_align != display_align:
      continue

    found_region = r
    break

  if found_region is None:
    found_region = model.Region(f"r{len(regions)}", doc)
    found_region.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        height=styles.LengthType(height, styles.LengthType.Units.pct),
        width=styles.LengthType(width, styles.LengthType.Units.pct),
      )
      )
    found_region.set_style(
      styles.StyleProperties.Origin,
      styles.CoordinateType(
        x=styles.LengthType(x_origin, styles.LengthType.Units.pct),
        y=styles.LengthType(y_origin, styles.LengthType.Units.pct)
      )
    )
    found_region.set_style(
      styles.StyleProperties.DisplayAlign,
      display_align
    )
    doc.put_region(found_region)
  
  return found_region

def to_model(stl_document: typing.IO, _config: typing.Optional[STLReaderConfiguration] = None, progress_callback=lambda _: None):
  """Converts an STL document to the data model"""

  doc = model.ContentDocument()

  gsi = blocks.GSI(stl_document.read(1024))

  doc.set_cell_resolution(
    model.CellResolutionType(
      columns=round(100 * DEFAULT_TELETEXT_COLS / (100 - 2 * DEFAULT_HORIZONTAL_SAFE_MARGIN_PCT)),
      rows=round(100 * DEFAULT_TELETEXT_ROWS / (100 - 2 * DEFAULT_VERTICAL_SAFE_MARGIN_PCT))
    )
  )

  body = model.Body(doc)
  
  body.set_style(styles.StyleProperties.LineHeight, styles.LengthType(DEFAULT_LINE_HEIGHT_PCT, styles.LengthType.Units.pct))

  doc.set_body(body)

  sgn_to_div_map = {}

  last_sn = None

  is_in_extension = False

  for i in itertools.count():
    
    tti_buf = stl_document.read(128)

    if not tti_buf:
      break

    tti = blocks.TTI(gsi, tti_buf)

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

      last_sn =  tti.get_sn()

      # find the div to which the subtitle belongs, based on SGN

      div_element = sgn_to_div_map.get(tti.get_sgn())

      # create the div if it does not exist

      if div_element is None:
        div_element = model.Div(doc)
        body.push_child(div_element)
        sgn_to_div_map[tti.get_sgn()] = div_element

      # create the p that will hold the subtitle

      p_element = model.P(doc)

      if tti.get_jc() == 0x01:
        p_element.set_style(styles.StyleProperties.TextAlign, styles.TextAlignType.start)
      elif tti.get_jc() == 0x03:
        p_element.set_style(styles.StyleProperties.TextAlign, styles.TextAlignType.end)
      else:
        p_element.set_style(styles.StyleProperties.TextAlign, styles.TextAlignType.center)

      
      if gsi.get_dsc() in (0x20, 0x30):
        # use large region and always align at the bottom for undefined and open subtitles

        region = get_region(
          doc,
          round(DEFAULT_HORIZONTAL_SAFE_MARGIN_PCT),
          round(DEFAULT_VERTICAL_SAFE_MARGIN_PCT),
          round(100 - 2 * DEFAULT_HORIZONTAL_SAFE_MARGIN_PCT),
           round(100 - 2 * DEFAULT_VERTICAL_SAFE_MARGIN_PCT),
          styles.DisplayAlignType.after
          )

      else:

        safe_area_height =  round(100 - DEFAULT_VERTICAL_SAFE_MARGIN_PCT * 2)
        safe_area_width =  round(100 - DEFAULT_HORIZONTAL_SAFE_MARGIN_PCT * 2)

        # assume that VP < MNR/2 means bottom-aligned and otherwise top-aligned
        # probably should offer an option to override this

        if tti.get_vp() < DEFAULT_TELETEXT_ROWS // 2:
          # top-aligned large region
          

          r_y = DEFAULT_VERTICAL_SAFE_MARGIN_PCT + ((tti.get_vp() - 1) / DEFAULT_TELETEXT_ROWS) * safe_area_height
          r_height = 100 - DEFAULT_VERTICAL_SAFE_MARGIN_PCT - r_y
          
          region = get_region(
            doc,
            round(DEFAULT_HORIZONTAL_SAFE_MARGIN_PCT),
            r_y,
            safe_area_width,
            r_height,
            styles.DisplayAlignType.after
          )

        else:

          r_y = DEFAULT_VERTICAL_SAFE_MARGIN_PCT
          r_height = ((tti.get_vp() + ttconv.stl.tf.line_count(tti_tf) - 1)/ DEFAULT_TELETEXT_ROWS) * safe_area_height
          
          region = get_region(
            doc,
            round(DEFAULT_HORIZONTAL_SAFE_MARGIN_PCT),
            r_y,
            safe_area_width,
            r_height,
            styles.DisplayAlignType.before
          )

      p_element.set_region(region)

      div_element.push_child(p_element)

    if tti.get_cs() in (0x01, 0x02, 0x03):

      # create a nested span if we are in cumulative mode

      sub_element = model.Span(doc)
      p_element.push_child(sub_element)
      p_element.push_child(model.Br(doc))

    else :

      sub_element = p_element

    sub_element.set_begin(tti.get_tci().to_temporal_offset())
    sub_element.set_end(tti.get_tco().to_temporal_offset())


    if gsi.get_dsc() not in (0x20, 0x30) and not ttconv.stl.tf.is_double_height(tti_tf):
      font_size = DEFAULT_SINGLE_HEIGHT_FONT_SIZE_PCT
    else:
      font_size = DEFAULT_DOUBLE_HEIGHT_FONT_SIZE_PCT

    sub_element.set_style(
      styles.StyleProperties.FontSize,
      styles.LengthType(
        font_size,
        styles.LengthType.Units.pct
      )
    )

    ttconv.stl.tf.to_model(sub_element, gsi.get_cct(), tti_tf)

    progress_callback(i/gsi.get_block_count())

  return doc
