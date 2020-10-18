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
from fractions import Fraction
from dataclasses import dataclass, field
import typing
import ttconv.model as model
import ttconv.imsc.namespaces as xml_ns
import ttconv.imsc.attributes as imsc_attr
from ttconv.imsc.style_properties import StyleProperties
import ttconv.imsc.style_properties as styles

LOGGER = logging.getLogger(__name__)

@dataclass
class DocumentParsingContext:
  
  doc: model.Document

  style_context: styles.StyleParsingContext = field(default_factory=styles.StyleParsingContext)
  
  temporal_context: imsc_attr.TemporalAttributeParsingContext = \
    field(default_factory=imsc_attr.TemporalAttributeParsingContext)

@dataclass
class ParentParsingContext:
  implicit_begin: typing.Optional[Fraction] = Fraction(0)
  time_container: imsc_attr.TimeContainer = imsc_attr.TimeContainer.par
  lang: str = ""
  space: model.WhiteSpaceHandling = model.WhiteSpaceHandling.DEFAULT
    
class TTElement:
  '''Processes the TTML <tt> element
  '''

  qn = f"{{{xml_ns.TTML}}}tt"

  @staticmethod
  def process(ttml_elem):

    doc = model.Document()

    context = DocumentParsingContext(doc=doc)

    # process attributes

    space = imsc_attr.XMLSpaceAttribute.extract(ttml_elem) or model.WhiteSpaceHandling.DEFAULT

    lang = imsc_attr.XMLLangAttribute.extract(ttml_elem)
    
    if lang is None:
      LOGGER.warning("xml:lang not specified on tt")
      lang = ""

    context.doc.set_lang(lang)

    context.doc.set_cell_resolution(imsc_attr.CellResolutionAttribute.extract(ttml_elem))

    px_resolution = imsc_attr.ExtentAttribute.extract(ttml_elem)

    if px_resolution is not None:
      context.doc.set_px_resolution(px_resolution)

    active_area = imsc_attr.ActiveAreaAttribute.extract(ttml_elem)

    if active_area is not None:
      context.doc.set_active_area(active_area)

    context.temporal_context.frame_rate = imsc_attr.FrameRateAttribute.extract(ttml_elem)

    context.temporal_context.tick_rate = imsc_attr.TickRateAttribute.extract(ttml_elem)

    # process children elements elements

    has_body = False
    has_head = False

    parent_context = ParentParsingContext(lang=lang, space=space)

    for child_element in ttml_elem:

      if BodyElement.is_instance(child_element):

        if not has_body:

          context.doc.set_body(
            ContentElement.process(
              context,
              parent_context,
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
            parent_context,
            child_element
          )

          has_head = True

        else:
          LOGGER.error("More than one head element present")

    return doc

class HeadElement:
  '''Processes the TTML <head> element
  '''

  qn = f"{{{xml_ns.TTML}}}head"

  @staticmethod
  def process(context: DocumentParsingContext, parent_context: ParentParsingContext, ttml_element):

    self_context = ParentParsingContext(
      space=imsc_attr.XMLSpaceAttribute.extract(ttml_element) or parent_context.space,
      lang=imsc_attr.XMLLangAttribute.extract(ttml_element) or parent_context.lang
    )

    # process children elements

    has_layout = False
    has_styling = False
    
    for child_element in ttml_element:

      if child_element.tag == LayoutElement.qn:

        if not has_layout:

          has_layout = True

          LayoutElement.process(
            context,
            self_context,
            child_element
          )

        else:

          LOGGER.error("Multiple layout elements")

      elif child_element.tag == StylingElement.qn:

        if not has_styling:

          has_styling = True

          StylingElement.process(
            context,
            self_context,
            child_element
          )

        else:

          LOGGER.error("Multiple styling elements")



class LayoutElement:
  '''Process the TTML <layout> element
  '''

  qn = f"{{{xml_ns.TTML}}}layout"

  @staticmethod
  def process(context: DocumentParsingContext, parent_context: ParentParsingContext, ttml_element):

    self_context = ParentParsingContext(
      space=imsc_attr.XMLSpaceAttribute.extract(ttml_element) or parent_context.space,
      lang=imsc_attr.XMLLangAttribute.extract(ttml_element) or parent_context.lang
    )
    
    for child_element in ttml_element:

      if child_element.tag == RegionElement.qn:

        r = RegionElement.process(
          context,
          self_context,
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

  qn = f"{{{xml_ns.TTML}}}region"

  @staticmethod
  def process(context: DocumentParsingContext, parent_context: ParentParsingContext, ttml_element):

    rid = imsc_attr.XMLIDAttribute.extract(ttml_element)

    if rid is None:
      LOGGER.error("All regions must have an id")
      return None

    r = model.Region(rid, context.doc)

    # process attributes
    
    r.set_space(imsc_attr.XMLSpaceAttribute.extract(ttml_element) or parent_context.space)

    r.set_lang(imsc_attr.XMLLangAttribute.extract(ttml_element) or parent_context.lang)
    
    ContentElement.process_style_properties(context, parent_context, ttml_element, r)

    return r

class StylingElement:
  '''Process the TTML <styling> element
  '''

  qn = f"{{{xml_ns.TTML}}}styling"

  @staticmethod
  def process(_context: DocumentParsingContext, _parent_context: ParentParsingContext, _ttml_element):
    pass

#
# process content elements
#

class ContentElement:
  '''TTML content elements: body, div, p, span, br
  '''

  @staticmethod
  def process_region_property(doc_context: DocumentParsingContext, _parent_context : ParentParsingContext, ttml_element, element):
    '''Read the region attribute and associate the element with the corresponding region'''
    rid = ttml_element.attrib.get('region')

    if rid is not None:
      r = doc_context.doc.get_region(rid)
      
      if r is not None:
        element.set_region(r)
      else:
        LOGGER.warning("Element references unknown region")

  @staticmethod
  def process_style_properties(doc_context: DocumentParsingContext, _: ParentParsingContext, ttml_element, element):
    '''Read TTML style properties into the model'''
    for attr in ttml_element.attrib:
      prop = StyleProperties.BY_QNAME.get(attr)
      if prop is not None:
        try:
          element.set_style(prop.model_prop, prop.extract(doc_context, ttml_element.attrib.get(attr)))
        except ValueError:
          LOGGER.error("Error reading style property: %s", prop.__name__)


  @staticmethod
  def class_from_ttml_element(ttml_element):

    content_element_classes = [
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
      BrElement
    ]

    for element_class in content_element_classes:
      if element_class.is_instance(ttml_element):
        return element_class

    return None

  @staticmethod
  def make_anonymous_span(document, parent_element, span_text):
    if isinstance(parent_element, model.Span):

      return model.Text(document, span_text)

    else:

      s = model.Span(document)
      
      s.push_child(model.Text(document, span_text))

      return s
  
  @staticmethod
  def process(doc_context: DocumentParsingContext, parent_context: ParentParsingContext, ttml_element):

    model_class = ContentElement.class_from_ttml_element(ttml_element)
    
    if model_class is None:
      return None

    if parent_context.time_container == imsc_attr.TimeContainer.seq and model_class is BrElement:
      return None
      
    model_element = model_class.make(doc_context.doc)

    self_context = ParentParsingContext(
      lang=imsc_attr.XMLLangAttribute.extract(ttml_element) or parent_context.lang,
      space=imsc_attr.XMLSpaceAttribute.extract(ttml_element) or parent_context.space
      )

    model_element.set_space(self_context.space)

    model_element.set_lang(self_context.lang)

    if model_class.has_region:
      ContentElement.process_region_property(doc_context, parent_context, ttml_element, model_element)

    if model_class.has_styles:
      ContentElement.process_style_properties(doc_context, parent_context, ttml_element, model_element)

    if model_class.has_timing:

      (explicit_begin, explicit_end, explicit_dur, time_container) = \
        imsc_attr.TemporalAttribute.extract(doc_context.temporal_context, ttml_element)

      implicit_begin = parent_context.implicit_begin

      desired_begin = implicit_begin + (explicit_begin if explicit_begin is not None else Fraction(0))

      implicit_end = desired_begin

      self_context.time_container = time_container

      self_context.implicit_begin = Fraction(0)

    children = []

    # process text nodes

    if ttml_element.text is not None and \
      parent_context.time_container != imsc_attr.TimeContainer.seq and \
      model_class.is_mixed:

      children.append(ContentElement.make_anonymous_span(doc_context.doc, model_element, ttml_element.text))

      implicit_end = None

    # process children elements

    for ttml_child_element in ttml_element:

      child_element = ContentElement.process(
        doc_context,
        self_context,
        ttml_child_element
      )

      if child_element is None:
        continue

      if model_class.has_timing:

        if time_container == imsc_attr.TimeContainer.seq:

          implicit_end = child_element.get_end()

          self_context.implicit_begin = implicit_end

        else:

          if implicit_end is not None and child_element.get_end() is not None:
            implicit_end = max(implicit_end, child_element.get_end())
          else:
            implicit_end = None

      # TODO: add support for set

      children.append(child_element)

      # process tail text node
      
      if ttml_child_element.tail is not None and \
        parent_context.time_container != imsc_attr.TimeContainer.seq and \
        model_class.is_mixed:

        children.append(ContentElement.make_anonymous_span(doc_context.doc, model_element, ttml_child_element.tail))

        implicit_end = None

    # add childrend

    try:

      model_element.push_children(children)

    except ValueError:

      LOGGER.error("illegal children elements")

      return None

    # compute end
    
    if model_class.has_timing:

      if explicit_end is not None and explicit_dur is not None:

        desired_end = min(desired_begin + explicit_dur, implicit_begin + explicit_end)

      elif explicit_end is None and explicit_dur is not None:

        desired_end = desired_begin + explicit_dur

      elif explicit_end is not None and explicit_dur is None:

        desired_end = implicit_begin + explicit_end

      else:

        desired_end = implicit_end

      model_element.set_begin(desired_begin if desired_begin != 0 else None)

      model_element.set_end(desired_end)


    return model_element
'''
function resolveTiming(doc, element, prev_sibling, parent) {

        /* are we in a seq container? */

        var isinseq = parent && parent.timeContainer === "seq";

        /* determine implicit begin */

        var implicit_begin = 0; /* default */

        if (parent) {

            if (isinseq && prev_sibling) {

                /*
                 * if seq time container, offset from the previous sibling end
                 */

                implicit_begin = prev_sibling.end;


            } else {

                implicit_begin = parent.begin;

            }

        }

        /* compute desired begin */

        element.begin = element.explicit_begin ? element.explicit_begin + implicit_begin : implicit_begin;


        /* determine implicit end */

        var implicit_end = element.begin;

        var s = null;

        for (var set_i in element.sets) {

            resolveTiming(doc, element.sets[set_i], s, element);

            if (element.timeContainer === "seq") {

                implicit_end = element.sets[set_i].end;

            } else {

                implicit_end = Math.max(implicit_end, element.sets[set_i].end);

            }

            s = element.sets[set_i];

        }

        if (!('contents' in element)) {

            /* anonymous spans and regions and <set> and <br>s and spans with only children text nodes */

            if (isinseq) {

                /* in seq container, implicit duration is zero */

                implicit_end = element.begin;

            } else {

                /* in par container, implicit duration is indefinite */

                implicit_end = Number.POSITIVE_INFINITY;

            }

        } else {

            for (var content_i in element.contents) {

                resolveTiming(doc, element.contents[content_i], s, element);

                if (element.timeContainer === "seq") {

                    implicit_end = element.contents[content_i].end;

                } else {

                    implicit_end = Math.max(implicit_end, element.contents[content_i].end);

                }

                s = element.contents[content_i];

            }

        }

        /* determine desired end */
        /* it is never made really clear in SMIL that the explicit end is offset by the implicit begin */

        if (element.explicit_end !== null && element.explicit_dur !== null) {

            element.end = Math.min(element.begin + element.explicit_dur, implicit_begin + element.explicit_end);

        } else if (element.explicit_end === null && element.explicit_dur !== null) {

            element.end = element.begin + element.explicit_dur;

        } else if (element.explicit_end !== null && element.explicit_dur === null) {

            element.end = implicit_begin + element.explicit_end;

        } else {

            element.end = implicit_end;
        }

        delete element.explicit_begin;
        delete element.explicit_dur;
        delete element.explicit_end;

        doc._registerEvent(element);

    }
'''


class BodyElement:
  '''Process TTML body element
  '''

  qn = f"{{{xml_ns.TTML}}}body"
  has_region = True
  has_styles = True
  has_timing = True
  is_mixed = False

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == BodyElement.qn

  @staticmethod
  def make(doc: model.Document):
    return model.Body(doc)


class DivElement:
  '''Process TTML <div> element
  '''

  qn = f"{{{xml_ns.TTML}}}div"
  has_region = True
  has_styles = True
  has_timing = True
  is_mixed = False

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == DivElement.qn

  @staticmethod
  def make(doc: model.Document):
    return model.Div(doc)


class PElement:
  '''Process TTML <p> element
  '''

  qn = f"{{{xml_ns.TTML}}}p"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = True

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == PElement.qn

  @staticmethod
  def make(doc: model.Document):
    return model.P(doc)


class SpanElement:
  '''Process the TTML <span> element
  '''
  qn = f"{{{xml_ns.TTML}}}span"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = True

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == SpanElement.qn and SpanElement.get_ruby_attr(ttml_element) is None

  @staticmethod
  def make(doc: model.Document):
    return model.Span(doc)

  @staticmethod
  def get_ruby_attr(ttml_span):
    return ttml_span.get(f"{{{xml_ns.TTS}}}ruby")


class RubyElement:
  '''Process the TTML <span tts:ruby="container"> element
  '''
  ruby = "container"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = False

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == SpanElement.qn and SpanElement.get_ruby_attr(ttml_element) == RubyElement.ruby

  @staticmethod
  def make(doc: model.Document):
    return model.Ruby(doc)


class RbElement:
  '''Process the TTML <span tts:ruby="base"> element
  '''
  ruby = "base"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = True

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == SpanElement.qn and SpanElement.get_ruby_attr(ttml_element) == RbElement.ruby

  @staticmethod
  def make(doc: model.Document):
    return model.Rb(doc)

class RtElement:
  '''Process the TTML <span tts:ruby="text"> element
  '''
  ruby = "text"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = True

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == SpanElement.qn and SpanElement.get_ruby_attr(ttml_element) == RtElement.ruby

  @staticmethod
  def make(doc: model.Document):
    return model.Rt(doc)


class RpElement:
  '''Process the TTML <span tts:ruby="delimiter"> element
  '''

  ruby = "delimiter"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = True

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == SpanElement.qn and SpanElement.get_ruby_attr(ttml_element) == RpElement.ruby

  @staticmethod
  def make(doc: model.Document):
    return model.Rp(doc)


class RbcElement:
  '''Process the TTML <span tts:ruby="baseContainer"> element
  '''

  ruby = "baseContainer"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = False

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == SpanElement.qn and SpanElement.get_ruby_attr(ttml_element) == RbcElement.ruby

  @staticmethod
  def make(doc: model.Document):
    return model.Rbc(doc)


class RtcElement:
  '''Process the TTML <span tts:ruby="textContainer"> element
  '''

  ruby = "textContainer"
  has_timing = True
  has_region = True
  has_styles = True
  is_mixed = False

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == SpanElement.qn and SpanElement.get_ruby_attr(ttml_element) == RtcElement.ruby

  @staticmethod
  def make(doc: model.Document):
    return model.Rtc(doc)

class BrElement:
  '''Process the TTML <br> element
  '''

  qn = f"{{{xml_ns.TTML}}}br"
  has_timing = False
  has_region = False
  has_styles = True
  is_mixed = False

  @staticmethod
  def is_instance(ttml_element):
    return ttml_element.tag == BrElement.qn

  @staticmethod
  def make(doc: model.Document):
    return model.Br(doc)
