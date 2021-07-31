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
import ttconv.stl.reader

class STLReaderTests(unittest.TestCase):

  def test_irt_requirement_0164_001(self):
    with open("src/test/resources/stl/irt/requirement-0164-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  def test_irt_requirement_0224_001(self):
    with open("src/test/resources/stl/irt/requirement-0224-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  def test_irt_requirement_0213_001(self):
    with open("src/test/resources/stl/irt/requirement-0213-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  def test_irt_requirement_0213_002(self):
    with open("src/test/resources/stl/irt/requirement-0213-002.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  def test_irt_requirement_0213_003(self):
    with open("src/test/resources/stl/irt/requirement-0213-003.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  def test_irt_requirement_0213_004(self):
    with open("src/test/resources/stl/irt/requirement-0213-004.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)


  """
  --------------------------------------
  IRT Requirement 61
  --------------------------------------
  title: Time Code In mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0061-001
  --------------------------------------
  title: Testing Time Code In with value media 25 frames lowerbounds
  --------------------------------------
  """  
  def test_irt_requirement_0061_001(self):
    with open("src/test/resources/stl/irt/requirement-0061-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/@begin 
  text: The begin attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p[position() = 1] 
  condition: @begin = '00:00:00.000' 
  text: Expected value: "00:00:00.000"  ""
  """  
  
  """
  --------------------------------------
  Test 0061-002
  --------------------------------------
  title: Testing Time Code In with value media 25 frames upperbounds
  --------------------------------------
  """  
  def test_irt_requirement_0061_002(self):
    with open("src/test/resources/stl/irt/requirement-0061-002.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/@begin 
  text: The begin attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p[position() = 1] 
  condition: @begin = '23:59:59.960' 
  text: Expected value: "23:59:59.960"  ""
  """  
  
  """
  --------------------------------------
  Test 0061-003
  --------------------------------------
  title: Testing Time Code In with value smpte 25 frames lower bound
  --------------------------------------
  """  
  def test_irt_requirement_0061_003(self):
    with open("src/test/resources/stl/irt/requirement-0061-003.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/@begin 
  text: The begin attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p[position() = 1] 
  condition: @begin = '00:00:00:00' 
  text: Expected value: "00:00:00:00"  ""
  """  
  
  """
  --------------------------------------
  Test 0061-004
  --------------------------------------
  title: Testing Time Code In with value smpte 25 frames upper bound
  --------------------------------------
  """  
  def test_irt_requirement_0061_004(self):
    with open("src/test/resources/stl/irt/requirement-0061-004.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/@begin 
  text: The begin attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p[position() = 1] 
  condition: @begin = '23:59:59:24' 
  text: Expected value: "23:59:59:24"  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 62
  --------------------------------------
  title: Time Code Out mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0062-001
  --------------------------------------
  title: Testing Time Code Out with value media 25 frames lower bound
  --------------------------------------
  """  
  def test_irt_requirement_0062_001(self):
    with open("src/test/resources/stl/irt/requirement-0062-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/@end 
  text: The end attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p[position() = 1] 
  condition: @end = '00:00:00.000' 
  text: Expected value: "00:00:00.000"  ""
  """  
  
  """
  --------------------------------------
  Test 0062-002
  --------------------------------------
  title: Testing Time Code Out with value media 25 frames upper bound
  --------------------------------------
  """  
  def test_irt_requirement_0062_002(self):
    with open("src/test/resources/stl/irt/requirement-0062-002.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/@end 
  text: The end attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p[position() = 1] 
  condition: @end = '23:59:59.960' 
  text: Expected value: "23:59:59.960"  ""
  """  
  
  """
  --------------------------------------
  Test 0062-003
  --------------------------------------
  title: Testing Time Code Out with value smpte 25 frames lower bound
  --------------------------------------
  """  
  def test_irt_requirement_0062_003(self):
    with open("src/test/resources/stl/irt/requirement-0062-003.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/@end 
  text: The end attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p[position() = 1] 
  condition: @end = '00:00:00:00' 
  text: Expected value: "00:00:00:00"  ""
  """  
  
  """
  --------------------------------------
  Test 0062-004
  --------------------------------------
  title: Testing Time Code Out with value smpte 25 frames upper bound
  --------------------------------------
  """  
  def test_irt_requirement_0062_004(self):
    with open("src/test/resources/stl/irt/requirement-0062-004.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/@end 
  text: The end attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p[position() = 1] 
  condition: @end = '23:59:59:24' 
  text: Expected value: "23:59:59:24"  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 67
  --------------------------------------
  title: Justification Code 01h mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0067-001
  --------------------------------------
  title: Testing JC with value "01h"
  --------------------------------------
  """  
  def test_irt_requirement_0067_001(self):
    with open("src/test/resources/stl/irt/requirement-0067-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span 
  text: The tt:span element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: @style=//tt:tt/tt:head/tt:styling/tt:style[@tts:textAlign='start']/@xml:id 
  text: Expected value: "singleHeightLeft"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: string-length(./text())=string-length(normalize-space(./text())) 
  text: Expected value: ""  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 68
  --------------------------------------
  title: Justification Code 02h mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0068-001
  --------------------------------------
  title: Testing JC with value "02h"
  --------------------------------------
  """  
  def test_irt_requirement_0068_001(self):
    with open("src/test/resources/stl/irt/requirement-0068-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span 
  text: The tt:span element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: @style=//tt:tt/tt:head/tt:styling/tt:style[@tts:textAlign='center']/@xml:id 
  text: Expected value: "singleHeightCenter"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: string-length(./text())=string-length(normalize-space(./text())) 
  text: Expected value: ""  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 69
  --------------------------------------
  title: Justification Code 03h mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0069-001
  --------------------------------------
  title: Testing JC with value "03h"
  --------------------------------------
  """  
  def test_irt_requirement_0069_001(self):
    with open("src/test/resources/stl/irt/requirement-0069-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span 
  text: The tt:span element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: @style=//tt:tt/tt:head/tt:styling/tt:style[@tts:textAlign='end']/@xml:id 
  text: Expected value: "singleHeightRight"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: string-length(./text())=string-length(normalize-space(./text())) 
  text: Expected value: ""  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 71
  --------------------------------------
  title: Text Field mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0071-001
  --------------------------------------
  title: Testing Text Field conversion to one or more tt:span elements
  --------------------------------------
  """  
  def test_irt_requirement_0071_001(self):
    with open("src/test/resources/stl/irt/requirement-0071-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p[position() = 1] 
  condition: count(tt:span) >= 1 
  text: Expected value: "number of tt:span elements greater or equal 1"  ""
  """  
  
  """
  --------------------------------------
  Test 0071-002
  --------------------------------------
  title: Testing Text Field conversion to one or more tt:span elements (no StartBox/EndBox)
  --------------------------------------
  """  
  def test_irt_requirement_0071_002(self):
    with open("src/test/resources/stl/irt/requirement-0071-002.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p[1]/tt:span[1] 
  text: The first tt:span element of the first tt:p element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p[1]/tt:span[1] 
  condition: child::text()[1]='Test1 Test2' 
  text: Expected value: "Test1 Test2"  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 72
  --------------------------------------
  title: tt:p element mapping - text content
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0072-001
  --------------------------------------
  title: Testing that text from Text Field element is inside a tt:span element
  --------------------------------------
  """  
  def test_irt_requirement_0072_001(self):
    with open("src/test/resources/stl/irt/requirement-0072-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(descendant::text()) = count(child::tt:span/child::text()) 
  text: Expected value: "true"  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 73
  --------------------------------------
  title: DoubleHeight mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0073-001
  --------------------------------------
  title: Testing DoubleHeight element mapping
  --------------------------------------
  """  
  def test_irt_requirement_0073_001(self):
    with open("src/test/resources/stl/irt/requirement-0073-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span 
  text: The tt:span element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: substring-after(@style, ' ')=//tt:tt/tt:head/tt:styling/tt:style[@tts:fontSize='1c 2c']/@xml:id 
  text: Expected value: "1c 2c"  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 74
  --------------------------------------
  title: Line break handling
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0074-001
  --------------------------------------
  title: Testing that the newline element is mapped the tt:br element
  --------------------------------------
  """  
  def test_irt_requirement_0074_001(self):
    with open("src/test/resources/stl/irt/requirement-0074-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:br) = 1 
  text: Expected value: "1"  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 76
  --------------------------------------
  title: Control Codes mapping - closed subtitles
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0076-001
  --------------------------------------
  title: Testing Control Codes mapping for AlphaBlack
  --------------------------------------
  """  
  def test_irt_requirement_0076_001(self):
    with open("src/test/resources/stl/irt/requirement-0076-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span 
  text: The p element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: '2'.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: /tt:tt/tt:head/tt:styling/tt:style[                 @tts:color='black']                 [tokenize(normalize-space(current()/@style), ' ') = @xml:id] 
  text: Expected a referenced style with attribute tts:color='black'. Referenced styles: ""
  """  
  
  """
  --------------------------------------
  Test 0076-002
  --------------------------------------
  title: Testing Control Codes mapping for AlphaWhite
  --------------------------------------
  """  
  def test_irt_requirement_0076_002(self):
    with open("src/test/resources/stl/irt/requirement-0076-002.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span 
  text: The p element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: '2'.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: /tt:tt/tt:head/tt:styling/tt:style[                 @tts:color='white']                 [tokenize(normalize-space(current()/@style), ' ') = @xml:id] 
  text: Expected a referenced style with attribute tts:color='white'. Referenced styles: ""
  """  
  
  """
  --------------------------------------
  Test 0076-003
  --------------------------------------
  title: Testing Control Codes mapping for AlphaRed
  --------------------------------------
  """  
  def test_irt_requirement_0076_003(self):
    with open("src/test/resources/stl/irt/requirement-0076-003.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span 
  text: The p element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: '2'.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: /tt:tt/tt:head/tt:styling/tt:style[                 @tts:color='red']                 [tokenize(normalize-space(current()/@style), ' ') = @xml:id] 
  text: Expected a referenced style with attribute tts:color='red'. Referenced styles: ""
  """  
  
  """
  --------------------------------------
  Test 0076-004
  --------------------------------------
  title: Testing Control Codes mapping for AlphaGreen
  --------------------------------------
  """  
  def test_irt_requirement_0076_004(self):
    with open("src/test/resources/stl/irt/requirement-0076-004.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span 
  text: The p element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: '2'.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: /tt:tt/tt:head/tt:styling/tt:style[                 @tts:color='lime']                 [tokenize(normalize-space(current()/@style), ' ') = @xml:id] 
  text: Expected a referenced style with attribute tts:color='lime'. Referenced styles: ""
  """  
  
  """
  --------------------------------------
  Test 0076-005
  --------------------------------------
  title: Testing Control Codes mapping for AlphaYellow
  --------------------------------------
  """  
  def test_irt_requirement_0076_005(self):
    with open("src/test/resources/stl/irt/requirement-0076-005.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span 
  text: The p element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: '2'.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: /tt:tt/tt:head/tt:styling/tt:style[                 @tts:color='yellow']                 [tokenize(normalize-space(current()/@style), ' ') = @xml:id] 
  text: Expected a referenced style with attribute tts:color='yellow'. Referenced styles: ""
  """  
  
  """
  --------------------------------------
  Test 0076-006
  --------------------------------------
  title: Testing Control Codes mapping for AlphaBlue
  --------------------------------------
  """  
  def test_irt_requirement_0076_006(self):
    with open("src/test/resources/stl/irt/requirement-0076-006.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span 
  text: The p element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: '2'.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: /tt:tt/tt:head/tt:styling/tt:style[                 @tts:color='blue']                 [tokenize(normalize-space(current()/@style), ' ') = @xml:id] 
  text: Expected a referenced style with attribute tts:color='blue'. Referenced styles: ""
  """  
  
  """
  --------------------------------------
  Test 0076-007
  --------------------------------------
  title: Testing Control Codes mapping for AlphaMagenta
  --------------------------------------
  """  
  def test_irt_requirement_0076_007(self):
    with open("src/test/resources/stl/irt/requirement-0076-007.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span 
  text: The p element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: '2'.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: /tt:tt/tt:head/tt:styling/tt:style[                 @tts:color='magenta']                 [tokenize(normalize-space(current()/@style), ' ') = @xml:id] 
  text: Expected a referenced style with attribute tts:color='magenta'. Referenced styles: ""
  """  
  
  """
  --------------------------------------
  Test 0076-008
  --------------------------------------
  title: Testing Control Codes mapping for AlphaCyan
  --------------------------------------
  """  
  def test_irt_requirement_0076_008(self):
    with open("src/test/resources/stl/irt/requirement-0076-008.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span 
  text: The p element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: '2'.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: /tt:tt/tt:head/tt:styling/tt:style[                 @tts:color='cyan']                 [tokenize(normalize-space(current()/@style), ' ') = @xml:id] 
  text: Expected a referenced style with attribute tts:color='cyan'. Referenced styles: ""
  """  
  
  """
  --------------------------------------
  Test 0076-009
  --------------------------------------
  title: Testing Control Codes mapping for BlackBackground
  --------------------------------------
  """  
  def test_irt_requirement_0076_009(self):
    with open("src/test/resources/stl/irt/requirement-0076-009.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span 
  text: The p element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: '2'.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[1] 
  condition: /tt:tt/tt:head/tt:styling/tt:style[                 @tts:backgroundColor='white']                 [tokenize(normalize-space(current()/@style), ' ') = @xml:id] 
  text: Expected a referenced style with attribute tts:backgroundColor='white' in first span. Referenced styles: ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: /tt:tt/tt:head/tt:styling/tt:style[                 @tts:backgroundColor='black']                 [tokenize(normalize-space(current()/@style), ' ') = @xml:id] 
  text: Expected a referenced style with attribute tts:backgroundColor='black' in second span. Referenced styles: ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 77
  --------------------------------------
  title: Teletext subtitle mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0077-001
  --------------------------------------
  title: Testing DSC with value "1" and no style information
  --------------------------------------
  """  
  def test_irt_requirement_0077_001(self):
    with open("src/test/resources/stl/irt/requirement-0077-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span 
  text: The tt:span element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: substring-before(@style, ' ')=//tt:tt/tt:head/tt:styling/tt:style[@tts:backgroundColor='black']/@xml:id 
  text: Expected value: "AlphaWhiteOnAlphaBlack"  ""
  """  
  
  """
  --------------------------------------
  Test 0077-002
  --------------------------------------
  title: Testing DSC with value "2" and no style information
  --------------------------------------
  """  
  def test_irt_requirement_0077_002(self):
    with open("src/test/resources/stl/irt/requirement-0077-002.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span 
  text: The tt:span element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: substring-before(@style, ' ')=//tt:tt/tt:head/tt:styling/tt:style[@tts:backgroundColor='black']/@xml:id 
  text: Expected value: "AlphaWhiteOnAlphaBlack"  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 90
  --------------------------------------
  title: BlackBackground element mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0090-001
  --------------------------------------
  title: Testing BlackBackground with AlphaBlack
  --------------------------------------
  """  
  def test_irt_requirement_0090_001(self):
    with open("src/test/resources/stl/irt/requirement-0090-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'BlackOnBlack' 
  text: Expected value: "BlackOnBlack"  ""
  """  
  
  """
  --------------------------------------
  Test 0090-002
  --------------------------------------
  title: Testing BlackBackground with AlphaBlue
  --------------------------------------
  """  
  def test_irt_requirement_0090_002(self):
    with open("src/test/resources/stl/irt/requirement-0090-002.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'BlueOnBlack' 
  text: Expected value: "BlueOnBlack"  ""
  """  
  
  """
  --------------------------------------
  Test 0090-003
  --------------------------------------
  title: Testing BlackBackground with AlphaCyan
  --------------------------------------
  """  
  def test_irt_requirement_0090_003(self):
    with open("src/test/resources/stl/irt/requirement-0090-003.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'CyanOnBlack' 
  text: Expected value: "CyanOnBlack"  ""
  """  
  
  """
  --------------------------------------
  Test 0090-004
  --------------------------------------
  title: Testing BlackBackground with AlphaGreen
  --------------------------------------
  """  
  def test_irt_requirement_0090_004(self):
    with open("src/test/resources/stl/irt/requirement-0090-004.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'GreenOnBlack' 
  text: Expected value: "GreenOnBlack"  ""
  """  
  
  """
  --------------------------------------
  Test 0090-005
  --------------------------------------
  title: Testing BlackBackground with AlphaMagenta
  --------------------------------------
  """  
  def test_irt_requirement_0090_005(self):
    with open("src/test/resources/stl/irt/requirement-0090-005.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'MagentaOnBlack' 
  text: Expected value: "MagentaOnBlack"  ""
  """  
  
  """
  --------------------------------------
  Test 0090-006
  --------------------------------------
  title: Testing BlackBackground with AlphaRed
  --------------------------------------
  """  
  def test_irt_requirement_0090_006(self):
    with open("src/test/resources/stl/irt/requirement-0090-006.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'RedOnBlack' 
  text: Expected value: "RedOnBlack"  ""
  """  
  
  """
  --------------------------------------
  Test 0090-007
  --------------------------------------
  title: Testing BlackBackground with AlphaWhite
  --------------------------------------
  """  
  def test_irt_requirement_0090_007(self):
    with open("src/test/resources/stl/irt/requirement-0090-007.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'WhiteOnBlack' 
  text: Expected value: "WhiteOnBlack"  ""
  """  
  
  """
  --------------------------------------
  Test 0090-008
  --------------------------------------
  title: Testing BlackBackground with AlphaYellow
  --------------------------------------
  """  
  def test_irt_requirement_0090_008(self):
    with open("src/test/resources/stl/irt/requirement-0090-008.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'YellowOnBlack' 
  text: Expected value: "YellowOnBlack"  ""
  """  
  
  """
  --------------------------------------
  Test 0090-009
  --------------------------------------
  title: Testing unchanging BlackBackground
  --------------------------------------
  """  
  def test_irt_requirement_0090_009(self):
    with open("src/test/resources/stl/irt/requirement-0090-009.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 1 
  text: Expected value: "1"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: @style = 'WhiteOnBlack' 
  text: Expected value: "WhiteOnBlack"  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 91
  --------------------------------------
  title: NewBackground element mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0091-001
  --------------------------------------
  title: Testing NewBackground with AlphaBlack
  --------------------------------------
  """  
  def test_irt_requirement_0091_001(self):
    with open("src/test/resources/stl/irt/requirement-0091-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'BlackOnBlack' 
  text: Expected value: "BlackOnBlack  ""
  """  
  
  """
  --------------------------------------
  Test 0091-002
  --------------------------------------
  title: Testing NewBackground with AlphaBlue
  --------------------------------------
  """  
  def test_irt_requirement_0091_002(self):
    with open("src/test/resources/stl/irt/requirement-0091-002.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'BlackOnBlue' 
  text: Expected value: "BlackOnBlue"  ""
  """  
  
  """
  --------------------------------------
  Test 0091-003
  --------------------------------------
  title: Testing NewBackground with AlphaCyan
  --------------------------------------
  """  
  def test_irt_requirement_0091_003(self):
    with open("src/test/resources/stl/irt/requirement-0091-003.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'BlackOnCyan' 
  text: Expected value: "BlackOnCyan"  ""
  """  
  
  """
  --------------------------------------
  Test 0091-004
  --------------------------------------
  title: Testing NewBackground with AlphaGreen
  --------------------------------------
  """  
  def test_irt_requirement_0091_004(self):
    with open("src/test/resources/stl/irt/requirement-0091-004.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'BlackOnGreen' 
  text: Expected value: "BlackOnGreen"  ""
  """  
  
  """
  --------------------------------------
  Test 0091-005
  --------------------------------------
  title: Testing NewBackground with AlphaMagenta
  --------------------------------------
  """  
  def test_irt_requirement_0091_005(self):
    with open("src/test/resources/stl/irt/requirement-0091-005.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style  = 'BlackOnMagenta' 
  text: Expected value: "BlackOnMagenta"  ""
  """  
  
  """
  --------------------------------------
  Test 0091-006
  --------------------------------------
  title: Testing NewBackground with AlphaRed
  --------------------------------------
  """  
  def test_irt_requirement_0091_006(self):
    with open("src/test/resources/stl/irt/requirement-0091-006.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'BlackOnRed' 
  text: Expected value: "BlackOnRed"  ""
  """  
  
  """
  --------------------------------------
  Test 0091-007
  --------------------------------------
  title: Testing NewBackground with AlphaWhite
  --------------------------------------
  """  
  def test_irt_requirement_0091_007(self):
    with open("src/test/resources/stl/irt/requirement-0091-007.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'BlackOnWhite' 
  text: Expected value: "BlackOnWhite"  ""
  """  
  
  """
  --------------------------------------
  Test 0091-008
  --------------------------------------
  title: Testing NewBackground with AlphaYellow
  --------------------------------------
  """  
  def test_irt_requirement_0091_008(self):
    with open("src/test/resources/stl/irt/requirement-0091-008.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'BlackOnYellow' 
  text: Expected value: "BlackOnYellow"  ""
  """  
  
  """
  --------------------------------------
  Test 0091-009
  --------------------------------------
  title: Testing unchanging NewBackground
  --------------------------------------
  """  
  def test_irt_requirement_0091_009(self):
    with open("src/test/resources/stl/irt/requirement-0091-009.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 1 
  text: Expected value: "1"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: @style = 'BlackOnGreen' 
  text: Expected value: "BlackOnGreen"  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 79
  --------------------------------------
  title: AlphaBlack element mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0079-001
  --------------------------------------
  title: Testing NewBackground element with AlphaBlack
  --------------------------------------
  """  
  def test_irt_requirement_0079_001(self):
    with open("src/test/resources/stl/irt/requirement-0079-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'WhiteOnBlack' 
  text: Expected value: "WhiteOnBlack"  ""
  """  
  
  """
  --------------------------------------
  Test 0079-002
  --------------------------------------
  title: Testing NewForeground element with AlphaBlack
  --------------------------------------
  """  
  def test_irt_requirement_0079_002(self):
    with open("src/test/resources/stl/irt/requirement-0079-002.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'BlackOnGreen' 
  text: Expected value: "BlackOnGreen"  ""
  """  
  
  """
  --------------------------------------
  Test 0079-003
  --------------------------------------
  title: Testing NewBackground element with unchanging AlphaBlack
  --------------------------------------
  """  
  def test_irt_requirement_0079_003(self):
    with open("src/test/resources/stl/irt/requirement-0079-003.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) eq 1 
  text: Expected value: "1"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: @style = 'WhiteOnBlack' 
  text: Expected value: "WhiteOnBlack"  ""
  """  
  
  """
  --------------------------------------
  Test 0079-004
  --------------------------------------
  title: Testing NewForeground element with unchanging AlphaBlack
  --------------------------------------
  """  
  def test_irt_requirement_0079_004(self):
    with open("src/test/resources/stl/irt/requirement-0079-004.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 1 
  text: Expected value: "1"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: @style = 'BlackOnGreen' 
  text: Expected value: "BlackOnGreen"  ""
  """  
  
  """
  --------------------------------------
  Test 0079-005
  --------------------------------------
  title: Testing NewForeground element with unchanging AlphaBlack and no foreground
  --------------------------------------
  """  
  def test_irt_requirement_0079_005(self):
    with open("src/test/resources/stl/irt/requirement-0079-005.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 1 
  text: Expected value: "1"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: @style = 'BlackOnBlack' 
  text: Expected value: "BlackOnBlack"  ""
  """  
  
  """
  --------------------------------------
  Test 0079-006
  --------------------------------------
  title: Testing NewForeground element with AlphaBlack with a previous NewBackground and text directly after NewBackground and new foreground color = old background color
  --------------------------------------
  """  
  def test_irt_requirement_0079_006(self):
    with open("src/test/resources/stl/irt/requirement-0079-006.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 3 
  text: Expected value: "3"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[1] 
  condition: @style = 'WhiteOnBlack' 
  text: Expected value: "WhiteOnBlack"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'GreenOnGreen' 
  text: Expected value: "GreenOnGreen"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[3] 
  condition: @style = 'BlackOnGreen' 
  text: Expected value: "BlackOnGreen"  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 80
  --------------------------------------
  title: AlphaRed element mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0080-001
  --------------------------------------
  title: Testing NewBackground element with AlphaRed
  --------------------------------------
  """  
  def test_irt_requirement_0080_001(self):
    with open("src/test/resources/stl/irt/requirement-0080-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'WhiteOnRed' 
  text: Expected value: "WhiteOnRed"  ""
  """  
  
  """
  --------------------------------------
  Test 0080-002
  --------------------------------------
  title: Testing NewForeground element with AlphaRed
  --------------------------------------
  """  
  def test_irt_requirement_0080_002(self):
    with open("src/test/resources/stl/irt/requirement-0080-002.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'RedOnGreen' 
  text: Expected value: "RedOnGreen"  ""
  """  
  
  """
  --------------------------------------
  Test 0080-003
  --------------------------------------
  title: Testing NewBackground element with unchanging AlphaRed
  --------------------------------------
  """  
  def test_irt_requirement_0080_003(self):
    with open("src/test/resources/stl/irt/requirement-0080-003.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 1 
  text: Expected value: "1"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: @style = 'WhiteOnRed' 
  text: Expected value: "WhiteOnRed"  ""
  """  
  
  """
  --------------------------------------
  Test 0080-004
  --------------------------------------
  title: Testing NewForeground element with unchanging AlphaRed
  --------------------------------------
  """  
  def test_irt_requirement_0080_004(self):
    with open("src/test/resources/stl/irt/requirement-0080-004.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 1 
  text: Expected value: "1"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: @style = 'RedOnGreen' 
  text: Expected value: "RedOnGreen"  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 81
  --------------------------------------
  title: AlphaGreen element mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0081-001
  --------------------------------------
  title: Testing NewBackground element with AlphaGreen
  --------------------------------------
  """  
  def test_irt_requirement_0081_001(self):
    with open("src/test/resources/stl/irt/requirement-0081-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'WhiteOnGreen' 
  text: Expected value: "WhiteOnGreen"  ""
  """  
  
  """
  --------------------------------------
  Test 0081-002
  --------------------------------------
  title: Testing NewForeground element with AlphaGreen
  --------------------------------------
  """  
  def test_irt_requirement_0081_002(self):
    with open("src/test/resources/stl/irt/requirement-0081-002.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'GreenOnGreen' 
  text: Expected value: "GreenOnGreen"  ""
  """  
  
  """
  --------------------------------------
  Test 0081-003
  --------------------------------------
  title: Testing NewBackground element with unchanging AlphaGreen
  --------------------------------------
  """  
  def test_irt_requirement_0081_003(self):
    with open("src/test/resources/stl/irt/requirement-0081-003.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 1 
  text: Expected value: "1"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: @style = 'WhiteOnGreen' 
  text: Expected value: "WhiteOnGreen"  ""
  """  
  
  """
  --------------------------------------
  Test 0081-004
  --------------------------------------
  title: Testing NewForeground element with unchanging AlphaGreen
  --------------------------------------
  """  
  def test_irt_requirement_0081_004(self):
    with open("src/test/resources/stl/irt/requirement-0081-004.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 1 
  text: Expected value: "1"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: @style = 'GreenOnBlack' 
  text: Expected value: "GreenOnBlack"  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 82
  --------------------------------------
  title: AlphaYellow element mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0082-001
  --------------------------------------
  title: Testing NewBackground element with AlphaYellow
  --------------------------------------
  """  
  def test_irt_requirement_0082_001(self):
    with open("src/test/resources/stl/irt/requirement-0082-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'WhiteOnYellow' 
  text: Expected value: "WhiteOnYellow"  ""
  """  
  
  """
  --------------------------------------
  Test 0082-002
  --------------------------------------
  title: Testing NewForeground element with AlphaYellow
  --------------------------------------
  """  
  def test_irt_requirement_0082_002(self):
    with open("src/test/resources/stl/irt/requirement-0082-002.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'YellowOnGreen' 
  text: Expected value: "YellowOnGreen"  ""
  """  
  
  """
  --------------------------------------
  Test 0082-003
  --------------------------------------
  title: Testing NewBackground element with unchanging AlphaYellow
  --------------------------------------
  """  
  def test_irt_requirement_0082_003(self):
    with open("src/test/resources/stl/irt/requirement-0082-003.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 1 
  text: Expected value: "1"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: @style = 'WhiteOnYellow' 
  text: Expected value: "WhiteOnYellow"  ""
  """  
  
  """
  --------------------------------------
  Test 0082-004
  --------------------------------------
  title: Testing NewForeground element with unchanging AlphaYellow
  --------------------------------------
  """  
  def test_irt_requirement_0082_004(self):
    with open("src/test/resources/stl/irt/requirement-0082-004.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 1 
  text: Expected value: "1"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: @style = 'YellowOnBlack' 
  text: Expected value: "YellowOnBlack"  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 83
  --------------------------------------
  title: AlphaBlue element mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0083-001
  --------------------------------------
  title: Testing NewBackground element with AlphaBlue
  --------------------------------------
  """  
  def test_irt_requirement_0083_001(self):
    with open("src/test/resources/stl/irt/requirement-0083-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'WhiteOnBlue' 
  text: Expected value: "WhiteOnBlue"  ""
  """  
  
  """
  --------------------------------------
  Test 0083-002
  --------------------------------------
  title: Testing NewForeground element with AlphaBlue
  --------------------------------------
  """  
  def test_irt_requirement_0083_002(self):
    with open("src/test/resources/stl/irt/requirement-0083-002.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'BlueOnGreen' 
  text: Expected value: "BlueOnGreen"  ""
  """  
  
  """
  --------------------------------------
  Test 0083-003
  --------------------------------------
  title: Testing NewBackground element with unchanging AlphaBlue
  --------------------------------------
  """  
  def test_irt_requirement_0083_003(self):
    with open("src/test/resources/stl/irt/requirement-0083-003.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 1 
  text: Expected value: "1"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: @style = 'WhiteOnBlue' 
  text: Expected value: "WhiteOnBlue"  ""
  """  
  
  """
  --------------------------------------
  Test 0083-004
  --------------------------------------
  title: Testing NewForeground element with unchanging AlphaBlue
  --------------------------------------
  """  
  def test_irt_requirement_0083_004(self):
    with open("src/test/resources/stl/irt/requirement-0083-004.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 1 
  text: Expected value: "1"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: @style = 'BlueOnBlack' 
  text: Expected value: "BlueOnBlack"  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 84
  --------------------------------------
  title: AlphaMagenta element mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0084-001
  --------------------------------------
  title: Testing NewBackground element with AlphaMagenta
  --------------------------------------
  """  
  def test_irt_requirement_0084_001(self):
    with open("src/test/resources/stl/irt/requirement-0084-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'WhiteOnMagenta' 
  text: Expected value: "WhiteOnMagenta"  ""
  """  
  
  """
  --------------------------------------
  Test 0084-002
  --------------------------------------
  title: Testing NewForeground element with AlphaMagenta
  --------------------------------------
  """  
  def test_irt_requirement_0084_002(self):
    with open("src/test/resources/stl/irt/requirement-0084-002.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'MagentaOnGreen' 
  text: Expected value: "MagentaOnGreen"  ""
  """  
  
  """
  --------------------------------------
  Test 0084-003
  --------------------------------------
  title: Testing NewBackground element with unchanging AlphaMagenta
  --------------------------------------
  """  
  def test_irt_requirement_0084_003(self):
    with open("src/test/resources/stl/irt/requirement-0084-003.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 1 
  text: Expected value: "1"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: @style = 'WhiteOnMagenta' 
  text: Expected value: "WhiteOnMagenta"  ""
  """  
  
  """
  --------------------------------------
  Test 0084-004
  --------------------------------------
  title: Testing NewForeground element with unchanging AlphaMagenta
  --------------------------------------
  """  
  def test_irt_requirement_0084_004(self):
    with open("src/test/resources/stl/irt/requirement-0084-004.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 1 
  text: Expected value: "1"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: @style = 'MagentaOnBlack' 
  text: Expected value: "MagentaOnBlack"  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 85
  --------------------------------------
  title: AlphaCyan element mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0085-001
  --------------------------------------
  title: Testing NewBackground element with AlphaCyan
  --------------------------------------
  """  
  def test_irt_requirement_0085_001(self):
    with open("src/test/resources/stl/irt/requirement-0085-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'WhiteOnCyan' 
  text: Expected value: "WhiteOnCyan"  ""
  """  
  
  """
  --------------------------------------
  Test 0085-002
  --------------------------------------
  title: Testing NewForeground element with AlphaCyan
  --------------------------------------
  """  
  def test_irt_requirement_0085_002(self):
    with open("src/test/resources/stl/irt/requirement-0085-002.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 2 
  text: Expected value: "2"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[2] 
  condition: @style = 'CyanOnGreen' 
  text: Expected value: "CyanOnGreen"  ""
  """  
  
  """
  --------------------------------------
  Test 0085-003
  --------------------------------------
  title: Testing NewBackground element with unchanging AlphaCyan
  --------------------------------------
  """  
  def test_irt_requirement_0085_003(self):
    with open("src/test/resources/stl/irt/requirement-0085-003.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 1 
  text: Expected value: "1"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: @style = 'WhiteOnCyan' 
  text: Expected value: "WhiteOnCyan"  ""
  """  
  
  """
  --------------------------------------
  Test 0085-004
  --------------------------------------
  title: Testing NewForeground element with unchanging AlphaCyan
  --------------------------------------
  """  
  def test_irt_requirement_0085_004(self):
    with open("src/test/resources/stl/irt/requirement-0085-004.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p 
  text: The tt:p element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 1 
  text: Expected value: "1"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span 
  condition: @style = 'CyanOnBlack' 
  text: Expected value: "CyanOnBlack"  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 86
  --------------------------------------
  title: EndBox element mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0086-001
  --------------------------------------
  title: Testing EndBox element mapping with three closing EndBox elements and without changing the colors
  --------------------------------------
  """  
  def test_irt_requirement_0086_001(self):
    with open("src/test/resources/stl/irt/requirement-0086-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span 
  text: The tt:span element must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 3 
  text: Expected value: "3"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[1] 
  condition: @style = 'WhiteOnBlack' 
  text: Expected value: "WhiteOnBlack"  ""
  """  
  
  """
  --------------------------------------
  IRT Requirement 87
  --------------------------------------
  title: StartBox element mapping
  --------------------------------------
  """


  """
  --------------------------------------
  Test 0087-001
  --------------------------------------
  title: Testing StartBox element mapping with three StartBox elements and with referencing a style with the appropriate background and foreground color
  --------------------------------------
  """  
  def test_irt_requirement_0087_001(self):
    with open("src/test/resources/stl/irt/requirement-0087-001.stl", "rb") as f:
      ttconv.stl.reader.to_model(f)

  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span 
  text: The tt:span element must be present.
  """  
  
  """
  ASSERT
  context: / 
  condition: tt:tt/tt:body/tt:div/tt:p/tt:span/@style 
  text: The style attribute must be present.
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p 
  condition: count(tt:span) = 3 
  text: Expected value: "3"  ""
  """  
  
  """
  ASSERT
  context: tt:tt/tt:body/tt:div/tt:p/tt:span[1] 
  condition: @style = 'WhiteOnBlack' 
  text: Expected value: "WhiteOnBlack"  ""
  """  
  
      
      
if __name__ == '__main__':
  unittest.main()
