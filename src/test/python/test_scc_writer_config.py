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
from fractions import Fraction
import json
import unittest

from ttconv.scc.config import SCCFrameRate, SccWriterConfiguration


class SccWriterConfigurationTest(unittest.TestCase):

  def test_defaults(self):
    config = SccWriterConfiguration()

    self.assertEqual(config.allow_reflow, True)
    self.assertEqual(config.force_popon, False)
    self.assertEqual(config.frame_rate, SCCFrameRate.FPS_2997)

  def test_allow_reflow(self):
    config = SccWriterConfiguration.parse(json.loads("""{"allow_reflow": true }"""))
    self.assertEqual(config.allow_reflow, True)

    config = SccWriterConfiguration.parse(json.loads("""{"allow_reflow": false }"""))
    self.assertEqual(config.allow_reflow, False)

  def test_force_popon(self):
    config = SccWriterConfiguration.parse(json.loads("""{"force_popon": true }"""))
    self.assertEqual(config.force_popon, True)

    config = SccWriterConfiguration.parse(json.loads("""{"force_popon": false }"""))
    self.assertEqual(config.force_popon, False)

  def test_rollup_lines(self):
    config = SccWriterConfiguration.parse(json.loads("""{"rollup_lines": 2 }"""))
    self.assertEqual(config.rollup_lines, 2)

    config = SccWriterConfiguration.parse(json.loads("""{"rollup_lines": 3 }"""))
    self.assertEqual(config.rollup_lines, 3)

    config = SccWriterConfiguration.parse(json.loads("""{"rollup_lines": 4 }"""))
    self.assertEqual(config.rollup_lines, 4)

    with self.assertRaises(ValueError):
      config = SccWriterConfiguration.parse(json.loads("""{"rollup_lines": 5 }"""))

  def test_frame_rate(self):
    config = SccWriterConfiguration.parse(json.loads("""{"frame_rate": "30" }"""))
    self.assertEqual(config.frame_rate.fps, Fraction(30))

    config = SccWriterConfiguration.parse(json.loads("""{"frame_rate": "2997" }"""))
    self.assertEqual(config.frame_rate.fps, Fraction(30000, 1001))

    with self.assertRaises(ValueError):
      config = SccWriterConfiguration.parse(json.loads("""{"frame_rate": 30 }"""))

if __name__ == '__main__':
  unittest.main()
