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

'''Unit tests for the STL reader'''

# pylint: disable=R0201,C0115,C0116

import unittest
from ttconv.model import Br, Region, Span
import ttconv.stl.reader
import ttconv.style_properties as styles
from ttconv.time_code import SmpteTimeCode, FPS_25

class STLReaderTests(unittest.TestCase):

  def test_irt_requirement_0056_001_modfied(self):
    '''Testing subtitles in different subtitle groups (SGN)'''
    with open("src/test/resources/stl/irt/requirement-0056-001_modified.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      
      div_list = list(doc.get_body())
      self.assertEqual(len(div_list), 3)
      
      p1_span = div_list[0].first_child().first_child()
      p2_span = div_list[0].first_child().next_sibling().first_child()
      p3_span = div_list[1].first_child().first_child()
      p4_span = div_list[2].first_child().first_child()
      self.assertEqual(p1_span.first_child().get_text(), "Subtitle 1 Group 1")
      self.assertEqual(p2_span.first_child().get_text(), "Subtitle 2 Group 1")
      self.assertEqual(p3_span.first_child().get_text(), "Subtitle 3 Group 2")
      self.assertEqual(p4_span.first_child().get_text(), "Subtitle 4 Group 3")

  def test_irt_requirement_0061_001(self):
    '''Testing Time Code In with value media 25 frames lowerbounds'''  
    with open("src/test/resources/stl/irt/requirement-0061-001.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      p = doc.get_body().first_child().first_child()
      self.assertEqual(p.get_begin(),
                      SmpteTimeCode.parse("00:00:00:00",FPS_25).to_temporal_offset())
   
  def test_irt_requirement_0061_004_modified(self):
    '''Testing Time Code In with value media 25 frames upperbounds'''
    with open("src/test/resources/stl/irt/requirement-0061-004_modified.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      p = doc.get_body().first_child().first_child()
      self.assertEqual(p.get_begin(),
                      SmpteTimeCode.parse("23:59:59:24",FPS_25).to_temporal_offset())

  def test_irt_requirement_0062_001(self):
    '''Testing Time Code Out with value media 25 frames lower bound'''
    with open("src/test/resources/stl/irt/requirement-0062-001.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      p = doc.get_body().first_child().first_child()
      self.assertEqual(p.get_end(),
                      SmpteTimeCode.parse("00:00:00:00",FPS_25).to_temporal_offset())

  def test_irt_requirement_0062_002_modified(self):
    '''Testing Time Code Out with value media 25 frames upper bound'''
    with open("src/test/resources/stl/irt/requirement-0062-002_modified.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      p = doc.get_body().first_child().first_child()
      self.assertEqual(p.get_end(),
                       SmpteTimeCode.parse("23:59:59:24",FPS_25).to_temporal_offset())

  def test_irt_requirement_0067_001(self):
    '''Justification Code 01h mapping'''
    with open("src/test/resources/stl/irt/requirement-0067-001.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      p = doc.get_body().first_child().first_child()
      self.assertEqual(p.get_style(styles.StyleProperties.TextAlign),
                       styles.TextAlignType.start)

  def test_irt_requirement_0068_001(self):
    '''Testing JC with value "02h"'''
    with open("src/test/resources/stl/irt/requirement-0068-001.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      p = doc.get_body().first_child().first_child()
      self.assertEqual(p.get_style(styles.StyleProperties.TextAlign),
                       styles.TextAlignType.center)

  def test_irt_requirement_0069_001(self):
    '''Justification Code 03h mapping'''
    with open("src/test/resources/stl/irt/requirement-0069-001.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      p = doc.get_body().first_child().first_child()
      self.assertEqual(p.get_style(styles.StyleProperties.TextAlign),
                       styles.TextAlignType.end)
  
  def test_irt_requirement_0071_002(self):
    '''Testing Text Field conversion to one or more tt:span elements (no StartBox/EndBox)'''
    with open("src/test/resources/stl/irt/requirement-0071-002.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      text = doc.get_body()\
                .first_child()\
                .first_child()\
                .first_child()\
                .first_child()\
                .get_text()
      self.assertEqual(text, "Test1 Test2") 

  def test_irt_requirement_0074_001(self):
    '''Testing that the newline element is mapped the tt:br element'''
    with open("src/test/resources/stl/irt/requirement-0074-001.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      p_childs = list(doc.get_body().first_child().first_child())
      self.assertTrue(isinstance(p_childs[1], Br))
      
  
  def test_irt_requirement_0076_001(self):
    '''Testing Control Codes mapping for AlphaBlack'''
    with open("src/test/resources/stl/irt/requirement-0076-001.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(color_second_span, styles.NamedColors.black.value)

  def test_irt_requirement_0076_002(self):
    '''Testing Control Codes mapping for AlphaWhite'''
    with open("src/test/resources/stl/irt/requirement-0076-002.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(color_second_span, styles.NamedColors.white.value)

  def test_irt_requirement_0076_003(self):
    '''Testing Control Codes mapping for AlphaRed'''
    with open("src/test/resources/stl/irt/requirement-0076-003.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(color_second_span, styles.NamedColors.red.value)

  def test_irt_requirement_0076_004(self):
    '''Testing Control Codes mapping for AlphaGreen'''
    with open("src/test/resources/stl/irt/requirement-0076-004.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(color_second_span, styles.NamedColors.lime.value)
 
  def test_irt_requirement_0076_005(self):
    '''Testing Control Codes mapping for AlphaYellow,'''
    with open("src/test/resources/stl/irt/requirement-0076-005.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(color_second_span, styles.NamedColors.yellow.value)

  def test_irt_requirement_0076_006(self):
    '''Testing Control Codes mapping for AlphaBlue'''
    with open("src/test/resources/stl/irt/requirement-0076-006.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(color_second_span, styles.NamedColors.blue.value)
 
  def test_irt_requirement_0076_007(self):
    '''Testing Control Codes mapping for AlphaMagenta'''
    with open("src/test/resources/stl/irt/requirement-0076-007.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(color_second_span, styles.NamedColors.magenta.value)
  
  def test_irt_requirement_0076_008(self):
    '''Testing Control Codes mapping for AlphaCyan'''
    with open("src/test/resources/stl/irt/requirement-0076-008.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(color_second_span, styles.NamedColors.cyan.value)
   
  def test_irt_requirement_0076_009(self):
    '''Testing Control Codes mapping for BlackBackground'''
    with open("src/test/resources/stl/irt/requirement-0076-009.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_first_span = spans[0].get_style(styles.StyleProperties.BackgroundColor)
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      self.assertEqual(background_color_first_span, styles.NamedColors.white.value)
      self.assertEqual(background_color_second_span, styles.NamedColors.black.value)
 
  def test_irt_requirement_0077_001(self):
    '''Testing DSC with value "1" and no style information'''
    with open("src/test/resources/stl/irt/requirement-0077-001.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_first_span = spans[0].get_style(styles.StyleProperties.BackgroundColor)
      self.assertEqual(background_color_first_span, styles.NamedColors.black.value)
 
  def test_irt_requirement_0077_002(self):
    '''Testing DSC with value "2" and no style information'''
    with open("src/test/resources/stl/irt/requirement-0077-002.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_first_span = spans[0].get_style(styles.StyleProperties.BackgroundColor)
      self.assertEqual(background_color_first_span, styles.NamedColors.black.value)

  def test_irt_requirement_0086_001(self):
    '''Testing EndBox element mapping with three closing EndBox 
       elements and without changing the colors'''
    with open("src/test/resources/stl/irt/requirement-0086-001.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      p = doc.get_body().first_child().first_child()
      spans = [s for s in list(p) if isinstance(s, Span)]
      self.assertEqual(len(spans), 3)

  def test_irt_requirement_0087_001(self):
    '''Testing StartBox element mapping with 3x2 StartBox elements 
      and with referencing a style with the appropriate background 
      and foreground color'''
    with open("src/test/resources/stl/irt/requirement-0087-001.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      p = doc.get_body().first_child().first_child()
      spans = [s for s in list(p) if isinstance(s, Span)]
      background_color_first_span = spans[0].get_style(styles.StyleProperties.BackgroundColor)
      color_first_span = spans[0].get_style(styles.StyleProperties.Color)
      self.assertEqual(len(spans), 3)
      self.assertEqual(background_color_first_span, styles.NamedColors.black.value)
      self.assertEqual(color_first_span, styles.NamedColors.white.value)   

  def test_irt_requirement_0090_001(self):
    '''Testing BlackBackground with AlphaBlack'''
    with open("src/test/resources/stl/irt/requirement-0090-001.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      self.assertEqual(background_color_second_span, styles.NamedColors.black.value)

 
  def test_irt_requirement_0090_002(self):
    '''Testing BlackBackground with AlphaBlue'''
    with open("src/test/resources/stl/irt/requirement-0090-002.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(background_color_second_span, styles.NamedColors.black.value)
      self.assertEqual(color_second_span, styles.NamedColors.blue.value)
  
  def test_irt_requirement_0090_003(self):
    '''Testing BlackBackground with AlphaCyan'''
    with open("src/test/resources/stl/irt/requirement-0090-003.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(background_color_second_span, styles.NamedColors.black.value)
      self.assertEqual(color_second_span, styles.NamedColors.cyan.value)
  
  def test_irt_requirement_0090_004(self):
    '''Testing BlackBackground with AlphaGreen'''
    with open("src/test/resources/stl/irt/requirement-0090-004.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(background_color_second_span, styles.NamedColors.black.value)
      self.assertEqual(color_second_span, styles.NamedColors.lime.value)
  
  def test_irt_requirement_0090_005(self):
    '''Testing BlackBackground with AlphaMagenta'''
    with open("src/test/resources/stl/irt/requirement-0090-005.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(background_color_second_span, styles.NamedColors.black.value)
      self.assertEqual(color_second_span, styles.NamedColors.magenta.value)
  
  def test_irt_requirement_0090_006(self):
    '''Testing BlackBackground with AlphaRed'''
    with open("src/test/resources/stl/irt/requirement-0090-006.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(background_color_second_span, styles.NamedColors.black.value)
      self.assertEqual(color_second_span, styles.NamedColors.red.value)
  
  def test_irt_requirement_0090_007(self):
    '''Testing BlackBackground with AlphaWhite'''
    with open("src/test/resources/stl/irt/requirement-0090-007.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(background_color_second_span, styles.NamedColors.black.value)
      self.assertEqual(color_second_span, styles.NamedColors.white.value)
  
  def test_irt_requirement_0090_008(self):
    '''Testing BlackBackground with AlphaYellow'''
    with open("src/test/resources/stl/irt/requirement-0090-008.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(background_color_second_span, styles.NamedColors.black.value)
      self.assertEqual(color_second_span, styles.NamedColors.yellow.value)
  
  def test_irt_requirement_0090_009(self):
    '''Testing unchanging BlackBackground'''
    with open("src/test/resources/stl/irt/requirement-0090-009.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(background_color_second_span, styles.NamedColors.black.value)
      self.assertEqual(color_second_span, styles.NamedColors.white.value)

  def test_irt_requirement_0091_001(self):
    '''Testing NewBackground with AlphaBlack'''
    with open("src/test/resources/stl/irt/requirement-0091-001.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(background_color_second_span, styles.NamedColors.black.value)
      self.assertEqual(color_second_span, styles.NamedColors.black.value)
  
  def test_irt_requirement_0091_002(self):
    '''Testing NewBackground with AlphaBlue'''
    with open("src/test/resources/stl/irt/requirement-0091-002.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_first_span = spans[0].get_style(styles.StyleProperties.BackgroundColor)
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(background_color_first_span, styles.NamedColors.black.value)
      self.assertEqual(background_color_second_span, styles.NamedColors.blue.value)
      self.assertEqual(color_second_span, styles.NamedColors.black.value)
  
  def test_irt_requirement_0091_003(self):
    '''Testing NewBackground with AlphaCyan'''
    with open("src/test/resources/stl/irt/requirement-0091-003.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(background_color_second_span, styles.NamedColors.cyan.value)
      self.assertEqual(color_second_span, styles.NamedColors.black.value)
  
  def test_irt_requirement_0091_004(self):
    '''Testing NewBackground with AlphaGreen'''
    with open("src/test/resources/stl/irt/requirement-0091-004.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(background_color_second_span, styles.NamedColors.lime.value)
      self.assertEqual(color_second_span, styles.NamedColors.black.value)
  
  def test_irt_requirement_0091_005(self):
    '''Testing NewBackground with AlphaMagenta'''
    with open("src/test/resources/stl/irt/requirement-0091-005.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(background_color_second_span, styles.NamedColors.magenta.value)
      self.assertEqual(color_second_span, styles.NamedColors.black.value)

  def test_irt_requirement_0091_006(self):
    '''Testing NewBackground with AlphaRed'''
    with open("src/test/resources/stl/irt/requirement-0091-006.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(background_color_second_span, styles.NamedColors.red.value)
      self.assertEqual(color_second_span, styles.NamedColors.black.value)   
  
  def test_irt_requirement_0091_007(self):
    '''Testing NewBackground with AlphaWhite'''
    with open("src/test/resources/stl/irt/requirement-0091-007.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(background_color_second_span, styles.NamedColors.white.value)
      self.assertEqual(color_second_span, styles.NamedColors.black.value)
  
  def test_irt_requirement_0091_008(self):
    '''Testing NewBackground with AlphaYellow'''
    with open("src/test/resources/stl/irt/requirement-0091-008.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(background_color_second_span, styles.NamedColors.yellow.value)
      self.assertEqual(color_second_span, styles.NamedColors.black.value)
  
  def test_irt_requirement_0091_009(self):
    '''Testing unchanging NewBackground'''
    with open("src/test/resources/stl/irt/requirement-0091-009.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_second_span = spans[1].get_style(styles.StyleProperties.BackgroundColor)
      color_second_span = spans[1].get_style(styles.StyleProperties.Color)
      self.assertEqual(background_color_second_span, styles.NamedColors.lime.value)
      self.assertEqual(color_second_span, styles.NamedColors.black.value)

  def test_setting_background_before_startbox(self):
    '''Testing NewBackground Control Code before StartBox'''    
    with open("src/test/resources/stl/sandflow/setting_background_before_startbox.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      spans = list(doc.get_body().first_child().first_child())
      background_color_first_span = spans[0].get_style(styles.StyleProperties.BackgroundColor)
      self.assertEqual(background_color_first_span, styles.NamedColors.yellow.value)

  def test_multi_tti_subtitle(self):
    '''Testing subtitle that spans over multiple TTI blocks with different EBN values'''
    with open("src/test/resources/stl/sandflow/multi_tti_subtitle.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      text = doc.get_body()\
                .first_child()\
                .first_child()\
                .first_child()\
                .first_child()\
                .get_text()
      self.assertEqual(text, "Foo Bar Baz")

  def test_tcp_processing(self):
    '''Testing use of TCP from GSI Block'''  
    with open("src/test/resources/stl/sandflow/test_tcp_processing.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      p_list = list(doc.get_body().first_child())
      self.assertEqual(p_list[0].get_begin(),
                      SmpteTimeCode.parse("00:00:00:00",FPS_25).to_temporal_offset())
      self.assertEqual(p_list[0].get_end(),
                      SmpteTimeCode.parse("00:00:01:24",FPS_25).to_temporal_offset())

  def test_default_font_stack(self):
    '''Testing default font stack'''  
    with open("src/test/resources/stl/sandflow/setting_background_before_startbox.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      self.assertEqual(doc.get_body().get_style(
        styles.StyleProperties.FontFamily),
        ("Verdana", "Arial", "Tiresias", styles.GenericFontFamilyType.sansSerif)
      )

  def test_cumulative_set(self):
    '''Testing cumulative subtitles'''
    with open("src/test/resources/stl/sandflow/cumulative_set.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      p_list = list(doc.get_body().first_child())
      p1_span = p_list[0].first_child()
      self.assertEqual(p1_span.first_child().get_text(),
                       "Not part of cumulative set.")
      
      p2_children = list(p_list[1])
      self.assertEqual(len(p2_children), 4)

      span1_text = p2_children[0].first_child().first_child().get_text()
      span2_text = p2_children[1].first_child().first_child().get_text()
      span3_text = p2_children[2].first_child().first_child().get_text()
      span4_text = p2_children[3].first_child().first_child().get_text()

      self.assertEqual(span1_text, "1")
      self.assertEqual(span2_text, "2")
      self.assertEqual(span3_text, "3")
      self.assertEqual(span4_text, "4")
  
  def test_vp18_3_lines(self):
    '''Testing vertical positioning of multi-row subtitle'''
    with open("src/test/resources/stl/sandflow/vp18_3_lines.stl", "rb") as f:
      doc = ttconv.stl.reader.to_model(f)
      p = doc.get_body().first_child().first_child()
      region = p.get_region()
      region_extent = region.get_style(styles.StyleProperties.Extent).height.value
      self.assertEqual(region_extent, 80)


if __name__ == '__main__':
  unittest.main()
