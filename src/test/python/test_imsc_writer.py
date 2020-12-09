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

'''Unit tests for the IMSC writer'''

# pylint: disable=R0201,C0115,C0116

import os
import unittest
import logging
from fractions import Fraction
import xml.etree.ElementTree as et
import xml.dom.minidom as minidom
import ttconv.imsc.reader as imsc_reader
import ttconv.imsc.writer as imsc_writer
import ttconv.model as model
import ttconv.style_properties as styles
import ttconv.imsc.namespaces as xml_ns
import ttconv.imsc.style_properties as imsc_styles
import ttconv.imsc.attributes as attributes
from ttconv.scc.utils import get_extent_from_dimensions

def _get_set_style(imsc_style_prop, model_value):
  e = et.Element("p")
  assert imsc_style_prop.model_prop.validate(model_value)
  imsc_style_prop.from_model(e, model_value)
  return e.attrib.get(f"{{{imsc_style_prop.ns}}}{imsc_style_prop.local_name}")

def _get_time(imsc_style_prop, model_value):
  e = et.Element("p")
  assert imsc_style_prop.model_prop.validate(model_value)
  imsc_style_prop.from_model(e, model_value)
  return e.attrib.get(f"{{{imsc_style_prop.ns}}}{imsc_style_prop.local_name}")

class ReaderWriterTest(unittest.TestCase):

  def setUp(self):
    if not os.path.exists('build'):
      os.makedirs('build')

  def pretty_print(self, elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = et.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    print(reparsed.toprettyxml(indent="\t"))

  def write_pretty_xml(self, tree: et.ElementTree, file_path):
    rough_string = et.tostring(tree.getroot(), 'utf-8')
    reparsed = minidom.parseString(rough_string)
    with open(file_path, "wb") as f:
      f.write(reparsed.toprettyxml(indent="  ", encoding="utf-8"))

  def test_animation_001(self):
    file_to_parse = "src/test/resources/ttml/imsc-tests/imsc1/ttml/animation/Animation001.ttml"
    
    tree = et.parse(file_to_parse)

    # create the model
    test_model = imsc_reader.to_model(tree)

    # convert from a model to a ttml document
    tree_from_model = imsc_writer.from_model(test_model)

    # write the document out to a file
    self.write_pretty_xml(tree_from_model, 'build/out.ttml')

  def test_imsc_1_test_suite(self):
    if not os.path.exists('build/imsc1'):
      os.makedirs('build/imsc1')
    for root, _subdirs, files in os.walk("src/test/resources/ttml/imsc-tests/imsc1/ttml"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".ttml":
          with self.subTest(name), self.assertLogs() as logs:
            logging.getLogger().info("*****dummy*****") # dummy log
            tree = et.parse(os.path.join(root, filename))
            test_model = imsc_reader.to_model(tree)
            tree_from_model = imsc_writer.from_model(test_model)
            self.write_pretty_xml(tree_from_model, f'build/imsc1/{name}.ttml')
            if len(logs.output) > 1:
              self.fail(logs.output)

  def test_imsc_1_1_test_suite(self):
    if not os.path.exists('build/imsc1_1'):
      os.makedirs('build/imsc1_1')
    for root, _subdirs, files in os.walk("src/test/resources/ttml/imsc-tests/imsc1_1/ttml"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".ttml":
          with self.subTest(name), self.assertLogs() as logs:
            logging.getLogger().info("*****dummy*****") # dummy log
            tree = et.parse(os.path.join(root, filename))
            test_model = imsc_reader.to_model(tree)
            tree_from_model = imsc_writer.from_model(test_model)
            self.write_pretty_xml(tree_from_model, f'build/imsc1_1/{name}.ttml')
            if len(logs.output) > 1:
              self.fail(logs.output)

class FromModelBodyWriterTest(unittest.TestCase):

  def setUp(self):
    if not os.path.exists('build'):
      os.makedirs('build')
    
    et.register_namespace("ttml", xml_ns.TTML)
    et.register_namespace("ttp", xml_ns.TTP)
    et.register_namespace("tts", xml_ns.TTS)
    et.register_namespace("ittp", xml_ns.ITTP)
    et.register_namespace("itts", xml_ns.ITTS)

  def test_body_only(self):

    doc = model.ContentDocument()
    body = model.Body(doc)
    div = model.Div(doc)
    p = model.P(doc)
    span = model.Span(doc)
    text = model.Text(doc)
    text.set_text("asdf")
    
    span.push_child(text)
    p.push_child(span)
    div.push_child(p)
    body.push_child(div)
    doc.set_body(body)

    # write the document out to a file
    imsc_writer.from_model(doc).write('build/BodyElement.out.ttml', encoding='utf-8', xml_declaration=True)

    #self.pretty_print(tree_from_model.getroot())

class StylePropertyWriterTest(unittest.TestCase):

  def test_tts_luminance_gain(self):
    self.assertEqual(
      _get_set_style(imsc_styles.StyleProperties.LuminanceGain, 1.2),
      "1.2"
    )

  def test_tts_opacity(self):
    self.assertEqual(_get_set_style(imsc_styles.StyleProperties.Opacity, 0.532), "0.532")

  def test_tts_overflow(self):
    self.assertEqual(
      _get_set_style(imsc_styles.StyleProperties.Overflow, styles.OverflowType.visible),
      "visible"
    )

  def test_tts_padding(self):
    padding = styles.PaddingType(
      before=styles.LengthType(10.1),
      end=styles.LengthType(20.2),
      after=styles.LengthType(30.3),
      start=styles.LengthType(40.4)
    )

    self.assertEqual(
      _get_set_style(imsc_styles.StyleProperties.Padding, padding),
      r"10.1% 20.2% 30.3% 40.4%"
    )

  def test_tts_ruby_align(self):
    self.assertEqual(
      _get_set_style(imsc_styles.StyleProperties.RubyAlign, styles.RubyAlignType.spaceAround),
      "spaceAround"
    )

  def test_tts_ruby_position(self):
    self.assertEqual(
      _get_set_style(imsc_styles.StyleProperties.RubyPosition, styles.AnnotationPositionType.outside),
      "outside"
    )

  def test_tts_ruby_reserve(self):
    rr1 = styles.SpecialValues.none
    self.assertEqual(
      _get_set_style(
        imsc_styles.StyleProperties.RubyReserve,
        rr1
        ),
      "none"
    )

    rr2 = styles.RubyReserveType(
      position=styles.RubyReserveType.Position.both,
      length=styles.LengthType(value=1.2, units=styles.LengthType.Units.em)
    )
    self.assertEqual(
      _get_set_style(
        imsc_styles.StyleProperties.RubyReserve,
        rr2
        ),
      "both 1.2em"
    )

    rr3 = styles.RubyReserveType(
      position=styles.RubyReserveType.Position.outside,
    )
    self.assertEqual(
      _get_set_style(
        imsc_styles.StyleProperties.RubyReserve,
        rr3
        ),
      "outside"
    )

  def test_tts_shear(self):
    self.assertEqual(
      _get_set_style(imsc_styles.StyleProperties.Shear, 12.3),
      "12.3%"
    )

  def test_tts_text_align(self):
    self.assertEqual(
      _get_set_style(imsc_styles.StyleProperties.TextAlign, styles.TextAlignType.start),
      "start"
    )

  def test_tts_text_combine(self):
    self.assertEqual(
      _get_set_style(imsc_styles.StyleProperties.TextCombine, styles.TextCombineType.all),
      "all"
    )

  def test_tts_text_decoration(self):
    self.assertEqual(
      _get_set_style(
        imsc_styles.StyleProperties.TextDecoration,
        styles.TextDecorationType(
          underline=False,
          line_through=True
        )
      ),
      "noUnderline lineThrough"
    )

  def test_tts_text_emphasis(self):
    self.assertEqual(
      _get_set_style(
        imsc_styles.StyleProperties.TextEmphasis,
        styles.TextEmphasisType(
          style=styles.TextEmphasisType.Style.filled_circle,
          color=styles.NamedColors.red.value,
          position=styles.TextEmphasisType.Position.after
        )
      ),
      "filled circle #ff0000 after"
    )

  def test_tts_text_outline(self):
    to1 = styles.SpecialValues.none
    self.assertEqual(
      _get_set_style(
        imsc_styles.StyleProperties.TextOutline,
        to1
        ),
      "none"
    )

    to2 = styles.TextOutlineType(
      color=styles.NamedColors.red.value,
      thickness=styles.LengthType(value=5)
    )
    self.assertEqual(
      _get_set_style(
        imsc_styles.StyleProperties.TextOutline,
        to2
        ),
      "#ff0000 5%"
    )

  def test_tts_text_shadow(self):
    ts1 = styles.SpecialValues.none
    self.assertEqual(
      _get_set_style(
        imsc_styles.StyleProperties.TextShadow,
        ts1
        ),
      "none"
    )

    ts2 = styles.TextShadowType(
      (
        styles.TextShadowType.Shadow(
          x_offset=styles.LengthType(value=1, units=styles.LengthType.Units.em),
          y_offset=styles.LengthType(value=1.2, units=styles.LengthType.Units.em)
        ),
        styles.TextShadowType.Shadow(
          x_offset=styles.LengthType(value=0.5, units=styles.LengthType.Units.em),
          y_offset=styles.LengthType(value=0.7, units=styles.LengthType.Units.em),
          blur_radius=styles.LengthType(value=1, units=styles.LengthType.Units.em),
          color=styles.NamedColors.red.value
        )
      )
    )

    self.assertEqual(
      _get_set_style(
        imsc_styles.StyleProperties.TextShadow,
        ts2
        ),
      "1em 1.2em, 0.5em 0.7em 1em #ff0000"
    )

  def test_tts_unicode_bidi(self):
    self.assertEqual(
      _get_set_style(
        imsc_styles.StyleProperties.UnicodeBidi,
        styles.UnicodeBidiType.bidiOverride
      ),
      "bidiOverride"
    )

  def test_tts_visibility(self):
    self.assertEqual(
      _get_set_style(
        imsc_styles.StyleProperties.Visibility,
        styles.VisibilityType.hidden
      ),
      "hidden"
    )

  def test_tts_wrap_option(self):
    self.assertEqual(
      _get_set_style(
        imsc_styles.StyleProperties.WrapOption,
        styles.WrapOptionType.noWrap
      ),
      "noWrap"
    )

  def test_tts_writing_mode(self):
    self.assertEqual(
      _get_set_style(
        imsc_styles.StyleProperties.WritingMode,
        styles.WritingModeType.tbrl
      ),
      "tbrl"
    )

  def test_tts_writing_extent(self):
    self.assertEqual(
      _get_set_style(imsc_styles.StyleProperties.Extent,
      get_extent_from_dimensions(123, 456, styles.LengthType.Units.px)),
      '123px 456px'
    )

  def test_tts_writing_no_extent_when_no_body(self):

    d = model.ContentDocument()

    tree_from_model = imsc_writer.from_model(d)

    extent = tree_from_model.getroot().attrib.get(
      f"{{{imsc_styles.StyleProperties.Extent.ns}}}{imsc_styles.StyleProperties.Extent.local_name}")
    
    self.assertEqual(extent, None)
  
  def test_tts_writing_no_extent_when_body_has_no_extents(self):

    doc = model.ContentDocument()
    body = model.Body(doc)
    div = model.Div(doc)
    p = model.P(doc)
    span = model.Span(doc)
    text = model.Text(doc)
    text.set_text("asdf")
    
    span.push_child(text)
    p.push_child(span)
    div.push_child(p)
    body.push_child(div)
    doc.set_body(body)

    tree_from_model = imsc_writer.from_model(doc)

    extent = tree_from_model.getroot().attrib.get(
      f"{{{imsc_styles.StyleProperties.Extent.ns}}}{imsc_styles.StyleProperties.Extent.local_name}")
    
    self.assertEqual(extent, None)

  def test_tts_writing_extent_when_body_has_extents(self):

    doc = model.ContentDocument()
    body = model.Body(doc)
    div = model.Div(doc)

    div.set_style(styles.StyleProperties.Extent,
      get_extent_from_dimensions(123, 456, styles.LengthType.Units.px))

    p = model.P(doc)
    span = model.Span(doc)
    text = model.Text(doc)
    text.set_text("asdf")
    
    span.push_child(text)
    p.push_child(span)
    div.push_child(p)
    body.push_child(div)
    doc.set_body(body)

    r = model.Region("hello", doc)
    r.set_style(styles.StyleProperties.Extent,
      get_extent_from_dimensions(123, 456, styles.LengthType.Units.px))

    doc.put_region(r)

    tree_from_model = imsc_writer.from_model(doc)

    extent = tree_from_model.getroot().attrib.get(
      f"{{{imsc_styles.StyleProperties.Extent.ns}}}{imsc_styles.StyleProperties.Extent.local_name}")
    
    self.assertEqual(extent, '1920px 1080px')

  def test_style_property_base_has_px(self):
    prop = imsc_styles.StyleProperty
    self.assertEqual(imsc_styles.StyleProperty.has_px(prop),
      False
    )

  def test_style_property_Disparity_has_px(self):
    prop = styles.LengthType(1, styles.LengthType.units.em)
    self.assertEqual(imsc_styles.StyleProperties.Disparity.has_px(prop), False)

    prop = styles.LengthType(1, styles.LengthType.units.px)
    self.assertEqual(imsc_styles.StyleProperties.Disparity.has_px(prop), True)

  def test_style_property_Extent_has_px(self):
    prop = styles.ExtentType(styles.LengthType(1, styles.LengthType.units.px), 
      styles.LengthType(1, styles.LengthType.units.em))
    self.assertEqual(imsc_styles.StyleProperties.Extent.has_px(prop), True)

    prop = styles.ExtentType(styles.LengthType(1, styles.LengthType.units.px), 
      styles.LengthType(1, styles.LengthType.units.px))
    self.assertEqual(imsc_styles.StyleProperties.Extent.has_px(prop), True)

    prop = styles.ExtentType(styles.LengthType(1, styles.LengthType.units.em), 
      styles.LengthType(1, styles.LengthType.units.px))
    self.assertEqual(imsc_styles.StyleProperties.Extent.has_px(prop), True)

    prop = styles.ExtentType(styles.LengthType(1, styles.LengthType.units.em), 
      styles.LengthType(1, styles.LengthType.units.em))
    self.assertEqual(imsc_styles.StyleProperties.Extent.has_px(prop), False)

  def test_style_property_FontSize_has_px(self):
    prop = styles.LengthType(1, styles.LengthType.units.em)
    self.assertEqual(imsc_styles.StyleProperties.FontSize.has_px(prop), False)

    prop = styles.LengthType(1, styles.LengthType.units.px)
    self.assertEqual(imsc_styles.StyleProperties.FontSize.has_px(prop), True)

  def test_style_property_LineHeight_has_px(self):
    prop = styles.SpecialValues.normal
    self.assertEqual(imsc_styles.StyleProperties.LineHeight.has_px(prop), False)

    prop = styles.LengthType(1, styles.LengthType.units.em)
    self.assertEqual(imsc_styles.StyleProperties.LineHeight.has_px(prop), False)

    prop = styles.LengthType(1, styles.LengthType.units.px)
    self.assertEqual(imsc_styles.StyleProperties.LineHeight.has_px(prop), True)

  def test_style_property_Origin_has_px(self):
    prop = styles.PositionType(styles.LengthType(1, styles.LengthType.units.px), 
      styles.LengthType(1, styles.LengthType.units.em))
    self.assertEqual(imsc_styles.StyleProperties.Origin.has_px(prop), True)

    prop = styles.PositionType(styles.LengthType(1, styles.LengthType.units.px), 
      styles.LengthType(1, styles.LengthType.units.px))
    self.assertEqual(imsc_styles.StyleProperties.Origin.has_px(prop), True)

    prop = styles.PositionType(styles.LengthType(1, styles.LengthType.units.em), 
      styles.LengthType(1, styles.LengthType.units.px))
    self.assertEqual(imsc_styles.StyleProperties.Origin.has_px(prop), True)

    prop = styles.PositionType(styles.LengthType(1, styles.LengthType.units.em), 
      styles.LengthType(1, styles.LengthType.units.em))
    self.assertEqual(imsc_styles.StyleProperties.Origin.has_px(prop), False)

  def test_style_property_Padding_has_px(self):
    prop = styles.PaddingType(
      before = styles.LengthType(10.1, styles.LengthType.units.px),
      end = styles.LengthType(20.2, styles.LengthType.units.em),
      after = styles.LengthType(30.3, styles.LengthType.units.em),
      start = styles.LengthType(40.4, styles.LengthType.units.em)
    )
    self.assertEqual(imsc_styles.StyleProperties.Padding.has_px(prop), True)

    prop = styles.PaddingType(
      before = styles.LengthType(10.1, styles.LengthType.units.em),
      end = styles.LengthType(20.2, styles.LengthType.units.px),
      after = styles.LengthType(30.3, styles.LengthType.units.em),
      start = styles.LengthType(40.4, styles.LengthType.units.em)
    )
    self.assertEqual(imsc_styles.StyleProperties.Padding.has_px(prop), True)

    prop = styles.PaddingType(
      before = styles.LengthType(10.1, styles.LengthType.units.em),
      end = styles.LengthType(20.2, styles.LengthType.units.em),
      after = styles.LengthType(30.3, styles.LengthType.units.px),
      start = styles.LengthType(40.4, styles.LengthType.units.em)
    )
    self.assertEqual(imsc_styles.StyleProperties.Padding.has_px(prop), True)

    prop = styles.PaddingType(
      before = styles.LengthType(10.1, styles.LengthType.units.em),
      end = styles.LengthType(20.2, styles.LengthType.units.em),
      after = styles.LengthType(30.3, styles.LengthType.units.em),
      start = styles.LengthType(40.4, styles.LengthType.units.px)
    )
    self.assertEqual(imsc_styles.StyleProperties.Padding.has_px(prop), True)

    prop = styles.PaddingType(
      before = styles.LengthType(10.1, styles.LengthType.units.em),
      end = styles.LengthType(20.2, styles.LengthType.units.em),
      after = styles.LengthType(30.3, styles.LengthType.units.em),
      start = styles.LengthType(40.4, styles.LengthType.units.em)
    )
    self.assertEqual(imsc_styles.StyleProperties.Padding.has_px(prop), False)

  def test_style_property_RubyReserve_has_px(self):
    prop = styles.RubyReserveType(
      position=styles.RubyReserveType.Position.both,
      length=styles.LengthType(value=1.2, units=styles.LengthType.Units.px)
    )
    self.assertEqual(imsc_styles.StyleProperties.RubyReserve.has_px(prop), True)

    prop = styles.RubyReserveType(
      position=styles.RubyReserveType.Position.both,
      length=styles.LengthType(value=1.2, units=styles.LengthType.Units.em)
    )
    self.assertEqual(imsc_styles.StyleProperties.RubyReserve.has_px(prop), False)


  def test_style_property_TextOutline_has_px(self):
    prop = styles.SpecialValues.none
    self.assertEqual(imsc_styles.StyleProperties.TextOutline.has_px(prop), False)

    prop = styles.TextOutlineType(
      color=styles.NamedColors.red.value,
      thickness=styles.LengthType(value=5, units=styles.LengthType.Units.em)
    )
    self.assertEqual(imsc_styles.StyleProperties.TextOutline.has_px(prop), False)

    prop = styles.TextOutlineType(
      color=styles.NamedColors.red.value,
      thickness=styles.LengthType(value=5, units=styles.LengthType.Units.px)
    )
    self.assertEqual(imsc_styles.StyleProperties.TextOutline.has_px(prop), True)
    
  def test_style_property_TextShadow_has_px(self):
    prop = styles.TextShadowType(
      (
        styles.TextShadowType.Shadow(
          x_offset=styles.LengthType(value=1, units=styles.LengthType.Units.em),
          y_offset=styles.LengthType(value=1, units=styles.LengthType.Units.em)
        ),
        styles.TextShadowType.Shadow(
          x_offset=styles.LengthType(value=0.5, units=styles.LengthType.Units.em),
          y_offset=styles.LengthType(value=0.7, units=styles.LengthType.Units.em),
          blur_radius=styles.LengthType(value=1, units=styles.LengthType.Units.em),
          color=styles.NamedColors.red.value
        )
      )
    )
    self.assertEqual(imsc_styles.StyleProperties.TextShadow.has_px(prop), False)

    prop = styles.TextShadowType(
      (
        styles.TextShadowType.Shadow(
          x_offset=styles.LengthType(value=1, units=styles.LengthType.Units.px),
          y_offset=styles.LengthType(value=1.2, units=styles.LengthType.Units.em)
        ),
        styles.TextShadowType.Shadow(
          x_offset=styles.LengthType(value=0.5, units=styles.LengthType.Units.em),
          y_offset=styles.LengthType(value=0.7, units=styles.LengthType.Units.em),
          blur_radius=styles.LengthType(value=1, units=styles.LengthType.Units.em),
          color=styles.NamedColors.red.value
        )
      )
    )
    self.assertEqual(imsc_styles.StyleProperties.TextShadow.has_px(prop), True)

    prop = styles.TextShadowType(
      (
        styles.TextShadowType.Shadow(
          x_offset=styles.LengthType(value=1, units=styles.LengthType.Units.em),
          y_offset=styles.LengthType(value=1.2, units=styles.LengthType.Units.em)
        ),
        styles.TextShadowType.Shadow(
          x_offset=styles.LengthType(value=0.5, units=styles.LengthType.Units.px),
          y_offset=styles.LengthType(value=0.7, units=styles.LengthType.Units.em),
          blur_radius=styles.LengthType(value=1, units=styles.LengthType.Units.em),
          color=styles.NamedColors.red.value
        )
      )
    )
    self.assertEqual(imsc_styles.StyleProperties.TextShadow.has_px(prop), True)

class WriterWithTimeFormattingTest(unittest.TestCase):

  def test_write_with_frames(self):

    context = attributes.TemporalAttributeWritingContext(None)
    time = Fraction(1, 4)
    val = attributes.to_time_format(context, time)
    self.assertEqual(val, '00:00:00.250')

    context = attributes.TemporalAttributeWritingContext(None)
    time = Fraction(1, 3)
    val = attributes.to_time_format(context, time)
    self.assertEqual(val, '00:00:00.333')

    context = attributes.TemporalAttributeWritingContext(Fraction(30000, 1000))
    time = Fraction(2, 1)
    val = attributes.to_time_format(context, time)
    self.assertEqual(val, '60f')

    context = attributes.TemporalAttributeWritingContext(Fraction(30000, 1001))
    time = Fraction(3, 1)
    val = attributes.to_time_format(context, time)
    self.assertEqual(val, '90f')

    context = attributes.TemporalAttributeWritingContext(Fraction(25000, 1000))
    time = Fraction(3600, 1)
    val = attributes.to_time_format(context, time)
    self.assertEqual(val, '90000f')

    context = attributes.TemporalAttributeWritingContext(Fraction(30000, 1001))
    time = Fraction(0.7674333333333333)
    val = attributes.to_time_format(context, time)
    self.assertEqual(val, '23f')

    context = attributes.TemporalAttributeWritingContext(Fraction(30000, 1001))
    time = 2301 / Fraction(30000, 1001)
    val = attributes.to_time_format(context, time)
    self.assertEqual(val, '2301f')
    
if __name__ == '__main__':
  unittest.main()
