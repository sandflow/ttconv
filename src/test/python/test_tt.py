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

'''Unit tests for the app'''

# pylint: disable=R0201,C0115,C0116

import os
import io
import unittest
from contextlib import redirect_stdout
from contextlib import redirect_stderr
import ttconv.tt as tt

class IMSCAppTest(unittest.TestCase):

  def setUp(self):
    if not os.path.exists('build'):
      os.makedirs('build')

  def test_convert(self):
    tt.main(["convert",  
      "-i",  "src/test/resources/ttml/body_only.ttml" ,
      "-o", "build/body_only.out.ttml",
      "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])

  def test_convert_input_file_type_ttml(self):
    tt.main(["convert",
      "-i", "src/test/resources/ttml/body_only.ttml",
      "--itype", "ttml",
      "-o", "build/body_only.out.ttml",
      "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])

  def test_convert_input_file_type_TTML(self):
    tt.main(["convert",
      "-i", "src/test/resources/ttml/body_only.ttml",
      "--itype", "TTML",
      "-o", "build/body_only.out.ttml",
      "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])

  def test_convert_output_file_type_ttml(self):
    tt.main(["convert",
      "-i", "src/test/resources/ttml/body_only.ttml",
      "-o", "build/body_only.out.ttml",
      "--otype", "ttml",
      "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])

  def test_convert_output_file_type_TTML(self):
    tt.main(["convert",
      "-i", "src/test/resources/ttml/body_only.ttml",
      "-o", "build/body_only.out.ttml",
      "--otype", "TTML",
      "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])

  def test_convert_input_file_type_scc(self):
    tt.main(["convert", 
      "-i", "src/test/resources/scc/pop-on.scc",
      "--itype", "scc", 
      "-o", "build/pop-on.out.ttml", 
      "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])

  def test_convert_bad_input_file_name(self):
    with self.assertRaises(ValueError):
      tt.main(["convert", 
      "-i", "src/test/resources/ttml/body_only.not_ttml", 
      "-o", "build/body_only.out.ttml", 
      "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])

  def test_convert_bad_output_file_name(self):
    with self.assertRaises(ValueError):
      tt.main(["convert", 
        "-i", "src/test/resources/ttml/body_only.ttml", 
        "-o", "build/body_only.out.not_ttml", 
        "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])

  def test_convert_bad_input_file_arg(self):
    with self.assertRaises(ValueError):
      tt.main(["convert", 
        "-i", "src/test/resources/ttml/body_only.ttml", 
        "-o", "build/body_only.out.ttml", 
        "--itype", "not_ttml", 
        "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])

  def test_convert_bad_output_file_arg(self):
    with self.assertRaises(ValueError):
      tt.main(["convert", 
        "-i", "src/test/resources/ttml/body_only.ttml", 
        "-o", "build/body_only.out.not_ttml", 
        "--otype", "not_ttml", 
        "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])

  def test_convert_mismtach_file_type_and_file_name(self):
    tt.main(["convert", 
      "-i", "src/test/resources/ttml/body_only.ttml", 
      "--itype", "scc", 
      "-o", "build/body_only123.out.ttml", 
      "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])

  def test_pop_on_scc(self):
    tt.main(["convert", 
      "-i", "src/test/resources/scc/pop-on.scc", 
      "-o", "build/pop-on.ttml", 
      "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])
    self.assertTrue(os.path.exists("build/pop-on.ttml"))
    tt.main(["convert", 
      "-i", "src/test/resources/scc/pop-on.scc", 
      "-o", "build/pop-on.srt", 
      "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])
    self.assertTrue(os.path.exists("build/pop-on.srt"))

  def test_paint_on_scc(self):
    tt.main(["convert", 
      "-i", "src/test/resources/scc/paint-on.scc", 
      "-o", "build/paint-on.ttml", 
      "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])
    self.assertTrue(os.path.exists("build/paint-on.ttml"))
    tt.main(["convert", 
      "-i", "src/test/resources/scc/paint-on.scc", 
      "-o", "build/paint-on.srt", 
      "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])
    self.assertTrue(os.path.exists("build/paint-on.srt"))

  def test_mix_rows_roll_up_scc(self):
    tt.main(["convert", 
      "-i", "src/test/resources/scc/mix-rows-roll-up.scc", 
      "-o", "build/mix-rows-roll-up.ttml", 
      "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])
    self.assertTrue(os.path.exists("build/mix-rows-roll-up.ttml"))
    tt.main(["convert", 
      "-i", "src/test/resources/scc/mix-rows-roll-up.scc", 
      "-o", "build/mix-rows-roll-up.srt", 
      "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])
    self.assertTrue(os.path.exists("build/mix-rows-roll-up.srt"))

  def test_bad_function(self):

    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
      # Note passing a bad function name
      #
      with self.assertRaises(SystemExit):
        tt.main("covert")

  def test_with_config(self):
    tt.main(['convert', 
      '-i', 'src/test/resources/ttml/body_only.ttml', 
      '-o', 'build/body_only.out.ttml', 
      '--config', '{"general": {"progress_bar":false, "log_level":"WARN"}}'])

  def test_with_config_file(self):
    tt.main(["convert", 
      "-i", "src/test/resources/ttml/body_only.ttml", 
      "-o", "build/body_only.out.ttml", 
      "--config_file", "src/test/resources/config_files/unit_test_cfg.json"])

  def test_file_types_by_type_and_string(self):
    
    self.assertEqual(None, tt.FileTypes.get_file_type(None, None))

    with self.assertRaises(ValueError):
      tt.FileTypes.get_file_type(None, "")

    with self.assertRaises(ValueError):
      tt.FileTypes.get_file_type(None, "asdf")

    self.assertEqual(tt.FileTypes.TTML, tt.FileTypes.get_file_type(tt.FileTypes.TTML.value, None))
    self.assertEqual(tt.FileTypes.TTML, tt.FileTypes.get_file_type(tt.FileTypes.TTML.value, "asdf"))
    self.assertEqual(tt.FileTypes.TTML, tt.FileTypes.get_file_type(None, "ttml"))

    self.assertEqual(tt.FileTypes.SCC, tt.FileTypes.get_file_type(tt.FileTypes.SCC.value, None))
    self.assertEqual(tt.FileTypes.SCC, tt.FileTypes.get_file_type(tt.FileTypes.SCC.value, "asdf"))
    self.assertEqual(tt.FileTypes.SCC, tt.FileTypes.get_file_type(None, "scc"))

    self.assertEqual(tt.FileTypes.SRT, tt.FileTypes.get_file_type(tt.FileTypes.SRT.value, None))
    self.assertEqual(tt.FileTypes.SRT, tt.FileTypes.get_file_type(tt.FileTypes.SRT.value, "asdf"))
    self.assertEqual(tt.FileTypes.SRT, tt.FileTypes.get_file_type(None, "srt"))

  def test_document_lang_override(self):
    out_path = "build/body_only.out.es-419.ttml"
    in_path = "src/test/resources/ttml/body_only.ttml"

    with open(in_path, encoding="utf-8") as f:
      self.assertNotRegex(f.read(), "lang=['\"]es-419['\"]")
    
    tt.main(['convert', 
      '-i', 'src/test/resources/ttml/body_only.ttml', 
      '-o', out_path, 
      '--config', '{"general": {"progress_bar":false, "document_lang":"es-419"}}'])
    
    with open(out_path, encoding="utf-8") as f:
      self.assertRegex(f.read(), "lang=['\"]es-419['\"]")

  def test_lcd_filter(self):
    out_path = "build/referential_styling.ttml"
    in_path = "src/test/resources/ttml/referential_styling.ttml"

    tt.main(['convert',
      '-i', in_path,
      '-o', out_path,
      '--filter', 'lcd',
      '--config', '{"lcd": {"bg_color": "blue", "safe_area": 0, "color": "red", "preserve_text_align": true}}'
      ])

    tt.main(['convert',
      '-i', in_path,
      '-o', out_path,
      '--filter', 'lcd',
      '--config', '{"lcd": {"bg_color":"red"}}'
      ])

if __name__ == '__main__':
  unittest.main()
