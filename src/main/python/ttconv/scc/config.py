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

from dataclasses import dataclass, field

from ttconv.config import ModuleConfiguration
from ttconv.style_properties import TextAlignType


@dataclass
class SccReaderConfiguration(ModuleConfiguration):
  """SCC reader configuration"""

  class TextAlignDecoder:
    """Utility callable for converting string to Fraction"""

    def __call__(self, value: [str, TextAlignType]) -> TextAlignType:
      if isinstance(value, TextAlignType):
        return value

      if value == "left":
        return TextAlignType.start

      if value == "center":
        return TextAlignType.center

      if value == "right":
        return TextAlignType.end

      raise ValueError(f"Invalid text align '{value}' value. Expect: 'left', 'center' or 'right'.")

  text_align: TextAlignType = field(
    default=TextAlignType.start,
    metadata={"decoder": TextAlignDecoder()}
  )

  @classmethod
  def name(cls):
    return "scc_reader"
