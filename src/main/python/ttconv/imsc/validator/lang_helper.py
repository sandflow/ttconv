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

'''RFC 5646 language tag syntax checks'''

import re

# RFC 5646, 2.1 — all grandfathered tags (stored lowercase for case-insensitive lookup)
_RFC5646_GRANDFATHERED = {
  # irregular
  "en-gb-oed", "i-ami", "i-bnn", "i-default", "i-enochian", "i-hak",
  "i-klingon", "i-lux", "i-mingo", "i-navajo", "i-pwn", "i-tao",
  "i-tay", "i-tsu", "sgn-be-fr", "sgn-be-nl", "sgn-ch-de",
  # regular
  "art-lojban", "cel-gaulish", "no-bok", "no-nyn", "zh-guoyu",
  "zh-hakka", "zh-min", "zh-min-nan", "zh-xiang",
}

# langtag per RFC 5646, 2.1 (well-formedness only, no registry check)
#   language  = 2*3ALPHA ["-" extlang] / 4ALPHA / 5*8ALPHA
#   extlang   = 3ALPHA *2("-" 3ALPHA)
#   script    = 4ALPHA
#   region    = 2ALPHA / 3DIGIT
#   variant   = 5*8alphanum / DIGIT 3alphanum
#   extension = singleton 1*("-" 2*8alphanum)   singleton ≠ "x"
#   privateuse = "x" 1*("-" 1*8alphanum)
_RFC5646_LANGTAG_RE = re.compile(
  r'^(?:[a-z]{2,3}(?:-[a-z]{3}){0,3}|[a-z]{4}|[a-z]{5,8})'  # language [extlang]
  r'(?:-[a-z]{4})?'                                            # script
  r'(?:-(?:[a-z]{2}|[0-9]{3}))?'                              # region
  r'(?:-(?:[a-z0-9]{5,8}|[0-9][a-z0-9]{3}))*'                # *variant
  r'(?:-[0-9a-wy-z](?:-[a-z0-9]{2,8})+)*'                    # *extension
  r'(?:-x(?:-[a-z0-9]{1,8})+)?$',                             # privateuse
  re.IGNORECASE | re.ASCII
)

_RFC5646_PRIVATEUSE_RE = re.compile(
  r'^x(?:-[a-z0-9]{1,8})+$',
  re.IGNORECASE | re.ASCII
)


def is_valid_language_tag(value: str) -> bool:
  """Returns True if value is a well-formed language tag per RFC 5646."""
  if value.lower() in _RFC5646_GRANDFATHERED:
    return True
  if _RFC5646_PRIVATEUSE_RE.match(value):
    return True
  return _RFC5646_LANGTAG_RE.match(value) is not None


def get_primary_language_subtag(value: str) -> str:
  """Returns the primary language subtag (the portion before the first "-"),
  lowercased, of an RFC 5646 language tag."""
  return value.split("-", 1)[0].lower()
