#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2021, Sandflow Consulting LLC
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

"""Unit tests for the Vtt writer"""

# pylint: disable=R0201,C0115,C0116,W0212

import os
import unittest
import xml.etree.ElementTree as et
from fractions import Fraction
from pathlib import Path

import ttconv.imsc.reader as imsc_reader
import ttconv.scc.reader as scc_reader
import ttconv.stl.reader as stl_reader
from ttconv.vtt.config import VTTWriterConfiguration
import ttconv.vtt.writer as vtt_writer
from ttconv.model import ContentDocument, Region, Body, Div, P, Span, Text, ContentElement
from ttconv.style_properties import StyleProperties, DisplayType


class VttWriterTest(unittest.TestCase):

  def test_vtt_writer(self):
    doc = ContentDocument()

    r1 = Region("r1", doc)
    doc.put_region(r1)

    r2 = Region("r2", doc)
    r2.set_begin(Fraction(2))
    r2.set_end(Fraction(4))
    doc.put_region(r2)

    body = Body(doc)
    doc.set_body(body)

    div = Div(doc)
    body.push_child(div)

    p = P(doc)
    p.set_region(r1)
    p.set_end(Fraction(2))
    div.push_child(p)

    span = Span(doc)
    span.push_child(Text(doc, "Lorem ipsum dolor sit amet,"))
    p.push_child(span)

    p = P(doc)
    p.set_region(r2)
    div.push_child(p)

    span = Span(doc)
    span.push_child(Text(doc, "consectetur adipiscing elit."))
    p.push_child(span)

    p = P(doc)
    p.set_region(r1)
    p.set_begin(Fraction(4))
    p.set_end(Fraction(6))
    div.push_child(p)

    span = Span(doc)
    span.push_child(Text(doc, "Pellentesque interdum lacinia sollicitudin."))
    p.push_child(span)

    expected_vtt = """WEBVTT

1
00:00:00.000 --> 00:00:02.000
Lorem ipsum dolor sit amet,

2
00:00:02.000 --> 00:00:04.000
consectetur adipiscing elit.

3
00:00:04.000 --> 00:00:06.000
Pellentesque interdum lacinia sollicitudin.
"""

    vtt_from_model = vtt_writer.from_model(doc, None)

    self.assertEqual(expected_vtt, vtt_from_model)

  def test_position(self):
    ttml_doc_str = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en-US" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling" xmlns:ttp="http://www.w3.org/ns/ttml#parameter" xmlns:ttm="http://www.w3.org/ns/ttml#metadata" ttp:frameRate="24" ttp:frameRateMultiplier="1000 1001" ttp:profile="http://www.w3.org/ns/ttml/profile/imsc1/text" ttp:timeBase="media">
  <head>
    <styling>
      <style xml:id="style.center" tts:fontFamily="Arial" tts:fontSize="100%" tts:fontStyle="normal" tts:fontWeight="normal" tts:backgroundColor="transparent" tts:color="white" tts:textAlign="center"/>
    </styling>
    <layout>
      <region xml:id="region.after" tts:displayAlign="after" tts:backgroundColor="transparent" tts:origin="10% 10%" tts:extent="80% 80%"/>
      <region xml:id="region.before" tts:displayAlign="before" tts:backgroundColor="transparent" tts:origin="10% 10%" tts:extent="80% 80%"/>
    </layout>
  </head>
  <body>
    <div>
      <p style="style.center" region="region.after" begin="00:00:03:12" end="00:00:12:00">Only one or two short samples are needed<br/>to make sure the conversion basically works</p>
      <p style="style.center" region="region.before" begin="00:00:14:09" end="00:00:25:17">Cool, got it, will do it by end of next week.</p>
    </div>
  </body>
</tt>"""

    expected_vtt="""WEBVTT

1
00:00:03.501 --> 00:00:12.000 line:90%,after
Only one or two short samples are needed
to make sure the conversion basically works

2
00:00:14.375 --> 00:00:25.709 line:10%,before
Cool, got it, will do it by end of next week.
"""

    model = imsc_reader.to_model(et.ElementTree(et.fromstring(ttml_doc_str)))
    config = VTTWriterConfiguration()
    config.line_position = True
    vtt_from_model = vtt_writer.from_model(model, config)
    self.assertEqual(expected_vtt, vtt_from_model)

  def test_scc_test_suite(self):
    for root, _subdirs, files in os.walk("src/test/resources/scc"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".scc":
          with self.subTest(name):
            path = os.path.join(root, filename)
            scc_content = Path(path).read_text()
            test_model = scc_reader.to_model(scc_content)
            vtt_from_model = vtt_writer.from_model(test_model, None)
            self.assertTrue(len(vtt_from_model) > 0, msg=f"Could not convert {path}")
            self._check_output_vtt(test_model, vtt_from_model, path)

  def test_irt_stl_test_suite(self):
    for root, _subdirs, files in os.walk("src/test/resources/stl/irt"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".stl":
          with self.subTest(name):
            path = os.path.join(root, filename)
            with open(path, "rb") as stl_content:
              test_model = stl_reader.to_model(stl_content)
            vtt_from_model = vtt_writer.from_model(test_model, None)
            self.assertTrue(len(vtt_from_model) > 0, msg=f"Could not convert {path}")
            self._check_output_vtt(test_model, vtt_from_model, path)

  def test_sandflow_stl_test_suite(self):
    for root, _subdirs, files in os.walk("src/test/resources/stl/sandflow"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".stl":
          with self.subTest(name):
            path = os.path.join(root, filename)
            with open(path, "rb") as stl_content:
              test_model = stl_reader.to_model(stl_content)
            vtt_from_model = vtt_writer.from_model(test_model, None)
            self.assertTrue(len(vtt_from_model) > 0, msg=f"Could not convert {path}")
            self._check_output_vtt(test_model, vtt_from_model, path)

  def test_imsc_1_test_suite(self):
    for root, _subdirs, files in os.walk("src/test/resources/ttml/imsc-tests/imsc1/ttml"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".ttml":
          with self.subTest(name):
            path = os.path.join(root, filename)
            tree = et.parse(path)
            test_model = imsc_reader.to_model(tree)
            vtt_from_model = vtt_writer.from_model(test_model, None)
            self._check_output_vtt(test_model, vtt_from_model, path)

  @unittest.skip("Too long to process")
  def test_imsc_1_1_test_suite(self):
    for root, _subdirs, files in os.walk("src/test/resources/ttml/imsc-tests/imsc1_1/ttml"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".ttml":
          with self.subTest(name):
            path = os.path.join(root, filename)
            tree = et.parse(path)
            test_model = imsc_reader.to_model(tree)
            vtt_from_model = vtt_writer.from_model(test_model, None)
            self._check_output_vtt(test_model, vtt_from_model, path)

  @unittest.skip("IMSC 1.2 is not supported")
  def test_imsc_1_2_test_suite(self):
    for root, _subdirs, files in os.walk("src/test/resources/ttml/imsc-tests/imsc1_2/ttml"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".ttml":
          with self.subTest(name):
            path = os.path.join(root, filename)
            tree = et.parse(path)
            test_model = imsc_reader.to_model(tree)
            vtt_from_model =vtt_writer.from_model(test_model, None)
            self._check_output_vtt(test_model, vtt_from_model, path)

  #
  # Utility functions
  #

  def _has_child_paragraphs(self, element: ContentElement) -> bool:
    has_paragraphs = False

    for child in element:
      if child.get_style(StyleProperties.Display) is DisplayType.none and not list(child.iter_animation_steps()):
        continue

      if isinstance(child, P):
        return True

      if isinstance(child, Div):
        has_paragraphs = self._has_child_paragraphs(child)

    return has_paragraphs

  def _has_document_paragraphs(self, doc: ContentDocument) -> bool:
    body = doc.get_body()

    if body is None:
      return False

    paragraphs = False

    for child in body:
      if self._has_child_paragraphs(child):
        return True

    return paragraphs

  def _check_output_vtt(self, model: ContentDocument, vtt: str, path: str):
    if self._has_document_paragraphs(model):
      self.assertTrue(len(vtt) > 0, msg=f"Could not convert {path}")
    else:
      self.assertEqual(8, len(vtt), msg=f"Could not convert {path}")

  def test_empty_isds(self):
    tree = et.parse('src/test/resources/ttml/imsc-tests/imsc1/ttml/timing/BasicTiming010.ttml')
    doc = imsc_reader.to_model(tree)
    srt_from_model = vtt_writer.from_model(doc)

    self.assertEqual(srt_from_model, """WEBVTT

1
00:00:10.000 --> 00:00:24.400
This text must appear at 10 seconds and disappear at 24.4 seconds

2
00:00:25.000 --> 00:00:35.000
This text must appear at 25 seconds and disappear at 35 seconds
""")


if __name__ == '__main__':
  unittest.main()
