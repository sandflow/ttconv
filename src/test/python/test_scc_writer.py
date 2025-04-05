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

"""Unit tests for the SCC writer"""

# pylint: disable=R0201,C0115,C0116,W0212

import json
import os
import unittest
import xml.etree.ElementTree as et
from fractions import Fraction
from pathlib import Path

import ttconv.imsc.reader as imsc_reader
import ttconv.scc.writer as scc_writer
from ttconv.scc.config import SccWriterConfiguration
from ttconv.model import ContentDocument, Region, Body, Div, P, Span, Text, ContentElement
from ttconv.style_properties import StyleProperties, DisplayType


class SCCWriterTest(unittest.TestCase):

  def test_basic(self):
    ttml_doc_str = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:frameRate="30" ttp:frameRateMultiplier="1000 1001">
  <body>
    <div>
      <p begin="30f" end="90f">Line 1<br/>Line 2</p>
      <p begin="400f" end="450f">Line 3 blah<br/>Line 4 blah</p>
     </div>
  </body>
</tt>"""

    expected_scc=""""""

    model = imsc_reader.to_model(et.ElementTree(et.fromstring(ttml_doc_str)))
    config = SccWriterConfiguration()
    scc_from_model = scc_writer.from_model(model, config)
    self.assertEqual(scc_from_model, expected_scc)

if __name__ == '__main__':
  unittest.main()
