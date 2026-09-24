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

"""Utility classes to build the TTML element grammar"""

from __future__ import annotations
import ttconv.imsc.validator.infoset as IS
import typing

class NodeSequence:
  """A list of nodes with a current-position index.

  Can be constructed from:
    - a list: index starts at 0
    - another NodeSequence: shares the same list and starts at the same index,
      allowing a caller to speculatively advance without consuming from the original.
  """

  # TODO: add a list of elements not to be pruned
  def __init__(
      self,
      source: typing.Sequence[IS.Element | IS.Text] | NodeSequence | None,
      mixed_content: bool | None = None,
      non_foreign_ns: set | None = None
    ):
    if isinstance(source, NodeSequence):
      self._nodes = source._nodes
      self._index = source._index
      self._mixed_content = mixed_content if mixed_content is not None else source._mixed_content
      self._non_foreign_ns = non_foreign_ns if non_foreign_ns is not None else source._non_foreign_ns
    else:
      self._nodes = source if source is not None else []
      self._index = 0
      self._mixed_content = mixed_content or False
      self._non_foreign_ns = non_foreign_ns

  def peek(self) -> IS.Element | IS.Text | None:
    """Returns the current node without advancing, or None if exhausted."""
    # skip empty text nodes if not mixed content, and skip element not in
    # self._non_foreign_ns if self._non_foreign_ns is not None
    while self._index < len(self._nodes):
      n = self._nodes[self._index]
      if (isinstance(n, IS.Element) and (self._non_foreign_ns is None or n.name.qname.ns in self._non_foreign_ns)) \
        or (isinstance(n, IS.Text) and (self._mixed_content or not n.value.isspace())):
        return self._nodes[self._index]
      self._index += 1      
    return None

  def pop(self) -> IS.Element | IS.Text | None:
    """Returns the current node and advances the index, or None if exhausted."""
    token = self.peek()
    if token is not None:
      self._index += 1
    return token

  def update_from(self, other: NodeSequence):
    if not isinstance(other, NodeSequence) or other._nodes is not self._nodes:
      raise ValueError
    self._index = other._index

  def __bool__(self) -> bool:
    return self._index < len(self._nodes)

  def __len__(self):
    return len(self._nodes) - self._index


class Rule:
  """Base class for IMSC validation rules"""
  def match(self, their_seq: NodeSequence, ctx: typing.Any) -> bool:
    """Attempts to match the beginning of their_seq against this rule.

    Returns True if the rule matches, False otherwise.
    A True return value does not imply validity: errors might have been logged.
    A True return value also does not imply progress: their_seq might not advance,
    e.g. for a rule that can match zero nodes. Any caller that loops on repeated
    True results (e.g. ZeroOrMoreRule, or a hypothetical OneOrMoreRule) must
    guard against this to avoid an infinite loop.
    """
    raise NotImplementedError
  
  def match_all(self, their_seq: NodeSequence, ctx: typing.Any) -> bool:
    """Attempts to match tne entirety of their_seq against this rule.

    Returns True if the rule matches, False otherwise.
    """

    if not self.match(their_seq, ctx):
      return False
    
    if their_seq.peek() is not None:
      return False
    
    return True

  def pattern(self) -> str:
    raise NotImplementedError

class SequenceRule(Rule):
  def __init__(self, *rules: Rule, mixed_content: bool | None = None):
    self.rules = rules
    self.mixed_content = mixed_content

  def match(self, their_seq: NodeSequence, ctx: typing.Any) -> bool:
    our_seq = NodeSequence(their_seq, mixed_content=self.mixed_content)

    for rule in self.rules:
      if not rule.match(our_seq, ctx):
        return False

    their_seq.update_from(our_seq)
    return True

  def pattern(self) -> str:
    return "(" + " ".join(e.pattern() for e in self.rules) + ")"

class AnyRule(Rule):
  def __init__(self, *rules: Rule):
    self.rules = rules

  def match(self, their_seq: NodeSequence, ctx: typing.Any) -> bool:
    for rule in self.rules:
      our_seq = NodeSequence(their_seq)
      if rule.match(our_seq, ctx):
        their_seq.update_from(our_seq)
        return True
    return False

  def pattern(self) -> str:
    return "(" + " | ".join(e.pattern() for e in self.rules) + ")"

class OptionalRule(Rule):
  def __init__(self, rule: Rule, mixed_content: bool | None = None):
    self.rule = rule
    self.mixed_content = mixed_content

  def match(self, their_seq: NodeSequence, ctx: typing.Any) -> bool:
    our_seq = NodeSequence(their_seq, self.mixed_content)
    if not self.rule.match(our_seq, ctx):
      return True
    their_seq.update_from(our_seq)
    return True

  def pattern(self) -> str:
    return f"{self.rule.pattern()}?"

class ZeroOrMoreRule(Rule):
  def __init__(self, rule: Rule, mixed_content: bool | None = None):
    self.rule = rule
    self.mixed_content = mixed_content

  def match(self, their_seq: NodeSequence, ctx: typing.Any) -> bool:
    our_seq = NodeSequence(their_seq, self.mixed_content)
    while our_seq.peek() is not None:
      progress_index = our_seq._index
      if not self.rule.match(our_seq, ctx):
        break
      if our_seq._index == progress_index:
        break

    their_seq.update_from(our_seq)
    return True

  def pattern(self) -> str:
    return f"{self.rule.pattern()}*"

class OneOrMoreRule(Rule):
  def __init__(self, rule: Rule, mixed_content: bool | None = None):
    self.rule = rule
    self.mixed_content = mixed_content

  def match(self, their_seq: NodeSequence, ctx: typing.Any) -> bool:
    our_seq = NodeSequence(their_seq, self.mixed_content)

    if not self.rule.match(our_seq, ctx):
      return False

    while our_seq.peek() is not None:
      progress_index = our_seq._index
      if not self.rule.match(our_seq, ctx):
        break
      if our_seq._index == progress_index:
        break

    their_seq.update_from(our_seq)
    return True

  def pattern(self) -> str:
    return f"{self.rule.pattern()}+"

class UnorderedRule(Rule):
  """Matches a run of nodes in any order, where each rule occurs a bounded number of times.

  Each entry is a `(rule, min_occurs, max_occurs)` tuple, where `max_occurs` is `None` if unbounded.

  Nodes are matched greedily: at each position, the rules that have not yet reached their maximum are tried in the order
  given and the first that matches wins. As a result, a node that matches a rule that has reached its maximum falls
  through to a later rule that also matches it, e.g. a catch-all, instead of failing to match. The rule fails, without
  consuming any node, if a rule occurs fewer than `min_occurs` times. Each occurrence of a rule must consume at least one
  node.
  """

  def __init__(self, *entries: typing.Tuple[Rule, int, typing.Optional[int]], mixed_content: bool | None = None):
    for rule, min_occurs, max_occurs in entries:
      if min_occurs < 0 or (max_occurs is not None and max_occurs < max(min_occurs, 1)):
        raise ValueError(f"Invalid occurrences for {rule.pattern()}: min {min_occurs}, max {max_occurs}")
    self.entries = entries
    self.mixed_content = mixed_content

  def match(self, their_seq: NodeSequence, ctx: typing.Any) -> bool:
    our_seq = NodeSequence(their_seq, self.mixed_content)
    counts = [0] * len(self.entries)

    while our_seq.peek() is not None:
      for i, (rule, _, max_occurs) in enumerate(self.entries):
        if max_occurs is not None and counts[i] >= max_occurs:
          continue

        candidate = NodeSequence(our_seq)
        if rule.match(candidate, ctx) and candidate._index != our_seq._index:
          our_seq.update_from(candidate)
          counts[i] += 1
          break
      else:
        break

    if any(count < min_occurs for count, (_, min_occurs, _) in zip(counts, self.entries)):
      return False

    their_seq.update_from(our_seq)
    return True

  def pattern(self) -> str:
    def occurrences(min_occurs: int, max_occurs: typing.Optional[int]) -> str:
      return {(1, 1): "", (0, 1): "?", (0, None): "*", (1, None): "+"}.get(
        (min_occurs, max_occurs),
        f"{{{min_occurs},{'' if max_occurs is None else max_occurs}}}"
      )

    return "(" + " & ".join(r.pattern() + occurrences(lo, hi) for r, lo, hi in self.entries) + ")"

class PCDATARule(Rule):
  """Validates that all nodes in a sequence are text nodes
  """

  def match(self, their_seq: NodeSequence, ctx: typing.Any) -> bool:
    our_seq = NodeSequence(their_seq)
    while isinstance(our_seq.peek(), IS.Text):
      our_seq.pop()

    their_seq.update_from(our_seq)
    return True

  def pattern(self) -> str:
    return "#PCDATA"

class EmptyRule(Rule):
  """Validates that the sequence is empty
  """

  def match(self, their_seq: NodeSequence, ctx: typing.Any) -> bool:
    return their_seq.peek() is None

  def pattern(self) -> str:
    return "EMPTY"