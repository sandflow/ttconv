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

'''Unit tests for ISD generation using caching'''

# pylint: disable=R0201,C0115,C0116

import unittest
from ttconv.isd import ISD
import ttconv.model as model
import ttconv.style_properties as styles
import xml.etree.ElementTree as et
import ttconv.imsc.reader as imsc_reader


class ISDCacheTests(unittest.TestCase):

  def test_show_background(self):
    ttml_doc = """<tt xml:lang="en"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:timeBase="media">
  <head>
    <styling>
      <style xml:id="s1" tts:backgroundColor="#ff0000" />
    </styling>
    <layout>
      <region xml:id="r1" style="s1" tts:extent="50% 50%" tts:origin="0% 0%"/>
      <region xml:id="r2" style="s1" tts:extent="50% 50%" tts:origin="0% 50%"/>
      <region xml:id="r3" style="s1" tts:extent="50% 50%" tts:origin="50% 50%"/>
      <region xml:id="r4" tts:extent="50% 50%" tts:origin="50% 0%"/>
    </layout>
  </head>
  <body>
    <div>
      <p region="r4" begin="00:00:00" end="00:00:00.2" xml:id="p0">ABCDEF</p>
      <p region="r1" begin="00:00:00.25" end="00:00:04" xml:id="p1"><span style="s1">a</span></p>
      <p region="r2" begin="00:00:00.25" end="00:00:04" xml:id="p2"><span style="s1">g</span></p>
      <p region="r3" begin="00:00:00.25" end="00:00:04" xml:id="p3"><span style="s1">m</span></p>
      <p region="r4" begin="00:00:00.25" end="00:00:04" xml:id="p4"><span style="s1">s</span></p>
    </div>
  </body>
</tt>"""

    doc = imsc_reader.to_model(et.ElementTree(et.fromstring(ttml_doc)))

    sig_times = ISD.significant_times(doc)

    isd = ISD.from_model(doc, 0.2, sig_times)

    self.assertEqual(len(list(isd.iter_regions())), 4)

if __name__ == '__main__':
  unittest.main()
