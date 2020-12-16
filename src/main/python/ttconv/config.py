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

"""TT configuration"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Optional, Dict


class ModuleConfiguration:
  """Base class for module configurations"""

  @classmethod
  def get_fields(cls) -> Dict:
    """Returns data class fields"""
    return cls.__dict__['__dataclass_fields__']

  @classmethod
  def validate(cls, config_dict: Dict):
    """Validates configuration dictionary"""
    for (name, field) in cls.get_fields().items():
      optional_field = "Optional" in field.type

      config_value = config_dict.get(name)
      if not optional_field and config_value is None:
        raise ValueError("Compulsory configuration field missing:", name)

  @staticmethod
  def parse_fraction(value: str) -> Fraction:
    """Utility function for parsing Fractions"""
    [num, den] = value.split('/')

    return Fraction(int(num), int(den))


@dataclass
class GeneralConfiguration(ModuleConfiguration):
  """TT general configuration"""
  log_level: Optional[str] = "DEBUG"
  other = None

  @staticmethod
  def parse(config_value: Dict) -> GeneralConfiguration:
    """Parse configuration dictionary"""
    log_level = config_value.get("log_level")
    if log_level is not None:
      return GeneralConfiguration(log_level)
    # default
    return GeneralConfiguration()
