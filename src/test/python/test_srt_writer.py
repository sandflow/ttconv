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

"""Unit tests for the SRT writer"""

# pylint: disable=R0201,C0115,C0116,W0212
from fractions import Fraction
from unittest import TestCase

import ttconv.srt.writer as srt_writer
from ttconv.model import Document, Region, Body, Div, P, Span, Text


class SrtWriterTest(TestCase):

  def test_srt_writer(self):
    doc = Document()

    r1 = Region("r1", doc)
    doc.put_region(r1)

    r2 = Region("r2", doc)
    r2.set_begin(Fraction(2))
    r2.set_end(Fraction(4))
    doc.put_region(r2)

    body = Body(doc)
    doc.set_body(body)

    div = Div(doc)
    body.push_child(div)

    p = P(doc)
    p.set_region(r1)
    p.set_end(Fraction(2))
    div.push_child(p)

    span = Span(doc)
    span.push_child(Text(doc, "Lorem ipsum dolor sit amet,"))
    p.push_child(span)

    p = P(doc)
    p.set_region(r2)
    div.push_child(p)

    span = Span(doc)
    span.push_child(Text(doc, "consectetur adipiscing elit."))
    p.push_child(span)

    p = P(doc)
    p.set_region(r1)
    p.set_begin(Fraction(4))
    p.set_end(Fraction(6))
    div.push_child(p)

    span = Span(doc)
    span.push_child(Text(doc, "Pellentesque interdum lacinia sollicitudin."))
    p.push_child(span)

    expected_srt = """1
00:00:00,000 --> 00:00:02,000
Lorem ipsum dolor sit amet,

2
00:00:02,000 --> 00:00:04,000
consectetur adipiscing elit.

3
00:00:04,000 --> 00:00:06,000
Pellentesque interdum lacinia sollicitudin.
"""

    srt_from_model = srt_writer.from_model(doc)

    self.assertEqual(expected_srt, srt_from_model)
