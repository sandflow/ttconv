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

"""Unit tests for the IMSC 1.1 Text Profile filter.

Based on https://www.w3.org/TR/ttml-imsc1.1/ sections 6, 7.12, and 8.4.
"""

# pylint: disable=R0201,C0115,C0116

import unittest
import io
from fractions import Fraction

import ttconv.model as model
import ttconv.style_properties as styles
from ttconv.filters.doc.imsc11text import IMSC11TextFilter, IMSC11TextFilterConfig
from ttconv.filters.document_filter import DocumentFilter
from ttconv.imsc.designators import IMSC_11_TEXT_PROFILE_DESIGNATOR
from ttconv.vtt.reader import to_model


def _make_simple_doc():
  """Creates a minimal valid ContentDocument with Body > Div > P > Span > Text."""
  doc = model.ContentDocument()

  region = model.Region("r0", doc)
  region.set_style(
    styles.StyleProperties.Origin,
    styles.CoordinateType(
      x=styles.LengthType(0, styles.LengthType.Units.pct),
      y=styles.LengthType(0, styles.LengthType.Units.pct),
    ),
  )
  region.set_style(
    styles.StyleProperties.Extent,
    styles.ExtentType(
      width=styles.LengthType(100, styles.LengthType.Units.pct),
      height=styles.LengthType(100, styles.LengthType.Units.pct),
    ),
  )
  doc.put_region(region)

  body = model.Body(doc)
  doc.set_body(body)

  div = model.Div(doc)
  body.push_child(div)

  p = model.P(doc)
  p.set_begin(Fraction(0))
  p.set_end(Fraction(5))
  p.set_region(region)
  div.push_child(p)

  span = model.Span(doc)
  span.set_style(styles.StyleProperties.Color, styles.NamedColors.white.value)
  p.push_child(span)

  text = model.Text(doc, "Hello world")
  span.push_child(text)

  return doc


class IMSC11TextFilterTest(unittest.TestCase):

  def test_valid_document_passes(self):
    doc = _make_simple_doc()
    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  def test_valid_vtt_document_passes(self):
    f = io.StringIO("WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nHello world\n")
    doc = to_model(f)
    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  def test_empty_document_passes(self):
    doc = model.ContentDocument()
    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  # Section 8.4.7: origin SHALL use px or % only
  def test_origin_rh_unit_raises(self):
    doc = model.ContentDocument()
    region = model.Region("r0", doc)
    region.set_style(
      styles.StyleProperties.Origin,
      styles.CoordinateType(
        x=styles.LengthType(10, styles.LengthType.Units.px),
        y=styles.LengthType(10, styles.LengthType.Units.rh),
      ),
    )
    region.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        width=styles.LengthType(100, styles.LengthType.Units.pct),
        height=styles.LengthType(100, styles.LengthType.Units.pct),
      ),
    )
    doc.put_region(region)

    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  def test_origin_px_pct_passes(self):
    doc = model.ContentDocument()
    region = model.Region("r0", doc)
    region.set_style(
      styles.StyleProperties.Origin,
      styles.CoordinateType(
        x=styles.LengthType(10, styles.LengthType.Units.px),
        y=styles.LengthType(10, styles.LengthType.Units.pct),
      ),
    )
    region.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        width=styles.LengthType(100, styles.LengthType.Units.pct),
        height=styles.LengthType(100, styles.LengthType.Units.pct),
      ),
    )
    doc.put_region(region)

    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  # Section 8.4.2: extent SHALL use px, %, or rh/rw
  def test_extent_rw_rh_passes(self):
    doc = model.ContentDocument()
    region = model.Region("r0", doc)
    region.set_style(
      styles.StyleProperties.Origin,
      styles.CoordinateType(
        x=styles.LengthType(0, styles.LengthType.Units.pct),
        y=styles.LengthType(0, styles.LengthType.Units.pct),
      ),
    )
    region.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        width=styles.LengthType(80, styles.LengthType.Units.rw),
        height=styles.LengthType(80, styles.LengthType.Units.rh),
      ),
    )
    doc.put_region(region)

    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  # Section 8.4.2: extent SHALL be present on all regions
  def test_region_without_extent_raises(self):
    doc = model.ContentDocument()
    region = model.Region("r0", doc)
    doc.put_region(region)

    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  def test_region_extent_from_initial_value_passes(self):
    doc = model.ContentDocument()
    doc.put_initial_value(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        width=styles.LengthType(100, styles.LengthType.Units.pct),
        height=styles.LengthType(100, styles.LengthType.Units.pct),
      ),
    )
    region = model.Region("r0", doc)
    region.set_style(
      styles.StyleProperties.Origin,
      styles.CoordinateType(
        x=styles.LengthType(0, styles.LengthType.Units.pct),
        y=styles.LengthType(0, styles.LengthType.Units.pct),
      ),
    )
    doc.put_region(region)

    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  # Section 8.4.5: negative lengths SHALL NOT be used
  # (except on tts:disparity and tts:textShadow)
  def test_negative_extent_raises(self):
    doc = model.ContentDocument()
    region = model.Region("r0", doc)
    region.set_style(
      styles.StyleProperties.Origin,
      styles.CoordinateType(
        x=styles.LengthType(0, styles.LengthType.Units.pct),
        y=styles.LengthType(0, styles.LengthType.Units.pct),
      ),
    )
    region.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        width=styles.LengthType(100, styles.LengthType.Units.pct),
        height=styles.LengthType(-10, styles.LengthType.Units.pct),
      ),
    )
    doc.put_region(region)

    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  def test_negative_origin_raises(self):
    doc = model.ContentDocument()
    region = model.Region("r0", doc)
    region.set_style(
      styles.StyleProperties.Origin,
      styles.CoordinateType(
        x=styles.LengthType(-5, styles.LengthType.Units.pct),
        y=styles.LengthType(0, styles.LengthType.Units.pct),
      ),
    )
    region.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        width=styles.LengthType(100, styles.LengthType.Units.pct),
        height=styles.LengthType(100, styles.LengthType.Units.pct),
      ),
    )
    doc.put_region(region)

    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  # Section 8.4.12: linePadding only supports c units.
  # The model itself rejects non-c units on LinePadding at set_style() time.
  def test_line_padding_pct_rejected_by_model(self):
    doc = _make_simple_doc()
    for region in doc.iter_regions():
      with self.assertRaises(ValueError):
        region.set_style(
          styles.StyleProperties.LinePadding,
          styles.LengthType(5, styles.LengthType.Units.pct),
        )

  def test_line_padding_c_passes(self):
    doc = _make_simple_doc()
    for region in doc.iter_regions():
      region.set_style(
        styles.StyleProperties.LinePadding,
        styles.LengthType(0.5, styles.LengthType.Units.c),
      )

    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  # Section 8.4.11: textShadow SHALL NOT have more than 4 shadows
  def test_text_shadow_5_shadows_raises(self):
    doc = _make_simple_doc()
    body = doc.get_body()
    for element in body.dfs_iterator():
      if isinstance(element, model.Span):
        shadow = styles.TextShadowType.Shadow(
          x_offset=styles.LengthType(1, styles.LengthType.Units.px),
          y_offset=styles.LengthType(1, styles.LengthType.Units.px),
        )
        element.set_style(
          styles.StyleProperties.TextShadow,
          styles.TextShadowType(shadows=(shadow, shadow, shadow, shadow, shadow)),
        )

    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  def test_text_shadow_4_shadows_passes(self):
    doc = _make_simple_doc()
    body = doc.get_body()
    for element in body.dfs_iterator():
      if isinstance(element, model.Span):
        shadow = styles.TextShadowType.Shadow(
          x_offset=styles.LengthType(1, styles.LengthType.Units.px),
          y_offset=styles.LengthType(1, styles.LengthType.Units.px),
        )
        element.set_style(
          styles.StyleProperties.TextShadow,
          styles.TextShadowType(shadows=(shadow, shadow, shadow, shadow)),
        )

    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  # em units are permitted (#length-em is permitted in section 6)
  def test_em_unit_on_font_size_passes(self):
    doc = _make_simple_doc()
    body = doc.get_body()
    for element in body.dfs_iterator():
      if isinstance(element, model.P):
        element.set_style(
          styles.StyleProperties.FontSize,
          styles.LengthType(1.5, styles.LengthType.Units.em),
        )

    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  def test_line_height_normal_passes(self):
    doc = _make_simple_doc()
    body = doc.get_body()
    for element in body.dfs_iterator():
      if isinstance(element, model.P):
        element.set_style(styles.StyleProperties.LineHeight, styles.SpecialValues.normal)

    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  def test_first_violation_raises(self):
    doc = model.ContentDocument()
    region = model.Region("r0", doc)
    # No extent (violation) and rh unit on origin (violation)
    region.set_style(
      styles.StyleProperties.Origin,
      styles.CoordinateType(
        x=styles.LengthType(10, styles.LengthType.Units.rw),
        y=styles.LengthType(10, styles.LengthType.Units.rh),
      ),
    )
    doc.put_region(region)

    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  # Section 7.12.9: rh/rw units SHALL only appear on Extent, Position, and Origin
  def test_rh_on_font_size_raises(self):
    doc = _make_simple_doc()
    body = doc.get_body()
    for element in body.dfs_iterator():
      if isinstance(element, model.P):
        element.set_style(
          styles.StyleProperties.FontSize,
          styles.LengthType(10, styles.LengthType.Units.rh),
        )

    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  def test_rw_on_line_height_raises(self):
    doc = _make_simple_doc()
    body = doc.get_body()
    for element in body.dfs_iterator():
      if isinstance(element, model.P):
        element.set_style(
          styles.StyleProperties.LineHeight,
          styles.LengthType(10, styles.LengthType.Units.rw),
        )

    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  def test_rh_on_extent_passes(self):
    doc = model.ContentDocument()
    region = model.Region("r0", doc)
    region.set_style(
      styles.StyleProperties.Origin,
      styles.CoordinateType(
        x=styles.LengthType(0, styles.LengthType.Units.pct),
        y=styles.LengthType(0, styles.LengthType.Units.pct),
      ),
    )
    region.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        width=styles.LengthType(100, styles.LengthType.Units.rw),
        height=styles.LengthType(100, styles.LengthType.Units.rh),
      ),
    )
    doc.put_region(region)

    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  # Filter auto-registration
  def test_filter_registered_by_name(self):
    filt_cls = DocumentFilter.get_filter_by_name("imsc11text")
    self.assertIs(filt_cls, IMSC11TextFilter)


if __name__ == "__main__":
  unittest.main()
