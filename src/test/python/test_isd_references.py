#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2023, Sandflow Consulting LLC
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

import unittest
import os
import glob
import sys

# Ensure src/test/python is in sys.path to import generate_isd_references
sys.path.insert(0, os.path.join(os.getcwd(), "src", "test", "python"))

import generate_isd_references

class TestISDReferences(unittest.TestCase):

  def test_isd_references(self):
    input_dir = os.path.join("src", "test", "resources", "ttml", "imsc-tests")
    output_dir = os.path.join("src", "test", "resources", "isd-references")
    
    if not os.path.exists(output_dir):
      self.fail(f"Reference directory {output_dir} does not exist.")

    ttml_files = glob.glob(os.path.join(input_dir, "**", "*.ttml"), recursive=True)
    
    for ttml_file in ttml_files:
      with self.subTest(ttml_file=ttml_file):
        
        try:
          generated_content = generate_isd_references.generate_isd_sequence(ttml_file)
        except Exception as e:
          self.fail(f"Failed to generate ISD sequence for {ttml_file}: {e}")

        if not generated_content.strip():
          continue

        rel_path = os.path.relpath(ttml_file, input_dir)
        name_without_ext = os.path.splitext(rel_path)[0]
        output_filename = name_without_ext.replace(os.sep, "_") + ".txt"
        reference_path = os.path.join(output_dir, output_filename)
        
        if not os.path.exists(reference_path):
           self.fail(f"Reference file {reference_path} does not exist for {ttml_file}")

        with open(reference_path, "r", encoding="utf-8") as f:
          reference_content = f.read()
        
        self.assertEqual(generated_content.replace("\r\n", "\n"), reference_content.replace("\r\n", "\n"), f"Content mismatch for {ttml_file}")

if __name__ == '__main__':
  unittest.main()