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

from __future__ import annotations

import logging
from fractions import Fraction
import re
from typing import List, Optional

import ttconv.model as model
from ttconv.isd import ISD
from ttconv.scc.codes.characters import unicode_to_scc
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

def _LinesFromRegion(region: model.Region) -> List[_Line]:
  """Returns the list of lines that are flowed into the Region"""
  _lines: List[_Line] = []

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
      _lines[-1].text = _lines[-1].text + unicode_to_scc(element.get_text())
      return

  for body in region:
    for div in body:
      _process_element(div)

  return _lines

class _Line21Chunk:

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
    self._octet_buffer : bytearray = bytearray()
    self._start_frame : Optional[int] = None

  def set_begin(self, frame: Optional[int]):
    self._start_frame = frame

  def get_begin(self) -> Optional[int]:
    return self._start_frame

  def get_dur(self) -> int:
    return (len(self._octet_buffer) + 1) // 2

  def get_end(self) -> Optional[int]:
    if self._start_frame is None:
      return None
    return self._start_frame + self.get_dur()

  def push_control_code(self, cc: int):
    hi_octet = cc // 256
    lo_octet = cc % 256
    if (hi_octet > 127 or lo_octet > 127):
      raise RuntimeError("Line 21 octet is out of range")
    if len(self._octet_buffer) % 2 == 1:
      self._octet_buffer.append(0)
    self._octet_buffer.append(hi_octet)
    self._octet_buffer.append(lo_octet)

    # per spec, always double up control codes
    if 0x10 <= hi_octet <= 0x1F:
      self._octet_buffer.append(hi_octet)
      self._octet_buffer.append(lo_octet)

  def push_octet(self, octet: int):
    if (octet > 127):
      raise RuntimeError("Line 21 octet is out of range")
    self._octet_buffer.append(octet)

  def overlap(self, other: _Line21Chunk) -> bool:
    """Checks if the other chunk overlaps with the current chunk"""
    return other.get_begin() <= self.get_end() and other.get_end() >= self.get_begin()

  def insert(self, other: _Line21Chunk):
    """Inserts the other chunk while preserving the begin time of the current chunk"""
    if other.get_begin() is None or other.get_end() is None:
      raise RuntimeError("Cannot insert chunk with no begin time")

    if not self.overlap(other):
      raise RuntimeError("Cannot insert chunk that does not overlap")

    loc = max(0, other.get_begin() - self.get_begin())
    self._octet_buffer[loc:loc] = other._octet_buffer

    # adjust the begin time preserving the end time
    self._start_frame -= other.get_dur()

  def __len__(self):
    return len(self._octet_buffer)

  def __str__(self):
    def _octet2hex(octet):
      return format(_Line21Chunk.ODD_PARITY_OCTETS[octet], 'x')

    packets = []
    for i in range(len(self._octet_buffer) // 2):
      packets.append(_octet2hex(self._octet_buffer[2 * i]) + _octet2hex(self._octet_buffer[2 * i + 1]))
    if len(self._octet_buffer) % 2 == 1:
      packets.append(_octet2hex(self._octet_buffer[-1]) + _octet2hex(0))

    return str(SmpteTimeCode.from_frames(self.get_begin(), Fraction(30000, 1001))) + "\t" + " ".join(packets)


class SCCContext:
  """SCC writer state"""

  MAX_LINEWIDTH = 32
  FRAME_RATE = Fraction(30000, 1001)

  def __init__(self, config: SccWriterConfiguration):
    self._config = config
    self._last_lines: Optional[List[_Line]] = None
    self._chunks: List[_Line21Chunk] = []

  def add_isd(self, isd, begin: Fraction, end: Optional[Fraction]):
    """Converts and appends ISD content to SCC content"""

    LOGGER.debug(
      "Append ISD from %ss to %ss to SCC content.",
      float(begin),
      float(end) if end is not None else "indefinite"
    )

    regions : List[ISD.Region] = list(isd.iter_regions())

    if len(regions) == 0:
      return

    # for now, handle only one region
    if len(regions) > 1:
      LOGGER.error("Skipping ISD at %ss because it has more than one region", float(begin))
      return

    region = regions[0]

    lines = _LinesFromRegion(region)

    if len(lines) == 0:
      LOGGER.info("Skipping ISD at %ss because it has no lines of text", float(begin))
      return

    if any(len(e.text) > SCCContext.MAX_LINEWIDTH for e in lines):
      if not self._config.allow_reflow:
        raise RuntimeError(f"Line width exceeds the maximum allowed by the SCC writer ({SCCContext.MAX_LINEWIDTH})")

      # reflow text
      reflowed_lines: List[bytes] = []

      # remove duplicate spaces
      text = re.sub(b' +', b' ', b' '.join(e.text for e in lines))

      while len(text) > SCCContext.MAX_LINEWIDTH:
        break_i = SCCContext.MAX_LINEWIDTH

        for i in range(len(text) - 2, 0, -1):
          c = text[i]
          if c == ord(' ') and i < SCCContext.MAX_LINEWIDTH:
            break_i = i
            break

        reflowed_lines.append(text[:break_i])
        text = text[break_i + 1:]

      reflowed_lines.append(text)

      alignment = lines[0].alignment

      lines = [_Line(e, alignment) for e in reflowed_lines]

    if self._config.force_rollup:

      ru_chunk: _Line21Chunk = _Line21Chunk()

      ru_chunk.push_control_code(SccControlCode.RU4.get_ch1_value())
      ru_chunk.push_control_code(SccControlCode.CR.get_ch1_value())
      pac = SccPreambleAddressCode(1, 15, NamedColors.white, 0, False, False)
      ru_chunk.push_control_code(pac.get_ch1_packet())

      begin_f = int(begin * self.FRAME_RATE - ru_chunk.get_dur())
      if len(self._chunks) > 0 and begin_f < self._chunks[-1].get_end():
        begin_f = self._chunks[-1].get_end()
        LOGGER.warning("Overlapping roll-up text at %s", SmpteTimeCode.from_seconds(begin_f, self.FRAME_RATE))
      ru_chunk.set_begin(begin_f)

      for c in lines[-1].text:
        ru_chunk.push_octet(c)

      self._chunks.append(ru_chunk)

    else:
      enm_chunk: _Line21Chunk = _Line21Chunk()

      enm_chunk.push_control_code(SccControlCode.RCL.get_ch1_value())
      enm_chunk.push_control_code(SccControlCode.ENM.get_ch1_value())
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
        enm_chunk.push_control_code(pac.get_ch1_packet())

        for i in range(spaces):
          enm_chunk.push_octet(0x20)
        for c in line.text:
          enm_chunk.push_octet(c)
      enm_chunk.push_control_code(SccControlCode.EOC.get_ch1_value())

      enm_chunk.set_begin(int(begin * self.FRAME_RATE - enm_chunk.get_dur()))
      # check if there is an overlap with the previous chunk
      if len(self._chunks) > 0:
        if self._chunks[-2].get_end() + self._chunks[-1].get_dur() > enm_chunk.get_begin():
          LOGGER.warning("Skipping caption at %s due to overlap", float(begin))
          return

        if enm_chunk.overlap(self._chunks[-1]):
          enm_chunk.insert(self._chunks[-1])
          self._chunks.pop()

      self._chunks.append(enm_chunk)

      # initialize the EDM chunk
      edm_chunk = _Line21Chunk()
      edm_chunk.push_control_code(SccControlCode.EDM.get_ch1_value())
      edm_chunk.set_begin(int(end * self.FRAME_RATE - edm_chunk.get_dur()))
      self._chunks.append(edm_chunk)

    self._last_lines = lines

  def finish(self):
    pass

  def __str__(self) -> str:
    return "Scenarist_SCC V1.0\n\n" + "\n\n".join(map(str, self._chunks))


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
