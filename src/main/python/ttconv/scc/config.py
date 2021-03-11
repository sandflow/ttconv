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

"""SCC configuration"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ttconv.config import ModuleConfiguration
from ttconv.style_properties import TextAlignType


class TextAlignment(Enum):
  """Text alignment descriptions"""

  LEFT = ("left", TextAlignType.start)
  CENTER = ("center", TextAlignType.center)
  RIGHT = ("right", TextAlignType.end)
  AUTO = ("auto", TextAlignType.start)

  def __init__(self, label: str, text_align: TextAlignType):
    self.label = label
    self.text_align = text_align

  @staticmethod
  def from_value(value: [str, TextAlignment]) -> TextAlignment:
    """Try to create a text alignment instance from the specified value"""
    if isinstance(value, TextAlignment):
      return value

    for text_alignment in list(TextAlignment):
      if value.lower() == text_alignment.label.lower():
        return text_alignment

    raise ValueError(f"Invalid text align '{value}' value. Expect: 'left', 'center', 'right' or 'auto'.")


@dataclass
class SccReaderConfiguration(ModuleConfiguration):
  """SCC reader configuration"""

  text_align: TextAlignment = field(
    default=TextAlignment.AUTO,
    metadata={"decoder": TextAlignment.from_value}
  )

  @classmethod
  def name(cls):
    return "scc_reader"
