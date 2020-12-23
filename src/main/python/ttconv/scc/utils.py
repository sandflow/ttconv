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

"""SCC utility functions"""
from numbers import Number
from typing import Union

from ttconv.model import CellResolutionType
from ttconv.style_properties import LengthType, CoordinateType, ExtentType


def get_position_from_offsets(x_offset: int, y_offset: int, units=LengthType.Units.c) -> CoordinateType:
  """Converts offsets into position"""
  x_position = LengthType(value=x_offset, units=units)
  y_position = LengthType(value=y_offset, units=units)

  return CoordinateType(x_position, y_position)


def get_extent_from_dimensions(width: Union[int, Number], height: Union[int, Number], units=LengthType.Units.c) -> ExtentType:
  """Converts dimensions into extent"""
  height = LengthType(value=height, units=units)
  width = LengthType(value=width, units=units)

  return ExtentType(height, width)


def convert_cells_to_percentages(dimensions: Union[CoordinateType, ExtentType], cell_resolution: CellResolutionType) -> Union[
  CoordinateType, ExtentType]:
  """Converts dimensions from cell units to percentage units"""
  if isinstance(dimensions, CoordinateType):
    if dimensions.x.units is not LengthType.Units.c or dimensions.y.units is not LengthType.Units.c:
      raise ValueError("Dimensions to convert must be in cell units")

    x_percent = round(dimensions.x.value * 100 / cell_resolution.columns)
    y_percent = round(dimensions.y.value * 100 / cell_resolution.rows)
    return get_position_from_offsets(x_percent, y_percent, LengthType.Units.pct)

  if isinstance(dimensions, ExtentType):
    if dimensions.width.units is not LengthType.Units.c or dimensions.height.units is not LengthType.Units.c:
      raise ValueError("Dimensions to convert must be in cell units")

    width_percent = round(dimensions.width.value * 100 / cell_resolution.columns)
    height_percent = round(dimensions.height.value * 100 / cell_resolution.rows)
    return get_extent_from_dimensions(width_percent, height_percent, LengthType.Units.pct)

  raise ValueError(f"Unsupported dimensions type: {dimensions.__class__.__name__}")
