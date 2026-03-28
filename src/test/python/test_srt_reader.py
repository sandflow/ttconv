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

from ttconv.srt.config import SRTReaderConfiguration
from ttconv.srt.reader import to_model
import ttconv.style_properties as styles
import ttconv.model as model



class SrtReaderTest(unittest.TestCase):

  def test_sample(self):
    # from https://en.wikipedia.org/wiki/SubRip
    SAMPLE = b"""1
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

    f = io.BytesIO(SAMPLE)

    self.assertIsNotNone(to_model(f))

  def test_bold(self):
    f = io.BytesIO(b"""1
00:02:16,612 --> 00:02:19,376
Hello <b>my</b> name is Bob
""")
    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontWeight) == styles.FontWeightType.bold:
        break
    else:
      self.fail()

  def test_blank_lines(self):
    # from https://en.wikipedia.org/wiki/SubRip
    SAMPLE = b"""

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

    f = io.BytesIO(SAMPLE)

    self.assertIsNotNone(to_model(f))

  def test_bold_alt(self):
    srt_data = b"""1
00:02:16,612 --> 00:02:19,376
Hello {bold}my{/bold} name is Bob
"""
    doc = to_model(io.BytesIO(srt_data), SRTReaderConfiguration(extended_tags=True))
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontWeight) == styles.FontWeightType.bold:
        break
    else:
      self.fail()
    doc = to_model(io.BytesIO(srt_data))
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontWeight) == styles.FontWeightType.bold:
        self.fail()

  def test_bold_alt2(self):
    srt_data = b"""1
00:02:16,612 --> 00:02:19,376
Hello <bold>my</bold> name is Bob
"""
    doc = to_model(io.BytesIO(srt_data), SRTReaderConfiguration(extended_tags=True))
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontWeight) == styles.FontWeightType.bold:
        break
    else:
      self.fail()
    doc = to_model(io.BytesIO(srt_data))
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontWeight) == styles.FontWeightType.bold:
        self.fail()

  def test_bold_alt3(self):
    srt_data = b"""1
00:02:16,612 --> 00:02:19,376
Hello {b}my{/b} name is Bob
"""
    doc = to_model(io.BytesIO(srt_data), SRTReaderConfiguration(extended_tags=True))
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontWeight) == styles.FontWeightType.bold:
        break
    else:
      self.fail()
    doc = to_model(io.BytesIO(srt_data))
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontWeight) == styles.FontWeightType.bold:
        self.fail()

  def test_italic(self):
    f = io.BytesIO(b"""1
00:02:16,612 --> 00:02:19,376
Hello <i>my</i> name is Bob
""")
    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontStyle) == styles.FontStyleType.italic:
        break
    else:
      self.fail()

  def test_italic_alt(self):
    srt_data = b"""1
00:02:16,612 --> 00:02:19,376
Hello {italic}my{/italic} name is Bob
"""
    doc = to_model(io.BytesIO(srt_data), SRTReaderConfiguration(extended_tags=True))
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontStyle) == styles.FontStyleType.italic:
        break
    else:
      self.fail()
    doc = to_model(io.BytesIO(srt_data))
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontStyle) == styles.FontStyleType.italic:
        self.fail()

  def test_italic_alt1(self):
    srt_data = b"""1
00:02:16,612 --> 00:02:19,376
Hello {i}my{/i} name is Bob
"""
    doc = to_model(io.BytesIO(srt_data), SRTReaderConfiguration(extended_tags=True))
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontStyle) == styles.FontStyleType.italic:
        break
    else:
      self.fail()
    doc = to_model(io.BytesIO(srt_data))
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontStyle) == styles.FontStyleType.italic:
        self.fail()

  def test_italic_alt2(self):
    srt_data = b"""1
00:02:16,612 --> 00:02:19,376
Hello <italic>my</italic> name is Bob
"""
    doc = to_model(io.BytesIO(srt_data), SRTReaderConfiguration(extended_tags=True))
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontStyle) == styles.FontStyleType.italic:
        break
    else:
      self.fail()
    doc = to_model(io.BytesIO(srt_data))
    for e in doc.get_body().dfs_iterator():
      if e.get_style(styles.StyleProperties.FontStyle) == styles.FontStyleType.italic:
        self.fail()

  def test_underline(self):
    f = io.BytesIO(b"""1
00:02:16,612 --> 00:02:19,376
Hello <u>my</u> name is Bob
""")
    doc = to_model(f)
    for e in doc.get_body().dfs_iterator():
      text_decoration = e.get_style(styles.StyleProperties.TextDecoration)
      if text_decoration is not None and text_decoration.underline:
        break
    else:
      self.fail()

  def test_underline_alt(self):
    srt_data = b"""1
00:02:16,612 --> 00:02:19,376
Hello {underline}my{/underline} name is Bob
"""
    doc = to_model(io.BytesIO(srt_data), SRTReaderConfiguration(extended_tags=True))
    for e in doc.get_body().dfs_iterator():
      text_decoration = e.get_style(styles.StyleProperties.TextDecoration)
      if text_decoration is not None and text_decoration.underline:
        break
    else:
      self.fail()
    doc = to_model(io.BytesIO(srt_data))
    for e in doc.get_body().dfs_iterator():
      text_decoration = e.get_style(styles.StyleProperties.TextDecoration)
      if text_decoration is not None and text_decoration.underline:
        self.fail()

  def test_underline_alt1(self):
    srt_data = b"""1
00:02:16,612 --> 00:02:19,376
Hello {u}my{/u} name is Bob
"""
    doc = to_model(io.BytesIO(srt_data), SRTReaderConfiguration(extended_tags=True))
    for e in doc.get_body().dfs_iterator():
      text_decoration = e.get_style(styles.StyleProperties.TextDecoration)
      if text_decoration is not None and text_decoration.underline:
        break
    else:
      self.fail()
    doc = to_model(io.BytesIO(srt_data))
    for e in doc.get_body().dfs_iterator():
      text_decoration = e.get_style(styles.StyleProperties.TextDecoration)
      if text_decoration is not None and text_decoration.underline:
        self.fail()

  def test_underline_alt2(self):
    srt_data = b"""1
00:02:16,612 --> 00:02:19,376
Hello <underline>my</underline> name is Bob
"""
    doc = to_model(io.BytesIO(srt_data), SRTReaderConfiguration(extended_tags=True))
    for e in doc.get_body().dfs_iterator():
      text_decoration = e.get_style(styles.StyleProperties.TextDecoration)
      if text_decoration is not None and text_decoration.underline:
        break
    else:
      self.fail()
    doc = to_model(io.BytesIO(srt_data))
    for e in doc.get_body().dfs_iterator():
      text_decoration = e.get_style(styles.StyleProperties.TextDecoration)
      if text_decoration is not None and text_decoration.underline:
        self.fail()

  def test_blue(self):
    f = io.BytesIO(b"""1
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
    f = io.BytesIO(b"""1
00:02:16,612 --> 00:02:19,376
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
    f = io.BytesIO(b"""1
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
    f = io.BytesIO(b"""1
101:00:00,000 --> 101:00:01,000
Hello
""")
    doc = to_model(f)

    p_children = list(doc.get_body().first_child().first_child())
    self.assertEqual(len(p_children), 1)
    self.assertIsInstance(p_children[0], model.Span)
    self.assertEqual(p_children[0].first_child().get_text(), "Hello")

  def test_multiline_text(self):
    f = io.BytesIO(b"""1
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

  def test_alignment_tags_disabled_by_default(self):
    """Alignment tags should NOT be parsed when alignment_tags=False (default)"""
    f = io.BytesIO(rb"""1
00:00:00,000 --> 00:00:01,000
{\an1} Bottom Left
""")
    doc = to_model(f)
    # Should only have the default region (r_an2)
    regions = list(doc.iter_regions())
    self.assertEqual(len(regions), 1)
    self.assertEqual(regions[0].get_id(), "r_an2")
    # The alignment tag should remain in the text
    p = doc.get_body().first_child().first_child()
    text_content = ""
    for e in p.dfs_iterator():
      if isinstance(e, model.Text):
        text_content += e.get_text()
    self.assertIn("{\\an1}", text_content)

  def test_alignment_tags_all_positions(self):
    """Test all 9 alignment positions with alignment_tags=True"""
    f = io.BytesIO(rb"""1
00:00:00,000 --> 00:00:01,000
{\an1} V: Bottom - H: Left

2
00:00:02,000 --> 00:00:03,000
{\an2} V: Bottom - H: Center

3
00:00:04,000 --> 00:00:05,000
{\an3} V: Bottom - H: Right

4
00:00:06,000 --> 00:00:07,000
{\an4} V: Center - H: Left

5
00:00:08,000 --> 00:00:09,000
{\an5} V: Center - H: Center

6
00:00:10,000 --> 00:00:11,000
{\an6} V: Center - H: Right

7
00:00:12,000 --> 00:00:13,000
{\an7} V: Top - H: Left

8
00:00:14,000 --> 00:00:15,000
{\an8} V: Top - H: Center

9
00:00:16,000 --> 00:00:17,000
{\an9} V: Top - H: Right
""")
    doc = to_model(f, SRTReaderConfiguration(alignment_tags=True))

    # Should have 9 alignment regions (r_an2 is shared as default)
    regions = list(doc.iter_regions())
    self.assertEqual(len(regions), 9)  # r_an1 through r_an9

    # Check alignment regions exist with correct properties
    expected_alignments = {
      1: (styles.DisplayAlignType.after, styles.TextAlignType.start),
      2: (styles.DisplayAlignType.after, styles.TextAlignType.center),
      3: (styles.DisplayAlignType.after, styles.TextAlignType.end),
      4: (styles.DisplayAlignType.center, styles.TextAlignType.start),
      5: (styles.DisplayAlignType.center, styles.TextAlignType.center),
      6: (styles.DisplayAlignType.center, styles.TextAlignType.end),
      7: (styles.DisplayAlignType.before, styles.TextAlignType.start),
      8: (styles.DisplayAlignType.before, styles.TextAlignType.center),
      9: (styles.DisplayAlignType.before, styles.TextAlignType.end),
    }

    for code, (display_align, text_align) in expected_alignments.items():
      region = doc.get_region(f"r_an{code}")
      self.assertIsNotNone(region, f"Region r_an{code} should exist")
      self.assertEqual(
        region.get_style(styles.StyleProperties.DisplayAlign),
        display_align,
        f"r_an{code} DisplayAlign"
      )
      self.assertEqual(
        region.get_style(styles.StyleProperties.TextAlign),
        text_align,
        f"r_an{code} TextAlign"
      )

  def test_alignment_tag_stripped_from_text(self):
    """Alignment tag should be removed from displayed text"""
    f = io.BytesIO(b"""1
00:00:00,000 --> 00:00:01,000
{\an7} Top Left Text
""")
    doc = to_model(f, SRTReaderConfiguration(alignment_tags=True))
    p = doc.get_body().first_child().first_child()
    text_content = ""
    for e in p.dfs_iterator():
      if isinstance(e, model.Text):
        text_content += e.get_text()
    self.assertNotIn("{\\an", text_content)
    self.assertIn("Top Left Text", text_content)

  def test_alignment_region_safe_area(self):
    """Alignment regions should use fixed 10% safe area margin"""
    f = io.BytesIO(rb"""1
00:00:00,000 --> 00:00:01,000
{\an1} Test
""")
    doc = to_model(f, SRTReaderConfiguration(alignment_tags=True))
    region = doc.get_region("r_an1")
    origin = region.get_style(styles.StyleProperties.Origin)
    extent = region.get_style(styles.StyleProperties.Extent)

    # Fixed 10% safe area: origin at (10%, 10%), extent is (80%, 80%)
    self.assertEqual(origin.x.value, 10)
    self.assertEqual(origin.y.value, 10)
    self.assertEqual(extent.width.value, 80)
    self.assertEqual(extent.height.value, 80)

  def test_alignment_mixed_paragraphs(self):
    """Mix of paragraphs with and without alignment tags"""
    f = io.BytesIO(rb"""1
00:00:00,000 --> 00:00:01,000
No alignment tag here

2
00:00:02,000 --> 00:00:03,000
{\an7} Top left aligned

3
00:00:04,000 --> 00:00:05,000
Also no alignment tag
""")
    doc = to_model(f, SRTReaderConfiguration(alignment_tags=True))

    paragraphs = list(doc.get_body().first_child())
    self.assertEqual(len(paragraphs), 3)

    # First and third paragraphs should not have a region set (use default)
    self.assertIsNone(paragraphs[0].get_region())
    self.assertIsNone(paragraphs[2].get_region())

    # Second paragraph should have r_an7 region
    self.assertEqual(paragraphs[1].get_region().get_id(), "r_an7")

  def test_alignment_region_reuse(self):
    """Multiple paragraphs with same alignment should share region"""
    f = io.BytesIO(rb"""1
00:00:00,000 --> 00:00:01,000
{\an1} First bottom left

2
00:00:02,000 --> 00:00:03,000
{\an1} Second bottom left

3
00:00:04,000 --> 00:00:05,000
{\an9} Top right
""")
    doc = to_model(f, SRTReaderConfiguration(alignment_tags=True))

    paragraphs = list(doc.get_body().first_child())

    # First two paragraphs should share the same region
    self.assertIs(paragraphs[0].get_region(), paragraphs[1].get_region())
    self.assertEqual(paragraphs[0].get_region().get_id(), "r_an1")

    # Third paragraph should have different region
    self.assertEqual(paragraphs[2].get_region().get_id(), "r_an9")

    # Total alignment regions should be 2 (r_an1 and r_an9) + default r_an2
    regions = list(doc.iter_regions())
    self.assertEqual(len(regions), 3)

  def test_alignment_multiple_tags_uses_first(self):
    """Multiple alignment tags in same caption: uses first, removes all"""
    f = io.BytesIO(rb"""1
00:00:00,000 --> 00:00:01,000
{\an1}{\an9} Multiple tags here
""")
    doc = to_model(f, SRTReaderConfiguration(alignment_tags=True))
    p = doc.get_body().first_child().first_child()

    # Should use first alignment (an1 = bottom-left)
    self.assertEqual(p.get_region().get_id(), "r_an1")

    # Both tags should be removed from text
    text_content = ""
    for e in p.dfs_iterator():
      if isinstance(e, model.Text):
        text_content += e.get_text()
    self.assertNotIn("{\\an", text_content)
    self.assertIn("Multiple tags here", text_content)


if __name__ == '__main__':
  unittest.main()
