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
import inspect
import ttconv.model as model


LOGGER = logging.getLogger(__name__)

TTML_NS = "http://www.w3.org/ns/ttml"
TTP_NS = "http://www.w3.org/ns/ttml#parameter"

def to_model(xml_tree):
  '''Convers an IMSC document to the data model'''

  class _Context:
    def __init__(self):
      self.doc = None
      self.cell_resolution = None

  context = _Context()

  tt_element = xml_tree.getroot()

  if tt_element.tag != TTElement.qn:
    LOGGER.fatal("A tt element is not the root element")
    return None

  TTElement.process(context, tt_element)

  return context.doc



class TTElement:
  '''Processes the TTML <tt> element
  '''

  qn = f"{{{TTML_NS}}}tt"

  @staticmethod
  def process(context, ttml_elem):

    context.doc = model.Document()

    # process attributes

    space = XMLSpaceAttribute.extract(ttml_elem) or model.WhiteSpaceHandling.DEFAULT

    lang = XMLLangAttribute.extract(ttml_elem)
    
    if lang is None:
      LOGGER.warning("xml:lang not specified on tt")
      lang = ""

    context.cell_resolution = CellResolutionAttribute.extract(ttml_elem)

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

  qn = f"{{{TTML_NS}}}head"

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

  qn = f"{{{TTML_NS}}}layout"

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

  qn = f"{{{TTML_NS}}}region"

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

  qn = f"{{{TTML_NS}}}styling"

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
  def process_style_properties(_context, ttml_element, element):
    '''Read TTML style properties into the model'''
    for attr in ttml_element.attrib:
      prop = StyleProperties.BY_QNAME.get(attr)
      if prop is not None:
        element.set_style(prop.model_prop, prop.extract(ttml_element.attrib.get(attr)))

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    if ttml_element.tag == BodyElement.qn:

      element = BodyElement.process(context, inherited_space, inherited_lang, ttml_element)

    elif ttml_element.tag == DivElement.qn:

      element = DivElement.process(context, inherited_space, inherited_lang, ttml_element)

    elif ttml_element.tag == PElement.qn:

      element = PElement.process(context, inherited_space, inherited_lang, ttml_element)

    elif ttml_element.tag == SpanElement.qn:

      element = SpanElement.process(context, inherited_space, inherited_lang, ttml_element)

    elif ttml_element.tag == BrElement.qn:

      element = BrElement.process(context, inherited_space, inherited_lang, ttml_element)

    else:

      return None

    return element

class BodyElement:
  '''Process TTML body element
  '''

  qn = f"{{{TTML_NS}}}body"

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

  qn = f"{{{TTML_NS}}}div"

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

  qn = f"{{{TTML_NS}}}p"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.P(context.doc)

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

        if not isinstance(child_element, (model.Span, model.Br)):

          LOGGER.error("Children of p must be span or br instances")

        else:

          element.push_child(child_element)

    return element



class SpanElement:
  '''Process the TTML <span> element
  '''

  qn = f"{{{TTML_NS}}}span"

  @staticmethod
  def process(context, inherited_space, inherited_lang, ttml_element):

    element = model.Span(context.doc)

    # process attributes
    
    element.set_space(XMLSpaceAttribute.extract(ttml_element) or inherited_space)

    element.set_lang(XMLLangAttribute.extract(ttml_element) or inherited_lang)

    ContentElement.process_region_property(context, ttml_element, element)

    ContentElement.process_style_properties(context, ttml_element, element)

    # process text node

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

      if ttml_child_element.tail is not None:

        element.push_child(model.Text(context.doc, ttml_element.text))

    return element

class BrElement:
  '''Process the TTML <br> element
  '''

  qn = f"{{{TTML_NS}}}br"

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
# style properties
#

class StyleProperty:
  '''Base class for style properties'''

  @staticmethod
  def extract(xml_attrib):
    '''Converts an IMSC style property to a data model value'''


class StyleProperties:
  '''TTML style properties

  Class variables:
  
  `BY_QNAME`: mapping of qualified name to StyleProperty class
  '''

  class LineHeight(StyleProperty):
    '''tts:lineHeight'''

    LENGTH_RE = re.compile(r"^((?:\+|\-)?\d*(?:\.\d+)?)(px|em|c|%|rh|rw)$")

    model_prop = model.StyleProperties.LineHeight

    @staticmethod
    def extract(xml_attrib):

      if xml_attrib == "normal":

        r = xml_attrib

      else:
        m = StyleProperties.LineHeight.LENGTH_RE.match(xml_attrib)

        if m is None:
          raise Exception("Unsupported length")
      
        r = model.LengthType(float(m.group(1)), model.LengthType.Units(m.group(2)))
      
      return r

  BY_QNAME = {
    f"{{{v.model_prop.ns}}}{v.model_prop.local_name}" : v
    for n, v in list(locals().items()) if inspect.isclass(v)
    }
    
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

  qn = f"{TTP_NS}cellResolution"

  class ValueType:
    '''Value of the ttp:cellResolution attribute'''
    def __init__(self, rows=15, columns=32):
      self.rows = rows
      self.columns = columns

  _CELL_RESOLUTION_RE = re.compile(r"(\d+) (\d+)")

  @staticmethod
  def extract(ttml_element):

    r = CellResolutionAttribute.ValueType()

    cr = ttml_element.attrib.get(CellResolutionAttribute.qn)

    if cr is not None:

      m = CellResolutionAttribute._CELL_RESOLUTION_RE.match(cr)

      if m is not None:

        r = CellResolutionAttribute.ValueType(int(m.group(1)), int(m.group(2)))

      else:

        LOGGER.error("ttp:cellResolution invalid syntax")

    return r
