#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) Sandflow Consulting LLC
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

'''Unit tests for the NBCU-053 validator'''

import json
import unittest
from fractions import Fraction

from ttconv.imsc.validator.nbcu053.config import NBCU053ValidatorConfiguration
from ttconv.imsc.validator.nbcu053.model import AspectRatio, FrameRate, validate

class FrameRateTests(unittest.TestCase):

  def test_values(self):
    self.assertEqual(
      [(r.nominal_frame_rate, r.frame_rate_multiplier, r.text) for r in FrameRate],
      [(24, Fraction(1000, 1001), "23.98"), (25, Fraction(1), "25"), (30, Fraction(1000, 1001), "29.97")]
    )

  def test_from_text(self):
    for rate in FrameRate:
      self.assertIs(FrameRate.from_text(rate.text), rate)
    for bad in ("30", "23.976", "25.0", "", "abc"):
      with self.subTest(bad):
        with self.assertRaises(ValueError):
          FrameRate.from_text(bad)

class NBCU053ValidatorConfigurationTests(unittest.TestCase):

  def test_name(self):
    self.assertEqual(NBCU053ValidatorConfiguration.name(), "nbcu053")

  def test_all_fields(self):
    config = NBCU053ValidatorConfiguration.parse({"frame_rate": "23.98", "hdr": True, "aspect_ratio": "2.39"})
    self.assertEqual(config.frame_rate, FrameRate.FPS_23_98)
    self.assertTrue(config.hdr)
    self.assertEqual(config.aspect_ratio, AspectRatio.RATIO_2_39)

  def test_defaults(self):
    config = NBCU053ValidatorConfiguration.parse({"frame_rate": "25"})
    self.assertEqual(config.frame_rate, FrameRate.FPS_25)
    self.assertFalse(config.hdr)
    self.assertIsNone(config.aspect_ratio)

  def test_frame_rates(self):
    for frame_rate, expected in (("23.98", FrameRate.FPS_23_98), ("25", FrameRate.FPS_25), ("29.97", FrameRate.FPS_29_97)):
      with self.subTest(frame_rate):
        self.assertEqual(NBCU053ValidatorConfiguration.parse({"frame_rate": frame_rate}).frame_rate, expected)

  def test_aspect_ratios(self):
    for ratio in AspectRatio:
      with self.subTest(ratio.value):
        self.assertEqual(NBCU053ValidatorConfiguration.parse({"frame_rate": "25", "aspect_ratio": ratio.value}).aspect_ratio, ratio)

  def test_null_aspect_ratio(self):
    config = NBCU053ValidatorConfiguration.parse(json.loads('{"frame_rate": "25", "aspect_ratio": null}'))
    self.assertIsNone(config.aspect_ratio)

  def test_frame_rate_is_required(self):
    with self.assertRaises(ValueError):
      NBCU053ValidatorConfiguration.parse({"hdr": True})

  def test_bad_values(self):
    # frame_rate and aspect_ratio are strings from a known set: no number, and no other way of writing them
    for bad in ({"frame_rate": 30}, {"frame_rate": "30"}, {"frame_rate": "abc"}, {"frame_rate": None}, {"frame_rate": ["25"]},
                {"frame_rate": 25}, {"frame_rate": 25.0}, {"frame_rate": 23.98}, {"frame_rate": "25.0"}, {"frame_rate": " 25"},
                {"frame_rate": "23.976"}, {"frame_rate": True},
                {"frame_rate": "25", "aspect_ratio": 2.39}, {"frame_rate": "25", "aspect_ratio": 2.4}, {"frame_rate": "25", "aspect_ratio": 1},
                {"frame_rate": "25", "aspect_ratio": "2.4"}, {"frame_rate": "25", "aspect_ratio": "1"}, {"frame_rate": "25", "aspect_ratio": True},
                {"frame_rate": "25", "aspect_ratio": ["2.39"]}, {"frame_rate": "25", "aspect_ratio": 3},
                {"frame_rate": "25", "aspect_ratio": "3"}, {"frame_rate": "25", "aspect_ratio": "wide"}):
      with self.subTest(bad):
        with self.assertRaises(ValueError):
          NBCU053ValidatorConfiguration.parse(bad)

class NBCU053ValidatorDocumentTests(unittest.TestCase):

  def test_25_sdr_doc(self):
    with open("src/test/resources/ttml/nbcu/valid/nbcu053-25-sdr.ttml", "rb") as f:
      self.assertTrue(validate(f, expected_frame_rate=FrameRate.FPS_25))

  def test_25_hdr_doc(self):
    with open("src/test/resources/ttml/nbcu/valid/nbcu053-25-hdr.ttml", "rb") as f:
      self.assertTrue(validate(
        f,
        expected_frame_rate=FrameRate.FPS_25,
        hdr=True,
        aspect_ratio=AspectRatio.RATIO_2_39
      ))

  def test_2398_hdr_ja_doc(self):
    with open("src/test/resources/ttml/nbcu/valid/nbcu053-2398-hdr-ja.ttml", "rb") as f:
      self.assertTrue(validate(
        f,
        expected_frame_rate=FrameRate.FPS_23_98,
        hdr=True,
        aspect_ratio=AspectRatio.RATIO_2_39
      ))

  def test_2398_hdr_ja_display_aspect_ratio_doc(self):
    with open("src/test/resources/ttml/nbcu/valid/nbcu053-2398-hdr-ja-display-aspect-ratio.ttml", "rb") as f:
      self.assertTrue(validate(
        f,
        expected_frame_rate=FrameRate.FPS_23_98,
        hdr=True,
        aspect_ratio=AspectRatio.RATIO_2_39
      ))

  def test_2398_hdr_ja_bad_vertical_id_doc(self):
    with open("src/test/resources/ttml/nbcu/invalid/nbcu053-2398-hdr-ja-bad-vertical-id.ttml", "rb") as f:
      self.assertFalse(validate(
        f,
        expected_frame_rate=FrameRate.FPS_23_98,
        hdr=True,
        aspect_ratio=AspectRatio.RATIO_2_39
      ))

  def test_2398_hdr_ja_bad_vertical_writingmode_doc(self):
    with open("src/test/resources/ttml/nbcu/invalid/nbcu053-2398-hdr-ja-bad-vertical-writingmode.ttml", "rb") as f:
      self.assertFalse(validate(
        f,
        expected_frame_rate=FrameRate.FPS_23_98,
        hdr=True,
        aspect_ratio=AspectRatio.RATIO_2_39
      ))

  def test_2398_hdr_ja_bad_display_aspect_ratio_doc(self):
    with open("src/test/resources/ttml/nbcu/invalid/nbcu053-2398-hdr-ja-bad-display-aspect-ratio.ttml", "rb") as f:
      self.assertFalse(validate(
        f,
        expected_frame_rate=FrameRate.FPS_23_98,
        hdr=True,
        aspect_ratio=AspectRatio.RATIO_2_39
      ))

  def test_2398_hdr_ja_bad_framerate_doc(self):
    with open("src/test/resources/ttml/nbcu/invalid/nbcu053-2398-hdr-ja-bad-framerate.ttml", "rb") as f:
      self.assertFalse(validate(
        f,
        expected_frame_rate=FrameRate.FPS_23_98,
        hdr=True,
        aspect_ratio=AspectRatio.RATIO_2_39
      ))

  def test_2398_hdr_ja_bad_frameratemultiplier_doc(self):
    with open("src/test/resources/ttml/nbcu/invalid/nbcu053-2398-hdr-ja-bad-frameratemultiplier.ttml", "rb") as f:
      self.assertFalse(validate(
        f,
        expected_frame_rate=FrameRate.FPS_23_98,
        hdr=True,
        aspect_ratio=AspectRatio.RATIO_2_39
      ))

  def test_2398_hdr_ja_bad_vertical_origin_doc(self):
    with open("src/test/resources/ttml/nbcu/invalid/nbcu053-2398-hdr-ja-bad-vertical-origin.ttml", "rb") as f:
      self.assertFalse(validate(
        f,
        expected_frame_rate=FrameRate.FPS_23_98,
        hdr=True,
        aspect_ratio=AspectRatio.RATIO_2_39
      ))

  def test_2398_hdr_ja_bad_region_origin_doc(self):
    with open("src/test/resources/ttml/nbcu/invalid/nbcu053-2398-hdr-ja-bad-region-origin.ttml", "rb") as f:
      self.assertFalse(validate(f, expected_frame_rate=FrameRate.FPS_23_98, hdr=True))

  def test_2398_hdr_ja_bad_region_extent_doc(self):
    with open("src/test/resources/ttml/nbcu/invalid/nbcu053-2398-hdr-ja-bad-region-extent.ttml", "rb") as f:
      self.assertFalse(validate(f, expected_frame_rate=FrameRate.FPS_23_98, hdr=True))

  def test_2398_hdr_ja_bad_region_extent_value_doc(self):
    with open("src/test/resources/ttml/nbcu/invalid/nbcu053-2398-hdr-ja-bad-region-extent-value.ttml", "rb") as f:
      self.assertFalse(validate(f, expected_frame_rate=FrameRate.FPS_23_98, hdr=True))

  def test_2398_hdr_ja_missing_aspect_ratio_param(self):
    with open("src/test/resources/ttml/nbcu/valid/nbcu053-2398-hdr-ja.ttml", "rb") as f:
      self.assertFalse(validate(f, expected_frame_rate=FrameRate.FPS_23_98, hdr=True))

  def test_2398_hdr_ja_missing_luminancegain_doc(self):
    with open("src/test/resources/ttml/nbcu/invalid/nbcu053-2398-hdr-ja-missing-luminancegain.ttml", "rb") as f:
      self.assertFalse(validate(f, expected_frame_rate=FrameRate.FPS_23_98, hdr=True))

  def test_25_sdr_bad_luminancegain_doc(self):
    with open("src/test/resources/ttml/nbcu/invalid/nbcu053-25-sdr-bad-luminancegain.ttml", "rb") as f:
      self.assertFalse(validate(f, expected_frame_rate=FrameRate.FPS_25))

if __name__ == '__main__':
  unittest.main()
