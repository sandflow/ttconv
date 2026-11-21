#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2025, Sandflow Consulting LLC
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

"""IMSC 1.1 Text Profile conformance filter.

Validates a ContentDocument against IMSC 1.1 Text Profile constraints.

On success, adds the IMSC 1.1 Text Profile designator to the document's
content profiles. On failure, raises ValueError on the first violation found.
"""

from __future__ import annotations

from dataclasses import dataclass

from ttconv.config import ModuleConfiguration
from ttconv.filters.document_filter import DocumentFilter
from ttconv.imsc.designators import IMSC_11_TEXT_PROFILE_DESIGNATOR
from ttconv.imsc.validator.imsc11_validator import validate_document
import ttconv.model as model


@dataclass
class IMSC11TextFilterConfig(ModuleConfiguration):
  """Configuration for the IMSC 1.1 Text Profile conformance filter."""

  @classmethod
  def name(cls):
    return "imsc11text"


class IMSC11TextFilter(DocumentFilter):
  """Validates a ContentDocument against IMSC 1.1 Text Profile constraints.

  On success, adds the IMSC 1.1 Text Profile designator to the document's
  content profiles. On failure, raises ValueError with the first violation.
  """

  @classmethod
  def get_config_class(cls) -> ModuleConfiguration:
    return IMSC11TextFilterConfig

  def __init__(self, config: IMSC11TextFilterConfig = None):
    super().__init__(config or IMSC11TextFilterConfig())

  def process(self, doc: model.ContentDocument):
    validate_document(doc)

    # Success: add designator to content profiles
    content_profiles = doc.get_content_profiles()
    if content_profiles is None:
      content_profiles = set()
    content_profiles.add(IMSC_11_TEXT_PROFILE_DESIGNATOR)
    doc.set_content_profiles(content_profiles)
