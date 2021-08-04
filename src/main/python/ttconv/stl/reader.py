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

"""STL reader"""

from __future__ import annotations

import logging
import typing
import collections
import struct
import itertools
import codecs
import io
from fractions import Fraction

from ttconv.time_code import SmpteTimeCode 
from ttconv import model
import ttconv.style_properties as styles
from ttconv.stl.config import STLReaderConfiguration


LOGGER = logging.getLogger(__name__)


GSIBlock = collections.namedtuple(
  "GSI",
  ["CPN", "DFC", "DSC", "CCT", "LC", "OPT", "OET", "TPT", "TET", "TN", "TCD", "SLR", "CD", "RD", "RN", \
    "TNB", "TNS", "TNG", "MNC", "MNR", "TCS", "TCP", "TCF", "TND", "DSN", "CO", "PUB", "EN", "ECD", "UDA"]
)

TTIBlock = collections.namedtuple(
  "TTI",
  ["SGN", "SN", "EBN", "CS", "TCIh", "TCIm", "TCIs", "TCIf", "TCOh", "TCOm", "TCOs", "TCOf", "VP", "JC", "CF", "TF"]
)

# from https://bugs.python.org/file45750/iso6937.py
CCT0_DECODE_MAP = {
    b'\xa0': '\u00A0',  # NO-BREAK SPACE
    b'\xa1': '\u00A1',  # ¡
    b'\xa2': '\u00A2',  # ¢
    b'\xa3': '\u00A3',  # £
    # b'\xa4'
    b'\xa5': '\u00A5',  # ¥
    # b'\xa6'
    b'\xa7': '\u00A7',  # §
    b'\xa8': '\u00A4',  # ¤
    b'\xa9': '\u2018',  # ‘
    b'\xaa': '\u201C',  # “
    b'\xab': '\u00AB',  # «
    b'\xac': '\u2190',  # ←
    b'\xad': '\u2191',  # ↑
    b'\xae': '\u2192',  # →
    b'\xaf': '\u2193',  # ↓
    b'\xb0': '\u00B0',  # °
    b'\xb1': '\u00B1',  # ±
    b'\xb2': '\u00B2',  # ²
    b'\xb3': '\u00B3',  # ³
    b'\xb4': '\u00D7',  # ×
    b'\xb5': '\u00B5',  # µ
    b'\xb6': '\u00B6',  # ¶
    b'\xb7': '\u00B7',  # ·
    b'\xb8': '\u00F7',  # ÷
    b'\xb9': '\u2019',  # ’
    b'\xba': '\u201D',  # ”
    b'\xbb': '\u00BB',  # »
    b'\xbc': '\u00BC',  # ¼
    b'\xbd': '\u00BD',  # ½
    b'\xbe': '\u00BE',  # ¾
    b'\xbf': '\u00BF',  # ¿
    # b'\xc0'
    # b'\xc1'
    # b'\xc2'
    # b'\xc3'
    # b'\xc4'
    # b'\xc5'
    # b'\xc6'
    # b'\xc7'
    # b'\xc8'
    # '\xc9
    # b'\xca'
    # b'\xcb'
    # '\xcc
    # b'\xcd'
    # b'\xce'
    # b'\xcf'
    b'\xd0': '\u2014',  # —
    b'\xd1': '\u00B9',  # ¹
    b'\xd2': '\u00AE',  # ®
    b'\xd3': '\u00A9',  # ©
    b'\xd4': '\u2122',  # ™
    b'\xd5': '\u266A',  # ♪
    b'\xd6': '\u00AC',  # ¬
    b'\xd7': '\u00A6',  # ¦
    # b'\xd8'
    # b'\xd9'
    # b'\xda'
    # b'\xdb'
    b'\xdc': '\u215B',  # ⅛
    b'\xdd': '\u215C',  # ⅜
    b'\xde': '\u215D',  # ⅝
    b'\xdf': '\u215E',  # ⅞
    b'\xe0': '\u2126',  # Ω
    b'\xe1': '\u00C6',  # Æ
    b'\xe2': '\u00D0',  # Ð
    b'\xe3': '\u00AA',  # ª
    b'\xe4': '\u0126',  # Ħ
    # b'\xe5'
    b'\xe6': '\u0132',  # Ĳ
    b'\xe7': '\u013F',  # Ŀ
    b'\xe8': '\u0141',  # Ł
    b'\xe9': '\u00D8',  # Ø
    b'\xea': '\u0152',  # Œ
    b'\xeb': '\u00BA',  # º
    b'\xec': '\u00DE',  # Þ
    b'\xed': '\u0166',  # Ŧ
    b'\xee': '\u014A',  # Ŋ
    b'\xef': '\u0149',  # ŉ
    b'\xf0': '\u0138',  # ĸ
    b'\xf1': '\u00E6',  # æ
    b'\xf2': '\u0111',  # đ
    b'\xf3': '\u00F0',  # ð
    b'\xf4': '\u0127',  # ħ
    b'\xf5': '\u0131',  # ı
    b'\xf6': '\u0133',  # ĳ
    b'\xf7': '\u0140',  # ŀ
    b'\xf8': '\u0142',  # ł
    b'\xf9': '\u00F8',  # ø
    b'\xfa': '\u0153',  # œ
    b'\xfb': '\u00DF',  # ß
    b'\xfc': '\u00FE',  # þ
    b'\xfd': '\u0167',  # ŧ
    b'\xfe': '\u014B',  # ŋ
    b'\xff': '\u00AD',  # SOFT HYPHEN

    b'\xc1A': '\u00C0',  # À
    b'\xc1E': '\u00C8',  # È
    b'\xc1I': '\u00CC',  # Ì
    b'\xc1O': '\u00D2',  # Ò
    b'\xc1U': '\u00D9',  # Ù
    b'\xc1a': '\u00E0',  # à
    b'\xc1e': '\u00E8',  # è
    b'\xc1i': '\u00EC',  # ì
    b'\xc1o': '\u00F2',  # ò
    b'\xc1u': '\u00F9',  # ù

    b'\xc2 ': '\u00B4',  # ´
    b'\xc2A': '\u00C1',  # Á
    b'\xc2C': '\u0106',  # Ć
    b'\xc2E': '\u00C9',  # É
    b'\xc2I': '\u00CD',  # Í
    b'\xc2L': '\u0139',  # Ĺ
    b'\xc2N': '\u0143',  # Ń
    b'\xc2O': '\u00D3',  # Ó
    b'\xc2R': '\u0154',  # Ŕ
    b'\xc2S': '\u015A',  # Ś
    b'\xc2U': '\u00DA',  # Ú
    b'\xc2Y': '\u00DD',  # Ý
    b'\xc2Z': '\u0179',  # Ź
    b'\xc2a': '\u00E1',  # á
    b'\xc2c': '\u0107',  # ć
    b'\xc2e': '\u00E9',  # é
    b'\xc2g': '\u0123',  # ģ
    b'\xc2i': '\u00ED',  # í
    b'\xc2l': '\u013A',  # ĺ
    b'\xc2n': '\u0144',  # ń
    b'\xc2o': '\u00F3',  # ó
    b'\xc2r': '\u0155',  # ŕ
    b'\xc2s': '\u015B',  # ś
    b'\xc2u': '\u00FA',  # ú
    b'\xc2y': '\u00FD',  # ý
    b'\xc2z': '\u017A',  # ź

    b'\xc3A': '\u00C2',  # Â
    b'\xc3C': '\u0108',  # Ĉ
    b'\xc3E': '\u00CA',  # Ê
    b'\xc3G': '\u011C',  # Ĝ
    b'\xc3H': '\u0124',  # Ĥ
    b'\xc3I': '\u00CE',  # Î
    b'\xc3J': '\u0134',  # Ĵ
    b'\xc3O': '\u00D4',  # Ô
    b'\xc3S': '\u015C',  # Ŝ
    b'\xc3U': '\u00DB',  # Û
    b'\xc3W': '\u0174',  # Ŵ
    b'\xc3Y': '\u0176',  # Ŷ
    b'\xc3a': '\u00E2',  # â
    b'\xc3c': '\u0109',  # ĉ
    b'\xc3e': '\u00EA',  # ê
    b'\xc3g': '\u011D',  # ĝ
    b'\xc3h': '\u0125',  # ĥ
    b'\xc3i': '\u00EE',  # î
    b'\xc3j': '\u0135',  # ĵ
    b'\xc3o': '\u00F4',  # ô
    b'\xc3s': '\u015D',  # ŝ
    b'\xc3u': '\u00FB',  # û
    b'\xc3w': '\u0175',  # ŵ
    b'\xc3y': '\u0177',  # ŷ

    b'\xc4A': '\u00C3',  # Ã
    b'\xc4I': '\u0128',  # Ĩ
    b'\xc4N': '\u00D1',  # Ñ
    b'\xc4O': '\u00D5',  # Õ
    b'\xc4U': '\u0168',  # Ũ
    b'\xc4a': '\u00E3',  # ã
    b'\xc4i': '\u0129',  # ĩ
    b'\xc4n': '\u00F1',  # ñ
    b'\xc4o': '\u00F5',  # õ
    b'\xc4u': '\u0169',  # ũ

    b'\xc5 ': '\u00AF',  # ¯
    b'\xc5A': '\u0100',  # Ā
    b'\xc5E': '\u0112',  # Ē
    b'\xc5I': '\u012A',  # Ī
    b'\xc5O': '\u014C',  # Ō
    b'\xc5U': '\u016A',  # Ū
    b'\xc5a': '\u0101',  # ā
    b'\xc5e': '\u0113',  # ē
    b'\xc5i': '\u012B',  # ī
    b'\xc5o': '\u014D',  # ō
    b'\xc5u': '\u016B',  # ū

    b'\xc6 ': '\u02D8',  # ˘
    b'\xc6A': '\u0102',  # Ă
    b'\xc6G': '\u011E',  # Ğ
    b'\xc6U': '\u016C',  # Ŭ
    b'\xc6a': '\u0103',  # ă
    b'\xc6g': '\u011F',  # ğ
    b'\xc6u': '\u016D',  # ŭ

    b'\xc7 ': '\u02D9',  # ˙
    b'\xc7C': '\u010A',  # Ċ
    b'\xc7E': '\u0116',  # Ė
    b'\xc7G': '\u0120',  # Ġ
    b'\xc7I': '\u0130',  # İ
    b'\xc7Z': '\u017B',  # Ż
    b'\xc7c': '\u010B',  # ċ
    b'\xc7e': '\u0117',  # ė
    b'\xc7g': '\u0121',  # ġ
    b'\xc7z': '\u017C',  # ż

    b'\xc8 ': '\u00A8',  # ¨
    b'\xc8A': '\u00C4',  # Ä
    b'\xc8E': '\u00CB',  # Ë
    b'\xc8I': '\u00CF',  # Ï
    b'\xc8O': '\u00D6',  # Ö
    b'\xc8U': '\u00DC',  # Ü
    b'\xc8Y': '\u0178',  # Ÿ
    b'\xc8a': '\u00E4',  # ä
    b'\xc8e': '\u00EB',  # ë
    b'\xc8i': '\u00EF',  # ï
    b'\xc8o': '\u00F6',  # ö
    b'\xc8u': '\u00FC',  # ü
    b'\xc8y': '\u00FF',  # ÿ

    b'\xca ': '\u02DA',  # ˚
    b'\xcaA': '\u00C5',  # Å
    b'\xcaU': '\u016E',  # Ů
    b'\xcaa': '\u00E5',  # å
    b'\xcau': '\u016F',  # ů

    b'\xcb ': '\u00B8',  # ¸
    b'\xcbC': '\u00C7',  # Ç
    b'\xcbG': '\u0122',  # Ģ
    b'\xcbK': '\u0136',  # Ķ
    b'\xcbL': '\u013B',  # Ļ
    b'\xcbN': '\u0145',  # Ņ
    b'\xcbR': '\u0156',  # Ŗ
    b'\xcbS': '\u015E',  # Ş
    b'\xcbT': '\u0162',  # Ţ
    b'\xcbc': '\u00E7',  # ç
    b'\xcbg': '\u0123',  # ģ
    b'\xcbk': '\u0137',  # ķ
    b'\xcbl': '\u013C',  # ļ
    b'\xcbn': '\u0146',  # ņ
    b'\xcbr': '\u0157',  # ŗ
    b'\xcbs': '\u015F',  # ş
    b'\xcbt': '\u0163',  # ţ

    b'\xcd ': '\u02DD',  # ˝
    b'\xcdO': '\u0150',  # Ő
    b'\xcdU': '\u0170',  # Ű
    b'\xcdo': '\u0151',  # ő
    b'\xcdu': '\u0171',  # ű

    b'\xce ': '\u02DB',  # ˛
    b'\xceA': '\u0104',  # Ą
    b'\xceE': '\u0118',  # Ę
    b'\xceI': '\u012E',  # Į
    b'\xceU': '\u0172',  # Ų
    b'\xcea': '\u0105',  # ą
    b'\xcee': '\u0119',  # ę
    b'\xcei': '\u012F',  # į
    b'\xceu': '\u0173',  # ų

    b'\xcf ': '\u02C7',  # ˇ
    b'\xcfC': '\u010C',  # Č
    b'\xcfD': '\u010E',  # Ď
    b'\xcfE': '\u011A',  # Ě
    b'\xcfL': '\u013D',  # Ľ
    b'\xcfN': '\u0147',  # Ň
    b'\xcfR': '\u0158',  # Ř
    b'\xcfS': '\u0160',  # Š
    b'\xcfT': '\u0164',  # Ť
    b'\xcfZ': '\u017D',  # Ž
    b'\xcfc': '\u010D',  # č
    b'\xcfd': '\u010F',  # ď
    b'\xcfe': '\u011B',  # ě
    b'\xcfl': '\u013E',  # ľ
    b'\xcfn': '\u0148',  # ň
    b'\xcfr': '\u0159',  # ř
    b'\xcfs': '\u0161',  # š
    b'\xcft': '\u0165',  # ť
    b'\xcfz': '\u017E',  # ž
}

_REPLACEMENT_CHAR = 	"�"

_UNUSED_SPACE_CODE = 0x8F

def is_character_code(c) -> bool:
  return 0x20 <= c <= 0x7F or 0xA0 <= c <= 0xFF

def is_printable_code(c) -> bool:
  return is_character_code(c) and c != 0x20
 
def is_control_code(c) -> bool:
  return 0x00 <= c <= 0x07 or 0x0A <= c <= 0x0D or 0x1C <= c <= 0x1D or 0x80 <= c <= 0x85

def is_newline_code(c) -> bool:
  return c == 0x8A

def is_unused_space_code(c) -> bool:
  return c == _UNUSED_SPACE_CODE

def is_space_code(c) -> bool:
  return c == 0x20

def is_lwsp_code(c) -> bool:
  return is_control_code(c) or is_newline_code(c) or is_space_code(c)

def iso6937_decode_func(bytes_buf, errors):
  # pylint: disable=unused-argument
  s = io.StringIO()

  i = 0
  while i < len(bytes_buf):
    if 0x20 <= bytes_buf[i] <= 0x7E:
      s.write(chr(bytes_buf[i]))
      i += 1
    elif 0xC1 <= bytes_buf[i] <= 0xCF:
      b = bytes(bytes_buf[i:i+2])
      c = CCT0_DECODE_MAP.get(b)
      if c is not None:
        s.write(c)
      else:
        s.write(_REPLACEMENT_CHAR)
        LOGGER.warning("Unknown character sequence: %s", str(b))
      i += 2
    else:
      b = bytes(bytes_buf[i:i+1])
      c = CCT0_DECODE_MAP.get(b)
      if c is not None:
        s.write(c)
      else:
        s.write(_REPLACEMENT_CHAR)
        LOGGER.warning("Unknown character: %s", str(b))
      i += 1

  return (s.getvalue(), len(bytes_buf))

def note_decode_error(error):
  LOGGER.warning("Unknown character: %s", hex(error.object[error.start]))
  return (_REPLACEMENT_CHAR, error.end)

codecs.register_error("note", note_decode_error)

def process_tti_tf(element: model.ContentElement, tti_cct, tti_tf):
  
  fg_color = styles.NamedColors.white.value

  bg_color = styles.NamedColors.transparent.value

  is_italic = False

  is_underline = False

  span_element = None

  text_buffer = bytearray()

  tf_i = 0

  if tti_cct == b'00':
    decode_func = iso6937_decode_func
  elif tti_cct == b'01':
    decode_func = codecs.getdecoder("iso8859_5")
  elif tti_cct == b'02':
    decode_func = codecs.getdecoder("iso8859_6")
  elif tti_cct == b'03':
    decode_func = codecs.getdecoder("iso8859_7")
  elif tti_cct == b'04':
    decode_func = codecs.getdecoder("iso8859_8")
  else:
    raise NotImplementedError

  def peek_next_char() -> int:
    return _UNUSED_SPACE_CODE if tf_i >= len(tti_tf) else tti_tf[tf_i + 1]

  def peek_prev_char() -> int:
    return _UNUSED_SPACE_CODE if tf_i <= 0 else tti_tf[tf_i - 1]

  def next_char() -> int:
    nonlocal tf_i
    c = peek_next_char()
    tf_i = min(tf_i + 1, len(tti_tf))
    return c

  def cur_char() -> int:
    return _UNUSED_SPACE_CODE if tf_i >= len(tti_tf) else tti_tf[tf_i]

  def start_span():
    nonlocal span_element
    nonlocal bg_color
    nonlocal fg_color
    nonlocal is_underline
    nonlocal is_italic

    if span_element is None:
      span_element = model.Span(element.get_doc())
      span_element.set_style(styles.StyleProperties.BackgroundColor, bg_color)
      span_element.set_style(styles.StyleProperties.Color, fg_color)
      if is_underline:
        span_element.set_style(
          styles.StyleProperties.TextDecoration,
          styles.TextDecorationType(underline=True)
        )
      if is_italic:
        span_element.set_style(
          styles.StyleProperties.FontStyle,
          styles.FontStyleType.italic
        )

  def end_span():
    nonlocal span_element

    if len(text_buffer) > 0 and span_element is not None:
      text_element = model.Text(element.get_doc())
      text_element.set_text(decode_func(text_buffer, errors="note")[0])

      span_element.push_child(text_element)
      element.push_child(span_element)
      span_element = None
      text_buffer.clear()

  def append_character(c):
    if c != 0x20 or (is_printable_code(peek_next_char()) and is_printable_code(peek_prev_char())):
      start_span()
      text_buffer.append(c)

  def new_line():
    if not is_newline_code(peek_next_char()) and not is_unused_space_code(peek_next_char()):
      end_span()
      element.push_child(model.Br(element.get_doc()))
      start_span()

  while True:

    c = cur_char()

    if is_unused_space_code(c):
      break

    if is_character_code(c):
      # start_span()
      append_character(c)

    elif is_newline_code(c):
      new_line()

    elif is_control_code(c):
      end_span()

      if c in (0x84, 0x0B, 0x1C):
        bg_color = styles.NamedColors.black.value
      elif c == 0x85:
        bg_color = styles.NamedColors.transparent.value
      elif c == 0x1D:
        bg_color = fg_color
      elif c == 0x00:
        fg_color = styles.NamedColors.black.value
      elif c == 0x01:
        fg_color = styles.NamedColors.red.value
      elif c == 0x02:
        fg_color = styles.NamedColors.lime.value
      elif c == 0x03:
        fg_color = styles.NamedColors.yellow.value
      elif c == 0x04:
        fg_color = styles.NamedColors.blue.value
      elif c == 0x05:
        fg_color = styles.NamedColors.magenta.value
      elif c == 0x06:
        fg_color = styles.NamedColors.cyan.value
      elif c == 0x07:
        fg_color = styles.NamedColors.white.value
      elif c == 0x80:
        is_italic = True
      elif c == 0x81:
        is_italic = False
      elif c == 0x82:
        is_underline = True
      elif c == 0x83:
        is_underline = False

      append_character(0x20)

    next_char()

  end_span()


#
# STL reader
#

def to_model(stl_document: typing.IO, _config: typing.Optional[STLReaderConfiguration] = None, progress_callback=lambda _: None):
  """Converts an STL document to the data model"""

  gsi_block = GSIBlock._make(
    struct.unpack(
      '3s8sc2s2s32s32s32s32s32s32s16s6s6s2s5s5s3s2s2s1s8s8s1s1s3s32s32s32s75x576s',
      stl_document.read(1024)
    )
  )

  if gsi_block.DFC == b'STL25.01':
    gsi_fps = Fraction(25)
  elif gsi_block.DFC == b'STL30.01':
    gsi_fps = Fraction(30000, 1001)
  elif gsi_block.DFC == b'STL50.01':
    gsi_fps = Fraction(50)
    LOGGER.warning("Non-standard 50 fps frame rate")
  else:
    LOGGER.error("Unknown frame rate %s, defaulting to 25 fps", gsi_block.DFC)
    gsi_fps = Fraction(25)

  gsi_cct = gsi_block.CCT

  # language code LC

  # max number of rows

  if gsi_block.DSC in (0x31, 0x32):
    # teletext
    gsi_mnr = 23
  else:
    # open or undefined
    gsi_mnr = int(gsi_block.MNR)

  tti_block_count = int(gsi_block.TNB)

  doc = model.ContentDocument()

  # assume 44x23 character matrix within a ‘Subtitle Safe Area’ of ~90% of the width and ~80% height of the related video object
  doc.set_cell_resolution(
    model.CellResolutionType(
      columns=44,
      rows=29)
  )

  body = model.Body(doc)
  doc.set_body(body)

  sgn_map = {}

  region_map = {}

  last_sn = None

  is_in_extension = False

  tti_tf = b''

  for i in itertools.count():
    
    buf = stl_document.read(128)

    if not buf:
      break

    tti_block = TTIBlock._make(
      struct.unpack(
        '<BHBBBBBBBBBBBBB112s',
        buf
      )
    )

    tti_ebn = tti_block.EBN

    if 0xEF < tti_ebn < 0xFF:
      # skip user data and reserved blocks
      continue

    if is_in_extension:

      # if we are within an extension block, only accumulate the text information

      tti_tf += tti_block.TF
      
    else:

      # otherwise, initilialize the subtitle information

      tti_tf = tti_block.TF

      tti_sn = tti_block.SN
      tti_sgn = int(tti_block.SGN)
      tti_cs = tti_block.CS
      tti_tci = SmpteTimeCode(tti_block.TCIh, tti_block.TCIm, tti_block.TCIs, tti_block.TCIf, gsi_fps)
      tti_tco = SmpteTimeCode(tti_block.TCOh, tti_block.TCOm, tti_block.TCOs, tti_block.TCOf, gsi_fps)
      tti_jc = tti_block.JC
      tti_vp = tti_block.VP

    # continue accumulating if we have an extension block

    if tti_ebn != 0xFF:
      is_in_extension = True
      continue

    is_in_extension = False

    # create a new subtitle if SN changes and we are not in cumulative mode

    if tti_sn is not last_sn and tti_cs in (0x00, 0x01):

      # find the div to which the subtitle belongs, based on SGN

      cur_div = sgn_map.get(tti_sgn)

      # create the div if it does not exist

      if cur_div is None:
        cur_div = model.Div(doc)
        body.push_child(cur_div)
        sgn_map[tti_sgn] = cur_div

      # create the p that will hold the subtitle

      sub_element = model.P(doc)

      if tti_jc == 0x01:
        sub_element.set_style(styles.StyleProperties.TextAlign, styles.TextAlignType.start)
      elif tti_jc == 0x03:
        sub_element.set_style(styles.StyleProperties.TextAlign, styles.TextAlignType.end)
      else:
        sub_element.set_style(styles.StyleProperties.TextAlign, styles.TextAlignType.center)

      # assume that VP < MNR/2 means bottom-aligned and otherwise top-aligned
      # probably should offer an option to override this

      if tti_vp > gsi_mnr / 2:
        region = region_map.get(0)

        if region is None:
          region = model.Region("bottom", doc)
          region.set_style(
            styles.StyleProperties.Extent,
            styles.ExtentType(
              height=styles.LengthType(value=80, units=styles.LengthType.Units.pct),
              width=styles.LengthType(value=90, units=styles.LengthType.Units.pct),
            )
          )
          region.set_style(
            styles.StyleProperties.Origin,
            styles.CoordinateType(
              x=styles.LengthType(5, styles.LengthType.Units.pct),
              y=styles.LengthType(10, styles.LengthType.Units.pct)
            )
          )
          region.set_style(
            styles.StyleProperties.DisplayAlign,
            styles.DisplayAlignType.after
          )
          doc.put_region(region)
          region_map[0] = region
      else:
        region = region_map.get(1)

        if region is None:
          region = model.Region("top", doc)
          region.set_style(
            styles.StyleProperties.Extent,
            styles.ExtentType(
              height=styles.LengthType(value=80, units=styles.LengthType.Units.pct),
              width=styles.LengthType(value=90, units=styles.LengthType.Units.pct),
            )
          )
          region.set_style(
            styles.StyleProperties.Origin,
            styles.CoordinateType(
              x=styles.LengthType(5, styles.LengthType.Units.pct),
              y=styles.LengthType(10, styles.LengthType.Units.pct)
            )
          )
          region.set_style(
            styles.StyleProperties.DisplayAlign,
            styles.DisplayAlignType.before
          )
          doc.put_region(region)
          region_map[1] = region

      sub_element.set_region(region)

      cur_div.push_child(sub_element)

    if tti_cs in (0x01, 0x02, 0x03):

      # create a nested span if we are in cumulative mode

      cur_element = model.Span(doc)
      sub_element.push_child(cur_element)
      sub_element.push_child(model.Br(doc))

    else :

      cur_element = sub_element

    cur_element.set_begin(tti_tci.to_temporal_offset())
    cur_element.set_end(tti_tco.to_temporal_offset())
    process_tti_tf(cur_element, gsi_cct, tti_tf)
    progress_callback(i/tti_block_count)

  return doc