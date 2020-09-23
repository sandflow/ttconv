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

'''ttconv tt'''

import logging
import sys
import argparse
import xml.etree.ElementTree as et
#import ttconv.model as model
import ttconv.imsc.imsc_reader as imsc_reader
import ttconv.imsc.imsc_writer as imsc_writer

LOGGER = logging.getLogger(__name__)

def convert_parse_args(argv):
  '''Parses command line arguments for convert. Returns inputfile, outputfile.'''

  parser = argparse.ArgumentParser()

  parser.add_argument("-i", "--input", help="Input file path", required=True)
  parser.add_argument("-o", "--output", help="Output file path", required=True)

  # Pass in argv such that it is processed based on 
  # what is passed into parse_args.
  # This allows the unit tests to pass in args through
  # the main function
  #
  args = parser.parse_args(argv)

  return args.input, args.output

def convert(argv):
  '''Process input and output through the reader, converter, and writer'''

  inputfile = ""
  outputfile = ""
  
  inputfile, outputfile = convert_parse_args(argv)

  LOGGER.info("Input file is %s", inputfile)
  LOGGER.info("Output file is %s", outputfile)

  # 
  # Parse the xml input file into an ElementTree
  #
  tree = et.parse(inputfile)

  #
  # Pass the parsed xml to the reader
  #
  _model = imsc_reader.to_model(tree)

  #
  # Construct and configure the writer
  #
  writer = imsc_writer.Writer()

  #writer.from_model(_model)
  writer.from_xml(inputfile)
  writer.write(outputfile)

def validate_parse_args(argv):
  '''Parses command line arguments for validate. Returns inputfile.'''

  parser = argparse.ArgumentParser()

  parser.add_argument("-i", "--input", help="Input file path", required=True)

  # Pass in argv such that it is processed based on 
  # what is passed into parse_args.
  # This allows the unit tests to pass in args through
  # the main function
  #
  args = parser.parse_args(argv)

  return args.input

def validate(argv):
  '''Process input through the validator'''

  inputfile = ""
  
  inputfile = validate_parse_args(argv)

  LOGGER.info("Input file is %s", inputfile)

  # 
  # Parse the xml input file into an ElementTree
  #
  #tree = et.parse(inputfile)

  #
  # Pass the parsed xml to the validator
  #
  #_model = imsc_reader.to_model(tree)

def main(argv):
  '''Main application processing'''

  #LOGGER.basicConfig(filename='main.log', level=LOGGER.INFO)
  
  if argv[0] == "convert":
    convert(argv[1:])
  elif argv[0] == "validate":
    validate(argv[1:])
  else:
    print("Invalid function - ", argv[0])
    print("Valid functions: convert, validate")
    raise RuntimeError('Bad args')

if __name__ == "__main__":
  main(sys.argv[1:])
