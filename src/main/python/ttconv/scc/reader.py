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

"""SCC reader"""

from __future__ import annotations

import logging
from typing import Optional

from ttconv.model import ContentDocument, Body, Div, CellResolutionType, ActiveAreaType
from ttconv.scc.caption_paragraph import SCC_SAFE_AREA_CELL_RESOLUTION_ROWS, \
  SCC_SAFE_AREA_CELL_RESOLUTION_COLUMNS, SCC_ROOT_CELL_RESOLUTION_ROWS, SCC_ROOT_CELL_RESOLUTION_COLUMNS
from ttconv.scc.config import SccReaderConfiguration
from ttconv.scc.context import SccContext
from ttconv.scc.line import SccLine
from ttconv.style_properties import StyleProperties, LengthType, GenericFontFamilyType

LOGGER = logging.getLogger(__name__)


#
# SCC reader
#

def to_model(scc_content: str, config: Optional[SccReaderConfiguration] = None, progress_callback=lambda _: None):
  """Converts a SCC document to the data model"""

  document = ContentDocument()

  # Safe area must be a 32x15 grid, that represents 80% of the root area
  root_cell_resolution = CellResolutionType(rows=SCC_ROOT_CELL_RESOLUTION_ROWS, columns=SCC_ROOT_CELL_RESOLUTION_COLUMNS)
  document.set_cell_resolution(root_cell_resolution)

  safe_area_x_offset = int((root_cell_resolution.columns - SCC_SAFE_AREA_CELL_RESOLUTION_COLUMNS) / 2)
  safe_area_y_offset = int((root_cell_resolution.rows - SCC_SAFE_AREA_CELL_RESOLUTION_ROWS) / 2)

  context = SccContext(safe_area_x_offset, safe_area_y_offset, config)

  # The active area is equivalent to the safe area
  active_area = ActiveAreaType(
    left_offset=context.safe_area_x_offset / root_cell_resolution.columns,
    top_offset=context.safe_area_y_offset / root_cell_resolution.rows,
    width=(root_cell_resolution.columns - (context.safe_area_x_offset * 2)) / root_cell_resolution.columns,
    height=(root_cell_resolution.rows - (context.safe_area_y_offset * 2)) / root_cell_resolution.rows,
  )
  document.set_active_area(active_area)

  body = Body()
  body.set_doc(document)
  document.set_body(body)

  # the default value of LineHeight ("normal") typically translates to 125% of the font size, which causes regions to overflow.
  body.set_style(StyleProperties.LineHeight, LengthType(value=100, units=LengthType.Units.pct))

  # use a more readable font than the default Courier
  body.set_style(StyleProperties.FontFamily, ("Consolas", "Monaco", GenericFontFamilyType.monospace))

  # add line padding
  body.set_style(StyleProperties.LinePadding, LengthType(value=0.25, units=LengthType.Units.c))

  context.div = Div()
  context.div.set_doc(document)
  body.push_child(context.div)

  lines = scc_content.splitlines()
  nb_lines = len(lines)

  for (index, line) in enumerate(lines):
    LOGGER.debug(line)
    scc_line = SccLine.from_str(line)

    progress_callback((index + 1) / nb_lines)

    if scc_line is None:
      continue

    scc_line.process(context)

  context.flush()

  return document


def to_disassembly(scc_content: str, show_channels = False) -> str:
  """Dumps an SCC document into the disassembly format"""
  disassembly = ""
  for line in scc_content.splitlines():
    LOGGER.debug(line)
    scc_line = SccLine.from_str(line)

    if scc_line is None:
      continue

    line_to_disassembly = scc_line.to_disassembly(show_channels)
    LOGGER.debug(line_to_disassembly)

    disassembly += line_to_disassembly + "\n"

  return disassembly
