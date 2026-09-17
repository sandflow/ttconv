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

"""TTML Infoset"""

from __future__ import annotations
from dataclasses import dataclass
import typing
import xml.parsers.expat

from ttconv.imsc.validator.event_handler import EventHandler
from ttconv.imsc.namespaces import QName

@dataclass(frozen=True)
class Name:
  """Represents a qualified name"""
  prefix: str | None
  qname: QName

@dataclass(frozen=True)
class Attribute:
  """Represents an attribute in the TTML infoset"""
  name: Name
  value: str

@dataclass
class Text:
  """Represents a text node in the TTML infoset"""
  value: str
  parent: typing.Optional[Element] = None

class Element:
  """Represents an element in the IMSC infoset"""
  def __init__(self, name: Name, parent=None, line_number: typing.Optional[int] = None):
    self.name: Name = name
    self.parent: Element | None = parent
    self.children: typing.List[Element | Text] = []
    self.attributes: typing.Dict[QName, Attribute] = {}
    self.line_number: int | None = line_number

  def get_name(self) -> Name:
    return self.name

  def get_line_number(self) -> typing.Optional[int]:
    return self.line_number

  def add_child(self, child: Element | Text):
    self.children.append(child)
    child.parent = self

  def get_children(self) -> typing.Sequence[Element | Text]:
    return self.children

  def add_attribute(self, attr: Attribute):
    self.attributes[attr.name.qname] = attr

  def get_attribute(self, name: QName) -> Attribute | None:
    return self.attributes.get(name)

  def has_attribute(self, name: QName) -> bool:
    return name in self.attributes

  def get_attributes(self) -> typing.Sequence[Attribute]:
    return list(self.attributes.values())

@dataclass(frozen=True)
class Infoset:
  """Represents a TTML infoset"""
  root: Element
  # maps prefix to the namespace URIs it was bound to
  namespaces: dict[str, list[str]]

  @staticmethod
  def fromFile(f: typing.BinaryIO, event_handler: EventHandler) -> typing.Optional[Infoset]:
    SEP = " "

    def _resolve_name(expat_name: str, ns_map: dict[str, list[str]]) -> Name:
      if SEP in expat_name:
        uri, local = expat_name.split(SEP, 1)
        prefixes = ns_map.get(uri)
        return Name(prefix=prefixes[-1] if prefixes else None, qname=QName(ns=uri, local_name=local))
      return Name(prefix=None, qname=QName(ns=None, local_name=expat_name))

    class _Handler:

      def __init__(self, parser: xml.parsers.expat.XMLParserType):
        self.ns_map: dict[str, list[str]] = {}
        self.prefix_to_uri: dict[str, list[str]] = {}
        self.elem_stack: list[Element] = []
        self.result: Element | None = None
        self.parser: xml.parsers.expat.XMLParserType = parser

      def get_result(self) -> Element | None:
        return self.result

      def start_ns(self, prefix, uri):
        self.ns_map.setdefault(uri, []).append(prefix)
        self.prefix_to_uri.setdefault(prefix, []).append(uri)

      def end_ns(self, prefix):
        uri_stack = self.prefix_to_uri.get(prefix)
        if uri_stack:
          uri = uri_stack.pop()
          ps = self.ns_map.get(uri)
          if ps:
            ps.pop()

      def start(self, tag, attrib):
        elem = Element(_resolve_name(tag, self.ns_map), line_number=self.parser.CurrentLineNumber)
        for name, value in attrib.items():
          elem.add_attribute(Attribute(_resolve_name(name, self.ns_map), value))
        self.elem_stack.append(elem)

      def end(self, _):
        elem = self.elem_stack.pop()
        if self.elem_stack:
          parent = self.elem_stack[-1]
          elem.parent = parent
          parent.children.append(elem)
        else:
          self.result = elem

      def data(self, text):
        if self.elem_stack and text:
          self.elem_stack[-1].children.append(Text(text))

    parser = xml.parsers.expat.ParserCreate(namespace_separator=SEP)
    handler = _Handler(parser)
    parser.StartNamespaceDeclHandler = handler.start_ns
    parser.EndNamespaceDeclHandler = handler.end_ns
    parser.StartElementHandler = handler.start
    parser.EndElementHandler = handler.end
    parser.CharacterDataHandler = handler.data

    try:
      parser.ParseFile(f)
    except xml.parsers.expat.ExpatError as e:
      event_handler.error("XML parse error at line %d: %s", e.lineno, e)
      return None

    r = handler.get_result()
    if r is None:
      event_handler.error("Empty XML document")
      return None
    assert r is not None
    return Infoset(r, handler.prefix_to_uri)

