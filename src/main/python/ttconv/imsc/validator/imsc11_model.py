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

from __future__ import annotations
from dataclasses import dataclass, field
import io
from typing import List
import typing
import xml.etree.ElementTree as ET

from ttconv.imsc.validator.attribute_vocabulary import AttributeVocabulary
from ttconv.imsc.validator.event_handler import EventHandler
import ttconv.imsc.validator.namespaces
import ttconv.imsc.validator.other_attributes as other_attrs
import ttconv.imsc.validator.style_attributes as style_attrs
from ttconv.imsc.validator.rules import AnyRule, EmptyRule, NodeSequence, OneOrMoreRule, OptionalRule, PCDATARule, Rule, SequenceRule, ZeroOrMoreRule
import ttconv.imsc.validator.infoset as IS
import ttconv.imsc.validator.namespaces as NS

from ttconv.imsc.validator.ttml_profile_helper import is_ttml2_feature_ns, is_ttml2_feature_designation, is_ttml2_extension_designation
from ttconv.imsc.validator.uri_helper import is_absolute_uri, urijoin

import ttconv.imsc.reader as imsc_reader
from ttconv.filters.doc.imsc11text import IMSC11TextFilter

class ErrorCountingEventHandler(EventHandler):
  '''A facade `EventHandler` to count the number of error/fatal events received.'''

  def __init__(self, delegate: typing.Optional[EventHandler] = None):
    self._delegate = delegate if delegate is not None else EventHandler()
    self.error_count = 0

  def debug(self, msg: str, *args):
    self._delegate.debug(msg, *args)

  def info(self, msg: str, *args):
    self._delegate.info(msg, *args)

  def warn(self, msg: str, *args):
    self._delegate.warn(msg, *args)

  def error(self, msg: str, *args):
    self.error_count += 1
    self._delegate.error(msg, *args)

  def fatal(self, msg: str, *args):
    self.error_count += 1
    self._delegate.fatal(msg, *args)

@dataclass
class StyleDefinition:
  id: str
  in_styling: bool
  style_refs: typing.Set[str] = field(default_factory=set)
  spec_styles: typing.Set[ttconv.imsc.validator.namespaces.QName] = field(default_factory=set)

@dataclass
class IMSCValidationContext(other_attrs.ValidationContext):
  event_handler: EventHandler = field(default_factory=ErrorCountingEventHandler)
  xml_base_stack: List[str] = field(default_factory=lambda: [])
  in_head: bool = False
  in_styling: bool = False
  element_stack: List[IS.Element] = field(default_factory=lambda: [])
  rule_stack: List[Rule] = field(default_factory=lambda: [])
  style_defs: typing.Dict[str, StyleDefinition] = field(default_factory=dict)

PARAMETER_ATTRIBUTES = AttributeVocabulary(
  other_attrs.ActiveAreaAttribute,
  other_attrs.CellResolutionAttribute,
  other_attrs.DisplayAspectRatioAttribute,
#  other_attrs.DropModeAttribute,
  other_attrs.FrameRateAttribute,
  other_attrs.FrameRateMultiplierAttribute,
  other_attrs.TickRateAttribute,
  other_attrs.TimeBaseAttribute,
  other_attrs.ContentProfilesAttribute,
  other_attrs.ProfileAttribute,
  other_attrs.AspectRatioAttribute,
  other_attrs.ProgressivelyDecodableAttribute,
)

TIMING_ATTRIBUTES = AttributeVocabulary(
  other_attrs.BeginAttribute,
  other_attrs.EndAttribute,
  other_attrs.DurAttribute
)

METADATA_ATTRIBUTES = AttributeVocabulary(
  other_attrs.MetadataRoleAttribute,
  other_attrs.MetadataAgentAttribute
)

# style properties that are generally permitted
STYLE_ATTRIBUTES = AttributeVocabulary(
  style_attrs.BackgroundColor,
  style_attrs.Color,
  style_attrs.Direction,
  style_attrs.Disparity,
  style_attrs.Display,
  style_attrs.DisplayAlign,
  style_attrs.Extent,
  style_attrs.FillLineGap,
  style_attrs.ForcedDisplay,
  style_attrs.FontFamily,
  style_attrs.FontSize,
  style_attrs.FontStyle,
  style_attrs.FontVariant,
  style_attrs.FontWeight,
  style_attrs.LineHeight,
  style_attrs.LinePadding,
  style_attrs.LuminanceGain,
  style_attrs.MultiRowAlign,
  style_attrs.Opacity,
  style_attrs.Origin,
  style_attrs.Overflow,
  style_attrs.Padding,
  style_attrs.Position,
  style_attrs.Ruby,
  style_attrs.RubyAlign,
  style_attrs.RubyPosition,
  style_attrs.RubyReserve,
  style_attrs.Shear,
  style_attrs.ShowBackground,
  style_attrs.TextAlign,
  style_attrs.TextCombine,
  style_attrs.TextDecoration,
  style_attrs.TextEmphasis,
  style_attrs.TextOutline,
  style_attrs.TextShadow,
  style_attrs.UnicodeBidi,
  style_attrs.Visibility,
  style_attrs.WrapOption,
  style_attrs.WritingMode,
  style_attrs.ZIndex,
)

DEPRECATED_ATTRIBUTES = AttributeVocabulary(
  style_attrs.ZIndex,
  other_attrs.AspectRatioAttribute,
  other_attrs.ProgressivelyDecodableAttribute,
)

NON_FOREIGN_NAMESPACES = set([
  None,
  NS.XML,
  NS.TTML,
  NS.TTP,
  NS.TTS,
  NS.TTA,
  NS.TTM,
  NS.ITTP,
  NS.ITTS,
  NS.ITTM,
  NS.EBUTTS,
  NS.SMPTE,
  NS.XLINK
])

class IMSCElement(Rule):

  qname: NS.QName
  content_model: Rule
  optional_attributes = AttributeVocabulary()
  required_attributes = AttributeVocabulary()
  applicable_styles = AttributeVocabulary()

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):

    # validate attributes that are not prohibited
    for attr in e.get_attributes():
      # ignore foreign namespaces
      if not attr.name.qname.ns in NON_FOREIGN_NAMESPACES:
        continue

      attr_model = self.optional_attributes.get(attr.name.qname) or self.required_attributes.get(attr.name.qname)
      if attr_model is None:
        ctx.event_handler.error("Attribute %s is prohibited on <%s> (line %s)", attr.name.qname.local_name, e.get_name().qname.local_name, e.get_line_number())
        continue

      if attr.name.qname in DEPRECATED_ATTRIBUTES:
        ctx.event_handler.warn("Attribute (%s) is deprecated on <%s> (line %s)", attr.name.qname.local_name, e.get_name().qname.local_name, e.get_line_number())

      try:
        attr_model.validate(attr.value, ctx)
      except ValueError as ve:
        ctx.event_handler.error("%s", ve)

      if e.get_name().qname not in (Style.qname, Set.qname, Initial.qname) and \
            hasattr(attr_model, "is_inherited") and \
            not attr_model.is_inherited \
            and self.applicable_styles is not None and \
            attr.name.qname not in self.applicable_styles:
          ctx.event_handler.error("Attribute %s is not applicable to <%s> (line %s)", attr.name.qname.local_name, e.get_name().qname.local_name, e.get_line_number())

    # check for required attributes
    for req_attr in self.required_attributes:
      if not e.has_attribute(req_attr.qname):
        ctx.event_handler.error("Required attribute `%s` missing", req_attr.qname)

    # check for prohibited styles through referential styling
    if e.get_name().qname not in (Style.qname, Set.qname, Initial.qname):
      sa = e.get_attribute(other_attrs.StyleAttribute.qname)
      if sa is not None:
        for style_id in other_attrs.StyleAttribute.parse(sa.value):
          style_def = ctx.style_defs.get(style_id)
          if style_def is not None:
            for ref_style in sorted(style_def.spec_styles):
              attr_model = STYLE_ATTRIBUTES.get(ref_style)
              if attr_model is None or not hasattr(attr_model, "is_inherited"):
                continue
              if attr_model.is_inherited is False and self.applicable_styles is not None and ref_style not in self.applicable_styles:
                ctx.event_handler.error("Referential style %s is not applicable to <%s> (line %s)", ref_style.local_name, e.get_name().qname.local_name, e.get_line_number())

  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    # TODO: report line numbers contained in element
    # TODO: report pattern that is failing
    if hasattr(self, "content_model") and \
      not self.content_model.match_all(
        NodeSequence(element.get_children(),
                     non_foreign_ns=NON_FOREIGN_NAMESPACES),
                     ctx):
      ctx.event_handler.error(f"{self.pattern()} contents does not match {self.content_model.pattern()}")

  def match(self, their_seq: NodeSequence, ctx: IMSCValidationContext) -> bool:
    if not self.is_instance(their_seq, ctx):
      return False
    element = their_seq.pop()
    assert isinstance(element, IS.Element)

    # validate attributes
    self.validate_attributes(element, ctx)

    # process xml:base
    xml_base = element.get_attribute(other_attrs.XMLBaseAttribute.qname)
    if xml_base is not None:
      ctx.xml_base_stack.append(xml_base.value)

    # process element and rule stack
    ctx.element_stack.append(element)
    ctx.rule_stack.append(self)

    self.validate_contents(element, ctx)

    # process element and rule stack
    ctx.element_stack.pop()
    ctx.rule_stack.pop()

    # pop xml:base
    if xml_base is not None:
      ctx.xml_base_stack.pop()

    return True

  def is_instance(self, their_seq: NodeSequence, ctx: IMSCValidationContext) -> bool:
    element = their_seq.peek()
    return isinstance(element, IS.Element) and element.name.qname == self.qname

  def pattern(self):
    return self.qname.local_name

class ForeignElement(Rule):
  def is_instance(self, their_seq: NodeSequence, ctx: IMSCValidationContext) -> bool:
    element = their_seq.peek()
    if not isinstance(element, IS.Element):
      return False

    return element.name.qname.ns not in NON_FOREIGN_NAMESPACES

  def match(self, their_seq: NodeSequence, ctx: IMSCValidationContext) -> bool:
    if not self.is_instance(their_seq, ctx):
      return False
    element = their_seq.pop()

    return True

  def pattern(self):
    # TODO: maybe use "<foreign>" instead?
    return "FOREIGN"

class Actor(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTM, "actor")
  content_model = EmptyRule()
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLLangAttribute,
    other_attrs.XMLIDAttribute,
    other_attrs.XMLSpaceAttribute,
    )
  required_attributes = AttributeVocabulary(
    other_attrs.AgentAttribute,
  )

class Name(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTM, "name")
  content_model = PCDATARule()
  required_attributes = AttributeVocabulary(
    other_attrs.NameTypeAttribute,
  )
  optional_attributes = AttributeVocabulary(other_attrs.XMLLangAttribute,
    other_attrs.XMLIDAttribute,
    other_attrs.XMLSpaceAttribute,)

class Agent(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTM, "agent")
  content_model: Rule = SequenceRule(ZeroOrMoreRule(Name()), OptionalRule(Actor()))
  required_attributes = AttributeVocabulary(
    other_attrs.AgentTypeAttribute,
  )
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLLangAttribute,
    other_attrs.XMLIDAttribute,
    other_attrs.XMLSpaceAttribute,
    )

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)
    xml_id = e.get_attribute(other_attrs.XMLIDAttribute.qname);
    if xml_id is not None and ctx.in_head:
      ctx.sig_agent_ids.add(xml_id.value)    

class Item(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTM, "item")
  required_attributes = AttributeVocabulary(
    other_attrs.ItemNameAttribute,
  )
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLLangAttribute,
    other_attrs.XMLIDAttribute,
    other_attrs.XMLSpaceAttribute,
    )
Item.content_model = AnyRule(PCDATARule(), ZeroOrMoreRule(Item()))

class Copyright(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTM, "copyright")
  content_model: Rule = PCDATARule()
  optional_attributes = AttributeVocabulary(other_attrs.XMLLangAttribute,
    other_attrs.XMLIDAttribute,
    other_attrs.XMLSpaceAttribute,)

class Desc(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTM, "desc")
  content_model: Rule = PCDATARule()
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLLangAttribute,
    other_attrs.XMLIDAttribute,
    other_attrs.XMLSpaceAttribute,
    )

class Title(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTM, "title")
  content_model: Rule = PCDATARule()
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLLangAttribute,
    other_attrs.XMLIDAttribute,
    other_attrs.XMLSpaceAttribute,
    )

class AltText(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.ITTM, "altText")
  content_model: Rule = PCDATARule()
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLLangAttribute,
    other_attrs.XMLIDAttribute,
    other_attrs.XMLSpaceAttribute,
    )
  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    ctx.event_handler.warn("ittm:altText element is deprecated")

class Metadata(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTML, "metadata")
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLLangAttribute,
    other_attrs.XMLIDAttribute,
    other_attrs.XMLSpaceAttribute,
    METADATA_ATTRIBUTES,
    )
  content_model: Rule = ZeroOrMoreRule(AnyRule(Agent(), Name(), Actor(), Copyright(), Desc(), Title(), Item(), AltText(), ForeignElement()))

class Initial(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTML, "initial")
  content_model: Rule = ZeroOrMoreRule(Metadata())
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLLangAttribute,
    other_attrs.XMLIDAttribute,
    other_attrs.XMLSpaceAttribute,
    STYLE_ATTRIBUTES
  )

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)
    # verify that one or more style attributes are present
    if not any(attr.name.qname in STYLE_ATTRIBUTES for attr in e.get_attributes()):
      ctx.event_handler.error("No style attribute specified in an initial element")

class Style(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTML, "style")
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLLangAttribute,
    other_attrs.XMLIDAttribute,
    other_attrs.XMLSpaceAttribute,
    STYLE_ATTRIBUTES,
    other_attrs.StyleAttribute,
    style_attrs.Extent,
    style_attrs.Disparity,
    style_attrs.Opacity,
    style_attrs.Padding
  )
  content_model = ZeroOrMoreRule(Metadata())

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)
    # remember all the style elements we encounter
    if ctx.in_styling:
      xml_id = e.get_attribute(other_attrs.XMLIDAttribute.qname)
      if xml_id is not None:
        sd = StyleDefinition(xml_id.value, in_styling=ctx.in_styling)
        ctx.style_defs[xml_id.value] = sd

        # collect referenced styles
        sa = e.get_attribute(other_attrs.StyleAttribute.qname)
        if sa is not None:
          for target_id in other_attrs.StyleAttribute.parse(sa.value):
            sd.style_refs.add(target_id)

        # collect specified styles
        for a in e.get_attributes():
          if a.name.qname in STYLE_ATTRIBUTES:
            sd.spec_styles.add(a.name.qname)

class Styling(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTML, "styling")
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLLangAttribute,
    other_attrs.XMLIDAttribute,
    other_attrs.XMLSpaceAttribute,
  )
  content_model = SequenceRule(
    ZeroOrMoreRule(Metadata()),
    ZeroOrMoreRule(Initial()),
    ZeroOrMoreRule(Style()),
  )
  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    ctx.in_styling = True
    r = super().validate_contents(element, ctx)
    ctx.in_styling = False

    def _collect_ref_styles(root: StyleDefinition, current: StyleDefinition):
      for ref_id in current.style_refs:
        if root.id == ref_id:
          ctx.event_handler.error("Infinite referential styling loop starting with style id %s", root.id)
          return
        sd = ctx.style_defs.get(ref_id)
        if sd is not None:
          if not sd.in_styling:
            ctx.event_handler.error("Invalid reference to nested style id %s", ref_id)
          root.spec_styles.update(sd.spec_styles)
          _collect_ref_styles(root, sd)

    # detect style reference loops, reference to nested styles and flatten referential style properties
    for _, style_def in ctx.style_defs.items():
      _collect_ref_styles(style_def, style_def)


class Region(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTML, "region")
  content_model: Rule
  required_attributes = AttributeVocabulary(
    other_attrs.XMLIDAttribute,
  )
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLLangAttribute,
    other_attrs.XMLSpaceAttribute,
    TIMING_ATTRIBUTES,
    other_attrs.StyleAttribute,
    STYLE_ATTRIBUTES
  )
  applicable_styles = AttributeVocabulary(
    style_attrs.BackgroundColor,
    style_attrs.Disparity,
    style_attrs.Display,
    style_attrs.DisplayAlign,
    style_attrs.Extent,
    style_attrs.LuminanceGain,
    style_attrs.Opacity,
    style_attrs.Origin,
    style_attrs.Overflow,
    style_attrs.Padding,
    style_attrs.Position,
    style_attrs.ShowBackground,
    style_attrs.Visibility,
    style_attrs.WritingMode,
    style_attrs.ZIndex
  )
  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)
    xml_id = e.get_attribute(other_attrs.XMLIDAttribute.qname);
    if xml_id is not None and ctx.in_head:
      ctx.region_ids.add(xml_id.value)   

class Layout(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTML, "layout")
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLLangAttribute,
    other_attrs.XMLIDAttribute,
    other_attrs.XMLSpaceAttribute,
  )
  content_model = ZeroOrMoreRule(AnyRule(Region(), Metadata(), ForeignElement()))

class Feature(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTP, "feature")
  content_model = PCDATARule()
  required_attributes = AttributeVocabulary(
  )
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLIDAttribute,
    other_attrs.FeatureValueAttribute,
  )
  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    super().validate_contents(element, ctx)

    text: str = ""
    for c in element.get_children():
      assert isinstance(c, IS.Text)
      text = text + c.value

    uri = urijoin(ctx.xml_base_stack[-1] if ctx.xml_base_stack else NS.TTF, text)

    if not is_ttml2_feature_designation(uri):
      ctx.event_handler.error("Invalid feature designator '%s'", uri)

class Extension(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTP, "extension")
  content_model = PCDATARule()
  required_attributes = AttributeVocabulary(
  )
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLIDAttribute,
    other_attrs.FeatureValueAttribute,
  )
  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    super().validate_contents(element, ctx)

    text: str = ""
    for c in element.get_children():
      assert isinstance(c, IS.Text)
      text = text + c.value

    uri = urijoin(ctx.xml_base_stack[-1] if ctx.xml_base_stack else NS.TTE, text)

    if not is_ttml2_extension_designation(uri):
      ctx.event_handler.error("Invalid extension designator '%s'", uri)

class Features(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTP, "features")
  content_model = SequenceRule(
    ZeroOrMoreRule(Metadata()),
    ZeroOrMoreRule(Feature())
  )
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLIDAttribute,
    other_attrs.XMLBaseAttribute,
  )
  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)

    uri_attr = e.get_attribute(other_attrs.XMLBaseAttribute.qname)
    if uri_attr is not None and not is_ttml2_feature_ns(uri_attr.value):
      ctx.event_handler.error("Invalid feature base namespace '%s'", uri_attr.value)

class Extensions(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTP, "extensions")
  content_model = SequenceRule(
    ZeroOrMoreRule(Metadata()),
    ZeroOrMoreRule(Extension())
  )
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLIDAttribute,
    other_attrs.XMLBaseAttribute,
  )
  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)

    uri_attr = e.get_attribute(other_attrs.XMLBaseAttribute.qname)
    if uri_attr is not None and not is_absolute_uri(uri_attr.value):
      ctx.event_handler.error("Invalid extension base namespace '%s'", uri_attr.value)


class Profile(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTP, "profile")
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLIDAttribute,
    other_attrs.UseAttribute,
  )
Profile.content_model = SequenceRule(
  ZeroOrMoreRule(Metadata()),
  AnyRule(
    SequenceRule(
      ZeroOrMoreRule(Features()),
      ZeroOrMoreRule(Extensions())
    ),
    ZeroOrMoreRule(Profile())
  )
)

class Head(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTML, "head")
  content_model = SequenceRule(
    ZeroOrMoreRule(AnyRule(Metadata(), Agent(), Copyright(), Desc(), Title(), Item(), Profile())),
    OptionalRule(Styling()),
    OptionalRule(Layout()),
  )
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLLangAttribute,
    other_attrs.XMLIDAttribute,
    other_attrs.XMLSpaceAttribute,
  )

  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    ctx.in_head = True
    super().validate_contents(element, ctx)
    ctx.in_head = False

class Set(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTML, "set")
  content_model = ZeroOrMoreRule(Metadata())
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLIDAttribute,
    other_attrs.XMLLangAttribute,
    other_attrs.XMLSpaceAttribute,
    TIMING_ATTRIBUTES,
    other_attrs.StyleAttribute,
    STYLE_ATTRIBUTES,
    style_attrs.Extent,
    style_attrs.Disparity,
    style_attrs.Opacity,
    style_attrs.Padding,
  )
  region_only_attributes = (
    style_attrs.Extent,
    style_attrs.Disparity,
    style_attrs.Opacity,
    style_attrs.Padding,
  )

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)
    parent_model = ctx.rule_stack[-1]
    if not isinstance(parent_model, IMSCElement):
      return
    for attr in e.get_attributes():
      style_model = STYLE_ATTRIBUTES.get(attr.name.qname)
      if hasattr(style_model, "is_inherited") and \
            not style_model.is_inherited \
            and parent_model.applicable_styles is not None and \
            attr.name.qname not in parent_model.applicable_styles:
          ctx.event_handler.error("Attribute %s is not applicable to %s", attr.name.qname, parent_model.qname)

Region.content_model = ZeroOrMoreRule(AnyRule(Metadata(), Style(), Set(), ForeignElement()))


class Br(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTML, "br")
  content_model = SequenceRule(
    ZeroOrMoreRule(Metadata()),
    ZeroOrMoreRule(Set())
  )
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLIDAttribute,
    other_attrs.XMLLangAttribute,
    other_attrs.XMLSpaceAttribute,
    other_attrs.StyleAttribute,
    METADATA_ATTRIBUTES,
    STYLE_ATTRIBUTES,
  )
  applicable_styles = AttributeVocabulary()

class Span(IMSCElement):
  """A `span` element. Subclasses represent specific ruby roles, distinguished
  by the specified value of tts:ruby, per TTML2, 10.2.35."""

  qname = ttconv.imsc.validator.namespaces.QName(NS.TTML, "span")
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLIDAttribute,
    other_attrs.XMLLangAttribute,
    other_attrs.XMLSpaceAttribute,
    TIMING_ATTRIBUTES,
    other_attrs.TimeContainerAttribute,
    other_attrs.RegionAttribute,
    other_attrs.StyleAttribute,
    STYLE_ATTRIBUTES,
    METADATA_ATTRIBUTES,
  )
  applicable_styles = AttributeVocabulary(
    style_attrs.BackgroundColor,
    style_attrs.Color,
    style_attrs.Direction,
    style_attrs.Display,
    style_attrs.FontFamily,
    style_attrs.FontSize,
    style_attrs.FontStyle,
    style_attrs.FontVariant,
    style_attrs.FontWeight,
    style_attrs.Ruby,
    style_attrs.TextCombine,
    style_attrs.TextDecoration,
    style_attrs.TextEmphasis,
    style_attrs.TextOutline,
    style_attrs.TextShadow,
    style_attrs.UnicodeBidi,
    style_attrs.Visibility,
    style_attrs.WrapOption,
  )
  # value of tts:ruby or `None` if tts:ruby is `"none"` or absent
  ruby_value: typing.Optional[str] = None

  def is_instance(self, their_seq: NodeSequence, ctx: IMSCValidationContext) -> bool:
    element = their_seq.peek()
    if not (isinstance(element, IS.Element) and element.name.qname == self.qname):
      return False
    ruby_attr = element.get_attribute(style_attrs.Ruby.qname)
    value = ruby_attr.value if ruby_attr is not None else None
    if self.ruby_value is None:
      return value is None or value == "none"
    return value == self.ruby_value

  def pattern(self) -> str:
    if self.ruby_value is None:
      return super().pattern()
    return type(self).__name__.lower()

class Rb(Span):
  """Ruby base content: a `span` with tts:ruby="base"."""
  content_model = ZeroOrMoreRule(AnyRule(Span(), PCDATARule()), mixed_content=True)
  ruby_value = "base"

class Rt(Span):
  """Ruby text content: a `span` with tts:ruby="text"."""
  content_model = ZeroOrMoreRule(AnyRule(Span(), PCDATARule()), mixed_content=True)
  ruby_value = "text"
  applicable_styles = AttributeVocabulary(
    Span.applicable_styles,
    style_attrs.RubyPosition,
  )

class Rp(Span):
  """Ruby fallback delimiter: a `span` with tts:ruby="delimiter"."""
  content_model = ZeroOrMoreRule(AnyRule(Span(), PCDATARule()), mixed_content=True)
  ruby_value = "delimiter"

class Rbc(Span):
  """Ruby base container: a `span` with tts:ruby="baseContainer"."""
  ruby_value = "baseContainer"
  content_model = OneOrMoreRule(Rb())  # rbc : rb+
  applicable_styles = AttributeVocabulary(
    style_attrs.Ruby,
    style_attrs.BackgroundColor,
    style_attrs.Direction,
    style_attrs.Display,
    style_attrs.Visibility,
  )

class Rtc(Span):
  """Ruby text container: a `span` with tts:ruby="textContainer"."""
  ruby_value = "textContainer"
  content_model = AnyRule(  # rtc : rt+ | rp rt+ rp
  OneOrMoreRule(Rt()),
  SequenceRule(Rp(), OneOrMoreRule(Rt()), Rp()),
)
  applicable_styles = AttributeVocabulary(
    style_attrs.Ruby,
    style_attrs.BackgroundColor,
    style_attrs.Direction,
    style_attrs.Display,
    style_attrs.RubyPosition,
    style_attrs.Visibility,
  )

class Ruby(Span):
  """Ruby container: a `span` with tts:ruby="container"."""
  ruby_value = "container"
  content_model = AnyRule(  # ruby : rb rt | rb rp rt rp | rbc rtc rtc?
  SequenceRule(Rb(), Rt()),
  SequenceRule(Rb(), Rp(), Rt(), Rp()),
  SequenceRule(Rbc(), Rtc(), OptionalRule(Rtc())),
)
  applicable_styles = AttributeVocabulary(
    style_attrs.Ruby,
    style_attrs.RubyAlign,
    style_attrs.BackgroundColor,
    style_attrs.Direction,
    style_attrs.Display,
    style_attrs.Visibility,
  )

Span.content_model = SequenceRule(
  ZeroOrMoreRule(Metadata()),
  ZeroOrMoreRule(Set()),
  ZeroOrMoreRule(AnyRule(Ruby(), Span(), Br(), Set(), PCDATARule()), mixed_content=True),
)


class P(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTML, "p")
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLIDAttribute,
    other_attrs.XMLLangAttribute,
    other_attrs.XMLSpaceAttribute,
    TIMING_ATTRIBUTES,
    other_attrs.TimeContainerAttribute,
    other_attrs.RegionAttribute,
    other_attrs.StyleAttribute,
    STYLE_ATTRIBUTES,
    METADATA_ATTRIBUTES,
  )
  applicable_styles = AttributeVocabulary(
    style_attrs.BackgroundColor,
    style_attrs.Direction,
    style_attrs.Display,
    style_attrs.FillLineGap,
    style_attrs.FontFamily,
    style_attrs.FontSize,
    style_attrs.FontStyle,
    style_attrs.FontVariant,
    style_attrs.FontWeight,
    style_attrs.LineHeight,
    style_attrs.LinePadding,
    style_attrs.MultiRowAlign,
    style_attrs.RubyReserve,
    style_attrs.Shear,
    style_attrs.TextAlign,
    style_attrs.UnicodeBidi,
    style_attrs.Visibility,
  )
  content_model = SequenceRule(
    ZeroOrMoreRule(Metadata()),
    ZeroOrMoreRule(Set()),
    ZeroOrMoreRule(AnyRule(Ruby(), Span(), Br(), Set(), PCDATARule()), mixed_content=True),
  )


class Div(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTML, "div")
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLIDAttribute,
    other_attrs.XMLLangAttribute,
    other_attrs.XMLSpaceAttribute,
    TIMING_ATTRIBUTES,
    other_attrs.TimeContainerAttribute,
    other_attrs.RegionAttribute,
    other_attrs.StyleAttribute,
    STYLE_ATTRIBUTES,
    METADATA_ATTRIBUTES,
  )
  applicable_styles = AttributeVocabulary(
    style_attrs.BackgroundColor,
    style_attrs.Display,
    style_attrs.Visibility,
  )
Div.content_model = SequenceRule(
  ZeroOrMoreRule(Metadata()),
  ZeroOrMoreRule(Set()),
  ZeroOrMoreRule(AnyRule(Div(), P()))
)

class Body(IMSCElement):
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTML, "body")
  optional_attributes = AttributeVocabulary(
    other_attrs.XMLIDAttribute,
    other_attrs.XMLLangAttribute,
    other_attrs.XMLSpaceAttribute,
    TIMING_ATTRIBUTES,
    other_attrs.TimeContainerAttribute,
    other_attrs.RegionAttribute,
    other_attrs.StyleAttribute,
    STYLE_ATTRIBUTES,
    METADATA_ATTRIBUTES,
  )
  applicable_styles = AttributeVocabulary(
    style_attrs.BackgroundColor,
    style_attrs.Display,
    style_attrs.Visibility,
  )
Body.content_model = SequenceRule(ZeroOrMoreRule(Metadata()), ZeroOrMoreRule(Set()), ZeroOrMoreRule(Div()))

class TT(IMSCElement):
  content_model: Rule = SequenceRule(OptionalRule(Head()), OptionalRule(Body()))
  qname = ttconv.imsc.validator.namespaces.QName(NS.TTML, "tt")
  optional_attributes = AttributeVocabulary(
    other_attrs.ExtentAttribute,
    other_attrs.XMLLangAttribute,
    other_attrs.XMLIDAttribute,
    other_attrs.XMLSpaceAttribute,
    PARAMETER_ATTRIBUTES
  )

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)
    if e.get_attribute(other_attrs.XMLLangAttribute.qname) is None:
      ctx.event_handler.error("xml:lang attribute missing")

  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    super().validate_contents(element, ctx)

    if ctx.time_base != other_attrs.TimeBase.media:
      ctx.event_handler.error("Time base %s is not supported", ctx.time_base)

    # validate that all referenced styles exist
    for target_id in sorted(ctx.target_style_ids):
      if target_id not in ctx.style_defs:
        ctx.event_handler.error("No referenceable style element with xml:id '%s' exists", target_id)

    # validate that all referenced regions exist
    for target_id in sorted(ctx.target_region_ids):
      if target_id not in ctx.region_ids:
        ctx.event_handler.error("No referenceable region element with xml:id '%s' exists", target_id)

    # validate that all references agents exist
    for target_id in sorted(ctx.target_sig_agent_ids):
      if target_id not in ctx.sig_agent_ids:
        ctx.event_handler.error("No significant agent with xml:id '%s' exists", target_id)

def validate(f: typing.BinaryIO, event_handler: typing.Optional[EventHandler] = None) -> bool:
  '''Validates `f` and returns whether no ERROR-or-above records were logged.'''
  counting_handler = ErrorCountingEventHandler(event_handler)

  data = f.read()

  infoset = IS.Infoset.fromFile(io.BytesIO(data), counting_handler)
  if infoset is None:
    return False

  ctx = IMSCValidationContext(namespaces=infoset.namespaces, event_handler=counting_handler)

  if not TT().match(NodeSequence([infoset.root]), ctx):
    ctx.event_handler.error("Root element must be tt")
    return ctx.event_handler.error_count == 0

  # ttconv's IMSC 1.1 Text Profile filter assumes a valid IMSC 1.1 file
  if ctx.event_handler.error_count == 0:
    try:
      doc = imsc_reader.to_model(ET.parse(io.BytesIO(data)))
      if doc is not None:
        IMSC11TextFilter().process(doc)
    except Exception as e: # pylint: disable=broad-except
      ctx.event_handler.error("%s", e)

  return ctx.event_handler.error_count == 0
