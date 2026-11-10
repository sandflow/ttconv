#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2026, Sandflow Consulting LLC
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

"""Unit tests for FileTypes.get_file_type edge cases"""

import unittest

from ttconv.tt import FileTypes


class TestGetFileType(unittest.TestCase):

  def test_known_extension(self):
    self.assertIs(FileTypes.get_file_type(None, ".srt"), FileTypes.SRT)

  def test_extension_without_dot(self):
    self.assertIs(FileTypes.get_file_type(None, "srt"), FileTypes.SRT)

  def test_explicit_type(self):
    self.assertIs(FileTypes.get_file_type("srt", ".ttml"), FileTypes.SRT)

  def test_unknown_extension_returns_none(self):
    """An unknown file extension must not raise: the caller reports it cleanly."""
    self.assertIsNone(FileTypes.get_file_type(None, ".xyz"))

  def test_unknown_explicit_type_returns_none(self):
    """An unknown explicit type must not raise: the caller reports it cleanly."""
    self.assertIsNone(FileTypes.get_file_type("xyz", ".srt"))

  def test_missing_extension_returns_none(self):
    self.assertIsNone(FileTypes.get_file_type(None, ""))

  def test_no_type_no_extension_returns_none(self):
    self.assertIsNone(FileTypes.get_file_type(None, None))


if __name__ == "__main__":
  unittest.main()
