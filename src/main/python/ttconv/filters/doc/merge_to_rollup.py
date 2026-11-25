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

import collections
import typing
from dataclasses import dataclass, field
from fractions import Fraction

from ttconv.config import ModuleConfiguration
from ttconv.filters.document_filter import DocumentFilter
from ttconv.model import Br, ContentDocument, P, ContentElement, Span, Text


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


def _line_length_decoder(value: typing.Union[int, str]) -> int:
  value = int(value)

  if value < 1:
    raise ValueError("line_length must be positive")

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

  # maximum number of characters per line when reflowing the text of a run
  line_length: int = field(default=32, metadata={"decoder": _line_length_decoder})


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
    text: str
    p: P
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

      if isinstance(e, Span) and not isinstance(e.parent(), P):
        raise ValueError("span elements must have a p element as parent")

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

    # collect, in runs, the lines of p elements that are contiguous, after reflowing the words of each run
    # into lines of at most line_length characters. A word longer than line_length occupies a line of its own.
    line_runs: typing.List[typing.List["MergeToRollUpDocFilter._Line"]] = []
    cur_run: typing.List["MergeToRollUpDocFilter._Line"] = []
    for i in range(len(all_ps)):

      # P elements are not contiguous if the gap between them is greater
      # than max_gap or they do not belong to the same region
      if i == 0 or \
        all_ps[i].get_begin() - all_ps[i-1].get_end() > self.config.max_gap or \
        all_ps[i].get_region() != all_ps[i-1].get_region():
        cur_run = []
        line_runs.append(cur_run)

      # distribute the duration of the p element across its words in proportion to their number of
      # characters, and extend each line to the end of its last word
      p = all_ps[i]
      begin = typing.cast(Fraction, p.get_begin())
      end = typing.cast(Fraction, p.get_end())
      dur = end - begin
      words = self._extract_words(p)
      char_count = sum(len(word) for word in words)
      char_cum = 0
      for word in words:
        word_begin = begin + Fraction(dur * char_cum, char_count)
        char_cum += len(word)
        word_end = begin + Fraction(dur * char_cum, char_count)

        if cur_run and len(cur_run[-1].text) + 1 + len(word) <= self.config.line_length:
          cur_run[-1].text += " " + word
          cur_run[-1].p = p
          cur_run[-1].end = word_end
        else:
          cur_run.append(self._Line(word, p, word_begin, word_end))

    # generate roll-up p elements from the lines of each run: each line starts a new p element that
    # contains it and up to num_lines - 1 preceding lines, so that the window builds up one line at a
    # time. At the end of the run, the window drains one line at a time, with the last line's interval
    # split evenly across the draining p elements.
    for lines in line_runs:
      if not lines:
        continue

      window: typing.Deque["MergeToRollUpDocFilter._Line"] = collections.deque([lines[0]], maxlen=self.config.num_lines)
      next_line_idx = 1
      drain_step: typing.Optional[Fraction] = None

      while window:
        if next_line_idx < len(lines):
          begin, end = window[-1].begin, window[-1].end
        elif drain_step is None:
          begin = window[-1].begin
          drain_step = Fraction(window[-1].end - begin, len(window))
          end = begin + drain_step
        else:
          begin, end = end, end + drain_step

        # create a p element containing the lines in the window, each as a single unstyled span
        # separated by br elements, and append it to the parent of the original p element of the
        # last line in the window
        original_p = window[-1].p

        new_p = P(doc)
        original_p.copy_to(new_p)
        new_p.set_begin(begin)
        new_p.set_end(end)
        new_p.set_region(original_p.get_region())

        for line_idx, line in enumerate(window):
          if line_idx > 0:
            new_p.push_child(Br(doc))

          span = Span(doc)
          span.push_child(Text(doc, line.text))
          new_p.push_child(span)

        typing.cast(ContentElement, original_p.parent()).push_child(new_p)

        if next_line_idx < len(lines):
          window.append(lines[next_line_idx])
          next_line_idx += 1
        else:
          window.popleft()

    for p in all_ps:
      p.remove()

    return doc

  @staticmethod
  def _extract_words(p: P) -> typing.List[str]:
    """Splits the text of `p` into words, separated by whitespace or br elements. Span styling is
    discarded."""
    fragments: typing.List[str] = []
    for child in p:
      if isinstance(child, Br):
        fragments.append(" ")
      else:
        fragments.extend(typing.cast(Text, text).get_text() for text in child)

    return "".join(fragments).split()
