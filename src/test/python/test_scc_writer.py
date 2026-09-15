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

from io import StringIO
import json
import os
import unittest
import xml.etree.ElementTree as et
from fractions import Fraction
from pathlib import Path

import sys
from ttconv.imsc.attributes import TimeExpressionSyntaxEnum
from ttconv.imsc.config import IMSCWriterConfiguration
import ttconv.imsc.reader as imsc_reader
import ttconv.imsc.writer as imsc_writer
import ttconv.scc.writer as scc_writer
import ttconv.scc.reader as scc_reader
import ttconv.vtt.reader as vtt_reader
import ttconv.srt.reader as srt_reader

from ttconv.scc.config import SCCFrameRate, SccWriterConfiguration
from ttconv.model import ContentDocument, Region, Body, Div, P, Span, Text, ContentElement
from ttconv.style_properties import StyleProperties, DisplayType

class SccWriterConfigurationTest(unittest.TestCase):

  def test_defaults(self):
    config = SccWriterConfiguration()

    self.assertEqual(config.allow_reflow, True)
    self.assertEqual(config.force_popon, False)
    self.assertEqual(config.frame_rate, SCCFrameRate.FPS_2997_DF)

  def test_allow_reflow(self):
    config = SccWriterConfiguration.parse(json.loads("""{"allow_reflow": true }"""))
    self.assertEqual(config.allow_reflow, True)

    config = SccWriterConfiguration.parse(json.loads("""{"allow_reflow": false }"""))
    self.assertEqual(config.allow_reflow, False)

  def test_force_popon(self):
    config = SccWriterConfiguration.parse(json.loads("""{"force_popon": true }"""))
    self.assertEqual(config.force_popon, True)

    config = SccWriterConfiguration.parse(json.loads("""{"force_popon": false }"""))
    self.assertEqual(config.force_popon, False)

  def test_rollup_lines(self):
    config = SccWriterConfiguration.parse(json.loads("""{"rollup_lines": 2 }"""))
    self.assertEqual(config.rollup_lines, 2)

    config = SccWriterConfiguration.parse(json.loads("""{"rollup_lines": 3 }"""))
    self.assertEqual(config.rollup_lines, 3)

    config = SccWriterConfiguration.parse(json.loads("""{"rollup_lines": 4 }"""))
    self.assertEqual(config.rollup_lines, 4)

    with self.assertRaises(ValueError):
      config = SccWriterConfiguration.parse(json.loads("""{"rollup_lines": 5 }"""))

  def test_rollup_gap_tolerance(self):
    config = SccWriterConfiguration()
    self.assertEqual(config.rollup_gap_tolerance, 0)

    config = SccWriterConfiguration.parse(json.loads("""{"rollup_gap_tolerance": "1/30" }"""))
    self.assertEqual(config.rollup_gap_tolerance, Fraction(1, 30))

  def test_rollup_detection_pct(self):
    config = SccWriterConfiguration()
    self.assertEqual(config.rollup_detection_pct, 100)

    config = SccWriterConfiguration.parse(json.loads("""{"rollup_detection_pct": 50 }"""))
    self.assertEqual(config.rollup_detection_pct, 50)

    with self.assertRaises(ValueError):
      config = SccWriterConfiguration.parse(json.loads("""{"rollup_detection_pct": -1 }"""))

    with self.assertRaises(ValueError):
      config = SccWriterConfiguration.parse(json.loads("""{"rollup_detection_pct": 101 }"""))

  def test_frame_rate(self):
    config = SccWriterConfiguration.parse(json.loads("""{"frame_rate": "30NDF" }"""))
    self.assertEqual(config.frame_rate.fps, Fraction(30))
    self.assertFalse(config.frame_rate.df)

    config = SccWriterConfiguration.parse(json.loads("""{"frame_rate": "29.97NDF" }"""))
    self.assertEqual(config.frame_rate.fps, Fraction(30000, 1001))
    self.assertFalse(config.frame_rate.df)

    config = SccWriterConfiguration.parse(json.loads("""{"frame_rate": "29.97DF" }"""))
    self.assertEqual(config.frame_rate.fps, Fraction(30000, 1001))
    self.assertTrue(config.frame_rate.df)

    with self.assertRaises(ValueError):
      config = SccWriterConfiguration.parse(json.loads("""{"frame_rate": 30 }"""))

class SCCWriterTest(unittest.TestCase):

  def test_basic(self):
    ttml_doc_str = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:frameRate="30" ttp:frameRateMultiplier="1000 1001">
  <body>
    <div>
      <p begin="30f" end="90f">Hello</p>
      <p begin="120f" end="150f">Bonjour</p>
     </div>
  </body>
</tt>"""

    expected_scc="""Scenarist_SCC V1.0

00:00:00;21	9420 9420 94ae 94ae 9440 9440 c8e5 ecec ef80 942f 942f

00:00:03;00	942c 942c

00:00:03;20	9420 9420 94ae 94ae 9440 9440 c2ef 6eea ef75 f280 942f 942f

00:00:05;00	942c 942c"""

  def test_pop_on_centered(self):
    ttml_doc_str = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:frameRate="30" ttp:frameRateMultiplier="1000 1001">
  <body>
    <div>
      <p begin="30f" end="90f" tts:textAlign="center">Hello</p>
     </div>
  </body>
</tt>"""

    expected_scc="""Scenarist_SCC V1.0

00:00:00;21	9420 9420 94ae 94ae 94d6 94d6 20c8 e5ec ecef 942f 942f

00:00:03;00	942c 942c"""

    model = imsc_reader.to_model(et.ElementTree(et.fromstring(ttml_doc_str)))
    assert model is not None
    config = SccWriterConfiguration()
    scc_from_model = scc_writer.from_model(model, config)
    self.assertEqual(scc_from_model, expected_scc)

  def test_pop_on_right_aligned(self):
    ttml_doc_str = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:frameRate="30" ttp:frameRateMultiplier="1000 1001">
  <body>
    <div>
      <p begin="30f" end="90f" tts:textAlign="right">Hello</p>
     </div>
  </body>
</tt>"""

    expected_scc="""Scenarist_SCC V1.0

00:00:00;20	9420 9420 94ae 94ae 94dc 94dc 2020 20c8 e5ec ecef 942f 942f

00:00:03;00	942c 942c"""

    model = imsc_reader.to_model(et.ElementTree(et.fromstring(ttml_doc_str)))
    assert model is not None
    config = SccWriterConfiguration()
    scc_from_model = scc_writer.from_model(model, config)
    self.assertEqual(scc_from_model, expected_scc)

  def test_rollup(self):
    ttml_doc_str = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:frameRate="30" ttp:frameRateMultiplier="1000 1001">
  <body>
    <div>
      <p begin="30f" end="90f">Hello</p>
      <p begin="90f" end="150f">Hello my name</p>
      <p begin="150f" end="300f">Hello my name<br/>is Paul.</p>
     </div>
  </body>
</tt>"""

    expected_scc="""Scenarist_SCC V1.0

00:00:00;28	94a7 94a7 94ad 94ad 9470 9470 c8e5 ecec ef80

00:00:03;00	206d 7920 6e61 6de5

00:00:04;28	94a7 94a7 94ad 94ad 9470 9470 e973 20d0 6175 ecae

00:00:10;00	942c 942c"""

    model = imsc_reader.to_model(et.ElementTree(et.fromstring(ttml_doc_str)))
    config = SccWriterConfiguration()
    scc_from_model = scc_writer.from_model(model, config)
    self.assertEqual(scc_from_model, expected_scc)

    # round-trip test
    rt_model = scc_reader.to_model(scc_from_model)
    # cfg = IMSCWriterConfiguration(time_format=TimeExpressionSyntaxEnum.frames, fps=Fraction(30000, 1001))
    # imsc_writer.from_model(rt_model, cfg).write(sys.stdout.buffer)
    b = rt_model.get_body()
    div = list(b)[0]
    p0 = list(div)[0]
    self.assertEqual(Fraction(30 * 1001, 30000), p0.get_begin())
    p1 = list(div)[1]
    self.assertEqual(Fraction(150 * 1001, 30000), p1.get_begin())
    self.assertEqual(Fraction(300 * 1001, 30000), p1.get_end())

  def test_rollup_detection_break(self):
    # captions with small inter-cue gaps must not defeat roll-up detection,
    # and one non-matching pair must not force the whole document to pop-on
    with open("src/test/resources/vtt/rollup-detection-break.vtt", "r", encoding="utf-8-sig") as f:
      model = vtt_reader.to_model(f)

    config = SccWriterConfiguration(rollup_gap_tolerance=Fraction(1, 30), rollup_detection_pct=50)
    scc_from_model = scc_writer.from_model(model, config)

    self.assertIn("94a7 94a7", scc_from_model)
    self.assertNotIn("9420 9420", scc_from_model)

  def test_rollup_multiline_start(self):
    f = StringIO("""1
00:00:01,000 --> 00:00:02,000
Line 1
Line 2

2
00:00:02,000 --> 00:00:03,000
Line 1
Line 2
Line 3

3
00:00:03,000 --> 00:00:04,000
Line 2
Line 3
Line 4
""")

    expected_scc="""Scenarist_SCC V1.0

00:00:00;16	94a7 94a7 94ad 94ad 9470 9470 4ce9 6ee5 2031 94a7 94a7 94ad 94ad 9470 9470 4ce9 6ee5 2032

00:00:01;27	94a7 94a7 94ad 94ad 9470 9470 4ce9 6ee5 20b3

00:00:02;27	94a7 94a7 94ad 94ad 9470 9470 4ce9 6ee5 2034

00:00:03;29	942c 942c"""

    model = srt_reader.to_model(f)
    config = SccWriterConfiguration()
    scc_from_model = scc_writer.from_model(model, config)
    self.assertEqual(scc_from_model, expected_scc)

  def test_rollup_restart(self):
    f = StringIO("""1
01:00:01,000 --> 01:00:02,000
Line 1

2
01:00:02,000 --> 01:00:03,000
Line 1
Line 2

3
01:00:03,000 --> 01:00:04,000
Line 2
Line 3

4
01:00:06,000 --> 01:00:07,000
Line 4

5
01:00:09,000 --> 01:00:10,000
Line 1
Line 2

6
01:00:10,000 --> 00:00:11,000
Line 2
Line 3
""")

    expected_scc="""Scenarist_SCC V1.0

01:00:00;28	94a7 94a7 94ad 94ad 9470 9470 4ce9 6ee5 2031

01:00:01;28	94a7 94a7 94ad 94ad 9470 9470 4ce9 6ee5 2032

01:00:02;28	94a7 94a7 94ad 94ad 9470 9470 4ce9 6ee5 20b3

01:00:03;29	942c 942c

01:00:05;27	94a7 94a7 94ad 94ad 9470 9470 4ce9 6ee5 2034

01:00:06;29	942c 942c

01:00:08;16	94a7 94a7 94ad 94ad 9470 9470 4ce9 6ee5 2031 94a7 94a7 94ad 94ad 9470 9470 4ce9 6ee5 2032

01:00:09;29	942c 942c"""

    model = srt_reader.to_model(f)
    config = SccWriterConfiguration()
    scc_from_model = scc_writer.from_model(model, config)
    self.assertEqual(scc_from_model, expected_scc)

  def test_basic_2997NDF(self):
    ttml_doc_str = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml">
  <body>
    <div>
      <p begin="3600s" end="3602s">Hello</p>
     </div>
  </body>
</tt>"""

    model = imsc_reader.to_model(et.ElementTree(et.fromstring(ttml_doc_str)))
    assert model is not None

    expected_scc="""Scenarist_SCC V1.0

00:59:56:03	9420 9420 94ae 94ae 9440 9440 c8e5 ecec ef80 942f 942f

00:59:58:12	942c 942c"""

    config = SccWriterConfiguration(frame_rate=SCCFrameRate.FPS_2997_NDF)
    scc_from_model = scc_writer.from_model(model, config)
    self.assertEqual(scc_from_model, expected_scc)

  def test_basic_30FPS(self):
    ttml_doc_str = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:frameRate="30">
  <body>
    <div>
      <p begin="30f" end="90f">Hello</p>
      <p begin="120f" end="150f">Bonjour</p>
     </div>
  </body>
</tt>"""

    model = imsc_reader.to_model(et.ElementTree(et.fromstring(ttml_doc_str)))
    assert model is not None

    expected_scc="""Scenarist_SCC V1.0

00:00:00:21	9420 9420 94ae 94ae 9440 9440 c8e5 ecec ef80 942f 942f

00:00:03:00	942c 942c

00:00:03:20	9420 9420 94ae 94ae 9440 9440 c2ef 6eea ef75 f280 942f 942f

00:00:05:00	942c 942c"""

    config = SccWriterConfiguration(frame_rate=SCCFrameRate.FPS_30_NDF)
    scc_from_model = scc_writer.from_model(model, config)
    self.assertEqual(scc_from_model, expected_scc)

  def test_zero_start(self):
    ttml_doc_str = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:frameRate="30">
  <body>
    <div>
      <p begin="0f" end="90f">Hello</p>
     </div>
  </body>
</tt>"""

    model = imsc_reader.to_model(et.ElementTree(et.fromstring(ttml_doc_str)))

    with self.assertRaises(RuntimeError):
      scc_writer.from_model(model)

    scc_from_model = scc_writer.from_model(model, SccWriterConfiguration(start_tc="01:00:00;00"))
    expected_scc="""Scenarist_SCC V1.0

00:59:59;21	9420 9420 94ae 94ae 9440 9440 c8e5 ecec ef80 942f 942f

01:00:02;29	942c 942c"""
    self.assertEqual(scc_from_model, expected_scc)

    scc_from_model = scc_writer.from_model(model, SccWriterConfiguration(frame_rate=SCCFrameRate.FPS_30_NDF, start_tc="01:00:00:00"))
    expected_scc="""Scenarist_SCC V1.0

00:59:59:21	9420 9420 94ae 94ae 9440 9440 c8e5 ecec ef80 942f 942f

01:00:03:00	942c 942c"""
    self.assertEqual(scc_from_model, expected_scc)

  def test_multi_regions(self):
    expected_scc="""Scenarist_SCC V1.0

00:00:00;22	9420 9420 94ae 94ae 9440 9440 6180 942f 942f

00:00:01;29	942c 942c

00:00:02;22	9420 9420 94ae 94ae 9440 9440 6280 942f 942f

00:00:03;29	942c 942c"""

    SAMPLE = """<tt xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling" xml:lang="en">
	<head>
		<layout>
			<region xml:id="r_a" tts:origin="0% 0%" tts:extent="50% 50%" />
			<region xml:id="r_b" tts:origin="50% 50%" tts:extent="50% 50%" />
		</layout>
	</head>
	<body>
		<div>
			<p region="r_a" begin="00:00:01.000" end="00:00:02.000">a</p>
			<p region="r_b" begin="00:00:03.000" end="00:00:04.000">b</p>
		</div>
	</body>
</tt>

"""

    model = imsc_reader.to_model(et.ElementTree(et.fromstring(SAMPLE)))
    scc_from_model = scc_writer.from_model(model)
    self.assertEqual(scc_from_model, expected_scc)

if __name__ == '__main__':
  unittest.main()
