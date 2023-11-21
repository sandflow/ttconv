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

'''Unit tests for the STL reader configuration'''

# pylint: disable=R0201,C0115,C0116

import unittest
import json

import ttconv.stl.reader
import ttconv.stl.config
import ttconv.style_properties as styles
from ttconv.time_code import SmpteTimeCode, FPS_25

class STLReaderConfigurationTest(unittest.TestCase):

  def test_disable_fill_line_gap(self):
    config_json = '{"disable_fill_line_gap":true}'
    config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads(config_json))

    with open("src/test/resources/stl/sandflow/setting_background_before_startbox.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f, config)
      self.assertIn(doc.get_body().get_style(styles.StyleProperties.FillLineGap), (False, None))

  def test_default_fill_line_gap(self):
    with open("src/test/resources/stl/sandflow/setting_background_before_startbox.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      self.assertEqual(doc.get_body().get_style(styles.StyleProperties.FillLineGap), True)

  def test_enable_fill_line_gap(self):
    config_json = '{"disable_fill_line_gap":false}'
    config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads(config_json))

    with open("src/test/resources/stl/sandflow/setting_background_before_startbox.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f, config)
      self.assertEqual(doc.get_body().get_style(styles.StyleProperties.FillLineGap), True)

  def test_program_start_tc_parsing(self):
    config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads('{"program_start_tc":"00:01:00:12"}'))
    self.assertEqual(config.program_start_tc, "00:01:00:12")

    config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads("{}"))
    self.assertIsNone(config.program_start_tc)

  def test_program_max_row_count_parsing(self):
    config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads('{"max_row_count":2}'))
    self.assertEqual(config.max_row_count, 2)

    config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads('{"max_row_count":"MNR"}'))
    self.assertEqual(config.max_row_count, "MNR")

    config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads("{}"))
    self.assertIsNone(config.max_row_count)

  def test_disable_line_padding(self):
    config_json = '{"disable_line_padding":true}'
    config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads(config_json))

    with open("src/test/resources/stl/sandflow/setting_background_before_startbox.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f, config)
      self.assertIsNone(doc.get_body().get_style(styles.StyleProperties.LinePadding))

  def test_disable_ebu_style(self):
    config_json = '{"disable_ebu_style":true}'
    config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads(config_json))

    with open("src/test/resources/stl/sandflow/setting_background_before_startbox.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f, config)
      self.assertIsNone(doc.get_active_area())
      self.assertIs(doc.get_cell_resolution().rows, 15)
      self.assertIsNone(doc.get_body().get_style(styles.StyleProperties.LinePadding))
      self.assertIsNone(doc.get_body().first_child().first_child().get_style(styles.StyleProperties.FontSize))
      self.assertIsNone(doc.get_body().first_child().first_child().get_style(styles.StyleProperties.LineHeight))

  def test_default_line_padding(self):
    with open("src/test/resources/stl/sandflow/setting_background_before_startbox.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      self.assertIsNotNone(doc.get_body().get_style(styles.StyleProperties.LinePadding))
      self.assertNotEqual(doc.get_body().get_style(styles.StyleProperties.LinePadding).value, 0)

  def test_enable_line_padding(self):
    config_json = '{"disable_line_padding":false}'
    config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads(config_json))

    with open("src/test/resources/stl/sandflow/setting_background_before_startbox.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f, config)
      self.assertIsNotNone(doc.get_body().get_style(styles.StyleProperties.LinePadding))
      self.assertNotEqual(doc.get_body().get_style(styles.StyleProperties.LinePadding).value, 0)
      
  def test_tcp_override_001(self):
    '''Testing TCP Override with 09:00:00:00'''  
    with open("src/test/resources/stl/sandflow/test_tcp_processing.stl", "rb") as f:
      config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads('{"program_start_tc":"09:00:00:00"}'))
      doc = ttconv.stl.reader.to_model(f, config)
      p_list = list(doc.get_body().first_child())
      self.assertEqual(p_list[0].get_begin(),
                      SmpteTimeCode.parse("01:00:00:00",FPS_25).to_temporal_offset())
      self.assertEqual(p_list[0].get_end(),
                      SmpteTimeCode.parse("01:00:01:24",FPS_25).to_temporal_offset())

  def test_tcp_override_002(self):
    '''Testing TCP Override with 00:00:00:00'''  
    with open("src/test/resources/stl/sandflow/test_tcp_processing.stl", "rb") as f:
      config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads('{"program_start_tc":"00:00:00:00"}'))
      doc = ttconv.stl.reader.to_model(f, config)
      p_list = list(doc.get_body().first_child())
      self.assertEqual(p_list[0].get_begin(),
                      SmpteTimeCode.parse("00:00:00:00",FPS_25).to_temporal_offset())
      self.assertEqual(p_list[0].get_end(),
                      SmpteTimeCode.parse("00:00:02:00",FPS_25).to_temporal_offset())
      self.assertEqual(p_list[1].get_begin(),
                      SmpteTimeCode.parse("10:00:00:00",FPS_25).to_temporal_offset())
      self.assertEqual(p_list[1].get_end(),
                      SmpteTimeCode.parse("10:00:01:24",FPS_25).to_temporal_offset())

  def test_tcp_override_003(self):
    '''Testing use of TCP from GSI Block'''  
    with open("src/test/resources/stl/sandflow/test_tcp_processing.stl", "rb") as f:
      config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads('{"program_start_tc":"TCP"}'))
      doc = ttconv.stl.reader.to_model(f, config)
      p_list = list(doc.get_body().first_child())
      self.assertEqual(p_list[0].get_begin(),
                      SmpteTimeCode.parse("00:00:00:00",FPS_25).to_temporal_offset())
      self.assertEqual(p_list[0].get_end(),
                      SmpteTimeCode.parse("00:00:01:24",FPS_25).to_temporal_offset())

  def test_program_font_stack_parsing(self):
    config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads('{"font_stack":"Times New Roman,serif"}'))
    self.assertEqual(config.font_stack, ("Times New Roman", styles.GenericFontFamilyType.serif))

    config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads("{}"))
    self.assertIsNone(config.font_stack)

  def test_font_stack_override(self):
    config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads('{"font_stack":"Times New Roman,serif"}'))

    with open("src/test/resources/stl/sandflow/setting_background_before_startbox.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f, config)
      self.assertEqual(
        doc.get_body().get_style(styles.StyleProperties.FontFamily),
        ("Times New Roman", styles.GenericFontFamilyType.serif)
      )

  def test_force_bottom_align_with_margin(self):
    config_json = '{"force_bottom_align_with_margin":0}'
    config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads(config_json))

    with open("src/test/resources/stl/sandflow/vp01_vp08.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f, config)
      regions = list(doc.iter_regions())
      self.assertIs(len(regions), 1)
      displayAlign = regions[0].get_style(styles.StyleProperties.DisplayAlign)
      origin = regions[0].get_style(styles.StyleProperties.Origin)
      extent = regions[0].get_style(styles.StyleProperties.Extent)
      self.assertIs(displayAlign, styles.DisplayAlignType.after)
      self.assertIs(origin.y.units, styles.LengthType.Units.pct)
      self.assertIs(extent.height.units, styles.LengthType.Units.pct)
      self.assertEqual(origin.y.value + extent.height.value, 100)

if __name__ == '__main__':
  unittest.main()
