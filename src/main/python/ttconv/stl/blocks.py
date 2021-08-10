#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2021, Sandflow Consulting LLC
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

import collections
import struct
import logging
from fractions import Fraction
from ttconv.time_code import SmpteTimeCode 


LOGGER = logging.getLogger(__name__)

class GSI:
  _BLOCK_DEF = collections.namedtuple(
      "GSI",
      ["CPN", "DFC", "DSC", "CCT", "LC", "OPT", "OET", "TPT", "TET", "TN", "TCD", "SLR", "CD", "RD", "RN", \
        "TNB", "TNS", "TNG", "MNC", "MNR", "TCS", "TCP", "TCF", "TND", "DSN", "CO", "PUB", "EN", "ECD", "UDA"]
    )

  _LC_BCP47_MAP = {
    0x00: "",
    0x08: "de",
    0x09: "en",
    0x0A: "es",
    0x0F: "fr",
    0x15: "it",
    0x21: "pt"
  }

  def __init__(self, block: bytes):

    self.fields = GSI._BLOCK_DEF._make(
      struct.unpack(
        '3s8sc2s2s32s32s32s32s32s32s16s6s6s2s5s5s3s2s2s1s8s8s1s1s3s32s32s32s75x576s', block
      )
    )

    if self.fields.DFC == b'STL25.01':
      self.fps = Fraction(25)
    elif self.fields.DFC == b'STL30.01':
      self.fps = Fraction(30000, 1001)
    elif self.fields.DFC == b'STL50.01':
      self.fps = Fraction(50)
      LOGGER.warning("Non-standard 50 fps frame rate")
    else:
      LOGGER.error("Unknown frame rate %s, defaulting to 25 fps", self.fields.DFC)
      self.fps = Fraction(25)

    self.cct = self.fields.CCT


    self.mnr = int(self.fields.MNR)

    self.block_count = int(self.fields.TNB)

    self.language = GSI._LC_BCP47_MAP.get(self.fields.LC, "")

  def get_dsc(self) -> int:
    return self.fields.DSC

  def get_language(self) -> str:
    return self.language

  def get_block_count(self) -> int:
    return self.block_count

  def get_mnr(self) -> int:
    return self.mnr

  def get_fps(self) -> Fraction:
    return self.fps

  def get_cct(self) -> int:
    return self.cct

class TTI:
  _BLOCK_DEF = collections.namedtuple(
    "TTI", ["SGN", "SN", "EBN", "CS", "TCIh", "TCIm", "TCIs", "TCIf", "TCOh", "TCOm", "TCOs", "TCOf", "VP", "JC", "CF", "TF"]
  )

  def __init__(self, gsi: GSI, block: bytes):
    self.fields = self._BLOCK_DEF._make(
      struct.unpack(
        '<BHBBBBBBBBBBBBB112s', block
      )
    )

    self.ebn = self.fields.EBN
    self.tf = self.fields.TF
    self.sn = self.fields.SN
    self.sgn = int(self.fields.SGN)
    self.cs = self.fields.CS
    self.tci = SmpteTimeCode(self.fields.TCIh, self.fields.TCIm, self.fields.TCIs, self.fields.TCIf, gsi.get_fps())
    self.tco = SmpteTimeCode(self.fields.TCOh, self.fields.TCOm, self.fields.TCOs, self.fields.TCOf, gsi.get_fps())
    self.jc = self.fields.JC
    self.vp = self.fields.VP

  def get_ebn(self) -> int:
    return self.ebn

  def get_tf(self) -> bytes:
    return self.tf

  def get_sn(self) -> int:
    return self.sn

  def get_sgn(self) -> int:
    return self.sgn

  def get_cs(self) -> int:
    return self.cs

  def get_tci(self) -> SmpteTimeCode:
    return self.tci

  def get_tco(self) -> SmpteTimeCode:
    return self.tco

  def get_jc(self) -> int:
    return self.jc

  def get_vp(self) -> int:
    return self.vp
