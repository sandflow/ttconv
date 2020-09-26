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

'''IMSC reader'''

import re
import logging
import ttconv.model as model
import ttconv.imsc.utils as utils
from ttconv.imsc.style_properties import StyleProperties


LOGGER = logging.getLogger(__name__)


def to_model(xml_tree):
  '''Convers an IMSC document to the data model'''

  class _Context:
    def __init__(self):
      self.doc = None

  context = _Context()

  tt_element = xml_tree.getroot()

  if tt_element.tag != TTElement.qn:
    LOGGER.fatal("A tt element is not the root element")
    return None

  TTElement.process(context, tt_element)

  return context.doc



class TTMLNamespaces:
  '''Holds XML namespaces defined by TTML
  '''
  TTML = "http://www.w3.org/ns/ttml"
  TTP = "http://www.w3.org/ns/ttml#parameter"
  TTS = "http://www.w3.org/ns/ttml#styling"
  ITTP = "http://www.w3.org/ns/ttml/profile/imsc1#parameter"

class TTElement:
  '''Processes the TTML <tt> element
  '''

  qn = f"{{{TTMLNamespaces.TTML}}}tt"

  @staticmethod
  def process(context, ttml_elem):

    context.doc = model.Document()

    # process attributes

    space = XMLSpaceAttribute.extract(ttml_elem) or model.WhiteSpaceHandling.DEFAULT

    lang = XMLLangAttribute.extract(ttml_elem)
    
    if lang is None:
      LOGGER.warning("xml:lang not specified on tt")
      lang = ""

    context.doc.set_cell_resolution(CellResolutionAttribute.extract(ttml_elem))

    px_resolution = ExtentAttribute.extract(ttml_elem)

    if px_resolution is not None:
      context.doc.set_px_resolution(px_resolution)

    active_area = ActiveAreaAttribute.extract(ttml_elem)

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

class HeadElement:
  '''Processes the TTML <head> element
  '''

  qn = f"{{{TTMLNamespaces.TTML}}}head"

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
            XMLSpaceAttribute.extract(ttml_element) or inherited_space,
            XMLLangAttribute.extract(ttml_element) or inherited_lang,
            child_element
          )

        else:

          LOGGER.error("Multiple layout elements")

      elif child_element.tag == StylingElement.qn:

        if not has_styling:

          has_styling = True

          StylingElement.process(
            context,
            XMLSpaceAttribute.extract(ttml_element) or inherited_space,
            XMLLangAttribute.extract(ttml_element) or inherited_lang,
            child_element
          )

        else:

          LOGGER.error("Multiple styling elements")



class LayoutElement:
  '''Process the TTML <layout> element
  '''

  qn = f"{{{TTMLNamespaces.TTML}}}layout"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):
    
    for child_element in ttml_element:

      if child_element.tag == RegionElement.qn:

        r = RegionElement.process(
          context,
          XMLSpaceAttribute.extract(ttml_element) or inherited_space,
          XMLLangAttribute.extract(ttml_element) or inherited_lang,
          child_element
        )

        if r is not None:
          context.doc.put_region(r)

      #elif child_element.tag == INITIAL_ELEMENT_QNAME:

      #  _process_initial_element(context, space, lang, child_element)

      else:

        LOGGER.warning("Unexpected child of layout element")



class RegionElement:
  '''Process the TTML <region> element
  '''

  qn = f"{{{TTMLNamespaces.TTML}}}region"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    rid = XMLIDAttribute.extract(ttml_element)

    if rid is None:
      LOGGER.error("All regions must have an id")
      return None

    r = model.Region(rid, context.doc)

    # process attributes
    
    r.set_space(XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    r.set_lang(XMLLangAttribute.extract(ttml_element) or inherited_lang)
    
    ContentElement.process_style_properties(context, ttml_element, r)

    return r

class StylingElement:
  '''Process the TTML <styling> element
  '''

  qn = f"{{{TTMLNamespaces.TTML}}}styling"

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

class BodyElement:
  '''Process TTML body element
  '''

  qn = f"{{{TTMLNamespaces.TTML}}}body"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Body(context.doc)

    # process attributes
    
    element.set_space(XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(XMLLangAttribute.extract(ttml_element) or inherited_lang)

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


class DivElement:
  '''Process TTML <div> element
  '''

  qn = f"{{{TTMLNamespaces.TTML}}}div"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Div(context.doc)

    # process attributes
    
    element.set_space(XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(XMLLangAttribute.extract(ttml_element) or inherited_lang)

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

class PElement:
  '''Process TTML <p> element
  '''

  qn = f"{{{TTMLNamespaces.TTML}}}p"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.P(context.doc)

    # process attributes
    
    element.set_space(XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(XMLLangAttribute.extract(ttml_element) or inherited_lang)

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

class SpanElement:
  '''Process the TTML <span> element
  '''

  qn = f"{{{TTMLNamespaces.TTML}}}span"

  @staticmethod
  def make_anonymous_span(doc, text):

    s = model.Span(doc)
    t = model.Text(doc, text)
    s.push_child(t)

    return s

  @staticmethod
  def get_ruby_attr(ttml_span):
    return ttml_span.get(f"{{{TTMLNamespaces.TTS}}}ruby")

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Span(context.doc)

    # process attributes
    
    element.set_space(XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(XMLLangAttribute.extract(ttml_element) or inherited_lang)

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


class RubyElement:
  '''Process the TTML <span tts:ruby="container"> element
  '''

  ruby = "container"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Ruby(context.doc)

    # process attributes
    
    element.set_space(XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(XMLLangAttribute.extract(ttml_element) or inherited_lang)

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


class RbElement:
  '''Process the TTML <span tts:ruby="base"> element
  '''

  ruby = "base"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Rb(context.doc)

    # process attributes
    
    element.set_space(XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(XMLLangAttribute.extract(ttml_element) or inherited_lang)

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


class RtElement:
  '''Process the TTML <span tts:ruby="text"> element
  '''

  ruby = "text"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Rt(context.doc)

    # process attributes
    
    element.set_space(XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(XMLLangAttribute.extract(ttml_element) or inherited_lang)

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


class RpElement:
  '''Process the TTML <span tts:ruby="delimiter"> element
  '''

  ruby = "delimiter"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Rp(context.doc)

    # process attributes
    
    element.set_space(XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(XMLLangAttribute.extract(ttml_element) or inherited_lang)

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

class RbcElement:
  '''Process the TTML <span tts:ruby="baseContainer"> element
  '''

  ruby = "baseContainer"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Rbc(context.doc)

    # process attributes
    
    element.set_space(XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(XMLLangAttribute.extract(ttml_element) or inherited_lang)

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


class RtcElement:
  '''Process the TTML <span tts:ruby="textContainer"> element
  '''

  ruby = "textContainer"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Rtc(context.doc)

    # process attributes
    
    element.set_space(XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(XMLLangAttribute.extract(ttml_element) or inherited_lang)

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


class BrElement:
  '''Process the TTML <br> element
  '''

  qn = f"{{{TTMLNamespaces.TTML}}}br"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Br(context.doc)

    # process attributes
    
    element.set_space(XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(XMLLangAttribute.extract(ttml_element) or inherited_lang)

    ContentElement.process_style_properties(context, ttml_element, element)

    # process children elements

    if len(ttml_element) > 0:
      LOGGER.error("Br cannot contain children elements")

    if ttml_element.text is not None:
      LOGGER.error("Br cannot contain text nodes")

    return element


#
# other attributes
#

class XMLIDAttribute:
  '''xml:id attribute
  '''

  qn = '{http://www.w3.org/XML/1998/namespace}id'

  @staticmethod
  def extract(ttml_element):
    return ttml_element.attrib.get(XMLIDAttribute.qn)



class XMLLangAttribute:
  '''xml:lang attribute
  '''

  qn = '{http://www.w3.org/XML/1998/namespace}lang'

  @staticmethod
  def extract(ttml_element):
    return ttml_element.attrib.get(XMLLangAttribute.qn)



class XMLSpaceAttribute:
  '''xml:space attribute
  '''

  qn = '{http://www.w3.org/XML/1998/namespace}space'

  @staticmethod
  def extract(ttml_element):

    value = ttml_element.attrib.get(XMLSpaceAttribute.qn)

    r = None

    if value is not None:

      try: 
        r = model.WhiteSpaceHandling(value)
      except ValueError:
        LOGGER.error("Bad xml:space value (%s)", value)
    
    return r



class RegionAttribute:
  '''TTML region attribute'''

  qn = "region"

  @staticmethod
  def extract(ttml_element):
    return ttml_element.attrib.get(RegionAttribute.qn)



class CellResolutionAttribute:
  '''ttp:cellResolution attribute
  '''

  qn = f"{TTMLNamespaces.TTP}cellResolution"

  _CELL_RESOLUTION_RE = re.compile(r"(\d+) (\d+)")

  @staticmethod
  def extract(ttml_element) -> model.CellResolutionType:

    cr = ttml_element.attrib.get(CellResolutionAttribute.qn)

    if cr is not None:

      m = CellResolutionAttribute._CELL_RESOLUTION_RE.match(cr)

      if m is not None:

        return model.CellResolutionType(int(m.group(1)), int(m.group(2)))

      LOGGER.error("ttp:cellResolution invalid syntax")

    # default value in TTML

    return model.CellResolutionType(rows=15, columns=32)

class ExtentAttribute:
  '''ttp:extent attribute on \\<tt\\>
  '''

  qn = f"{{{TTMLNamespaces.TTS}}}extent"

  @staticmethod
  def extract(ttml_element) -> model.PixelResolutionType:

    extent = ttml_element.attrib.get(ExtentAttribute.qn)

    if extent is not None:

      s = extent.split(" ")

      (w, w_units) = utils.parse_length(s[0])

      (h, h_units) = utils.parse_length(s[1])

      if w_units != "px" or h_units != "px":
        LOGGER.error("ttp:extent on <tt> does not use px units")
        return None

      return model.PixelResolutionType(w, h)

    return None

class ActiveAreaAttribute:
  '''ittp:activeArea attribute on \\<tt\\>
  '''

  qn = f"{{{TTMLNamespaces.ITTP}}}activeArea"

  @staticmethod
  def extract(ttml_element) -> model.ActiveAreaType:

    aa = ttml_element.attrib.get(ActiveAreaAttribute.qn)

    if aa is not None:

      s = aa.split(" ")

      if len(s) != 4:
        LOGGER.error("Syntax error in ittp:activeArea on <tt>")
        return None

      (left_offset, left_offset_units) = utils.parse_length(s[0])

      (top_offset, top_offset_units) = utils.parse_length(s[1])

      (w, w_units) = utils.parse_length(s[2])

      (h, h_units) = utils.parse_length(s[3])

      if w_units != "%" or h_units != "%" or left_offset_units != "%" or top_offset_units != "%":
        LOGGER.error("ittp:activeArea on <tt> must use % units")
        return None

      return model.ActiveAreaType(
        left_offset / 100,
        top_offset / 100,
        w / 100,
        h / 100
        )

    return None
