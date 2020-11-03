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

"""Unit tests for SCC disassembly format conversion"""

# pylint: disable=R0201,C0115,C0116,W0212

import unittest

from ttconv.scc.reader import to_disassembly


class SccReaderTest(unittest.TestCase):

  def test_scc_disassembly(self):
    scc_content = """Scenarist_SCC V1.0

00:00:00:22	9425 9425 94ad 94ad 9470 9470 4c6f 7265 6d20 6970 7375 6d20 646f 6c6f 7220 7369 7420 616d 6574 2c80

00:00:02:23	9425 9425 94ad 94ad 9673 9673 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e

00:00:20;06	9426 9426 94ad 94ad 9470 9470 5065 6c6c 656e 7465 7371 7565 2069 6e74 6572 6475 6d20 6c61 6369 6e69 6120 736f 6c6c 6963 6974 7564 696e 2e80

00:00:21;24	9426 9426 94ad 94ad 9470 9470 496e 7465 6765 7220 6c75 6374 7573 2065 7420 6c69 6775 6c61 2061 6320 7361 6769 7474 6973 2e80

00:00:49;03	94a7 94ad 9470 5574 2061 7420 6469 616d 2073 6974 2061 6d65 7420 6e75 6c6c 6120 6672 696e 6769 6c6c 6180

00:00:50;23	94a7 94ad 9470 7665 7374 6962 756c 756d 206e 6563 2076 6974 6165 206e 6973 692e

00:02:53:14	9429 9429 94d2 94d2 4c6f 7265 6d20 6970 7375 6d20 646f 6c6f 7220 7369 7420 616d 6574 2c80 94f2 94f2 636f 6e73 6563 7465 7475 7220 6164 6970 6973 6369 6e67 2065 6c69 742e

00:02:56:00	9429 9429 94d2 94d2 5065 6c6c 656e 7465 7371 7565 2069 6e74 6572 6475 6d20 6c61 6369 6e69 6120 736f 6c6c 6963 6974 7564 696e 2e80

00:02:56:25	9429 9429 94f2 94f2 496e 7465 6765 7220 6c75 6374 7573 2065 7420 6c69 6775 6c61 2061 6320 7361 6769 7474 6973 2e80

01:02:53:14	94ae 94ae 9420 9420 947a 947a 97a2 97a2 a820 68ef f26e 2068 ef6e 6be9 6e67 2029 942c 942c 8080 8080 942f 942f

01:02:55:14	942c 942c

01:03:27:29	94ae 94ae 9420 9420 94f2 94f2 c845 d92c 2054 c845 91b0 45ae 942c 942c 8080 8080 942f 942f

01:11:31:01	9420 9420 9452 9452 97a1 97a1 54e5 73f4 2080 9132 2043 6170 f4e9 ef6e 2080 94f2 94f2 97a1 97a1 54e5 73f4 2080 91ae 91ae f4e5 73f4 9120 9120 2043 6170 f4e9 ef6e 7380 942c 942c 942f 942f

01:11:33:14	942c 942c
"""

    expected = """00:00:00:22	{RU2}{RU2}{CR}{CR}{1500}{1500}Lorem ipsum dolor sit amet,
00:00:02:23	{RU2}{RU2}{CR}{CR}{0804}{0804}consectetur adipiscing elit.
00:00:20;06	{RU3}{RU3}{CR}{CR}{1500}{1500}Pellentesque interdum lacinia sollicitudin.
00:00:21;24	{RU3}{RU3}{CR}{CR}{1500}{1500}Integer luctus et ligula ac sagittis.
00:00:49;03	{RU4}{CR}{1500}Ut at diam sit amet nulla fringilla
00:00:50;23	{RU4}{CR}{1500}vestibulum nec vitae nisi.
00:02:53:14	{RDC}{RDC}{1404}{1404}Lorem ipsum dolor sit amet,{1504}{1504}consectetur adipiscing elit.
00:02:56:00	{RDC}{RDC}{1404}{1404}Pellentesque interdum lacinia sollicitudin.
00:02:56:25	{RDC}{RDC}{1504}{1504}Integer luctus et ligula ac sagittis.
01:02:53:14	{ENM}{ENM}{RCL}{RCL}{1520}{1520}{TO2}{TO2}( horn honking ){EDM}{EDM}{}{}{EOC}{EOC}
01:02:55:14	{EDM}{EDM}
01:03:27:29	{ENM}{ENM}{RCL}{RCL}{1504}{1504}HEY, THE®E.{EDM}{EDM}{}{}{EOC}{EOC}
01:11:31:01	{RCL}{RCL}{1404}{1404}{TO1}{TO1}Test ½ Caption {1504}{1504}{TO1}{TO1}Test {I}{I}test{Wh}{Wh} Captions{EDM}{EDM}{EOC}{EOC}
01:11:33:14	{EDM}{EDM}
"""

    disassembly = to_disassembly(scc_content)

    self.assertEqual(expected, disassembly)
