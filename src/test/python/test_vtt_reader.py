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

"""Unit tests for the VTT reader"""

# pylint: disable=R0201,C0115,C0116,W0212
import unittest
import io
import os.path

from ttconv.vtt.reader import to_model
import ttconv.style_properties as styles
import ttconv.model as model


class VTTReaderTest(unittest.TestCase):

  def test_sample(self):
    SAMPLE = b"""WEBVTT

02:00.000 --> 02:05.000
<b>This is bold text</c>

04:00.000 --> 04:05.000
<i>This is italic</i> and this is not
"""
    f = io.BytesIO(SAMPLE)
    self.assertIsNotNone(to_model(f))


  def test_samples(self):
    for root, _subdirs, files in os.walk("src/test/resources/vtt/"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".vtt":
          with self.subTest(name):
            with open(os.path.join(root, filename), "rb") as f:
              self.assertIsNotNone(to_model(f))

  def test_bold(self):
    f = io.BytesIO(b"""WEBVTT

02:00.000 --> 02:05.000
<b>This is bold text</b>
""")
    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontWeight) == styles.FontWeightType.bold:
        break
    else:
      self.fail()

  def test_blank_lines(self):
    # from https://en.wikipedia.org/wiki/SubRip
    SAMPLE = b"""WEBVTT

1
00:02:16.612 --> 00:02:19.376
Senator, we're making
our final approach into Coruscant.


2
00:02:19.482 --> 00:02:21.609
Very good, Lieutenant.

5
00:03:20.476 --> 00:03:22.671
There was no danger at all.



"""

    f = io.BytesIO(SAMPLE)
    self.assertIsNotNone(to_model(f))

  def test_malformed_blank_lines(self):
    # from https://github.com/sandflow/ttconv/issues/439
    # the first cue should be ignored since it is malformed
    SAMPLE = b"""WEBVTT
Kind: captions
Language: en

00:00:00.799 --> 00:00:02.869 align:start position:0%

hi<00:00:01.040><c> everyone</c><00:00:01.920><c> today</c><00:00:02.240><c> we're</c><00:00:02.399><c> going</c><00:00:02.639><c> to</c><00:00:02.720><c> be</c>

00:00:02.869 --> 00:00:02.879 align:start position:0%
hi everyone today we're going to be
"""

    doc = to_model(io.BytesIO(SAMPLE))
    self.assertIsNotNone(doc)
    body = list(doc.get_body())
    self.assertEqual(len(body), 1)
    div = list(body[0])
    self.assertEqual(len(div), 1)

  def test_single_line_with_space(self):
    # from https://github.com/sandflow/ttconv/issues/439
    # the first cue is not ignored since the first line contains a single space
    SAMPLE = b"""WEBVTT
Kind: captions
Language: en

00:00:00.799 --> 00:00:02.869 align:start position:0%
\x20
hi<00:00:01.040><c> everyone</c><00:00:01.920><c> today</c><00:00:02.240><c> we're</c><00:00:02.399><c> going</c><00:00:02.639><c> to</c><00:00:02.720><c> be</c>

00:00:02.869 --> 00:00:02.879 align:start position:0%
hi everyone today we're going to be
"""

    doc = to_model(io.BytesIO(SAMPLE))
    self.assertIsNotNone(doc)
    body = list(doc.get_body())
    self.assertEqual(len(body), 1)
    div = list(body[0])
    self.assertEqual(len(div), 2)

  def test_toplevel_timestamp_tags(self):
    # from https://github.com/sandflow/ttconv/issues/439
    SAMPLE = b"""WEBVTT
Kind: captions
Language: en

00:00:00.799 --> 00:00:02.869 align:start position:0%
\x20
hi<00:00:01.040><c> everyone</c><00:00:01.920><c> today</c><00:00:02.240><c> we're</c><00:00:02.399><c> going</c><00:00:02.639><c> to</c><00:00:02.720><c> be</c>

00:00:02.869 --> 00:00:02.879 align:start position:0%
hi everyone today we're going to be
"""

    doc = to_model(io.BytesIO(SAMPLE))
    body = list(doc.get_body())
    spans_and_brs = list(body[0][0])
    self.assertIsNone(spans_and_brs[0].get_begin()) # \x20
    self.assertIsNone(spans_and_brs[2].get_begin()) # hi
    self.assertEqual(spans_and_brs[3].get_begin(), 1.040 - 0.799) # everyone
    self.assertEqual(spans_and_brs[4].get_begin(), 1.920 - 0.799) # today

  def test_italic(self):
    f = io.BytesIO(b"""WEBVTT

00:02:16.612 --> 00:02:19.376
Hello <i>my</i> name is Bob
""")
    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontStyle) == styles.FontStyleType.italic:
        break
    else:
      self.fail()


  def test_underline(self):
    f = io.BytesIO(b"""WEBVTT

00:02:16.612 --> 00:02:19.376
Hello <u>my</u> name is Bob
""")
    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      text_decoration = e.get_style(styles.StyleProperties.TextDecoration)
      if text_decoration is not None and text_decoration.underline:
        break
    else:
      self.fail()


  def test_blue(self):
    f = io.BytesIO(b"""WEBVTT

02:00.000 --> 02:05.000
<c.blue>This is bold text</c>
""")

    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.Color) == styles.NamedColors.blue.value:
        break
    else:
      self.fail()


  def test_bg_blue(self):
    f = io.BytesIO(b"""WEBVTT

02:00.000 --> 02:05.000
<c.bg_blue>This is bold text</c>
""")

    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.BackgroundColor) == styles.NamedColors.blue.value:
        break
    else:
      self.fail()

  def test_lang(self):
    f = io.BytesIO(b"""WEBVTT

02:00.000 --> 02:05.000
<lang es-419>Spanish as used in Latin America and the Caribbean</lang>
""")

    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      if e.get_lang() == "es-419":
        break
    else:
      self.fail()


  def test_multiline_tags(self):
    f = io.BytesIO(b"""WEBVTT

00:02:16.612 --> 00:02:19.376
Hello <b>my
</b> name is Bob
""")
    doc = to_model(f)
    i = doc.get_body().first_child().first_child().dfs_iterator()

    self.assertIsInstance(next(i), model.P)
    self.assertIsInstance(next(i), model.Span)
    self.assertIsInstance(next(i), model.Text)
    e = next(i)
    self.assertIsInstance(e, model.Span)
    self.assertEqual(e.get_style(styles.StyleProperties.FontWeight), styles.FontWeightType.bold)
    self.assertIsInstance(next(i), model.Span)
    self.assertIsInstance(next(i), model.Text)
    self.assertIsInstance(next(i), model.Br)
    self.assertIsInstance(next(i), model.Span)
    self.assertIsInstance(next(i), model.Text)

  def test_long_hours(self):
    f = io.BytesIO(b"""WEBVTT

101:00:00.000 --> 101:00:01.000
Hello my name is Bob
""")
    doc = to_model(f)

    self.assertEqual(
      363600,
      doc.get_body().first_child().first_child().get_begin()
    )

    self.assertEqual(
      363601,
      doc.get_body().first_child().first_child().get_end()
    )

  def test_ts_tag(self):
    f = io.BytesIO(b"""WEBVTT

00:00:01.000 --> 00:00:03.000
Hello my name<00:02.000>is Bob
""")
    doc = to_model(f)

    self.assertEqual(
      1,
      doc.get_body().first_child().first_child().get_begin()
    )

    second_span = list(doc.get_body().first_child().first_child())[1]

    self.assertEqual(
      1,
      second_span.get_begin()
    )

  def test_ignore_style(self):
    SAMPLE = b"""WEBVTT

STYLE
::cue { color:lime }

00:00:00.000 --> 00:00:25.000
Red or green?
"""
    f = io.BytesIO(SAMPLE)
    self.assertIsNotNone(to_model(f))

  def test_ruby(self):
    # from WPT (bidi_vertical_lr.vrr)
    SAMPLE = b"""WEBVTT

00:00:00.000 --> 00:00:05.000
<ruby>.<rt>\xd7\x90<c>\xd7\x90</c></rt>ab)<rt>x</rt></ruby>
"""
    f = io.BytesIO(SAMPLE)
    self.assertIsNotNone(to_model(f))


  def test_line_origin_extent(self):
    f = io.BytesIO(b"""WEBVTT

1
00:00:00.000 --> 00:00:02.000 line:0
Line 0 starting from top

2
00:00:03.000 --> 00:00:05.000 line:5
Line 5 starting from top

3
00:00:06.000 --> 00:00:08.000 line:45%
Line in percentage

4
00:00:09.000 --> 00:00:11.000 line:-1
Line 1 starting from bottom
""")
    doc = to_model(f)
    regions = list(doc.iter_regions())
    # line 0 starting from top
    self.assertEqual(round(regions[0].get_style(styles.StyleProperties.Origin).y.value), 0)
    self.assertEqual(round(regions[0].get_style(styles.StyleProperties.Extent).height.value), 100)
    # line 5 starting from top
    self.assertEqual(round(regions[1].get_style(styles.StyleProperties.Origin).y.value), 31)
    self.assertEqual(round(regions[1].get_style(styles.StyleProperties.Extent).height.value), 69)
    # line in percentage
    self.assertEqual(round(regions[2].get_style(styles.StyleProperties.Origin).y.value), 45)
    self.assertEqual(round(regions[2].get_style(styles.StyleProperties.Extent).height.value), 55)
    # line 1 starting from bottom
    self.assertEqual(round(regions[3].get_style(styles.StyleProperties.Origin).y.value), 94)
    self.assertEqual(round(regions[3].get_style(styles.StyleProperties.Extent).height.value), 6)

  def _cue_settings_to_region(self, settings: str) -> model.Region:
    f = io.BytesIO(f"""WEBVTT

1
00:00:00.000 --> 00:00:02.000 {settings}
Line 0 starting from top

""".encode('utf-8'))
    doc = to_model(f)
    regions = list(doc.iter_regions())
    self.assertTrue(len(regions), 1)
    return regions[0]

  def test_pos_20_center(self):
    r = self._cue_settings_to_region("position:20%,center")
    o : styles.CoordinateType = r.get_style(styles.StyleProperties.Origin)
    e : styles.ExtentType = r.get_style(styles.StyleProperties.Extent)
    self.assertEqual(o.x.value, 0)
    self.assertEqual(e.width.value, 40)

  def test_pos_90_center(self):
    r = self._cue_settings_to_region("position:90%")
    o : styles.CoordinateType = r.get_style(styles.StyleProperties.Origin)
    e : styles.ExtentType = r.get_style(styles.StyleProperties.Extent)
    self.assertEqual(o.x.value, 80)
    self.assertEqual(e.width.value, 20)

  def test_pos_90_left(self):
    r = self._cue_settings_to_region("position:90%,line-left")
    o : styles.CoordinateType = r.get_style(styles.StyleProperties.Origin)
    e : styles.ExtentType = r.get_style(styles.StyleProperties.Extent)
    self.assertEqual(o.x.value, 90)
    self.assertEqual(e.width.value, 10)

  def test_pos_90_right(self):
    r = self._cue_settings_to_region("position:90%,line-right")
    o : styles.CoordinateType = r.get_style(styles.StyleProperties.Origin)
    e : styles.ExtentType = r.get_style(styles.StyleProperties.Extent)
    self.assertEqual(o.x.value, 0)
    self.assertEqual(e.width.value, 90)

  def test_pos_99_left_10(self):
    r = self._cue_settings_to_region("position:99%,line-left size:10")
    o : styles.CoordinateType = r.get_style(styles.StyleProperties.Origin)
    e : styles.ExtentType = r.get_style(styles.StyleProperties.Extent)
    self.assertEqual(o.x.value, 95)
    self.assertEqual(e.width.value, 5)

  def test_line_99(self):
    r = self._cue_settings_to_region("line:99%")
    o : styles.CoordinateType = r.get_style(styles.StyleProperties.Origin)
    e : styles.ExtentType = r.get_style(styles.StyleProperties.Extent)
    self.assertEqual(o.y.value, 93.75)
    self.assertEqual(e.height.value, 6.25)

  def test_line_minus_3(self):
    r = self._cue_settings_to_region("line:-3")
    o : styles.CoordinateType = r.get_style(styles.StyleProperties.Origin)
    e : styles.ExtentType = r.get_style(styles.StyleProperties.Extent)
    self.assertEqual(o.y.value, 81.25)
    self.assertEqual(e.height.value, 18.75)

  def test_line_minus_3_after(self):
    r = self._cue_settings_to_region("line:-3,end")
    o : styles.CoordinateType = r.get_style(styles.StyleProperties.Origin)
    e : styles.ExtentType = r.get_style(styles.StyleProperties.Extent)
    self.assertEqual(o.y.value, 0)
    self.assertEqual(e.height.value, 81.25)

  def test_line_99_vertical(self):
    r = self._cue_settings_to_region("line:99% vertical:lr")
    o : styles.CoordinateType = r.get_style(styles.StyleProperties.Origin)
    e : styles.ExtentType = r.get_style(styles.StyleProperties.Extent)
    self.assertEqual(o.x.value, 93.75)
    self.assertEqual(e.width.value, 6.25)

  def test_default_positioning(self):
    r = self._cue_settings_to_region("")
    o : styles.CoordinateType = r.get_style(styles.StyleProperties.Origin)
    e : styles.ExtentType = r.get_style(styles.StyleProperties.Extent)
    self.assertEqual(o.y.value, 100*1/23)
    self.assertEqual(e.height.value, 100 - 2*100*1/23)
    self.assertEqual(o.x.value, 100*1/40)
    self.assertEqual(e.width.value, 100 - 2*100*1/40)

if __name__ == '__main__':
  unittest.main()
