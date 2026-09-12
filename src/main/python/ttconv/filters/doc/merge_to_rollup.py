#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2026, Sandflow Consulting LLC
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

"""Defines the Merge to roll-up filter."""

from __future__ import annotations

import typing
from dataclasses import dataclass, field
from fractions import Fraction

from ttconv.config import ModuleConfiguration
from ttconv.filters.document_filter import DocumentFilter
from ttconv.model import Br, ContentDocument, P, ContentElement


def _max_gap_decoder(value: typing.Union[Fraction, str, int, float]) -> Fraction:
  if isinstance(value, Fraction):
    return value

  if isinstance(value, str):
    return Fraction(value)

  if isinstance(value, (int, float)):
    return Fraction(value).limit_denominator(1_000_000)

  raise ValueError("max_gap must be a number or a numeric string")


@dataclass
class MergeToRollUpDocFilterConfig(ModuleConfiguration):
  """Configuration class for the Merge to roll-up filter"""

  @classmethod
  def name(cls):
    return "merge_to_rollup"

  # maximum gap, in seconds, between two paragraphs for them to be merged
  max_gap: typing.Optional[Fraction] = field(default=Fraction(1, 30), metadata={"decoder": _max_gap_decoder})


class MergeToRollUpDocFilter(DocumentFilter):
  """Merges paragraphs that have identical styles and are separated by
  less than 1/30 s, so that they are presented as a single, continuous
  caption instead of being popped on and off independently."""

  @classmethod
  def get_config_class(cls) -> ModuleConfiguration:
    return MergeToRollUpDocFilterConfig

  def __init__(self, config: MergeToRollUpDocFilterConfig):
    super().__init__(config)

  @dataclass
  class _Line:
    first: ContentElement
    last: ContentElement
    begin: Fraction
    end: Fraction

  def process(self, doc: ContentDocument) -> ContentDocument:
    body = doc.get_body()

    if body is None:
      return doc

    all_ps = [e for e in body.dfs_iterator() if isinstance(e, P)]
    all_ps.sort(key=lambda p: p.get_begin() if p.get_begin() is not None else Fraction(0)) # type: ignore

    target_p = None
    for p in all_ps:

      if p.get_end() is None:
        target_p = None
        continue

      begin = p.get_begin() if p.get_begin() is not None else Fraction(0)

      if target_p is None or begin - target_p.get_end() > self.config.max_gap:
        target_p = p
        continue

      target_p.push_child(Br(target_p.get_doc()))
      for child in p:
        child.remove()
        target_p.push_child(child)
      p.remove()
      target_p.set_end(p.get_end())

    return doc
