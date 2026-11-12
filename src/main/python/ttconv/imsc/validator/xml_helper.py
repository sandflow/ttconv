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

'''XML syntax utilities'''

import re

# NCNameStartChar and NCNameChar per Namespaces in XML 1.0 \u00A73
# (same as NameStartChar / NameChar from XML 1.0 \u00A72.3, minus ':')
_NC_NAME_START = (
  r'[a-zA-Z_\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D'
  r'\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF'
  r'\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF]'
)
_NC_NAME_CHAR = (
  r'[a-zA-Z0-9._\-\u00B7\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF'
  r'\u0300-\u036F\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u203F-\u2040'
  r'\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD'
  r'\U00010000-\U000EFFFF]'
)

_NC_NAME_PAT = _NC_NAME_START + _NC_NAME_CHAR + r'*'

_XML_NAME_RE = re.compile(r'^' + _NC_NAME_PAT + r'$')


def is_valid_xml_name(value: str) -> bool:
  """Returns True if value is a valid NCName per Namespaces in XML 1.0 \u00A73."""
  return _XML_NAME_RE.match(value) is not None


# NameChar per XML 1.0 \u00A72.3, i.e. NCNameChar plus ':'
_XML_NAME_CHAR_RE = re.compile(r'^[:' + _NC_NAME_CHAR[1:] + r'$')


def is_xml_name_char(value: str) -> bool:
  """Returns True if value is a single character matching the NameChar production per XML 1.0 \u00A72.3."""
  return _XML_NAME_CHAR_RE.match(value) is not None


# QName ::= (Prefix ':')? LocalPart   where Prefix and LocalPart are both NCName
_XML_QNAME_RE = re.compile(r'^(?:(' + _NC_NAME_PAT + r'):)?(' + _NC_NAME_PAT + r')$')


def xml_qname_parts(value: str) -> tuple:
  """Returns a (Prefix, LocalPart) tuple for value per QName syntax in Namespaces in XML 1.0.

  Prefix is None if value has no prefix. LocalPart is None if value is not a valid QName.
  """
  m = _XML_QNAME_RE.match(value)
  if m is None:
    return (None, None)
  return (m.group(1), m.group(2))
