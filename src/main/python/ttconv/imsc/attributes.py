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

'''Process IMSC non-style attributes'''

import re
import logging
import ttconv.model as model
import ttconv.imsc.utils as utils
import ttconv.imsc.namespaces as ns
#import xml.etree.ElementTree as et

LOGGER = logging.getLogger(__name__)

class XMLIDAttribute:
  '''xml:id attribute
  '''

  qn = '{http://www.w3.org/XML/1998/namespace}id'

  @staticmethod
  def extract(ttml_element):
    return ttml_element.attrib.get(XMLIDAttribute.qn)



class XMLLangAttribute:
  '''xml:lang attribute
  '''

  qn = '{http://www.w3.org/XML/1998/namespace}lang'

  @staticmethod
  def extract(ttml_element):
    return ttml_element.attrib.get(XMLLangAttribute.qn)

  @staticmethod
  def set(ttml_element, lang):
    ttml_element.set(XMLLangAttribute.qn, lang)

class XMLSpaceAttribute:
  '''xml:space attribute
  '''

  qn = '{http://www.w3.org/XML/1998/namespace}space'

  @staticmethod
  def extract(ttml_element):

    value = ttml_element.attrib.get(XMLSpaceAttribute.qn)

    r = None

    if value is not None:

      try: 
        r = model.WhiteSpaceHandling(value)
      except ValueError:
        LOGGER.error("Bad xml:space value (%s)", value)
    
    return r



class RegionAttribute:
  '''TTML region attribute'''

  qn = "region"

  @staticmethod
  def extract(ttml_element):
    return ttml_element.attrib.get(RegionAttribute.qn)

  @staticmethod
  def set(ttml_element, res):
    ttml_element.set(XMLIDAttribute.qn, res)


class CellResolutionAttribute:
  '''ttp:cellResolution attribute
  '''

  qn = f"{{{ns.TTP}}}cellResolution"

  _CELL_RESOLUTION_RE = re.compile(r"(\d+) (\d+)")

  @staticmethod
  def extract(ttml_element) -> model.CellResolutionType:

    cr = ttml_element.attrib.get(CellResolutionAttribute.qn)

    if cr is not None:

      m = CellResolutionAttribute._CELL_RESOLUTION_RE.match(cr)

      if m is not None:

        return model.CellResolutionType(int(m.group(1)), int(m.group(2)))

      LOGGER.error("ttp:cellResolution invalid syntax")

    # default value in TTML

    return model.CellResolutionType(rows=15, columns=32)

  @staticmethod
  def set(ttml_element, res):
    ttml_element.set(CellResolutionAttribute.qn, f"{res.rows:.0f}px {res.columns:.0f}px")

class ExtentAttribute:
  '''ttp:extent attribute on \\<tt\\>
  '''

  qn = f"{{{ns.TTS}}}extent"

  @staticmethod
  def extract(ttml_element) -> model.PixelResolutionType:

    extent = ttml_element.attrib.get(ExtentAttribute.qn)

    if extent is not None:

      s = extent.split(" ")

      (w, w_units) = utils.parse_length(s[0])

      (h, h_units) = utils.parse_length(s[1])

      if w_units != "px" or h_units != "px":
        LOGGER.error("ttp:extent on <tt> does not use px units")
        return None

      return model.PixelResolutionType(w, h)

    return None

  @staticmethod
  def set(ttml_element, res):
    ttml_element.set(ExtentAttribute.qn, 
    f"{res.width:.0f} {res.height:.0f}")

class ActiveAreaAttribute:
  '''ittp:activeArea attribute on \\<tt\\>
  '''

  qn = f"{{{ns.ITTP}}}activeArea"

  @staticmethod
  def extract(ttml_element) -> model.ActiveAreaType:

    aa = ttml_element.attrib.get(ActiveAreaAttribute.qn)

    if aa is not None:

      s = aa.split(" ")

      if len(s) != 4:
        LOGGER.error("Syntax error in ittp:activeArea on <tt>")
        return None

      (left_offset, left_offset_units) = utils.parse_length(s[0])

      (top_offset, top_offset_units) = utils.parse_length(s[1])

      (w, w_units) = utils.parse_length(s[2])

      (h, h_units) = utils.parse_length(s[3])

      if w_units != "%" or h_units != "%" or left_offset_units != "%" or top_offset_units != "%":
        LOGGER.error("ittp:activeArea on <tt> must use % units")
        return None

      return model.ActiveAreaType(
        left_offset / 100,
        top_offset / 100,
        w / 100,
        h / 100
        )

    return None

  @staticmethod
  def set(ttml_element, activeArea):
    ttml_element.set(ActiveAreaAttribute.qn, 
      f"{(activeArea.left_offset * 100):.0f}% {(activeArea.top_offset * 100):.0f}% {(activeArea.width * 100):.0f}% {activeArea.height * 100:.0f}%")
