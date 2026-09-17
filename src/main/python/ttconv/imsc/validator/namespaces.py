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

'''XML namespaces and related utilities'''

from __future__ import annotations

from dataclasses import dataclass

XML = "http://www.w3.org/XML/1998/namespace"
TTML = "http://www.w3.org/ns/ttml"
TTP = "http://www.w3.org/ns/ttml#parameter"
TTS = "http://www.w3.org/ns/ttml#styling"
TTA = "http://www.w3.org/ns/ttml#audio"
TTM = "http://www.w3.org/ns/ttml#metadata"
ITTP = "http://www.w3.org/ns/ttml/profile/imsc1#parameter"
ITTS = "http://www.w3.org/ns/ttml/profile/imsc1#styling"
ITTM = "http://www.w3.org/ns/ttml/profile/imsc1#metadata"
EBUTTS = "urn:ebu:tt:style"
SMPTE = "http://www.smpte-ra.org/schemas/2052-1/2010/smpte-tt"
TTF = "http://www.w3.org/ns/ttml/feature/"
TT_PROFILE = "http://www.w3.org/ns/ttml/profile/"
XLINK = "http://www.w3.org/1999/xlink"
TTE = "http://www.w3.org/ns/ttml/extension/"

@dataclass(frozen=True, order=True)
class QName:
  """Represents a qualified name"""
  ns: str | None
  local_name: str

  def to_clark_name(self):
    """Clark name representation of the qualified name"""
    if self.ns is None:
      return self.local_name
    return f"{{{self.ns}}}{self.local_name}"
  
  @staticmethod
  def from_clark_name(clark_name: str):
    if clark_name.startswith("{"):
        uri, local = clark_name[1:].split("}", 1)
        return QName(ns=uri, local_name=local)
    return QName(ns=None, local_name=clark_name)

  def __str__(self):
    return self.to_clark_name()