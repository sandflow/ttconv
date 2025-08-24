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

"""Unit tests for the SCC reader"""

# pylint: disable=R0201,C0115,C0116,W0212
import unittest
from fractions import Fraction
from numbers import Number
from typing import Union, Type, Optional

from ttconv import model
from ttconv.isd import ISD
from ttconv.model import Br, P, ContentElement, CellResolutionType, Span
from ttconv.scc.codes.attribute_codes import SccAttributeCode
from ttconv.scc.reader import to_model, to_disassembly
from ttconv.style_properties import StyleProperties, CoordinateType, LengthType, FontStyleType, NamedColors, TextDecorationType, \
  StyleProperty, ExtentType, ColorType, DisplayAlignType, ShowBackgroundType
from ttconv.time_code import FPS_29_97, SmpteTimeCode, FPS_30

LOREM_IPSUM = """Lorem ipsum dolor sit amet,
consectetur adipiscing elit.
Pellentesque interdum lacinia sollicitudin.
Integer luctus et ligula ac sagittis.
Ut at diam sit amet nulla fringilla
vestibulum nec vitae nisi.
"""


class SccWBDTest(unittest.TestCase):

  def test_SCC_2997_NDF(self):
    with open("../ttconv-private-repo/src/test/resources/scc/wbd/SCC_2997_NDF.scc", "r") as f:
      doc = to_model(f.read())
      isds = list(ISD.generate_isd_sequence(doc))

      def _process_element(e):
        if isinstance(e, model.Text):
          return e.get_text()
        else:
          return "".join(map(_process_element, list(e)))

      for i, (begin, isd) in enumerate(isds):
        if i == 4:
          break
        end = isds[i + 1][0] if i + 1 < len(isds) else None

        t = ""
        for region in isd.iter_regions():
          for body in region:
            t += _process_element(body)

        if len(t) > 0:
          print("")
          print(f"{SmpteTimeCode.from_seconds(begin, FPS_30)}, {SmpteTimeCode.from_seconds(end, FPS_30)}")
          print(t)

  def test_SCC_2997_DF(self):
    with open("../ttconv-private-repo/src/test/resources/scc/wbd/SCC_2997_DF.scc", "r") as f:
      doc = to_model(f.read())
      isds = list(ISD.generate_isd_sequence(doc))

      def _process_element(e):
        if isinstance(e, model.Text):
          return e.get_text()
        else:
          return "".join(map(_process_element, list(e)))

      for i, (begin, isd) in enumerate(isds):
        if i < len(isds) - 4:
          continue
        end = isds[i + 1][0] if i + 1 < len(isds) else None

        t = ""
        for region in isd.iter_regions():
          for body in region:
            t += _process_element(body)

        if len(t) > 0:
          print("")
          print(f"{SmpteTimeCode.from_seconds(begin, FPS_29_97)}, {SmpteTimeCode.from_seconds(end, FPS_29_97)}")
          print(t)

if __name__ == '__main__':
  unittest.main()
