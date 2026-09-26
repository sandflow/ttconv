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
import logging
import tempfile
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

  def test_convert_bad_vtt_signature(self):
    with self.assertRaises(SystemExit):
      tt.main(["convert",
        "-i", "src/test/resources/vtt/invalid/bad-signature.vtt",
        "-o", "build/bad-signature.out.ttml",
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

  def test_log_levels(self):
    log_level = ["DEBUG", "INFO", "WARN", "ERROR"]
    for l in log_level:
      tt.main(['convert',
        '-i', 'src/test/resources/ttml/body_only.ttml',
        '-o', 'build/body_only.out.ttml',
        '--config', f'{{"general": {{"progress_bar": false, "log_level": "{l}"}} }}'])

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
    
  def test_srt_reader_extended_tags(self):
    in_path = "src/test/resources/srt/extended-tags.srt"

    out_path = "build/extended_tags.ttml"
    tt.main(['convert',
      '-i', in_path,
      '-o', out_path,
      '--config', '{"srt_reader": {"extended_tags": true}}'
      ])
    with open(out_path, encoding="utf-8") as f:
      self.assertRegex(f.read(), "fontWeight")
    
    out_path = "build/no-extended_tags.ttml"
    tt.main(['convert',
      '-i', in_path,
      '-o', out_path
      ])
    with open(out_path, encoding="utf-8") as f:
      self.assertNotRegex(f.read(), "fontWeight")

  def test_imsc11filter(self):
    out_path = "build/imsc11filter.ttml"
    in_path = "src/test/resources/ttml/referential_styling.ttml"

    tt.main(['convert',
      '-i', in_path,
      '-o', out_path,
      '--filter', 'imsc11filter'
      ])


class ValidateSubcommandTest(unittest.TestCase):
  '''Unit tests for the "validate" subcommand, which validates a TTML document
  against the IMSC 1.1 model (see ttconv.imsc.validator.imsc11_model).'''

  _VALID_DOCUMENT = "src/test/resources/ttml/validation/tt-body-div-p-two-spans-valid.ttml"
  _INVALID_DOCUMENT = "src/test/resources/ttml/validation/imsc11-condition-attribute-invalid.ttml"

  def setUp(self):
    root_logger = logging.getLogger()
    self._orig_level = root_logger.level
    self._orig_handlers = list(root_logger.handlers)

  def tearDown(self):
    root_logger = logging.getLogger()
    root_logger.handlers = self._orig_handlers
    root_logger.setLevel(self._orig_level)

  def test_valid_document_returns_zero(self):
    with redirect_stderr(io.StringIO()) as stderr:
      self.assertEqual(tt.main(["validate", self._VALID_DOCUMENT]), 0)
    self.assertEqual(stderr.getvalue(), "")

  def test_invalid_document_returns_one_and_prints_error(self):
    with redirect_stderr(io.StringIO()) as stderr:
      self.assertEqual(tt.main(["validate", self._INVALID_DOCUMENT]), 1)
    self.assertIn("ERROR:", stderr.getvalue())

  def test_unknown_log_level_argument_exits_with_usage_error(self):
    with redirect_stderr(io.StringIO()):
      with self.assertRaises(SystemExit) as cm:
        tt.main(["validate", "--log-level", "bogus", self._VALID_DOCUMENT])
    self.assertEqual(cm.exception.code, 2)

  def test_default_model_is_imsc11text(self):
    with redirect_stderr(io.StringIO()) as stderr:
      self.assertEqual(tt.main(["validate", "--model", "imsc11text", self._INVALID_DOCUMENT]), 1)
    self.assertIn("ERROR:", stderr.getvalue())

  def test_unknown_model_argument_exits_with_usage_error(self):
    with redirect_stderr(io.StringIO()):
      with self.assertRaises(SystemExit) as cm:
        tt.main(["validate", "--model", "bogus", self._VALID_DOCUMENT])
    self.assertEqual(cm.exception.code, 2)

  def test_nonexistent_file_argument_exits(self):
    with redirect_stderr(io.StringIO()):
      with self.assertRaises(SystemExit):
        tt.main(["validate", "/nonexistent-file.ttml"])

  def test_log_level_below_error_still_prints_errors(self):
    # "error" is the highest level accepted by --log-level, so error messages
    # are always printed regardless of the level requested
    with redirect_stderr(io.StringIO()) as stderr:
      self.assertEqual(tt.main(["validate", "--log-level", "warning", self._INVALID_DOCUMENT]), 1)
    self.assertIn("ERROR:", stderr.getvalue())


class ValidateNBCU053SubcommandTest(unittest.TestCase):
  '''Unit tests for the "nbcu053" model of the "validate" subcommand, which is configured with --config or --config_file'''

  _VALID_DOCUMENT = "src/test/resources/ttml/nbcu/valid/nbcu053-2398-hdr-ja.ttml"
  _INVALID_DOCUMENT = "src/test/resources/ttml/nbcu/invalid/nbcu053-2398-hdr-ja-bad-framerate.ttml"
  _CONFIG = '{"nbcu053": {"frame_rate": "23.98", "hdr": true, "aspect_ratio": "2.39"}}'

  def setUp(self):
    root_logger = logging.getLogger()
    self._orig_level = root_logger.level
    self._orig_handlers = list(root_logger.handlers)

  def tearDown(self):
    root_logger = logging.getLogger()
    root_logger.handlers = self._orig_handlers
    root_logger.setLevel(self._orig_level)

  def _validate(self, document, *args):
    with redirect_stderr(io.StringIO()) as stderr:
      try:
        return tt.main(["validate", "--model", "nbcu053", *args, document]), stderr.getvalue()
      except SystemExit as e:
        return e.code, stderr.getvalue()

  def test_valid_document_returns_zero(self):
    self.assertEqual(self._validate(self._VALID_DOCUMENT, "--config", self._CONFIG), (0, ""))

  def test_invalid_document_returns_one_and_prints_error(self):
    code, stderr = self._validate(self._INVALID_DOCUMENT, "--config", self._CONFIG)
    self.assertEqual(code, 1)
    self.assertIn("ttp:frameRate SHALL be", stderr)

  def test_config_file(self):
    with tempfile.TemporaryDirectory() as directory:
      path = os.path.join(directory, "config.json")
      with open(path, "w") as f:
        f.write(self._CONFIG)
      self.assertEqual(self._validate(self._VALID_DOCUMENT, "--config_file", path), (0, ""))

  def test_config_file_overrides_config(self):
    with tempfile.TemporaryDirectory() as directory:
      path = os.path.join(directory, "config.json")
      with open(path, "w") as f:
        f.write('{"nbcu053": {"frame_rate": "25"}}')
      # the frame rate of the file, 25, is not the frame rate of the document
      code, _ = self._validate(self._VALID_DOCUMENT, "--config", self._CONFIG, "--config_file", path)
    self.assertEqual(code, 1)

  def test_missing_configuration_exits(self):
    code, stderr = self._validate(self._VALID_DOCUMENT)
    self.assertNotIn(code, (0, None))
    self.assertIn("requires a nbcu053 configuration", stderr)

  def test_missing_frame_rate_exits(self):
    code, stderr = self._validate(self._VALID_DOCUMENT, "--config", '{"nbcu053": {"hdr": true}}')
    self.assertNotIn(code, (0, None))
    self.assertIn("frame_rate", stderr)

  def test_bad_frame_rate_exits(self):
    code, stderr = self._validate(self._VALID_DOCUMENT, "--config", '{"nbcu053": {"frame_rate": 30}}')
    self.assertNotIn(code, (0, None))
    self.assertIn("frame_rate shall be one of", stderr)

  def test_numeric_frame_rate_exits(self):
    # the frame rate is a string, even if it looks like a number
    code, stderr = self._validate(self._VALID_DOCUMENT, "--config", '{"nbcu053": {"frame_rate": 23.98}}')
    self.assertNotIn(code, (0, None))
    self.assertIn("frame_rate shall be one of", stderr)

  def test_configuration_is_ignored_by_other_models(self):
    with redirect_stderr(io.StringIO()):
      self.assertEqual(tt.main(["validate", "--config", self._CONFIG, ValidateSubcommandTest._VALID_DOCUMENT]), 0)


class ValidateEBUTTDSubcommandTest(unittest.TestCase):
  '''Unit tests for the "ebuttd" model of the "validate" subcommand'''

  _VALID_DOCUMENT = "src/test/resources/ttml/ebuttd/valid/example.ttml"
  _INVALID_DOCUMENT = "src/test/resources/ttml/ebuttd/invalid/time_base_not_media.ttml"

  def setUp(self):
    root_logger = logging.getLogger()
    self._orig_level = root_logger.level
    self._orig_handlers = list(root_logger.handlers)

  def tearDown(self):
    root_logger = logging.getLogger()
    root_logger.handlers = self._orig_handlers
    root_logger.setLevel(self._orig_level)

  def test_valid_document_returns_zero(self):
    with redirect_stderr(io.StringIO()) as stderr:
      self.assertEqual(tt.main(["validate", "--model", "ebuttd", self._VALID_DOCUMENT]), 0)
    self.assertEqual(stderr.getvalue(), "")

  def test_invalid_document_returns_one_and_prints_error(self):
    with redirect_stderr(io.StringIO()) as stderr:
      self.assertEqual(tt.main(["validate", "--model", "ebuttd", self._INVALID_DOCUMENT]), 1)
    self.assertIn("ERROR:", stderr.getvalue())


if __name__ == '__main__':
  unittest.main()
