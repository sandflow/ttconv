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
from argparse import ArgumentParser
import xml.etree.ElementTree as et
#import ttconv.model as model
import ttconv.imsc.imsc_reader as imsc_reader
import ttconv.imsc.imsc_writer as imsc_writer

LOGGER = logging.getLogger(__name__)

# Argument parsing setup
#
cli = ArgumentParser()
subparsers = cli.add_subparsers(dest="subcommand")

def argument(*name_or_flags, **kwargs):
  """Convenience function to properly format arguments to pass to the
  subcommand decorator."""

  return (list(name_or_flags), kwargs)


def subcommand(args=None, parent=subparsers):
  """Decorator to define a new subcommand in a sanity-preserving way.
  The function will be stored in the ``func`` variable when the parser
  parses arguments so that it can be called directly like so::

      args = cli.parse_args()
      args.func(args)

  Usage example::

      @subcommand([argument("-d", help="Enable debug mode", action="store_true")])
      def subcommand(args):
          print(args)

  Then on the command line::

      $ python cli.py subcommand -d

  """
  def decorator(func):
    parser = parent.add_parser(func.__name__, description=func.__doc__)
    for arg in args:
      parser.add_argument(*arg[0], **arg[1])
    parser.set_defaults(func=func)

  if args is None:
    args = []
  return decorator


@subcommand([argument("-i", "--input", help="Input file path", required=True), 
  argument("-o", "--output", help="Output file path", required=True)])
def convert(args):
  '''Process input and output through the reader, converter, and writer'''

  inputfile = args.input
  outputfile = args.output

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


@subcommand([argument("-i", "--input", help="Input file path", required=True)])
def validate(args):
  '''Process input through the validator'''

  print(args.input)
  LOGGER.info("Input file is %s", args.input)


def main(argv):
  '''Main application processing'''

  args = cli.parse_args(argv)
  if args.subcommand is None:
    cli.print_help()
  else:
    args.func(args)

if __name__ == "__main__":
  main(sys.argv[1:])
