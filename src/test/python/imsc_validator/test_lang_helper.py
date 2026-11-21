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

'''Unit tests for ttconv.imsc.validator.lang_helper'''

import unittest

from ttconv.imsc.validator.lang_helper import get_primary_language_subtag, is_valid_language_tag


class TestIsValidLanguageTag(unittest.TestCase):

  def test_accepts_primary_language_only(self):
    self.assertTrue(is_valid_language_tag("en"))

  def test_accepts_language_and_region(self):
    self.assertTrue(is_valid_language_tag("en-US"))

  def test_accepts_language_script_region(self):
    self.assertTrue(is_valid_language_tag("zh-Hans-CN"))

  def test_accepts_region_as_digits(self):
    self.assertTrue(is_valid_language_tag("es-419"))

  def test_accepts_grandfathered_tag(self):
    self.assertTrue(is_valid_language_tag("i-klingon"))

  def test_accepts_grandfathered_tag_case_insensitive(self):
    self.assertTrue(is_valid_language_tag("I-KLINGON"))

  def test_accepts_privateuse_tag(self):
    self.assertTrue(is_valid_language_tag("x-private-use"))

  def test_rejects_empty_string(self):
    self.assertFalse(is_valid_language_tag(""))

  def test_rejects_malformed_tag(self):
    self.assertFalse(is_valid_language_tag("this-is-not-a-tag-"))


class TestGetPrimaryLanguageSubtag(unittest.TestCase):

  def test_returns_primary_subtag(self):
    self.assertEqual(get_primary_language_subtag("en-US"), "en")

  def test_lowercases_result(self):
    self.assertEqual(get_primary_language_subtag("EN-US"), "en")

  def test_returns_whole_tag_when_no_subtags(self):
    self.assertEqual(get_primary_language_subtag("en"), "en")


if __name__ == "__main__":
  unittest.main()
