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

"""WebVTT writer"""

import logging
from fractions import Fraction
from typing import Dict, List, Optional

import ttconv.model as model
import ttconv.vtt.style as style
from ttconv.filters import Filter
from ttconv.filters.default_style_properties import DefaultStylePropertyValuesFilter
from ttconv.filters.merge_paragraphs import ParagraphsMergingFilter
from ttconv.filters.merge_regions import RegionsMergingFilter
from ttconv.filters.supported_style_properties import SupportedStylePropertiesFilter
from ttconv.isd import ISD
from ttconv.vtt.paragraph import VttParagraph
from ttconv.vtt.css_class import CssClass
from ttconv.style_properties import StyleProperties, FontStyleType, NamedColors, FontWeightType, TextDecorationType

LOGGER = logging.getLogger(__name__)


class VttContext:
  """VTT writer context"""

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
      StyleProperties.BackgroundColor: [
        # Every values
      ],
    }),
    DefaultStylePropertyValuesFilter({
      StyleProperties.Color: NamedColors.white.value,
      StyleProperties.BackgroundColor: NamedColors.transparent.value,
      StyleProperties.FontWeight: FontWeightType.normal,
      StyleProperties.FontStyle: FontStyleType.normal,
    })
  )

  def __init__(self):
    self._captions_counter: int = 0
    self._begin: Fraction = Fraction(0)
    self._end: Fraction = Fraction(0)
    self._paragraphs: List[VttParagraph] = []
    self._css_classes: List[CssClass] = []
    self._colors_used: Dict[str, str] = {}
    self._background_colors_used: Dict[str, str] = {}

  def append_element(self, element: model.ContentElement, begin: Fraction, end: Optional[Fraction]):
    """Converts model element to VTT content"""

    if isinstance(element, model.Div):
      for elem in list(element):
        self.append_element(elem, begin, end)

    if isinstance(element, model.P):

      self._captions_counter += 1

      self._paragraphs.append(VttParagraph(self._captions_counter))
      self._paragraphs[-1].set_begin(begin)
      self._paragraphs[-1].set_end(end)

      for elem in list(element):
        self.append_element(elem, begin, end)

    if isinstance(element, model.Span):
      is_bold = style.is_element_bold(element)
      is_italic = style.is_element_italic(element)
      is_underlined = style.is_element_underlined(element)
      color = style.get_color(element)
      bg_color = style.get_background_color(element)

      if color is not None:
        if self._colors_used.get(color) is None:
          color_classname = style.get_color_classname(color)
          self._colors_used[color] = color_classname
          self._css_classes.append(CssClass("color", color, color_classname))
        else:
          color_classname = self._colors_used[color]
        self._paragraphs[-1].append_text(style.COLOR_TAG_IN.format(color_classname))

      if bg_color is not None:
        if self._background_colors_used.get(bg_color) is None:
          bg_color_classname = style.get_background_color_classname(bg_color)
          self._background_colors_used[bg_color] = bg_color_classname
          self._css_classes.append(CssClass("background-color", bg_color, bg_color_classname))
        else:
          bg_color_classname = self._background_colors_used[bg_color]
        self._paragraphs[-1].append_text(style.BG_COLOR_TAG_IN.format(bg_color_classname))

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
      if color is not None:
        self._paragraphs[-1].append_text(style.COLOR_TAG_OUT)
      if bg_color is not None:
        self._paragraphs[-1].append_text(style.BG_COLOR_TAG_OUT)


    if isinstance(element, model.Br):
      self._paragraphs[-1].append_text("\n")

    if isinstance(element, model.Text):
      self._paragraphs[-1].append_text(element.get_text())

  def add_isd(self, isd, begin: Fraction, end: Optional[Fraction]):
    """Converts and appends ISD content to VTT content"""

    LOGGER.debug(
      "Append ISD from %ss to %ss to VTT content.",
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

    LOGGER.debug("Check and process the last VTT paragraph.")

    if self._paragraphs and self._paragraphs[-1].get_end() is None:
      if self._paragraphs[-1].is_only_whitespace():
        # if the last paragraph contains only whitespace, remove it
        LOGGER.debug("Removing empty unbounded last paragraph.")
        self._paragraphs.pop()

      else:
        # set default end time code
        LOGGER.warning("Set a default end value to paragraph (begin + 10s).")
        self._paragraphs[-1].set_end(self._paragraphs[-1].get_begin().to_seconds() + 10.0)

  def style_block(self):
    """Generated CSS INLINE STYLE Block"""
    style_block = ""
    cue_default = "\n".join(("::cue {","  background-color: transparent;", "}\n"))
    if len(self._css_classes) > 0:
      style_block = "STYLE\n" + cue_default +"\n".join(css.to_string() for css in self._css_classes) + "\n\n"
    return style_block

  def __str__(self) -> str:
    return "WEBVTT\n\n" + self.style_block() + "\n".join(p.to_string() for p in self._paragraphs)


#
# vtt writer
#


def from_model(doc: model.ContentDocument, _isd_config = None, progress_callback=lambda _: None) -> str:
  """Converts the data model to a VTT document"""

  vtt = VttContext()

  # split progress between ISD construction and VTT writing

  def _isd_progress(progress: float):
    progress_callback(progress / 2)

  # Compute ISDs

  isds = ISD.generate_isd_sequence(doc, _isd_progress)

  # process ISDs

  for i, (begin, isd) in enumerate(isds):

    end = isds[i + 1][0] if i + 1 < len(isds) else None

    for vtt_filter in vtt.filters:
      vtt_filter.process(isd)

    vtt.add_isd(isd, begin, end)

    progress_callback(0.5 + (i + 1) / len(isds) / 2)

  vtt.finish()

  return str(vtt)
