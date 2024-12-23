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

"""Unit tests for the SRT reader"""

# pylint: disable=R0201,C0115,C0116,W0212
import unittest
import io

from ttconv.srt.reader import to_model
import ttconv.style_properties as styles
import ttconv.model as model



class SrtReaderTest(unittest.TestCase):

  def test_sample(self):
    # from https://en.wikipedia.org/wiki/SubRip
    SAMPLE = """1
00:02:16,612 --> 00:02:19,376
Senator, we're making
our final approach into Coruscant.

2
00:02:19,482 --> 00:02:21,609
Very good, Lieutenant.

3
00:03:13,336 --> 00:03:15,167
We made it.

4
00:03:18,608 --> 00:03:20,371
I guess I was wrong.

5
00:03:20,476 --> 00:03:22,671
There was no danger at all."""

    f = io.StringIO(SAMPLE)

    self.assertIsNotNone(to_model(f))

  def test_bold(self):
    f = io.StringIO(r"""1
00:02:16,612 --> 00:02:19,376
Hello <bold>my</bold> name is Bob
""")
    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontWeight) == styles.FontWeightType.bold:
        break
    else:
      self.fail()

  def test_blank_lines(self):
    # from https://en.wikipedia.org/wiki/SubRip
    SAMPLE = """

1
00:02:16,612 --> 00:02:19,376
Senator, we're making
our final approach into Coruscant.


2
00:02:19,482 --> 00:02:21,609
Very good, Lieutenant.

5
00:03:20,476 --> 00:03:22,671
There was no danger at all.



"""

    f = io.StringIO(SAMPLE)

    self.assertIsNotNone(to_model(f))

  def test_bold_alt(self):
    f = io.StringIO(r"""1
00:02:16,612 --> 00:02:19,376
Hello {bold}my{/bold} name is Bob
""")
    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontWeight) == styles.FontWeightType.bold:
        break
    else:
      self.fail()

  def test_italic(self):
    f = io.StringIO(r"""1
00:02:16,612 --> 00:02:19,376
Hello <italic>my</italic> name is Bob
""")
    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontStyle) == styles.FontStyleType.italic:
        break
    else:
      self.fail()

  def test_italic_alt(self):
    f = io.StringIO(r"""1
00:02:16,612 --> 00:02:19,376
Hello {italic}my{/italic} name is Bob
""")
    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontStyle) == styles.FontStyleType.italic:
        break
    else:
      self.fail()

  def test_underline(self):
    f = io.StringIO(r"""1
00:02:16,612 --> 00:02:19,376
Hello <underline>my</underline> name is Bob
""")
    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      text_decoration = e.get_style(styles.StyleProperties.TextDecoration)
      if text_decoration is not None and text_decoration.underline:
        break
    else:
      self.fail()

  def test_underline_alt(self):
    f = io.StringIO(r"""1
00:02:16,612 --> 00:02:19,376
Hello {underline}my{/underline} name is Bob
""")
    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      text_decoration = e.get_style(styles.StyleProperties.TextDecoration)
      if text_decoration is not None and text_decoration.underline:
        break
    else:
      self.fail()

  def test_blue(self):
    f = io.StringIO(r"""1
00:02:16,612 --> 00:02:19,376
Hello <font color='blue'>my</font> name is Bob
""")

    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.Color) == styles.NamedColors.blue.value:
        break
    else:
      self.fail()

  def test_multiline_tags(self):
    f = io.StringIO(r"""1
00:02:16,612 --> 00:02:19,376
Hello <bold>my
</bold> name is Bob
""")
    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontWeight) == styles.FontWeightType.bold:
        break
    else:
      self.fail()

  def test_long_hours(self):
    f = io.StringIO(r"""1
101:00:00,000 --> 101:00:01,000
Hello <bold>my</bold> name is Bob
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

  def test_single_line_text(self):
    f = io.StringIO(r"""1
101:00:00,000 --> 101:00:01,000
Hello
""")
    doc = to_model(f)

    p_children = list(doc.get_body().first_child().first_child())
    self.assertEqual(len(p_children), 1)
    self.assertIsInstance(p_children[0], model.Span)
    self.assertEqual(p_children[0].first_child().get_text(), "Hello")

  def test_multiline_text(self):
    f = io.StringIO(r"""1
101:00:00,000 --> 101:00:01,000
Hello
World
""")
    doc = to_model(f)

    p_children = list(doc.get_body().first_child().first_child())
    self.assertEqual(len(p_children), 3)
    self.assertIsInstance(p_children[0], model.Span)
    self.assertEqual(p_children[0].first_child().get_text(), "Hello")
    self.assertIsInstance(p_children[1], model.Br)
    self.assertIsInstance(p_children[2], model.Span)
    self.assertEqual(p_children[2].first_child().get_text(), "World")


if __name__ == '__main__':
  unittest.main()
