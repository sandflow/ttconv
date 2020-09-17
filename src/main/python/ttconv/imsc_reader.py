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

LOGGER = logging.getLogger(__name__)

TTML_NS = "http://www.w3.org/ns/ttml"
TTP_NS = "http://www.w3.org/ns/ttml#parameter"

class _Context:
  def __init__(self):
    self.doc = None
    self.cr_columns = 32
    self.cr_rows = 15

#
# process tt element
#

TT_ELEMENT_QNAME = f"{{{TTML_NS}}}tt"

def _process_tt_element(context, ttml_elem):

  context.doc = model.Document()

  # process attributes

  space = _get_xml_space(ttml_elem) or model.WhiteSpaceHandling.DEFAULT

  lang = _get_xml_lang(ttml_elem)
  
  if lang is None:
    LOGGER.warning("xml:lang not specified on tt")
    lang = ""

  _process_cell_resolution(context, ttml_elem)

  # process children elements elements

  has_body = False
  has_head = False

  for child_element in ttml_elem:

    if child_element.tag == BODY_ELEMENT_QNAME:

      if not has_body:

        context.doc.set_body(
          _process_content_element(
            context,
            space,
            lang,
            child_element
          )
        )

        has_body = True

      else:
        LOGGER.error("More than one body element present")

    elif child_element.tag == HEAD_ELEMENT_QNAME:

      if not has_head:
        _process_head_element(
          context,
          space,
          lang,
          child_element
        )

        has_head = True

      else:
        LOGGER.error("More than one head element present")

#
# process head element
#

HEAD_ELEMENT_QNAME = f"{{{TTML_NS}}}head"

def _process_head_element(context, inherited_space, inherited_lang, ttml_element):

  # process children elements

  has_layout = False
  has_styling = False
  
  for child_element in ttml_element:

    if child_element.tag == LAYOUT_ELEMENT_QNAME:

      if not has_layout:

        has_layout = True

        _process_layout_element(
          context,
          _get_xml_space(ttml_element) or inherited_space,
          _get_xml_lang(ttml_element) or inherited_lang,
          child_element
        )

      else:

        LOGGER.error("Multiple layout elements")

    elif child_element.tag == STYLING_ELEMENT_QNAME:

      if not has_styling:

        has_styling = True

        _process_styling_element(
          context,
          _get_xml_space(ttml_element) or inherited_space,
          _get_xml_lang(ttml_element) or inherited_lang,
          child_element
        )

      else:

        LOGGER.error("Multiple styling elements")

#
# process layout element
#

LAYOUT_ELEMENT_QNAME = f"{{{TTML_NS}}}layout"

def _process_layout_element(context, inherited_space, inherited_lang, ttml_element):
  
  for child_element in ttml_element:

    if child_element.tag == REGION_ELEMENT_QNAME:

      r = _process_region_element(
        context,
        _get_xml_space(ttml_element) or inherited_space,
        _get_xml_lang(ttml_element) or inherited_lang,
        child_element
      )

      if r is not None:
        context.doc.put_region(r)

    #elif child_element.tag == INITIAL_ELEMENT_QNAME:

    #  _process_initial_element(context, space, lang, child_element)

    else:

      LOGGER.warning("Unexpected child of layout element")

#
# process region element
#

REGION_ELEMENT_QNAME = f"{{{TTML_NS}}}region"

def _process_region_element(context, inherited_space, inherited_lang, ttml_element):


  rid = _get_id(ttml_element)

  if rid is None:
    LOGGER.error("All regions must have an id")
    return None

  r = model.Region(rid, context.doc)

  # process attributes
  
  r.set_space(_get_xml_space(ttml_element) or inherited_space)

  r.set_lang(_get_xml_lang(ttml_element) or inherited_lang)
  
  _process_style_properties(context, ttml_element, r)

  return r

#
# process styling element
#

STYLING_ELEMENT_QNAME = f"{{{TTML_NS}}}styling"

def _process_styling_element(_context, _inherited_space, _inherited_lang, _ttml_element):
  pass

#
# process content elements
#

def _process_content_element(context, inherited_space, inherited_lang, ttml_element):

  if ttml_element.tag == BODY_ELEMENT_QNAME:

    element = _process_body_element(context, inherited_space, inherited_lang, ttml_element)

  elif ttml_element.tag == DIV_ELEMENT_QNAME:

    element = _process_div_element(context, inherited_space, inherited_lang, ttml_element)

  elif ttml_element.tag == P_ELEMENT_QNAME:

    element = _process_p_element(context, inherited_space, inherited_lang, ttml_element)

  elif ttml_element.tag == SPAN_ELEMENT_QNAME:

    element = _process_span_element(context, inherited_space, inherited_lang, ttml_element)

  elif ttml_element.tag == BR_ELEMENT_QNAME:

    element = _process_br_element(context, inherited_space, inherited_lang, ttml_element)

  else:

    return None

  return element

#
# process Body
#

BODY_ELEMENT_QNAME = f"{{{TTML_NS}}}body"

def _process_body_element(context, inherited_space, inherited_lang, ttml_element):

  element = model.Body(context.doc)

  # process attributes
  
  element.set_space(_get_xml_space(ttml_element) or inherited_space)

  element.set_lang(_get_xml_lang(ttml_element) or inherited_lang)

  _process_region_property(context, ttml_element, element)

  _process_style_properties(context, ttml_element, element)

  # process children elements

  for ttml_child_element in ttml_element:
    child_element = _process_content_element(
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

#
# process Div
#

DIV_ELEMENT_QNAME = f"{{{TTML_NS}}}div"

def _process_div_element(context, inherited_space, inherited_lang, ttml_element):

  element = model.Div(context.doc)

  # process attributes
  
  element.set_space(_get_xml_space(ttml_element) or inherited_space)

  element.set_lang(_get_xml_lang(ttml_element) or inherited_lang)

  _process_region_property(context, ttml_element, element)

  _process_style_properties(context, ttml_element, element)

  # process children elements

  for ttml_child_element in ttml_element:
    child_element = _process_content_element(
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

#
# process P
#

P_ELEMENT_QNAME = f"{{{TTML_NS}}}p"

def _process_p_element(context, inherited_space, inherited_lang, ttml_element):

  element = model.P(context.doc)

  # process attributes
  
  element.set_space(_get_xml_space(ttml_element) or inherited_space)

  element.set_lang(_get_xml_lang(ttml_element) or inherited_lang)

  _process_region_property(context, ttml_element, element)

  _process_style_properties(context, ttml_element, element)

  # process children elements

  for ttml_child_element in ttml_element:
    child_element = _process_content_element(
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

#
# process Span
#

SPAN_ELEMENT_QNAME = f"{{{TTML_NS}}}span"

def _process_span_element(context, inherited_space, inherited_lang, ttml_element):

  element = model.Span(context.doc)

  # process attributes
  
  element.set_space(_get_xml_space(ttml_element) or inherited_space)

  element.set_lang(_get_xml_lang(ttml_element) or inherited_lang)

  _process_region_property(context, ttml_element, element)

  _process_style_properties(context, ttml_element, element)

  # process text node

  if ttml_element.text is not None:
    element.push_child(model.Text(context.doc, ttml_element.text))

  # process children elements

  for ttml_child_element in ttml_element:

    child_element = _process_content_element(
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

#
# process Br
#

BR_ELEMENT_QNAME = f"{{{TTML_NS}}}br"

def _process_br_element(context, inherited_space, inherited_lang, ttml_element):

  element = model.Br(context.doc)

  # process attributes
  
  element.set_space(_get_xml_space(ttml_element) or inherited_space)

  element.set_lang(_get_xml_lang(ttml_element) or inherited_lang)

  _process_style_properties(context, ttml_element, element)

  # process children elements

  if len(ttml_element) > 0:
    LOGGER.error("Br cannot contain children elements")

  if ttml_element.text is not None:
    LOGGER.error("Br cannot contain text nodes")

  return element

#
# imsc reader
#

def to_model(xml_tree):
  '''Convers an IMSC document to the data model'''

  context = _Context()

  tt_element = xml_tree.getroot()

  if tt_element.tag != TT_ELEMENT_QNAME:
    LOGGER.fatal("A tt element is not the root element")
    return None

  _process_tt_element(context, tt_element)

  return context.doc


#
# extract style properties
#

def _process_style_properties(_context, ttml_element, element):
  for attr in ttml_element.attrib:
    prop = StyleProperties.BY_QNAME.get(attr)
    if prop is not None:
      element.set_style(prop.model_prop, prop.extract(ttml_element.attrib.get(attr)))

#
# Process region attribute
#

def _process_region_property(context, ttml_element, element):
  rid = ttml_element.attrib.get('region')

  if rid is not None:
    r = context.doc.get_region(rid)
    
    if r is not None:
      element.set_region(r)
    else:
      LOGGER.warning("Element references unknown region")

#
# style properties
#

class StyleProperty:
  '''Base class for style properties'''

  @staticmethod
  def extract(xml_attrib):
    '''Converts an IMSC style property to a data model value'''


class StyleProperties:
  '''TTML2 style properties'''

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

  # register all style properties by qualified name

  BY_QNAME = {
    f"{{{v.model_prop.ns}}}{v.model_prop.local_name}" : v
    for n, v in list(locals().items()) if callable(v)
    }

#
# xml:id
#

XMLID_ATTRIB_QNAME = '{http://www.w3.org/XML/1998/namespace}id'

def _get_id(ttml_element):
  return ttml_element.attrib.get(XMLID_ATTRIB_QNAME)

#
# xml:lang
#

XMLLANG_ATTRIB_QNAME = '{http://www.w3.org/XML/1998/namespace}lang'

def _get_xml_lang(ttml_element):
  return ttml_element.attrib.get(XMLLANG_ATTRIB_QNAME)

#
# xml:space
#

XMLSPACE_ATTRIB_QNAME = '{http://www.w3.org/XML/1998/namespace}space'

def _get_xml_space(ttml_element):
  value = ttml_element.attrib.get(XMLSPACE_ATTRIB_QNAME)
  space = None

  if value is not None:

    try: 
      space = model.WhiteSpaceHandling(value)
    except ValueError:
      LOGGER.error("Bad xml:space value (%s)", value)
      
    
  return space

#
# ttp:cellResolution
#

CELLRESOLUTION_ATTRIB_QNAME = f"{TTP_NS}cellResolution"

CELL_RESOLUTION_RE = re.compile(r"(\d+) (\d+)")

def _process_cell_resolution(context, ttml_element):

  cr = ttml_element.attrib.get(CELLRESOLUTION_ATTRIB_QNAME)

  if cr is not None:

    m = CELL_RESOLUTION_RE.match(cr)

    if m is not None:

      context.cr_columns = m.group(1)
      context.cr_rows = m.group(2)

    else:

      LOGGER.error("ttp:cellResolution invalid syntax")
