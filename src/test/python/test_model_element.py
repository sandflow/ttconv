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
import ttconv.style_properties as styles

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

  def test_remove_child(self):
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

  def test_remove_children(self):
    p = model.ContentElement()

    c1 = model.ContentElement()

    c2 = model.ContentElement()

    c3 = model.ContentElement()

    p.push_child(c1)

    p.push_child(c2)

    p.push_child(c3)

    p.remove_children()

    self.assertFalse(p.has_children())

  def test_children_accessors(self):
    p = model.ContentElement()

    c1 = model.ContentElement()

    c2 = model.ContentElement()

    c3 = model.ContentElement()

    p.push_child(c1)

    p.push_child(c2)

    p.push_child(c3)

    self.assertEqual(len(p), 3)

    self.assertEqual(p[0], c1)

    self.assertRaises(IndexError, lambda key: p[key], 5)

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
    with self.assertRaises(TypeError):
      bad_id = " "
      p.set_id(bad_id)

  def test_animation_step_init(self):

    model.DiscreteAnimationStep(styles.StyleProperties.Color, 0, 1, styles.NamedColors.aqua.value)

    with self.assertRaises(ValueError):
      model.DiscreteAnimationStep(None, 0, 1, styles.NamedColors.aqua.value)
      
    with self.assertRaises(ValueError):
      model.DiscreteAnimationStep(styles.StyleProperties.Color, 0, 1, None)

    with self.assertRaises(ValueError):
      model.DiscreteAnimationStep(styles.StyleProperties.Color, 0, 1, "hello")

  def test_add_remove_animation_step(self):
    p = model.ContentElement()

    s1 = model.DiscreteAnimationStep(styles.StyleProperties.Color, 0, 1, styles.NamedColors.aqua.value)

    s2 = model.DiscreteAnimationStep(styles.StyleProperties.Color, 2, None, styles.NamedColors.black.value)

    s3 = model.DiscreteAnimationStep(styles.StyleProperties.TextAlign, 1, None, styles.TextAlignType.center)

    p.add_animation_step(s1)

    p.add_animation_step(s2)

    p.add_animation_step(s3)

    self.assertListEqual([s1, s2, s3], list(p.iter_animation_steps()))

    p.remove_animation_step(s2)

    self.assertListEqual([s1, s3], list(p.iter_animation_steps()))


class BodyTest(unittest.TestCase):

  def test_push_child(self):
    b = model.Body()

    b.push_child(model.Div())

    with self.assertRaises(TypeError):
      b.push_child(model.P())

class DivTest(unittest.TestCase):

  def test_push_child(self):

    d1 = model.Div()

    d1.push_child(model.P())

    d1.push_child(model.Div())

    with self.assertRaises(TypeError):
      d1.push_child(model.Text())

class PTest(unittest.TestCase):

  def test_push_child(self):

    p = model.P()

    p.push_child(model.Br())

    p.push_child(model.Span())

    p.push_child(model.Ruby())

    with self.assertRaises(TypeError):
      p.push_child(model.Text())


class SpanTest(unittest.TestCase):

  def test_push_child(self):

    s = model.Span()

    s.push_child(model.Br())

    s.push_child(model.Span())

    s.push_child(model.Text())

    with self.assertRaises(TypeError):
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

class RubyTest(unittest.TestCase):

  def test_push_child(self):

    r = model.Ruby()

    with self.assertRaises(RuntimeError):
      r.push_child(model.P())

  def test_remove_child(self):

    r = model.Ruby()

    c1 = model.Rb()

    c2 = model.Rt()

    r.push_children([c1, c2])

    with self.assertRaises(RuntimeError):
      c1.remove()

    with self.assertRaises(RuntimeError):
      r.remove_child(c1)

  def test_push_children(self):

    r = model.Ruby()

    r.push_children([model.Rb(), model.Rt()])

    r.remove_children()

    r.push_children([model.Rb(), model.Rp(), model.Rt(), model.Rp()])

    r.remove_children()

    r.push_children([model.Rbc(), model.Rtc()])

    r.remove_children()

    r.push_children([model.Rbc(), model.Rtc(), model.Rtc()])

    with self.assertRaises(RuntimeError):
      r.push_children([model.Rb(), model.Rt()])

class RtcTest(unittest.TestCase):

  def test_push_child(self):

    r = model.Rtc()

    with self.assertRaises(RuntimeError):
      r.push_child(model.P())

  def test_remove_child(self):

    r = model.Rtc()

    c1 = model.Rt()

    c2 = model.Rt()

    r.push_children([c1, c2])

    with self.assertRaises(RuntimeError):
      c1.remove()

    with self.assertRaises(RuntimeError):
      r.remove_child(c1)

  def test_push_children(self):

    r = model.Rtc()

    r.push_children([model.Rt(), model.Rt()])

    r.remove_children()

    r.push_children([model.Rp(), model.Rt(), model.Rt(), model.Rp()])

    with self.assertRaises(ValueError):
      r.push_children([model.Rb(), model.Rt()])

class RbTest(unittest.TestCase):

  def test_push_child(self):

    s = model.Rb()

    s.push_child(model.Span())

    with self.assertRaises(TypeError):
      s.push_child(model.P())


class RtTest(unittest.TestCase):

  def test_push_child(self):

    s = model.Rt()

    s.push_child(model.Span())

    with self.assertRaises(TypeError):
      s.push_child(model.P())


class RpTest(unittest.TestCase):

  def test_push_child(self):

    s = model.Rp()

    s.push_child(model.Span())

    with self.assertRaises(TypeError):
      s.push_child(model.P())


class RbcTest(unittest.TestCase):

  def test_push_child(self):

    s = model.Rbc()

    s.push_child(model.Rb())

    with self.assertRaises(TypeError):
      s.push_child(model.P())


if __name__ == '__main__':
  unittest.main()
