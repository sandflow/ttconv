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

"""Defines an event handler"""

from fractions import Fraction
import logging
import typing

LOGGER = logging.getLogger(__name__)

class EventHandler:
  '''Allows a callee to inform the caller of events that occur during processing. Typically
  overridden by the caller.
  '''

  def debug(self, msg: str, *args):
    LOGGER.debug(msg, *args)

  def info(self, msg: str, *args):
    LOGGER.info(msg, *args)

  def warn(self, msg: str, *args):
    LOGGER.warning(msg, *args)

  def error(self, msg: str, *args):
    LOGGER.error(msg, *args)

  def fatal(self, msg: str, *args):
    LOGGER.fatal(msg, *args)


class ContextEventHandler(EventHandler):
  '''Forwards events to `event_handler`, with the context set by
  `set_context()`, if any, appended to each message,
  e.g., the time of the ISD in which the event occurs'''

  def __init__(self, event_handler: EventHandler):
    self._event_handler = event_handler
    self._context: typing.Optional[str] = None

  def set_context(self, context: typing.Optional[str]):
    '''Sets the context of subsequent events, or removes it if `context` is `None`'''
    self._context = context

  def _format(self, msg: str, args) -> str:
    msg = msg % args if args else msg
    return msg if self._context is None else f"{msg} ({self._context})"

  def debug(self, msg: str, *args):
    self._event_handler.debug("%s", self._format(msg, args))

  def info(self, msg: str, *args):
    self._event_handler.info("%s", self._format(msg, args))

  def warn(self, msg: str, *args):
    self._event_handler.warn("%s", self._format(msg, args))

  def error(self, msg: str, *args):
    self._event_handler.error("%s", self._format(msg, args))

  def fatal(self, msg: str, *args):
    self._event_handler.fatal("%s", self._format(msg, args))


def make_temporal_context(time: Fraction) -> str:
  '''Returns the context of events that occur at `time`, in seconds.'''
  seconds = f"{float(time):.4f}".rstrip("0").rstrip(".")
  return f"at {seconds}s"
