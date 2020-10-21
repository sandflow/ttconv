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
import ttconv.style_properties as styles
import ttconv.imsc.namespaces as xml_ns
import ttconv.imsc.attributes as imsc_attr
from ttconv.imsc.style_properties import StyleProperties
import ttconv.imsc.style_properties as styles

LOGGER = logging.getLogger(__name__)

class TTMLElement:

  def __init__(self, parent: typing.Optional[TTMLElement] = None):

    self.doc = parent.doc if parent is not None else model.Document()

    self.style_context = parent.style_context if parent else styles.StyleParsingContext()

    self.style_elements: typing.Dict[str, StyleElement] = parent.style_elements if parent else {}

    self.temporal_context = parent.temporal_context if parent else imsc_attr.TemporalAttributeParsingContext()

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

  def process_lang_attribute(self, parent: TTMLElement, xml_elem):
    self.lang = imsc_attr.XMLLangAttribute.extract(xml_elem) or parent.lang

  def process_space_attribute(self, parent: TTMLElement, xml_elem):
    self.space = imsc_attr.XMLSpaceAttribute.extract(xml_elem) or parent.space


class TTElement(TTMLElement):
  '''Processes the TTML <tt> element
  '''

  qn = f"{{{xml_ns.TTML}}}tt"

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == TTElement.qn

  @staticmethod
  def from_xml(xml_elem) -> TTElement:

    element = TTElement()

    element.space = imsc_attr.XMLSpaceAttribute.extract(xml_elem) or model.WhiteSpaceHandling.DEFAULT

    lang_attr = imsc_attr.XMLLangAttribute.extract(xml_elem)

    if lang_attr is None:
      LOGGER.warning("xml:lang not specified on tt")
      lang_attr = ""

    element.lang = lang_attr

    element.doc.set_lang(element.lang)

    element.doc.set_cell_resolution(
      imsc_attr.CellResolutionAttribute.extract(xml_elem)
    )

    px_resolution = imsc_attr.ExtentAttribute.extract(xml_elem)

    if px_resolution is not None:
      element.doc.set_px_resolution(px_resolution)

    active_area = imsc_attr.ActiveAreaAttribute.extract(xml_elem)

    if active_area is not None:
      element.doc.set_active_area(active_area)

    element.temporal_context.frame_rate = imsc_attr.FrameRateAttribute.extract(xml_elem)

    element.temporal_context.tick_rate = imsc_attr.TickRateAttribute.extract(xml_elem)

    # process children elements elements

    has_body = False
    has_head = False

    for child_element in xml_elem:

      if BodyElement.is_instance(child_element):

        if not has_body:

          has_body = True

          body_element = ContentElement.from_xml(element, child_element)

          element.doc.set_body(body_element.model_element if body_element is not None else None)

        else:
          LOGGER.error("More than one body element present")

      elif HeadElement.is_instance(child_element):

        if not has_head:

          has_head = True

          HeadElement.from_xml(element, child_element)

        else:
          LOGGER.error("More than one head element present")

    return element

class HeadElement(TTMLElement):
  '''Processes the TTML <head> element
  '''

  qn = f"{{{xml_ns.TTML}}}head"

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == HeadElement.qn

  @staticmethod
  def from_xml(parent: TTMLElement, xml_element) -> HeadElement:
    
    element = HeadElement(parent)

    element.process_lang_attribute(parent, xml_element)

    element.process_space_attribute(parent, xml_element)

    # process children elements

    has_layout = False
    has_styling = False
    
    for child_element in xml_element:

      if LayoutElement.is_instance(child_element):

        if not has_layout:

          has_layout = True

          LayoutElement.from_xml(
            element,
            child_element
          )

        else:

          LOGGER.error("Multiple layout elements")

      elif StylingElement.is_instance(child_element):

        if not has_styling:

          has_styling = True

          StylingElement.from_xml(
            element,
            child_element
          )

        else:

          LOGGER.error("Multiple styling elements")

    return element



class LayoutElement(TTMLElement):
  '''Process the TTML <layout> element
  '''

  qn = f"{{{xml_ns.TTML}}}layout"

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == LayoutElement.qn

  @staticmethod
  def from_xml(parent: TTMLElement, xml_elem):

    element = LayoutElement(parent)

    element.process_lang_attribute(parent, xml_elem)

    element.process_space_attribute(parent, xml_elem)
    
    for child_element in xml_elem:

      if RegionElement.is_instance(child_element):

        r = RegionElement.from_xml(element, child_element)

        if r is not None:
          element.doc.put_region(r.model_element)

      else:

        LOGGER.warning("Unexpected child of layout element")

    return element

class StylingElement(TTMLElement):
  '''Process the TTML <styling> element
  '''

  qn = f"{{{xml_ns.TTML}}}styling"

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == StylingElement.qn

  def merge_chained_styles(self, style_element: StyleElement):

    while len(style_element.style_refs) > 0:

      style_ref = style_element.style_refs.pop()

      if style_ref not in self.style_elements:
        LOGGER.error("Style id not present")
        continue

      self.merge_chained_styles(self.style_elements[style_ref])

      for style_prop, value in self.style_elements[style_ref].styles.items():
        style_element.styles.setdefault(style_prop, value)


  @staticmethod
  def from_xml(parent: TTMLElement, xml_elem):
    styling_elem = StylingElement(parent)

    for child_xml_elem in xml_elem:

      if InitialElement.is_instance(child_xml_elem):

        InitialElement.from_xml(styling_elem, child_xml_elem)

      elif StyleElement.is_instance(child_xml_elem):
        
        style_element = StyleElement.from_xml(styling_elem, child_xml_elem)

        if style_element is None:
          continue

        if style_element.id in styling_elem.style_elements:
          LOGGER.error("Duplicate style id")
          continue

        style_element.style_elements[style_element.id] = style_element
      
    # merge style elements

    for style_element in parent.style_elements.values():
      styling_elem.merge_chained_styles(style_element)


class StyleElement(TTMLElement):
  '''Process the TTML <style> element
  '''

  qn = f"{{{xml_ns.TTML}}}style"

  def __init__(self, parent: typing.Optional[TTMLElement] = None):
    self.styles: typing.Dict[styles.StyleProperty, typing.Any] = dict()
    self.style_refs: typing.List[str] = None
    self.id: str = None
    super().__init__(parent)

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == StyleElement.qn

  @staticmethod
  def from_xml(parent: TTMLElement, xml_elem):
    
    element = StyleElement(parent)

    for attr in xml_elem.attrib:
      prop = StyleProperties.BY_QNAME.get(attr)

      if not prop:
        continue

      try:

        element.styles[prop.model_prop] = prop.extract(element.style_context, xml_elem.attrib.get(attr))

      except ValueError:

        LOGGER.error("Error reading style property: %s", prop.__name__)

    if isinstance(parent, RegionElement):

      # nested styling
      # merge style properties with the parent Region element

      for style_prop, value in element.styles.items():
        region_style = parent.model_element.get_style(style_prop)

        if region_style is None:
          parent.model_element.set_style(style_prop, value)

      return None

    # styling > style element

    element.style_refs = imsc_attr.StyleAttribute.extract(xml_elem)

    element.id = imsc_attr.XMLIDAttribute.extract(xml_elem)

    if element.id is None:
      LOGGER.error("A style element must have an id")
      return None

    return element

class InitialElement(TTMLElement):
  '''Process the TTML <initial> element
  '''

  qn = f"{{{xml_ns.TTML}}}initial"

  @staticmethod
  def is_instance(xml_elem) -> bool:
    return xml_elem.tag == InitialElement.qn

  @staticmethod
  def from_xml(parent: TTMLElement, xml_elem):
    
    element = InitialElement(parent)

    for attr in xml_elem.attrib:

      prop = StyleProperties.BY_QNAME.get(attr)

      if not prop:

        continue

      try:

        element.doc.put_initial_value(
          prop.model_prop,
          prop.extract(element.style_context, xml_elem.attrib.get(attr))
        )

      except (ValueError, TypeError):

        LOGGER.error("Error reading style property: %s", prop.__name__)

    return element


#
# process content elements
#

class ContentElement(TTMLElement):
  '''TTML content elements: body, div, p, span, br
  '''

  def __init__(self, parent: typing.Optional[TTMLElement] = None, model_element: typing.Optional[model.ContentElement] = None):
    self.children: typing.List[model.ContentElement] = []
    self.model_element: model.ContentElement = model_element
    super().__init__(parent)

  @property
  def has_timing(self):
    raise NotImplementedError

  @property
  def has_region(self):
    raise NotImplementedError

  @property
  def has_styles(self):
    raise NotImplementedError

  @property
  def is_mixed(self):
    raise NotImplementedError

  @property
  def has_children(self):
    raise NotImplementedError

  def process_region_property(self, xml_elem):
    rid = xml_elem.attrib.get('region')

    if rid is None:
      return

    r = self.doc.get_region(rid)
    
    if r is not None:
      self.model_element.set_region(r)
    else:
      LOGGER.warning("Element references unknown region")

  def process_referential_styling(self, xml_elem):

    for style_ref in imsc_attr.StyleAttribute.extract(xml_elem):
      style_element = self.style_elements.get(style_ref)

      if style_element is None:
        LOGGER.error("non existant style id")
        continue

      for model_prop, value in style_element.styles.items():
        if self.model_element.get_style(model_prop) is None:
          self.model_element.set_style(model_prop, value)

  def process_specified_styling(self, xml_elem):

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

  def process_set_style_properties(self, parent: TTMLElement, xml_elem):
    if parent.model_element is None:
      LOGGER.error("Set parent does not exist")
      return

    if not isinstance(parent, ContentElement):
      LOGGER.error("Set parent is not a content element")
      return

    for attr in xml_elem.attrib:
      prop = StyleProperties.BY_QNAME.get(attr)
      if prop is not None:
        try:
          parent.model_element.add_animation_step(
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

  def process_lang_attribute(self, parent: TTMLElement, xml_elem):
    super().process_lang_attribute(parent, xml_elem)
    self.model_element.set_lang(self.lang)

  def process_space_attribute(self, parent: TTMLElement, xml_elem):
    super().process_space_attribute(parent, xml_elem)
    self.model_element.set_space(self.space)

  @staticmethod
  def make_anonymous_span(document, parent_model_element, span_text):
    if isinstance(parent_model_element, model.Span):

      return model.Text(document, span_text)

    s = model.Span(document)
    
    s.push_child(model.Text(document, span_text))

    return s

  @classmethod
  def from_xml(cls, parent: TTMLElement, xml_elem):
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
        return ttml_elem_class.from_xml(parent, xml_elem)
    
    return None

  def process(self, parent: TTMLElement, xml_elem):

    self.process_lang_attribute(parent, xml_elem)

    self.process_space_attribute(parent, xml_elem)

    if self.has_region:
      self.process_region_property(xml_elem)

    if isinstance(self, SetElement):

      self.process_set_style_properties(parent, xml_elem)

    elif self.has_styles:

      self.process_specified_styling(xml_elem)

    # temporal processing

    self.time_container = imsc_attr.TimeContainerAttribute.extract(xml_elem)

    self.explicit_begin = imsc_attr.BeginAttribute.extract(self.temporal_context, xml_elem)

    self.explicit_dur = imsc_attr.DurAttribute.extract(self.temporal_context, xml_elem)

    self.explicit_end = imsc_attr.EndAttribute.extract(self.temporal_context, xml_elem)

    self.implicit_begin = Fraction(0) if parent.time_container.is_par() else (parent.implicit_end - parent.desired_begin)
    
    self.desired_begin = self.implicit_begin + (self.explicit_begin if self.explicit_begin is not None else Fraction(0))

    if isinstance(self, (BrElement, RegionElement, SetElement)) and parent.time_container.is_par():
      self.implicit_end = None
    else:
      self.implicit_end = self.desired_begin
      
    # process children elements

    if self.is_mixed and xml_elem.text is not None and self.time_container.is_par():
      self.children.append(ContentElement.make_anonymous_span(self.doc, self.model_element, xml_elem.text))
      self.implicit_end = None

    for child_xml_element in xml_elem:

      if isinstance(self, RegionElement) and StyleElement.is_instance(child_xml_element):
        style_element = StyleElement(self)
        style_element.from_xml(self, child_xml_element)
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

        if not isinstance(child_element, SetElement) or \
          child_element.desired_begin is None or \
          child_element.desired_end is None and \
          child_element.desired_begin != child_element.desired_end:

          self.children.append(child_element.model_element)

      # process tail text node

      if self.is_mixed and child_xml_element.tail is not None and self.time_container.is_par():
        self.children.append(
          ContentElement.make_anonymous_span(
            self.doc,
            self.model_element,
            child_xml_element.tail
            )
          )
        self.implicit_end = None

    if self.has_styles:

      self.process_referential_styling(xml_elem)

    try:

      self.model_element.push_children(self.children)

    except (ValueError, TypeError) as e:

      LOGGER.error(str(e))

      return None

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

    if self.has_timing:

      self.model_element.set_begin(self.desired_begin if self.desired_begin != 0 else None)

      self.model_element.set_end(self.desired_end)

class RegionElement(ContentElement):
  '''Process the TTML <region> element
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
  def from_xml(cls, parent: TTMLElement, xml_elem):
    rid = imsc_attr.XMLIDAttribute.extract(xml_elem)

    if rid is None:
      LOGGER.error("All regions must have an id")
      return None

    element = RegionElement(parent, model.Region(rid, parent.doc))
    element.process(parent, xml_elem)
    return element
    
class SetElement(ContentElement):
  '''Process TTML <set> element
  '''

  qn = f"{{{xml_ns.TTML}}}set"
  has_region = False
  has_styles = False
  has_timing = True
  is_mixed = False
  has_children = False

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == DivElement.qn

  @classmethod
  def from_xml(cls, parent: TTMLElement, xml_elem):
    element = SetElement(parent)
    element.process(parent, xml_elem)
    return element

class BodyElement(ContentElement):
  '''Process TTML body element
  '''

  qn = f"{{{xml_ns.TTML}}}body"
  has_region = True
  has_styles = True
  has_timing = True
  is_mixed = False
  has_children = True

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == BodyElement.qn

  @classmethod
  def from_xml(cls, parent: TTMLElement, xml_elem):
    element = BodyElement(parent, model.Body(parent.doc))
    element.process(parent, xml_elem)
    return element


class DivElement(ContentElement):
  '''Process TTML <div> element
  '''

  qn = f"{{{xml_ns.TTML}}}div"
  has_region = True
  has_styles = True
  has_timing = True
  is_mixed = False
  has_children = True

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == DivElement.qn

  @classmethod
  def from_xml(cls, parent: TTMLElement, xml_elem):
    element = DivElement(parent, model.Div(parent.doc))
    element.process(parent, xml_elem)
    return element

class PElement(ContentElement):
  '''Process TTML <p> element
  '''

  qn = f"{{{xml_ns.TTML}}}p"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = True
  has_children = True

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == PElement.qn

  @classmethod
  def from_xml(cls, parent: TTMLElement, xml_elem):
    element = PElement(parent, model.P(parent.doc))
    element.process(parent, xml_elem)
    return element


class SpanElement(ContentElement):
  '''Process the TTML <span> element
  '''
  qn = f"{{{xml_ns.TTML}}}span"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = True
  has_children = True

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == SpanElement.qn and SpanElement.get_ruby_attr(ttml_element) is None

  @staticmethod
  def get_ruby_attr(ttml_span):
    return ttml_span.get(f"{{{xml_ns.TTS}}}ruby")

  @classmethod
  def from_xml(cls, parent: TTMLElement, xml_elem):
    element = SpanElement(parent, model.Span(parent.doc))
    element.process(parent, xml_elem)
    return element


class RubyElement(ContentElement):
  '''Process the TTML <span tts:ruby="container"> element
  '''
  ruby = "container"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = False
  has_children = True

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == SpanElement.qn and SpanElement.get_ruby_attr(ttml_element) == RubyElement.ruby

  @classmethod
  def from_xml(cls, parent: TTMLElement, xml_elem):
    element = RubyElement(parent, model.Ruby(parent.doc))
    element.process(parent, xml_elem)
    return element


class RbElement(ContentElement):
  '''Process the TTML <span tts:ruby="base"> element
  '''
  ruby = "base"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = True
  has_children = True

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == SpanElement.qn and SpanElement.get_ruby_attr(ttml_element) == RbElement.ruby

  @classmethod
  def from_xml(cls, parent: TTMLElement, xml_elem):
    element = RbElement(parent, model.Rb(parent.doc))
    element.process(parent, xml_elem)
    return element

class RtElement(ContentElement):
  '''Process the TTML <span tts:ruby="text"> element
  '''
  ruby = "text"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = True
  has_children = True

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == SpanElement.qn and SpanElement.get_ruby_attr(ttml_element) == RtElement.ruby

  @classmethod
  def from_xml(cls, parent: TTMLElement, xml_elem):
    element = RtElement(parent, model.Rt(parent.doc))
    element.process(parent, xml_elem)
    return element


class RpElement(ContentElement):
  '''Process the TTML <span tts:ruby="delimiter"> element
  '''

  ruby = "delimiter"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = True
  has_children = True

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == SpanElement.qn and SpanElement.get_ruby_attr(ttml_element) == RpElement.ruby

  @classmethod
  def from_xml(cls, parent: TTMLElement, xml_elem):
    element = RpElement(parent, model.Rp(parent.doc))
    element.process(parent, xml_elem)
    return element


class RbcElement(ContentElement):
  '''Process the TTML <span tts:ruby="baseContainer"> element
  '''

  ruby = "baseContainer"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = False
  has_children = True

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == SpanElement.qn and SpanElement.get_ruby_attr(ttml_element) == RbcElement.ruby

  @classmethod
  def from_xml(cls, parent: TTMLElement, xml_elem):
    element = RbcElement(parent, model.Rbc(parent.doc))
    element.process(parent, xml_elem)
    return element


class RtcElement(ContentElement):
  '''Process the TTML <span tts:ruby="textContainer"> element
  '''

  ruby = "textContainer"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = False
  has_children = True

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == SpanElement.qn and SpanElement.get_ruby_attr(ttml_element) == RtcElement.ruby

  @classmethod
  def from_xml(cls, parent: TTMLElement, xml_elem):
    element = RtcElement(parent, model.Rtc(parent.doc))
    element.process(parent, xml_elem)
    return element

class BrElement(ContentElement):
  '''Process the TTML <br> element
  '''

  qn = f"{{{xml_ns.TTML}}}br"
  has_timing = False
  has_region = False
  has_styles = True
  is_mixed = False
  has_children = False

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == BrElement.qn

  @classmethod
  def from_xml(cls, parent: TTMLElement, xml_elem):
    element = BrElement(parent, model.Br(parent.doc))
    element.process(parent, xml_elem)
    return element
