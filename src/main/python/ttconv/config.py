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

import dataclasses
from dataclasses import dataclass
from typing import Optional, Dict, List, Any


class ModuleConfiguration:
  """Base class for module configurations"""

  @classmethod
  def get_fields(cls) -> List[dataclasses.Field]:
    """Returns data class fields"""
    return list(dataclasses.fields(cls))

  @classmethod
  def validate(cls, config_dict: Dict):
    """Validates configuration dictionary"""
    for field in cls.get_fields():
      optional_field = "Optional" in field.type or cls.get_field_default(field) is not None

      config_value = config_dict.get(field.name)
      if not optional_field and config_value is None:
        raise ValueError("Compulsory configuration field missing:", field.name)

  @classmethod
  def parse(cls, config_dict: Dict) -> ModuleConfiguration:
    """Parses configuration dictionary"""
    cls.validate(config_dict)

    kwargs = {}
    for field in cls.get_fields():

      field_value = config_dict.get(field.name, cls.get_field_default(field))

      decoder = field.metadata.get("decoder")
      if decoder is not None:
        field_value = decoder.__call__(field_value)

      kwargs[field.name] = field_value

    instance = cls(**kwargs)

    return instance

  @staticmethod
  def get_field_default(field: dataclasses.Field) -> Optional[Any]:
    """Returns the default field value if any, None otherwise"""
    if isinstance(field.default, dataclasses._MISSING_TYPE):
      return None
    return field.default

  @classmethod
  def name(cls):
    """Returns the configuration name"""
    raise NotImplementedError


@dataclass
class GeneralConfiguration(ModuleConfiguration):
  """TT general configuration"""
  log_level: Optional[str] = "INFO"
  progress_bar: Optional[bool] = True

  @classmethod
  def name(cls):
    return "general"
