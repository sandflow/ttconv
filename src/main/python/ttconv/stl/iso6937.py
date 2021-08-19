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

"""Decoder for the ISO 6937 character set"""

import codecs
import io

# from https://bugs.python.org/file45750/iso6937.py
_CCT0_DECODE_MAP = {
    b'\xa0': '\u00A0',  # NO-BREAK SPACE
    b'\xa1': '\u00A1',  # ¡
    b'\xa2': '\u00A2',  # ¢
    b'\xa3': '\u00A3',  # £
    b'\xa4': '\u00A4',  # $
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

def decode(byte_buffer: bytes, errors="strict"):
  """Decodes `byte_buffer` to a string according to ISO 6937 character set and returns it.
  """

  # pylint: disable=unused-argument
  handler = codecs.lookup_error(errors)
  s = io.StringIO()

  i = 0
  while i < len(byte_buffer):
    if 0x20 <= int(byte_buffer[i]) <= 0x7E:
      s.write(chr(byte_buffer[i]))
      i += 1
    elif 0xC1 <= int(byte_buffer[i]) <= 0xCF:
      b = bytes(byte_buffer[i:i+2])
      c = _CCT0_DECODE_MAP.get(b)
      if c is not None:
        s.write(c)
      else:
        s.write("�")
        handler(UnicodeDecodeError("iso6937", byte_buffer, i, i + 2, f"Unknown character sequence: {str(b)}"))
      i += 2
    else:
      b = bytes(byte_buffer[i:i+1])
      c = _CCT0_DECODE_MAP.get(b)
      if c is not None:
        s.write(c)
      else:
        s.write("�")
        handler(UnicodeDecodeError("iso6937", byte_buffer, i, i + 1, f"Unknown character sequence: {str(b)}"))
      i += 1

  return (s.getvalue(), len(byte_buffer))
