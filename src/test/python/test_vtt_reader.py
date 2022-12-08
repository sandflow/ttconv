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

from ttconv.vtt.reader import to_model
import ttconv.style_properties as styles



class VTTReaderTest(unittest.TestCase):

  def test_sample(self):
    SAMPLE = """WEBVTT

02:00.000 --> 02:05.000
<b>This is bold text</c>

04:00.000 --> 04:05.000
<i>This is italic</i> and this is not
"""

    f = io.StringIO(SAMPLE)

    self.assertIsNotNone(to_model(f))

  def test_bold(self):
    f = io.StringIO(r"""WEBVTT

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
    SAMPLE = """WEBVTT

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

    f = io.StringIO(SAMPLE)
    self.assertIsNotNone(to_model(f))

  def test_italic(self):
    f = io.StringIO(r"""WEBVTT

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
    f = io.StringIO(r"""WEBVTT

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
    f = io.StringIO(r"""WEBVTT

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
    f = io.StringIO(r"""WEBVTT

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
    f = io.StringIO(r"""WEBVTT

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
    f = io.StringIO(r"""WEBVTT

00:02:16.612 --> 00:02:19.376
Hello <b>my
</b> name is Bob
""")
    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontWeight) == styles.FontWeightType.bold:
        break
    else:
      self.fail()

  def test_long_hours(self):
    f = io.StringIO(r"""WEBVTT

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
    f = io.StringIO(r"""WEBVTT

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

if __name__ == '__main__':
  unittest.main()
