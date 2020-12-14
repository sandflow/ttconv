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

'''Unit tests for logging and progress bar'''

import logging
import unittest
import ttconv.tt as tt

LOGGER = logging.getLogger("ttconv")

class IMSCAppLoggingProgressBarTest(unittest.TestCase):

  def test_logging_info(self):

    with self.assertLogs('ttconv', level='INFO') as cm:
      inputfile = "input"
      outputfile = "output"
      LOGGER.info("Input file is %s", inputfile)
      LOGGER.info("Output file is %s", outputfile)
      LOGGER.info('test 1')

      LOGGER.info('test 2')
      LOGGER.info('test 3')
      LOGGER.info('test 4')
      LOGGER.info('test 5')
      LOGGER.info('test 6')
      LOGGER.info('test 7')

    self.assertEqual(cm.output, [
                                'INFO:ttconv:Input file is input',
                                'INFO:ttconv:Output file is output',
                                'INFO:ttconv:test 1',
                                'INFO:ttconv:test 2',
                                'INFO:ttconv:test 3',
                                'INFO:ttconv:test 4',
                                'INFO:ttconv:test 5',
                                'INFO:ttconv:test 6',
                                'INFO:ttconv:test 7'
                                ])

  def test_logging_progress_bar(self):

    inputfile = "input"
    outputfile = "output"
    LOGGER.info("Input file is %s", inputfile)
    LOGGER.info("Output file is %s", outputfile)
    LOGGER.info('test 1')

    tt.progress_callback(0)
    LOGGER.info('test 2')
    LOGGER.info('test 3')
    tt.progress_callback(0.1)
    tt.progress_callback(1)
    LOGGER.info('test 4')
    tt.progress_callback(0.3)
    LOGGER.info('test 5')
    tt.LOGGER.info('test 6')
    tt.progress_callback(1)
    LOGGER.info('test 7')


  def test_logging_progress_bar_asserts(self):

    with self.assertLogs('ttconv', level='INFO') as cm:
      inputfile = "input"
      outputfile = "output"
      LOGGER.info("Input file is %s", inputfile)
      LOGGER.info("Output file is %s", outputfile)
      LOGGER.info('test 1')

      tt.progress_callback(0)
      LOGGER.info('test 2')
      LOGGER.info('test 3')
      #tt.progress_callback(0.1)
      #tt.progress_callback(1)
      LOGGER.info('test 4')
      #tt.progress_callback(0.3)
      LOGGER.info('test 5')
      LOGGER.info('test 6')
      #tt.progress_callback(1)
      LOGGER.info('test 7')

    self.assertEqual(cm.output, [
                                'INFO:ttconv:Input file is input',
                                'INFO:ttconv:Output file is output',
                                'INFO:ttconv:test 1',
                                'Reading Progress: |--------------------------------------------------| 0.0% Complete',
                                'INFO:ttconv:test 2',
                                'INFO:ttconv:test 3',
                                'INFO:ttconv:test 4',
                                'INFO:ttconv:test 5',
                                'INFO:ttconv:test 6',
                                'INFO:ttconv:test 7'
                                ])

if __name__ == '__main__':
  unittest.main()
