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

'''Unit tests for the IMSC writer'''

# pylint: disable=R0201,C0115,C0116

import os
import unittest
import xml.etree.ElementTree as et
import ttconv.imsc.reader as imsc_reader
import ttconv.imsc.writer as imsc_writer
import xml.dom.minidom as minidom
import ttconv.model as model
import ttconv.style_properties as styles
import ttconv.imsc.namespaces as xml_ns
import ttconv.imsc.elements as imsc_elements

class ReaderWriterTest(unittest.TestCase):

  def setUp(self):
    if not os.path.exists('build'):
      os.makedirs('build')

  def pretty_print(self, elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = et.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    print(reparsed.toprettyxml(indent="\t"))

  def test_body_only(self):

    # parse the data
    #file_to_parse = "src/test/resources/ttml/imsc-tests/imsc1/ttml/activeArea/ActiveArea001.ttml"
    #file_to_parse = "src/test/resources/ttml/imsc-tests/imsc1/ttml/altText/altText1.ttml"
    #file_to_parse = "src/test/resources/ttml/body_only.ttml"
    #file_to_parse = "src/test/resources/ttml/imsc-tests/imsc1/ttml/aspectRatio/aspectRatio1.ttml"
    #file_to_parse = "src/test/resources/ttml/imsc-tests/imsc1/ttml/backgroundColor/BackgroundColor001.ttml"
    file_to_parse = "src/test/resources/ttml/imsc-tests/imsc1/ttml/br/br-in-span-001.ttml"
    
    tree = et.parse(file_to_parse)

    # create the model
    test_model = imsc_reader.to_model(tree)

    # convert from a model to a ttml document
    tree_from_model = imsc_writer.from_model(test_model)

    # write the document out to a file
    tree_from_model.write('build/out.ttml', encoding='utf-8', xml_declaration=True)

    #self.pretty_print(tree_from_model.getroot())

class FromModelBodyWriterTest(unittest.TestCase):

  def setUp(self):
    if not os.path.exists('build'):
      os.makedirs('build')
    
    et.register_namespace("ttml", xml_ns.TTML)
    et.register_namespace("ttp", xml_ns.TTP)
    et.register_namespace("tts", xml_ns.TTS)
    et.register_namespace("ittp", xml_ns.ITTP)
    et.register_namespace("itts", xml_ns.ITTS)

  def test_body_only(self):

    return

    class _Context:
      def __init__(self):
        self.imsc_doc = None

    context = _Context()

    context.imsc_doc = et.Element("tt")

    body = model.Body()
    div = model.Div()
    p = model.P()
    span = model.Span()
    text = model.Text()
    text.set_text("asdf")
    
    span.push_child(text)
    p.push_child(span)
    div.push_child(p)
    body.push_child(div)

    imsc_elements.BodyElement.from_model(context, body)

    found_span = et.ElementTree(context.imsc_doc).find("tt")
    if found_span is not None:
      found_span.text 

    # write the document out to a file
    et.ElementTree(context.imsc_doc).write('build/BodyElement.out.ttml', encoding='utf-8', xml_declaration=True)

    #self.pretty_print(tree_from_model.getroot())

if __name__ == '__main__':
  unittest.main()
