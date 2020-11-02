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

'''Unit tests for the date model'''

# pylint: disable=R0201,C0115,C0116

import unittest
from fractions import Fraction
import ttconv.model as model
import ttconv.style_properties as styles
from ttconv.isd import ISD

class ISDTest(unittest.TestCase):

  def test_significant_times(self):
    d = model.Document()

    a1 = model.DiscreteAnimationStep(
      style_property=styles.StyleProperties.Color,
      value=styles.NamedColors.red.value
    )

    a2 = model.DiscreteAnimationStep(
      begin=Fraction(1),
      style_property=styles.StyleProperties.Color,
      value=styles.NamedColors.green.value
    )

    a3 = model.DiscreteAnimationStep(
      end=Fraction(1),
      style_property=styles.StyleProperties.Color,
      value=styles.NamedColors.blue.value
    )

    r1 = model.Region("r1", d)
    d.put_region(r1)

    # r2: sig times = {2, 9}

    r2 = model.Region("r2", d)
    r2.set_begin(Fraction(2))
    r2.set_end(Fraction(9))
    r2.add_animation_step(a1)
    d.put_region(r2)

    # b: sig times = {1, 10}

    b = model.Body(d)
    b.set_begin(Fraction(1))
    b.set_end(Fraction(10))
    d.set_body(b)

    # div1: offset = 1, sig times = {2, 4}

    div1 = model.Div(d)
    div1.add_animation_step(a2)
    div1.set_begin(Fraction(3))
    b.push_child(div1)

    # div2: offset = 1, sig times = {10}

    div2 = model.Div(d)
    div2.set_end(Fraction(12))
    b.push_child(div2)

    # p1: offset = 0, sig times = {}

    p1 = model.P(d)
    div2.push_child(p1)

    span1 = model.Span(d)
    p1.push_child(span1)

    t1 = model.Text(d, "hello")
    span1.push_child(t1)

    #

    self.assertEqual(ISD.significant_times(d), set((0, 2, 9, 1, 10, 4)))

if __name__ == '__main__':
  unittest.main()
