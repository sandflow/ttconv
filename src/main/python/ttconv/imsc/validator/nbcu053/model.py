#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) Sandflow Consulting LLC
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

"""NBCU-053 IMSC 1.1 Validator"""

from __future__ import annotations

from enum import Enum
from fractions import Fraction
import io
import math
import typing
from typing import Optional
import xml.etree.ElementTree as ET

from ttconv.isd import ISD
import ttconv.imsc.reader as imsc_reader
import ttconv.model as model
import ttconv.style_properties as styles

from ttconv.imsc.validator.event_handler import EventHandler
import ttconv.imsc.validator.imsc11_model as imsc11_model
import ttconv.imsc.validator.infoset as IS
from ttconv.imsc.validator.lang_helper import get_primary_language_subtag
import ttconv.imsc.validator.other_attributes as other_attrs

class FrameRate(Enum):
  '''The frame rates permitted by NBCU-053. The value of each is the expected ttp:frameRate, the expected ttp:frameRateMultiplier
  and the text that denotes the frame rate, e.g., in a configuration.'''
  FPS_23_98 = (24, Fraction(1000, 1001), "23.98")
  FPS_25 = (25, Fraction(1, 1), "25")
  FPS_29_97 = (30, Fraction(1000, 1001), "29.97")

  def __init__(self, nominal_frame_rate: int, frame_rate_multiplier: Fraction, text: str):
    self.nominal_frame_rate = nominal_frame_rate
    self.frame_rate_multiplier = frame_rate_multiplier
    self.text = text

  @classmethod
  def from_text(cls, text: str) -> FrameRate:
    '''Returns the frame rate that `text` denotes, or raises `ValueError`'''
    for frame_rate in cls:
      if frame_rate.text == text:
        return frame_rate

    raise ValueError(f"`{text}` is not a permitted frame rate")

def _validate_root_parameters(root: IS.Element, expected_frame_rate: FrameRate,
                              aspect_ratio: typing.Optional[AspectRatio]):
  dar_attr = root.get_attribute(other_attrs.DisplayAspectRatioAttribute.qname)
  if dar_attr is not None and aspect_ratio is not None:
    dar = other_attrs.DisplayAspectRatioAttribute.extract(dar_attr.value)
    dar_value = f"{float(dar):.2f}"
    if dar_value != aspect_ratio.value:
      raise ValueError(
        f"ttp:displayAspectRatio SHALL match the aspect_ratio parameter '{aspect_ratio.value}', "
        f"found '{dar_attr.value}' ('{dar_value}')"
      )

  time_base_attr = root.get_attribute(other_attrs.TimeBaseAttribute.qname)
  if time_base_attr is not None and \
    other_attrs.TimeBaseAttribute.extract(time_base_attr.value) != other_attrs.TimeBase.media:
    raise ValueError(
      f"ttp:timeBase SHALL be 'media', found '{time_base_attr.value}'"
    )

  expected_nominal_fps = expected_frame_rate.nominal_frame_rate
  expected_fps_mult = expected_frame_rate.frame_rate_multiplier

  nominal_fps_attr = root.get_attribute(other_attrs.FrameRateAttribute.qname)
  nominal_fps = 30
  if nominal_fps_attr is not None:
    nominal_fps = other_attrs.FrameRateAttribute.extract(nominal_fps_attr.value)
  if nominal_fps != expected_nominal_fps:
    raise ValueError(
      f"ttp:frameRate SHALL be '{expected_nominal_fps}', found '{nominal_fps}'"
    )

  fps_mult_attr = root.get_attribute(other_attrs.FrameRateMultiplierAttribute.qname)
  fps_mult = Fraction(1)
  if fps_mult_attr is not None:
    fps_mult = other_attrs.FrameRateMultiplierAttribute.extract(fps_mult_attr.value)
  if fps_mult != expected_fps_mult:
    raise ValueError(
      f"ttp:frameRateMultiplier SHALL be "
      f"'{expected_fps_mult.numerator} {expected_fps_mult.denominator}', found '{fps_mult}'"
    )

_EXPECTED_COLOR_SDR = styles.ColorType((0xEB, 0xEB, 0xEB, 255))  # tts:color="#EBEBEB"
_EXPECTED_COLOR_HDR = styles.ColorType((0x92, 0x92, 0x92, 255))  # tts:color="#929292"
_EXPECTED_BACKGROUND_COLOR = styles.NamedColors.transparent.value  # tts:backgroundColor="transparent"
_EXPECTED_TEXT_OUTLINE_COLOR_SDR = styles.ColorType((0x10, 0x10, 0x10, 255))  # tts:textOutline="#101010 3%"
_EXPECTED_TEXT_OUTLINE_COLOR_HDR = styles.ColorType((0x00, 0x00, 0x00, 255))  # tts:textOutline="#000000 3%"
_EXPECTED_TEXT_OUTLINE_THICKNESS = styles.LengthType(3/15*0.8, styles.LengthType.Units.rh)  # tts:textOutline="#101010 3%" of 80% at 15 rows
_EXPECTED_TEXT_OUTLINE_THICKNESS_CHARACTER_BASED = styles.LengthType(3/15, styles.LengthType.Units.rh)  # tts:textOutline="#101010 3%" of 100% at 15 rows
_EXPECTED_FONT_SIZE = styles.LengthType(80/15, styles.LengthType.Units.rh)  # tts:fontSize="80%" of 15 rows
_EXPECTED_LUMINANCE_GAIN = 1.5
_EXPECTED_FONT_SIZE_CHARACTER_BASED = styles.LengthType(100/15, styles.LengthType.Units.rh)  # tts:fontSize="100%" of 15 rows
_EXPECTED_ORIGIN = styles.CoordinateType(
  x=styles.LengthType(2.5, styles.LengthType.Units.pct),
  y=styles.LengthType(15, styles.LengthType.Units.pct)
)  # tts:origin="2.5% 15%"
_EXPECTED_EXTENT = styles.ExtentType(
  width=styles.LengthType(95, styles.LengthType.Units.pct),
  height=styles.LengthType(70, styles.LengthType.Units.pct)
)  # tts:extent="95% 70%"

_VERTICAL_REGION_IDS = frozenset(["Region_Vertical_Left", "Region_Vertical_Right"])

def _make_pct_origin(x: float, y: float) -> styles.CoordinateType:
  return styles.CoordinateType(
    x=styles.LengthType(x, styles.LengthType.Units.pct),
    y=styles.LengthType(y, styles.LengthType.Units.pct)
  )

def _make_pct_extent(w: float, h: float) -> styles.ExtentType:
  return styles.ExtentType(
    width=styles.LengthType(w, styles.LengthType.Units.pct),
    height=styles.LengthType(h, styles.LengthType.Units.pct)
  )

def _format_length(length: styles.LengthType) -> str:
  return f"{length.value}{length.units.value}"

def _format_origin(origin: typing.Optional[styles.CoordinateType]) -> str:
  if origin is None:
    return str(None)
  return f"{_format_length(origin.x)} {_format_length(origin.y)}"

def _format_extent(extent: typing.Optional[styles.ExtentType]) -> str:
  if extent is None:
    return str(None)
  return f"{_format_length(extent.width)} {_format_length(extent.height)}"

class AspectRatio(Enum):
  '''Display aspect ratio groups defined by NBCU-053 section 4.3.'''
  RATIO_2_66 = "2.66"
  RATIO_2_55 = "2.55"
  RATIO_2_40 = "2.40"
  RATIO_2_39 = "2.39"
  RATIO_2_35 = "2.35"
  RATIO_2_20 = "2.20"
  RATIO_2_15 = "2.15"
  RATIO_2_00 = "2.00"
  RATIO_1_90 = "1.90"
  RATIO_1_85 = "1.85"
  RATIO_1_78 = "1.78"
  RATIO_1_66 = "1.66"
  RATIO_1_65 = "1.65"
  RATIO_1_50 = "1.50"
  RATIO_1_47 = "1.47"
  RATIO_1_44 = "1.44"
  RATIO_1_37 = "1.37"
  RATIO_1_33 = "1.33"
  RATIO_0_56 = "0.56"  # 9:16
  RATIO_0_80 = "0.80"  # 4:5
  RATIO_1_00 = "1.00"  # 1:1

_EXPECTED_VERT_REGION_DIMS = {
  AspectRatio.RATIO_2_66: (_make_pct_origin(5, 23), _make_pct_extent(88, 54)),
  AspectRatio.RATIO_2_55: (_make_pct_origin(5, 21), _make_pct_extent(88, 60)),
  AspectRatio.RATIO_2_40: (_make_pct_origin(5, 19), _make_pct_extent(88, 62)),
  AspectRatio.RATIO_2_39: (_make_pct_origin(5, 19), _make_pct_extent(88, 62)),
  AspectRatio.RATIO_2_35: (_make_pct_origin(5, 19), _make_pct_extent(88, 62)),
  AspectRatio.RATIO_2_20: (_make_pct_origin(5, 16), _make_pct_extent(88, 72)),
  AspectRatio.RATIO_2_15: (_make_pct_origin(5, 16), _make_pct_extent(88, 72)),
  AspectRatio.RATIO_2_00: (_make_pct_origin(5, 12), _make_pct_extent(88, 78)),
  AspectRatio.RATIO_1_90: (_make_pct_origin(5, 10), _make_pct_extent(88, 80)),
  AspectRatio.RATIO_1_85: (_make_pct_origin(5, 10), _make_pct_extent(88, 80)),
  AspectRatio.RATIO_1_78: (_make_pct_origin(5, 10), _make_pct_extent(88, 80)),
  AspectRatio.RATIO_1_66: (_make_pct_origin(8.5, 10), _make_pct_extent(81, 80)),
  AspectRatio.RATIO_1_65: (_make_pct_origin(8.5, 10), _make_pct_extent(81, 80)),
  AspectRatio.RATIO_1_50: (_make_pct_origin(13, 10), _make_pct_extent(72, 80)),
  AspectRatio.RATIO_1_47: (_make_pct_origin(13, 10), _make_pct_extent(72, 80)),
  AspectRatio.RATIO_1_44: (_make_pct_origin(14, 10), _make_pct_extent(70, 80)),
  AspectRatio.RATIO_1_37: (_make_pct_origin(16, 10), _make_pct_extent(67, 80)),
  AspectRatio.RATIO_1_33: (_make_pct_origin(17, 10), _make_pct_extent(65, 80)),
  AspectRatio.RATIO_0_56: (_make_pct_origin(16, 10), _make_pct_extent(68, 80)),
  AspectRatio.RATIO_0_80: (_make_pct_origin(14, 10), _make_pct_extent(72, 80)),
  AspectRatio.RATIO_1_00: (_make_pct_origin(10, 10), _make_pct_extent(80, 80)),
}

_NON_CHARACTER_BASED_LANGUAGES = frozenset([
    # --- Latin Script ---
    "cs",  # Czech
    "da",  # Danish
    "de",  # German
    "en",  # English
    "es",  # Spanish
    "et",  # Estonian
    "fi",  # Finnish
    "fr",  # French
    "hr",  # Croatian
    "hu",  # Hungarian
    "id",  # Indonesian
    "is",  # Icelandic
    "it",  # Italian
    "lt",  # Lithuanian
    "lv",  # Latvian
    "nl",  # Dutch
    "no",  # Norwegian
    "pl",  # Polish
    "pt",  # Portuguese
    "ro",  # Romanian
    "sk",  # Slovak
    "sl",  # Slovene
    "so",  # Somali
    "sv",  # Swedish
    "sw",  # Swahili
    "tl",  # Tagalog
    "tr",  # Turkish
    "vi",  # Vietnamese

    # --- Cyrillic Script ---
    "be",  # Belarusian
    "bg",  # Bulgarian
    "kk",  # Kazakh
    "ky",  # Kyrgyz
    "mk",  # Macedonian
    "mn",  # Mongolian
    "ru",  # Russian
    "sr",  # Serbian (Cyrillic)
    "tg",  # Tajik
    "uk",  # Ukrainian

    # --- Greek Script ---
    "el",  # Modern Greek
])

def _is_character_based_lang(lang: Optional[str]) -> bool:
  tag = get_primary_language_subtag(lang) if lang is not None else None
  return tag not in _NON_CHARACTER_BASED_LANGUAGES

def _lengths_approx_equal(a: styles.LengthType, b: styles.LengthType) -> bool:
  if a.units != b.units:
    return False
  a_value = float(a.value)
  b_value = float(b.value)
  return math.isclose(a_value, b_value, rel_tol=0.001)

def _validate_styles(element: model.ContentElement, hdr: bool):
  elem_name = type(element).__name__
  expected_color = _EXPECTED_COLOR_HDR if hdr else _EXPECTED_COLOR_SDR
  expected_outline_color = _EXPECTED_TEXT_OUTLINE_COLOR_HDR if hdr else _EXPECTED_TEXT_OUTLINE_COLOR_SDR

  bg_color = element.get_style(styles.StyleProperties.BackgroundColor)
  if bg_color is not None and bg_color != _EXPECTED_BACKGROUND_COLOR:
    raise ValueError(f"{elem_name}: computed tts:backgroundColor SHALL be 'transparent', found '{bg_color}'")

  color = element.get_style(styles.StyleProperties.Color)
  if color is not None and color != expected_color:
    raise ValueError(f"{elem_name}: tts:color SHALL be '{expected_color}', found '{color}'")

  font_size: typing.Optional[styles.LengthType] = element.get_style(styles.StyleProperties.FontSize)
  if font_size is not None:
    lang = element.get_lang()
    if _is_character_based_lang(lang):
      if not _lengths_approx_equal(font_size, _EXPECTED_FONT_SIZE_CHARACTER_BASED):
        raise ValueError(
          f"{elem_name}: tts:fontSize SHALL be '100%' for character-based language '{lang}', "
          f"found '{font_size.value * 15}%'."
        )
    elif not _lengths_approx_equal(font_size, _EXPECTED_FONT_SIZE):
      raise ValueError(
        f"{elem_name}: tts:fontSize SHALL be '80%' for non-character-based languages '{lang}', "
        f"found '{font_size.value * 15}%' ."
      )

  text_outline = element.get_style(styles.StyleProperties.TextOutline)
  if text_outline is not None:
    if _is_character_based_lang(element.get_lang()):
      expected_thickness = _EXPECTED_TEXT_OUTLINE_THICKNESS_CHARACTER_BASED
    else:
      expected_thickness = _EXPECTED_TEXT_OUTLINE_THICKNESS
    if text_outline is styles.SpecialValues.none or \
      text_outline.color != expected_outline_color or \
      not _lengths_approx_equal(text_outline.thickness, expected_thickness):
        raise ValueError(
          f"{elem_name}: tts:textOutline color SHALL be '{expected_outline_color}'"
        )

  shear = element.get_style(styles.StyleProperties.Shear)
  if shear is not None and shear != 0:
    raise ValueError(
      f"{elem_name}: tts:shear SHALL NOT be used and tts:fontStyle=\"italic\" used instead."
    )


def _validate_doc_styles(
  doc: model.ContentDocument,
  expected_vert_pos: typing.Optional[typing.Tuple[styles.CoordinateType, styles.ExtentType]],
  hdr: bool
):
  # currently unreachable in practice: imsc11_model.validate() already rejects tts:writingMode
  # outside <region> as a generic IMSC 1.1 applicability error. Kept as a backstop in case that
  # generic check is ever relaxed.
  body = doc.get_body()
  if body is not None:
    for element in body.dfs_iterator():
      writing_mode = element.get_style(styles.StyleProperties.WritingMode)
      if writing_mode is not None:
        raise ValueError(
          f"{type(element).__name__}: tts:writingMode SHALL only be specified on <region> elements, "
          f"found '{writing_mode.value}'"
        )

  # region constraints
  for region in doc.iter_regions():
    # luminanceGain constraints
    gain = region.get_style(styles.StyleProperties.LuminanceGain)
    if hdr:
      if gain is None or gain != _EXPECTED_LUMINANCE_GAIN:
        raise ValueError(
          f"In HDR files, tts:luminanceGain SHALL be present and equal to '{_EXPECTED_LUMINANCE_GAIN}', "
          f"found '{gain}'."
        )
    elif gain is not None and gain != _EXPECTED_LUMINANCE_GAIN:
      raise ValueError(
        f"If present in SDR files, tts:luminanceGain SHALL be present and equal to '{_EXPECTED_LUMINANCE_GAIN}', "
        f"found '{gain}'."
      )

    # vertical text region constraints (NBCU-053 section 4)
    region_id = region.get_id()
    writing_mode = region.get_style(styles.StyleProperties.WritingMode)
    is_vertical_region = region_id in _VERTICAL_REGION_IDS
    is_vertical_writing = writing_mode == styles.WritingModeType.tbrl
    origin = region.get_style(styles.StyleProperties.Origin)
    extent = region.get_style(styles.StyleProperties.Extent)

    if is_vertical_region or is_vertical_writing:

      if not (is_vertical_region and is_vertical_writing):
        raise ValueError(
          f"Region '{region_id}': tts:writingMode SHALL be 'tbrl' if "
          f"xml:id 'Region_Vertical_Left' or 'Region_Vertical_Right', and vice vera"
        )

      if expected_vert_pos is None:
        raise ValueError(
          f"Region '{region_id}': aspect_ratio parameter SHALL be specified when vertical text is present."
        )
      if (origin, extent) != expected_vert_pos:
        expected_origin, expected_extent = expected_vert_pos
        raise ValueError(
          f"Region '{region_id}': tts:origin/tts:extent SHALL be origin='{_format_origin(expected_origin)}' "
          f"extent='{_format_extent(expected_extent)}' for the specified aspect ratio, "
          f"found origin='{_format_origin(origin)}' extent='{_format_extent(extent)}'"
        )
    else:
      if origin != _EXPECTED_ORIGIN:
        raise ValueError(
          f"Region '{region_id}': tts:origin SHALL be '{_format_origin(_EXPECTED_ORIGIN)}', "
          f"found '{_format_origin(origin)}'"
        )
      if extent != _EXPECTED_EXTENT:
        raise ValueError(
          f"Region '{region_id}': tts:extent SHALL be '{_format_extent(_EXPECTED_EXTENT)}', "
          f"found '{_format_extent(extent)}'"
        )

def validate(
  f: typing.BinaryIO,
  expected_frame_rate: FrameRate,
  hdr: bool = False,
  aspect_ratio: typing.Optional[AspectRatio] = None,
  event_handler: typing.Optional[EventHandler] = None
) -> bool:
  '''Validates `f` and returns whether no ERROR-or-above records were logged.

  `f` must be a valid IMSC 1.1 document, and validation stops at the first failure of the IMSC 1.1 model.

  `aspect_ratio` SHALL be provided if the document contains vertical text regions.
  '''

  data = f.read()
  counting_handler = imsc11_model.ErrorCountingEventHandler(event_handler)

  try:

    # first confirm the document is a conformant IMSC 1.1 document
    if not imsc11_model.validate(io.BytesIO(data), counting_handler):
      return False

    infoset = IS.Infoset.fromFile(io.BytesIO(data), counting_handler)
    if infoset is None:
      counting_handler.error("Invalid empty document")
      return False

    _validate_root_parameters(infoset.root, expected_frame_rate, aspect_ratio)

    if infoset.root.get_attribute(other_attrs.DisplayAspectRatioAttribute.qname) is not None:
      expected_vert_pos = (_EXPECTED_ORIGIN, _EXPECTED_EXTENT)
    else:
      expected_vert_pos = _EXPECTED_VERT_REGION_DIMS[aspect_ratio] if aspect_ratio is not None else None

    doc = imsc_reader.to_model(ET.parse(io.BytesIO(data)))
    if doc is None:
      counting_handler.error("Invalid empty document")
      return False

    _validate_doc_styles(doc, expected_vert_pos, hdr)

    isd_sequence = ISD.generate_isd_sequence(doc)
    for _, isd in isd_sequence:
      for isd_region in isd.iter_regions():
        _validate_styles(isd_region, hdr)
        for element in isd_region.dfs_iterator():
          _validate_styles(element, hdr)

  except ValueError as ve:
    counting_handler.error("%s", ve)
    return False

  return counting_handler.error_count == 0
