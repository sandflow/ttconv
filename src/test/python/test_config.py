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

"""Unit tests for the configuration module"""

# pylint: disable=R0201,C0115,C0116,W0212
import json
from fractions import Fraction
import unittest

from ttconv.config import GeneralConfiguration
from ttconv.imsc.config import TimeExpressionEnum, IMSCWriterConfiguration
from ttconv.isd import ISDConfiguration
from ttconv.tt import CONFIGURATIONS


class ConfigurationTest(unittest.TestCase):

  def test_config_parsing(self):

    config_json = """{
      "general": {
        "progress_bar": false,
        "log_level": "INFO"
      },
      "imsc_writer": {
        "fps": "30000/1001",
        "time_format": "frames"
      },
      "isd" : {
        "multi_thread": false
      },
      "imsc_reader" : {},
      "srt_writer" : {},
      "scc_reader" : {}
    }
    """
    config_dict = json.loads(config_json)

    expected_configurations = [
      GeneralConfiguration(log_level='INFO', progress_bar=False),
      IMSCWriterConfiguration(time_format=TimeExpressionEnum.frames, fps=Fraction(30000, 1001)),
      ISDConfiguration(multi_thread=False)
    ]

    module_configurations = []
    for config_class in CONFIGURATIONS:
      config_value = config_dict.get(config_class.name())

      if config_value is None:
        continue

      module_config = config_class.parse(config_value)

      self.assertIsNotNone(module_config)
      module_configurations.append(module_config)

    for exp_config in expected_configurations:
      self.assertTrue(exp_config in module_configurations)

  def test_default_config_parsing(self):

    config_json = """{
      "imsc_writer": {
        "fps": "30000/1001",
        "time_format": "frames"
      },
      "general": {},
      "isd" : {},
      "imsc_reader" : {},
      "srt_writer" : {},
      "scc_reader" : {}
    }
    """
    config_dict = json.loads(config_json)

    expected_configurations = [
      GeneralConfiguration(),
      IMSCWriterConfiguration(time_format=TimeExpressionEnum.frames, fps=Fraction(30000, 1001)),
      ISDConfiguration()
    ]

    module_configurations = []

    for config_class in CONFIGURATIONS:
      config_value = config_dict.get(config_class.name())

      if config_value is None:
        continue

      module_config = config_class.parse(config_value)

      self.assertIsNotNone(module_config)
      module_configurations.append(module_config)

    for exp_config in expected_configurations:
      self.assertTrue(exp_config in module_configurations)

if __name__ == '__main__':
  unittest.main()
