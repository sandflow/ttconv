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

import logging
import os
import unittest
import io
from fractions import Fraction
import ttconv.imsc.reader as imsc_reader
import ttconv.model as model
import ttconv.style_properties as styles
import ttconv.stl.reader as stl_reader
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
    f = io.BytesIO(b"WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nHello world\n")
    doc = to_model(f)
    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  def test_empty_document_passes(self):
    doc = model.ContentDocument()
    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

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
    with self.assertRaises(ValueError):
      for element in body.dfs_iterator():
        if isinstance(element, model.Span):
          shadow = styles.TextShadowType.Shadow(
            x_offset=styles.LengthType(1, styles.LengthType.Units.pct),
            y_offset=styles.LengthType(1, styles.LengthType.Units.pct),
          )
          element.set_style(
            styles.StyleProperties.TextShadow,
            styles.TextShadowType(shadows=(shadow, shadow, shadow, shadow, shadow)),
          )
        IMSC11TextFilter().process(doc)

  def test_text_shadow_4_shadows_passes(self):
    doc = _make_simple_doc()
    body = doc.get_body()
    for element in body.dfs_iterator():
      if isinstance(element, model.Span):
        shadow = styles.TextShadowType.Shadow(
          x_offset=styles.LengthType(1, styles.LengthType.Units.pct),
          y_offset=styles.LengthType(1, styles.LengthType.Units.pct),
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
    # No extent — violates section 8.4.2
    doc.put_region(region)

    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  # rh/rw units are allowed on all properties per maintainer review
  def test_rh_on_font_size_passes(self):
    doc = _make_simple_doc()
    body = doc.get_body()
    for element in body.dfs_iterator():
      if isinstance(element, model.P):
        element.set_style(
          styles.StyleProperties.FontSize,
          styles.LengthType(10, styles.LengthType.Units.rh),
        )

    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

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

  # Section 7.2.18: c units SHALL NOT be present outside of ebutts:linePadding
  def test_c_unit_on_font_size_raises(self):
    doc = _make_simple_doc()
    body = doc.get_body()
    for element in body.dfs_iterator():
      if isinstance(element, model.P):
        element.set_style(
          styles.StyleProperties.FontSize,
          styles.LengthType(1, styles.LengthType.Units.c),
        )

    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  # Section 8.4.13: ebutts:multiRowAlign SHALL only appear on p elements
  def test_multi_row_align_on_span_raises(self):
    doc = _make_simple_doc()
    body = doc.get_body()
    for element in body.dfs_iterator():
      if isinstance(element, model.Span):
        element.set_style(
          styles.StyleProperties.MultiRowAlign,
          styles.MultiRowAlignType.center,
        )

    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  def test_multi_row_align_on_p_passes(self):
    doc = _make_simple_doc()
    body = doc.get_body()
    for element in body.dfs_iterator():
      if isinstance(element, model.P):
        element.set_style(
          styles.StyleProperties.MultiRowAlign,
          styles.MultiRowAlignType.center,
        )

    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  # Section 7.12.1.3: no more than 4 regions per ISD
  def test_more_than_4_regions_raises(self):
    doc = model.ContentDocument()
    regions = []
    for i in range(5):
      region = model.Region(f"r{i}", doc)
      region.set_style(
        styles.StyleProperties.Origin,
        styles.CoordinateType(
          x=styles.LengthType(0, styles.LengthType.Units.pct),
          y=styles.LengthType(i * 20, styles.LengthType.Units.pct),
        ),
      )
      region.set_style(
        styles.StyleProperties.Extent,
        styles.ExtentType(
          width=styles.LengthType(100, styles.LengthType.Units.pct),
          height=styles.LengthType(20, styles.LengthType.Units.pct),
        ),
      )
      doc.put_region(region)
      regions.append(region)

    body = model.Body(doc)
    doc.set_body(body)
    div = model.Div(doc)
    body.push_child(div)

    for region in regions:
      p = model.P(doc)
      p.set_begin(Fraction(0))
      p.set_end(Fraction(5))
      p.set_region(region)
      div.push_child(p)
      span = model.Span(doc)
      p.push_child(span)
      text = model.Text(doc, "Hello")
      span.push_child(text)

    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  def test_4_regions_passes(self):
    doc = model.ContentDocument()
    regions = []
    for i in range(4):
      region = model.Region(f"r{i}", doc)
      region.set_style(
        styles.StyleProperties.Origin,
        styles.CoordinateType(
          x=styles.LengthType(0, styles.LengthType.Units.pct),
          y=styles.LengthType(i * 25, styles.LengthType.Units.pct),
        ),
      )
      region.set_style(
        styles.StyleProperties.Extent,
        styles.ExtentType(
          width=styles.LengthType(100, styles.LengthType.Units.pct),
          height=styles.LengthType(25, styles.LengthType.Units.pct),
        ),
      )
      doc.put_region(region)
      regions.append(region)

    body = model.Body(doc)
    doc.set_body(body)
    div = model.Div(doc)
    body.push_child(div)

    for region in regions:
      p = model.P(doc)
      p.set_begin(Fraction(0))
      p.set_end(Fraction(5))
      p.set_region(region)
      div.push_child(p)
      span = model.Span(doc)
      p.push_child(span)
      text = model.Text(doc, "Hello")
      span.push_child(text)

    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  # Section 8.4.10: textOutline thickness SHALL NOT exceed 10% of fontSize
  def test_text_outline_exceeds_10pct_raises(self):
    doc = _make_simple_doc()
    body = doc.get_body()
    for element in body.dfs_iterator():
      if isinstance(element, model.Span):
        element.set_style(
          styles.StyleProperties.FontSize,
          styles.LengthType(100, styles.LengthType.Units.pct),
        )
        element.set_style(
          styles.StyleProperties.TextOutline,
          styles.TextOutlineType(
            thickness=styles.LengthType(11, styles.LengthType.Units.pct),
          ),
        )

    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  def test_text_outline_within_10pct_passes(self):
    doc = _make_simple_doc()
    body = doc.get_body()
    for element in body.dfs_iterator():
      if isinstance(element, model.Span):
        element.set_style(
          styles.StyleProperties.FontSize,
          styles.LengthType(100, styles.LengthType.Units.pct),
        )
        element.set_style(
          styles.StyleProperties.TextOutline,
          styles.TextOutlineType(
            thickness=styles.LengthType(10, styles.LengthType.Units.pct),
          ),
        )

    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  # Section 8.4.7/8.4.8: document-wide origin/position mutual exclusion
  def test_origin_position_coexist_across_regions_raises(self):
    doc = model.ContentDocument()
    r0 = model.Region("r0", doc)
    r0.set_style(
      styles.StyleProperties.Origin,
      styles.CoordinateType(
        x=styles.LengthType(0, styles.LengthType.Units.pct),
        y=styles.LengthType(0, styles.LengthType.Units.pct),
      ),
    )
    r0.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        width=styles.LengthType(50, styles.LengthType.Units.pct),
        height=styles.LengthType(50, styles.LengthType.Units.pct),
      ),
    )
    doc.put_region(r0)

    r1 = model.Region("r1", doc)
    r1.set_style(
      styles.StyleProperties.Position,
      styles.PositionType(
        h_edge=styles.PositionType.HEdge.left,
        h_offset=styles.LengthType(50, styles.LengthType.Units.pct),
        v_edge=styles.PositionType.VEdge.top,
        v_offset=styles.LengthType(0, styles.LengthType.Units.pct),
      ),
    )
    r1.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        width=styles.LengthType(50, styles.LengthType.Units.pct),
        height=styles.LengthType(50, styles.LengthType.Units.pct),
      ),
    )
    doc.put_region(r1)

    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  def test_all_regions_use_origin_passes(self):
    doc = model.ContentDocument()
    for i in range(2):
      r = model.Region(f"r{i}", doc)
      r.set_style(
        styles.StyleProperties.Origin,
        styles.CoordinateType(
          x=styles.LengthType(i * 50, styles.LengthType.Units.pct),
          y=styles.LengthType(0, styles.LengthType.Units.pct),
        ),
      )
      r.set_style(
        styles.StyleProperties.Extent,
        styles.ExtentType(
          width=styles.LengthType(50, styles.LengthType.Units.pct),
          height=styles.LengthType(50, styles.LengthType.Units.pct),
        ),
      )
      doc.put_region(r)

    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  # Section 8.4.7: tts:origin SHALL use px or % only
  def test_origin_rw_raises(self):
    doc = model.ContentDocument()
    region = model.Region("r0", doc)
    region.set_style(
      styles.StyleProperties.Origin,
      styles.CoordinateType(
        x=styles.LengthType(10, styles.LengthType.Units.rw),
        y=styles.LengthType(10, styles.LengthType.Units.pct),
      ),
    )
    region.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        width=styles.LengthType(80, styles.LengthType.Units.pct),
        height=styles.LengthType(80, styles.LengthType.Units.pct),
      ),
    )
    doc.put_region(region)

    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  # Section 8.4.12: linePadding SHALL use c units only
  def test_line_padding_rh_raises(self):
    doc = _make_simple_doc()
    for region in doc.iter_regions():
      region.set_style(
        styles.StyleProperties.LinePadding,
        styles.LengthType(0.5, styles.LengthType.Units.rh),
      )

    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  def test_line_padding_rw_raises(self):
    doc = _make_simple_doc()
    for region in doc.iter_regions():
      region.set_style(
        styles.StyleProperties.LinePadding,
        styles.LengthType(0.5, styles.LengthType.Units.rw),
      )

    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  # Spatial overlap checks

  def _make_two_region_doc(self, ox1, oy1, ew1, eh1, ox2, oy2, ew2, eh2):
    """Builds a doc with two regions each containing active content.

    All coordinates and sizes are in percent units.
    """
    doc = model.ContentDocument()
    body = model.Body(doc)
    doc.set_body(body)
    div = model.Div(doc)
    body.push_child(div)

    for idx, (ox, oy, ew, eh) in enumerate(
        [(ox1, oy1, ew1, eh1), (ox2, oy2, ew2, eh2)]
    ):
      region = model.Region(f"r{idx}", doc)
      region.set_style(
        styles.StyleProperties.Origin,
        styles.CoordinateType(
          x=styles.LengthType(ox, styles.LengthType.Units.pct),
          y=styles.LengthType(oy, styles.LengthType.Units.pct),
        ),
      )
      region.set_style(
        styles.StyleProperties.Extent,
        styles.ExtentType(
          width=styles.LengthType(ew, styles.LengthType.Units.pct),
          height=styles.LengthType(eh, styles.LengthType.Units.pct),
        ),
      )
      doc.put_region(region)

      p = model.P(doc)
      p.set_begin(Fraction(0))
      p.set_end(Fraction(5))
      p.set_region(region)
      div.push_child(p)
      span = model.Span(doc)
      p.push_child(span)
      text = model.Text(doc, "Hello")
      span.push_child(text)

    return doc

  def test_overlapping_regions_raises(self):
    # r0: x=[0,60], y=[0,50]   r1: x=[40,100], y=[0,50]  → overlap at x=[40,60]
    doc = self._make_two_region_doc(0, 0, 60, 50, 40, 0, 60, 50)
    with self.assertRaises(ValueError):
      IMSC11TextFilter().process(doc)

  def test_abutting_regions_horizontal_passes(self):
    # r0: x=[0,50], y=[0,100]   r1: x=[50,100], y=[0,100]  → share edge, no overlap
    doc = self._make_two_region_doc(0, 0, 50, 100, 50, 0, 50, 100)
    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  def test_abutting_regions_vertical_passes(self):
    # r0: x=[0,100], y=[0,50]   r1: x=[0,100], y=[50,100]  → share edge, no overlap
    doc = self._make_two_region_doc(0, 0, 100, 50, 0, 50, 100, 50)
    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  def test_non_overlapping_regions_with_gap_passes(self):
    # r0: x=[0,40], y=[0,100]   r1: x=[60,100], y=[0,100]  → gap at x=[40,60]
    doc = self._make_two_region_doc(0, 0, 40, 100, 60, 0, 40, 100)
    filt = IMSC11TextFilter()
    filt.process(doc)
    self.assertIn(IMSC_11_TEXT_PROFILE_DESIGNATOR, doc.get_content_profiles())

  # Filter auto-registration
  def test_filter_registered_by_name(self):
    filt_cls = DocumentFilter.get_filter_by_name("imsc11text")
    self.assertIs(filt_cls, IMSC11TextFilter)

  def test_stl_docs(self):
    for root, _subdirs, files in os.walk("src/test/resources/stl"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".stl":
            with self.subTest(name):
              with open(os.path.join(root, filename), "rb") as i_file:
                model = stl_reader.to_model(i_file)
                self.assertIsNotNone(model)
                filt = IMSC11TextFilter()
                filt.process(model)

  def test_imsc_1_test_suite(self):
    for root, _subdirs, files in os.walk("src/test/resources/ttml/imsc-tests/imsc1/ttml"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".ttml":
            with self.subTest(name):
              logging.getLogger().info("*****dummy*****") # dummy log
              with open(os.path.join(root, filename), 'rb') as f:
                model = imsc_reader.to_model(f)
              self.assertIsNotNone(model)
              filt = IMSC11TextFilter()
              filt.process(model)


  def test_imsc_1_1_test_suite(self):
    for root, _subdirs, files in os.walk("src/test/resources/ttml/imsc-tests/imsc1_1/ttml"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".ttml":
            with self.subTest(name):
              logging.getLogger().info("*****dummy*****") # dummy log
              with open(os.path.join(root, filename), 'rb') as f:
                model = imsc_reader.to_model(f)
              self.assertIsNotNone(model)
              filt = IMSC11TextFilter()
              filt.process(model)

  def test_imsc_1_3_test_suite(self):
    for root, _subdirs, files in os.walk("src/test/resources/ttml/imsc-tests/imsc1_3/ttml"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".ttml":
            with self.subTest(name):
              with open(os.path.join(root, filename), 'rb') as f:
                model = imsc_reader.to_model(f)
              self.assertIsNotNone(model)
              filt = IMSC11TextFilter()
              with self.assertRaises(ValueError):
                filt.process(model)

if __name__ == "__main__":
  unittest.main()
