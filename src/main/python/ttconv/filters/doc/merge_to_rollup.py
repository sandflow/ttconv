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

import itertools
import typing
from dataclasses import dataclass, field
from fractions import Fraction

from ttconv.config import ModuleConfiguration
from ttconv.filters.document_filter import DocumentFilter
from ttconv.model import Br, ContentDocument, P, ContentElement, Text


def have_same_contents(a: ContentElement, b: ContentElement) -> bool:
  # are the the same element kind
  if type(a) is not type(b):
    return False

  # do they belong to the same document
  if a.get_doc() is not b.get_doc():
    return False

  # do they have the same region, space handling and language
  if a.get_region() is not b.get_region() or a.get_space() != b.get_space() or a.get_lang() != b.get_lang():
    return False

  # do they have the same styles
  a_styles = {style_prop: a.get_style(style_prop) for style_prop in a.iter_styles()}
  b_styles = {style_prop: b.get_style(style_prop) for style_prop in b.iter_styles()}
  if a_styles != b_styles:
    return False

  if isinstance(a, Text):
    return a.get_text() == typing.cast(Text, b).get_text()

  a_children = list(a)
  b_children = list(b)

  if len(a_children) != len(b_children):
    return False

  return all(have_same_contents(ac, bc) for ac, bc in zip(a_children, b_children))


def _max_gap_decoder(value: typing.Union[Fraction, str, int, float]) -> Fraction:
  if isinstance(value, Fraction):
    return value

  if isinstance(value, str):
    return Fraction(value)

  if isinstance(value, (int, float)):
    return Fraction(value).limit_denominator(1_000_000)

  raise ValueError("max_gap must be a number or a numeric string")


def _num_lines_decoder(value: typing.Union[int, str]) -> int:
  value = int(value)

  if value not in (2, 3, 4):
    raise ValueError("num_lines must be 2, 3 or 4")

  return value


@dataclass
class MergeToRollUpDocFilterConfig(ModuleConfiguration):
  """Configuration class for the Merge to roll-up filter"""

  @classmethod
  def name(cls):
    return "merge_to_rollup"

  # maximum gap, in seconds, between two paragraphs for them to be merged
  max_gap: typing.Optional[Fraction] = field(default=Fraction(0, 1), metadata={"decoder": _max_gap_decoder})

  # number of lines simultaneously visible in the roll-up
  num_lines: int = field(default=3, metadata={"decoder": _num_lines_decoder})



class MergeToRollUpDocFilter(DocumentFilter):
  """Merges paragraphs into roll-up style captions if they have identical regions and are separated by
  less than `max_gap`."""

  @classmethod
  def get_config_class(cls) -> ModuleConfiguration:
    return MergeToRollUpDocFilterConfig

  def __init__(self, config: MergeToRollUpDocFilterConfig):
    super().__init__(config)
    self.config = config

  @dataclass
  class _Line:
    first: ContentElement
    last: ContentElement
    begin: Fraction
    end: Fraction

  def process(self, doc: ContentDocument) -> ContentDocument:
    # fast fail if there is no body
    body = doc.get_body()
    if body is None:
      return doc

    # collect all the p elements and make sure they match a constrained stucture
    all_ps: typing.List[P] = []

    for e in body.dfs_iterator():
      if isinstance(e, P):
        if e.get_begin() is None:
          # TODO: imsc_reader.to_model() stores an explicit begin of 0 as None
          # (0 being the implicit default begin), so normalize it back to 0.
          e.set_begin(Fraction(0))
        if e.get_end() is None:
          raise ValueError("p elements must have a finite end")
        all_ps.append(e)
      elif e.get_begin() is not None:
        # TODO: non-p elements can legitimately end up with a non-None get_end()
        # (e.g. imsc_reader.to_model() sets a container's end to the max end of
        # its children), so only a non-None begin is treated as a violation here.
        raise ValueError("Only p elements may have a begin")

      if isinstance(e, Br) and not isinstance(e.parent(), P):
        raise ValueError("br elements must have a p element as parent")

    all_ps.sort(key=lambda p: p.get_begin()) # type: ignore

    for prev_p, next_p in zip(all_ps, all_ps[1:]):
      if next_p.get_begin() < prev_p.get_end():
        raise ValueError("p elements must not overlap in time")

    if len(all_ps) == 0:
      return doc

    # merge successive paragraphs with identical contents
    for i in range(len(all_ps) - 1, 0, -1):
      if all_ps[i].get_begin() - all_ps[i-1].get_end() > self.config.max_gap and \
        have_same_contents(all_ps[i - 1], all_ps[i]):
        all_ps[i - 1].set_end(all_ps[i].get_end())
        all_ps[i].remove()
        del all_ps[i]

    # collect, in runs, all lines of p elements who are contiguous
    runs: typing.List[typing.List["MergeToRollUpDocFilter._Line"]] = []
    cur_run: typing.List["MergeToRollUpDocFilter._Line"] = []
    for i in range(len(all_ps)):

      # P elements are not contiguous if the gap between them is greater
      # than max_gap or they do not belong to the same region
      if i == 0 or \
        all_ps[i].get_begin() - all_ps[i-1].get_end() > self.config.max_gap or \
        all_ps[i].get_region() != all_ps[i-1].get_region():
        cur_run = []
        runs.append(cur_run)

      p = all_ps[i]
      begin = typing.cast(Fraction, p.get_begin())
      end = typing.cast(Fraction, p.get_end())

      lines = []
      cur_line: typing.Optional["MergeToRollUpDocFilter._Line"] = None

      for child in itertools.chain(p, [None]):
        if child is None or isinstance(child, Br):
          if cur_line is not None:
            lines.append(cur_line)
          cur_line = None
          continue
        if cur_line is None:
          cur_line = self._Line(first=child, last=child, begin=begin, end=end)
        else:
          cur_line.last = child

      if not lines:
        continue

      total_duration = Fraction(end - begin, len(lines))

      for j in range(len(lines)):
        lines[j].begin = begin + j * total_duration
        lines[j].end = begin + (j + 1) * total_duration
        cur_run.append(lines[j])

    # generate roll-up p elements: consecutive lines are merged into a single p
    # element for as long as they fit within num_lines
    for run in runs:
      window: typing.List["MergeToRollUpDocFilter._Line"] = []
      cur_new_p: typing.Optional[P] = None

      for line in run:
        window.append(line)
        evicted = len(window) > self.config.num_lines
        if evicted:
          window.pop(0)

        if cur_new_p is None or evicted:
          original_p = typing.cast(ContentElement, line.first.parent())
          parent = typing.cast(ContentElement, original_p.parent())

          cur_new_p = P(doc)
          original_p.copy_to(cur_new_p)
          cur_new_p.set_begin(line.begin)
          cur_new_p.set_region(original_p.get_region())

          for ctx_idx, ctx_line in enumerate(window):
            if ctx_idx > 0:
              cur_new_p.push_child(Br(doc))

            child = ctx_line.first
            while True:
              cur_new_p.push_child(child.clone(doc))
              if child is ctx_line.last:
                break
              child = typing.cast(ContentElement, child.next_sibling())

          parent.push_child(cur_new_p)
        else:
          cur_new_p.push_child(Br(doc))

          child = line.first
          while True:
            cur_new_p.push_child(child.clone(doc))
            if child is line.last:
              break
            child = typing.cast(ContentElement, child.next_sibling())

        cur_new_p.set_end(line.end)

    for p in all_ps:
      p.remove()

    return doc
