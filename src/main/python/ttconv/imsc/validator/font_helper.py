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

'''tts:fontFamily <font-families> syntax checks, per TTML2, 10.3.16'''

import re

# <whitespace> per TTML2, 10.3.41
_WSP = r'[ \t\n\r]'

# <lwsp> per TTML2, 10.3.23
_LWSP = _WSP + r'+'

# escape ::= "\" char , per TTML2, 10.3.15 /, 8.3.13
_ESCAPE = r'\\.'

# non-ascii-or-c1 ::= [^\0-\237] per TTML2, 10.3.15, i.e. any character
# outside of the ASCII and C1 control ranges
_NON_ASCII_OR_C1 = r'\u00A0-\U0010FFFF'

# identifier-start / identifier-following / identifier, per TTML2, 10.3.15
_IDENTIFIER_START = r'(?:[A-Za-z_' + _NON_ASCII_OR_C1 + r']|' + _ESCAPE + r')'
_IDENTIFIER_FOLLOWING = r'(?:[A-Za-z0-9_\-' + _NON_ASCII_OR_C1 + r']|' + _ESCAPE + r')'
_IDENTIFIER = r'-?' + _IDENTIFIER_START + _IDENTIFIER_FOLLOWING + r'*'

# unquoted-string ::= identifier (<lwsp> identifier)* , per TTML2, 10.3.15, extended
# to allow zero or more leading/trailing <wsp>, as permitted for "font-family" by
# XSL 1.1, 7.9.2 (https://www.w3.org/TR/2006/REC-xsl11-20061205/#font-family), which
# cites the CSS2 "font-family" property that TTML2's <family-name> grammar derives from
_UNQUOTED_STRING = _WSP + r'*' + _IDENTIFIER + r'(?:' + _LWSP + _IDENTIFIER + r')*' + _WSP + r'*'

# <quoted-string> per TTML2, 8.3.13
_DOUBLE_QUOTED_STRING = r'"(?:[^"\\]|' + _ESCAPE + r')*"'
_SINGLE_QUOTED_STRING = r"'(?:[^'\\]|" + _ESCAPE + r")*'"
_QUOTED_STRING = r'(?:' + _DOUBLE_QUOTED_STRING + r'|' + _SINGLE_QUOTED_STRING + r')'

# <family-name> ::= unquoted-string | <quoted-string> , per TTML2, 10.3.15
# <generic-family-name> (10.3.19) is itself a single identifier, and so is
# already matched by unquoted-string; <font-family> therefore reduces to <family-name>
_FONT_FAMILY = r'(?:' + _UNQUOTED_STRING + r'|' + _QUOTED_STRING + r')'

# <font-families> ::= font-family (<lwsp>? "," <lwsp>? font-family)* , per TTML2, 10.3.16
_OPTIONAL_LWSP = r'(?:' + _LWSP + r')?'
_FONT_FAMILIES_RE = re.compile(
  r'^' + _FONT_FAMILY + r'(?:' + _OPTIONAL_LWSP + r',' + _OPTIONAL_LWSP + _FONT_FAMILY + r')*$'
)

# matches quoted-string tokens, so they can be excluded when checking for the
# "leading double hyphen" restriction on unquoted identifiers below
_QUOTED_STRING_RE = re.compile(_QUOTED_STRING)

# a <family-name> that takes the form of an unquoted-string containing an
# identifier that starts with two HYPHEN-MINUS (U+002D) characters is invalid,
# per TTML2, 10.3.15
_LEADING_DOUBLE_HYPHEN_RE = re.compile(r'(?:^|(?<=[, \t\n\r]))--')


def is_quoted_string(value: str) -> bool:
  """Returns True if value is exactly a <quoted-string> expression, per TTML2, 8.3.13"""
  return _QUOTED_STRING_RE.fullmatch(value) is not None


def is_valid_font_families(value: str) -> bool:
  """Returns True if value is a valid <font-families> expression, per TTML2,
  10.3.16"""
  if _FONT_FAMILIES_RE.match(value) is None:
    return False

  # a <family-name> that takes the form of a quoted-string with no content
  # between the delimiting quotes does not denote a usable font family name
  if any(len(m.group()) == 2 for m in _QUOTED_STRING_RE.finditer(value)):
    return False

  unquoted_only = _QUOTED_STRING_RE.sub('', value)
  return _LEADING_DOUBLE_HYPHEN_RE.search(unquoted_only) is None


