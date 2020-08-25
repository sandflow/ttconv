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

'''Data model'''

from enum import Enum

#
# Types
#

class LengthType:

  class Units(Enum):
    em = "em"
    pct = "%"
    rh = "rh"
    rw = "rw"

  def __init__(self, value, units: Units):
    self.value = value
    self.units = units
#
# Content Elements
#

class WhiteSpaceHandling(Enum):
  PRESERVE = "preserve"
  DEFAULT = "default"

class ContentElement:

  def __init__(self, doc=None):

    # space handling

    self._space = WhiteSpaceHandling.DEFAULT

    # language

    self._lang = ""
    
    # owner document

    self._doc = doc

    # hierarchy

    self._first_child = None
    self._last_child = None
    self._parent = None
    self._previous_sibling = None
    self._next_sibling = None

    # styles

    self._styles = {}

    # animation

    self._sets = {}

    # layout

    self._region = None

    # timing

    self._begin = None
    self._end = None

    # id

    self._id = None

  # document

  def is_attached(self):
    return self.get_doc() is not None

  def get_doc(self):
    return self._doc

  def set_doc(self, doc):

    if doc is None:

      # detaching

      if self.parent() is not None:
        raise RuntimeError("Element must be removed from parent first")

      self.set_region(None)

    else:

      # attaching

      for e in self.dfs_iterator():
        if e.is_attached():
          raise RuntimeError("Element must be detached first")

    self._doc = doc

    for e in self:
      e.set_doc(doc)

  # hierarchical structure

  def has_children(self):
    return self._first_child is not None

  def root(self):
    root = self

    while root.parent() is not None:
      root = root.parent()

    return root

  def next_sibling(self):
    return self._next_sibling

  def previous_sibling(self):
    return self._previous_sibling

  def parent(self):
    return self._parent

  def remove(self):

    # skip processing if already a root

    if self._parent is None:
      return

    # remove from parent

    # pylint: disable=W0212

    if self._parent._first_child is self:
      self._parent._first_child = self._next_sibling

    if self._parent._last_child is self:
      self._parent._last_child = self._previous_sibling

    if self._previous_sibling is not None:
      self._previous_sibling._next_sibling = self._next_sibling

    if self._next_sibling is not None:
      self._next_sibling._previous_sibling = self._previous_sibling

    # pylint: enable=W0212

    self._parent = None
    self._next_sibling = None
    self._previous_sibling = None

  def push_child(self, child):
    if child.parent() is not None:
      raise RuntimeError("Element already has a parent")

    if child.get_doc() != self.get_doc():
      raise RuntimeError("Element belongs to a different document")

    if child is self:
      raise RuntimeError("Cannot add a root element to its descendents")

    # pylint: disable=W0212

    child._parent = self

    child._previous_sibling = self._last_child
    child._next_sibling = None

    if self._last_child is not None:
      self._last_child._next_sibling = child

    if self._first_child is None:
      self._first_child = child

    self._last_child = child

    # pylint: enable=W0212

  def __iter__(self):
    child = self._first_child
    while child is not None:
      yield child
      child = child._next_sibling

  def dfs_iterator(self):
    yield self
    for c in self:
      yield from c.dfs_iterator()

  # id

  def get_id(self):
    return self._id

  def set_id(self, element_id):
    self._id = element_id
  
  # style properties

  def get_style(self, style_prop):
    return self._styles.get(style_prop)

  def set_style(self, style_prop, value):
    if style_prop not in StyleProperties.ALL:
      raise ValueError("Invalid style property")

    if not style_prop.validate(value):
      raise ValueError("Invalid value")

    self._styles[style_prop] = value

  # layout properties

  def set_region(self, region):

    if region is not None:
      if self.get_doc() is None:
        raise Exception("Not associated with a document")
        
      if not self.get_doc().has_region(region.get_id()):
        raise ValueError("Region is unknown")

    self._region = region

  def get_region(self):
    return self._region

  # timing properties

  def set_begin(self, time_offset):
    self._begin = time_offset

  def get_begin(self):
    return self._begin

  # white space handling

  def set_space(self, wsh):
    if wsh not in WhiteSpaceHandling.__members__.values():
      raise TypeError("Must be a WhiteSpaceHandling value")

    self._space = wsh

  def get_space(self):
    return self._space

  # language

  def set_lang(self, language):
    self._lang = str(language)

  def get_lang(self):
    return self._lang

#
# Body
#
  
class Body(ContentElement):

  def push_child(self, child):
    if not isinstance(child, Div):
      raise TypeError("Children of body must be div instances")
    super().push_child(child)

#
# Div
#
  
class Div(ContentElement):

  def push_child(self, child):
    if not isinstance(child, P):
      raise TypeError("Children of body must be P instances")
    super().push_child(child)

#
# P
#
  
class P(ContentElement):

  def push_child(self, child):
    if not isinstance(child, P):
      raise TypeError("Children of body must be P instances")
    super().push_child(child)

#
# Region
#
  
class Region(ContentElement):

  def __init__(self, region_id, doc=None):
    super().__init__(doc)
    
    if region_id is None:
      raise ValueError("Every region must have an id")

    self._id = str(region_id)

  def set_id(self, element_id):
    if element_id != self.get_id():
      raise Exception("Region id is immutable")

  def push_child(self, child):
    raise Exception("Region elements do not have children")

  def set_region(self, region):
    if region is not None:
      raise Exception("Region elements cannot be associated with regions")
    super().set_region(region)

#
# Document
#

class Document:

  def __init__(self):
    self._regions = {}
    self._body = None
    self._initials = {}

  # body

  def get_body(self):
    return self._body

  def set_body(self, body: Body):
    if not isinstance(body, Body):
      raise TypeError("Argument must be an instance of Body")

    if body.parent() is not None:
      raise ValueError("Body must be a root element")

    self._body = body

  # regions

  def has_region(self, region_id):
    return region_id in self._regions

  def put_region(self, region):
    if not isinstance(region, Region):
      raise TypeError("Argument must be an instance of Region")

    if region.get_doc() != self:
      raise RuntimeError("Region does not belongs to this document")

    self._regions[region.get_id()] = region

  def remove_region(self, region_id):
    del self._regions[region_id]

  def get_region(self, region_id):
    return self._regions.get(region_id)

  def iter_regions(self):
    return self._regions.values()

  # initials

  def get_initial(self, q_name):
    return self._initials.get(q_name)

  def put_initial(self, initial):
    if not isinstance(initial, Initial):
      raise TypeError("initial must be an instance of Initial")

    self._initials[initial.qn] = initial

  def has_initial(self, q_name):
    return q_name in self._initials

  def delete_initial(self, q_name):
    return self._initials.pop(q_name, None)

  def iter_initials(self):
    return self._initials.values()

class Initial:
  pass

class Style:
  pass

#
# Style properties
#

class StyleProperties:

  class LineHeight:

    ns = "http://www.w3.org/ns/ttml#styling"
    local_name = "lineHeight"
    is_inherited = True
    is_animatable = True
    initial = "normal"
    applies_to = [Body]

    @staticmethod
    def validate(value):
      return value == "normal" or isinstance(value, LengthType)

  # add style lookup class variables

  ALL = {v for n, v in list(locals().items()) if callable(v)}
