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

import sys
from ttconv.imsc.attributes import TimeExpressionSyntaxEnum
from ttconv.imsc.config import IMSCWriterConfiguration
import ttconv.imsc.reader as imsc_reader
import ttconv.imsc.writer as imsc_writer
import ttconv.scc.writer as scc_writer
import ttconv.scc.reader as scc_reader
import ttconv.vtt.reader as vtt_reader
from ttconv.isd import ISD
from ttconv.scc.config import SCCFrameRate, SccWriterConfiguration
from ttconv.time_code import SmpteTimeCode
from ttconv.model import ContentDocument, Region, Body, Div, P, Span, Text, ContentElement
from ttconv.style_properties import StyleProperties, DisplayType

class SccWriterConfigurationTest(unittest.TestCase):

  def test_defaults(self):
    config = SccWriterConfiguration()

    self.assertEqual(config.allow_reflow, True)
    self.assertEqual(config.force_popon, False)
    self.assertEqual(config.frame_rate, SCCFrameRate.FPS_2997_DF)
    self.assertEqual(config.drop_overlapping_captions, True)

  def test_drop_overlapping_captions(self):
    config = SccWriterConfiguration.parse(json.loads("""{"drop_overlapping_captions": false }"""))
    self.assertEqual(config.drop_overlapping_captions, False)

    config = SccWriterConfiguration.parse(json.loads("""{"drop_overlapping_captions": true }"""))
    self.assertEqual(config.drop_overlapping_captions, True)

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

  _FPS_2997 = Fraction(30000, 1001)

  @staticmethod
  def _read_scc_vtt(name):
    fixture = Path(__file__).parent.parent / "resources" / "scc" / "vtt" / name
    with open(fixture, encoding="utf-8") as f:
      return vtt_reader.to_model(f)

  @classmethod
  def _scc_chunks(cls, scc):
    """Returns [(begin_frame, packet_count)] for each timecoded row of an SCC document."""
    rows = []
    for line in scc.splitlines():
      if "\t" not in line:
        continue
      tc, packets = line.split("\t")
      rows.append((SmpteTimeCode.parse(tc, cls._FPS_2997).to_frames(), len(packets.split())))
    return rows

  @classmethod
  def _rt_display_windows(cls, scc):
    """Round-trips an SCC document and returns each displayed caption's on-screen
    duration in frames (next ISD begin minus this ISD begin)."""
    seq = ISD.generate_isd_sequence(scc_reader.to_model(scc))
    windows = []
    for i, (begin, isd) in enumerate(seq):
      if any(len(r) > 0 for r in isd.iter_regions()):
        end = seq[i + 1][0] if i + 1 < len(seq) else None
        if end is not None:
          windows.append(int(end * cls._FPS_2997) - int(begin * cls._FPS_2997))
    return windows

  def test_dense_popon_emitted_scc_is_ordered(self):
    for name in ("dense_popon_line21.vtt", "dense_popon_cascade.vtt"):
      scc = scc_writer.from_model(self._read_scc_vtt(name), SccWriterConfiguration())
      rows = self._scc_chunks(scc)
      for (begin, count), (next_begin, _) in zip(rows, rows[1:]):
        self.assertGreaterEqual(
          next_begin, begin + count,
          msg=f"overlapping/decreasing chunks in {name}: {rows}")

  def test_dense_popon_default_delays_and_preserves(self):
    # every source caption here can be shown before its own erase, so the default
    # (drop_overlapping_captions true) delays them but drops none
    scc = scc_writer.from_model(self._read_scc_vtt("dense_popon_line21.vtt"), SccWriterConfiguration())

    source_captions = len(list(self._read_scc_vtt("dense_popon_line21.vtt").get_body())[0])
    windows = self._rt_display_windows(scc)

    self.assertEqual(scc.count("9420") // 2, source_captions)
    self.assertEqual(len(windows), source_captions)
    # none self-erased: every emitted caption has a positive on-screen window,
    # including one squeezed short by the collision
    self.assertTrue(all(w > 0 for w in windows), msg=f"self-erased caption: {windows}")
    self.assertLess(min(windows), max(windows))

  def test_dense_popon_default_drops_infeasible(self):
    # a caption that cannot finish its display before its own erase is dropped
    scc = scc_writer.from_model(self._read_scc_vtt("dense_popon_cascade.vtt"), SccWriterConfiguration())

    source_captions = len(list(self._read_scc_vtt("dense_popon_cascade.vtt").get_body())[0])
    emitted_captions = scc.count("9420") // 2
    windows = self._rt_display_windows(scc)

    self.assertLess(emitted_captions, source_captions)
    self.assertEqual(len(windows), emitted_captions)
    self.assertTrue(all(w > 0 for w in windows), msg=f"self-erased caption: {windows}")
    rows = self._scc_chunks(scc)
    for (begin, count), (next_begin, _) in zip(rows, rows[1:]):
      self.assertGreaterEqual(next_begin, begin + count, msg=f"overlap/decrease: {rows}")

  def test_dense_popon_keep_never_drops(self):
    # with drop_overlapping_captions false no caption is ever lost, even when this
    # means pushing erases later and drifting the timeline
    config = SccWriterConfiguration.parse(json.loads("""{"drop_overlapping_captions": false }"""))
    scc = scc_writer.from_model(self._read_scc_vtt("dense_popon_cascade.vtt"), config)

    source_captions = len(list(self._read_scc_vtt("dense_popon_cascade.vtt").get_body())[0])
    emitted_captions = scc.count("9420") // 2
    windows = self._rt_display_windows(scc)

    self.assertEqual(emitted_captions, source_captions)
    self.assertEqual(len(windows), source_captions)
    self.assertTrue(all(w > 0 for w in windows), msg=f"self-erased caption: {windows}")
    rows = self._scc_chunks(scc)
    for (begin, count), (next_begin, _) in zip(rows, rows[1:]):
      self.assertGreaterEqual(next_begin, begin + count, msg=f"overlap/decrease: {rows}")

  def test_dense_popon_no_line_drop(self):
    expected_scc = """Scenarist_SCC V1.0

00:00:28;23	9420 9420 94ae 94ae 1370 1370 c1ec 7661 f2e5 7aa7 7320 70e5 f273 70e5 e3f4 e976 e52c 2049 2061 6d20 64ef 6ee5 9452 9452 20f7 e9f4 6820 f468 e973 2070 f2ef eae5 e3f4 ae20 49a7 6d80 942f 942f

00:00:31;28	9420 9420 94ae 94ae 13d0 13d0 f2e5 6164 7920 e6ef f220 73ef 6de5 f468 e96e 6720 e5ec 73e5 ae20 c4ef 2079 ef75 1370 1370 f468 e96e 6b20 4cef 6e64 ef6e 20f7 ef75 ec64 2062 e520 e56e f4e9 e3e9 6e67 20e5 94d6 94d6 2020 ef75 6768 942c 942c 942f 942f

00:00:36;20	9420 9420 94ae 94ae 94d6 94d6 e6ef f220 68e9 6dbf 942c 942c 942f 942f

00:00:37;13	942c 942c 9420 9420 94ae 94ae 13d0 13d0 4ce5 f420 6de5 20ea 7573 f420 70e9 e36b 2075 7020 ef6e 2073 ef6d e5f4 68e9 6e67 1370 1370 f468 61f4 2079 ef75 206d e56e f4e9 ef6e e564 20f4 68e5 f2e5 2c20 f768 7920 c1f4 9454 9454 2020 e5f4 e9e3 ef20 cd61 64f2 e964 942f 942f

00:00:40;14	9420 9420 94ae 94ae 13d0 13d0 61f2 e56e a7f4 2067 efe9 6e67 20f4 ef20 73e5 ecec 20f4 ef20 c261 f2e3 e5ec ef6e 1370 1370 ae20 d9e5 732c 20f4 68e5 7920 61f2 e520 f2e9 7661 ec73 2c20 79e5 732c 20f4 68e5 94d6 94d6 2020 2061 f2e5 942c 942c 942f 942f

00:00:45;15	942c 942c"""

    scc = scc_writer.from_model(self._read_scc_vtt("dense_popon_line21.vtt"), SccWriterConfiguration())
    self.assertEqual(scc, expected_scc)

    self.assertEqual(scc.count("9420") // 2, 5)

  def test_dense_popon_carry_erase_not_stale(self):
    # a colliding caption is delayed and the previous erase is carried into its
    # chunk, so the stale erase never wipes the caption that follows it
    ttml_doc_str = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml">
  <body><div>
    <p begin="0.633s" end="1.5s">Hi</p>
    <p begin="1.5s" end="2.94s">Let me just pick up on something there</p>
  </div></body>
</tt>"""
    model = imsc_reader.to_model(et.ElementTree(et.fromstring(ttml_doc_str)))
    scc = scc_writer.from_model(model, SccWriterConfiguration())

    self.assertEqual(scc.count("9420") // 2, 2)

    rows = self._scc_chunks(scc)
    for (begin, count), (next_begin, _) in zip(rows, rows[1:]):
      self.assertGreaterEqual(next_begin, begin + count, msg=f"overlap/decrease: {rows}")

    # the erase (942c) is merged in front of the delayed caption's paint (9420),
    # rather than emitted as a standalone row that would erase it
    self.assertTrue(
      any("\t" in l and l.split("\t")[1].startswith("942c 942c 9420") for l in scc.splitlines()),
      msg="previous erase was not carried into the delayed caption's chunk")

    windows = self._rt_display_windows(scc)
    self.assertEqual(len(windows), 2)
    self.assertTrue(all(w > 0 for w in windows), msg=f"self-erased caption: {windows}")

if __name__ == '__main__':
  unittest.main()
