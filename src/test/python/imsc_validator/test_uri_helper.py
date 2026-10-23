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

'''Unit tests for ttconv.imsc.validator.uri_helper'''

import unittest

from ttconv.imsc.validator.uri_helper import is_absolute_uri, is_relative_uri, is_uri


class TestIsAbsoluteUri(unittest.TestCase):

  def test_scheme_authority_path(self):
    self.assertTrue(is_absolute_uri("http://example.com/path"))

  def test_scheme_only(self):
    self.assertTrue(is_absolute_uri("mailto:foo@example.com"))

  def test_scheme_with_empty_hier_part(self):
    self.assertTrue(is_absolute_uri("foo:"))

  def test_scheme_with_query(self):
    self.assertTrue(is_absolute_uri("http://example.com/path?q=1&a=b"))

  def test_ipv4_authority(self):
    self.assertTrue(is_absolute_uri("http://192.168.0.1/"))

  def test_ipv6_authority(self):
    self.assertTrue(is_absolute_uri("http://[2001:db8::1]/"))

  def test_ipvfuture_authority(self):
    self.assertTrue(is_absolute_uri("http://[v1.fe80::a+en1]/"))

  def test_userinfo_and_port(self):
    self.assertTrue(is_absolute_uri("http://user:pass@example.com:8080/path"))

  def test_path_rootless(self):
    self.assertTrue(is_absolute_uri("urn:isbn:0451450523"))

  def test_rejects_relative_reference(self):
    self.assertFalse(is_absolute_uri("/path/to/resource"))

  def test_rejects_missing_scheme(self):
    self.assertFalse(is_absolute_uri("example.com/path"))

  def test_rejects_fragment(self):
    self.assertFalse(is_absolute_uri("http://example.com/path#frag"))

  def test_rejects_invalid_scheme(self):
    self.assertFalse(is_absolute_uri("1http://example.com"))

  def test_rejects_empty_string(self):
    self.assertFalse(is_absolute_uri(""))

  def test_rejects_invalid_host_character(self):
    # "{" is not a valid reg-name, IPv4address, or IP-literal character
    self.assertFalse(is_absolute_uri("http://exa{mple.com/"))


class TestIsRelativeUri(unittest.TestCase):

  def test_path_absolute(self):
    self.assertTrue(is_relative_uri("/path/to/resource"))

  def test_path_noscheme(self):
    self.assertTrue(is_relative_uri("path/to/resource"))

  def test_network_path_reference(self):
    self.assertTrue(is_relative_uri("//example.com/path"))

  def test_empty_path(self):
    self.assertTrue(is_relative_uri(""))

  def test_empty_path_with_fragment(self):
    self.assertTrue(is_relative_uri("#"))

  def test_query_only(self):
    self.assertTrue(is_relative_uri("?q=1"))

  def test_with_query_and_fragment(self):
    self.assertTrue(is_relative_uri("path?q=1#frag"))

  def test_dot_segments(self):
    self.assertTrue(is_relative_uri("../sibling/resource.ttml"))

  def test_rejects_absolute_uri_with_scheme(self):
    self.assertFalse(is_relative_uri("http://example.com/path"))

  def test_first_segment_cannot_contain_colon(self):
    # a colon in the first path segment of a path-noscheme reference would
    # otherwise be ambiguous with a URI scheme
    self.assertFalse(is_relative_uri("a:b/c"))

  def test_colon_allowed_in_later_segment(self):
    self.assertTrue(is_relative_uri("a/b:c"))


class TestIsUriReference(unittest.TestCase):

  def test_accepts_absolute_uri(self):
    self.assertTrue(is_uri("http://example.com/path"))

  def test_accepts_absolute_uri_with_fragment(self):
    # unlike is_absolute_uri (RFC 3986, 4.3), URI-reference (4.1) allows a
    # scheme-qualified URI to carry a fragment
    self.assertTrue(is_uri("http://example.com/path#frag"))

  def test_accepts_relative_ref(self):
    self.assertTrue(is_uri("path/to/resource"))

  def test_accepts_dot_segment(self):
    self.assertTrue(is_uri("."))

  def test_accepts_fragment_only(self):
    self.assertTrue(is_uri("#foo"))

  def test_accepts_empty_string(self):
    self.assertTrue(is_uri(""))

  def test_rejects_invalid_characters(self):
    self.assertFalse(is_uri("http://example.com/pa th"))

  def test_rejects_invalid_scheme(self):
    self.assertFalse(is_uri("1http://example.com"))


if __name__ == "__main__":
  unittest.main()
