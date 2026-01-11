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

import unittest
from fractions import Fraction
from ttconv.utils import DisjointIntervals

class DisjointIntervalsTest(unittest.TestCase):

  def test_add_simple(self):
    di = DisjointIntervals()
    di.add(Fraction(0), Fraction(10))
    self.assertEqual(len(di), 1)
    self.assertTrue(di.contains(Fraction(0)))
    self.assertTrue(di.contains(Fraction(5)))
    self.assertFalse(di.contains(Fraction(10)))

  def test_add_disjoint(self):
    di = DisjointIntervals()
    di.add(Fraction(0), Fraction(10))
    di.add(Fraction(20), Fraction(30))
    self.assertEqual(len(di), 2)
    self.assertTrue(di.contains(Fraction(5)))
    self.assertTrue(di.contains(Fraction(25)))
    self.assertFalse(di.contains(Fraction(15)))

  def test_add_overlap(self):
    di = DisjointIntervals()
    di.add(Fraction(0), Fraction(10))
    di.add(Fraction(5), Fraction(15))
    self.assertEqual(len(di), 1)
    self.assertEqual(list(di)[0], (Fraction(0), Fraction(15)))

  def test_add_adjacent(self):
    di = DisjointIntervals()
    di.add(Fraction(0), Fraction(10))
    di.add(Fraction(10), Fraction(20))
    self.assertEqual(len(di), 1)
    self.assertEqual(list(di)[0], (Fraction(0), Fraction(20)))

  def test_add_contained(self):
    di = DisjointIntervals()
    di.add(Fraction(0), Fraction(20))
    di.add(Fraction(5), Fraction(15))
    self.assertEqual(len(di), 1)
    self.assertEqual(list(di)[0], (Fraction(0), Fraction(20)))

  def test_add_enclosing(self):
    di = DisjointIntervals()
    di.add(Fraction(5), Fraction(15))
    di.add(Fraction(0), Fraction(20))
    self.assertEqual(len(di), 1)
    self.assertEqual(list(di)[0], (Fraction(0), Fraction(20)))

  def test_add_merge_multiple(self):
    di = DisjointIntervals()
    di.add(Fraction(0), Fraction(10))
    di.add(Fraction(20), Fraction(30))
    di.add(Fraction(40), Fraction(50))
    di.add(Fraction(5), Fraction(45))
    self.assertEqual(len(di), 1)
    self.assertEqual(list(di)[0], (Fraction(0), Fraction(50)))

  def test_infinity_end(self):
    di = DisjointIntervals()
    di.add(Fraction(10), None)
    self.assertEqual(len(di), 1)
    self.assertEqual(list(di)[0], (Fraction(10), None))
    self.assertTrue(di.contains(Fraction(1000)))

  def test_merge_infinity(self):
    di = DisjointIntervals()
    di.add(Fraction(0), Fraction(10))
    di.add(Fraction(5), None)
    self.assertEqual(len(di), 1)
    self.assertEqual(list(di)[0], (Fraction(0), None))

  def test_merge_infinity_gap(self):
    di = DisjointIntervals()
    di.add(Fraction(0), Fraction(10))
    di.add(Fraction(20), None)
    di.add(Fraction(5), Fraction(25))
    self.assertEqual(len(di), 1)
    self.assertEqual(list(di)[0], (Fraction(0), None))

  def test_add_invalid(self):
    di = DisjointIntervals()
    with self.assertRaises(ValueError):
      di.add(Fraction(10), Fraction(5))
    with self.assertRaises(ValueError):
      di.add(Fraction(10), Fraction(10))

if __name__ == '__main__':
  unittest.main()