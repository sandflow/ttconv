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
from fractions import Fraction
import ttconv.model as model
import ttconv.style_properties as styles

class ContentDocumentTest(unittest.TestCase):

  def test_init(self):
    d = model.ContentDocument()

    self.assertIsNone(d.get_body())
    
    self.assertEqual(d.get_px_resolution(), model.PixelResolutionType(width=1920, height=1080))

    self.assertEqual(len(d.iter_initial_values()), 0)

    self.assertEqual(len(d.iter_regions()), 0)

    self.assertEqual(d.get_cell_resolution(), model.CellResolutionType(rows=15, columns=32))
  
  
  def test_set_body(self):
    d = model.ContentDocument()

    b = model.Body(d)

    d.set_body(b)

    self.assertEqual(d.get_body(), b)

    d.set_body(None)

    self.assertIsNone(d.get_body())

  def test_set_bad_body(self):
    d = model.ContentDocument()

    b = model.Body()

    with self.assertRaises(ValueError):
      d.set_body(b)
  
  def test_add_region(self):
    d = model.ContentDocument()

    r = model.Region("hello", d)

    d.put_region(r)

    self.assertIs(d.get_region(r.get_id()), r)

  def test_remove_region(self):
    d = model.ContentDocument()

    r = model.Region("hello", d)

    d.put_region(r)

    self.assertIs(d.get_region(r.get_id()), r)

    d.remove_region(r.get_id())

    self.assertFalse(d.has_region(r.get_id()))

    self.assertIsNone(d.get_region(r.get_id()))


  def test_add_detached_region(self):
    d = model.ContentDocument()

    r = model.Region("hello")

    with self.assertRaises(ValueError):
      d.put_region(r)


  def test_add_dup_region(self):
    d = model.ContentDocument()

    r1 = model.Region("hello", d)

    r2 = model.Region("hello", d)

    d.put_region(r1)

    d.put_region(r2)

    self.assertIs(d.get_region(r2.get_id()), r2)

  def test_iter_region(self):
    d = model.ContentDocument()

    r1 = model.Region("hello1", d)

    r2 = model.Region("hello2", d)

    d.put_region(r1)

    d.put_region(r2)

    self.assertCountEqual(d.iter_regions(), [r1, r2])


  def test_add_initial_value(self):
    d = model.ContentDocument()

    c = styles.ColorType((12, 23, 43, 56))

    d.put_initial_value(styles.StyleProperties.Color, c)

    c2 = d.get_initial_value(styles.StyleProperties.Color)

    self.assertEqual(c, c2)

  def test_remove_initial_value(self):
    d = model.ContentDocument()

    c = styles.ColorType((12, 23, 43, 56))

    d.put_initial_value(styles.StyleProperties.Color, c)

    c2 = d.get_initial_value(styles.StyleProperties.Color)

    self.assertEqual(c, c2)

    d.remove_initial_value(styles.StyleProperties.Color)

    self.assertFalse(d.has_initial_value(styles.StyleProperties.Color))

    self.assertIsNone(d.get_initial_value(styles.StyleProperties.Color))

  def test_add_null_initial_value(self):
    d = model.ContentDocument()

    c = styles.ColorType((12, 23, 43, 56))

    d.put_initial_value(styles.StyleProperties.Color, c)

    c2 = d.get_initial_value(styles.StyleProperties.Color)

    self.assertEqual(c, c2)

    d.put_initial_value(styles.StyleProperties.Color, None)

    self.assertFalse(d.has_initial_value(styles.StyleProperties.Color))

    self.assertIsNone(d.get_initial_value(styles.StyleProperties.Color))

  def test_add_dup_initial_value(self):
    d = model.ContentDocument()

    c1 = styles.ColorType((12, 23, 43, 56))

    c2 = styles.ColorType((12, 96, 43, 56))

    d.put_initial_value(styles.StyleProperties.Color, c1)

    d.put_initial_value(styles.StyleProperties.Color, c2)

    self.assertIsNot(d.get_initial_value(styles.StyleProperties.Color), c1)

    self.assertIs(d.get_initial_value(styles.StyleProperties.Color), c2)

  def test_add_bad_initial_value(self):
    d = model.ContentDocument()

    c1 = styles.ColorType((12, 23, 43, 56))
    
    with self.assertRaises(ValueError):
      d.put_initial_value(styles.StyleProperties.Extent, c1)

  def test_iter_initial_values(self):
    d = model.ContentDocument()

    c1 = styles.ColorType((12, 23, 43, 56))

    c2 = styles.ColorType((12, 96, 43, 56))

    d.put_initial_value(styles.StyleProperties.Color, c1)

    d.put_initial_value(styles.StyleProperties.BackgroundColor, c2)

    self.assertCountEqual(
      [(styles.StyleProperties.Color, c1), (styles.StyleProperties.BackgroundColor, c2)],
      d.iter_initial_values()
    )

  def test_cell_resolution(self):

    cr = model.CellResolutionType(rows=10, columns=20)

    self.assertEqual(cr.columns, 20)

    self.assertEqual(cr.rows, 10)

    with self.assertRaises(ValueError):
      cr = model.CellResolutionType(rows=0, columns=20)

  def test_language(self):

    d = model.ContentDocument()

    self.assertEqual(d.get_lang(), "")

    lang = "fr-CA"

    d.set_lang(lang)

    self.assertEqual(d.get_lang(), lang)

    with self.assertRaises(TypeError):
      d.set_lang(1)

  def test_pixel_resolution(self):

    cr = model.PixelResolutionType(height=480, width=640)

    self.assertEqual(cr.height, 480)

    self.assertEqual(cr.width, 640)

    with self.assertRaises(ValueError):
      cr = model.PixelResolutionType(height=0, width=640)


  def test_active_area_default(self):

    aa = model.ActiveAreaType()

    self.assertEqual(aa.left_offset, 0)

    self.assertEqual(aa.top_offset, 0)

    self.assertEqual(aa.height, 1)

    self.assertEqual(aa.width, 1)


  def test_active_area(self):

    aa = model.ActiveAreaType(0.1, 0.15, 0.8, 0.7)

    self.assertEqual(aa.left_offset, 0.1)

    self.assertEqual(aa.top_offset, 0.15)

    self.assertEqual(aa.width, 0.8)

    self.assertEqual(aa.height, 0.7)

    with self.assertRaises(ValueError):
      model.ActiveAreaType(-0.1, 0.15, 0.8, 0.7)

    with self.assertRaises(ValueError):
      model.ActiveAreaType(0.1, 0.15, -0.8, 0.7)


  def test_document_active_area_default(self):

    d = model.ContentDocument()

    self.assertIsNone(d.get_active_area())


  def test_document_active_area(self):

    d = model.ContentDocument()

    aa = model.ActiveAreaType(0.1, 0.15, 0.8, 0.7)

    d.set_active_area(aa)

    self.assertEqual(
      d.get_active_area(),
      aa
      )

    d.set_active_area(None)

    self.assertIsNone(d.get_active_area())


  def test_display_aspect_ratio(self):

    d = model.ContentDocument()

    self.assertIsNone(d.get_display_aspect_ratio())

    d.set_display_aspect_ratio(Fraction(16, 9))

    self.assertEqual(d.get_display_aspect_ratio(), Fraction(16, 9))

    d.set_display_aspect_ratio(None)

    self.assertIsNone(d.get_display_aspect_ratio())

    with self.assertRaises(TypeError):
      d.set_display_aspect_ratio("hello")


if __name__ == '__main__':
  unittest.main()
