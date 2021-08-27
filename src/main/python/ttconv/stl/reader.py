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

from ttconv.stl.config import STLReaderConfiguration
from ttconv.stl.datafile import DataFile

LOGGER = logging.getLogger(__name__)

#
# STL reader
#

def to_model(data_file: typing.IO, config: typing.Optional[STLReaderConfiguration] = None, progress_callback=lambda _: None):
  """Converts an STL document to the data model"""

  m = DataFile(
    data_file.read(1024),
    disable_fill_line_gap=False if config is None else config.disable_fill_line_gap,
    disable_line_padding=False if config is None else config.disable_line_padding,
    start_tc=None if config is None else config.program_start_tc,
    font_stack=None if config is None else config.font_stack,
    max_row_count=None if config is None else config.max_row_count
    )

  for i in itertools.count():

    buf = data_file.read(128)

    if not buf:
      break

    try:
      m.process_tti_block(buf)
    except:
      LOGGER.error("Bad TTI block")
      raise
    
    progress_callback(i/m.get_tti_count())

  return m.get_document()
