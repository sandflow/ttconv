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

"""SRT writer"""

import logging
from fractions import Fraction
from typing import List, Optional

import ttconv.model as model
import ttconv.srt.style as style
from ttconv.filters import Filter
from ttconv.filters.default_style_properties import DefaultStylePropertyValuesFilter
from ttconv.filters.merge_paragraphs import ParagraphsMergingFilter
from ttconv.filters.merge_regions import RegionsMergingFilter
from ttconv.filters.supported_style_properties import SupportedStylePropertiesFilter
from ttconv.isd import ISD, ISDConfiguration
from ttconv.srt.paragraph import SrtParagraph
from ttconv.style_properties import StyleProperties, FontStyleType, NamedColors, FontWeightType, TextDecorationType

LOGGER = logging.getLogger(__name__)


class SrtContext:
  """SRT writer context"""

  filters: List[Filter] = (
    RegionsMergingFilter(),
    ParagraphsMergingFilter(),
    SupportedStylePropertiesFilter({
      StyleProperties.FontWeight: [
        # Every values
      ],
      StyleProperties.FontStyle: [
        FontStyleType.normal,
        FontStyleType.italic
      ],
      StyleProperties.TextDecoration: [
        TextDecorationType.underline
      ],
      StyleProperties.Color: [
        # Every values
      ],
    }),
    DefaultStylePropertyValuesFilter({
      StyleProperties.Color: NamedColors.white.value,
      StyleProperties.FontWeight: FontWeightType.normal,
      StyleProperties.FontStyle: FontStyleType.normal,
    })
  )

  def __init__(self):
    self._captions_counter: int = 0
    self._begin: Fraction = Fraction(0)
    self._end: Fraction = Fraction(0)
    self._paragraphs: List[SrtParagraph] = []

  def append_element(self, element: model.ContentElement, begin: Fraction, end: Optional[Fraction]):
    """Converts model element to SRT content"""

    if isinstance(element, model.Div):
      for elem in list(element):
        self.append_element(elem, begin, end)

    if isinstance(element, model.P):

      self._captions_counter += 1

      self._paragraphs.append(SrtParagraph(self._captions_counter))
      self._paragraphs[-1].set_begin(begin)
      self._paragraphs[-1].set_end(end)

      for elem in list(element):
        self.append_element(elem, begin, end)

      self._paragraphs[-1].normalize_eol()

      if self._paragraphs[-1].is_only_whitespace():
        LOGGER.debug("Removing empty paragraph.")
        self._paragraphs.pop()

    if isinstance(element, model.Span):
      is_bold = style.is_element_bold(element)
      is_italic = style.is_element_italic(element)
      is_underlined = style.is_element_underlined(element)
      font_color = style.get_font_color(element)

      if font_color is not None:
        self._paragraphs[-1].append_text(style.FONT_COLOR_TAG_IN.format(font_color))

      if is_bold:
        self._paragraphs[-1].append_text(style.BOLD_TAG_IN)
      if is_italic:
        self._paragraphs[-1].append_text(style.ITALIC_TAG_IN)
      if is_underlined:
        self._paragraphs[-1].append_text(style.UNDERLINE_TAG_IN)

      for elem in list(element):
        self.append_element(elem, begin, end)

      if is_underlined:
        self._paragraphs[-1].append_text(style.UNDERLINE_TAG_OUT)
      if is_italic:
        self._paragraphs[-1].append_text(style.ITALIC_TAG_OUT)
      if is_bold:
        self._paragraphs[-1].append_text(style.BOLD_TAG_OUT)
      if font_color is not None:
        self._paragraphs[-1].append_text(style.FONT_COLOR_TAG_OUT)

    if isinstance(element, model.Br):
      self._paragraphs[-1].append_text("\n")

    if isinstance(element, model.Text):
      self._paragraphs[-1].append_text(element.get_text())

  def add_isd(self, isd, begin: Fraction, end: Optional[Fraction]):
    """Converts and appends ISD content to SRT content"""

    LOGGER.debug(
      "Append ISD from %ss to %ss to SRT content.",
      float(begin),
      float(end) if end is not None else "unbounded"
    )

    is_isd_empty = True

    for region in isd.iter_regions():

      if len(region) > 0:
        is_isd_empty = False

      for body in region:
        for div in list(body):
          self.append_element(div, begin, end)

    if is_isd_empty:
      LOGGER.debug("Skipping empty paragraph.")

  def finish(self):
    """Checks and processes the last paragraph"""

    LOGGER.debug("Check and process the last SRT paragraph.")

    if self._paragraphs and self._paragraphs[-1].get_end() is None:
      if self._paragraphs[-1].is_only_whitespace():
        # if the last paragraph contains only whitespace, remove it
        LOGGER.debug("Removing empty unbounded last paragraph.")
        self._paragraphs.pop()

      else:
        # set default end time code
        LOGGER.warning("Set a default end value to paragraph (begin + 10s).")
        self._paragraphs[-1].set_end(self._paragraphs[-1].get_begin().to_seconds() + 10.0)

  def __str__(self) -> str:
    return "\n".join(p.to_string(id + 1) for id, p in enumerate(self._paragraphs))


#
# srt writer
#


def from_model(doc: model.ContentDocument, isd_config: Optional[ISDConfiguration] = None, progress_callback=lambda _: None) -> str:
  """Converts the data model to a SRT document"""

  srt = SrtContext()

  # split progress between ISD construction and SRT writing

  def _isd_progress(progress: float):
    progress_callback(progress / 2)

  # Compute ISDs

  isds = list(
    ISD.generate_isd_sequence(doc, _isd_progress, is_multithreaded=isd_config.multi_thread if isd_config is not None else True)
  )

  # process ISDs

  for i, (begin, isd) in enumerate(isds):

    end = isds[i + 1][0] if i + 1 < len(isds) else None

    for srt_filter in srt.filters:
      srt_filter.process(isd)

    srt.add_isd(isd, begin, end)

    progress_callback(0.5 + (i + 1) / len(isds) / 2)

  srt.finish()

  return str(srt)
