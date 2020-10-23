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

from __future__ import annotations
import logging
from fractions import Fraction
import typing
import ttconv.model as model
import ttconv.imsc.namespaces as xml_ns
import ttconv.imsc.attributes as imsc_attr
from ttconv.imsc.style_properties import StyleProperties
import ttconv.imsc.style_properties as imsc_styles
import xml.etree.ElementTree as et

LOGGER = logging.getLogger(__name__)

class TTMLElement:
  '''Static information about a TTML element
  '''

  class ParsingContext:
    '''State information when parsing a TTML element'''

    def __init__(self, ttml_class: TTMLElement, parent_ctx: typing.Optional[TTMLElement.ParsingContext] = None):

      self.doc = parent_ctx.doc if parent_ctx is not None else model.Document()

      self.style_context = parent_ctx.style_context if parent_ctx else imsc_styles.StyleParsingContext()

      self.style_elements: typing.Dict[str, StyleElement] = parent_ctx.style_elements if parent_ctx else {}

      self.temporal_context = parent_ctx.temporal_context if parent_ctx else imsc_attr.TemporalAttributeParsingContext()

      self.ttml_class: TTMLElement = ttml_class

      self.lang = None

      self.space = None

      self.time_container: imsc_attr.TimeContainer = imsc_attr.TimeContainer.par

      self.explicit_begin = None

      self.implicit_begin = None

      self.desired_begin = None

      self.explicit_end = None

      self.implicit_end = None

      self.desired_end = None

      self.explicit_dur = None

    def process_lang_attribute(self, parent_ctx: TTMLElement.ParsingContext, xml_elem):
      '''Processes the xml:lang attribute, including inheritance from the parent
      '''
      self.lang = imsc_attr.XMLLangAttribute.extract(xml_elem) or parent_ctx.lang

    def process_space_attribute(self, parent_ctx: TTMLElement.ParsingContext, xml_elem):
      '''Processes the xml:space attribute, including inheritance from the parent
      '''
      self.space = imsc_attr.XMLSpaceAttribute.extract(xml_elem) or parent_ctx.space

  @staticmethod
  def is_instance(xml_elem) -> bool:
    '''Returns true if the XML element `xml_elem` is an instance of the class
    '''
    raise NotImplementedError

  @staticmethod
  def from_xml(parent_ctx, xml_elem):
    '''Returns a parsing context for the TTML element represented by the XML element `xml_elem` and
    given the parent context `parent_ctx`
    '''
    raise NotImplementedError

  @staticmethod
  def from_model(model_value, xml_element):
    '''Returns a parsing context for the TTML element represented by the XML element `xml_elem` and
    given the parent context `parent_ctx`
    '''
    raise NotImplementedError


class TTElement(TTMLElement):
  '''Processes the TTML <tt> element
  '''

  class ParsingContext(TTMLElement.ParsingContext):
    '''State information when parsing a <tt> element'''

  qn = f"{{{xml_ns.TTML}}}tt"

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == TTElement.qn

  @staticmethod
  def from_xml(_parent_ctx: typing.Optional[TTMLElement.ParsingContext], xml_elem) -> TTElement.ParsingContext:
    '''`_parent_ctx` is ignored and can be set to `None`
    '''

    tt_ctx = TTElement.ParsingContext(TTElement)

    tt_ctx.space = imsc_attr.XMLSpaceAttribute.extract(xml_elem) or model.WhiteSpaceHandling.DEFAULT

    lang_attr = imsc_attr.XMLLangAttribute.extract(xml_elem)

    if lang_attr is None:
      LOGGER.warning("xml:lang not specified on tt")
      lang_attr = ""

    tt_ctx.lang = lang_attr

    tt_ctx.doc.set_lang(tt_ctx.lang)

    tt_ctx.doc.set_cell_resolution(
      imsc_attr.CellResolutionAttribute.extract(xml_elem)
    )

    px_resolution = imsc_attr.ExtentAttribute.extract(xml_elem)

    if px_resolution is not None:
      tt_ctx.doc.set_px_resolution(px_resolution)

    active_area = imsc_attr.ActiveAreaAttribute.extract(xml_elem)

    if active_area is not None:
      tt_ctx.doc.set_active_area(active_area)

    tt_ctx.temporal_context.frame_rate = imsc_attr.FrameRateAttribute.extract(xml_elem)

    tt_ctx.temporal_context.tick_rate = imsc_attr.TickRateAttribute.extract(xml_elem)

    # process children elements elements

    has_body = False
    has_head = False

    for child_element in xml_elem:

      if BodyElement.is_instance(child_element):

        if not has_body:

          has_body = True

          body_element = ContentElement.from_xml(tt_ctx, child_element)

          tt_ctx.doc.set_body(body_element.model_element if body_element is not None else None)

        else:
          LOGGER.error("More than one body element present")

      elif HeadElement.is_instance(child_element):

        if not has_head:

          has_head = True

          HeadElement.from_xml(tt_ctx, child_element)

        else:
          LOGGER.error("More than one head element present")

    return tt_ctx

  @staticmethod
  def from_model(model_value, context):

    body = model_value.get_body()

    space = model.WhiteSpaceHandling.DEFAULT
    
    if body is not None:
      lang = body.get_lang()
      if lang is not None:
        imsc_attr.XMLLangAttribute.set(context.imsc_doc, lang)

    imsc_attr.CellResolutionAttribute.set(context.imsc_doc, model_value.get_cell_resolution())
    imsc_attr.ExtentAttribute.set(context.imsc_doc, model_value.get_px_resolution())
    imsc_attr.ActiveAreaAttribute.set(context.imsc_doc, model_value.get_active_area())

    # Write the <head> section first
    for region in model_value.iter_regions():
      HeadElement.from_model(
        model_value, 
        context,
        region
      )

    body = model_value.get_body()
    if body is not None:
      BodyElement.from_model(
        context,
        body
      )

class HeadElement(TTMLElement):
  '''Processes the TTML <head> element
  '''

  class ParsingContext(TTMLElement.ParsingContext):
    '''Maintains state when parsing a <head> element
    '''

  qn = f"{{{xml_ns.TTML}}}head"

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == HeadElement.qn

  @staticmethod
  def from_xml(parent_ctx: TTMLElement.ParsingContext, xml_elem) -> HeadElement.ParsingContext:
    
    head_ctx = HeadElement.ParsingContext(HeadElement, parent_ctx)

    head_ctx.process_lang_attribute(parent_ctx, xml_elem)

    head_ctx.process_space_attribute(parent_ctx, xml_elem)

    # process children elements

    has_layout = False
    has_styling = False
    
    for child_element in xml_elem:

      if LayoutElement.is_instance(child_element):

        if not has_layout:

          has_layout = True

          LayoutElement.from_xml(
            head_ctx,
            child_element
          )

        else:

          LOGGER.error("Multiple layout elements")

      elif StylingElement.is_instance(child_element):

        if not has_styling:

          has_styling = True

          StylingElement.from_xml(
            head_ctx,
            child_element
          )

        else:

          LOGGER.error("Multiple styling elements")

    return head_ctx

  @staticmethod
  def from_model(i_model, context, region):

    # Check for exiting head
    head = context.imsc_doc.find("head")
    if head is None:
      head = et.SubElement(context.imsc_doc, "head")

    StylingElement.from_model(
      i_model,
      context,
      head
    )

    LayoutElement.from_model(
      head,
      region
    )


class LayoutElement(TTMLElement):
  '''Process the TTML <layout> element
  '''
  
  class ParsingContext(TTMLElement.ParsingContext):
    '''Maintains state when parsing a <layout> element
    '''

  qn = f"{{{xml_ns.TTML}}}layout"

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == LayoutElement.qn

  @staticmethod
  def from_xml(parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[LayoutElement.ParsingContext]:

    layout_ctx = LayoutElement.ParsingContext(LayoutElement, parent_ctx)

    layout_ctx.process_lang_attribute(parent_ctx, xml_elem)

    layout_ctx.process_space_attribute(parent_ctx, xml_elem)
    
    for child_element in xml_elem:

      if RegionElement.is_instance(child_element):

        r = RegionElement.from_xml(layout_ctx, child_element)

        if r is not None:
          layout_ctx.doc.put_region(r.model_element)

      else:

        LOGGER.warning("Unexpected child of layout element")

    return layout_ctx

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

class StylingElement(TTMLElement):
  '''Process the TTML <styling> element
  '''

  class ParsingContext(TTMLElement.ParsingContext):
    '''Maintains state when parsing a <styling> element
    '''

    def merge_chained_styles(self, style_element: StyleElement):
      '''Flattens Chained Referential Styling of the target `style_element` by specifying
      the style properties of the referenced style elements directly in the target element
      '''

      while len(style_element.style_refs) > 0:

        style_ref = style_element.style_refs.pop()

        if style_ref not in self.style_elements:
          LOGGER.error("Style id not present")
          continue

        self.merge_chained_styles(self.style_elements[style_ref])

        for style_prop, value in self.style_elements[style_ref].styles.items():
          style_element.styles.setdefault(style_prop, value)

  qn = f"{{{xml_ns.TTML}}}styling"

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == StylingElement.qn

  @staticmethod
  def from_xml(parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[StylingElement.ParsingContext]:
    styling_ctx = StylingElement.ParsingContext(StylingElement, parent_ctx)

    for child_xml_elem in xml_elem:

      if InitialElement.is_instance(child_xml_elem):

        InitialElement.from_xml(styling_ctx, child_xml_elem)

      elif StyleElement.is_instance(child_xml_elem):
        
        style_element = StyleElement.from_xml(styling_ctx, child_xml_elem)

        if style_element is None:
          continue

        if style_element.id in styling_ctx.style_elements:
          LOGGER.error("Duplicate style id")
          continue

        style_element.style_elements[style_element.id] = style_element
      
    # merge style elements

    for style_element in parent_ctx.style_elements.values():
      styling_ctx.merge_chained_styles(style_element)

    return styling_ctx

  @staticmethod
  def from_model(model_value, context, xml_element):
    
    if model_value is None:
      return

    styling_element = context.imsc_doc.find("styling")
    if styling_element is None:
      styling_element = et.SubElement(xml_element, "styling")

    StyleElement.from_model(model_value, styling_element)

    #ContentElement.from_model_style_properties(model_value, styling_element)

    for init_val in model_value.iter_initial_values():
      InitialElement.from_model(init_val, styling_element)



class StyleElement(TTMLElement):
  '''Process the TTML <style> element
  '''

  class ParsingContext(TTMLElement.ParsingContext):
    '''Maintains state when parsing the element
    '''

    def __init__(self, parent_ctx: typing.Optional[TTMLElement.ParsingContext] = None):
      self.styles: typing.Dict[imsc_styles.StyleProperty, typing.Any] = dict()
      self.style_refs: typing.List[str] = None
      self.id: str = None
      super().__init__(StyleElement, parent_ctx)

  qn = f"{{{xml_ns.TTML}}}style"

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == StyleElement.qn

  @staticmethod
  def from_xml(parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[StyleElement.ParsingContext]:
    
    style_ctx = StyleElement.ParsingContext(parent_ctx)

    for attr in xml_elem.attrib:
      prop = StyleProperties.BY_QNAME.get(attr)

      if not prop:
        continue

      try:

        style_ctx.styles[prop.model_prop] = prop.extract(style_ctx.style_context, xml_elem.attrib.get(attr))

      except ValueError:

        LOGGER.error("Error reading style property: %s", prop.__name__)

    if issubclass(parent_ctx.ttml_class, RegionElement):

      # nested styling
      # merge style properties with the parent Region element

      for style_prop, value in style_ctx.styles.items():
        region_style = parent_ctx.model_element.get_style(style_prop)

        if region_style is None:
          parent_ctx.model_element.set_style(style_prop, value)

      return None

    # styling > style element

    style_ctx.style_refs = imsc_attr.StyleAttribute.extract(xml_elem)

    style_ctx.id = imsc_attr.XMLIDAttribute.extract(xml_elem)

    if style_ctx.id is None:
      LOGGER.error("A style element must have an id")
      return None

    return style_ctx


  @staticmethod
  def from_model(model_value, xml_element):
    
    if model_value is None:
      return

    styling_element = et.SubElement(xml_element, "style")

    #ContentElement.from_model_style_properties(model_value, styling_element)


class InitialElement(TTMLElement):
  '''Process the TTML <initial> element
  '''

  class ParsingContext(TTMLElement.ParsingContext):
    '''Maintains state when parsing the element
    '''

  qn = f"{{{xml_ns.TTML}}}initial"

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == InitialElement.qn

  @staticmethod
  def from_xml(parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[InitialElement.ParsingContext]:
    
    initial_ctx = InitialElement.ParsingContext(InitialElement, parent_ctx)

    for attr in xml_elem.attrib:

      prop = StyleProperties.BY_QNAME.get(attr)

      if not prop:

        continue

      try:

        initial_ctx.doc.put_initial_value(
          prop.model_prop,
          prop.extract(initial_ctx.style_context, xml_elem.attrib.get(attr))
        )

      except (ValueError, TypeError):

        LOGGER.error("Error reading style property: %s", prop.__name__)

    return initial_ctx


  @staticmethod
  def from_model(model_value, xml_element):
    
    if model_value is None:
      return

    initial_element = et.SubElement(xml_element, "initial")

    #ContentElement.from_model_style_properties(model_value, initial_element)


#
# process content elements
#

class ContentElement(TTMLElement):
  '''TTML content elements: body, div, p, span, br
  '''

  class ParsingContext(TTMLElement.ParsingContext):
    '''Maintains state when parsing the element
    '''
    def __init__(
        self,
        ttml_class: typing.Optional[TTMLElement],
        parent_ctx: TTMLElement.ParsingContext,
        model_element: typing.Optional[model.ContentElement] = None
      ):
      self.children: typing.List[model.ContentElement] = []
      self.model_element: model.ContentElement = model_element
      super().__init__(ttml_class, parent_ctx)

    def process_region_property(self, xml_elem):
      '''Reads and processes the `region` attribute
      '''
      rid = xml_elem.attrib.get('region')

      if rid is None:
        return

      r = self.doc.get_region(rid)
      
      if r is not None:
        self.model_element.set_region(r)
      else:
        LOGGER.warning("Element references unknown region")

    def process_referential_styling(self, xml_elem):
      '''Processes referential styling
      '''
      for style_ref in imsc_attr.StyleAttribute.extract(xml_elem):
        style_element = self.style_elements.get(style_ref)

        if style_element is None:
          LOGGER.error("non existant style id")
          continue

        for model_prop, value in style_element.styles.items():
          if self.model_element.get_style(model_prop) is None:
            self.model_element.set_style(model_prop, value)

    def process_specified_styling(self, xml_elem):
      '''Processes specified styling
      '''
      for attr in xml_elem.attrib:
        prop = StyleProperties.BY_QNAME.get(attr)

        if prop is None:
          continue

        try:
          self.model_element.set_style(
            prop.model_prop,
            prop.extract(self.style_context, xml_elem.attrib.get(attr))
            )
        except ValueError:
          LOGGER.error("Error reading style property: %s", prop.__name__)

    def process_set_style_properties(self, parent_ctx: TTMLElement, xml_elem):
      '''Processes style properties on `<set>` element
      '''
      if parent_ctx.model_element is None:
        LOGGER.error("Set parent does not exist")
        return

      if not issubclass(parent_ctx.ttml_class, ContentElement):
        LOGGER.error("Set parent is not a content element")
        return

      for attr in xml_elem.attrib:
        prop = StyleProperties.BY_QNAME.get(attr)
        if prop is not None:
          try:
            parent_ctx.model_element.add_animation_step(
              model.DiscreteAnimationStep(
                prop.model_prop,
                self.desired_begin,
                self.desired_end,
                prop.extract(self.style_context, xml_elem.attrib.get(attr))
              )
            )
            break
          except ValueError:
            LOGGER.error("Error reading style property: %s", prop.__name__)

    def process_lang_attribute(self, parent_ctx: TTMLElement.ParsingContext, xml_elem):
      super().process_lang_attribute(parent_ctx, xml_elem)
      self.model_element.set_lang(self.lang)

    def process_space_attribute(self, parent_ctx: TTMLElement.ParsingContext, xml_elem):
      super().process_space_attribute(parent_ctx, xml_elem)
      self.model_element.set_space(self.space)

    # pylint: disable=too-many-branches

    def process(self, parent_ctx: TTMLElement.ParsingContext, xml_elem):
      '''Generic processing applicable to TTML elements rooted in `region` and `body` elements
      '''
      self.process_lang_attribute(parent_ctx, xml_elem)

      self.process_space_attribute(parent_ctx, xml_elem)

      if self.ttml_class.has_region:
        self.process_region_property(xml_elem)

      if issubclass(self.ttml_class, SetElement):

        self.process_set_style_properties(parent_ctx, xml_elem)

      elif self.ttml_class.has_styles:

        self.process_specified_styling(xml_elem)

      # temporal processing

      self.time_container = imsc_attr.TimeContainerAttribute.extract(xml_elem)

      self.explicit_begin = imsc_attr.BeginAttribute.extract(self.temporal_context, xml_elem)

      self.explicit_dur = imsc_attr.DurAttribute.extract(self.temporal_context, xml_elem)

      self.explicit_end = imsc_attr.EndAttribute.extract(self.temporal_context, xml_elem)

      if parent_ctx.time_container.is_par():
        self.implicit_begin = Fraction(0)
      else:      
        self.implicit_begin = parent_ctx.implicit_end - parent_ctx.desired_begin
      
      self.desired_begin = self.implicit_begin + (self.explicit_begin if self.explicit_begin is not None else Fraction(0))

      if issubclass(self.ttml_class, (BrElement, RegionElement, SetElement)) and \
        parent_ctx.time_container.is_par():
        self.implicit_end = None
      else:
        self.implicit_end = self.desired_begin
        
      # process children elements

      if self.ttml_class.is_mixed and xml_elem.text is not None and self.time_container.is_par():
        self.children.append(ContentElement.make_anonymous_span(self.doc, self.model_element, xml_elem.text))
        self.implicit_end = None

      for child_xml_element in xml_elem:

        if issubclass(self.ttml_class, RegionElement) and StyleElement.is_instance(child_xml_element):
          StyleElement.from_xml(self, child_xml_element)
          continue

        child_element = ContentElement.from_xml(self, child_xml_element)

        if child_element is not None:

          if self.time_container.is_seq():

            self.implicit_end = child_element.desired_end

          else:

            if self.implicit_end is not None and child_element.desired_end is not None:

              self.implicit_end = max(self.implicit_end, child_element.desired_end)

            else:

              self.implicit_end = None

          # skip child if it has no temporal extent

          if not issubclass(child_element.ttml_class, SetElement) or \
            child_element.desired_begin is None or \
            child_element.desired_end is None and \
            child_element.desired_begin != child_element.desired_end:

            self.children.append(child_element.model_element)

        # process tail text node

        if self.ttml_class.is_mixed and child_xml_element.tail is not None and self.time_container.is_par():
          self.children.append(
            ContentElement.make_anonymous_span(
              self.doc,
              self.model_element,
              child_xml_element.tail
              )
            )
          self.implicit_end = None

      if self.ttml_class.has_styles:

        self.process_referential_styling(xml_elem)

      try:

        self.model_element.push_children(self.children)

      except (ValueError, TypeError) as e:

        LOGGER.error(str(e))

        return

      # temporal end processing

      if self.explicit_end is not None and self.explicit_dur is not None:

        self.desired_end = min(self.desired_begin + self.explicit_dur, self.implicit_begin + self.explicit_end)
        self.desired_end = min(self.desired_begin + self.explicit_dur, self.implicit_begin + self.explicit_end)

      elif self.explicit_end is None and self.explicit_dur is not None:

        self.desired_end = self.desired_begin + self.explicit_dur

      elif self.explicit_end is not None and self.explicit_dur is None:

        self.desired_end = self.implicit_begin + self.explicit_end

      else:

        self.desired_end = self.implicit_end

      if self.ttml_class.has_timing:

        self.model_element.set_begin(self.desired_begin if self.desired_begin != 0 else None)

        self.model_element.set_end(self.desired_end)

    # pylint: enable=too-many-branches

  @staticmethod
  def from_model_style_properties(model_content_element, element):
    '''Write TTML style properties from the model into into the region_element'''

    for qname, style_property_class in StyleProperties.BY_QNAME.items():
      value = model_content_element.get_style(style_property_class.model_prop)
      if value is not None:
          style_property_class.set(element, value)

  @staticmethod
  def from_model(context, body):
    
    if body is None:
      return

    BodyElement.from_model(context, body)


  @property
  def has_timing(self):
    '''`True` if the element supports temporal attributes
    '''
    raise NotImplementedError

  @property
  def has_region(self):
    '''`True` if the element can reference a region
    '''
    raise NotImplementedError

  @property
  def has_styles(self):
    '''`True` if the element can contain style properties
    '''
    raise NotImplementedError

  @property
  def is_mixed(self):
    '''`True` if the element can contain text
    '''
    raise NotImplementedError

  @property
  def has_children(self):
    '''`True` if the element can contain children elements
    '''
    raise NotImplementedError

  @staticmethod
  def make_anonymous_span(document, model_element, span_text):
    '''Creates an anonymous span in the element `model_element` from the text contained in `span_text`
    '''
    if isinstance(model_element, model.Span):

      return model.Text(document, span_text)

    s = model.Span(document)
    
    s.push_child(model.Text(document, span_text))

    return s

  @classmethod
  def from_xml(cls, parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[ContentElement.ParsingContext]:
    content_classes = [
      BodyElement,
      DivElement,
      PElement,
      SpanElement,
      RubyElement,
      RbElement,
      RtElement,
      RpElement,
      RbcElement,
      RtcElement,
      BrElement,
      SetElement,
      RegionElement
      ]

    for ttml_elem_class in content_classes:
      if ttml_elem_class.is_instance(xml_elem):
        return ttml_elem_class.from_xml(parent_ctx, xml_elem)
    
    return None

  # pylint: disable=too-many-branches

class RegionElement(ContentElement):
  '''Process the TTML <region> element
  '''

  class ParsingContext(ContentElement.ParsingContext):
    '''Maintains state when parsing the element
    '''

  qn = f"{{{xml_ns.TTML}}}region"
  has_timing = True
  has_region = False
  has_styles = True
  is_mixed = False
  has_children = False

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == RegionElement.qn

  @classmethod
  def from_xml(cls, parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[RegionElement.ParsingContext]:
    rid = imsc_attr.XMLIDAttribute.extract(xml_elem)

    if rid is None:
      LOGGER.error("All regions must have an id")
      return None

    region_ctx = RegionElement.ParsingContext(RegionElement, parent_ctx, model.Region(rid, parent_ctx.doc))
    region_ctx.process(parent_ctx, xml_elem)
    return region_ctx

  @staticmethod
  def from_model(layout, region):

    region_element = et.SubElement(layout, "region")

    attrib = region.get_id()
    if attrib is not None:
      imsc_attr.RegionAttribute.set(region_element, attrib)

    ContentElement.from_model_style_properties(region, region_element)

class SetElement(ContentElement):
  '''Process TTML <set> element
  '''

  class ParsingContext(ContentElement.ParsingContext):
    '''Maintains state when parsing the element
    '''

  qn = f"{{{xml_ns.TTML}}}set"
  has_region = False
  has_styles = False
  has_timing = True
  is_mixed = False
  has_children = False

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == DivElement.qn

  @classmethod
  def from_xml(cls, parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[SetElement.ParsingContext]:
    set_ctx = SetElement.ParsingContext(SetElement, parent_ctx)
    set_ctx.process(parent_ctx, xml_elem)
    return set_ctx

  @staticmethod
  def from_model(layout, set):

    set_element = et.SubElement(layout, "set")

#    attrib = region.get_id()
#    if attrib is not None:
#      imsc_attr.RegionAttribute.set(region_element, attrib)

class BodyElement(ContentElement):
  '''Process TTML body element
  '''

  class ParsingContext(ContentElement.ParsingContext):
    '''Maintains state when parsing the element
    '''

  qn = f"{{{xml_ns.TTML}}}body"
  has_region = True
  has_styles = True
  has_timing = True
  is_mixed = False
  has_children = True

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == BodyElement.qn

  @classmethod
  def from_xml(cls, parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[BodyElement.ParsingContext]:
    body_ctx = BodyElement.ParsingContext(BodyElement, parent_ctx, model.Body(parent_ctx.doc))
    body_ctx.process(parent_ctx, xml_elem)
    return body_ctx

  @staticmethod
  def from_model(context, body):
    
    if body is None:
      return
    
    body_element = context.imsc_doc.find("body")
    if body_element is None:
      body_element = et.SubElement(context.imsc_doc, "body")
    
    attrib = body.get_id()
    if attrib is not None:
      body_element.set(imsc_attr.XMLIDAttribute.qn, attrib)

    attrib = body.get_style(StyleProperties.LineHeight)
    if attrib is not None:
      body_element.set("tts:lineHeight", attrib)

    ContentElement.from_model_style_properties(body, body_element)

    for div in body:
      DivElement.from_model(div, body_element)


class DivElement(ContentElement):
  '''Process TTML <div> element
  '''

  class ParsingContext(ContentElement.ParsingContext):
    '''Maintains state when parsing the element
    '''

  qn = f"{{{xml_ns.TTML}}}div"
  has_region = True
  has_styles = True
  has_timing = True
  is_mixed = False
  has_children = True

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == DivElement.qn

  @classmethod
  def from_xml(cls, parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[DivElement.ParsingContext]:
    div_ctx = DivElement.ParsingContext(DivElement, parent_ctx, model.Div(parent_ctx.doc))
    div_ctx.process(parent_ctx, xml_elem)
    return div_ctx

  @staticmethod
  def from_model(parent_div, parent_element):
    
    if parent_div is None:
      return

    div_element = et.SubElement(parent_element, "div")

    ContentElement.from_model_style_properties(parent_div, div_element)

    if parent_div.has_children():
      for child in parent_div:
        if isinstance(child, model.P):
          PElement.from_model(child, div_element)
        elif isinstance(child, model.Div):
          DivElement.from_model(child, div_element)
        else:
          LOGGER.error("Children of div must be p or div")
    else:
      pass


class PElement(ContentElement):
  '''Process TTML <p> element
  '''

  class ParsingContext(ContentElement.ParsingContext):
    '''Maintains state when parsing the element
    '''

  qn = f"{{{xml_ns.TTML}}}p"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = True
  has_children = True

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == PElement.qn

  @classmethod
  def from_xml(cls, parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[PElement.ParsingContext]:
    p_ctx = PElement.ParsingContext(PElement, parent_ctx, model.P(parent_ctx.doc))
    p_ctx.process(parent_ctx, xml_elem)
    return p_ctx

  @staticmethod
  def from_model(parent_p, parent_element):
    
    if parent_p is None:
      return

    p_element = et.SubElement(parent_element, "p")

    ContentElement.from_model_style_properties(parent_p, parent_element)

    if parent_p.get_region():
      imsc_attr.RegionAttribute.set(parent_element, parent_p.get_region().get_id())

    if parent_p.get_begin():
      imsc_attr.BeginAttribute.set(parent_element, parent_p.get_begin())

    # TODO - do we need to set a dur? If so, do we compute it here with end - begin?
    #if parent_p.get_dur():
    #  imsc_attr.DurAttribute.set(parent_element, parent_p.get_dur())

    if parent_p.get_end():
      imsc_attr.EndAttribute.set(parent_element, parent_p.get_end())

    if parent_p.has_children():
      for child in parent_p:
        if isinstance(child, model.Span):
          SpanElement.from_model(child, p_element)
        elif isinstance(child, model.Ruby):
          RubyElement.from_model(child, p_element)
        elif isinstance(child, model.Br):
          BrElement.from_model(child, p_element)
        else:
          LOGGER.error("Children of p must be span or br or text")


class SpanElement(ContentElement):
  '''Process the TTML <span> element
  '''

  class ParsingContext(ContentElement.ParsingContext):
    '''Maintains state when parsing the element
    '''

  qn = f"{{{xml_ns.TTML}}}span"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = True
  has_children = True

  @staticmethod
  def is_instance(xml_elem):
    return xml_elem.tag == SpanElement.qn and SpanElement.get_ruby_attr(xml_elem) is None

  @staticmethod
  def get_ruby_attr(ttml_span):
    '''extracts the value of the TTML `tts:ruby` attribute from the XML element `ttml_span`
    '''
    return ttml_span.get(f"{{{xml_ns.TTS}}}ruby")

  @classmethod
  def from_xml(cls, parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[SpanElement.ParsingContext]:
    span_ctx = SpanElement.ParsingContext(SpanElement, parent_ctx, model.Span(parent_ctx.doc))
    span_ctx.process(parent_ctx, xml_elem)
    return span_ctx

  @staticmethod
  def from_model(model_value, xml_element):
    
    if model_value is None:
      return

    span_element = et.SubElement(xml_element, "span")

    ContentElement.from_model_style_properties(model_value, span_element)

    if model_value.has_children():
      for child in model_value:
        if isinstance(child, model.Span):
          SpanElement.from_model(child, xml_element)
        elif isinstance(child, model.Br):
          BrElement.from_model(child, xml_element)
        elif isinstance(child, model.Text):
          # TODO - do we want to have a TextElement object?
          #TextElement.from_model(xml_element, child)          
          span_element.text = child.get_text()
        else:
          LOGGER.error("Children of div must be p or div")
    else:
      pass


class RubyElement(ContentElement):
  '''Process the TTML <span tts:ruby="container"> element
  '''

  class ParsingContext(ContentElement.ParsingContext):
    '''Maintains state when parsing the element
    '''

  ruby = "container"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = False
  has_children = True

  @staticmethod
  def is_instance(xml_elem):
    return xml_elem.tag == SpanElement.qn and SpanElement.get_ruby_attr(xml_elem) == RubyElement.ruby

  @classmethod
  def from_xml(cls, parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[RubyElement.ParsingContext]:
    ruby_ctx = RubyElement.ParsingContext(RubyElement, parent_ctx, model.Ruby(parent_ctx.doc))
    ruby_ctx.process(parent_ctx, xml_elem)
    return ruby_ctx

  @staticmethod
  def from_model(parent_div, parent_element):
    
    if parent_div is None:
      return

    #ContentElement.from_model_style_properties(parent_div, span_element)


class RbElement(ContentElement):
  '''Process the TTML <span tts:ruby="base"> element
  '''

  class ParsingContext(ContentElement.ParsingContext):
    '''Maintains state when parsing the element
    '''

  ruby = "base"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = True
  has_children = True

  @staticmethod
  def is_instance(xml_elem):
    return xml_elem.tag == SpanElement.qn and SpanElement.get_ruby_attr(xml_elem) == RbElement.ruby

  @classmethod
  def from_xml(cls, parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[RbElement.ParsingContext]:
    rb_ctx = RbElement.ParsingContext(RbElement, parent_ctx, model.Rb(parent_ctx.doc))
    rb_ctx.process(parent_ctx, xml_elem)
    return rb_ctx

  @staticmethod
  def from_model(parent_div, parent_element):
    
    if parent_div is None:
      return


class RtElement(ContentElement):
  '''Process the TTML <span tts:ruby="text"> element
  '''

  class ParsingContext(ContentElement.ParsingContext):
    '''Maintains state when parsing the element
    '''

  ruby = "text"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = True
  has_children = True

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == SpanElement.qn and SpanElement.get_ruby_attr(xml_elem) == RtElement.ruby

  @classmethod
  def from_xml(cls, parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[RtElement.ParsingContext]:
    rt_ctx = RtElement.ParsingContext(RtElement, parent_ctx, model.Rt(parent_ctx.doc))
    rt_ctx.process(parent_ctx, xml_elem)
    return rt_ctx

  @staticmethod
  def from_model(parent_div, parent_element):
    
    if parent_div is None:
      return


class RpElement(ContentElement):
  '''Process the TTML <span tts:ruby="delimiter"> element
  '''

  class ParsingContext(ContentElement.ParsingContext):
    '''Maintains state when parsing the element
    '''

  ruby = "delimiter"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = True
  has_children = True

  @staticmethod
  def is_instance(xml_elem):
    return xml_elem.tag == SpanElement.qn and SpanElement.get_ruby_attr(xml_elem) == RpElement.ruby

  @classmethod
  def from_xml(cls, parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[RpElement.ParsingContext]:
    rp_ctx = RpElement.ParsingContext(RpElement, parent_ctx, model.Rp(parent_ctx.doc))
    rp_ctx.process(parent_ctx, xml_elem)
    return rp_ctx

  @staticmethod
  def from_model(parent_div, parent_element):
    
    if parent_div is None:
      return


class RbcElement(ContentElement):
  '''Process the TTML <span tts:ruby="baseContainer"> element
  '''

  class ParsingContext(ContentElement.ParsingContext):
    '''Maintains state when parsing the element
    '''

  ruby = "baseContainer"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = False
  has_children = True

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == SpanElement.qn and SpanElement.get_ruby_attr(xml_elem) == RbcElement.ruby

  @classmethod
  def from_xml(cls, parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[RbcElement.ParsingContext]:
    rbc_ctx = RbcElement.ParsingContext(RbcElement, parent_ctx, model.Rbc(parent_ctx.doc))
    rbc_ctx.process(parent_ctx, xml_elem)
    return rbc_ctx

  @staticmethod
  def from_model(parent_div, parent_element):
    
    if parent_div is None:
      return


class RtcElement(ContentElement):
  '''Process the TTML <span tts:ruby="textContainer"> element
  '''

  class ParsingContext(ContentElement.ParsingContext):
    '''Maintains state when parsing the element
    '''

  ruby = "textContainer"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = False
  has_children = True

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == SpanElement.qn and SpanElement.get_ruby_attr(xml_elem) == RtcElement.ruby

  @classmethod
  def from_xml(cls, parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[RtcElement.ParsingContext]:
    rtc_ctx = RtcElement.ParsingContext(RtcElement, parent_ctx, model.Rtc(parent_ctx.doc))
    rtc_ctx.process(parent_ctx, xml_elem)
    return rtc_ctx

  @staticmethod
  def from_model(parent_div, parent_element):
    
    if parent_div is None:
      return

class BrElement(ContentElement):
  '''Process the TTML <br> element
  '''

  class ParsingContext(ContentElement.ParsingContext):
    '''Maintains state when parsing the element
    '''

  qn = f"{{{xml_ns.TTML}}}br"
  has_timing = False
  has_region = False
  has_styles = True
  is_mixed = False
  has_children = False

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == BrElement.qn

  @classmethod
  def from_xml(cls, parent_ctx: TTMLElement.ParsingContext, xml_elem) -> typing.Optional[BrElement.ParsingContext]:
    br_ctx = BrElement.ParsingContext(BrElement, parent_ctx, model.Br(parent_ctx.doc))
    br_ctx.process(parent_ctx, xml_elem)
    return br_ctx

  @staticmethod
  def from_model(model_value, xml_element):
    
    if model_value is None:
      return

    br_element = et.SubElement(xml_element, "br")

    ContentElement.from_model_style_properties(model_value, br_element)

    if model_value.has_children():
      LOGGER.error("Br should not have children")
    else:
      pass
