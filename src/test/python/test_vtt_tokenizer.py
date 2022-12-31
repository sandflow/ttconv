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

'''Unit tests for the WebVTT tokenizer'''

# pylint: disable=R0201,C0115,C0116

import unittest

import ttconv.vtt.tokenizer as tokenizer

class VTTTokenizerTest(unittest.TestCase):

  def test_tokenizer_classes(self):
    cue_text = "<c.yellow.bg_blue.magenta.bg_black>This is magenta text on a black background</c>"

    t = tokenizer.Tokenizer(cue_text)

    start_tag_token: tokenizer.StartTagToken = t.next()
    self.assertIsInstance(start_tag_token, tokenizer.StartTagToken)
    self.assertEqual(start_tag_token.tag, "c")
    self.assertListEqual(start_tag_token.classes, ["yellow", "bg_blue", "magenta", "bg_black"])

    string_token: tokenizer.StringToken = t.next()
    self.assertIsInstance(string_token, tokenizer.StringToken)
    self.assertEqual(string_token.value, "This is magenta text on a black background")

    end_tag_token: tokenizer.EndTagToken = t.next()
    self.assertIsInstance(end_tag_token, tokenizer.EndTagToken)
    self.assertEqual(end_tag_token.tag, "c")

    self.assertIsNone(t.next())

  def test_tokenizer_multiline_incomplete_elements(self):
    cue_text = """<c.yellow><c.bg_black >This</c></c>
<c.bg_yellow>is
<c.bg_red>row 18"""

    t = tokenizer.Tokenizer(cue_text)

    start_tag_token: tokenizer.StartTagToken = t.next()
    self.assertIsInstance(start_tag_token, tokenizer.StartTagToken)
    self.assertEqual(start_tag_token.tag, "c")
    self.assertListEqual(start_tag_token.classes, ["yellow"])

    start_tag_token: tokenizer.StartTagToken = t.next()
    self.assertIsInstance(start_tag_token, tokenizer.StartTagToken)
    self.assertEqual(start_tag_token.tag, "c")
    self.assertListEqual(start_tag_token.classes, ["bg_black"])

    string_token: tokenizer.StringToken = t.next()
    self.assertIsInstance(string_token, tokenizer.StringToken)
    self.assertEqual(string_token.value, "This")

    end_tag_token: tokenizer.EndTagToken = t.next()
    self.assertIsInstance(end_tag_token, tokenizer.EndTagToken)
    self.assertEqual(end_tag_token.tag, "c")

    end_tag_token: tokenizer.EndTagToken = t.next()
    self.assertIsInstance(end_tag_token, tokenizer.EndTagToken)
    self.assertEqual(end_tag_token.tag, "c")

    string_token: tokenizer.StringToken = t.next()
    self.assertIsInstance(string_token, tokenizer.StringToken)
    self.assertEqual(string_token.value, "\n")

    start_tag_token: tokenizer.StartTagToken = t.next()
    self.assertIsInstance(start_tag_token, tokenizer.StartTagToken)
    self.assertEqual(start_tag_token.tag, "c")
    self.assertListEqual(start_tag_token.classes, ["bg_yellow"])

    string_token: tokenizer.StringToken = t.next()
    self.assertIsInstance(string_token, tokenizer.StringToken)
    self.assertEqual(string_token.value, "is\n")

    start_tag_token: tokenizer.StartTagToken = t.next()
    self.assertIsInstance(start_tag_token, tokenizer.StartTagToken)
    self.assertEqual(start_tag_token.tag, "c")
    self.assertListEqual(start_tag_token.classes, ["bg_red"])

    string_token: tokenizer.StringToken = t.next()
    self.assertIsInstance(string_token, tokenizer.StringToken)
    self.assertEqual(string_token.value, "row 18")

    self.assertIsNone(t.next())
