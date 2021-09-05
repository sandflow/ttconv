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

"""Processes an EBU STL data file into the canonical model"""

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
  b'00': "",
  b'01': "sq",
  b'02': "br",
  b'03': "ca",
  b'04': "hr",
  b'05': "cy",
  b'06': "cs",
  b'07': "da",
  b'08': "de",
  b'09': "en",
  b'0A': "es",
  b'0B': "eo",
  b'0C': "et",
  b'0D': "eu",
  b'0E': "fo",
  b'0F': "fr",
  b'10': "fy",
  b'11': "ga",
  b'12': "gd",
  b'13': "gl",
  b'14': "is",
  b'15': "it",
  b'16': "se",
  b'17': "la",
  b'18': "lv",
  b'19': "lb",
  b'1A': "lt",
  b'1B': "hu",
  b'1C': "mt",
  b'1D': "nl",
  b'1E': "no",
  b'1F': "oc",
  b'20': "pl",
  b'21': "pt",
  b'22': "ro",
  b'23': "rm",
  b'24': "sr",
  b'25': "sk",
  b'26': "sl",
  b'27': "fi",
  b'28': "sv",
  b'29': "tr",
  b'2A': "nl",
  b'2B': "wa",
  # b'2C'-b'3F' have no mappings
  b'7F': "am",
  b'7E': "ar",
  b'7D': "hy",
  b'7C': "as",
  b'7B': "az",
  b'7A': "bm",
  b'79': "be",
  b'78': "bn",
  b'77': "bg",
  b'76': "my",
  b'75': "zh",
  b'74': "cv",
  b'73': "prs",
  b'72': "ff",
  b'71': "ka",
  b'70': "el",
  b'6F': "gu",
  b'6E': "gn",
  b'6D': "ha",
  b'6C': "he",
  b'6B': "hi",
  b'6A': "id",
  b'69': "ja",
  b'68': "kn",
  b'67': "kk",
  b'66': "km",
  b'65': "ko",
  b'64': "lo",
  b'63': "mk",
  b'62': "mg",
  b'61': "ms",
  b'60': "mo",
  b'5F': "mr",
  b'5E': "nd",
  b'5D': "ne",
  b'5C': "or",
  b'5B': "pap",
  b'5A': "fa",
  b'59': "pa",
  b'58': "ps",
  b'57': "qu",
  b'56': "ru",
  # b'55' (Ruthenian) has no mappings
  b'54': "sh",
  b'53': "sn",
  b'52': "si",
  b'51': "so",
  b'50': "srn",
  b'4F': "sw",
  b'4E': "tg",
  b'4D': "ta",
  b'4C': "tt",
  b'4B': "te",
  b'4A': "th",
  b'49': "uk",
  b'48': "ur",
  b'47': "uz",
  b'46': "vi",
  b'45': "zu",
  # b'44'-b'40' are undefined
}

_DFC_FRACTION_MAP = {
  b'STL23.01': Fraction(24000, 1001),
  b'STL24.01': Fraction(24),
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

def _get_region_from_model(
  doc: model.ContentDocument,
  x_origin: Number,
  y_origin: Number,
  width: Number,
  height: Number,
  display_align: styles.DisplayAlignType
  ):
  """Returns a matching region from `doc` or creates one
  """

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
  """Represents an EBU STL datafile
  """

  def __init__(
    self,
    gsi_block: bytes,
    disable_fill_line_gap: bool = False,
    disable_line_padding: bool = False,
    start_tc: typing.Optional[str] = None,
    font_stack: typing.Tuple[typing.Union[str, styles.GenericFontFamilyType]] = None,
    max_row_count: typing.Optional[typing.Union[int, str]] = None
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

    self.doc.set_active_area(
      model.ActiveAreaType(
        left_offset=DEFAULT_HORIZONTAL_SAFE_MARGIN_PCT / 100,
        top_offset=DEFAULT_VERTICAL_SAFE_MARGIN_PCT / 100,
        width=1 - 2 * DEFAULT_HORIZONTAL_SAFE_MARGIN_PCT / 100,
        height=1 - 2 * DEFAULT_VERTICAL_SAFE_MARGIN_PCT / 100
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

    self.language = _LC_BCP47_MAP.get(self.gsi.LC)
    if self.language is None:
      LOGGER.warning("Unknown LC value: %s, defaulting to 'unspecified''", self.gsi.LC)
      self.language = ""
    else:
      LOGGER.debug("GSI LC: %s", self.gsi.LC)

    self.doc.set_lang(self.language)

    if start_tc is None:
      self.start_offset = 0
    elif start_tc == "TCP":
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

    if max_row_count is None or self.is_teletext():
      self.max_row_count = DEFAULT_TELETEXT_ROWS
    elif isinstance(max_row_count, str) and max_row_count == "MNR":
      try:
        self.max_row_count = int(self.gsi.MNR)
        LOGGER.debug("GSI MNR: %s", self.gsi.MNR)
      except ValueError:
        LOGGER.error("Invalid MNR value: %s", self.gsi.MNR)
        self.start_offset = DEFAULT_TELETEXT_ROWS
    else:
      self.max_row_count = max_row_count

    # p_element for use across cumulative subtitles 
    self.cur_p_element = None

  def get_language(self) -> str:
    """Returns the language of the datafile as an RFC 5646 Language Tag
    """
    return self.language

  def get_tti_count(self) -> int:
    """Returns the number of text blocks in the datafile
    """
    return self.tti_count

  def get_fps(self) -> Fraction:
    """Returns the frame rate of the datafile
    """
    return self.fps

  def get_cct(self) -> int:
    """Returns the codepage of the text fields contained in the datafile
    """
    return self.cct

  def get_document(self):
    """Returns the document instance generated from the datafile
    """
    return self.doc

  def is_teletext(self):
    """Returns whether the datafile contains teletext subtitles or open/undefined subtitles
    """
    return ord(self.gsi.DSC) in (0x31, 0x32)

  def get_max_row_count(self):
    """Returns the maximum number of rows
    """
    return self.max_row_count

  def process_tti_block(self, tti_block: bytes):
    """Processes a single TTI block
    """
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

    is_double_height_characters = tf.has_double_height_char(self.tti_tf)

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

      safe_area_height =  round(100 - DEFAULT_VERTICAL_SAFE_MARGIN_PCT * 2)
      safe_area_width =  round(100 - DEFAULT_HORIZONTAL_SAFE_MARGIN_PCT * 2)

      # assume that VP < max number of rows/2 means bottom-aligned and otherwise top-aligned
      # probably should offer an option to override this

      if tti.VP < self.get_max_row_count() // 2:
        # top-aligned large region
        
        r_y = DEFAULT_VERTICAL_SAFE_MARGIN_PCT + ((tti.VP - 1) / self.get_max_row_count()) * safe_area_height
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

        line_count = tf.line_count(self.tti_tf, is_double_height_characters)
        vp = tti.VP
        line_height = 2 if is_double_height_characters else 1

        r_y = DEFAULT_VERTICAL_SAFE_MARGIN_PCT
        r_height = ((vp + line_count * line_height - 1)/ self.get_max_row_count()) * safe_area_height
        
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
