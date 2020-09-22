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

'''Unit tests for the date model'''

# pylint: disable=R0201,C0115,C0116

import unittest
import ttconv.model as model

class ContentElementTest(unittest.TestCase):

  def test_init(self):
    e = model.ContentElement()

    self.assertTrue(e.root() is e)
    self.assertIsNone(e.parent())
    self.assertFalse(e.has_children())
    self.assertIsNone(e.get_doc())

  def test_attach(self):
    doc = model.Document()

    e = model.ContentElement()

    e.set_doc(doc)

    self.assertTrue(e.get_doc() is doc)
    self.assertTrue(e.is_attached())

  def test_already_attached(self):
    doc = model.Document()
    doc2 = model.Document()

    e = model.ContentElement()

    e.set_doc(doc)

    with self.assertRaises(RuntimeError):
      e.set_doc(doc2)

  def test_detach(self):
    doc = model.Document()

    e = model.ContentElement()

    e.set_doc(doc)

    e.set_doc(None)

    self.assertIsNone(e.get_doc())
    self.assertFalse(e.is_attached())

  def test_failed_child_detach(self):
    doc = model.Document()

    e = model.ContentElement(doc)

    c = model.ContentElement(doc)

    e.push_child(c)

    with self.assertRaises(RuntimeError):
      c.set_doc(None)

  def test_push_child(self):
    p = model.ContentElement()

    c = model.ContentElement()

    p.push_child(c)

    self.assertEqual(p, c.root())

    self.assertTrue(p.has_children())

    self.assertEqual(sum(1 for _ in p), 1)

    for a_child in p:
      self.assertEqual(a_child, c)

  def test_push_child_with_existing_parent(self):
    p = model.ContentElement()

    c1 = model.ContentElement()

    c2 = model.ContentElement()

    c3 = model.ContentElement()

    p.push_child(c1)

    p.push_child(c2)

    c1.push_child(c3)

    with self.assertRaises(RuntimeError):
      p.push_child(c3)

  def test_push_child_as_self(self):
    p = model.ContentElement()

    with self.assertRaises(RuntimeError):
      p.push_child(p)

  def test_dfs(self):
    p = model.ContentElement()

    c1 = model.ContentElement()

    c2 = model.ContentElement()

    c3 = model.ContentElement()

    p.push_child(c1)

    p.push_child(c2)

    c1.push_child(c3)

    dfs = list(p.dfs_iterator())

    self.assertListEqual([p, c1, c3, c2], dfs)

  def test_remove(self):
    p = model.ContentElement()

    c1 = model.ContentElement()

    c2 = model.ContentElement()

    p.push_child(c1)

    p.push_child(c2)

    self.assertEqual(sum(1 for _ in p), 2)

    c2.remove()

    self.assertIsNone(c2.parent())

    self.assertIsNone(c2.next_sibling())

    self.assertIsNone(c2.previous_sibling())

    self.assertEqual(sum(1 for _ in p), 1)

    for a_child in p:
      self.assertEqual(a_child, c1)

  def test_remove_children(self):
    p = model.ContentElement()

    c1 = model.ContentElement()

    c2 = model.ContentElement()

    c3 = model.ContentElement()

    p.push_child(c1)

    p.push_child(c2)

    p.push_child(c3)

    c1.remove()

    self.assertEqual(sum(1 for _ in p), 2)

    c3.remove()

    self.assertEqual(sum(1 for _ in p), 1)

    c2.remove()

    self.assertEqual(sum(1 for _ in p), 0)

  def test_id(self):
    p = model.ContentElement()

    self.assertIsNone(p.get_id())

    # good id
    good_id = "a"
    p.set_id(good_id)
    self.assertEqual(p.get_id(), good_id)

    # None
    p.set_id(None)
    self.assertIsNone(p.get_id())

    # bad id
    with self.assertRaises(RuntimeError):
      bad_id = " "
      p.set_id(bad_id)

class BodyTest(unittest.TestCase):

  def test_push_child(self):
    b = model.Body()

    b.push_child(model.Div())

    with self.assertRaises(RuntimeError):
      b.push_child(model.P())

class DivTest(unittest.TestCase):

  def test_push_child(self):

    d1 = model.Div()

    d1.push_child(model.P())

    d1.push_child(model.Div())

    with self.assertRaises(RuntimeError):
      d1.push_child(model.Text())

class PTest(unittest.TestCase):

  def test_push_child(self):

    p = model.P()

    p.push_child(model.Br())

    p.push_child(model.Span())

    with self.assertRaises(RuntimeError):
      p.push_child(model.Text())

class SpanTest(unittest.TestCase):

  def test_push_child(self):

    s = model.Span()

    s.push_child(model.Br())

    s.push_child(model.Span())

    s.push_child(model.Text())

    with self.assertRaises(RuntimeError):
      s.push_child(model.P())

class TextTest(unittest.TestCase):

  def test_push_child(self):

    t = model.Text()

    with self.assertRaises(RuntimeError):
      t.push_child(model.Span())

  def test_set_text(self):

    t = model.Text()

    self.assertEqual(t.get_text(), "")

    sample_text = "hello"

    t.set_text(sample_text)

    self.assertEqual(t.get_text(), sample_text)

    with self.assertRaises(TypeError):
      t.set_text(None)

class RegionTest(unittest.TestCase):

  def test_push_child(self):

    r = model.Region("hello")

    with self.assertRaises(RuntimeError):
      r.push_child(model.P())

  def test_set_id(self):

    r = model.Region("hello")

    with self.assertRaises(RuntimeError):
      r.set_id("blah")

  def test_set_region(self):

    r1 = model.Region("hello")

    r2 = model.Region("blah")

    with self.assertRaises(RuntimeError):
      r1.set_region(r2)

if __name__ == '__main__':
  unittest.main()
