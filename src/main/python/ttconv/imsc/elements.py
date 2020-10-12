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

'''Process TTML elements'''

import logging
import ttconv.model as model
import ttconv.imsc.namespaces as xml_ns
import ttconv.imsc.attributes as imsc_attr
from ttconv.imsc.style_properties import StyleProperties
import xml.etree.ElementTree as et


LOGGER = logging.getLogger(__name__)

class TTElement:
  '''Processes the TTML <tt> element
  '''

  qn = f"{{{xml_ns.TTML}}}tt"

  @staticmethod
  def process(context, ttml_elem):

    context.doc = model.Document()

    # process attributes

    space = imsc_attr.XMLSpaceAttribute.extract(ttml_elem) or model.WhiteSpaceHandling.DEFAULT

    lang = imsc_attr.XMLLangAttribute.extract(ttml_elem)
    
    if lang is None:
      LOGGER.warning("xml:lang not specified on tt")
      lang = ""

    context.doc.set_cell_resolution(imsc_attr.CellResolutionAttribute.extract(ttml_elem))

    px_resolution = imsc_attr.ExtentAttribute.extract(ttml_elem)

    if px_resolution is not None:
      context.doc.set_px_resolution(px_resolution)

    active_area = imsc_attr.ActiveAreaAttribute.extract(ttml_elem)

    if active_area is not None:
      context.doc.set_active_area(active_area)  

    # process children elements elements

    has_body = False
    has_head = False

    for child_element in ttml_elem:

      if child_element.tag == BodyElement.qn:

        if not has_body:

          context.doc.set_body(
            ContentElement.process(
              context,
              space,
              lang,
              child_element
            )
          )

          has_body = True

        else:
          LOGGER.error("More than one body element present")

      elif child_element.tag == HeadElement.qn:

        if not has_head:
          HeadElement.process(
            context,
            space,
            lang,
            child_element
          )

          has_head = True

        else:
          LOGGER.error("More than one head element present")

  @staticmethod
  def from_model(context, i_model):

    body = i_model.get_body()
    
    if body is not None:
      lang = body.get_lang()
      if lang is not None:
        imsc_attr.XMLLangAttribute.set(context.imsc_doc, lang)

    imsc_attr.CellResolutionAttribute.set(context.imsc_doc, i_model.get_px_resolution())
    imsc_attr.ActiveAreaAttribute.set(context.imsc_doc, i_model.get_active_area())

    space = model.WhiteSpaceHandling.DEFAULT

    # Write the <head> section first
    for region in i_model.iter_regions():
      HeadElement.from_model(
        context,
        region
      )

    body = i_model.get_body()
    if body is not None:
      BodyElement.from_model(
        context,
        body
      )

class HeadElement:
  '''Processes the TTML <head> element
  '''

  qn = f"{{{xml_ns.TTML}}}head"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    # process children elements

    has_layout = False
    has_styling = False
    
    for child_element in ttml_element:

      if child_element.tag == LayoutElement.qn:

        if not has_layout:

          has_layout = True

          LayoutElement.process(
            context,
            imsc_attr.XMLSpaceAttribute.extract(ttml_element) or inherited_space,
            imsc_attr.XMLLangAttribute.extract(ttml_element) or inherited_lang,
            child_element
          )

        else:

          LOGGER.error("Multiple layout elements")

      elif child_element.tag == StylingElement.qn:

        if not has_styling:

          has_styling = True

          StylingElement.process(
            context,
            imsc_attr.XMLSpaceAttribute.extract(ttml_element) or inherited_space,
            imsc_attr.XMLLangAttribute.extract(ttml_element) or inherited_lang,
            child_element
          )

        else:

          LOGGER.error("Multiple styling elements")

  @staticmethod
  def from_model(context, region):

    # Check for exiting head
    head = context.imsc_doc.find("head")
    if head is None:
      head = et.SubElement(context.imsc_doc, "head")

    LayoutElement.from_model(
      head,
      region
    )

class LayoutElement:
  '''Process the TTML <layout> element
  '''

  qn = f"{{{xml_ns.TTML}}}layout"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):
    
    for child_element in ttml_element:

      if child_element.tag == RegionElement.qn:

        r = RegionElement.process(
          context,
          imsc_attr.XMLSpaceAttribute.extract(ttml_element) or inherited_space,
          imsc_attr.XMLLangAttribute.extract(ttml_element) or inherited_lang,
          child_element
        )

        if r is not None:
          context.doc.put_region(r)

      #elif child_element.tag == INITIAL_ELEMENT_QNAME:

      #  _process_initial_element(context, space, lang, child_element)

      else:

        LOGGER.warning("Unexpected child of layout element")

  @staticmethod
  def from_model(head, region):
    
    # Check for exiting head
    layout = head.find("layout")
    if layout is None:
      layout = et.SubElement(head, "layout")

    RegionElement.from_model(
      layout,
      region
    )

class RegionElement:
  '''Process the TTML <region> element
  '''

  qn = f"{{{xml_ns.TTML}}}region"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    rid = imsc_attr.XMLIDAttribute.extract(ttml_element)

    if rid is None:
      LOGGER.error("All regions must have an id")
      return None

    r = model.Region(rid, context.doc)

    # process attributes
    
    r.set_space(imsc_attr.XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    r.set_lang(imsc_attr.XMLLangAttribute.extract(ttml_element) or inherited_lang)
    
    ContentElement.process_style_properties(context, ttml_element, r)

    return r

  @staticmethod
  def from_model(layout, region):

    region_element = et.SubElement(layout, "region")

    attrib = region.get_id()
    if attrib is not None:
      region_element.set(imsc_attr.XMLIDAttribute.qn, attrib)

    attrib = region.get_style(StyleProperties.FontFamily)
    if attrib is not None:
      region_element.set("tts:fontFamily", attrib)

    #attrib = region.get_style(StyleProperties.showBackground)
    attrib = None
    if attrib is not None:
      region_element.set("tts:showBackground", attrib)

    #attrib = region.get_style(StyleProperties.showBackground)
    attrib = None
    if attrib is not None:
      region_element.set("tts:origin", attrib)

    #attrib = region.get_style(StyleProperties.showBackground)
    attrib = None
    if attrib is not None:
      region_element.set("tts:extent", attrib)

    #attrib = region.get_style(StyleProperties.showBackground)
    attrib = None
    if attrib is not None:
      region_element.set("tts:color", attrib)

    attrib = region.get_style(StyleProperties.BackgroundColor)
    if attrib is not None:
      region_element.set("tts:backgroundColor", attrib)

    attrib = region.get_style(StyleProperties.TextAlign)
    if attrib is not None:
      region_element.set("tts:textAlign", attrib)

    attrib = region.get_style(StyleProperties.DisplayAlign)
    if attrib is not None:
      region_element.set("tts:displayAlign", attrib)

class StylingElement:
  '''Process the TTML <styling> element
  '''

  qn = f"{{{xml_ns.TTML}}}styling"

  @staticmethod
  def process(_context, _inherited_space, _inherited_lang, _ttml_element):
    pass

#
# process content elements
#

class ContentElement:
  '''TTML content elements: body, div, p, span, br
  '''

  @staticmethod
  def process_region_property(context, ttml_element, element):
    '''Read the region attribute and associate the element with the corresponding region'''
    rid = ttml_element.attrib.get('region')

    if rid is not None:
      r = context.doc.get_region(rid)
      
      if r is not None:
        element.set_region(r)
      else:
        LOGGER.warning("Element references unknown region")

  @staticmethod
  def process_style_properties(context, ttml_element, element):
    '''Read TTML style properties into the model'''
    for attr in ttml_element.attrib:
      prop = StyleProperties.BY_QNAME.get(attr)
      if prop is not None:
        try:
          element.set_style(prop.model_prop, prop.extract(context, ttml_element.attrib.get(attr)))
        except ValueError:
          LOGGER.error("Error reading style property: %s", prop.__name__)

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    if ttml_element.tag == BodyElement.qn:

      element = BodyElement.process(context, inherited_space, inherited_lang, ttml_element)

    elif ttml_element.tag == DivElement.qn:

      element = DivElement.process(context, inherited_space, inherited_lang, ttml_element)

    elif ttml_element.tag == PElement.qn:

      element = PElement.process(context, inherited_space, inherited_lang, ttml_element)

    elif ttml_element.tag == SpanElement.qn:

      ruby = SpanElement.get_ruby_attr(ttml_element)

      if ruby == RubyElement.ruby:

        element = RubyElement.process(context, inherited_space, inherited_lang, ttml_element)

      elif ruby == RbElement.ruby:

        element = RbElement.process(context, inherited_space, inherited_lang, ttml_element)

      elif ruby == RtElement.ruby:

        element = RtElement.process(context, inherited_space, inherited_lang, ttml_element)

      elif ruby == RpElement.ruby:

        element = RpElement.process(context, inherited_space, inherited_lang, ttml_element)

      elif ruby == RbcElement.ruby:

        element = RbcElement.process(context, inherited_space, inherited_lang, ttml_element)

      elif ruby == RtcElement.ruby:

        element = RtcElement.process(context, inherited_space, inherited_lang, ttml_element)

      else:

        element = SpanElement.process(context, inherited_space, inherited_lang, ttml_element)

    elif ttml_element.tag == BrElement.qn:

      element = BrElement.process(context, inherited_space, inherited_lang, ttml_element)

    else:

      return None

    return element

  @staticmethod
  def from_model(context, body):
    
    if body is None:
      return

    BodyElement.from_model(context, body)





class BodyElement:
  '''Process TTML body element
  '''

  qn = f"{{{xml_ns.TTML}}}body"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Body(context.doc)

    # process attributes
    
    element.set_space(imsc_attr.XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(imsc_attr.XMLLangAttribute.extract(ttml_element) or inherited_lang)

    ContentElement.process_region_property(context, ttml_element, element)

    ContentElement.process_style_properties(context, ttml_element, element)

    # process children elements

    for ttml_child_element in ttml_element:
      child_element = ContentElement.process(
        context,
        element.get_space(),
        element.get_lang(),
        ttml_child_element
      )

      if child_element is not None:
        if not isinstance(child_element, model.Div):
          LOGGER.error("Children of body must be div instances")
        else:
          element.push_child(child_element)

    return element

  @staticmethod
  def from_model(context, body):
    
    if body is None:
      return
    
    body_element = context.imsc_doc.find("body")
    if body_element is None:
      body_element = et.SubElement(context.imsc_doc, "body")
    
    attrib = body._id
    if attrib is not None:
      body_element.set(imsc_attr.XMLIDAttribute.qn, attrib)

    attrib = body.get_style(StyleProperties.LineHeight)
    if attrib is not None:
      body_element.set("tts:lineHeight", attrib)

    for div in body:
      DivElement.from_model(body_element, div)

class DivElement:
  '''Process TTML <div> element
  '''

  qn = f"{{{xml_ns.TTML}}}div"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Div(context.doc)

    # process attributes
    
    element.set_space(imsc_attr.XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(imsc_attr.XMLLangAttribute.extract(ttml_element) or inherited_lang)

    ContentElement.process_region_property(context, ttml_element, element)

    ContentElement.process_style_properties(context, ttml_element, element)

    # process children elements

    for ttml_child_element in ttml_element:
      child_element = ContentElement.process(
        context,
        element.get_space(),
        element.get_lang(),
        ttml_child_element
      )

      if child_element is not None:
        if not isinstance(child_element, (model.P, model.Div)):
          LOGGER.error("Children of div must be div or p instances")
        else:
          element.push_child(child_element)

    return element

  @staticmethod
  def from_model(parent_element, parent_div):
    
    if parent_div is None:
      return

    div_element = et.SubElement(parent_element, "div")

    if parent_div.has_children():
      for child in parent_div:
        if isinstance(child, model.P):
          PElement.from_model(div_element, child)
        elif isinstance(child, model.Div):
          DivElement.from_model(div_element, child)
        else:
          LOGGER.error("Children of div must be p or div")
    else:
      pass

class PElement:
  '''Process TTML <p> element
  '''

  qn = f"{{{xml_ns.TTML}}}p"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.P(context.doc)

    # process attributes
    
    element.set_space(imsc_attr.XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(imsc_attr.XMLLangAttribute.extract(ttml_element) or inherited_lang)

    ContentElement.process_region_property(context, ttml_element, element)

    ContentElement.process_style_properties(context, ttml_element, element)

    # process children elements

    if ttml_element.text:
      element.push_child(SpanElement.make_anonymous_span(context.doc, ttml_element.text))

    for ttml_child_element in ttml_element:
      child_element = ContentElement.process(
        context,
        element.get_space(),
        element.get_lang(),
        ttml_child_element
      )

      if child_element is not None:

        if not isinstance(child_element, (model.Span, model.Br, model.Ruby)):

          LOGGER.error("Children of p must be span, br or ruby instances")

        else:

          element.push_child(child_element)

      if ttml_child_element.tail:
        element.push_child(SpanElement.make_anonymous_span(context.doc, ttml_child_element.tail))

    return element

  @staticmethod
  def from_model(parent_element, parent_p):
    
    if parent_p is None:
      return

    p_element = et.SubElement(parent_element, "p")

    if parent_p.has_children():
      for child in parent_p:
        if isinstance(child, model.Span):
          SpanElement.from_model(p_element, child)
        elif isinstance(child, model.Ruby):
          RubyElement.from_model(p_element, child)
        elif isinstance(child, model.Br):
          BrElement.from_model(p_element, child)
        else:
          LOGGER.error("Children of p must be span or br or text")

class SpanElement:
  '''Process the TTML <span> element
  '''

  qn = f"{{{xml_ns.TTML}}}span"

  @staticmethod
  def make_anonymous_span(doc, text):

    s = model.Span(doc)
    t = model.Text(doc, text)
    s.push_child(t)

    return s

  @staticmethod
  def get_ruby_attr(ttml_span):
    return ttml_span.get(f"{{{xml_ns.TTS}}}ruby")

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Span(context.doc)

    # process attributes
    
    element.set_space(imsc_attr.XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(imsc_attr.XMLLangAttribute.extract(ttml_element) or inherited_lang)

    ContentElement.process_region_property(context, ttml_element, element)

    ContentElement.process_style_properties(context, ttml_element, element)

    # process head text node

    if ttml_element.text is not None:
      element.push_child(model.Text(context.doc, ttml_element.text))

    # process children elements

    for ttml_child_element in ttml_element:

      child_element = ContentElement.process(
        context,
        element.get_space(),
        element.get_lang(),
        ttml_child_element
      )

      if child_element is not None:

        if not isinstance(child_element, (model.Span, model.Br)):

          LOGGER.error("Children of p must be span or br or text instances")

        else:

          element.push_child(child_element)

      # process tail text node

      if ttml_child_element.tail:
        element.push_child(model.Text(context.doc, ttml_child_element.tail))

    return element

  @staticmethod
  def from_model(parent_element, parent_div):
    
    if parent_div is None:
      return

    span_element = et.SubElement(parent_element, "span")

    if parent_div.has_children():
      for child in parent_div:
        if isinstance(child, model.Span):
          SpanElement.from_model(parent_element, child)
        elif isinstance(child, model.Br):
          BrElement.from_model(parent_element, child)
        elif isinstance(child, model.Text):
          # TODO - do we want to have a TextElement object?
          #TextElement.from_model(parent_element, child)          
          span_element.text = child.get_text()
        else:
          LOGGER.error("Children of div must be p or div")
    else:
      pass


class RubyElement:
  '''Process the TTML <span tts:ruby="container"> element
  '''

  ruby = "container"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Ruby(context.doc)

    # process attributes
    
    element.set_space(imsc_attr.XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(imsc_attr.XMLLangAttribute.extract(ttml_element) or inherited_lang)

    ContentElement.process_region_property(context, ttml_element, element)

    ContentElement.process_style_properties(context, ttml_element, element)

    # process children elements

    children = []

    for ttml_child_element in ttml_element:
      child_element = ContentElement.process(
        context,
        element.get_space(),
        element.get_lang(),
        ttml_child_element
      )

      if child_element is not None:

        children.append(child_element)

    try:

      element.push_children(children)

      return element

    except (RuntimeError, TypeError):
      
      LOGGER.error("Malformed ruby element")

      return None

  @staticmethod
  def from_model(parent_element, parent_div):
    
    if parent_div is None:
      return

class RbElement:
  '''Process the TTML <span tts:ruby="base"> element
  '''

  ruby = "base"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Rb(context.doc)

    # process attributes
    
    element.set_space(imsc_attr.XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(imsc_attr.XMLLangAttribute.extract(ttml_element) or inherited_lang)

    ContentElement.process_region_property(context, ttml_element, element)

    ContentElement.process_style_properties(context, ttml_element, element)

    # process head text node

    if ttml_element.text is not None:
      element.push_child(SpanElement.make_anonymous_span(context.doc, ttml_element.text))

    # process children elements

    for ttml_child_element in ttml_element:

      child_element = ContentElement.process(
        context,
        element.get_space(),
        element.get_lang(),
        ttml_child_element
      )

      if child_element is not None:

        if not isinstance(child_element, model.Span):

          LOGGER.error("Children of rb must be span instances")

        else:

          element.push_child(child_element)

      # process tail text node

      if ttml_child_element.tail:
        element.push_child(SpanElement.make_anonymous_span(context.doc, ttml_child_element.tail))

    return element

  @staticmethod
  def from_model(parent_element, parent_div):
    
    if parent_div is None:
      return

class RtElement:
  '''Process the TTML <span tts:ruby="text"> element
  '''

  ruby = "text"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Rt(context.doc)

    # process attributes
    
    element.set_space(imsc_attr.XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(imsc_attr.XMLLangAttribute.extract(ttml_element) or inherited_lang)

    ContentElement.process_region_property(context, ttml_element, element)

    ContentElement.process_style_properties(context, ttml_element, element)

    # process head text node

    if ttml_element.text is not None:
      element.push_child(SpanElement.make_anonymous_span(context.doc, ttml_element.text))

    # process children elements

    for ttml_child_element in ttml_element:

      child_element = ContentElement.process(
        context,
        element.get_space(),
        element.get_lang(),
        ttml_child_element
      )

      if child_element is not None:

        if not isinstance(child_element, model.Span):

          LOGGER.error("Children of rt must be span instances")

        else:

          element.push_child(child_element)

      # process tail text node

      if ttml_child_element.tail:
        element.push_child(SpanElement.make_anonymous_span(context.doc, ttml_child_element.tail))

    return element

  @staticmethod
  def from_model(parent_element, parent_div):
    
    if parent_div is None:
      return

class RpElement:
  '''Process the TTML <span tts:ruby="delimiter"> element
  '''

  ruby = "delimiter"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Rp(context.doc)

    # process attributes
    
    element.set_space(imsc_attr.XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(imsc_attr.XMLLangAttribute.extract(ttml_element) or inherited_lang)

    ContentElement.process_region_property(context, ttml_element, element)

    ContentElement.process_style_properties(context, ttml_element, element)

    # process head text node

    if ttml_element.text is not None:
      element.push_child(SpanElement.make_anonymous_span(context.doc, ttml_element.text))

    # process children elements

    for ttml_child_element in ttml_element:

      child_element = ContentElement.process(
        context,
        element.get_space(),
        element.get_lang(),
        ttml_child_element
      )

      if child_element is not None:

        if not isinstance(child_element, model.Span):

          LOGGER.error("Children of rp must be span instances")

        else:

          element.push_child(child_element)

      # process tail text node

      if ttml_child_element.tail:
        element.push_child(SpanElement.make_anonymous_span(context.doc, ttml_child_element.tail))

    return element

  @staticmethod
  def from_model(parent_element, parent_div):
    
    if parent_div is None:
      return

class RbcElement:
  '''Process the TTML <span tts:ruby="baseContainer"> element
  '''

  ruby = "baseContainer"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Rbc(context.doc)

    # process attributes
    
    element.set_space(imsc_attr.XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(imsc_attr.XMLLangAttribute.extract(ttml_element) or inherited_lang)

    ContentElement.process_region_property(context, ttml_element, element)

    ContentElement.process_style_properties(context, ttml_element, element)

    # process children elements

    for ttml_child_element in ttml_element:

      child_element = ContentElement.process(
        context,
        element.get_space(),
        element.get_lang(),
        ttml_child_element
      )

      if child_element is not None:

        if not isinstance(child_element, model.Rb):

          LOGGER.error("Children of rbc must be rb instances")

        else:

          element.push_child(child_element)

    return element

  @staticmethod
  def from_model(parent_element, parent_div):
    
    if parent_div is None:
      return

class RtcElement:
  '''Process the TTML <span tts:ruby="textContainer"> element
  '''

  ruby = "textContainer"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Rtc(context.doc)

    # process attributes
    
    element.set_space(imsc_attr.XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(imsc_attr.XMLLangAttribute.extract(ttml_element) or inherited_lang)

    ContentElement.process_region_property(context, ttml_element, element)

    ContentElement.process_style_properties(context, ttml_element, element)

    # process children elements

    children = []

    for ttml_child_element in ttml_element:
      child_element = ContentElement.process(
        context,
        element.get_space(),
        element.get_lang(),
        ttml_child_element
      )

      if child_element is not None:

        children.append(child_element)

    try:

      element.push_children(children)

      return element

    except (RuntimeError, TypeError):
      
      LOGGER.error("Malformed rtc element")

      return None

  @staticmethod
  def from_model(parent_element, parent_div):
    
    if parent_div is None:
      return

class BrElement:
  '''Process the TTML <br> element
  '''

  qn = f"{{{xml_ns.TTML}}}br"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Br(context.doc)

    # process attributes
    
    element.set_space(imsc_attr.XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(imsc_attr.XMLLangAttribute.extract(ttml_element) or inherited_lang)

    ContentElement.process_style_properties(context, ttml_element, element)

    # process children elements

    if len(ttml_element) > 0:
      LOGGER.error("Br cannot contain children elements")

    if ttml_element.text is not None:
      LOGGER.error("Br cannot contain text nodes")

    return element

  @staticmethod
  def from_model(parent_element, parent_div):
    
    if parent_div is None:
      return
