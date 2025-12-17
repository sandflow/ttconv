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
from typing import List, Optional, Sequence

import ttconv.model as model
from ttconv.isd import ISD
from ttconv.scc.codes.characters import unicode_to_scc
from ttconv.scc.codes.preambles_address_codes import SccPreambleAddressCode
from ttconv.scc.config import SccWriterConfiguration
from ttconv.style_properties import StyleProperties, NamedColors, TextAlignType
from ttconv.scc.codes.control_codes import SccControlCode
from ttconv.time_code import FPS_29_97, FPS_30, SmpteTimeCode

LOGGER = logging.getLogger(__name__)

class _Caption:
  """Collection of lines of text with a begin and end time and an alignment"""

  def __init__(self):
    self._begin: Fraction = 0
    self._end: Optional[Fraction] = None
    self._lines: List[str] = []
    self._alignment: TextAlignType = TextAlignType.start

  def set_begin(self, begin: Fraction):
    """Sets the begin time of the lines"""
    self._begin = begin

  def get_begin(self) -> Fraction:
    """Returns the begin time of the lines"""
    return self._begin

  def set_end(self, end: Fraction):
    """Sets the end time of the lines"""
    self._end = end

  def get_end(self) -> Optional[Fraction]:
    """Returns the end time of the lines"""
    return self._end

  def set_alignment(self, alignment: TextAlignType):
    """Sets the alignment of the lines"""
    self._alignment = alignment

  def get_alignment(self) -> TextAlignType:
    """Returns the alignment of the lines"""
    return self._alignment

  def set_lines(self, lines: List[str]):
    """Sets the lines of text"""
    self._lines = lines

  def __len__(self):
    return len(self._lines)

  def __getitem__(self, index: int) -> str:
    return self._lines[index]

  def __setitem__(self, index: int, value: str):
    self._lines[index] = value

  def __iter__(self):
    return iter(self._lines)

  def append(self, line: str):
    self._lines.append(line)

  @staticmethod
  def from_regions(regions: Sequence[model.Region]) -> _Caption:
    """Returns the list of lines that are flowed into the Region"""
    _lines: _Caption = _Caption()

    def _process_element(element: model.ContentElement):

      if isinstance(element, model.Div):
        for elem in element:
          _process_element(elem)
        return

      if isinstance(element, model.P):
        _lines.append("")
        _lines.set_alignment(element.get_style(StyleProperties.TextAlign))
        for elem in element:
          _process_element(elem)
        return

      if isinstance(element, model.Span):
        for elem in element:
          _process_element(elem)
        return

      if isinstance(element, model.Br):
        _lines.append("")
        return

      if isinstance(element, model.Text):
        _lines[-1] = _lines[-1] + element.get_text()
        return

    for region in regions:
      for body in region:
        for div in body:
          _process_element(div)

    return _lines

class _Chunk:

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
    self._begin_frame : Optional[int] = None

  def set_begin(self, frame: Optional[int]):
    self._begin_frame = frame

  def get_begin(self) -> Optional[int]:
    return self._begin_frame

  def get_dur(self) -> int:
    return (len(self._octet_buffer) + 1) // 2

  def get_end(self) -> Optional[int]:
    if self._begin_frame is None:
      return None
    return self._begin_frame + self.get_dur()

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

  def push_char(self, char: str):
    if len(char) != 1:
      raise ValueError("Length of string must be exactly 1")
    
    scc_bytes = unicode_to_scc(char)

    if len(scc_bytes) > 1 and len(self._octet_buffer) % 2 == 1:
      self._octet_buffer.append(0)
    
    for b in scc_bytes:
      self._octet_buffer.append(b)

  def overlap(self, other: _Chunk) -> bool:
    """Checks if the other chunk overlaps with the current chunk"""
    return other.get_begin() <= self.get_end() and other.get_end() >= self.get_begin()

  def insert(self, other: _Chunk):
    """Inserts the other chunk while preserving the begin time of the current chunk"""
    if other.get_begin() is None or other.get_end() is None:
      raise RuntimeError("Cannot insert chunk with no begin time")

    if not self.overlap(other):
      raise RuntimeError("Cannot insert chunk that does not overlap")

    loc = 2 * max(0, other.get_begin() - self.get_begin())
    self._octet_buffer[loc:loc] = other._octet_buffer

    # adjust the begin time preserving the end time
    self.set_begin(self.get_begin() - other.get_dur())

  def __len__(self):
    return len(self._octet_buffer)

  def to_string(self, fps : Fraction, is_df: bool, start_offset: int) -> str:
    if fps not in (FPS_29_97, FPS_30):
      raise ValueError(f"Frame rate {fps} out-of-range")

    if fps != FPS_29_97 and is_df:
      raise ValueError("Frame rate must be fractional if drop frame is true")

    def _octet2hex(octet):
      return format(_Chunk.ODD_PARITY_OCTETS[octet], 'x')

    packets = []
    for i in range(len(self._octet_buffer) // 2):
      packets.append(_octet2hex(self._octet_buffer[2 * i]) + _octet2hex(self._octet_buffer[2 * i + 1]))
    if len(self._octet_buffer) % 2 == 1:
      packets.append(_octet2hex(self._octet_buffer[-1]) + _octet2hex(0))

    return str(SmpteTimeCode.from_frames(self.get_begin() + start_offset, fps, is_df)) + "\t" + " ".join(packets)

MAX_LINEWIDTH = 32

#
# scc writer
#
def from_model(doc: model.ContentDocument, config: Optional[SccWriterConfiguration] = None, progress_callback=lambda _: None) -> str:
  """Converts the data model to an SCC document"""

  # split progress between ISD construction and SCC writing
  def _isd_progress(progress: float):
    progress_callback(progress / 2)

  config : SccWriterConfiguration = config if config is not None else SccWriterConfiguration()
  isds = ISD.generate_isd_sequence(doc, _isd_progress)
  is_rollup = None
  is_last_empty = True

  # generate list of captions
  captions: List[_Caption] = []
  for i, (begin, isd) in enumerate(isds):

    # 25% for creating captions
    progress_callback(0.5 + (i + 1) / len(isds) / 4)
    LOGGER.debug("Processing ISD at %ss to SCC content", float(begin))

    if len(captions) > 0 and captions[-1].get_end() is None:
      captions[-1].set_end(begin)

    non_empty_region_cnt = 0
    for r in isd.iter_regions():
      if len(r) > 0:
        non_empty_region_cnt += 1
        if non_empty_region_cnt > 1:
          # SCC can only handle one region at a time
          LOGGER.warning("Merging multiple regions at %ss; errors may result", float(begin))
          break

    if non_empty_region_cnt == 0:
      # skip empty ISD
      is_last_empty = True
      continue

    is_last_empty = False

    caption: _Caption = _Caption.from_regions(list(isd.iter_regions()))
    caption.set_begin(begin)

    if len(caption) == 0:
      # skip ISD with no text
      continue

    if any(len(e) > MAX_LINEWIDTH for e in caption):
      if config.allow_reflow:
        LOGGER.warning("Line width exceeded at %ss", float(begin))
      else:
        raise RuntimeError(f"Line width exceeded at {float(begin)}s, reflow disabled")
      # merge the lines of the caption and remove duplicate spaces
      text: str = re.sub(' +', ' ', ' '.join(caption))

      # reflow text
      reflowed_lines: List[str] = []
      while len(text) > MAX_LINEWIDTH:
        break_i = MAX_LINEWIDTH

        for i in range(len(text) - 2, 0, -1):
          c = text[i]
          if c == ord(' ') and i < MAX_LINEWIDTH:
            break_i = i
            break

        reflowed_lines.append(text[:break_i])
        text = text[break_i + 1:]

      reflowed_lines.append(text)

      caption.set_lines(reflowed_lines)

    # detect roll-up captions
    if len(captions) > 1 and is_rollup is not False and not is_last_empty:
      if caption[-1].startswith(captions[-1][-1]) or \
        len(caption) > 1 and caption[-2] == captions[-1][-1]:
        is_rollup = True
      else:
        if is_rollup is True:
          LOGGER.warning("Inconsistent roll-up captions, defaulting to pop-on")
        is_rollup = False

    captions.append(caption)

  chunks : List[_Chunk] = []
  for i, caption in enumerate(captions):
    # 25% for SCC writing
    progress_callback(0.75 + (i + 1) / len(captions) / 4)

    if is_rollup is True and not config.force_popon:
      ru_chunk: _Chunk = _Chunk()

      is_painton = i > 0 and caption[-1].startswith(captions[i - 1][-1])

      begin_f = int(caption.get_begin() * config.frame_rate.fps)

      if not is_painton:
        if config.rollup_lines == 2:
          ru_chunk.push_control_code(SccControlCode.RU2.get_ch1_value())
        elif config.rollup_lines == 3:
          ru_chunk.push_control_code(SccControlCode.RU3.get_ch1_value())
        else:
          ru_chunk.push_control_code(SccControlCode.RU4.get_ch1_value())
        # the caption begins when the CR code is received
        begin_f = begin_f - ru_chunk.get_dur()
        ru_chunk.push_control_code(SccControlCode.CR.get_ch1_value())
        pac = SccPreambleAddressCode(1, 15, NamedColors.white, 0, False, False)
        ru_chunk.push_control_code(pac.get_ch1_packet())


      if len(chunks) > 0 and begin_f < chunks[-1].get_end():
        begin_f = chunks[-1].get_end()
        LOGGER.warning("Overlapping roll-up text at %s", SmpteTimeCode.from_seconds(caption.get_begin(), config.frame_rate.fps))
      ru_chunk.set_begin(begin_f)

      for c in (caption[-1][len(captions[i - 1][-1]):] if is_painton else caption[-1]):
        ru_chunk.push_char(c)

      chunks.append(ru_chunk)

      # erase the display if there is a gap between roll-up captions
      if caption.get_end() is not None and \
        (i == len(captions) - 1 or caption.get_end() != captions[i + 1].get_begin()):
        edm_chunk = _Chunk()
        edm_chunk.push_control_code(SccControlCode.EDM.get_ch1_value())
        edm_chunk.set_begin(int(caption.get_end() * config.frame_rate.fps))
        chunks.append(edm_chunk)

    else:
      enm_chunk: _Chunk = _Chunk()

      enm_chunk.push_control_code(SccControlCode.RCL.get_ch1_value())
      enm_chunk.push_control_code(SccControlCode.ENM.get_ch1_value())
      for line_num, line in enumerate(caption, 15 - len(caption)):
        if caption.get_alignment() == TextAlignType.center:
          indent = (32 - len(line)) // 2
        elif caption.get_alignment() == TextAlignType.end:
          indent = 32 - len(line)
        else:
          indent = None

        spaces = indent % 4 if indent is not None else 0
        indent = 4 * (indent // 4) if indent is not None else None

        pac = SccPreambleAddressCode(1, line_num, NamedColors.white, indent, False, False)
        enm_chunk.push_control_code(pac.get_ch1_packet())

        for i in range(spaces):
          enm_chunk.push_char(" ")
        for c in line:
          enm_chunk.push_char(c)
      enm_chunk.push_control_code(SccControlCode.EOC.get_ch1_value())

      enm_chunk.set_begin(int(caption.get_begin() * config.frame_rate.fps - enm_chunk.get_dur() + 2))
      # check if there is an overlap with the previous chunk
      if len(chunks) > 0:
        if chunks[-2].get_end() + chunks[-1].get_dur() > enm_chunk.get_begin():
          LOGGER.warning("Skipping ISD at %s due to overlap in line 21 packets with previous ISD", float(caption.get_begin()))
          continue

        if enm_chunk.overlap(chunks[-1]):
          enm_chunk.insert(chunks[-1])
          chunks.pop()

      chunks.append(enm_chunk)

      # initialize the EDM chunk
      if caption.get_end() is not None:
        edm_chunk = _Chunk()
        edm_chunk.push_control_code(SccControlCode.EDM.get_ch1_value())
        edm_chunk.set_begin(int(caption.get_end() * config.frame_rate.fps))
        chunks.append(edm_chunk)

  start_offset = 0
  if config.start_tc is not None:
    start_tc = SmpteTimeCode.parse(config.start_tc, config.frame_rate.fps)
    if start_tc.is_drop_frame() != config.frame_rate.df:
      raise RuntimeError("The drop-frame status of the specified start_timecode does not match the drop-frame status of the specified frame_rate")
    start_offset = start_tc.to_frames()

  for chunk in chunks:
    if start_offset + chunk.get_begin() < 0:
      raise RuntimeError("The SCC stream would start earlier than the specified start timecode")

  return "Scenarist_SCC V1.0\n\n" + "\n\n".join(map(lambda e: e.to_string(config.frame_rate.fps, config.frame_rate.df, start_offset), chunks))
