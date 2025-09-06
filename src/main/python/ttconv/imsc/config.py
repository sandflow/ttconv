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

"""IMSC configuration"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Optional, Union

from ttconv.config import ModuleConfiguration
from ttconv.imsc.attributes import TimeExpressionSyntaxEnum

class ContentProfilesSignaling(Enum):
  """IMSC profile signaling options"""

  NONE = "none"
  """No content profile is signaled"""

  CONTENT_PROFILES = "content_profiles"
  """Content profiles are signaled using the ttp:contentProfiles attribute"""

  def __init__(self, label: str):
    self.label = label

  @staticmethod
  def from_value(value: Union[str, ContentProfilesSignaling]) -> ContentProfilesSignaling:
    """Return the enum corresponding to the specified value"""
    if isinstance(value, ContentProfilesSignaling):
      return value

    for ps in list(ContentProfilesSignaling):
      if value.lower() == ps.label.lower():
        return ps

    raise ValueError(f"Invalid ContentProfilesSignaling value '{value}'. Expect {','.join([e.value for e in list(ContentProfilesSignaling)])}")

def parse_time_expression_syntax(config_value: str) -> Optional[TimeExpressionSyntaxEnum]:
  """Parse time expression from string value"""
  if config_value is None:
    return config_value

  str_values = map(lambda e: e.value, list(TimeExpressionSyntaxEnum))
  if config_value not in str_values:
    raise ValueError("Invalid time expression format", config_value)

  return TimeExpressionSyntaxEnum[config_value]

@dataclass
class IMSCWriterConfiguration(ModuleConfiguration):
  """IMSC writer configuration"""

  class FractionDecoder:
    """Utility callable for converting string to Fraction"""

    def __call__(self, value: str) -> Optional[Fraction]:
      if value is None:
        return None

      [num, den] = value.split('/')

      return Fraction(int(num), int(den))

  @classmethod
  def name(cls):
    return "imsc_writer"

  time_format: Optional[TimeExpressionSyntaxEnum] = field(
    default=None,
    metadata={"decoder": parse_time_expression_syntax}
    )
  fps: Optional[Fraction] = field(
    default=None,
    metadata={"decoder": FractionDecoder()}
    )
  profile_signaling: ContentProfilesSignaling = field(
    default=ContentProfilesSignaling.NONE,
    metadata={"decoder": ContentProfilesSignaling.from_value}
    )

