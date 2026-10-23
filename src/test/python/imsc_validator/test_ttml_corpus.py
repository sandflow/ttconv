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

'''Regression tests comparing the validator's behavior on the ttml1-tests,
ttml2-tests and imsc-tests corpora against checked-in references.
'''

import unittest
import os
import json
import logging

from ttconv.imsc.validator.imsc11_model import validate

_CORPUS_ROOT = "src/test/resources/ttml"
_REFERENCE_RESULTS_DIR = "src/test/resources/ttml/reference-results"

VALID_SUITE_DIRS = (
  "src/test/resources/ttml/ttml1-tests/validation/valid",
  "src/test/resources/ttml/ttml1-tests/presentation/valid",
  "src/test/resources/ttml/ttml2-tests/validation/valid",
  "src/test/resources/ttml/ttml2-tests/presentation/valid",
  "src/test/resources/ttml/imsc-tests/imsc1/ttml",
  "src/test/resources/ttml/imsc-tests/imsc1_1/ttml",
)

INVALID_SUITE_DIRS = (
  "src/test/resources/ttml/ttml1-tests/validation/invalid",
  "src/test/resources/ttml/ttml2-tests/validation/invalid",
)


def _reference_path(suite_dir: str) -> str:
  '''Maps a corpus directory to its checked-in reference JSON file, one per
  directory, e.g. ".../ttml1-tests/validation/valid" ->
  ".../reference-results/ttml1-tests-validation-valid-results.json".'''
  relative = os.path.relpath(suite_dir, _CORPUS_ROOT)
  name = relative.replace(os.sep, "-")
  return os.path.join(_REFERENCE_RESULTS_DIR, f"{name}-results.json")


def _corpus_files(suite_dir: str) -> dict:
  '''Maps filename -> full path for every .xml/.ttml file found by
  recursively walking suite_dir.'''
  files = {}
  for root, _subdirs, filenames in os.walk(suite_dir):
    for filename in filenames:
      if not filename.endswith((".xml", ".ttml")):
        continue
      # test-harness configuration, not a TTML document
      if filename == "test.config.xml":
        continue
      if filename in files:
        raise ValueError(f"Duplicate filename in {suite_dir}: {filename}")
      files[filename] = os.path.join(root, filename)
  return files

class _CollectingHandler(logging.Handler):
  def __init__(self):
    super().__init__()
    self.records = []

  def emit(self, record):
    self.records.append(record)


def _validate_and_summarize(path: str) -> dict:
  '''Validates the TTML document at path and summarizes the outcome as a
  {"result": "pass"|"fail"|"crash", "errors": [...], "warnings": [...]} dict,
  per the schema of the reference JSON files in
  src/test/resources/ttml/reference-results/.
  Only errors affect "result"; warnings (e.g. deprecated attribute usage) are
  captured for visibility but do not make a document invalid.
  '''
  handler = _CollectingHandler()
  root_logger = logging.getLogger()
  root_logger.addHandler(handler)
  root_logger.setLevel(logging.WARNING)
  try:
    with open(path, "rb") as f:
      validate(f)
    errors = [r.getMessage() for r in handler.records if r.levelno >= logging.ERROR]
    warnings = [r.getMessage() for r in handler.records if r.levelno == logging.WARNING]
    summary: dict = {"result": "fail" if errors else "pass"}
    if errors:
      summary["errors"] = errors
    if warnings:
      summary["warnings"] = warnings
    return summary
  except Exception as e: # pylint: disable=broad-except
    return {"result": "crash", "errors": [repr(e)]}
  finally:
    root_logger.removeHandler(handler)


def _assert_matches_reference(test_case: unittest.TestCase, suite_dir: str, reference_path: str):
  with open(reference_path) as f:
    reference = {entry["file"]: entry for entry in json.load(f)}

  corpus_files = _corpus_files(suite_dir)
  test_case.assertEqual(set(corpus_files.keys()), set(reference.keys()))

  for filename in sorted(corpus_files):
    with test_case.subTest(filename):
      summary = _validate_and_summarize(corpus_files[filename])
      summary["file"] = filename
      test_case.assertEqual(summary, reference[filename])

class TTML1ValidCorpusTests(unittest.TestCase):

  def test_ttml1_valid_corpus_matches_reference(self):
    # These corpora are TTML-valid, not necessarily IMSC-valid (IMSC is a
    # much narrower profile), so failures here are expected and not asserted
    # on directly. Instead, this guards against unintended changes to which
    # files pass/fail and why, against a checked-in reference per directory.
    # If a change in results is expected, regenerate the references by
    # running this file directly (not via unittest) and review the diff
    # before committing it.
    for suite_dir in VALID_SUITE_DIRS:
      with self.subTest(suite_dir):
        _assert_matches_reference(self, suite_dir, _reference_path(suite_dir))

class TTML1InvalidCorpusTests(unittest.TestCase):

  def test_ttml1_invalid_corpus_matches_reference(self):
    # Every file in these corpora is expected to be rejected (as a logged
    # error or a raised exception), but the validator does not yet catch
    # every one of them. Rather than a strict assertion that would be red
    # until every such gap is closed, this compares against a checked-in
    # reference per directory so regressions and improvements are both
    # visible. If a change in results is expected, regenerate the references
    # by running this file directly (not via unittest) and review the diff
    # before committing it.
    for suite_dir in INVALID_SUITE_DIRS:
      with self.subTest(suite_dir):
        _assert_matches_reference(self, suite_dir, _reference_path(suite_dir))


def _generate_reference(suite_dir: str, reference_path: str):  # pragma: no cover
  results = []
  corpus_files = _corpus_files(suite_dir)
  for filename in sorted(corpus_files):
    summary = _validate_and_summarize(corpus_files[filename])
    results.append({"file": filename, **summary})

  with open(reference_path, "w") as f:
    json.dump(results, f, indent=2)
    f.write("\n")

  counts = {}
  for r in results:
    counts[r["result"]] = counts.get(r["result"], 0) + 1
  print(f"Wrote {reference_path}")
  print(f"Total: {len(results)} Counts: {counts}")


if __name__ == '__main__':  # pragma: no cover
  for a_suite_dir in VALID_SUITE_DIRS + INVALID_SUITE_DIRS:
    _generate_reference(a_suite_dir, _reference_path(a_suite_dir))
