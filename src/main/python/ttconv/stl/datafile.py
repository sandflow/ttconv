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

from numbers import Number
import logging
import typing
import collections
import struct
from fractions import Fraction
import sys

from ttconv import model
import ttconv.style_properties as styles
from ttconv.stl import tf
from ttconv.time_code import SmpteTimeCode

LOGGER = logging.getLogger(__name__)

DEFAULT_HORIZONTAL_SAFE_MARGIN_PCT = 5
DEFAULT_VERTICAL_SAFE_MARGIN_PCT = 10
DEFAULT_TELETEXT_ROWS = 23
DEFAULT_TELETEXT_COLS = 40
DEFAULT_LINE_HEIGHT_PCT = 125
DEFAULT_SINGLE_HEIGHT_FONT_SIZE_PCT = 80
DEFAULT_DOUBLE_HEIGHT_FONT_SIZE_PCT = 160
LINE_PADDING_LENGTH_C = 0.5
DEFAULT_FONT_STACK = ("Verdana", "Arial", "Tiresias", styles.GenericFontFamilyType.sansSerif)

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
  # 0x2C-0x3F have no mappings
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
  # 0x55 (Ruthenian) has no mappings
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
  # 0x44-0x40 are undefined
}

_DFC_FRACTION_MAP = {
  b'STL25.01': Fraction(25),
  b'STL30.01': Fraction(30000, 1001),
  b'STL50.01': Fraction(50)
}

_GSIBlock = collections.namedtuple(
    "GSI",
    ["CPN", "DFC", "DSC", "CCT", "LC", "OPT", "OET", "TPT", "TET", "TN", "TCD", "SLR", "CD", "RD", "RN", \
      "TNB", "TNS", "TNG", "MNC", "MNR", "TCS", "TCP", "TCF", "TND", "DSN", "CO", "PUB", "EN", "ECD", "UDA"]
  )

_TTIBlock = collections.namedtuple(
    "TTI", ["SGN", "SN", "EBN", "CS", "TCIh", "TCIm", "TCIs", "TCIf", "TCOh", "TCOm", "TCOs", "TCOf", "VP", "JC", "CF", "TF"]
  )

def _get_region_from_model(doc: model.ContentDocument, x_origin: Number, y_origin: Number, width: Number, height: Number, display_align: styles.DisplayAlignType):

  found_region = None

  regions = list(doc.iter_regions())

  for r in regions:
    r_origin: styles.CoordinateType = r.get_style(styles.StyleProperties.Origin)
    assert r_origin is not None
    assert r_origin.x.units is styles.LengthType.Units.pct
    assert r_origin.y.units is styles.LengthType.Units.pct
    if r_origin.x.value != x_origin or r_origin.y.value != y_origin:
      continue

    r_extent: styles.ExtentType = r.get_style(styles.StyleProperties.Extent)
    assert r_extent is not None
    assert r_extent.height.units is styles.LengthType.Units.pct
    assert r_extent.width.units is styles.LengthType.Units.pct
    if r_extent.height.value != height or r_extent.width.value != width:
      continue  

    r_display_align: styles.DisplayAlignType = r.get_style(styles.StyleProperties.DisplayAlign)
    assert r_display_align is not None
    if r_display_align != display_align:
      continue

    found_region = r
    break

  if found_region is None:
    found_region = model.Region(f"r{len(regions)}", doc)
    found_region.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        height=styles.LengthType(height, styles.LengthType.Units.pct),
        width=styles.LengthType(width, styles.LengthType.Units.pct),
      )
      )
    found_region.set_style(
      styles.StyleProperties.Origin,
      styles.CoordinateType(
        x=styles.LengthType(x_origin, styles.LengthType.Units.pct),
        y=styles.LengthType(y_origin, styles.LengthType.Units.pct)
      )
    )
    found_region.set_style(
      styles.StyleProperties.DisplayAlign,
      display_align
    )
    doc.put_region(found_region)
  
  return found_region

class DataFile:

  def __init__(
    self,
    gsi_block: bytes,
    disable_fill_line_gap: bool = False,
    disable_line_padding: bool = False,
    start_tc: typing.Optional[str] = None,
    font_stack: typing.Tuple[typing.Union[str, styles.GenericFontFamilyType]] = None
    ):
    
    self.gsi = _GSIBlock._make(
      struct.unpack(
        '3s8sc2s2s32s32s32s32s32s32s16s6s6s2s5s5s3s2s2s1s8s8s1s1s3s32s32s32s75x576s', gsi_block
      )
    )

    self.doc = model.ContentDocument()

    self.doc.set_cell_resolution(
      model.CellResolutionType(
        columns=round(100 * DEFAULT_TELETEXT_COLS / (100 - 2 * DEFAULT_HORIZONTAL_SAFE_MARGIN_PCT)),
        rows=round(100 * DEFAULT_TELETEXT_ROWS / (100 - 2 * DEFAULT_VERTICAL_SAFE_MARGIN_PCT))
      )
    )

    self.body = model.Body(self.doc)
    
    if not disable_fill_line_gap:
      self.body.set_style(
        styles.StyleProperties.FillLineGap,
        True
      )

    if not disable_line_padding:
      self.body.set_style(
        styles.StyleProperties.LinePadding,
        styles.LengthType(
          LINE_PADDING_LENGTH_C,
          styles.LengthType.Units.c
        )
      )

    if font_stack is not None:
      self.body.set_style(
        styles.StyleProperties.FontFamily,
        font_stack
      )
    else:
      self.body.set_style(
        styles.StyleProperties.FontFamily,
        DEFAULT_FONT_STACK
      )

    self.doc.set_body(self.body)

    self.sgn_to_div_map = {}

    self.last_sn = None

    self.is_in_extension = False

    self.tti_tf = None

    self.fps = _DFC_FRACTION_MAP.get(self.gsi.DFC)
    if self.fps is None:
      LOGGER.error("Unknown GSI DFC value %s, defaulting to 25 fps", self.gsi.DFC)
      self.fps = Fraction(25)
    else:
      LOGGER.debug("GSI DFC: %s", self.gsi.DFC)

    self.cct = self.gsi.CCT
    LOGGER.debug("GSI CCT: %s", self.gsi.CCT)

    try:
      self.tti_count = int(self.gsi.TNB)
      LOGGER.debug("GSI TNB: %s", self.gsi.TNB)
    except ValueError:
      LOGGER.error("Invalid TNB field value: %s", self.gsi.TNB)
      self.tti_count = sys.maxsize

    self.language = _LC_BCP47_MAP.get(int(self.gsi.LC))
    if self.language is None:
      LOGGER.warning("Unknown LC value: %s, defaulting to 'unspecified''", self.gsi.LC)
      self.language = ""
    else:
      LOGGER.debug("GSI LC: %s", self.gsi.LC)

    if start_tc is None:
      try:
        self.start_offset = SmpteTimeCode(
            int(self.gsi.TCP[0:2]),
            int(self.gsi.TCP[2:4]),
            int(self.gsi.TCP[4:6]),
            int(self.gsi.TCP[6:8]),
            self.get_fps()
          ).to_temporal_offset()
        LOGGER.debug("GSI TCP: %s", self.gsi.TCP)
      except ValueError:
        LOGGER.error("Invalid TCP value: %s", self.gsi.tcp)
        self.start_offset = 0
    else:
      try:
        self.start_offset = SmpteTimeCode.parse(start_tc, self.get_fps()).to_temporal_offset()
      except ValueError:
        LOGGER.error("Invalid start_tc value")
        raise

    # p_element for use across cumulative subtitles 
    self.cur_p_element = None

  def get_language(self) -> str:
    return self.language

  def get_tti_count(self) -> int:
    return self.tti_count

  def get_fps(self) -> Fraction:
    return self.fps

  def get_cct(self) -> int:
    return self.cct

  def get_document(self):
    return self.doc

  def is_teletext(self):
    return ord(self.gsi.DSC) in (0x31, 0x32)

  def process_tti_block(self, tti_block: bytes):
    if tti_block is None:
      raise ValueError("tti_block should not be None")

    tti = _TTIBlock._make(
      struct.unpack(
        '<BHBBBBBBBBBBBBB112s', tti_block
      )
    )

    LOGGER.debug("Subtitle SN: %s", tti.SN)
    LOGGER.debug("  EBN: %s", tti.EBN)
    LOGGER.debug("  CS: %s", tti.CS)
    LOGGER.debug("  SGN: %s", tti.SGN)
    LOGGER.debug("  JC: %s", tti.JC)
    LOGGER.debug("  VP: %s", tti.VP)

    if 0xEF < tti.EBN < 0xFF:
      # skip user data and reserved blocks
      return

    if not self.is_in_extension:
      self.tti_tf = b''

    self.tti_tf += tti.TF.strip(b'\x8f')

    is_double_height_characters = tf.is_double_height(self.tti_tf)

    # continue accumulating if we have an extension block

    if tti.EBN != 0xFF:
      self.is_in_extension = True
      return

    self.is_in_extension = False

    # apply program offset

    try:
      tci = SmpteTimeCode(tti.TCIh, tti.TCIm, tti.TCIs, tti.TCIf, self.get_fps())
      tco = SmpteTimeCode(tti.TCOh, tti.TCOm, tti.TCOs, tti.TCOf, self.get_fps())
    except ValueError:
      LOGGER.error("Invalid TTI timecode")
      return

    begin_time = tci.to_temporal_offset() - self.start_offset
    if begin_time < 0:
      LOGGER.debug("Skipping subtitle because TCI is less than start time")
      return
    LOGGER.debug("  Time in: %s", tci)

    end_time = tco.to_temporal_offset() - self.start_offset
    if end_time < begin_time:
      LOGGER.error("Subtitle TCO is less than TCI")
      return
    LOGGER.debug("  Time out: %s", tco)

    # create a new subtitle if SN changes and we are not in cumulative mode

    if tti.SN is not self.last_sn and tti.CS in (0x00, 0x01):

      self.last_sn =  tti.SN

      # find the div to which the subtitle belongs, based on SGN

      div_element = self.sgn_to_div_map.get(tti.SGN)

      # create the div if it does not exist

      if div_element is None:
        div_element = model.Div(self.doc)
        self.body.push_child(div_element)
        self.sgn_to_div_map[tti.SGN] = div_element

      # create the p that will hold the subtitle

      self.cur_p_element = model.P(self.doc)

      if tti.JC == 0x01:
        self.cur_p_element.set_style(styles.StyleProperties.TextAlign, styles.TextAlignType.start)
      elif tti.JC == 0x03:
        self.cur_p_element.set_style(styles.StyleProperties.TextAlign, styles.TextAlignType.end)
      else:
        self.cur_p_element.set_style(styles.StyleProperties.TextAlign, styles.TextAlignType.center)

      self.cur_p_element.set_style(
        styles.StyleProperties.LineHeight,
        styles.LengthType(DEFAULT_LINE_HEIGHT_PCT,
        styles.LengthType.Units.pct)
      )

      if self.is_teletext() and not is_double_height_characters:
        font_size = DEFAULT_SINGLE_HEIGHT_FONT_SIZE_PCT
      else:
        font_size = DEFAULT_DOUBLE_HEIGHT_FONT_SIZE_PCT

      self.cur_p_element.set_style(
        styles.StyleProperties.FontSize,
        styles.LengthType(
          font_size,
          styles.LengthType.Units.pct
        )
      )
      if not self.is_teletext():
        # use large region and always align at the bottom for undefined and open subtitles

        region = _get_region_from_model(
          self.doc,
          round(DEFAULT_HORIZONTAL_SAFE_MARGIN_PCT),
          round(DEFAULT_VERTICAL_SAFE_MARGIN_PCT),
          round(100 - 2 * DEFAULT_HORIZONTAL_SAFE_MARGIN_PCT),
          round(100 - 2 * DEFAULT_VERTICAL_SAFE_MARGIN_PCT),
          styles.DisplayAlignType.after
          )

      else:

        safe_area_height =  round(100 - DEFAULT_VERTICAL_SAFE_MARGIN_PCT * 2)
        safe_area_width =  round(100 - DEFAULT_HORIZONTAL_SAFE_MARGIN_PCT * 2)

        # assume that VP < DEFAULT_TELETEXT_ROWS/2 means bottom-aligned and otherwise top-aligned
        # probably should offer an option to override this

        if tti.VP < DEFAULT_TELETEXT_ROWS // 2:
          # top-aligned large region
          
          r_y = DEFAULT_VERTICAL_SAFE_MARGIN_PCT + ((tti.VP - 1) / DEFAULT_TELETEXT_ROWS) * safe_area_height
          r_height = 100 - DEFAULT_VERTICAL_SAFE_MARGIN_PCT - r_y
          
          region = _get_region_from_model(
            self.doc,
            round(DEFAULT_HORIZONTAL_SAFE_MARGIN_PCT),
            r_y,
            safe_area_width,
            r_height,
            styles.DisplayAlignType.before
          )

        else:

          line_count = tf.line_count(self.tti_tf)
          vp = tti.VP
          line_height = 2 if is_double_height_characters else 1

          r_y = DEFAULT_VERTICAL_SAFE_MARGIN_PCT
          r_height = ((vp + line_count * line_height - 1)/ DEFAULT_TELETEXT_ROWS) * safe_area_height
          
          region = _get_region_from_model(
            self.doc,
            round(DEFAULT_HORIZONTAL_SAFE_MARGIN_PCT),
            r_y,
            safe_area_width,
            r_height,
            styles.DisplayAlignType.after
          )

      self.cur_p_element.set_region(region)

      div_element.push_child(self.cur_p_element)

    if tti.CS in (0x01, 0x02, 0x03):
      # create a nested span if we are in cumulative mode
      sub_element = model.Span(self.doc)
      self.cur_p_element.push_child(sub_element)
    else :
      sub_element = self.cur_p_element

    sub_element.set_begin(begin_time)
    sub_element.set_end(end_time)

    LOGGER.debug("  TF: %s", self.tti_tf)

    tf.to_model(sub_element, self.is_teletext(), self.get_cct(), self.tti_tf)

    if tti.CS in (0x01, 0x02):
      sub_element.push_child(model.Br(self.doc))
