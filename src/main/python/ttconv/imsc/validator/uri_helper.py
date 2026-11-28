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

'''RFC 3986 URI reference syntax checks'''

import re
import urllib.parse as URL


def _rfc3986_uri_components() -> dict:
  # pct-encoded = "%" HEXDIG HEXDIG
  pct = r'%[0-9A-Fa-f]{2}'
  # pchar = unreserved / pct-encoded / sub-delims / ":" / "@"
  pc = r"A-Za-z0-9\-._~!$&'()*+,;=:@"   # pchar chars (excluding pct-encoded)
  pchar = f'(?:[{pc}]|{pct})'
  # path productions
  seg    = f'{pchar}*'
  seg_nz = f'{pchar}+'
  path_abempty  = f'(?:/{seg})*'
  path_absolute = f'/(?:{seg_nz}(?:/{seg})*)?'
  path_rootless = f'{seg_nz}(?:/{seg})*'
  # segment-nz-nc = 1*( unreserved / pct-encoded / sub-delims / "@" )
  #   ; non-zero-length segment without any colon ":"
  ncc = r"A-Za-z0-9\-._~!$&'()*+,;=@"
  seg_nz_nc = f'(?:[{ncc}]|{pct})+'
  path_noscheme = f'{seg_nz_nc}(?:/{seg})*'
  # userinfo = *( unreserved / pct-encoded / sub-delims / ":" )
  uc = r"A-Za-z0-9\-._~!$&'()*+,;=:"
  userinfo = f'(?:[{uc}]|{pct})*'
  # reg-name = *( unreserved / pct-encoded / sub-delims )
  rc = r"A-Za-z0-9\-._~!$&'()*+,;="
  reg_name = f'(?:[{rc}]|{pct})*'
  # IPv4address: dec-octet "." dec-octet "." dec-octet "." dec-octet
  dec = r'(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])'
  ipv4 = f'(?:{dec}\\.){{3}}{dec}'
  # IPv6address — all 9 forms from RFC 4291, 2.2
  h16  = r'[0-9A-Fa-f]{1,4}'
  ls32 = f'(?:{h16}:{h16}|{ipv4})'
  ipv6 = '|'.join([
    f'(?:{h16}:){{6}}{ls32}',                                  # form 1
    f'::(?:{h16}:){{5}}{ls32}',                                # form 2
    f'(?:{h16})?::(?:{h16}:){{4}}{ls32}',                     # form 3
    f'(?:(?:{h16}:)?{h16})?::(?:{h16}:){{3}}{ls32}',          # form 4
    f'(?:(?:{h16}:){{,2}}{h16})?::(?:{h16}:){{2}}{ls32}',    # form 5
    f'(?:(?:{h16}:){{,3}}{h16})?::{h16}:{ls32}',              # form 6
    f'(?:(?:{h16}:){{,4}}{h16})?::{ls32}',                    # form 7
    f'(?:(?:{h16}:){{,5}}{h16})?::{h16}',                     # form 8
    f'(?:(?:{h16}:){{,6}}{h16})?::',                          # form 9
  ])
  # IPvFuture = "v" 1*HEXDIG "." 1*( unreserved / sub-delims / ":" )
  fc = r"A-Za-z0-9\-._~!$&'()*+,;=:"
  ipvfuture  = f'[vV][0-9A-Fa-f]+\\.(?:[{fc}])+'
  ip_literal = f'\\[(?:{ipv6}|{ipvfuture})\\]'
  # host / authority
  host      = f'(?:{ip_literal}|{ipv4}|{reg_name})'
  authority = f'(?:{userinfo}@)?{host}(?::[0-9]*)?'
  # query = *( pchar / "/" / "?" )
  qc    = r"A-Za-z0-9\-._~!$&'()*+,;=:@/?"
  query = f'(?:[{qc}]|{pct})*'
  return {
    'authority': authority,
    'path_abempty': path_abempty,
    'path_absolute': path_absolute,
    'path_rootless': path_rootless,
    'path_noscheme': path_noscheme,
    'query': query,
  }

def _build_rfc3986_absolute_uri_re() -> re.Pattern:
  # RFC 3986, 4.3: absolute-URI = scheme ":" hier-part [ "?" query ]
  c = _rfc3986_uri_components()
  hier_part = f'(?://{c["authority"]}{c["path_abempty"]}|{c["path_absolute"]}|{c["path_rootless"]}|)'
  # scheme = ALPHA *( ALPHA / DIGIT / "+" / "-" / "." )
  scheme = r'[A-Za-z][A-Za-z0-9+\-.]*'
  return re.compile(f'^{scheme}:{hier_part}(?:\\?{c["query"]})?$', re.ASCII)

# absolute-URI per RFC 3986, 4.3 (no fragment component)
_RFC3986_ABSOLUTE_URI_RE = _build_rfc3986_absolute_uri_re()


def _build_rfc3986_relative_ref_re() -> re.Pattern:
  # RFC 3986, 4.2: relative-ref = relative-part [ "?" query ] [ "#" fragment ]
  # relative-part = "//" authority path-abempty
  #               / path-absolute / path-noscheme / path-empty
  # fragment shares its character class with query.
  c = _rfc3986_uri_components()
  relative_part = f'(?://{c["authority"]}{c["path_abempty"]}|{c["path_absolute"]}|{c["path_noscheme"]}|)'
  return re.compile(f'^{relative_part}(?:\\?{c["query"]})?(?:#{c["query"]})?$', re.ASCII)

# relative-ref per RFC 3986, 4.2 (a URI reference without a scheme)
_RFC3986_RELATIVE_REF_RE = _build_rfc3986_relative_ref_re()

def _build_rfc3986_uri_re() -> re.Pattern:
  # RFC 3986, 3: URI = scheme ":" hier-part [ "?" query ] [ "#" fragment ]
  # (unlike absolute-URI per 4.3, URI carries an optional fragment component)
  c = _rfc3986_uri_components()
  hier_part = f'(?://{c["authority"]}{c["path_abempty"]}|{c["path_absolute"]}|{c["path_rootless"]}|)'
  # scheme = ALPHA *( ALPHA / DIGIT / "+" / "-" / "." )
  scheme = r'[A-Za-z][A-Za-z0-9+\-.]*'
  return re.compile(f'^{scheme}:{hier_part}(?:\\?{c["query"]})?(?:#{c["query"]})?$', re.ASCII)

# URI per RFC 3986, 3 (a scheme-qualified URI, with an optional fragment)
_RFC3986_URI_RE = _build_rfc3986_uri_re()

def is_relative_uri(uri: str) -> bool:
  """Returns True if value is a syntactically valid relative-ref per RFC 3986"""
  return _RFC3986_RELATIVE_REF_RE.match(uri) is not None

def is_absolute_uri(uri: str) -> bool:
  """Returns True if value is a syntactically valid absolute-URI per RFC 3986"""
  return _RFC3986_ABSOLUTE_URI_RE.match(uri) is not None

def is_uri(uri: str) -> bool:
  """Returns True if value is a syntactically valid URI-reference per RFC
  3986"""
  return _RFC3986_URI_RE.match(uri) is not None or is_relative_uri(uri)

def urijoin(base: str, url: str) -> str:
  '''Joins a url to a base url, preserving the fragment identifier, if any, from the uri.
  '''
  joined = URL.urljoin(base, url)
  if '#' not in url:
    return joined
  return joined.split('#', 1)[0] + '#' + url.split('#', 1)[1]
