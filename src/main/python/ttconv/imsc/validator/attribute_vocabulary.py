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

"""Utilities for maintaining collections of TTML attributes"""

class AttributeVocabulary:
  """Collection of TTML attributes"""

  def __init__(self, *args):
    '''Each arg may be an attribute class, an AttributeVocabulary instance
    (whose entries are merged in), or an iterable (list, frozenset, set) of
    attribute classes.'''
    self._map = {}
    for arg in args:
      if isinstance(arg, AttributeVocabulary):
        self._map.update(arg._map)
      elif isinstance(arg, (list, frozenset, set)):
        for attr in arg:
          self._map[attr.qname] = attr
      else:
        self._map[arg.qname] = arg

  def __contains__(self, qname):
    return qname in self._map

  def __getitem__(self, qname):
    return self._map[qname]

  def __iter__(self):
    return iter(self._map.values())

  def get(self, qname):
    return self._map.get(qname)