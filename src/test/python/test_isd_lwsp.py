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

'''Unit tests for white space handling during ISD generation'''

# pylint: disable=R0201,C0115,C0116

import unittest
import xml.etree.ElementTree as et
import ttconv.imsc.reader as imsc_reader
from ttconv.isd import ISD
import ttconv.model as model

class LSWPTests(unittest.TestCase):

  def test_lwsp_default(self):
    tree = et.parse('src/test/resources/ttml/lwsp_default.ttml')

    doc = imsc_reader.to_model(tree)

    isd = ISD.from_model(doc, 0)

    p0 = list(isd.iter_regions())[0][0][0][0]

    spans = list(p0)

    self.assertEqual(len(spans), 3)

    self.assertEqual(spans[0][0].get_text(), "hello ")

    self.assertEqual(spans[1][0].get_text(), "my name")

    self.assertEqual(spans[2][0].get_text(), " is Mathilda")

    p1 = list(isd.iter_regions())[0][0][0][1]

    spans = list(p1)

    self.assertEqual(len(spans), 4)

    self.assertEqual(spans[0][0].get_text(), "bonjour")

    self.assertEqual(spans[1][0].get_text(), " mon nom")

    self.assertIsInstance(spans[2], model.Br)

    self.assertEqual(spans[3][0].get_text(), "est")

if __name__ == '__main__':
  unittest.main()
