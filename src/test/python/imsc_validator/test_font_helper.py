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

'''Unit tests for ttconv.imsc.validator.font_helper'''

import unittest

from ttconv.imsc.validator.font_helper import is_valid_font_families


class TestIsValidFontFamilies(unittest.TestCase):

  def test_accepts_generic_family_name(self):
    self.assertTrue(is_valid_font_families("serif"))

  def test_accepts_camel_case_generic_family_name(self):
    self.assertTrue(is_valid_font_families("monospaceSerif"))

  def test_accepts_single_word_unquoted_family_name(self):
    self.assertTrue(is_valid_font_families("Arial"))

  def test_accepts_multi_word_unquoted_family_name(self):
    self.assertTrue(is_valid_font_families("Times New Roman"))

  def test_accepts_tab_as_lwsp_within_unquoted_family_name(self):
    self.assertTrue(is_valid_font_families("Arial\tSans"))

  def test_accepts_leading_wsp_before_unquoted_family_name(self):
    self.assertTrue(is_valid_font_families(" Arial"))

  def test_accepts_trailing_wsp_after_unquoted_family_name(self):
    self.assertTrue(is_valid_font_families("Arial "))

  def test_accepts_leading_and_trailing_wsp_around_unquoted_family_name(self):
    self.assertTrue(is_valid_font_families("  Arial  "))

  def test_accepts_interstitial_lwsp_in_unquoted_family_name(self):
    self.assertTrue(is_valid_font_families("New   York"))

  def test_accepts_newline_as_leading_or_trailing_wsp(self):
    self.assertTrue(is_valid_font_families("\nArial\n"))

  def test_accepts_leading_wsp_before_first_unquoted_name_in_list(self):
    self.assertTrue(is_valid_font_families(" Arial, serif"))

  def test_accepts_trailing_wsp_after_last_unquoted_name_in_list(self):
    self.assertTrue(is_valid_font_families("Arial, serif "))

  def test_accepts_double_quoted_family_name(self):
    self.assertTrue(is_valid_font_families('"Times New Roman"'))

  def test_accepts_single_quoted_family_name(self):
    self.assertTrue(is_valid_font_families("'Times New Roman'"))

  def test_accepts_escaped_quote_within_double_quoted_family_name(self):
    self.assertTrue(is_valid_font_families('"Foo \\"Bar\\""'))

  def test_accepts_leading_double_hyphen_within_quoted_family_name(self):
    self.assertTrue(is_valid_font_families('"--not-generic"'))

  def test_accepts_escaped_hyphen_within_unquoted_identifier(self):
    self.assertTrue(is_valid_font_families("Foo\\-Bar"))

  def test_accepts_single_leading_hyphen(self):
    self.assertTrue(is_valid_font_families("-foo"))

  def test_accepts_double_hyphen_not_at_start_of_identifier(self):
    self.assertTrue(is_valid_font_families("a--b"))

  def test_accepts_non_ascii_letters_unescaped(self):
    self.assertTrue(is_valid_font_families("Ünïcödé"))

  def test_accepts_list_of_two_family_names(self):
    self.assertTrue(is_valid_font_families("Arial, serif"))

  def test_accepts_list_without_space_after_comma(self):
    self.assertTrue(is_valid_font_families("Arial,serif"))

  def test_accepts_list_with_extra_lwsp_around_comma(self):
    self.assertTrue(is_valid_font_families("Arial ,  serif"))

  def test_accepts_list_mixing_quoted_and_unquoted_and_non_ascii_names(self):
    self.assertTrue(is_valid_font_families('"Times New Roman", serif, Ünïcödé Sans'))

  def test_rejects_empty_string(self):
    self.assertFalse(is_valid_font_families(""))

  def test_rejects_leading_double_hyphen_at_start(self):
    self.assertFalse(is_valid_font_families("--foo"))

  def test_rejects_leading_double_hyphen_after_comma(self):
    self.assertFalse(is_valid_font_families("Arial, --foo"))

  def test_rejects_leading_double_hyphen_after_lwsp(self):
    self.assertFalse(is_valid_font_families("Arial  --foo"))

  def test_rejects_leading_double_hyphen_after_leading_wsp(self):
    self.assertFalse(is_valid_font_families(" --foo"))

  def test_rejects_leading_wsp_before_quoted_family_name(self):
    self.assertFalse(is_valid_font_families(' "Times New Roman"'))

  def test_rejects_trailing_wsp_after_quoted_family_name(self):
    self.assertFalse(is_valid_font_families('"Times New Roman" '))

  def test_rejects_identifier_starting_with_digit(self):
    self.assertFalse(is_valid_font_families("1abc"))

  def test_rejects_trailing_comma(self):
    self.assertFalse(is_valid_font_families("Arial,"))

  def test_rejects_leading_comma(self):
    self.assertFalse(is_valid_font_families(",Arial"))

  def test_rejects_consecutive_commas(self):
    self.assertFalse(is_valid_font_families("Arial,,serif"))

  def test_rejects_unterminated_quoted_string(self):
    self.assertFalse(is_valid_font_families('"unterminated'))

  def test_rejects_unescaped_quote_within_single_quoted_string(self):
    self.assertFalse(is_valid_font_families("'It's'"))

  def test_rejects_invalid_separator(self):
    self.assertFalse(is_valid_font_families("Arial;serif"))

  def test_rejects_empty_quoted(self):
    self.assertFalse(is_valid_font_families("''"))

  def test_rejects_empty_double_quoted(self):
    self.assertFalse(is_valid_font_families('""'))
  
if __name__ == "__main__":
  unittest.main()
