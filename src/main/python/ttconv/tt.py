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

from __future__ import annotations

import json
import logging
import os
import sys
import typing
import xml.etree.ElementTree as et
from argparse import ArgumentParser
from enum import Enum
from pathlib import Path
from ttconv.filters.document_filter import DocumentFilter

import ttconv.imsc.reader as imsc_reader
import ttconv.imsc.writer as imsc_writer
import ttconv.imsc.validator.ebuttd.model as ebuttd_model
import ttconv.imsc.validator.imsc11_validator as imsc11_validator
import ttconv.imsc.validator.nbcu053.model as nbcu053_model
from ttconv.imsc.validator.nbcu053.model import NBCU053ValidatorConfiguration
import ttconv.imsc.validator.rosetta.model as rosetta_model
import ttconv.scc.reader as scc_reader
import ttconv.scc.writer as scc_writer
import ttconv.srt.writer as srt_writer
import ttconv.srt.reader as srt_reader
import ttconv.stl.reader as stl_reader
import ttconv.vtt.reader as vtt_reader
from ttconv.vtt.config import VTTWriterConfiguration
import ttconv.vtt.writer as vtt_writer
from ttconv.config import GeneralConfiguration
from ttconv.config import ModuleConfiguration
from ttconv.imsc.config import IMSCWriterConfiguration
from ttconv.isd import ISDConfiguration
from ttconv.scc.config import SccReaderConfiguration, SccWriterConfiguration
from ttconv.stl.config import STLReaderConfiguration
from ttconv.srt.config import SRTReaderConfiguration, SRTWriterConfiguration

LOGGER = logging.getLogger("ttconv")

CONFIGURATIONS = [
  GeneralConfiguration,
  IMSCWriterConfiguration,
  ISDConfiguration,
  SccReaderConfiguration,
  SRTReaderConfiguration,
]

class ProgressBar:
  '''Displays the progress of an operation on the console if it is a terminal.
  Nothing is displayed otherwise, e.g., when the console is redirected to a file.'''

  _LENGTH = 50

  active: typing.Optional[ProgressBar] = None

  def __init__(
    self,
    label: str,
    general_config: typing.Optional[GeneralConfiguration] = None,
    stream: typing.Optional[typing.TextIO] = None
  ):
    '''The progress bar is displayed unless disabled by `general_config.progress_bar`'''
    self.label = label
    if stream is not None:
      self.stream = stream
    else:
      self.stream = sys.stderr

    if not self.stream.isatty():
      self.enabled = False
    elif general_config is not None and general_config.progress_bar is False:
      self.enabled = False
    else:
      self.enabled = True
    self._line = ""

  def __enter__(self) -> ProgressBar:
    return self

  def __exit__(self, *_exc_info):
    self.close()

  def update(self, fraction: float):
    '''Displays `fraction`, between 0 and 1, of the operation as completed'''
    if not self.enabled:
      return
    ProgressBar.active = self
    fraction = min(1.0, max(0.0, float(fraction)))
    filled = int(self._LENGTH * fraction)
    self._line = f"{self.label} |{'█' * filled}{'-' * (self._LENGTH - filled)}| {100 * fraction:3.0f}%"
    self.stream.write("\r" + self._line)
    self.stream.flush()

  def clear(self):
    '''Erases the progress bar, e.g., so that a log message can be written in its place'''
    if self._line:
      self.stream.write("\r" + " " * len(self._line) + "\r")

  def redraw(self):
    '''Displays the progress bar again after `clear()`'''
    if self._line:
      self.stream.write(self._line)
      self.stream.flush()

  def close(self):
    '''Erases the progress bar, if it is displayed'''
    if ProgressBar.active is self:
      ProgressBar.active = None
    if self._line:
      self.clear()
      self.stream.flush()
      self._line = ""


class ConsoleHandler(logging.StreamHandler):
  '''Writes log messages to the console, i.e., the current `sys.stderr`, around the progress bar that is being displayed,
  if any'''

  def emit(self, record):
    self.stream = sys.stderr
    if ProgressBar.active is not None and ProgressBar.active.stream is self.stream:
      progress_bar = ProgressBar.active
    else:
      progress_bar = None
    if progress_bar is not None:
      progress_bar.clear()
    super().emit(record)
    if progress_bar is not None:
      progress_bar.redraw()


def die(msg: str):
  LOGGER.error(msg)
  sys.exit(msg)

class FileTypes(Enum):
  '''Enumerates the types of supported'''
  TTML = "ttml"
  SCC = "scc"
  SRT = "srt"
  STL = "stl"
  VTT = "vtt"

  @staticmethod
  def get_file_type(file_type: str, file_extension: str):
    """Convenience function to convert string ased file type 
    and extension to FileTypes."""

    if file_type is None and file_extension is None:
      return None

    if file_type is None:
      if len(file_extension) > 0 and file_extension[0] == '.':
        file_extension = file_extension[1:len(file_extension)]

      return FileTypes(file_extension.lower())

    return FileTypes(file_type.lower())


def load_json_config(args) -> typing.Optional[dict]:
  """Returns the configuration given by the --config and --config_file arguments, if any. Loading config data from a file takes
  priority over data passed in as a json string."""
  json_config_data = None

  if args.config is not None:
    json_config_data = json.loads(args.config)
  if args.config_file is not None:
    with open(args.config_file) as json_file:
      json_config_data = json.load(json_file)

  return json_config_data

def read_config_from_json(config_class, json_data) -> typing.Optional[ModuleConfiguration]:
  """Returns a requested configuration from json data"""
  if config_class is None or json_data is None:
    return None

  json_config = json_data.get(config_class.name())

  if json_config is None:
    return None

  return config_class.parse(json_config)


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
  argument("--otype", help="Output file type", required=False),
  argument("--filter", action="append", help="Document filter", required=False, default=[]),
  argument("--config", help="Configuration in json. Overridden by --config_file.", required=False),
  argument("--config_file", help="Configuration file. Overrides --config.", required=False)
])
def convert(args):
  '''Process input and output through the reader, converter, and writer'''

  inputfile = args.input
  outputfile = args.output

  json_config_data = load_json_config(args)

  general_config : GeneralConfiguration = read_config_from_json(GeneralConfiguration, json_config_data)

  if general_config is not None and general_config.log_level is not None:
    LOGGER.setLevel(general_config.log_level)

  read_progress = ProgressBar("Reading:", general_config)
  write_progress = ProgressBar("Writing:", general_config)

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
    model = imsc_reader.to_model(tree, read_progress.update)

  elif reader_type is FileTypes.SCC:
    file_as_str = Path(inputfile).read_text()

    #
    # Read the config
    #
    reader_config = read_config_from_json(SccReaderConfiguration, json_config_data)

    #
    # Pass the parsed xml to the reader
    #
    model = scc_reader.to_model(file_as_str, reader_config, read_progress.update)

  elif reader_type is FileTypes.STL:
    #
    # Read the config
    #
    reader_config = read_config_from_json(STLReaderConfiguration, json_config_data)

    #
    # Open the file and pass it to the reader
    #
    with open(inputfile, "rb") as f:
      model = stl_reader.to_model(f, reader_config, read_progress.update)

  elif reader_type is FileTypes.SRT:
    #
    # Read the config
    #
    reader_config = read_config_from_json(SRTReaderConfiguration, json_config_data)

    #
    # Open the file and pass it to the reader
    #
    with open(inputfile, "r", encoding="utf-8") as f:
      model = srt_reader.to_model(f, reader_config, read_progress.update)

  elif reader_type is FileTypes.VTT:

    #
    # Open the file and pass it to the reader
    #
    with open(inputfile, "r", encoding="utf-8") as f:
      model = vtt_reader.to_model(f, None, read_progress.update)

  else:
    if args.itype is not None:
      exit_str = f'Input type {args.itype} is not supported'
    else:
      exit_str = f'Input file {args.input} is not supported'

    die(exit_str)

  read_progress.close()

  #
  # handle the case where the input file could not be read into the model
  #
  if model is None:
    die("Aborting due to invalid input file contents.")

  #
  # apply document language
  #
  if general_config is not None and general_config.document_lang is not None:
    model.set_lang(general_config.document_lang)

  #
  # apply document filter
  #

  for filter_name in args.filter:
    doc_filter_class = DocumentFilter.get_filter_by_name(filter_name)

    if doc_filter_class is None:
      LOGGER.error("Unknown filter: %s", filter_name)
      continue

    filter_config_class = doc_filter_class.get_config_class()

    filter_config = read_config_from_json(filter_config_class, json_config_data)

    doc_filter: DocumentFilter = doc_filter_class(filter_config or filter_config_class())

    doc_filter.process(model)

  #
  # Write the output document
  #
  if writer_type is FileTypes.TTML:
    #
    # Read the config
    #
    writer_config = read_config_from_json(IMSCWriterConfiguration, json_config_data)

    #
    # Construct and configure the writer
    #
    tree_from_model = imsc_writer.from_model(model, writer_config, write_progress.update)

    #
    # Write out the converted file
    #
    tree_from_model.write(outputfile, encoding="utf-8")

  elif writer_type is FileTypes.SRT:
    #
    # Read the config
    #
    writer_config = read_config_from_json(SRTWriterConfiguration, json_config_data)

    #
    # Construct and configure the writer
    #
    srt_document = srt_writer.from_model(model, writer_config, write_progress.update)

    #
    # Write out the converted file
    #
    with open(outputfile, "w", encoding="utf-8") as srt_file:
      srt_file.write(srt_document)

  elif writer_type is FileTypes.VTT:
    #
    # Read the config
    #
    writer_config = read_config_from_json(VTTWriterConfiguration, json_config_data)

    #
    # Construct and configure the writer
    #
    vtt_document = vtt_writer.from_model(model, writer_config, write_progress.update)

    #
    # Write out the converted file
    #
    with open(outputfile, "w", encoding="utf-8") as vtt_file:
      vtt_file.write(vtt_document)

  elif writer_type is FileTypes.SCC:
    #
    # Read the config
    #
    writer_config = read_config_from_json(SccWriterConfiguration, json_config_data)

    #
    # Construct and configure the writer
    #
    scc_document = scc_writer.from_model(model, writer_config, write_progress.update)

    #
    # Write out the converted file
    #
    with open(outputfile, "w", encoding="utf-8") as scc_file:
      scc_file.write(scc_document)


  else:
    if args.otype is not None:
      exit_str = f'Output type {args.otype} is not supported'
    else:
      exit_str = f'Output file is {args.output} is not supported'

    die(exit_str)

  write_progress.close()


class ValidateModels(Enum):
  '''Enumerates the models that a document can be validated against. The value of each is the name of the model, its validation
  function and its configuration class, or `None` if the model is not configurable.'''
  IMSC11TEXT = ("imsc11text", imsc11_validator.validate, None)
  NBCU053 = ("nbcu053", nbcu053_model.validate, NBCU053ValidatorConfiguration)
  EBUTTD = ("ebuttd", ebuttd_model.validate, None)
  ROSETTA = ("rosetta", rosetta_model.validate, None)

  def __new__(cls, text: str, *_args):
    member = object.__new__(cls)
    member._value_ = text
    return member

  def __init__(self, _text: str, validate: typing.Callable[..., bool], config_class: typing.Optional[typing.Type[ModuleConfiguration]]):
    self.validate = validate
    self.config_class = config_class

  def __str__(self):
    return self._value_

VALIDATE_LOG_LEVELS: typing.Dict[str, int] = {
  "debug": logging.DEBUG,
  "info": logging.INFO,
  "warning": logging.WARNING,
  "error": logging.ERROR
}

@subcommand([
  argument("file", help="path to the TTML document to validate"),
  argument(
    "-m", "--model",
    type=ValidateModels,
    choices=list(ValidateModels),
    default=ValidateModels.IMSC11TEXT,
    help="model to validate against (default: %(default)s)"
  ),
  argument(
    "-l", "--log-level",
    choices=sorted(VALIDATE_LOG_LEVELS, key=lambda name: VALIDATE_LOG_LEVELS[name]),
    default="error",
    help="minimum severity of log messages to print (default: %(default)s)"
  ),
  argument("--config", help="Configuration in json. Overridden by --config_file.", required=False),
  argument("--config_file", help="Configuration file. Overrides --config.", required=False)
])
def validate(args) -> int:
  '''Validates a TTML document against a model (default: IMSC 1.1)'''

  log_level = VALIDATE_LOG_LEVELS[args.log_level]

  handler = ConsoleHandler()
  handler.setLevel(log_level)
  handler.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))

  root_logger = logging.getLogger()
  root_logger.setLevel(log_level)
  root_logger.addHandler(handler)

  # log messages are written by the handler of the root logger, with their level
  LOGGER.removeHandler(console)
  LOGGER.setLevel(logging.NOTSET)

  json_config_data = load_json_config(args)

  config = None

  config_class = args.model.config_class
  if config_class is not None:
    try:
      config = read_config_from_json(config_class, json_config_data)
      if config is None:
        config = config_class()
    except ValueError as e:
      die(f"invalid {config_class.name()} configuration: {' '.join(str(arg) for arg in e.args)}")

  general_config = read_config_from_json(GeneralConfiguration, json_config_data)

  try:
    with open(args.file, "rb") as f, ProgressBar("Validating:", general_config) as progress_bar:
      if not args.model.validate(f, config, progress_callback=progress_bar.update):
        return 1
  except OSError as e:
    die(f"can't open '{args.file}': {e}")

  return 0


# Ensure that the handler is added only once/globally
# Otherwise the handler will be called multiple times
console = ConsoleHandler()
LOGGER.addHandler(console)
LOGGER.setLevel(logging.INFO)


def main(argv=None):
  '''Main application processing'''

  args = cli.parse_args(argv if argv is not None else sys.argv[1:])
  if args.subcommand is None:
    cli.print_help()
    return None
  return args.func(args)


if __name__ == "__main__":
  sys.exit(main())
