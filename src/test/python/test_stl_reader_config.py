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

  def test_disable_line_padding(self):
    config_json = '{"disable_line_padding":true}'
    config = ttconv.stl.config.STLReaderConfiguration.parse(json.loads(config_json))

    with open("src/test/resources/stl/sandflow/setting_background_before_startbox.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f, config)
      self.assertIsNone(doc.get_body().get_style(styles.StyleProperties.LinePadding))

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

if __name__ == '__main__':
  unittest.main()
