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

'''Unit tests for the IMSC validator'''

import contextlib
import unittest
import os
import logging

from ttconv.imsc.validator.imsc11_model import validate

LOGGER = logging.getLogger(__name__)

class _CollectingHandler(logging.Handler):
  def __init__(self):
    super().__init__()
    self.records = []

  def emit(self, record):
    self.records.append(record)

@contextlib.contextmanager
def _assert_no_logs(test_case: unittest.TestCase):
  '''Portable equivalent of TestCase.assertNoLogs(), which is 3.10+ only.
  '''
  root_logger = logging.getLogger()
  handler = _CollectingHandler()
  old_handlers = root_logger.handlers[:]
  old_level = root_logger.level
  old_propagate = root_logger.propagate
  root_logger.handlers = [handler]
  root_logger.setLevel(1)  # capture everything; filtered by level below instead
  root_logger.propagate = False
  try:
    yield
  finally:
    root_logger.handlers = old_handlers
    root_logger.setLevel(old_level)
    root_logger.propagate = old_propagate
  offending = [r for r in handler.records if r.levelno >= logging.ERROR]
  if offending:
    test_case.fail(f"Expected no error messages to be logged, got: {[r.getMessage() for r in offending]}")

class IMSCValidatorDocumentTests(unittest.TestCase):

  def test_documents(self):
    for root, _subdirs, files in os.walk("src/test/resources/ttml/validation/"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".ttml":
          with self.subTest(name):
            with open(os.path.join(root, filename), "rb") as f:
              if name.endswith("invalid"):
                with self.assertLogs(level=logging.ERROR) as logs:
                  validate(f)
              else:
                with _assert_no_logs(self):
                  validate(f)

if __name__ == '__main__':
  unittest.main()

