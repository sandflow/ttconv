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

'''Unit tests for ttconv.imsc.validator.xml_helper'''

import unittest

from ttconv.imsc.validator.xml_helper import is_valid_xml_name, is_xml_name_char, xml_qname_parts


class TestIsValidXmlName(unittest.TestCase):

  def test_accepts_simple_name(self):
    self.assertTrue(is_valid_xml_name("foo"))

  def test_accepts_underscore_start(self):
    self.assertTrue(is_valid_xml_name("_foo"))

  def test_accepts_digits_after_first_char(self):
    self.assertTrue(is_valid_xml_name("foo123"))

  def test_accepts_hyphen_dot_after_first_char(self):
    self.assertTrue(is_valid_xml_name("foo-bar.baz"))

  def test_accepts_combining_mark_after_first_char(self):
    self.assertTrue(is_valid_xml_name("à"))

  def test_accepts_non_ascii_letter_start(self):
    self.assertTrue(is_valid_xml_name("Àfoo"))

  def test_rejects_leading_digit(self):
    self.assertFalse(is_valid_xml_name("1foo"))

  def test_rejects_leading_hyphen(self):
    self.assertFalse(is_valid_xml_name("-foo"))

  def test_rejects_leading_dot(self):
    self.assertFalse(is_valid_xml_name(".foo"))

  def test_rejects_colon(self):
    # colon is excluded from NCName (reserved for namespace prefix separator)
    self.assertFalse(is_valid_xml_name("foo:bar"))

  def test_rejects_whitespace(self):
    self.assertFalse(is_valid_xml_name("foo bar"))

  def test_rejects_empty_string(self):
    self.assertFalse(is_valid_xml_name(""))


class TestIsXmlNameChar(unittest.TestCase):

  def test_accepts_ascii_letter(self):
    self.assertTrue(is_xml_name_char("a"))

  def test_accepts_digit(self):
    self.assertTrue(is_xml_name_char("9"))

  def test_accepts_hyphen(self):
    self.assertTrue(is_xml_name_char("-"))

  def test_accepts_dot(self):
    self.assertTrue(is_xml_name_char("."))

  def test_accepts_colon(self):
    # unlike is_valid_xml_name, NameChar (XML 1.0, 2.3) includes ':'
    self.assertTrue(is_xml_name_char(":"))

  def test_accepts_combining_mark(self):
    self.assertTrue(is_xml_name_char("̀"))

  def test_rejects_multi_character_string(self):
    self.assertFalse(is_xml_name_char("ab"))

  def test_rejects_empty_string(self):
    self.assertFalse(is_xml_name_char(""))

  def test_rejects_whitespace(self):
    self.assertFalse(is_xml_name_char(" "))

  def test_rejects_disallowed_punctuation(self):
    self.assertFalse(is_xml_name_char("!"))


class TestXmlQnameParts(unittest.TestCase):

  def test_accepts_local_part_only(self):
    self.assertEqual(xml_qname_parts("foo"), (None, "foo"))

  def test_accepts_prefixed_name(self):
    self.assertEqual(xml_qname_parts("foo:bar"), ("foo", "bar"))

  def test_accepts_prefix_and_local_with_digits(self):
    self.assertEqual(xml_qname_parts("ns1:elem2"), ("ns1", "elem2"))

  def test_rejects_leading_digit_in_prefix(self):
    self.assertIsNone(xml_qname_parts("1foo:bar")[1])

  def test_rejects_leading_digit_in_local_part(self):
    self.assertIsNone(xml_qname_parts("foo:1bar")[1])

  def test_rejects_second_colon(self):
    self.assertIsNone(xml_qname_parts("foo:bar:baz")[1])

  def test_rejects_trailing_colon(self):
    self.assertIsNone(xml_qname_parts("foo:")[1])

  def test_rejects_leading_colon(self):
    self.assertIsNone(xml_qname_parts(":foo")[1])

  def test_rejects_empty_string(self):
    self.assertIsNone(xml_qname_parts("")[1])


if __name__ == "__main__":
  unittest.main()
