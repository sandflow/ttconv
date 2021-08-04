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

'''Unit tests for the STL reader'''

# pylint: disable=R0201,C0115,C0116

import unittest
import ttconv.stl.reader

class STLReaderTests(unittest.TestCase):

  def test_irt_requirement_0164_001(self):
    with open("src/test/resources/stl/irt/requirement-0164-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  def test_irt_requirement_0224_001(self):
    with open("src/test/resources/stl/irt/requirement-0224-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  def test_irt_requirement_0213_001(self):
    with open("src/test/resources/stl/irt/requirement-0213-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  def test_irt_requirement_0213_002(self):
    with open("src/test/resources/stl/irt/requirement-0213-002.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  def test_irt_requirement_0213_003(self):
    with open("src/test/resources/stl/irt/requirement-0213-003.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  def test_irt_requirement_0213_004(self):
    with open("src/test/resources/stl/irt/requirement-0213-004.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

if __name__ == '__main__':
  unittest.main()