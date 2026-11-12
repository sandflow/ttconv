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

'''Unit tests for ttconv.imsc.validator.rules'''

import unittest
import ttconv.imsc.validator.infoset as IS
import ttconv.imsc.namespaces as NS
from ttconv.imsc.validator.rules import (
  NodeSequence, AnyRule, OptionalRule, PCDATARule, Rule, SequenceRule, UnorderedRule, ZeroOrMoreRule
)


def _elem(local_name: str) -> IS.Element:
  return IS.Element(IS.Name(None, NS.QName(NS.TTML, local_name)))


class _SingleTextRule(Rule):
  """Test helper: matches exactly one IS.Text node."""
  def match(self, their_seq: NodeSequence, ctx) -> bool:
    our_seq = NodeSequence(their_seq)
    n = our_seq.pop()
    if not isinstance(n, IS.Text):
      return False
    their_seq.update_from(our_seq)
    return True
  def pattern(self) -> str:
    return "#text"


class _SingleElementRule(Rule):
  """Test helper: matches exactly one IS.Element node."""
  def match(self, their_seq: NodeSequence, ctx) -> bool:
    our_seq = NodeSequence(their_seq)
    n = our_seq.pop()
    if not isinstance(n, IS.Element):
      return False
    their_seq.update_from(our_seq)
    return True
  def pattern(self) -> str:
    return "elem"


class _NamedElementRule(Rule):
  """Test helper: matches exactly one IS.Element node with the given local name."""
  def __init__(self, local_name: str):
    self.local_name = local_name
  def match(self, their_seq: NodeSequence, ctx) -> bool:
    our_seq = NodeSequence(their_seq)
    n = our_seq.pop()
    if not isinstance(n, IS.Element) or n.name.qname.local_name != self.local_name:
      return False
    their_seq.update_from(our_seq)
    return True
  def pattern(self) -> str:
    return self.local_name


T1  = IS.Text("hello")
T2  = IS.Text("world")
WS  = IS.Text("  ")
E1  = _elem("span")
E2  = _elem("p")


class TestZeroOrMoreRule(unittest.TestCase):

  def test_matches_zero(self):
    seq = NodeSequence([])
    self.assertTrue(ZeroOrMoreRule(_SingleTextRule()).match(seq, None))
    self.assertIsNone(seq.peek())

  def test_matches_one(self):
    seq = NodeSequence([T1])
    self.assertTrue(ZeroOrMoreRule(_SingleTextRule()).match(seq, None))
    self.assertIsNone(seq.peek())

  def test_matches_many(self):
    seq = NodeSequence([T1, T2])
    self.assertTrue(ZeroOrMoreRule(_SingleTextRule()).match(seq, None))
    self.assertIsNone(seq.peek())

  def test_stops_at_non_matching_node(self):
    seq = NodeSequence([T1, E1])
    self.assertTrue(ZeroOrMoreRule(_SingleTextRule()).match(seq, None))
    self.assertIs(seq.peek(), E1)

  def test_does_not_consume_when_zero_matches(self):
    seq = NodeSequence([E1])
    self.assertTrue(ZeroOrMoreRule(_SingleTextRule()).match(seq, None))
    self.assertIs(seq.peek(), E1)

  def test_skips_whitespace_when_not_mixed_content(self):
    # whitespace is consumed but not passed to inner rule
    seq = NodeSequence([T1, WS, T2], mixed_content=False)
    self.assertTrue(ZeroOrMoreRule(_SingleTextRule()).match(seq, None))
    self.assertIsNone(seq.peek())

  def test_does_not_skip_whitespace_when_mixed_content(self):
    # whitespace is a regular node — inner rule must match it
    seq = NodeSequence([T1, WS, E1], mixed_content=True)
    self.assertTrue(ZeroOrMoreRule(_SingleTextRule()).match(seq, None))
    self.assertIs(seq.peek(), E1)

  def test_always_returns_true(self):
    seq = NodeSequence([E1, E2])
    self.assertTrue(ZeroOrMoreRule(_SingleTextRule()).match(seq, None))

  def test_pattern(self):
    self.assertEqual(ZeroOrMoreRule(_SingleTextRule()).pattern(), "#text*")


class TestPCDATARule(unittest.TestCase):
  # PCDATARule.validate() greedily consumes leading IS.Text nodes and always
  # returns True.  Use validate_all() to assert the entire sequence is text.

  def test_always_returns_true_on_empty(self):
    seq = NodeSequence([])
    self.assertTrue(PCDATARule().match(seq, None))

  def test_consumes_all_text_nodes(self):
    seq = NodeSequence([T1, T2])
    self.assertTrue(PCDATARule().match(seq, None))
    self.assertIsNone(seq.peek())

  def test_always_returns_true_on_element(self):
    seq = NodeSequence([E1])
    self.assertTrue(PCDATARule().match(seq, None))

  def test_does_not_consume_element(self):
    seq = NodeSequence([E1])
    PCDATARule().match(seq, None)
    self.assertIs(seq.peek(), E1)

  def test_consumes_leading_text_stops_at_element(self):
    seq = NodeSequence([T1, E1])
    PCDATARule().match(seq, None)
    self.assertIs(seq.peek(), E1)

  def test_consumes_nothing_when_first_node_is_element(self):
    seq = NodeSequence([E1, T1])
    PCDATARule().match(seq, None)
    self.assertIs(seq.peek(), E1)

  # validate_all() is the right tool for "sequence must be entirely text"
  def test_validate_all_passes_for_all_text(self):
    seq = NodeSequence([T1, T2])
    self.assertTrue(PCDATARule().match_all(seq, None))

  def test_validate_all_fails_when_element_present(self):
    seq = NodeSequence([E1])
    self.assertFalse(PCDATARule().match_all(seq, None))

  def test_validate_all_fails_for_text_then_element(self):
    seq = NodeSequence([T1, E1])
    self.assertFalse(PCDATARule().match_all(seq, None))

  def test_pattern(self):
    self.assertEqual(PCDATARule().pattern(), "#PCDATA")


class TestAnyRule(unittest.TestCase):

  def test_matches_first_alternative(self):
    seq = NodeSequence([T1])
    rule = AnyRule(_SingleTextRule(), _SingleElementRule())
    self.assertTrue(rule.match(seq, None))
    self.assertIsNone(seq.peek())

  def test_matches_second_alternative(self):
    seq = NodeSequence([E1])
    rule = AnyRule(_SingleTextRule(), _SingleElementRule())
    self.assertTrue(rule.match(seq, None))
    self.assertIsNone(seq.peek())

  def test_fails_when_no_alternative_matches(self):
    seq = NodeSequence([])
    rule = AnyRule(_SingleTextRule(), _SingleElementRule())
    self.assertFalse(rule.match(seq, None))

  def test_does_not_consume_on_failure(self):
    seq = NodeSequence([E1])
    rule = AnyRule(_SingleTextRule())
    self.assertFalse(rule.match(seq, None))
    self.assertIs(seq.peek(), E1)

  def test_pattern(self):
    rule = AnyRule(_SingleTextRule(), _SingleElementRule())
    self.assertEqual(rule.pattern(), "(#text | elem)")


class TestOptionalRule(unittest.TestCase):

  def test_matches_when_inner_matches(self):
    seq = NodeSequence([T1])
    self.assertTrue(OptionalRule(_SingleTextRule()).match(seq, None))
    self.assertIsNone(seq.peek())

  def test_matches_when_inner_does_not_match(self):
    seq = NodeSequence([E1])
    self.assertTrue(OptionalRule(_SingleTextRule()).match(seq, None))
    self.assertIs(seq.peek(), E1)

  def test_matches_empty_sequence(self):
    seq = NodeSequence([])
    self.assertTrue(OptionalRule(_SingleTextRule()).match(seq, None))

  def test_does_not_consume_on_mismatch(self):
    seq = NodeSequence([E1, T1])
    OptionalRule(_SingleTextRule()).match(seq, None)
    self.assertIs(seq.peek(), E1)

  def test_pattern(self):
    self.assertEqual(OptionalRule(_SingleTextRule()).pattern(), "#text?")


class TestSequenceRule(unittest.TestCase):

  def test_matches_ordered_sequence(self):
    seq = NodeSequence([T1, T2])
    rule = SequenceRule(_SingleTextRule(), _SingleTextRule())
    self.assertTrue(rule.match(seq, None))
    self.assertIsNone(seq.peek())

  def test_fails_when_second_rule_does_not_match(self):
    seq = NodeSequence([T1, E1])
    rule = SequenceRule(_SingleTextRule(), _SingleTextRule())
    self.assertFalse(rule.match(seq, None))

  def test_fails_on_empty_when_nodes_required(self):
    seq = NodeSequence([])
    rule = SequenceRule(_SingleTextRule())
    self.assertFalse(rule.match(seq, None))

  def test_skips_whitespace_when_not_mixed_content(self):
    seq = NodeSequence([WS, T1], mixed_content=False)
    rule = SequenceRule(_SingleTextRule())
    self.assertTrue(rule.match(seq, None))
    self.assertIsNone(seq.peek())

  def test_does_not_skip_whitespace_when_mixed_content(self):
    seq = NodeSequence([E1, WS, E2], mixed_content=True)
    seq.pop()
    self.assertTrue(isinstance(seq.peek(), IS.Text))

  def test_pattern(self):
    rule = SequenceRule(_SingleTextRule(), _SingleElementRule())
    self.assertEqual(rule.pattern(), "(#text elem)")


class TestUnorderedRule(unittest.TestCase):

  A, B, C = _elem("a"), _elem("b"), _elem("c")

  @staticmethod
  def _rule(**kwargs) -> UnorderedRule:
    return UnorderedRule(
      (_NamedElementRule("a"), 1, 1),
      (_NamedElementRule("b"), 0, 1),
      (_NamedElementRule("c"), 1, 3),
      **kwargs
    )

  def test_matches_in_any_order(self):
    for nodes in ([self.A, self.B, self.C], [self.C, self.B, self.A], [self.B, self.C, self.A], [self.C, self.A]):
      with self.subTest([n.name.qname.local_name for n in nodes]):
        seq = NodeSequence(list(nodes))
        self.assertTrue(self._rule().match(seq, None))
        self.assertIsNone(seq.peek())

  def test_interleaved_occurrences(self):
    seq = NodeSequence([self.C, self.A, self.C, self.B, self.C])
    self.assertTrue(self._rule().match_all(seq, None))

  def test_fails_below_minimum(self):
    seq = NodeSequence([self.A, self.B])
    self.assertFalse(self._rule().match(seq, None))
    self.assertIs(seq.peek(), self.A)

  def test_fails_when_empty_and_a_rule_is_required(self):
    self.assertFalse(self._rule().match(NodeSequence([]), None))

  def test_matches_empty_when_nothing_is_required(self):
    self.assertTrue(UnorderedRule((_NamedElementRule("a"), 0, 1)).match_all(NodeSequence([]), None))

  def test_stops_at_maximum(self):
    for extra in (self.A, self.C):
      with self.subTest(extra.name.qname.local_name):
        nodes = [self.A, self.C, self.C, self.C, extra]
        seq = NodeSequence(nodes)
        self.assertTrue(self._rule().match(seq, None))
        self.assertIs(seq.peek(), extra)
        self.assertFalse(self._rule().match_all(NodeSequence(nodes), None))

  def test_stops_at_unknown_node(self):
    seq = NodeSequence([self.A, self.C, self.C, E1, self.B])
    self.assertTrue(self._rule().match(seq, None))
    self.assertIs(seq.peek(), E1)

  def test_unbounded(self):
    rule = UnorderedRule((_NamedElementRule("a"), 1, None))
    self.assertTrue(rule.match_all(NodeSequence([self.A] * 50), None))
    self.assertFalse(rule.match(NodeSequence([]), None))

  def test_falls_through_to_later_rule_at_maximum(self):
    rule = UnorderedRule((_NamedElementRule("a"), 0, 1), (_SingleElementRule(), 0, None))
    seq = NodeSequence([self.A, self.A, self.A])
    self.assertTrue(rule.match_all(seq, None))

  def test_first_matching_rule_wins(self):
    # the catch-all is first, so it consumes `b`, and `b` is never seen as `b`
    rule = UnorderedRule((_SingleElementRule(), 0, None), (_NamedElementRule("b"), 1, 1))
    self.assertFalse(rule.match(NodeSequence([self.B]), None))

  def test_zero_length_matches_do_not_count_or_loop(self):
    # PCDATARule always matches, but consumes nothing on an element
    rule = UnorderedRule((PCDATARule(), 0, None), (_NamedElementRule("a"), 1, 1))
    seq = NodeSequence([self.A])
    self.assertTrue(rule.match_all(seq, None))

  def test_skips_whitespace_when_not_mixed_content(self):
    seq = NodeSequence([self.A, WS, self.C])
    self.assertTrue(self._rule().match_all(seq, None))

  def test_pattern(self):
    self.assertEqual(self._rule().pattern(), "(a & b? & c{1,3})")
    self.assertEqual(
      UnorderedRule((_NamedElementRule("a"), 0, None), (_NamedElementRule("b"), 1, None), (_NamedElementRule("c"), 2, None)).pattern(),
      "(a* & b+ & c{2,})"
    )

  def test_invalid_occurrences(self):
    for lo, hi in ((-1, 1), (2, 1), (0, 0)):
      with self.subTest((lo, hi)):
        with self.assertRaises(ValueError):
          UnorderedRule((_NamedElementRule("a"), lo, hi))


class TestValidateAll(unittest.TestCase):

  def test_returns_true_when_sequence_fully_consumed(self):
    seq = NodeSequence([T1])
    self.assertTrue(_SingleTextRule().match_all(seq, None))

  def test_returns_false_when_trailing_nodes_remain(self):
    seq = NodeSequence([T1, T2])
    self.assertFalse(_SingleTextRule().match_all(seq, None))

  def test_returns_false_when_rule_does_not_match(self):
    seq = NodeSequence([E1])
    self.assertFalse(_SingleTextRule().match_all(seq, None))


if __name__ == "__main__":
  unittest.main()
