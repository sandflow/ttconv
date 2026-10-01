#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) Sandflow Consulting LLC
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


"""NBCU-053 validator configuration"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import typing

from ttconv.config import ModuleConfiguration
from ttconv.imsc.validator.nbcu053.model import AspectRatio, FrameRate

def _decode_frame_rate(value: str) -> FrameRate:
  try:
    if isinstance(value, str):
      return FrameRate.from_text(value)
  except ValueError:
    pass

  raise ValueError(f"frame_rate shall be one of {', '.join(json.dumps(r.text) for r in FrameRate)}, not {json.dumps(value)}")

def _decode_aspect_ratio(value: typing.Optional[str]) -> typing.Optional[AspectRatio]:
  if value is None:
    return None

  if isinstance(value, str):
    for ratio in AspectRatio:
      if ratio.value == value:
        return ratio

  raise ValueError(f"aspect_ratio shall be one of {', '.join(json.dumps(r.value) for r in AspectRatio)}, not {json.dumps(value)}")

@dataclass
class NBCU053ValidatorConfiguration(ModuleConfiguration):
  """NBCU-053 validator configuration"""

  @classmethod
  def name(cls):
    return "nbcu053"

  # frame rate of the document: "23.98", "25" or "29.97"
  frame_rate: FrameRate = field(metadata={"decoder": _decode_frame_rate})

  # the document is an HDR document
  hdr: bool = field(default=False, metadata={"decoder": bool})

  # display aspect ratio of the media, as a string, e.g. "2.39". It is required if the document has vertical text.
  aspect_ratio: typing.Optional[AspectRatio] = field(default=None, metadata={"decoder": _decode_aspect_ratio})
