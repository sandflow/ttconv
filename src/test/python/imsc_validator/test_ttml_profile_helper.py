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

'''Unit tests for ttconv.imsc.validator.ttml_profile_helper'''

import unittest

import ttconv.imsc.validator.ttml_profile_helper as helper

# '#core' and '#zIndex' are defined by TTML1 (and carried over into TTML2).
# '#animate' and '#xlink' are defined only by TTML2.
_TTML1_NAMESPACE = "http://www.w3.org/ns/ttml/feature/"


class TestIsTtml2FeatureDesignator(unittest.TestCase):

  def test_accepts_feature_designator_carried_over_from_ttml1(self):
    self.assertTrue(helper.is_ttml2_feature_designation(_TTML1_NAMESPACE + "#core"))

  def test_accepts_ttml2_only_feature_designator(self):
    self.assertTrue(helper.is_ttml2_feature_designation(_TTML1_NAMESPACE + "#animate"))

  def test_rejects_unknown_feature_designator(self):
    self.assertFalse(helper.is_ttml2_feature_designation(_TTML1_NAMESPACE + "#bogus"))

  def test_rejects_wrong_namespace(self):
    self.assertFalse(helper.is_ttml2_feature_designation("http://example.com/ns/ttml/feature/#animate"))

  def test_rejects_namespace_without_fragment(self):
    self.assertFalse(helper.is_ttml2_feature_designation(_TTML1_NAMESPACE))

  def test_rejects_bare_fragment(self):
    self.assertFalse(helper.is_ttml2_feature_designation("#animate"))

  def test_rejects_empty_string(self):
    self.assertFalse(helper.is_ttml2_feature_designation(""))


class TestIsTtml2ValidProfileDesignator(unittest.TestCase):

  def test_accepts_relative_standard_designator(self):
    self.assertTrue(helper.is_ttml2_profile_designator("dfxp-full"))

  def test_accepts_another_relative_standard_designator(self):
    self.assertTrue(helper.is_ttml2_profile_designator("ttml2-presentation"))

  def test_rejects_unknown_relative_designator(self):
    self.assertFalse(helper.is_ttml2_profile_designator("bogus"))

  def test_accepts_absolute_standard_designator(self):
    self.assertTrue(helper.is_ttml2_profile_designator("http://www.w3.org/ns/ttml/profile/ttml2-full"))

  def test_rejects_unknown_absolute_designator_under_profile_namespace(self):
    self.assertFalse(helper.is_ttml2_profile_designator("http://www.w3.org/ns/ttml/profile/bar"))

  def test_accepts_custom_absolute_designator_outside_profile_namespace(self):
    self.assertTrue(helper.is_ttml2_profile_designator("http://example.com/my-profile"))

  def test_rejects_empty_string(self):
    self.assertFalse(helper.is_ttml2_profile_designator(""))


class TestAbsolutizeProfileDesignator(unittest.TestCase):

  def test_resolves_simple_relative_designator(self):
    self.assertEqual(
      helper.absolutize_profile_designator("dfxp-full"),
      "http://www.w3.org/ns/ttml/profile/dfxp-full"
    )

  def test_leaves_absolute_designator_unchanged(self):
    self.assertEqual(
      helper.absolutize_profile_designator("http://example.com/my-profile"),
      "http://example.com/my-profile"
    )

  def test_resolves_dot_segments_against_profile_namespace(self):
    # per RFC 3986, 5.3, ".." must be applied against the TT Profile
    # Namespace base URI rather than merely concatenated onto it
    self.assertEqual(
      helper.absolutize_profile_designator("../other/my-profile"),
      "http://www.w3.org/ns/ttml/other/my-profile"
    )

  def test_resolves_network_path_reference_by_replacing_authority(self):
    # a "//" relative reference replaces the base URI's authority entirely,
    # per RFC 3986, 5.3, rather than being appended to the base URI's path
    self.assertEqual(
      helper.absolutize_profile_designator("//example.com/my-profile"),
      "http://example.com/my-profile"
    )

  def test_raises_on_none(self):
    with self.assertRaises(ValueError):
      helper.absolutize_profile_designator(None)


if __name__ == "__main__":
  unittest.main()
