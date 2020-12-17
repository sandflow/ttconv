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

import os
import logging
import sys
from argparse import ArgumentParser
import xml.etree.ElementTree as et
from pathlib import Path
from enum import Enum
import ttconv.imsc.reader as imsc_reader
import ttconv.imsc.writer as imsc_writer
import ttconv.srt.writer as srt_writer
import ttconv.scc.reader as scc_reader

LOGGER = logging.getLogger("ttconv")

class ProgressConsoleHandler(logging.StreamHandler):
  """
  A handler class which allows the cursor to stay on
  one line for selected messages
  """

  class ProgressType(Enum):
    '''Whether the progress is for reading or writing operations
    '''
    read = 1
    write = 2

  def __init__(self):
    self.is_writing_progress_bar = False
    self.last_progress_msg = ""
    super().__init__()

  def emit(self, record):

    def progress_str(progress_type: ProgressConsoleHandler.ProgressType, percent_progress: float) -> str:
      '''Formats the progress string.'''

      prefix = "Reading:" if progress_type is ProgressConsoleHandler.ProgressType.read else "Writing:"
      suffix = 'Complete'
      length = 50
      fill = '█'
      filled_length = int(length * percent_progress)
      bar_val = fill * filled_length + '-' * (length - filled_length)
      
      return f'\r{prefix} |{bar_val}| {100 * percent_progress:3.0f}% {suffix}'

    try:
      msg = self.format(record)

      stream = self.stream

      is_progress_bar_record = hasattr(record, 'progress_bar')
      percent_progress = None

      if is_progress_bar_record:
        percent_progress = getattr(record, 'percent_progress')
        msg = progress_str(
          getattr(record, 'progress_bar'),
          float(percent_progress)
        )
        self.last_progress_msg = msg
  
      if self.is_writing_progress_bar and not is_progress_bar_record:
        # erase and over write the progress bar
        stream.write('\r')
        length = len(self.last_progress_msg)
        stream.write(' ' * length)

        # go to beginning of the line and write the new messages
        stream.write('\r')
        stream.write(msg)
        stream.write(self.terminator)

        # write the old progress information
        stream.write(self.last_progress_msg)
      elif is_progress_bar_record:
        stream.write(msg)
      else:
        stream.write(msg)
        stream.write(self.terminator)

      if is_progress_bar_record:
        self.is_writing_progress_bar = True
        if percent_progress is not None and float(percent_progress) >= 1.0:
          sys.stdout.write('\r\n')
          self.is_writing_progress_bar = False

      self.flush()

    except (KeyboardInterrupt, SystemExit):
      raise
    except: # pylint: disable=bare-except
      self.handleError(record)

def progress_callback_read(percent_progress: float):
  '''Callback handler used by reader and writer.'''
  LOGGER.info(
    "%d%%",
    percent_progress,
    extra={
      'progress_bar': ProgressConsoleHandler.ProgressType.read, 
      'percent_progress': percent_progress,
    }
  )

def progress_callback_write(percent_progress: float):
  '''Callback handler used by reader and writer.'''
  LOGGER.info(
    "%d%%",
    percent_progress,
    extra={
      'progress_bar': ProgressConsoleHandler.ProgressType.write, 
      'percent_progress': percent_progress,
    }
  )

class FileTypes(Enum):
  '''Enumerates the types of supported'''
  TTML = "ttml"
  SCC = "scc"
  SRT = "srt"

  @staticmethod
  def get_file_type(file_type: str, file_extension: str):
    """Convenience function to convert string ased file type 
    and extension to FileTypes."""

    if file_type is None and file_extension is None:
      return None

    if file_type is None:
      if len(file_extension) > 0 and file_extension[0] == '.':
        file_extension = file_extension[1:len(file_extension)]

      return FileTypes(file_extension)

    return FileTypes(file_type)

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


@subcommand([
  argument("-i", "--input", help="Input file path", required=True), 
  argument("-o", "--output", help="Output file path", required=True),
  argument("--itype", help="Input file type", required=False),
  argument("--otype", help="Output file type", required=False)
  ])
def convert(args):  
  '''Process input and output through the reader, converter, and writer'''

  inputfile = args.input
  outputfile = args.output

  LOGGER.info("Input file is %s", inputfile)
  LOGGER.info("Output file is %s", outputfile)

  _input_filename, input_file_extension = os.path.splitext(inputfile)
  _output_filename, output_file_extension = os.path.splitext(outputfile)

  reader_type = FileTypes.get_file_type(args.itype, input_file_extension)
  writer_type = FileTypes.get_file_type(args.otype, output_file_extension)

  if reader_type is FileTypes.TTML:
    # 
    # Parse the xml input file into an ElementTree
    #
    tree = et.parse(inputfile)

    #
    # Pass the parsed xml to the reader
    #
    model = imsc_reader.to_model(tree, progress_callback_read)

  elif reader_type is FileTypes.SCC:
    file_as_str = Path(inputfile).read_text()

    #
    # Pass the parsed xml to the reader
    #
    model = scc_reader.to_model(file_as_str, progress_callback_read)
  else:
    if args.itype is not None:
      exit_str  = f'Input type {args.itype} is not supported'
    else:
      exit_str  = f'Input file is {args.input} is not supported'
    
    LOGGER.error(exit_str)
    sys.exit(exit_str)

  if writer_type is FileTypes.TTML:
    #
    # Construct and configure the writer
    #
    tree_from_model = imsc_writer.from_model(model, None, progress_callback_write)

    #
    # Write out the converted file
    #
    tree_from_model.write(outputfile)

  elif writer_type is FileTypes.SRT:
    #
    # Construct and configure the writer
    #
    srt_document = srt_writer.from_model(model, progress_callback_write)

    #
    # Write out the converted file
    #
    with open(outputfile, "w", encoding="utf-8") as srt_file:
      srt_file.write(srt_document)

  else:
    if args.otype is not None:
      exit_str  = f'Output type {args.otype} is not supported'
    else:
      exit_str  = f'Output file is {args.output} is not supported'

    LOGGER.error(exit_str)
    sys.exit(exit_str)


@subcommand([argument("-i", "--input", help="Input file path", required=True)])
def validate(args):
  '''Process input through the validator'''

  print(args.input)
  LOGGER.info("Input file is %s", args.input)

# Ensure that the handler is added only once/globally
# Otherwise the handler will be called multiple times
progress = ProgressConsoleHandler()
LOGGER.addHandler(progress)
LOGGER.setLevel(logging.INFO) 

def main(argv):
  '''Main application processing'''

  args = cli.parse_args(argv)
  if args.subcommand is None:
    cli.print_help()
  else:
    args.func(args)

if __name__ == "__main__":
  main(sys.argv[1:])
