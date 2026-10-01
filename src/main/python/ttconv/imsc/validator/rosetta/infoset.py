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


"""Infoset that exposes the XML constructs that are constrained by IMSC Rosetta"""

from __future__ import annotations
from dataclasses import dataclass, field
import typing

import ttconv.imsc.validator.infoset as IS

@dataclass(frozen=True)
class RosettaInfoset(IS.Infoset):
  '''An infoset that also exposes the XML declaration and the namespace declarations of the root element'''

  # maps prefix (`None` for the default namespace) to the namespace URI declared on the root element
  root_namespaces: typing.Dict[typing.Optional[str], str] = field(default_factory=dict)
  # (version, encoding, standalone) of the XML declaration, or `None` if absent. standalone is -1 if unspecified.
  xml_declaration: typing.Optional[typing.Tuple[str, typing.Optional[str], int]] = None

  class _Handler(IS.Infoset._Handler):
    def __init__(self, parser):
      super().__init__(parser)
      self.root_namespaces: typing.Dict[typing.Optional[str], str] = {}
      self.xml_declaration: typing.Optional[typing.Tuple[str, typing.Optional[str], int]] = None
      parser.XmlDeclHandler = self.xml_decl

    def xml_decl(self, version, encoding, standalone):
      self.xml_declaration = (version, encoding, standalone)

    def start_ns(self, prefix, uri):
      # namespace declarations precede the start of the element on which they are declared
      if not self.elem_stack:
        self.root_namespaces[prefix] = uri
      super().start_ns(prefix, uri)

  @classmethod
  def _from_handler(cls, handler: RosettaInfoset._Handler) -> RosettaInfoset:
    assert handler.result is not None
    return cls(handler.result, handler.prefix_to_uri, handler.root_namespaces, handler.xml_declaration)
