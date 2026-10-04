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

'''TTML feature designation membership checks, per TTML2 \u00A7E.2 Table E-1 – Feature Support'''

import urllib.parse as URL

import ttconv.imsc.namespaces as NS
from ttconv.imsc.validator.uri_helper import is_absolute_uri, is_relative_uri
from ttconv.imsc.validator.xml_helper import is_valid_xml_name

# All feature designations recognized by TTML2, per Table E-1.
_TTML2_FEATURES = frozenset({
  '#animate', '#animate-fill', '#animate-minimal', '#animate-paced', '#animate-repeat', '#animate-spline',
  '#animation', '#animation-out-of-line', '#animation-version-2', '#audio', '#audio-description', '#audio-speech',
  '#background', '#background-image', '#backgroundClip', '#backgroundColor', '#backgroundColor-block', '#backgroundColor-inline',
  '#backgroundColor-region', '#backgroundExtent', '#backgroundImage', '#backgroundOrigin', '#backgroundPosition', '#backgroundRepeat',
  '#base', '#base-general', '#base-version-2', '#bidi', '#bidi-version-2', '#border',
  '#border-block', '#border-inline', '#border-radii', '#border-radii-1', '#border-radii-2', '#border-region',
  '#bpd', '#cellResolution', '#chunk', '#clockMode', '#clockMode-gps', '#clockMode-local',
  '#clockMode-utc', '#color', '#condition', '#condition-fn-media', '#condition-fn-parameter', '#condition-fn-supports',
  '#condition-primary', '#content', '#content-sizing', '#contentProfiles', '#contentProfiles-combined', '#core',
  '#data', '#direction', '#disparity', '#display', '#display-block', '#display-inline',
  '#display-inlineBlock', '#display-region', '#display-version-2', '#displayAlign', '#displayAlign-block', '#displayAlign-justify',
  '#displayAlign-region', '#displayAlign-relative', '#displayAlign-version-2', '#displayAspectRatio', '#dropMode', '#dropMode-dropNTSC',
  '#dropMode-dropPAL', '#dropMode-nonDrop', '#embedded-audio', '#embedded-content', '#embedded-data', '#embedded-font',
  '#embedded-image', '#extent', '#extent-auto', '#extent-auto-version-2', '#extent-contain', '#extent-cover',
  '#extent-full-version-2', '#extent-image', '#extent-length', '#extent-length-version-2', '#extent-measure', '#extent-region',
  '#extent-region-version-2', '#extent-root', '#extent-root-version-2', '#extent-version-2', '#font', '#fontFamily',
  '#fontFamily-generic', '#fontFamily-non-generic', '#fontKerning', '#fontSelectionStrategy', '#fontSelectionStrategy-character', '#fontShear',
  '#fontSize', '#fontSize-anamorphic', '#fontSize-isomorphic', '#fontStyle', '#fontStyle-italic', '#fontStyle-oblique',
  '#fontVariant', '#fontWeight', '#fontWeight-bold', '#frameRate', '#frameRateMultiplier', '#gain',
  '#image', '#image-png', '#initial', '#ipd', '#layout', '#length',
  '#length-cell', '#length-em', '#length-integer', '#length-negative', '#length-percentage', '#length-pixel',
  '#length-positive', '#length-real', '#length-root-container-relative', '#length-version-2', '#letterSpacing', '#lineBreak-uax14',
  '#lineHeight', '#lineShear', '#luminanceGain', '#markerMode', '#markerMode-continuous', '#markerMode-discontinuous',
  '#metadata', '#metadata-item', '#metadata-version-2', '#nested-div', '#nested-span', '#opacity',
  '#opacity-block', '#opacity-inline', '#opacity-region', '#opacity-version-2', '#origin', '#overflow',
  '#overflow-visible', '#padding', '#padding-1', '#padding-2', '#padding-3', '#padding-4',
  '#padding-block', '#padding-inline', '#padding-region', '#padding-version-2', '#pan', '#permitFeatureNarrowing',
  '#permitFeatureWidening', '#pitch', '#pixelAspectRatio', '#position', '#presentation', '#presentation-version-2',
  '#processorProfiles', '#processorProfiles-combined', '#profile', '#profile-full-version-2', '#profile-nesting', '#profile-version-2',
  '#region-implied-animation', '#region-inline', '#region-timing', '#resources', '#ruby', '#ruby-full',
  '#rubyAlign', '#rubyAlign-minimal', '#rubyAlign-withBase', '#rubyPosition', '#rubyReserve', '#set',
  '#set-fill', '#set-multiple-styles', '#set-repeat', '#shear', '#showBackground', '#source',
  '#speak', '#speech', '#structure', '#styling', '#styling-chained', '#styling-inheritance-content',
  '#styling-inheritance-region', '#styling-inline', '#styling-nested', '#styling-referential', '#subFrameRate', '#textAlign',
  '#textAlign-absolute', '#textAlign-justify', '#textAlign-relative', '#textAlign-version-2', '#textCombine', '#textDecoration',
  '#textDecoration-over', '#textDecoration-through', '#textDecoration-under', '#textEmphasis', '#textEmphasis-color', '#textEmphasis-minimal',
  '#textEmphasis-quoted-string', '#textOrientation', '#textOutline', '#textOutline-blurred', '#textOutline-unblurred', '#textShadow',
  '#tickRate', '#time-clock', '#time-clock-with-frames', '#time-offset', '#time-offset-with-frames', '#time-offset-with-ticks',
  '#time-wall-clock', '#timeBase-clock', '#timeBase-media', '#timeBase-smpte', '#timeContainer', '#timing',
  '#transformation', '#transformation-version-2', '#unicodeBidi', '#unicodeBidi-isolate', '#unicodeBidi-version-2', '#validation',
  '#visibility', '#visibility-block', '#visibility-image', '#visibility-inline', '#visibility-region', '#visibility-version-2',
  '#wrapOption', '#writingMode', '#writingMode-horizontal', '#writingMode-horizontal-lr', '#writingMode-horizontal-rl', '#writingMode-vertical',
  '#xlink', '#zIndex',
})


# Standard profile designators, per TTML2, Table 5-2 and IMSC 1.1.
_TTML2_STANDARD_PROFILE_DESIGNATORS = frozenset({
  NS.TT_PROFILE + "dfxp-full",
  NS.TT_PROFILE + "dfxp-presentation",
  NS.TT_PROFILE + "dfxp-transformation",
  NS.TT_PROFILE + "sdp-us",
  NS.TT_PROFILE + "ttml2-full",
  NS.TT_PROFILE + "ttml2-presentation",
  NS.TT_PROFILE + "ttml2-transformation",
  NS.TT_PROFILE + "imsc1.1/text",
  NS.TT_PROFILE + "imsc1.1/image",
  NS.TT_PROFILE + "imsc1/text",
  NS.TT_PROFILE + "imsc1/image",
})

def absolutize_profile_designator(uri: str) -> str:
  if uri is None:
    raise ValueError("Null URI")
  return URL.urljoin(NS.TT_PROFILE, uri) if is_relative_uri(uri) else uri

def is_ttml2_profile_designator(uri: str) -> bool:
  if uri is None:
    return False
  elif is_relative_uri(uri):
    uri = absolutize_profile_designator(uri)
    return uri in _TTML2_STANDARD_PROFILE_DESIGNATORS
  elif uri.startswith(NS.TT_PROFILE):
    return uri in _TTML2_STANDARD_PROFILE_DESIGNATORS
  return is_absolute_uri(uri)

def is_ttml2_feature_ns(value: str) -> bool:
  """Returns True if value is exactly the TT Feature Namespace URI"""
  return value == NS.TTF

def is_ttml2_feature_designation(value: str) -> bool:
  """Returns True if value is a valid TTML2 feature designation"""
  if not value.startswith(NS.TTF):
    return False
  return value[len(NS.TTF):] in _TTML2_FEATURES

def is_ttml2_extension_designation(designation: str) -> bool:
  """Returns True if value is a valid TTML2 extension designation"""
  if designation is None:
    return False
  if designation.startswith(NS.TTF):
    return False
  # there are no extensions defined in the TTML extension namespace
  if designation.startswith(NS.TTE):
    return False
  uri_parts = designation.split("#", 1)
  if len(uri_parts) != 2:
    return False
  abs_uri, fragment = uri_parts
  return is_absolute_uri(abs_uri) and is_valid_xml_name(fragment)

