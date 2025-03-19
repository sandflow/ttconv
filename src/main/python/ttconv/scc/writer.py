#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2025, Sandflow Consulting LLC
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

"""SCC writer"""

from itertools import islice
import logging
from fractions import Fraction
import re
from typing import List, Optional

import ttconv.model as model
from ttconv.isd import ISD
from ttconv.scc.codes.preambles_address_codes import SccPreambleAddressCode
from ttconv.scc.config import SccWriterConfiguration
from ttconv.style_properties import StyleProperties, FontStyleType, NamedColors, FontWeightType, TextDecorationType, TextAlignType, DisplayAlignType
from ttconv.scc.codes.control_codes import SccControlCode
from ttconv.time_code import SmpteTimeCode

LOGGER = logging.getLogger(__name__)

class _Line:
  def __init__(self, text: bytes, alignment: TextAlignType = TextAlignType.start):
    self.text = text
    self.alignment = alignment

def _LinesFromRegion(region: model.Region):
  """Returns the list of lines that are flowed into the Region"""
  _lines: List[_Line] = []
  _max_line_width: int = 32

  def _process_element(element: model.ContentElement):

    if isinstance(element, model.Div):
      for elem in element:
        _process_element(elem)
      return

    if isinstance(element, model.P):
      _lines.append(_Line(bytes(), element.get_style(StyleProperties.TextAlign)))
      for elem in element:
        _process_element(elem)
      return

    if isinstance(element, model.Span):
      for elem in element:
        _process_element(elem)
      return

    if isinstance(element, model.Br):
      _lines.append(_Line(bytes(), _lines[-1].alignment))
      return

    if isinstance(element, model.Text):
      _lines[-1].text = _lines[-1].text + element.get_text().encode('ascii')

      # limit lines to _max_line_width characters
      while (len(_lines[-1].text) > _max_line_width):
        line = _lines[-1].text
        break_i = _max_line_width

        for i in range(len(line) - 2, 0, -1):
          c = line[i]
          if c in (ord(' '), ord('-')) and i < _max_line_width:
            break_i = i
            break

        _lines.append(_Line( line[break_i + 1:], _lines[-1].alignment))
        _lines[-2].text = line[:break_i]

      return

  for body in region:
    for div in body:
      _process_element(div)

  return _lines

class _Line21Buffer:

  ODD_PARITY_OCTETS = [
    128, 1, 2, 131, 4, 133, 134, 7, 8, 137, 138, 11, 140, 13, 14, 143,
    16, 145, 146, 19, 148, 21, 22, 151, 152, 25, 26, 155, 28, 157, 158, 31,
    32, 161, 162, 35, 164, 37, 38, 167, 168, 41, 42, 171, 44, 173, 174, 47,
    176, 49, 50, 179, 52, 181, 182, 55, 56, 185, 186, 59, 188, 61, 62, 191,
    64, 193, 194, 67, 196, 69, 70, 199, 200, 73, 74, 203, 76, 205, 206, 79,
    208, 81, 82, 211, 84, 213, 214, 87, 88, 217, 218, 91, 220, 93, 94, 223,
    224, 97, 98, 227, 100, 229, 230, 103, 104, 233, 234, 107, 236, 109, 110, 239,
    112, 241, 242, 115, 244, 117, 118, 247, 248, 121, 122, 251, 124, 253, 254, 127
  ]

  def __init__(self):
    self._octet_buffer : List[int] = []

  def push_control_code(self, cc: int):
    hi_octet = cc // 256
    lo_octet = cc % 256
    if (hi_octet > 127 or lo_octet > 127):
      raise RuntimeError("Line 21 octet is out of range")
    if len(self._octet_buffer) % 2 == 1:
      self._octet_buffer.append(0)
    self._octet_buffer.append(hi_octet)
    self._octet_buffer.append(lo_octet)

  def push_octet(self, octet: int):
    if (octet > 127):
      raise RuntimeError("Line 21 octet is out of range")
    self._octet_buffer.append(octet)

  def __len__(self):
    return len(self._octet_buffer)

  def __str__(self):
    def _octet2hex(octet):
      return format(_Line21Buffer.ODD_PARITY_OCTETS[octet], 'x')

    packets = []
    for i in range(len(self._octet_buffer) // 2):
      packets.append(_octet2hex(self._octet_buffer[2 * i]) + _octet2hex(self._octet_buffer[2 * i + 1]))
    if len(self._octet_buffer) % 2 == 1:
      packets.append(_octet2hex(self._octet_buffer[-1]) + _octet2hex(0))

    return " ".join(packets)


class SCCContext:
  """SCC writer state"""

  def __init__(self, config: SccWriterConfiguration):
    self._events: List[str] = []

  def add_isd(self, isd, begin: Fraction, end: Optional[Fraction]):
    """Converts and appends ISD content to SRT content"""

    LOGGER.debug(
      "Append ISD from %ss to %ss to SCC content.",
      float(begin),
      float(end) if end is not None else "indefinite"
    )

    regions : List[ISD.Region] = list(isd.iter_regions())

    # for now, handle only one region

    if len(regions) > 1:
      LOGGER.error("Skipping ISD at %ss because it has more than one region", float(begin))
      return

    if len(regions) == 0:
      LOGGER.info("Skipping ISD at %ss because it has no regions", float(begin))
      return

    region = regions[0]

    lines = _LinesFromRegion(region)

    packet_buffer: _Line21Buffer = _Line21Buffer()

    packet_buffer.push_control_code(SccControlCode.RCL.get_ch1_value())
    packet_buffer.push_control_code(SccControlCode.RCL.get_ch1_value())

    packet_buffer.push_control_code(SccControlCode.ENM.get_ch1_value())
    packet_buffer.push_control_code(SccControlCode.ENM.get_ch1_value())

    for line_num, line in enumerate(lines, 15 - len(lines)):
      if line.alignment == TextAlignType.center:
        indent = int(32 - len(line.text) / 2)
      elif line.alignment == TextAlignType.end:
        indent = int(32 - len(line.text))
      else:
        indent = None

      spaces = indent % 4 if indent is not None else 0
      indent = indent // 4 if indent is not None else None

      pac = SccPreambleAddressCode(1, line_num, NamedColors.white, indent, False, False)
      packet_buffer.push_control_code(pac.get_ch1_packet())
      packet_buffer.push_control_code(pac.get_ch1_packet())

      for i in range(spaces):
        packet_buffer.push_octet(0x20)
      for c in line.text:
        packet_buffer.push_octet(c)

    packet_buffer.push_control_code(SccControlCode.EDM.get_ch1_value())
    packet_buffer.push_control_code(SccControlCode.EDM.get_ch1_value())

    packet_buffer.push_control_code(SccControlCode.EOC.get_ch1_value())
    packet_buffer.push_control_code(SccControlCode.EOC.get_ch1_value())

    scc_begin = SmpteTimeCode.from_seconds(begin - len(packet_buffer) * Fraction(1001, 30000) / 2, Fraction(30000, 1001))
    self._events.append(str(scc_begin) + "\t" + str(packet_buffer))

    packet_buffer: _Line21Buffer = _Line21Buffer()
    packet_buffer.push_control_code(SccControlCode.EDM.get_ch1_value())

    scc_end = SmpteTimeCode.from_seconds(end - len(packet_buffer) * Fraction(1001, 30000) / 2, Fraction(30000, 1001))
    self._events.append(str(scc_end) + "\t" + str(packet_buffer))
  def finish(self):
    pass

  def __str__(self) -> str:
    return "Scenarist_SCC V1.0\n\n" + "\n".join(self._events)


#
# scc writer
#
def from_model(doc: model.ContentDocument, config: Optional[SccWriterConfiguration] = None, progress_callback=lambda _: None) -> str:
  """Converts the data model to an SCC document"""

  scc_context = SCCContext(config if config is not None else SccWriterConfiguration())

  # split progress between ISD construction and SRT writing

  def _isd_progress(progress: float):
    progress_callback(progress / 2)

  # Compute ISDs

  isds = list(
    ISD.generate_isd_sequence(doc, _isd_progress)
  )

  # process ISDs

  for i, (begin, isd) in enumerate(isds):

    end = isds[i + 1][0] if i + 1 < len(isds) else None

    scc_context.add_isd(isd, begin, end)

    progress_callback(0.5 + (i + 1) / len(isds) / 2)

  scc_context.finish()

  return str(scc_context)
