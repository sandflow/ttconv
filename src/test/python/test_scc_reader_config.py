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

"""Unit tests for the SCC configuration module"""

# pylint: disable=R0201,C0115,C0116,W0212
import json
import unittest

from ttconv.scc.config import SccReaderConfiguration, SccWriterConfiguration, TextAlignment, SCCReaderFrameRate


class SccReaderConfigurationTest(unittest.TestCase):

  def test_scc_reader_config_text_alignment(self):
    self.assertEqual(TextAlignment.LEFT, TextAlignment.from_value("left"))
    self.assertEqual(TextAlignment.RIGHT, TextAlignment.from_value("right"))
    self.assertEqual(TextAlignment.CENTER, TextAlignment.from_value("center"))
    self.assertEqual(TextAlignment.AUTO, TextAlignment.from_value("auto"))
    self.assertRaisesRegex(ValueError, "Invalid text align 'other' value. Expect: 'left', 'center', 'right' or 'auto'",
                           TextAlignment.from_value, "other")

  def test_scc_reader_config_parsing_default_value(self):
    config_json = "{}"
    config_dict = json.loads(config_json)

    scc_reader_configuration = SccReaderConfiguration.parse(config_dict)

    self.assertEqual(scc_reader_configuration, SccReaderConfiguration(text_align=TextAlignment.AUTO))
    self.assertIsNone(scc_reader_configuration.frame_rate)

  def test_scc_reader_config_parsing_right_value(self):
    config_json = """{"text_align": "right" }"""
    config_dict = json.loads(config_json)

    scc_reader_configuration = SccReaderConfiguration.parse(config_dict)

    self.assertEqual(scc_reader_configuration, SccReaderConfiguration(text_align=TextAlignment.RIGHT))

  def test_scc_reader_config_parsing_left_value(self):
    config_json = """{"text_align": "left" }"""
    config_dict = json.loads(config_json)

    scc_reader_configuration = SccReaderConfiguration.parse(config_dict)

    self.assertEqual(scc_reader_configuration, SccReaderConfiguration(text_align=TextAlignment.LEFT))

  def test_scc_reader_config_parsing_center_value(self):
    config_json = """{"text_align": "center" }"""
    config_dict = json.loads(config_json)

    scc_reader_configuration = SccReaderConfiguration.parse(config_dict)

    self.assertEqual(scc_reader_configuration, SccReaderConfiguration(text_align=TextAlignment.CENTER))

  def test_scc_reader_config_parsing_auto_value(self):
    config_json = """{"text_align": "auto" }"""
    config_dict = json.loads(config_json)

    scc_reader_configuration = SccReaderConfiguration.parse(config_dict)

    self.assertEqual(scc_reader_configuration, SccReaderConfiguration(text_align=TextAlignment.AUTO))

  def test_scc_reader_config_parsing_frame_rate_values(self):
    for label, expected in [("30", SCCReaderFrameRate.FPS_30),
                             ("29.97", SCCReaderFrameRate.FPS_2997),
                             ("25", SCCReaderFrameRate.FPS_25),
                             ("23.976", SCCReaderFrameRate.FPS_2398)]:
      with self.subTest(label=label):
        config = SccReaderConfiguration.parse(json.loads(f'{{"frame_rate": "{label}"}}'))
        self.assertEqual(expected, config.frame_rate)

  def test_scc_reader_config_parsing_invalid_frame_rate_raises(self):
    self.assertRaises(ValueError, SccReaderConfiguration.parse, json.loads('{"frame_rate": "60"}'))


class SCCReaderFrameRateTest(unittest.TestCase):

  def test_from_value_returns_instance_unchanged(self):
    self.assertIs(SCCReaderFrameRate.FPS_2997, SCCReaderFrameRate.from_value(SCCReaderFrameRate.FPS_2997))

  def test_from_value_parses_all_labels(self):
    self.assertIs(SCCReaderFrameRate.FPS_30,   SCCReaderFrameRate.from_value("30"))
    self.assertIs(SCCReaderFrameRate.FPS_2997, SCCReaderFrameRate.from_value("29.97"))
    self.assertIs(SCCReaderFrameRate.FPS_25,   SCCReaderFrameRate.from_value("25"))
    self.assertIs(SCCReaderFrameRate.FPS_2398, SCCReaderFrameRate.from_value("23.976"))

  def test_from_value_invalid_raises(self):
    self.assertRaisesRegex(ValueError, "Invalid SCC Reader Frame Rate '60'",
                           SCCReaderFrameRate.from_value, "60")

if __name__ == '__main__':
  unittest.main()
