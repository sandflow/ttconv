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
    0x01: "sq",
    0x02: "br",
    0x03: "ca",
    0x04: "hr",
    0x05: "cy",
    0x06: "cs",
    0x07: "da",
    0x08: "de",
    0x09: "en",
    0x0A: "es",
    0x0B: "eo",
    0x0C: "et",
    0x0D: "eu",
    0x0E: "fo",
    0x0F: "fr",
    0x10: "fy",
    0x11: "ga",
    0x12: "gd",
    0x13: "gl",
    0x14: "is",
    0x15: "it",
    0x16: "se",
    0x17: "la",
    0x18: "lv",
    0x19: "lb",
    0x1A: "lt",
    0x1B: "hu",
    0x1C: "mt",
    0x1D: "nl",
    0x1E: "no",
    0x1F: "oc",
    0x20: "pl",
    0x21: "pt",
    0x22: "ro",
    0x23: "rm",
    0x24: "sr",
    0x25: "sk",
    0x26: "sl",
    0x27: "fi",
    0x28: "sv",
    0x29: "tr",
    0x2A: "nl",
    0x2B: "wa",
    0x2C: "",
    0x2D: "",
    0x2E: "",
    0x2F: "",
    0x30: "",
    0x31: "",
    0x32: "",
    0x33: "",
    0x34: "",
    0x35: "",
    0x36: "",
    0x37: "",
    0x38: "",
    0x39: "",
    0x3A: "",
    0x3B: "",
    0x3C: "",
    0x3D: "",
    0x3E: "",
    0x3F: "",
    0x7F: "am",
    0x7E: "ar",
    0x7D: "hy",
    0x7C: "as",
    0x7B: "az",
    0x7A: "bm",
    0x79: "be",
    0x78: "bn",
    0x77: "bg",
    0x76: "my",
    0x75: "zh",
    0x74: "cv",
    0x73: "prs",
    0x72: "ff",
    0x71: "ka",
    0x70: "el",
    0x6F: "gu",
    0x6E: "gn",
    0x6D: "ha",
    0x6C: "he",
    0x6B: "hi",
    0x6A: "id",
    0x69: "ja",
    0x68: "kn",
    0x67: "kk",
    0x66: "km",
    0x65: "ko",
    0x64: "lo",
    0x63: "mk",
    0x62: "mg",
    0x61: "ms",
    0x60: "mo",
    0x5F: "mr",
    0x5E: "nd",
    0x5D: "ne",
    0x5C: "or",
    0x5B: "pap",
    0x5A: "fa",
    0x59: "pa",
    0x58: "ps",
    0x57: "qu",
    0x56: "ru",
    0x55: "",
    0x54: "sh",
    0x53: "sn",
    0x52: "si",
    0x51: "so",
    0x50: "srn",
    0x4F: "sw",
    0x4E: "tg",
    0x4D: "ta",
    0x4C: "tt",
    0x4B: "te",
    0x4A: "th",
    0x49: "uk",
    0x48: "ur",
    0x47: "uz",
    0x46: "vi",
    0x45: "zu",
    0x44: "",
    0x43: "",
    0x42: "",
    0x41: "",
    0x40: ""
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

    self.tcp = SmpteTimeCode(
      int(self.fields.TCP[0:2]),
      int(self.fields.TCP[2:4]),
      int(self.fields.TCP[4:6]),
      int(self.fields.TCP[6:8]),
      self.fps
      )

  def get_dsc(self) -> int:
    return ord(self.fields.DSC)

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

  def get_tcp(self) -> SmpteTimeCode:
    return self.tcp

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
