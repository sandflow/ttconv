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

from ttconv.scc.config import SccReaderConfiguration
from ttconv.style_properties import TextAlignType


class SccReaderConfigurationTest(unittest.TestCase):

  def test_scc_reader_config_parsing_default_value(self):
    config_json = "{}"
    config_dict = json.loads(config_json)

    scc_reader_configuration = SccReaderConfiguration.parse(config_dict)

    self.assertEqual(scc_reader_configuration, SccReaderConfiguration(text_align=TextAlignType.start))

  def test_scc_reader_config_parsing_right_value(self):
    config_json = """{"text_align": "right" }"""
    config_dict = json.loads(config_json)

    scc_reader_configuration = SccReaderConfiguration.parse(config_dict)

    self.assertEqual(scc_reader_configuration, SccReaderConfiguration(text_align=TextAlignType.end))

  def test_scc_reader_config_parsing_left_value(self):
    config_json = """{"text_align": "left" }"""
    config_dict = json.loads(config_json)

    scc_reader_configuration = SccReaderConfiguration.parse(config_dict)

    self.assertEqual(scc_reader_configuration, SccReaderConfiguration(text_align=TextAlignType.start))

  def test_scc_reader_config_parsing_center_value(self):
    config_json = """{"text_align": "center" }"""
    config_dict = json.loads(config_json)

    scc_reader_configuration = SccReaderConfiguration.parse(config_dict)

    self.assertEqual(scc_reader_configuration, SccReaderConfiguration(text_align=TextAlignType.center))


if __name__ == '__main__':
  unittest.main()
