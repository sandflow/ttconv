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
import numbers
import xml.etree.ElementTree as et
import ttconv.model as model
import ttconv.style_properties as model_styles
import ttconv.imsc.namespaces as xml_ns
import ttconv.imsc.attributes as imsc_attr
from ttconv.imsc.style_properties import StyleProperties
import ttconv.imsc.style_properties as imsc_styles


LOGGER = logging.getLogger(__name__)

class TTMLElement:
  '''Static information about a TTML element
  '''

  class ParsingContext(imsc_styles.StyleParsingContext):
    '''State information when parsing a TTML element'''

    def __init__(self, ttml_class: typing.Type[TTMLElement], parent_ctx: typing.Optional[TTMLElement.ParsingContext] = None):

      self.doc = parent_ctx.doc if parent_ctx is not None else model.ContentDocument()

      self.style_elements: typing.Dict[str, StyleElement] = parent_ctx.style_elements if parent_ctx is not None else {}

      self.temporal_context = parent_ctx.temporal_context if parent_ctx is not None else imsc_attr.TemporalAttributeParsingContext()

      self.ttml_class: typing.Type[TTMLElement] = ttml_class

      self.lang: typing.Optional[str] = None

      self.space: typing.Optional[model.WhiteSpaceHandling] = None

      self.time_container: imsc_attr.TimeContainer = imsc_attr.TimeContainer.par

      self.explicit_begin: typing.Optional[Fraction] = None

      self.implicit_begin: typing.Optional[Fraction] = None

      self.desired_begin: typing.Optional[Fraction] = None

      self.explicit_end: typing.Optional[Fraction] = None

      self.implicit_end: typing.Optional[Fraction] = None

      self.desired_end: typing.Optional[Fraction] = None

      self.explicit_dur: typing.Optional[Fraction] = None

    def process_lang_attribute(self, parent_ctx: TTMLElement.ParsingContext, xml_elem):
      '''Processes the xml:lang attribute, including inheritance from the parent
      '''
      lang_attr_value = imsc_attr.XMLLangAttribute.extract(xml_elem)
      self.lang = lang_attr_value if lang_attr_value is not None else parent_ctx.lang

    def process_space_attribute(self, parent_ctx: TTMLElement.ParsingContext, xml_elem):
      '''Processes the xml:space attribute, including inheritance from the parent
      '''
      space_attr_value = imsc_attr.XMLSpaceAttribute.extract(xml_elem)
      self.space = space_attr_value if space_attr_value is not None else parent_ctx.space

  class WritingContext:
    '''State information when writing a TTML element'''

    def __init__(self, frame_rate: Fraction, time_expression_syntax: imsc_attr.TimeExpressionSyntaxEnum):
      self.temporal_context = imsc_attr.TemporalAttributeWritingContext(
        frame_rate=frame_rate,
        time_expression_syntax=time_expression_syntax
        )

  @staticmethod
  def is_instance(xml_elem) -> bool:
    '''Returns true if the XML element `xml_elem` is an instance of the class
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
  def from_xml(
    _parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element,
    progress_callback: typing.Callable[[numbers.Real], typing.NoReturn] = None
  ) -> TTElement.ParsingContext:
    '''`_parent_ctx` is ignored and can be set to `None`
    '''

    tt_ctx = TTElement.ParsingContext(TTElement)

    # process attributes

    space_attr = imsc_attr.XMLSpaceAttribute.extract(xml_elem)

    tt_ctx.space = space_attr if space_attr is not None else model.WhiteSpaceHandling.DEFAULT

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

    ittp_aspect_ratio = imsc_attr.AspectRatioAttribute.extract(xml_elem)

    ttp_dar = imsc_attr.DisplayAspectRatioAttribute.extract(xml_elem)

    if ttp_dar is not None:

      tt_ctx.doc.set_display_aspect_ratio(ttp_dar)

    elif ittp_aspect_ratio is not None:

      tt_ctx.doc.set_display_aspect_ratio(ittp_aspect_ratio)

    if ittp_aspect_ratio is not None and ttp_dar is not None:

      LOGGER.warning("Both ittp:aspectRatio and ttp:displayAspectRatio specified on tt")

    tt_ctx.temporal_context.frame_rate = imsc_attr.FrameRateAttribute.extract(xml_elem)

    tt_ctx.temporal_context.tick_rate = imsc_attr.TickRateAttribute.extract(xml_elem)

    # process head and body children elements

    has_body = False
    has_head = False

    for child_element in xml_elem:

      if BodyElement.is_instance(child_element):

        if not has_body:

          has_body = True

          body_element = ContentElement.from_xml(tt_ctx, child_element)

          tt_ctx.doc.set_body(body_element.model_element if body_element is not None else None)

          progress_callback(1)

        else:
          LOGGER.error("More than one body element present")

      elif HeadElement.is_instance(child_element):

        if not has_head:

          has_head = True

          HeadElement.from_xml(tt_ctx, child_element)

          progress_callback(0.5)

        else:
          LOGGER.error("More than one head element present")

    return tt_ctx

  @staticmethod
  def from_model(
    model_doc: model.ContentDocument,
    frame_rate: typing.Optional[Fraction],
    time_expression_syntax: imsc_attr.TimeExpressionSyntaxEnum,
    progress_callback: typing.Callable[[numbers.Real], typing.NoReturn]
  ) -> et.Element:
    '''Converts the data model to an IMSC document contained in an ElementTree Element'''

    ctx = TTMLElement.WritingContext(frame_rate, time_expression_syntax)

    tt_element = et.Element(TTElement.qn)

    imsc_attr.XMLLangAttribute.set(tt_element, model_doc.get_lang())
    
    if model_doc.get_cell_resolution() != model.CellResolutionType(rows=15, columns=32):
      imsc_attr.CellResolutionAttribute.set(tt_element, model_doc.get_cell_resolution())

    has_px = False

    all_elements = list(model_doc.iter_regions())

    if model_doc.get_body() is not None:
      all_elements.extend(model_doc.get_body().dfs_iterator())

    for element in all_elements:
      for model_style_prop in element.iter_styles():
        if StyleProperties.BY_MODEL_PROP[model_style_prop].has_px(element.get_style(model_style_prop)):
          has_px = True
          break
      for animation_step in element.iter_animation_steps():
        if StyleProperties.BY_MODEL_PROP[animation_step.style_property].has_px(animation_step.value):
          has_px = True
          break      
      if has_px:
        break

    if model_doc.get_px_resolution() is not None and has_px:
      imsc_attr.ExtentAttribute.set(tt_element, model_doc.get_px_resolution())

    if model_doc.get_active_area() is not None:
      imsc_attr.ActiveAreaAttribute.set(tt_element, model_doc.get_active_area())

    if model_doc.get_display_aspect_ratio() is not None:
      imsc_attr.DisplayAspectRatioAttribute.set(tt_element, model_doc.get_display_aspect_ratio())

    if frame_rate is not None:
      imsc_attr.FrameRateAttribute.set(tt_element, frame_rate)

    # Write the <head> section first
    head_element = HeadElement.from_model(ctx, model_doc)

    progress_callback(0.5)

    if head_element is not None:
      tt_element.append(head_element)

    model_body = model_doc.get_body()

    if model_body is not None:

      body_element = BodyElement.from_model(ctx, model_body)

      if body_element is not None:
        tt_element.append(body_element)

    progress_callback(1.0)

    return tt_element

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
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> HeadElement.ParsingContext:
    '''Converts the XML element `xml_elem` into its representation in the data model.
    `parent_ctx` contains state information passed from parent to child in the TTML hierarchy.
    '''
    
    head_ctx = HeadElement.ParsingContext(HeadElement, parent_ctx)

    # process attributes

    head_ctx.process_lang_attribute(parent_ctx, xml_elem)

    head_ctx.process_space_attribute(parent_ctx, xml_elem)

    # process layout and styling children elements

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
  def from_model(
    ctx: TTMLElement.WritingContext,
    model_doc: model.ContentDocument,
  )-> typing.Optional[et.Element]:
    '''Converts the ContentDocument `model_doc` into its TTML representation, i.e. an XML element.
    `ctx` contains state information used in the process.
    '''

    head_element = None

    styling_element = StylingElement.from_model(ctx, model_doc)

    if styling_element is not None:
      if head_element is None:
        head_element = et.Element(HeadElement.qn)
      head_element.append(styling_element)

    layout_element = LayoutElement.from_model(ctx, model_doc)

    if layout_element is not None:
      if head_element is None:
        head_element = et.Element(HeadElement.qn)
      head_element.append(layout_element)

    return head_element


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
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[LayoutElement.ParsingContext]:
    '''Converts the XML element `xml_elem` into its representation in the data model.
    `parent_ctx` contains state information passed from parent to child in the TTML hierarchy.
    '''

    layout_ctx = LayoutElement.ParsingContext(LayoutElement, parent_ctx)

    # process attributes

    layout_ctx.process_lang_attribute(parent_ctx, xml_elem)

    layout_ctx.process_space_attribute(parent_ctx, xml_elem)

    # process region elements
    
    for child_element in xml_elem:

      if RegionElement.is_instance(child_element):

        r = RegionElement.from_xml(layout_ctx, child_element)

        if r is not None:
          layout_ctx.doc.put_region(r.model_element)

      else:

        LOGGER.warning("Unexpected child of layout element")

    return layout_ctx

  @staticmethod
  def from_model(
    ctx: TTMLElement.WritingContext,
    model_doc: model.ContentDocument,
  ) -> typing.Optional[et.Element]:
    '''Returns a TTML `layout` element (an XML element) using the information in the ContentDocument `model_doc`.
    `ctx` contains state information used in the process.
    '''

    layout_element = None
    
    for r in model_doc.iter_regions():
      region_element = RegionElement.from_model(ctx, r)
      if region_element is not None:
        if layout_element is None:
          layout_element = et.Element(LayoutElement.qn)
        layout_element.append(region_element)

    return layout_element

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
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[StylingElement.ParsingContext]:
    '''Converts the XML element `xml_elem` into its representation in the data model.
    `parent_ctx` contains state information passed from parent to child in the TTML hierarchy.
    '''

    styling_ctx = StylingElement.ParsingContext(StylingElement, parent_ctx)

    # process style and initial children elements

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
      
    # merge style elements (the data model does not support referential
    # styling)

    for style_element in parent_ctx.style_elements.values():
      styling_ctx.merge_chained_styles(style_element)

    return styling_ctx

  @staticmethod
  def from_model(
    _ctx: TTMLElement.WritingContext,
    model_doc: model.ContentDocument
  ) -> typing.Optional[et.Element]:
    '''Returns a TTML `styling` element using the information in the ContentDocument `model_doc`.
    `ctx` contains state information used in the process.
    '''

    styling_element = None

    for style_prop, style_value in model_doc.iter_initial_values():

      imsc_style_prop = imsc_styles.StyleProperties.BY_MODEL_PROP.get(style_prop)

      if imsc_style_prop is None:
        LOGGER.error("Unknown property")
        continue

      initial_element = InitialElement.from_model(imsc_style_prop, style_value)
      if initial_element is not None:
        if styling_element is None:
          styling_element = et.Element(StylingElement.qn)
        styling_element.append(initial_element)

    return styling_element


class StyleElement(TTMLElement):
  '''Process the TTML <style> element
  '''

  class ParsingContext(TTMLElement.ParsingContext):
    '''Maintains state when parsing the element
    '''

    def __init__(self, parent_ctx: typing.Optional[TTMLElement.ParsingContext] = None):
      self.styles: typing.Dict[model_styles.StyleProperty, typing.Any] = dict()
      self.style_refs: typing.Optional[typing.List[str]] = None
      self.id: typing.Optional[str] = None
      super().__init__(StyleElement, parent_ctx)

  qn = f"{{{xml_ns.TTML}}}style"

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == StyleElement.qn

  @staticmethod
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[StyleElement.ParsingContext]:
    '''Converts the XML element `xml_elem` into its representation in the data model.
    `parent_ctx` contains state information passed from parent to child in the TTML hierarchy.
    '''

    style_ctx = StyleElement.ParsingContext(parent_ctx)

    # collect all specified style attributes

    for attr in xml_elem.attrib:
      prop = StyleProperties.BY_QNAME.get(attr)

      if prop is None:
        continue

      try:

        model_prop, model_value = prop.to_model(style_ctx, xml_elem)
        style_ctx.styles[model_prop] = model_value

      except ValueError:

        LOGGER.error("Error reading style property: %s", prop.__name__)

    # merge nested style attributes if the parent is a region element

    if issubclass(parent_ctx.ttml_class, RegionElement):

      for style_prop, value in style_ctx.styles.items():
        region_style = parent_ctx.model_element.get_style(style_prop)

        if region_style is None:
          parent_ctx.model_element.set_style(style_prop, value)

      return None

    # process other attributes

    style_ctx.style_refs = imsc_attr.StyleAttribute.extract(xml_elem)

    style_ctx.id = imsc_attr.XMLIDAttribute.extract(xml_elem)

    if style_ctx.id is None:
      LOGGER.error("A style element must have an id")
      return None

    return style_ctx


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
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[InitialElement.ParsingContext]:
    '''Converts the XML element `xml_elem` into its representation in the data model.
    `parent_ctx` contains state information passed from parent to child in the TTML hierarchy.
    '''

    initial_ctx = InitialElement.ParsingContext(InitialElement, parent_ctx)

    # collect the specified style attributes

    for attr in xml_elem.attrib:

      prop = StyleProperties.BY_QNAME.get(attr)

      if prop is None:

        continue

      try:

        # set the initial value on the data model ContentDocument (the data model does have 
        # a distinct <initial> element)

        model_prop, model_value = prop.to_model(initial_ctx, xml_elem)

        initial_ctx.doc.put_initial_value(model_prop, model_value)

      except (ValueError, TypeError):

        LOGGER.error("Error reading style property: %s", prop.__name__)

    return initial_ctx


  @staticmethod
  def from_model(style_prop: imsc_styles.StyleProperty, initial_value: typing.Any):
    '''Returns a TTML `initial` element corresponding to the style property `style_prop` with
    initial value `initial_value`.
    '''

    initial_element = et.Element(InitialElement.qn)
    
    style_prop.from_model(initial_element, initial_value)

    return initial_element


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
        ttml_class: typing.Optional[typing.Type[ContentElement]],
        parent_ctx: TTMLElement.ParsingContext,
        model_element: typing.Optional[model.ContentElement] = None
      ):
      self.children: typing.List[model.ContentElement] = []
      self.model_element: model.ContentElement = model_element
      super().__init__(ttml_class, parent_ctx)

    def process_region_property(self, xml_elem):
      '''Reads and processes the `region` attribute
      '''
      rid = imsc_attr.RegionAttribute.extract(xml_elem)

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
      for style_ref in reversed(imsc_attr.StyleAttribute.extract(xml_elem)):
        style_element = self.style_elements.get(style_ref)

        if style_element is None:
          LOGGER.error("non existant style id")
          continue

        for model_prop, value in style_element.styles.items():
          if not self.model_element.has_style(model_prop):
            self.model_element.set_style(model_prop, value)

    def process_specified_styling(self, xml_elem):
      '''Processes specified styling
      '''
      for attr in xml_elem.attrib:
        prop = StyleProperties.BY_QNAME.get(attr)

        if prop is None:
          continue

        try:
          model_prop, model_value = prop.to_model(self, xml_elem)

          self.model_element.set_style(model_prop, model_value)

        except ValueError:

          LOGGER.error("Error reading style property: %s", prop.__name__)

    def process_set_style_properties(self, parent_ctx: ContentElement.ParsingContext, xml_elem):
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
            model_prop, model_value = prop.to_model(self, xml_elem)
            parent_ctx.model_element.add_animation_step(
              model.DiscreteAnimationStep(
                model_prop,
                self.desired_begin,
                self.desired_end,
                model_value
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

    def process(self, parent_ctx: TTMLElement.ParsingContext, xml_elem: et.Element):
      '''Generic processing applicable to TTML elements rooted in `region` and `body` elements
      '''
      self.process_lang_attribute(parent_ctx, xml_elem)

      self.process_space_attribute(parent_ctx, xml_elem)

      if self.ttml_class.has_region:
        self.process_region_property(xml_elem)

      # temporal processing. Sequential time containers are converted to parallel time containers since the data model does not
      # support the former.

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
        # br, region and set elements have indefinite duration in parallel time containers

        self.implicit_end = None
      else:
        self.implicit_end = self.desired_begin
        
      # process text nodes

      if self.ttml_class.is_mixed and xml_elem.text is not None and self.time_container.is_par():
        self.children.append(ContentElement.make_anonymous_span(self.doc, self.model_element, xml_elem.text))
        self.implicit_end = None

      # process children elements

      is_inline_animation_complete = False

      for child_xml_element in xml_elem:

        if issubclass(self.ttml_class, RegionElement) and StyleElement.is_instance(child_xml_element):
          # process nest styling, which is specific to region elements, and does not affect temporal
          # processing
          StyleElement.from_xml(self, child_xml_element)
          continue

        child_element = ContentElement.from_xml(self, child_xml_element)

        if child_element is not None:

          if issubclass(child_element.ttml_class, SetElement):
            if is_inline_animation_complete:
              LOGGER.warning("<set> element is out of order")
          elif is_inline_animation_complete is False:
            is_inline_animation_complete = True

          if self.time_container.is_seq():

            self.implicit_end = None if child_element.desired_end is None else child_element.desired_end + self.desired_begin

          else:

            if self.implicit_end is not None and child_element.desired_end is not None:

              self.implicit_end = max(self.implicit_end, child_element.desired_end)

            else:

              self.implicit_end = None

          # skip child if it has no temporal extent

          if not issubclass(child_element.ttml_class, SetElement) and \
            (child_element.desired_begin is None or child_element.desired_end is None or \
              child_element.desired_begin != child_element.desired_end):

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

      # process referential styling last since it has the lowest priority compared to specified and nested styling

      if self.ttml_class.has_styles:

        self.process_referential_styling(xml_elem)

      try:
        
        if self.ttml_class.has_children:
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

        # temporal processing applies to all contents elements but explicit begin and end properties are stored only if their values
        # are not constant, e.g. br elements always have indefinit begin and end times in parallel time containers

        self.model_element.set_begin(self.desired_begin if self.desired_begin != 0 else None)

        self.model_element.set_end(self.desired_end)

      # process style properties

      if issubclass(self.ttml_class, SetElement):

        self.process_set_style_properties(parent_ctx, xml_elem)

      elif self.ttml_class.has_styles:

        self.process_specified_styling(xml_elem)

    # pylint: enable=too-many-branches

  @classmethod
  def make_ttml_element(cls):
    '''Creates an XML element for the content element
    '''
    raise NotImplementedError

  @staticmethod
  def from_model_style_properties(model_content_element, element):
    '''Write TTML style properties from the model'''

    for model_prop, imsc_prop in StyleProperties.BY_MODEL_PROP.items():
      value = model_content_element.get_style(model_prop)
      if value is not None:
        imsc_prop.from_model(element, value)

  @staticmethod
  def from_model_animation(ctx: TTMLElement.WritingContext, model_element: model.ContentElement, xml_element):
    '''Write TTML set element from the model'''

    for a_step in model_element.iter_animation_steps():
      set_element = SetElement.from_model(ctx, a_step)
      if set_element is not None:
        xml_element.append(set_element)


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
    s.set_space(model_element.get_space())
    s.set_lang(model_element.get_lang())

    s.push_child(model.Text(document, span_text))

    return s

  @staticmethod
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[ContentElement.ParsingContext]:
    '''Converts the XML element `xml_elem` into its representation in the data model.
    `parent_ctx` contains state information passed from parent to child in the TTML hierarchy.
    '''

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

  @staticmethod
  def from_model(
    ctx: TTMLElement.WritingContext,
    model_element: model.ContentElement
  ) -> typing.Optional[et.Element]:
    '''Returns the TTML element corresponding to the model element `model_element`.
    `ctx` contains state information used in the process.
    '''

    if isinstance(model_element, model.Body):
      imsc_class = BodyElement
    elif isinstance(model_element, model.Div):
      imsc_class = DivElement
    elif isinstance(model_element, model.P):
      imsc_class = PElement
    elif isinstance(model_element, model.Span):
      imsc_class = SpanElement
    elif isinstance(model_element, model.Br):
      imsc_class = BrElement
    elif isinstance(model_element, model.Ruby):
      imsc_class = RubyElement
    elif isinstance(model_element, model.Rb):
      imsc_class = RbElement
    elif isinstance(model_element, model.Rt):
      imsc_class = RtElement
    elif isinstance(model_element, model.Rbc):
      imsc_class = RbcElement
    elif isinstance(model_element, model.Rtc):
      imsc_class = RtcElement
    elif isinstance(model_element, model.Region):
      imsc_class = RegionElement
    else:
      return None

    xml_element = imsc_class.make_ttml_element()

    if (model_element.parent() is None and model_element.get_space() is model.WhiteSpaceHandling.PRESERVE) or \
      (model_element.parent() is not None and model_element.parent().get_space() != model_element.get_space()):
      imsc_attr.XMLSpaceAttribute.set(xml_element, model_element.get_space())

    if imsc_class.has_region:
      if model_element.get_region() is not None:
        imsc_attr.RegionAttribute.set(xml_element, model_element.get_region().get_id())

    if imsc_class.has_timing:
      if model_element.get_begin() is not None:
        imsc_attr.BeginAttribute.set(ctx.temporal_context, xml_element, model_element.get_begin())

      if model_element.get_end() is not None:
        imsc_attr.EndAttribute.set(ctx.temporal_context, xml_element, model_element.get_end())

    if model_element.get_id() is not None:
      imsc_attr.XMLIDAttribute.set(xml_element, model_element.get_id())

    if imsc_class.has_styles:
      ContentElement.from_model_style_properties(model_element, xml_element)
      ContentElement.from_model_animation(ctx, model_element, xml_element)

    if imsc_class.has_children:
      last_child_element = None

      for child in iter(model_element):
        if isinstance(child, model.Text):
          if last_child_element is None:
            xml_element.text = child.get_text()
          else:
            last_child_element.tail = child.get_text()

        child_element = ContentElement.from_model(ctx, child)
        if child_element is not None:
          xml_element.append(child_element)
        
        last_child_element = child_element

    return xml_element

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

  @staticmethod
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[RegionElement.ParsingContext]:
    rid = imsc_attr.XMLIDAttribute.extract(xml_elem)

    if rid is None:
      LOGGER.error("All regions must have an id")
      return None

    region_ctx = RegionElement.ParsingContext(RegionElement, parent_ctx, model.Region(rid, parent_ctx.doc))
    region_ctx.process(parent_ctx, xml_elem)
    return region_ctx

  @staticmethod
  def from_model(
    ctx: TTMLElement.WritingContext,
    model_element: model.Region
  ) -> typing.Optional[et.Element]:
    return ContentElement.from_model(ctx, model_element)

  @classmethod
  def make_ttml_element(cls):
    return et.Element(cls.qn)

class SetElement(ContentElement):
  '''Process TTML <set> element
  '''

  class ParsingContext(ContentElement.ParsingContext):
    '''Maintains state when parsing the element
    '''
    def process_lang_attribute(self, parent_ctx: TTMLElement.ParsingContext, xml_elem):
      # <set> ignores xml:lang
      pass

    def process_space_attribute(self, parent_ctx: TTMLElement.ParsingContext, xml_elem):
      # <set> ignores xml:space
      pass

  qn = f"{{{xml_ns.TTML}}}set"
  has_region = False
  has_styles = False
  has_timing = False
  is_mixed = False
  has_children = False

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == SetElement.qn

  @staticmethod
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[SetElement.ParsingContext]:
    set_ctx = SetElement.ParsingContext(SetElement, parent_ctx)
    set_ctx.process(parent_ctx, xml_elem)

    return set_ctx

  @staticmethod
  def from_model(
    ctx: TTMLElement.WritingContext,
    model_element: model.DiscreteAnimationStep
  ) -> typing.Optional[et.Element]:

    set_element = et.Element(SetElement.qn)

    imsc_style = imsc_styles.StyleProperties.BY_MODEL_PROP[model_element.style_property]

    imsc_style.from_model(
      set_element,
      model_element.value
    )

    if model_element.begin is not None:
      imsc_attr.BeginAttribute.set(ctx.temporal_context, set_element, model_element.begin)

    if model_element.end is not None:
      imsc_attr.EndAttribute.set(ctx.temporal_context, set_element, model_element.end)

    return set_element

  @classmethod
  def make_ttml_element(cls):
    return et.Element(cls.qn)


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

  @staticmethod
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[BodyElement.ParsingContext]:
    body_ctx = BodyElement.ParsingContext(BodyElement, parent_ctx, model.Body(parent_ctx.doc))
    body_ctx.process(parent_ctx, xml_elem)
    return body_ctx

  @staticmethod
  def from_model(ctx: TTMLElement.WritingContext, model_element: model.ContentElement):
    return ContentElement.from_model(ctx, model_element)

  @classmethod
  def make_ttml_element(cls):
    return et.Element(cls.qn)

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

  @staticmethod
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[DivElement.ParsingContext]:
    div_ctx = DivElement.ParsingContext(DivElement, parent_ctx, model.Div(parent_ctx.doc))
    div_ctx.process(parent_ctx, xml_elem)
    return div_ctx

  @staticmethod
  def from_model(ctx: TTMLElement.WritingContext, model_element: model.ContentElement):
    return ContentElement.from_model(ctx, model_element)

  @classmethod
  def make_ttml_element(cls):
    return et.Element(cls.qn)

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

  @staticmethod
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[PElement.ParsingContext]:
    p_ctx = PElement.ParsingContext(PElement, parent_ctx, model.P(parent_ctx.doc))
    p_ctx.process(parent_ctx, xml_elem)
    return p_ctx

  @staticmethod
  def from_model(ctx: TTMLElement.WritingContext, model_element: model.ContentElement):
    return ContentElement.from_model(ctx, model_element)

  @classmethod
  def make_ttml_element(cls):
    return et.Element(cls.qn)

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

  ruby_attribute_qn = f"{{{xml_ns.TTS}}}ruby"

  @staticmethod
  def is_instance(xml_elem):
    return xml_elem.tag == SpanElement.qn and SpanElement.get_ruby_attr(xml_elem) is None

  @staticmethod
  def get_ruby_attr(ttml_span):
    '''extracts the value of the TTML `tts:ruby` attribute from the XML element `ttml_span`
    '''
    return ttml_span.get(SpanElement.ruby_attribute_qn)

  @staticmethod
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[SpanElement.ParsingContext]:
    span_ctx = SpanElement.ParsingContext(SpanElement, parent_ctx, model.Span(parent_ctx.doc))
    span_ctx.process(parent_ctx, xml_elem)
    return span_ctx

  @staticmethod
  def from_model(ctx: TTMLElement.WritingContext, model_element: model.ContentElement):
    return ContentElement.from_model(ctx, model_element)

  @classmethod
  def make_ttml_element(cls):
    return et.Element(cls.qn)

class RubyElement(ContentElement):
  '''Process the TTML <span tts:ruby="container"> element
  '''

  class ParsingContext(ContentElement.ParsingContext):
    '''Maintains state when parsing the element
    '''

  qn = f"{{{xml_ns.TTML}}}span"
  ruby = "container"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = False
  has_children = True

  @staticmethod
  def is_instance(xml_elem):
    return xml_elem.tag == SpanElement.qn and SpanElement.get_ruby_attr(xml_elem) == RubyElement.ruby

  @staticmethod
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[RubyElement.ParsingContext]:
    ruby_ctx = RubyElement.ParsingContext(RubyElement, parent_ctx, model.Ruby(parent_ctx.doc))
    ruby_ctx.process(parent_ctx, xml_elem)
    return ruby_ctx

  @staticmethod
  def from_model(ctx: TTMLElement.WritingContext, model_element: model.ContentElement):
    return ContentElement.from_model(ctx, model_element)

  @classmethod
  def make_ttml_element(cls):
    return et.Element(cls.qn, {SpanElement.ruby_attribute_qn: cls.ruby})

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

  @staticmethod
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[RbElement.ParsingContext]:
    rb_ctx = RbElement.ParsingContext(RbElement, parent_ctx, model.Rb(parent_ctx.doc))
    rb_ctx.process(parent_ctx, xml_elem)
    return rb_ctx

  @staticmethod
  def from_model(ctx: TTMLElement.WritingContext, model_element: model.ContentElement):
    return ContentElement.from_model(ctx, model_element)

  @classmethod
  def make_ttml_element(cls):
    return et.Element(RubyElement.qn, {SpanElement.ruby_attribute_qn: cls.ruby})


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

  @staticmethod
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[RtElement.ParsingContext]:
    rt_ctx = RtElement.ParsingContext(RtElement, parent_ctx, model.Rt(parent_ctx.doc))
    rt_ctx.process(parent_ctx, xml_elem)
    return rt_ctx

  @staticmethod
  def from_model(ctx: TTMLElement.WritingContext, model_element: model.ContentElement):
    return ContentElement.from_model(ctx, model_element)

  @classmethod
  def make_ttml_element(cls):
    return et.Element(RubyElement.qn, {SpanElement.ruby_attribute_qn: cls.ruby})


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

  @staticmethod
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[RpElement.ParsingContext]:
    rp_ctx = RpElement.ParsingContext(RpElement, parent_ctx, model.Rp(parent_ctx.doc))
    rp_ctx.process(parent_ctx, xml_elem)
    return rp_ctx

  @staticmethod
  def from_model(ctx: TTMLElement.WritingContext, model_element: model.ContentElement):
    return ContentElement.from_model(ctx, model_element)

  @classmethod
  def make_ttml_element(cls):
    return et.Element(RubyElement.qn, {SpanElement.ruby_attribute_qn: cls.ruby})


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

  @staticmethod
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[RbcElement.ParsingContext]:
    rbc_ctx = RbcElement.ParsingContext(RbcElement, parent_ctx, model.Rbc(parent_ctx.doc))
    rbc_ctx.process(parent_ctx, xml_elem)
    return rbc_ctx

  @staticmethod
  def from_model(ctx: TTMLElement.WritingContext, model_element: model.ContentElement):
    return ContentElement.from_model(ctx, model_element)

  @classmethod
  def make_ttml_element(cls):
    return et.Element(RubyElement.qn, {SpanElement.ruby_attribute_qn: cls.ruby})


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

  @staticmethod
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[RtcElement.ParsingContext]:
    rtc_ctx = RtcElement.ParsingContext(RtcElement, parent_ctx, model.Rtc(parent_ctx.doc))
    rtc_ctx.process(parent_ctx, xml_elem)
    return rtc_ctx

  @staticmethod
  def from_model(ctx: TTMLElement.WritingContext, model_element: model.ContentElement):
    return ContentElement.from_model(ctx, model_element)

  @classmethod
  def make_ttml_element(cls):
    return et.Element(RubyElement.qn, {SpanElement.ruby_attribute_qn: cls.ruby})


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

  @staticmethod
  def from_xml(
    parent_ctx: typing.Optional[TTMLElement.ParsingContext],
    xml_elem: et.Element
  ) -> typing.Optional[BrElement.ParsingContext]:
    br_ctx = BrElement.ParsingContext(BrElement, parent_ctx, model.Br(parent_ctx.doc))
    br_ctx.process(parent_ctx, xml_elem)
    return br_ctx

  @staticmethod
  def from_model(
    ctx: TTMLElement.WritingContext,
    model_element: typing.Any
  ) -> typing.Optional[et.Element]:
    return ContentElement.from_model(ctx, model_element)

  @classmethod
  def make_ttml_element(cls):
    return et.Element(cls.qn)
