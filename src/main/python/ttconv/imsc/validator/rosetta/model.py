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


'''Validator for [IMSC Rosetta](https://github.com/imsc-rosetta/).
'''

from __future__ import annotations
from dataclasses import dataclass, field
import datetime
import io
import re
import typing

from ttconv.imsc.namespaces import QName
import ttconv.imsc.namespaces as NS
from ttconv.imsc.validator.attribute_vocabulary import AttributeVocabulary, attribute
from ttconv.imsc.validator.event_handler import EventHandler
import ttconv.imsc.validator.imsc11_model as imsc11
from ttconv.imsc.validator.imsc11_model import ErrorCountingEventHandler, IMSCElement, IMSCValidationContext
import ttconv.imsc.validator.infoset as IS
import ttconv.imsc.validator.other_attributes as other_attrs
from ttconv.imsc.validator.rosetta.infoset import RosettaInfoset
import ttconv.imsc.validator.rosetta.styles as styles
import ttconv.imsc.validator.style_attributes as style_attrs
from ttconv.imsc.validator.rules import AnyRule, EmptyRule, NodeSequence, OneOrMoreRule, PCDATARule, Rule, SequenceRule, UnorderedRule, ZeroOrMoreRule

ROSETTA = "https://github.com/imsc-rosetta/specification"

FORMAT_NAME = "rosetta-imsc"
FORMAT_VERSION = "0.0.0"

# maps the namespaces used in a Rosetta document to their mandatory prefix (`None` for the default namespace)
REQUIRED_PREFIXES: typing.Dict[str, typing.Optional[str]] = {
  NS.TTML: None,
  NS.TTM: "ttm",
  NS.TTS: "tts",
  NS.TTP: "ttp",
  NS.XML: "xml",
  NS.EBUTTS: "ebutts",
  NS.ITTS: "itts",
  ROSETTA: "rosetta",
}

# maps outline/dropshadow `span` styles to the corresponding `div` style that must be present
SPAN_OUTLINE_STYLES = {
  "s_outlineblack": "d_outline",
  "s_outlinered": "d_outline",
  "s_outlineyellow": "d_outline",
  "s_outlinegreen": "d_outline",
  "s_outlinecyan": "d_outline",
  "s_outlineblue": "d_outline",
  "s_outlinemagenta": "d_outline",
  "s_outlinewhite": "d_outline",

  "s_dropblack": "d_drop",
  "s_dropred": "d_drop",
  "s_dropyellow": "d_drop",
  "s_dropgreen": "d_drop",
  "s_dropcyan": "d_drop",
  "s_dropblue": "d_drop",
  "s_dropmagenta": "d_drop",
  "s_dropwhite": "d_drop",

  "s_noneblack": "d_none",
  "s_nonered": "d_none",
  "s_noneyellow": "d_none",
  "s_nonegreen": "d_none",
  "s_nonecyan": "d_none",
  "s_noneblue": "d_none",
  "s_nonemagenta": "d_none",
  "s_nonewhite": "d_none",
}

# exactly one of these is referenced by a ruby container
RUBY_ALIGN_STYLES = frozenset(("s_rb_algn_center", "s_rb_algn_around"))
RUBY_BASE_STYLE = "s_rb_b"
RUBY_TEXT_STYLE = "s_rb_t"
RUBY_STYLES = RUBY_ALIGN_STYLES | {"s_rb_posn_outside", RUBY_BASE_STYLE, RUBY_TEXT_STYLE}

_TIME_RE = re.compile(r"(\d{2}):([0-5]\d):([0-5]\d)\.(\d{3})")

def _parse_time_ms(value: str) -> int:
  '''Parses a time expression in HH:MM:SS.TTT format and returns it in milliseconds'''
  m = _TIME_RE.fullmatch(value)
  if m is None:
    raise ValueError("Time expression `%s` is not in HH:MM:SS.TTT format" % value)
  h, mn, s, ms = (int(g) for g in m.groups())
  return ((h * 60 + mn) * 60 + s) * 1000 + ms

@dataclass
class RosettaValidationContext(IMSCValidationContext):
  # namespace declarations found on the root element
  root_namespaces: typing.Dict[typing.Optional[str], str] = field(default_factory=dict)

@attribute
class BeginAttribute:
  '''begin attribute, restricted to HH:MM:SS.TTT'''
  qname = QName(None, "begin")

  @staticmethod
  def validate(value: str, _ctx):
    _parse_time_ms(value)

@attribute
class EndAttribute:
  '''end attribute, restricted to HH:MM:SS.TTT'''
  qname = QName(None, "end")

  @staticmethod
  def validate(value: str, _ctx):
    _parse_time_ms(value)

@attribute
class CommentAttribute:
  '''rosetta:comment attribute'''
  qname = QName(ROSETTA, "comment")

  @staticmethod
  def validate(_value: str, _ctx):
    pass

class RosettaElement(IMSCElement):
  '''Rosetta elements accept no attributes and no child elements other than those in their content model'''

  non_foreign_namespaces = None

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    # namespace prefixes are mandated by the specification
    for name in [e.get_name()] + [a.name for a in e.get_attributes()]:
      if name.qname.ns is None or name.qname.ns == NS.XML:
        continue
      expected = REQUIRED_PREFIXES.get(name.qname.ns)
      if name.qname.ns in REQUIRED_PREFIXES and name.prefix != expected:
        ctx.event_handler.error("Namespace %s must use the prefix `%s` on <%s> (line %s)", name.qname.ns,
          expected or "(default)", e.get_name().qname.local_name, e.get_line_number())
    super().validate_attributes(e, ctx)

def _get_referenced_style_ids(e: IS.Element) -> typing.List[str]:
  sa = e.get_attribute(other_attrs.StyleAttribute.qname)
  return other_attrs.StyleAttribute.parse(sa.value) if sa is not None else []

def _validate_applicable_styles_by_prefix(e: IS.Element, ctx: IMSCValidationContext, prefixes: typing.Tuple[str, ...]):
  '''Checks that the styles referenced by `e` may be applied to it'''
  for style_id in _get_referenced_style_ids(e):
    if style_id and not style_id.startswith(prefixes):
      ctx.event_handler.error("Style `%s` shall not be referenced by <%s> (line %s)", style_id, e.get_name().qname.local_name, e.get_line_number())

def _get_child_elements_by_qname(e: IS.Element, qname: QName) -> typing.List[IS.Element]:
  return [c for c in e.get_children() if isinstance(c, IS.Element) and c.name.qname == qname]

BOXED_STYLES = frozenset((
  "ps_bg_boxedblack", "ps_bg_boxedred", "ps_bg_boxedyellow", "ps_bg_boxedgreen",
  "ps_bg_boxedcyan", "ps_bg_boxedblue", "ps_bg_boxedmagenta", "ps_bg_boxedwhite",
))

GHOST_BOXED_STYLES = frozenset((
  "ps_bg_ghostboxedblack", "ps_bg_ghostboxedred", "ps_bg_ghostboxedyellow", "ps_bg_ghostboxedgreen",
  "ps_bg_ghostboxedcyan", "ps_bg_ghostboxedblue", "ps_bg_ghostboxedmagenta", "ps_bg_ghostboxedwhite",
))

BOXING_STYLES = BOXED_STYLES | GHOST_BOXED_STYLES

def _has_boxing(e: IS.Element) -> bool:
  '''Returns whether `e` references a boxed or ghost boxed style'''
  return not BOXING_STYLES.isdisjoint(_get_referenced_style_ids(e))

class MetadataTextElement(RosettaElement):
  '''A Rosetta metadata element that contains only text, which is unconstrained unless `check_text()` is overridden'''
  content_model = PCDATARule()

  def check_text(self, text: str) -> typing.Optional[str]:
    '''Returns the requirement that `text` does not meet, or `None` if it does'''
    return None

  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    super().validate_contents(element, ctx)
    text = "".join(c.value for c in element.get_children() if isinstance(c, IS.Text))
    problem = self.check_text(text)
    if problem is not None:
      ctx.event_handler.error("rosetta:%s %s (line %s)", self.qname.local_name, problem, element.get_line_number())

class Format(MetadataTextElement):
  qname = QName(ROSETTA, "format")

  def check_text(self, text: str) -> typing.Optional[str]:
    return None if text == FORMAT_NAME else f"shall be `{FORMAT_NAME}`"

class Version(MetadataTextElement):
  qname = QName(ROSETTA, "version")

  def check_text(self, text: str) -> typing.Optional[str]:
    return None if text == FORMAT_VERSION else f"shall be `{FORMAT_VERSION}`"

class EnumeratedElement(MetadataTextElement):
  '''An element whose text is one of `values`'''
  values: typing.Tuple[str, ...] = ()

  def check_text(self, text: str) -> typing.Optional[str]:
    return None if text in self.values else "shall be one of " + ", ".join(f"`{v}`" for v in self.values)

class Role(EnumeratedElement):
  qname = QName(ROSETTA, "role")
  values = ("SDH", "translationonly", "translationwithforced", "forcedonly")

class OriginalFormat(EnumeratedElement):
  qname = QName(ROSETTA, "originalFormat")
  values = ("EBUSTL", "OpenSTL", "SRT", "FPC", "PAC", "890", "CAP", "SMPTE2052", "EBUTT", "IMSC1.0")

class TimeElement(MetadataTextElement):
  '''An element whose text is a time in HH:MM:SS.TTT format'''

  def check_text(self, text: str) -> typing.Optional[str]:
    try:
      _parse_time_ms(text)
    except ValueError:
      return "shall be in HH:MM:SS.TTT format"
    return None

class StartOfProgramme(TimeElement):
  qname = QName(ROSETTA, "startOfProgramme")

class StartOfMedia(TimeElement):
  qname = QName(ROSETTA, "startOfMedia")

_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:[0-5]\d:[0-5]\d\.\d{3}Z")

class DateElement(MetadataTextElement):
  '''An element whose text is a UTC date and time in YYYY-MM-DDTHH:MM:SS.SSSZ format'''

  def check_text(self, text: str) -> typing.Optional[str]:
    if _DATE_RE.fullmatch(text) is not None:
      try:
        datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%fZ")
        return None
      except ValueError:
        pass
    return "shall be a UTC date and time in YYYY-MM-DDTHH:MM:SS.SSSZ format"

class Created(DateElement):
  qname = QName(ROSETTA, "created")

class Modified(DateElement):
  qname = QName(ROSETTA, "modified")

class Originator(MetadataTextElement):
  qname = QName(ROSETTA, "originator")

class TransformationProduct(MetadataTextElement):
  qname = QName(ROSETTA, "transformationProduct")

class TransformationProductVersion(MetadataTextElement):
  qname = QName(ROSETTA, "transformationProductVersion")

class ForeignElement(imsc11.ForeignElement):
  '''An element in a namespace that is neither a TTML one nor the Rosetta one'''

  def is_instance(self, their_seq: NodeSequence, ctx: IMSCValidationContext) -> bool:
    return super().is_instance(their_seq, ctx) and their_seq.peek().name.qname.ns != ROSETTA

class HeadMetadata(RosettaElement):
  '''`metadata` as a child of `head`. Elements in the Rosetta namespace are constrained by
  https://github.com/imsc-rosetta/imsc-rosetta-specification/blob/main/documents/metadata.md, elements in other
  namespaces are custom metadata, and are not validated. The TTML metadata elements permitted by IMSC 1.1 are also allowed.
  The order of elements is not significant.'''
  qname = QName(NS.TTML, "metadata")
  content_model = UnorderedRule(
    (Format(), 1, 1),
    (Version(), 1, 1),
    (Role(), 0, 1),
    (StartOfProgramme(), 0, 1),
    (StartOfMedia(), 0, 1),
    (Created(), 0, 1),
    (Modified(), 0, 1),
    (Originator(), 0, 1),
    (OriginalFormat(), 0, 1),
    (TransformationProduct(), 0, 1),
    (TransformationProductVersion(), 0, 1),
    (imsc11.Agent(), 0, None),
    (imsc11.Name(), 0, None),
    (imsc11.Actor(), 0, None),
    (imsc11.Copyright(), 0, None),
    (imsc11.Desc(), 0, None),
    (imsc11.Title(), 0, None),
    (imsc11.Item(), 0, None),
    (imsc11.AltText(), 0, None),
    (ForeignElement(), 0, None),
  )

  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    if self.content_model.match_all(NodeSequence(element.get_children(), non_foreign_ns=self.non_foreign_namespaces), ctx):
      return

    # the content model does not say what is wrong, so look for the usual suspects
    line = element.get_line_number()
    problems: typing.List[typing.Tuple[str, ...]] = []

    rosetta_entries = [(rule, lo, hi) for rule, lo, hi in self.content_model.entries
                       if isinstance(rule, RosettaElement) and rule.qname.ns == ROSETTA]

    known = {rule.qname for rule, _, _ in rosetta_entries}
    for c in element.get_children():
      if isinstance(c, IS.Element) and c.name.qname.ns == ROSETTA and c.name.qname not in known:
        problems.append(("Unknown element <rosetta:%s> in <metadata> (line %s)", c.name.qname.local_name, c.get_line_number()))

    for rule, lo, hi in rosetta_entries:
      count = len(_get_child_elements_by_qname(element, rule.qname))
      if count < lo or (hi is not None and count > hi):
        bound = ("exactly", lo) if lo == hi else ("at least", lo) if count < lo else ("at most", hi)
        problems.append(("<metadata> shall contain %s %s <rosetta:%s>, found %s (line %s)",
                         bound[0], "one" if bound[1] == 1 else bound[1], rule.qname.local_name, count, line))

    if not problems:
      problems.append(("%s contents does not match %s (line %s)", self.pattern(), self.content_model.pattern(), line))

    for msg, *args in problems:
      ctx.event_handler.error(msg, *args)

class Style(RosettaElement, imsc11.Style):
  content_model = EmptyRule()
  required_attributes = AttributeVocabulary(other_attrs.XMLIDAttribute)
  optional_attributes = AttributeVocabulary(imsc11.STYLE_ATTRIBUTES, other_attrs.StyleAttribute)

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)

    xml_id = e.get_attribute(other_attrs.XMLIDAttribute.qname)
    if xml_id is None:
      return

    line = e.get_line_number()
    validator = styles.STYLE_VALIDATORS.get(xml_id.value)
    if validator is None:
      ctx.event_handler.error("Style `%s` is not defined by the specification (line %s)", xml_id.value, line)
      return

    values = {a.name.qname: a.value for a in e.get_attributes() if a.name.qname != other_attrs.XMLIDAttribute.qname}
    validator.validate(xml_id.value, values, line, ctx.event_handler)

class Styling(RosettaElement, imsc11.Styling):
  content_model = OneOrMoreRule(Style())
  optional_attributes = AttributeVocabulary()

  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    super().validate_contents(element, ctx)
    if styles.QUANTISATION_REGION_STYLE not in ctx.style_defs:
      ctx.event_handler.error("Style `%s` shall be present (line %s)", styles.QUANTISATION_REGION_STYLE, element.get_line_number())

class Region(RosettaElement, imsc11.Region):
  content_model = EmptyRule()
  required_attributes = AttributeVocabulary(
    other_attrs.XMLIDAttribute,
    style_attrs.Origin,
    style_attrs.Extent,
    style_attrs.DisplayAlign,
    other_attrs.StyleAttribute,
  )
  optional_attributes = AttributeVocabulary()

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)
    if e.has_attribute(other_attrs.StyleAttribute.qname) and \
        set(_get_referenced_style_ids(e)) not in ({"r_default"}, {"r_default", "r_vertical"}):
      ctx.event_handler.error("style on <region> shall be `r_default` or `r_default r_vertical` (line %s)", e.get_line_number())

class Layout(RosettaElement, imsc11.Layout):
  content_model = OneOrMoreRule(Region())
  optional_attributes = AttributeVocabulary()

class Head(RosettaElement, imsc11.Head):
  content_model = SequenceRule(HeadMetadata(), Styling(), Layout())
  optional_attributes = AttributeVocabulary()

class Br(RosettaElement):
  qname = QName(NS.TTML, "br")
  content_model = EmptyRule()

class TextSpan(RosettaElement):
  '''A `span` that contains only text'''
  qname = imsc11.Span.qname
  content_model = PCDATARule()
  optional_attributes = AttributeVocabulary(other_attrs.StyleAttribute)
  applicable_styles = imsc11.Span.applicable_styles

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)
    _validate_applicable_styles_by_prefix(e, ctx, ("s_", "ps_"))

  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    super().validate_contents(element, ctx)
    if not RUBY_STYLES.isdisjoint(_get_referenced_style_ids(element)):
      ctx.event_handler.error("Ruby styles shall only be used on <span> elements that contain ruby (line %s)", element.get_line_number())

class BrOnlySpan(RosettaElement):
  '''A `span` that contains a single `br`, and has no attributes'''
  qname = imsc11.Span.qname
  content_model = Br()
  optional_attributes = AttributeVocabulary()

  def is_instance(self, their_seq: NodeSequence, ctx: IMSCValidationContext) -> bool:
    return super().is_instance(their_seq, ctx) and len(_get_child_elements_by_qname(their_seq.peek(), Br.qname)) > 0

class RubyPart(RosettaElement):
  '''A `span` that contains only text, and references `style_id`. Either the base or the text of a ruby container.'''
  qname = imsc11.Span.qname
  content_model = PCDATARule()
  required_attributes = AttributeVocabulary(other_attrs.StyleAttribute)
  applicable_styles = imsc11.Span.applicable_styles
  style_id: str

  def is_instance(self, their_seq: NodeSequence, ctx: IMSCValidationContext) -> bool:
    return super().is_instance(their_seq, ctx) and self.style_id in _get_referenced_style_ids(their_seq.peek())

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)
    _validate_applicable_styles_by_prefix(e, ctx, ("s_", "ps_"))

  def pattern(self):
    return f"{self.qname.local_name}[{self.style_id}]"

class RubyBase(RubyPart):
  '''A `span` that contains the base of a ruby container'''
  style_id = RUBY_BASE_STYLE

class RubyText(RubyPart):
  '''A `span` that contains the text of a ruby container'''
  style_id = RUBY_TEXT_STYLE

class RubySpan(RosettaElement):
  '''A `span` that references exactly one of `RUBY_ALIGN_STYLES`, and contains a ruby base and a ruby text, in any order'''
  qname = imsc11.Span.qname
  content_model = UnorderedRule((RubyBase(), 1, 1), (RubyText(), 1, 1))
  required_attributes = AttributeVocabulary(other_attrs.StyleAttribute)
  applicable_styles = AttributeVocabulary(
    imsc11.Span.applicable_styles,
    style_attrs.RubyAlign,
    style_attrs.RubyPosition,
  )

  def is_instance(self, their_seq: NodeSequence, ctx: IMSCValidationContext) -> bool:
    return super().is_instance(their_seq, ctx) and \
      len(RUBY_ALIGN_STYLES.intersection(_get_referenced_style_ids(their_seq.peek()))) == 1

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)
    _validate_applicable_styles_by_prefix(e, ctx, ("s_", "ps_"))

class P(RosettaElement):
  qname = QName(NS.TTML, "p")
  required_attributes = AttributeVocabulary(other_attrs.StyleAttribute)
  applicable_styles = imsc11.P.applicable_styles
  content_model = ZeroOrMoreRule(AnyRule(BrOnlySpan(), RubySpan(), TextSpan()))

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)
    if e.has_attribute(other_attrs.StyleAttribute.qname) and not {"p_font1", "p_font2"} & set(_get_referenced_style_ids(e)):
      ctx.event_handler.error("style on <p> shall contain p_font1 or p_font2 (line %s)", e.get_line_number())
    _validate_applicable_styles_by_prefix(e, ctx, ("p_", "ps_"))

  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    # whitespace is significant since xml:space is preserve and mixed_content is `False`
    if any(isinstance(c, IS.Text) for c in element.get_children()):
      ctx.event_handler.error("<p> shall not contain text or whitespace outside of <span> (line %s)", element.get_line_number())
    super().validate_contents(element, ctx)

class DivMetadata(RosettaElement):
  '''`metadata` as a child of `div`'''
  qname = QName(NS.TTML, "metadata")
  content_model = EmptyRule()
  required_attributes = AttributeVocabulary(CommentAttribute)

class Div(RosettaElement):
  qname = QName(NS.TTML, "div")
  required_attributes = AttributeVocabulary(
    other_attrs.XMLIDAttribute,
    other_attrs.RegionAttribute,
    BeginAttribute,
    EndAttribute,
    other_attrs.StyleAttribute,
  )
  applicable_styles = imsc11.Div.applicable_styles
  content_model = ZeroOrMoreRule(AnyRule(DivMetadata(), P()))

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)
    line = e.get_line_number()

    xml_id = e.get_attribute(other_attrs.XMLIDAttribute.qname)
    if xml_id is not None and not xml_id.value.startswith("e_"):
      ctx.event_handler.error("xml:id of <div> shall start with `e_` (line %s)", line)

    if e.has_attribute(other_attrs.StyleAttribute.qname) and "d_default" not in _get_referenced_style_ids(e):
      ctx.event_handler.error("style on <div> shall contain d_default (line %s)", line)
    _validate_applicable_styles_by_prefix(e, ctx, ("d_",))

    begin = e.get_attribute(BeginAttribute.qname)
    end = e.get_attribute(EndAttribute.qname)
    if begin is not None and end is not None:
      try:
        if _parse_time_ms(begin.value) >= _parse_time_ms(end.value):
          ctx.event_handler.error("begin shall precede end on <div> (line %s)", line)
      except ValueError:
        pass # already reported when validating each attribute

  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    super().validate_contents(element, ctx)
    line = element.get_line_number()

    # s_outlinexxx, s_dropxxx and s_nonexxx require d_outline, d_drop and d_none, respectively, to be referenced directly by
    # the `style` of the `div` or of `_d_default`, and outline and dropshadow cannot be mixed
    in_effect = set(_get_referenced_style_ids(element))
    d_default = ctx.style_defs.get("_d_default")
    if d_default is not None:
      in_effect |= d_default.style_refs
    used = set()
    for span in (e for e in element.dfs_iterator() if e.name.qname == imsc11.Span.qname):
      for style_id in _get_referenced_style_ids(span):
        required = SPAN_OUTLINE_STYLES.get(style_id)
        if required is None:
          continue
        used.add(required)
        if required not in in_effect:
          ctx.event_handler.error("Style `%s` shall not be used on <span> unless `%s` is specified in `_d_default` or on <div> (line %s)",
            style_id, required, span.get_line_number())
    if {"d_outline", "d_drop"} <= used:
      ctx.event_handler.error("Outline and dropshadow styles shall not be mixed in a <div> (line %s)", line)

    # boxing (ps_bg_xxx on every base level <span>) and striping (ps_bg_xxx on every <p>) are applied consistently
    paragraphs = _get_child_elements_by_qname(element, P.qname)

    boxed = any(BOXED_STYLES.intersection(_get_referenced_style_ids(e)) for p in paragraphs for e in p.dfs_iterator())
    ghost = any(GHOST_BOXED_STYLES.intersection(_get_referenced_style_ids(e)) for p in paragraphs for e in p.dfs_iterator())
    if boxed and ghost:
      ctx.event_handler.error("ps_bg_boxedxxx and ps_bg_ghostboxedxxx styles shall not be mixed in a <div> (line %s)", line)

    if any(_has_boxing(p) for p in paragraphs) and not all(_has_boxing(p) for p in paragraphs):
      ctx.event_handler.error("A ps_bg_xxx style shall be applied to every <p> of a <div> if it is applied to one (line %s)", line)

    base_spans = [(p, s) for p in paragraphs for s in _get_child_elements_by_qname(p, imsc11.Span.qname) if not _get_child_elements_by_qname(s, Br.qname)]
    if any(_has_boxing(s) for _, s in base_spans) and any(not _has_boxing(s) and not _has_boxing(p) for p, s in base_spans):
      ctx.event_handler.error("A ps_bg_xxx style shall be applied to every base level <span> of a <div> if it is applied to one (line %s)", line)

class Body(RosettaElement):
  qname = QName(NS.TTML, "body")
  content_model = OneOrMoreRule(Div())

class TT(RosettaElement, imsc11.TT):
  content_model = SequenceRule(Head(), Body())
  required_attributes = AttributeVocabulary(
    other_attrs.TimeBaseAttribute,
    other_attrs.CellResolutionAttribute,
    other_attrs.XMLSpaceAttribute,
    other_attrs.FrameRateAttribute,
    other_attrs.FrameRateMultiplierAttribute,
    other_attrs.XMLLangAttribute,
  )
  optional_attributes = AttributeVocabulary()

  def validate_attributes(self, e: IS.Element, ctx: IMSCValidationContext):
    super().validate_attributes(e, ctx)
    line = e.get_line_number()

    time_base = e.get_attribute(other_attrs.TimeBaseAttribute.qname)
    if time_base is not None and time_base.value != "media":
      ctx.event_handler.error("timeBase on <tt> shall be `media` (line %s)", line)

    cell_resolution = e.get_attribute(other_attrs.CellResolutionAttribute.qname)
    if cell_resolution is not None and cell_resolution.value != "30 15":
      ctx.event_handler.error("cellResolution on <tt> shall be `30 15` (line %s)", line)

    xml_space = e.get_attribute(other_attrs.XMLSpaceAttribute.qname)
    if xml_space is not None and xml_space.value != "preserve":
      ctx.event_handler.error("space on <tt> shall be `preserve` (line %s)", line)

    assert isinstance(ctx, RosettaValidationContext)
    for uri, prefix in REQUIRED_PREFIXES.items():
      if ctx.root_namespaces.get(prefix) != uri:
        ctx.event_handler.error("<tt> shall declare %s (line %s)",
          f"xmlns:{prefix}=\"{uri}\"" if prefix else f"xmlns=\"{uri}\"", line)

  def validate_contents(self, element: IS.Element, ctx: IMSCValidationContext):
    super().validate_contents(element, ctx)

    # so that subtitles do not move depending on whether ruby is present, every <p> of a document that uses ruby references
    # p_rb_res_outside
    elements = list(element.dfs_iterator())
    if any(e.name.qname == imsc11.Span.qname and len(RUBY_ALIGN_STYLES.intersection(_get_referenced_style_ids(e))) == 1 for e in elements):
      for p in (e for e in elements if e.name.qname == P.qname):
        if "p_rb_res_outside" not in _get_referenced_style_ids(p):
          ctx.event_handler.error("style on <p> shall contain p_rb_res_outside since the document contains ruby (line %s)", p.get_line_number())

def _validate_imscr(f: typing.BinaryIO, event_handler: typing.Optional[EventHandler] = None) -> bool:
  '''Validates the constraints that IMSC Rosetta adds to IMSC 1.1, and returns whether no ERROR-or-above records were logged.

  `f` is not validated against IMSC 1.1, and the results are only meaningful for a valid IMSC 1.1 document. Use `validate()`
  unless that is known to be the case.'''
  counting_handler = ErrorCountingEventHandler(event_handler)

  infoset = RosettaInfoset.fromFile(f, counting_handler)
  if infoset is None:
    return False

  if infoset.xml_declaration is None:
    counting_handler.error("The XML declaration is missing")
  else:
    version, encoding, standalone = infoset.xml_declaration
    if version != "1.0":
      counting_handler.error("XML declaration version shall be `1.0`, not `%s`", version)
    if encoding is None or encoding.upper() != "UTF-8":
      counting_handler.error("XML declaration encoding shall be `UTF-8`, not `%s`", encoding)
    if standalone != 1:
      counting_handler.error("XML declaration standalone shall be `yes`")

  ctx = RosettaValidationContext(
    namespaces=infoset.namespaces,
    root_namespaces=infoset.root_namespaces,
    event_handler=counting_handler
  )

  if not TT().match(NodeSequence([infoset.root]), ctx):
    ctx.event_handler.error("Root element must be tt")

  return counting_handler.error_count == 0

def validate(f: typing.BinaryIO, event_handler: typing.Optional[EventHandler] = None) -> bool:
  '''Validates `f` and returns whether no ERROR-or-above records were logged.

  `f` must be a valid IMSC 1.1 document, and validation stops at the first failure of the IMSC 1.1 model.'''
  data = f.read()

  if not imsc11.validate(io.BytesIO(data), event_handler):
    return False

  return _validate_imscr(io.BytesIO(data), event_handler)
