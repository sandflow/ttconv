#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) Sandflow Consulting LLC
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

'''Validator for [EBU-TT-D](https://tech.ebu.ch/publications/tech3380), the EBU-TT subtitling distribution format (EBU Tech 3380
version 1.0.1), which is a constrained subset of IMSC 1.1.
'''

from __future__ import annotations

import io
import typing
import xml.etree.ElementTree as ET

from ttconv.imsc.namespaces import QName
import ttconv.imsc.namespaces as NS
import ttconv.imsc.reader as imsc_reader
from ttconv.imsc.validator.attribute_vocabulary import AttributeVocabulary
import ttconv.imsc.validator.ebuttd.attributes as attrs
from ttconv.imsc.validator.event_handler import EventHandler
import ttconv.imsc.validator.imsc11_model as imsc11
from ttconv.imsc.validator.imsc11_model import ErrorCountingEventHandler, IMSCElement, IMSCValidationContext, \
  METADATA_ATTRIBUTES, NON_FOREIGN_NAMESPACES
import ttconv.imsc.validator.infoset as IS
import ttconv.imsc.validator.other_attributes as other_attrs
import ttconv.imsc.validator.style_attributes as style_attrs
from ttconv.imsc.validator.rules import AnyRule, EmptyRule, NodeSequence, OneOrMoreRule, OptionalRule, PCDATARule, SequenceRule, \
  UnorderedRule, ZeroOrMoreRule
from ttconv.isd import ISD
import ttconv.style_properties as styles

EBUTTM = "urn:ebu:tt:metadata"

# head

class ConformsToStandard(IMSCElement):
  qname = QName(EBUTTM, "conformsToStandard")
  content_model = PCDATARule()

  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    super().validate_contents(element, ctx)
    text = "".join(c.value for c in element.get_children() if isinstance(c, IS.Text)).strip()
    # urn:ebu:tt:distribution:2018-04 signals conformance to version 1.0.1 of EBU-TT-D
    if text.startswith("urn:ebu:tt:distribution:") and text != "urn:ebu:tt:distribution:2018-04":
      ctx.event_handler.warn("ebuttm:conformsToStandard shall be `urn:ebu:tt:distribution:2018-04` to signal conformance to this "
        "version of EBU-TT-D, not `%s` (line %s)", text, element.get_line_number())

class DocumentCopyright(IMSCElement):
  qname = QName(EBUTTM, "documentCopyright")
  content_model = PCDATARule()

  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    super().validate_contents(element, ctx)
    ctx.event_handler.warn("ebuttm:documentCopyright is deprecated, use ttm:copyright instead (line %s)", element.get_line_number())

# the ebuttm elements are matched by the content model of their parent, unlike other foreign elements
_EBUTTM_CONTENT_NAMESPACES = NON_FOREIGN_NAMESPACES | {EBUTTM}

class DocumentMetadata(IMSCElement):
  qname = QName(EBUTTM, "documentMetadata")
  non_foreign_namespaces = _EBUTTM_CONTENT_NAMESPACES
  non_foreign_attribute_namespaces = NON_FOREIGN_NAMESPACES
  # the other children of ebuttm:documentMetadata are not significant
  content_model = ZeroOrMoreRule(AnyRule(ConformsToStandard(), DocumentCopyright(), imsc11.ForeignElement()))

  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    super().validate_contents(element, ctx)
    ctx.event_handler.warn("ebuttm:documentMetadata is deprecated (line %s)", element.get_line_number())

class Metadata(imsc11.Metadata):
  '''Only the ebuttm elements that are children of /tt:tt/tt:head/tt:metadata, or of its ebuttm:documentMetadata child, are
  significant. Any other ebuttm element is a foreign element.'''
  non_foreign_namespaces = _EBUTTM_CONTENT_NAMESPACES
  non_foreign_attribute_namespaces = NON_FOREIGN_NAMESPACES
  content_model = ZeroOrMoreRule(AnyRule(
    imsc11.Agent(),
    imsc11.Name(),
    imsc11.Actor(),
    imsc11.Copyright(),
    imsc11.Desc(),
    imsc11.Title(),
    imsc11.Item(),
    imsc11.AltText(),
    ConformsToStandard(),
    DocumentMetadata(),
    DocumentCopyright(),
    imsc11.ForeignElement(),
  ))

class Style(imsc11.Style):
  content_model = EmptyRule()
  required_attributes = AttributeVocabulary(other_attrs.XMLIDAttribute)
  optional_attributes = AttributeVocabulary(
    style_attrs.Direction,
    attrs.FontFamily,
    attrs.FontSize,
    attrs.LineHeight,
    style_attrs.TextAlign,
    attrs.Color,
    attrs.BackgroundColor,
    attrs.FontStyle,
    style_attrs.FontWeight,
    attrs.TextDecoration,
    style_attrs.UnicodeBidi,
    style_attrs.WrapOption,
    style_attrs.MultiRowAlign,
    attrs.LinePadding,
    style_attrs.FillLineGap,
  )

class Styling(imsc11.Styling):
  content_model = SequenceRule(OptionalRule(imsc11.Metadata()), OneOrMoreRule(Style()))
  optional_attributes = AttributeVocabulary()

class Region(imsc11.Region):
  content_model = OptionalRule(imsc11.Metadata())
  required_attributes = AttributeVocabulary(
    other_attrs.XMLIDAttribute,
    attrs.Origin,
    attrs.Extent,
  )
  optional_attributes = AttributeVocabulary(
    other_attrs.StyleAttribute,
    style_attrs.DisplayAlign,
    style_attrs.Overflow,
    attrs.Padding,
    style_attrs.ShowBackground,
    style_attrs.WritingMode,
  )

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)
    xml_id = e.get_attribute_value(other_attrs.XMLIDAttribute.qname)

    # that regions that are presented at the same time do not overlap is validated by the IMSC 1.1 Text Profile
    origin = e.get_attribute_value(attrs.Origin.qname)
    extent = e.get_attribute_value(attrs.Extent.qname)
    if origin is None or extent is None:
      return # reported as missing
    try:
      x, y = map(attrs.parse_pct_length, origin.split())
      width, height = map(attrs.parse_pct_length, extent.split())
    except ValueError:
      return # reported when validating the attributes
    if x + width > 100 or y + height > 100:
      ctx.event_handler.error("Region `%s` shall not extend outside the root container region (line %s)", xml_id,
        e.get_line_number())

class Layout(imsc11.Layout):
  content_model = SequenceRule(OptionalRule(imsc11.Metadata()), OneOrMoreRule(Region()))
  optional_attributes = AttributeVocabulary()

class Head(imsc11.Head):
  # Annex B lists ttm:copyright before tt:metadata, while section 2.2 requires tt:metadata before any other child element
  content_model = SequenceRule(
    UnorderedRule((imsc11.Copyright(), 0, 1), (Metadata(), 0, 1)),
    Styling(),
    Layout(),
  )
  optional_attributes = AttributeVocabulary()

# body

class Br(IMSCElement):
  qname = QName(NS.TTML, "br")
  content_model = OptionalRule(imsc11.Metadata())
  optional_attributes = AttributeVocabulary(METADATA_ATTRIBUTES)
  applicable_styles = AttributeVocabulary()

class Span(IMSCElement):
  qname = imsc11.Span.qname
  content_model = SequenceRule(
    OptionalRule(imsc11.Metadata()),
    ZeroOrMoreRule(AnyRule(Br(), PCDATARule()), mixed_content=True),
  )
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLIDAttribute,
    attrs.Begin,
    attrs.End,
    other_attrs.StyleAttribute,
    other_attrs.XMLLangAttribute,
    other_attrs.XMLSpaceAttribute,
    METADATA_ATTRIBUTES,
  )
  applicable_styles = imsc11.Span.applicable_styles

class P(IMSCElement):
  qname = imsc11.P.qname
  content_model = SequenceRule(
    OptionalRule(imsc11.Metadata()),
    ZeroOrMoreRule(AnyRule(Span(), Br(), PCDATARule()), mixed_content=True),
  )
  required_attributes = AttributeVocabulary(other_attrs.XMLIDAttribute)
  optional_attributes = AttributeVocabulary(
    attrs.Begin,
    attrs.End,
    other_attrs.StyleAttribute,
    other_attrs.RegionAttribute,
    other_attrs.XMLLangAttribute,
    other_attrs.XMLSpaceAttribute,
    METADATA_ATTRIBUTES,
  )
  applicable_styles = imsc11.P.applicable_styles

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)
    line = e.get_line_number()

    p_region = e.get_attribute_value(other_attrs.RegionAttribute.qname)
    div_region = e.parent.get_attribute_value(other_attrs.RegionAttribute.qname) if e.parent is not None else None
    if p_region is not None and div_region is not None:
      ctx.event_handler.error("<p> shall not reference a region since its parent <div> does (line %s)", line)
    elif p_region is None and div_region is None:
      ctx.event_handler.warn("<p> does not reference a region, and neither does its parent <div>, and might not be displayed "
        "(line %s)", line)

  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    super().validate_contents(element, ctx)
    if not (element.has_attribute(attrs.Begin.qname) or element.has_attribute(attrs.End.qname)):
      return
    for span in element.get_children():
      if not isinstance(span, IS.Element) or span.name.qname != Span.qname:
        continue
      if span.has_attribute(attrs.Begin.qname) or span.has_attribute(attrs.End.qname):
        ctx.event_handler.error("<span> shall not specify timing since its parent <p> does (line %s)", span.get_line_number())

class Div(IMSCElement):
  qname = imsc11.Div.qname
  content_model = SequenceRule(OptionalRule(imsc11.Metadata()), OneOrMoreRule(P()))
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLIDAttribute,
    other_attrs.StyleAttribute,
    other_attrs.RegionAttribute,
    other_attrs.XMLLangAttribute,
    METADATA_ATTRIBUTES,
  )
  applicable_styles = imsc11.Div.applicable_styles

class Body(IMSCElement):
  qname = imsc11.Body.qname
  content_model = SequenceRule(OptionalRule(imsc11.Metadata()), OneOrMoreRule(Div()))
  optional_attributes = AttributeVocabulary(other_attrs.StyleAttribute, METADATA_ATTRIBUTES)
  applicable_styles = imsc11.Body.applicable_styles

class TT(imsc11.TT):
  content_model = SequenceRule(Head(), OptionalRule(Body()))
  required_attributes = AttributeVocabulary(
    other_attrs.XMLLangAttribute,
    attrs.TimeBase,
  )
  optional_attributes = AttributeVocabulary(
    attrs.CellResolution,
    other_attrs.XMLSpaceAttribute,
    other_attrs.ActiveAreaAttribute,
  )

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)
    if not e.has_attribute(attrs.CellResolution.qname):
      ctx.event_handler.warn("ttp:cellResolution should be specified explicitly on <tt> (line %s)", e.get_line_number())

def _validate_ebuttd(f: typing.BinaryIO, event_handler: typing.Optional[EventHandler] = None) -> bool:
  '''Validates the constraints that EBU-TT-D adds to IMSC 1.1, and returns whether no ERROR-or-above records were logged.

  `f` is not validated against IMSC 1.1, and the results are only meaningful for a valid IMSC 1.1 document. Use `validate()`
  unless that is known to be the case.'''
  counting_handler = ErrorCountingEventHandler(event_handler)

  data = f.read()

  infoset = IS.Infoset.fromFile(io.BytesIO(data), counting_handler)
  if infoset is None:
    return False

  ctx = IMSCValidationContext(namespaces=infoset.namespaces, event_handler=counting_handler)

  if not TT().match(NodeSequence([infoset.root]), ctx):
    counting_handler.error("Root element must be tt")
    return False

  # the content model skips over foreign elements, but EBU-TT-D only allows them in tt:metadata
  for e in infoset.root.dfs_iterator():
    if e.name.qname.ns != NS.TTML or e.name.qname.local_name == "metadata":
      continue
    for c in e.get_children():
      if isinstance(c, IS.Element) and c.name.qname.ns not in NON_FOREIGN_NAMESPACES:
        counting_handler.error("Element {%s}%s is not permitted in <%s> (line %s)", c.name.qname.ns, c.name.qname.local_name,
          e.name.qname.local_name, c.get_line_number())

  # the ttconv model, in which styles are resolved, is only available for a valid document
  if counting_handler.error_count == 0:
    try:
      doc = imsc_reader.to_model(ET.parse(io.BytesIO(data)))
      # warn, once per region, if text that is not wrapped is presented in a region that does not have tts:overflow="visible"
      reported_regions = set()
      isd_sequence = ISD.generate_isd_sequence(doc) if doc is not None else []
      for _, isd in isd_sequence:
        for isd_region in isd.iter_regions():
          if isd_region.get_id() in reported_regions or \
            isd_region.get_style(styles.StyleProperties.Overflow) == styles.OverflowType.visible:
            continue
          if any(e.get_style(styles.StyleProperties.WrapOption) == styles.WrapOptionType.noWrap
                 for e in isd_region.dfs_iterator()):
            reported_regions.add(isd_region.get_id())
            counting_handler.warn("Region `%s` should specify tts:overflow=\"visible\" since it contains text with "
              "tts:wrapOption=\"noWrap\"", isd_region.get_id())
    except ValueError as ve:
      counting_handler.error("%s", ve)

  return counting_handler.error_count == 0

def validate(f: typing.BinaryIO, event_handler: typing.Optional[EventHandler] = None) -> bool:
  '''Validates `f` and returns whether no ERROR-or-above records were logged.

  `f` must be a valid IMSC 1.1 document, and validation stops at the first failure of the IMSC 1.1 model.'''
  data = f.read()

  if not imsc11.validate(io.BytesIO(data), event_handler):
    return False

  return _validate_ebuttd(io.BytesIO(data), event_handler)
